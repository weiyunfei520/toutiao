from flask import current_app
from qiniu import Auth, put_data


def upload_image(file_data):
    """
    上传图片到七牛云
    :param file_data: bytes 文件
    :return: file_name
    """
    # 需要填写Access Key和Secret Key
    a_key = 'PgUNGf4ltLK3r0ABW4V7xOYg42FouQOrAh2iU_SK'
    s_key = 'IjN2YuUuBwBjs4rEDavCJjqj4tfFs97lDJBPj33s'

    # 构建鉴权对象
    q = Auth(a_key, s_key)

    # 要上传的空间
    bucket_name = 'py_43_toutiao'

    # 上传到七牛云后保存的文件名
    # key = 'my-python-七牛.png'
    key = None

    # 生成上传token, 可以指定过期时间等
    token = q.upload_token(bucket_name, expires=3600)

    # # 要上传文件的本地路径
    # localfile = '/Users/jemy/Documents/qiniu.png'

    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, file_data)
    # print(ret)
    # print(info)

    # if is_py2:
    #     assert ret['key'].encode('utf-8') == key
    # elif is_py3:
    #     assert ret['key'] == key
    #
    # assert ret['hash'] == etag(localfile)
    return ret['key']

ret = upload_image('./111.jpg')
print(ret)