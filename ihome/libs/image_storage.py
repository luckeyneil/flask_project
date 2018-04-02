# -*- coding:utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
from qiniu import put_data

# 需要填写你的 Access Key 和 Secret Key

access_key = 'B5RKQEn7OT-rRFNjkzBkcibOyjq7a6stkUkqCKkH'
secret_key = '9G9Q74cxXif0q17pSp8c0UIIq4lA4oVsYEvqmOBu'

def storage(file_data):
    """上传文件到七牛"""
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'luckeyway'
    # 上传到七牛后保存的文件名, 无需命名，系统会自动命名
    key=None
    # key = 'my-python-logo.png';
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'
    # put_file是指定路径的文件上传，此处不需要，可用到直接上传图片数据的put_data
    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, file_data)
    print 'info:',info
    print 'ret:',ret

    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)
    status_code = info.get('status_code')
    if status_code == 200:
        # 上传成功，返回保存的文件名，可以以后拼接域名获取图片
        return ret.get('key')
    else:
        raise Exception("上传失败")

if __name__ == '__main__':
    with open('test.png', 'rb') as f:
        data = f.read()

        storage(data)