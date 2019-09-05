from flask import current_app
from flask import g
from flask import request
from flask_restful.reqparse import RequestParser
from flask_restful import Resource

from models import db
from models.user import User
from utils.decorators import login_required
from utils.parser import image_file
from utils.storage import upload_image


class PhotoResource(Resource):
    # 使用装饰器验证用户
    method_decorators = [login_required]

    def patch(self):
        print(request.__dict__)
        # 接收请求的参数,并做检查
        rp = RequestParser()
        rp.add_argument('photo', type=image_file, required=True, location='files')
        args_dict = rp.parse_args()
        # 文件对象
        photo = args_dict['photo']
        # 上传图片到七牛云,获取图片key,就是图片的url名称
        file_name = upload_image(photo.read())
        # 把图片的名字保存到数据库
        User.query.filter(User.id==g.user_id).update({'profile_photo': file_name})
        db.session.commit()
        # 把图片的完整url返回
        ret_dict = {
            'photo_url': '{}/{}'.format(current_app.config['QINIU_DOMAIN'], file_name)
        }
        return ret_dict

from cache.user import UserProfileCache
class CurrentUserResource(Resource):
    # 检查登录
    method_decorators = [login_required]
    # 请求钩子 utils.middlewares.jwt_authentication已经注册生效了：把token中的user_id写入g对象中
    def get(self):
        # 返回当前用户信息
        # 从缓存和持久化存储中获取
        # 代码执行到这里时，就应该已经有g.user_id
        ret = UserProfileCache(user_id=g.user_id).get()
        print('=')
        print(ret)
        ret_dict = {
            'user_id': g.user_id,
            'user_name': ret['name'],
            'user_mobile': ret['mobile'],
            'user_photo': ret['profile_photo'],
            'certificate': ret['certificate'],
            'introduction': ret['introduction'],
            'arts_count': 0,
            'following_count': 0
        }
        return ret_dict

    def delete(self):
        ret = UserProfileCache(user_id=g.user_id).exists()
        if ret:
            UserProfileCache(user_id=g.user_id).clear()
        return {'message': 'ok'}