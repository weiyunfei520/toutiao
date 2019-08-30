from flask import request, g
from .jwt_util import verify_jwt


# 在toutiao/__init__.py中的create_app函数中，配置了请求钩子
# app.before_request(jwt_authentication)
# 所以我们这里只需要完成jwt_authentication函数就好了
def jwt_authentication():
    """根据request.headers.Authorization中的jwt token验证用户身份
        将token中user_id取出，放入g对象
        将是否为refresh_token也记录在g对象中
        方便每个请求在视图函数处理前，就能够在g对象中保存该用户的user_id，如果没有就为None"""
    g.user_id = None # 每次请求开始都设置默认值
    g.is_refresh_token = None # 每次请求开始都设置默认值
    authorization = request.headers.get('Authorization')
    # 如果request.headers.Authorization不是None
    # 并且该值是以'Bearer '开头，就说明该请求带有token
    if authorization and authorization.startswith('Bearer '):
        # strip()删除开头或是结尾的空格或换行符
        token = authorization.strip()[7:]
        payload = verify_jwt(token)
        if payload:
            g.user_id = payload.get('user_id')
            g.is_refresh_token = payload.get('refresh')