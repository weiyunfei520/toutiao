import requests, json

"""登录测试 POST /v1_0/authorizations"""
url = 'http://127.0.0.1:5000/v1_0/authorizations'
REDIS_SENTINELS = [('127.0.0.1', '26380'),
                   ('127.0.0.1', '26381'),
                   ('127.0.0.1', '26382'),]
REDIS_SENTINEL_SERVICE_NAME = 'mymaster'
from redis.sentinel import Sentinel
_sentinel = Sentinel(REDIS_SENTINELS)
redis_master = _sentinel.master_for(REDIS_SENTINEL_SERVICE_NAME)
redis_master.set('app:code:13161933309', '123456')

# 构造raw application/json形式的请求体
data = json.dumps({'mobile': '13161933309', 'code': '123456'})
# requests发送 POST raw application/json 请求
resp = requests.post(url, data=data, headers={'Content-Type': 'application/json'})
print(resp.json())
token = resp.json()['data']['token']
print(token)

"""测试 查询缓存获取用户信息 /v1_0/user"""
url = 'http://127.0.0.1:5000/v1_0/user'
headers = {'Authorization': 'Bearer {}'.format(token)}
resp = requests.get(url, headers=headers)
print(resp.json())