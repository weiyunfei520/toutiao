from flask_restful import Resource
from flask_limiter.util import get_remote_address
from flask import request, current_app, g
from flask_restful.reqparse import RequestParser
import random
from datetime import datetime, timedelta
from redis.exceptions import ConnectionError

from celery_tasks.sms.tasks import send_verification_code
from . import constants
from utils import parser
from models import db
from models.user import User, UserProfile
from utils.jwt_util import generate_jwt
# from cache import user as cache_user
from utils.limiter import limiter as lmt
from utils.decorators import set_db_to_read, set_db_to_write


class SMSVerificationCodeResource(Resource):
    """
    短信验证码
    """
    error_message = 'Too many requests.'

    decorators = [
        lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_MOBILE,
                  key_func=lambda: request.view_args['mobile'],
                  error_message=error_message),
        lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_IP,
                  key_func=get_remote_address,
                  error_message=error_message)
    ]

    def get(self, mobile):
        code = '{:0>6d}'.format(random.randint(0, 999999))
        current_app.redis_master.setex('app:code:{}'.format(mobile), constants.SMS_VERIFICATION_CODE_EXPIRES, code)
        send_verification_code.delay(mobile, code)
        return {'mobile': mobile}


class AuthorizationResource(Resource):
    """
    认证
    """
    method_decorators = {
        # 'post': [set_db_to_write],
        # 'put': [set_db_to_read]
    }

    def _generate_tokens(self, user_id, with_refresh_token=True):
        """
        生成token 和refresh_token
        :param user_id: 用户id
        :return: token, refresh_token
        """
        # 颁发JWT
        # 生成2小时有效的token
        payload = {'user_id': user_id, 'refresh': False}  # token内容
        secret_key = current_app.config['JWT_SECRET']  # 秘钥
        expiry = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
        token = generate_jwt(payload, expiry, secret=secret_key)

        refresh_token = None
        if with_refresh_token: # 生成长效token
            # 生成过期时间14天
            expiry = datetime.utcnow() + timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            # token内容
            payload = {'user_id': user_id, 'refresh': True}
            refresh_token = generate_jwt(payload, expiry, secret=secret_key)

        return token, refresh_token


    def post(self):
        """
        登录创建token
        """
        json_parser = RequestParser()
        json_parser.add_argument('mobile', type=parser.mobile, required=True, location='json')
        json_parser.add_argument('code', type=parser.regex(r'^\d{6}$'), required=True, location='json')
        args = json_parser.parse_args()
        mobile = args.mobile
        code = args.code

        # 从redis中获取验证码
        key = 'app:code:{}'.format(mobile)
        try:
            real_code = current_app.redis_master.get(key)
        except ConnectionError as e:
            current_app.logger.error(e)
            real_code = current_app.redis_slave.get(key)

        try:
            current_app.redis_master.delete(key)
        except ConnectionError as e:
            current_app.logger.error(e)

        if not real_code or real_code.decode() != code:
            return {'message': 'Invalid code.'}, 400

        # 查询或保存用户
        user = User.query.filter_by(mobile=mobile).first()

        if user is None:
            # 用户不存在，注册用户
            user_id = current_app.id_worker.get_id()
            user = User(id=user_id, mobile=mobile, name=mobile, last_login=datetime.now())
            db.session.add(user)
            profile = UserProfile(id=user.id)
            db.session.add(profile)
            db.session.commit()
        else:
            if user.status == User.STATUS.DISABLE:
                return {'message': 'Invalid user.'}, 403

        token, refresh_token = self._generate_tokens(user.id)

        return {'token': token, 'refresh_token': refresh_token}, 201


    # 补充put函数, 用于更新token
    def put(self):
        """
        刷新token
        :return:  {message:OK, data:{token: 2小时有效token}}
        """
        # 如果存在user_id,并且是15天的refresh_token,说明需要刷新2小时有效token
        if g.user_id is not None and g.is_refresh_token is not False:
            # token, _ = ... 此时不需要is_refresh_token
            token, _ = self._generate_tokens(g.user_id, with_refresh_token=False)
            return {'token': token}, 201
        else:
            # 返回403, 通知客户端让用户重新登录
            return {'message': 'Wrong refresh token.'}, 403