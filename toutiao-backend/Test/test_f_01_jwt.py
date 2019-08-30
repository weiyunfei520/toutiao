import requests, json


"""测试登录接口 POST /v1_0/authorizations"""
url = 'http://192.168.136.139:5000/v1_0/authorizations'
input('先去redis中给短信验证码 redis-cli -p 6380/6381; set app:code:13161933309 123456')
headers = {'Content-Type': 'application/json'}
data = {'mobile': '13161933309', 'code': '123456'}
resp = requests.post(url, headers=headers, data=json.dumps(data))
print(resp.json())
refresh_token = resp.json()['data']['refresh_token']

"""测试刷新token接口 PUT /v1_0/authorizations"""
# 1.登录 获取token和refresh_token
# 2.put请求 在请求头Authorization字段中带上'Bearer refresh_token'
headers['Authorization'] = 'Bearer {}'.format(refresh_token)
resp = requests.put(url, headers=headers)
print(resp.json())