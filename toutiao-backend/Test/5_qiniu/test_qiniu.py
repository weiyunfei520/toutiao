from qiniu import Auth, put_file


a_key = 'PgUNGf4ltLK3r0ABW4V7xOYg42FouQOrAh2iU_SK'
s_key = 'IjN2YuUuBwBjs4rEDavCJjqj4tfFs97lDJBPj33s'
q = Auth(a_key, s_key)
upload_file_name = None
token = q.upload_token('py_43_toutiao', key=upload_file_name, expires=3600)
print(token)

file_path = './wm.jpg'
ret, info = put_file(token, upload_file_name, file_path)
print(ret)
print(info)
