# -*- coding:utf-8 -*-

# ihome/__init__: 1.管理app的创建(Flask())，2.db的创建(SQLAlchemy())，3.csrf保护(CSRFProtect())，
#                    4.redis(redis.StrictRedis())，5.Session()，6.项目日志 等的创建

import redis
from flask import Flask
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect

from config import Config
from ihome.api_1_0 import api


def create_app(config_name):
    app = Flask(__name__)
    # app初始化
    app.config.from_object(config_name)

    # 在app创建的地方注册蓝图
    app.register_blueprint(api)
    # db的创建
    db = SQLAlchemy(app)

    # 定义CSRF对象
    csrf = CSRFProtect(app)

    # redis对象,这是session外其他地方要用到的redis对象
    redis_store = redis.StrictRedis(port=Config.REDIS_PORT, host=Config.REDIS_HOST, db=11)

    # Session，session存到redis中，配置信息都在app中
    Session(app)

    # 项目日志

    return app, db

