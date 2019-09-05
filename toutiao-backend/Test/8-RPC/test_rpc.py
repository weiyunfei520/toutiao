import requests, json

"""测试 POST /v1_0/authorizations 登录请求"""
# code参数：需要向主从redis中手动添加短信验证码用于测试
# redis-cli -p 6380/6381
# set app:code:13161933309 123456
# 关于app:code:13161933309是一个redis key，该key的命名方式在
# 在toutiao/resources/user/passport.py的SMSVerificationCodeResource类的get函数
# redis 通过哨兵集群操作主从
REDIS_SENTINELS = [('127.0.0.1', '26380'),
                   ('127.0.0.1', '26381'),
                   ('127.0.0.1', '26382'),]
REDIS_SENTINEL_SERVICE_NAME = 'mymaster'
from redis.sentinel import Sentinel
_sentinel = Sentinel(REDIS_SENTINELS)
redis_master = _sentinel.master_for(REDIS_SENTINEL_SERVICE_NAME)
# redis_slave = _sentinel.slave_for(REDIS_SENTINEL_SERVICE_NAME)
redis_master.set('app:code:18911111111', '123456')

"""登录"""
# 构造raw application/json形式的请求体
data = json.dumps({'mobile': '18911111111', 'code': '123456'})
# requests发送 POST raw application/json 登录请求
url = 'http://192.168.136.139:5000/v1_0/authorizations'
resp = requests.post(url, data=data, headers={'Content-Type': 'application/json'})
print(resp.json())

"""测试 get /v1_0/articles"""
# 从登录请求的响应中获取token
token = resp.json()['data']['token']
print(token)
# 构造请求头：带着refresh_token发送请求
headers = {'Authorization': 'Bearer {}'.format(token)}
url = 'http://192.168.136.139:5000/v1_0/articles'
args = {'channel_id': 1,}
resp = requests.get(url, headers=headers, params=args)
print(resp.json())