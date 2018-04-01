# -*- coding:utf-8 -*-

# ihome/api_1_0/__init__: 定义路由,创建蓝图对象
from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api/v1_0')

import index, models
