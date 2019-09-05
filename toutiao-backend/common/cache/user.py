import json
from flask import current_app
from redis import RedisError
from sqlalchemy.orm import load_only
from sqlalchemy.exc import DatabaseError

from . import constants
from models.user import User


class UserProfileCache():
    """操作用户信息缓存数据的工具类"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.key = 'user:{}:profile'.format(user_id)


    def query_db(self):
        """查询数据库,从self.get()函数中节选复制,
        如果不存在,写redis缓存为-1(防穿透) return None,
        如果存在,写redis缓存 return user_dict or None
        """

        r = current_app.redis_cluster
        try:
            user = User.query.options(load_only(
                User.mobile,
                User.name,
                User.profile_photo,
                User.introduction,
                User.certificate
            )).filter(User.id == self.user_id).first()
        except DatabaseError as e:
            current_app.logger.error(e)
            raise e # 抛出异常,不能None
            # 如果return None会和"数据库中没有记录"产生歧义

        # 如果数据库中没有记录,设置redis保存不存在的记录为-1,防穿透
        if user is None:
            try: # 一旦写缓存异常,并不影响下一次写入缓存
                r.setex(self.key, constants.UserNotExistsCacheTTL.get_ttl(), '-1') # 设置有效期
            except RedisError as e:
                current_app.logger.error(e)
            return None
        # 如果数据库中有记录,就设置redis记录 string
        else:
            user_dict = {
                'mobile': user.mobile,
                'name': user.name,
                'profile_photo': user.profile_photo,
                'introduction': user.introduction,
                'certificate': user.certificate
            }
            try:
                r.setex(self.key, constants.UserProfileCahceTTL.get_ttl(), user_dict) # 设置有效期
            except RedisError as e:
                current_app.logger.error(e)

            # 返回字典 {手机号, 昵称, 头像, 认证, 简介}
            return user_dict
    def get(self):
        """
        根据用户id查询缓存,返回用户信息
        先查询redis缓存记录
            如果有记录直接返回
            如果没有记录,就查询数据库
                如果数据库中没有记录,设置redis保存不存在的记录为-1防穿透
                如果数据库中有记录,就设置redis记录 string
        返回字典 {手机号, 昵称, 头像, 认证, 简介}
        :return: user_dict or None
        """
        r = current_app.redis_cluster
        # 先查询redis缓存记录
        try:
            ret = r.get(self.key) # 返回bytes类型
            print(ret)
        except RedisError as e:
            current_app.logger.error(e)
            # 在redis查缓存出现异常时,还可以继续向下执行,去查库,最终返回
            ret = None

        # 如果有记录直接返回
        if ret is not None:
            if ret == b'-1': # '-1'表示数据库没有该记录
                return None
            else:
                """# 坑
                b"{'user_name': '13161933309', 'user_photo': 'FglpF9w9Uih24uFCuVww4RNYVQMf', 'certificate': None, 'introduction': None}"
                如果要把json字符串转换成dict list的话
                    1. json字符串内部使用双引号
                    2. json字符串内部不能存在None null nil
                    3. replace('None', '""')
                """
                ret = str(ret, encoding='utf-8').replace("'", '"').replace('None', '""')
                return json.loads(ret) # json.loads/dumps 可以接收bytes类型
        else:
            # 如果没有记录,就查询数据库
                # 如果数据库中没有记录,设置redis保存不存在的记录为-1,防穿透
                # 如果数据库中有记录,就设置redis记录 string
                    # 返回 字典 {手机号, 昵称, 头像, 认证, 简介}
            user_dict = self.query_db()
            return user_dict

    def clear(self):
        """根据用户id删除缓存"""
        r = current_app.redis_cluster
        try:
            r.delete(self.key)
        except RedisError as e:
            current_app.logger.error(e)

    def exists(self):
        """根据用户id判断用户是否存在
        # 查询redis
        # 如果存在redis记录
            # 如果redis记录为-1，表示不存在 False
            # 如果redis记录不为-1，表示用户存在 True
        # 如果不存在redis记录
            # 去数据库查询，判断是否存在
                # 如果不存在，写redis记录为-1 False
                # 如果存在，写redis记录 True
        """
        r = current_app.redis_cluster
        try:
            ret = r.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            raise e  # 一旦出现异常，无法判断用户是否存在，所以抛出异常

        # 如果存在redis记录
        if ret is not None:
            # 如果redis记录为-1,表示不存在,False
            if ret == b'-1':
                return False
            # 如果redis记录不为-1,表示存在,True
            else:
                return True
        # 如果不存redis记录
        else:
            # 去数据库查询,判断是否存在
                # 如果不存在, 写redis记录为-1,False
                # 如果存在,写redis记录,True
            user_dict = self.query_db()
            if user_dict is not None:
                return True
            else:
                return False
