# -*- coding:utf-8 -*-

# ihome/api_1_0/__init__: 定义路由,创建蓝图对象
from flask import Blueprint

api = Blueprint('api', __name__)

import index, verify_code, passport, profile, house

import ihome.models


# 请求钩子，将返回的普通格式转化为json
@api.after_request
def after_request(response):
    resp_type = response.headers['Content-Type']
    # 请求钩子，如果返回的是普通数据，就强转为json，而其他特殊数据，则不改变
    if resp_type.startswith('text'):
        response.headers['Content-Type'] = 'application/json'

    return response

