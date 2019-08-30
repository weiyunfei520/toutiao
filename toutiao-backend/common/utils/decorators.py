from flask import g, current_app
from functools import wraps
from sqlalchemy.orm import load_only
from sqlalchemy.exc import SQLAlchemyError


from models import db


def set_db_to_read(func):
    """
    设置使用读数据库
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db.session().set_to_read()
        return func(*args, **kwargs)
    return wrapper


def set_db_to_write(func):
    """
    设置使用写数据库
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db.session().set_to_write()
        return func(*args, **kwargs)
    return wrapper


def login_required(func):
    """
       用户必须登录装饰器
       使用方法：放在method_decorators中
    """
    # Python装饰器（decorator）在实现的时候，被装饰后的函数其实已经是另外一个函数了（函数名等函数属性会发生改变）
    # 为了不影响，Python的functools包中提供了一个叫wraps的decorator来消除这样的副作用。
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user_id:
            # 如果g.user_id是None
            return {'message': 'User must be authorized.'}, 401
        elif g.is_refresh_token:
            # 如果是15天的token
            return {'message': 'Do not use refresh token.'}, 403
        else:
        # 存在g.user_id，且g.is_refresh_token为False
            return func(*args, **kwargs)
    return wrapper