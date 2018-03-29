# -*- coding:utf-8 -*-

# ihome/__init__: 1.管理app的创建(Flask())，2.db的创建(SQLAlchemy())，3.csrf保护(CSRFProtect())，
#                    4.redis(redis.StrictRedis())，5.Session()，6.项目日志 等的创建
from flask.ext.sqlalchemy import SQLAlchemy

import redis
from flask import Flask
from flask.ext.session import Session
# from flask_session import Session
from flask.ext.wtf import CSRFProtect
from config import Config

# utils需要转换为包
from utils.commons import RegexConverter

# db的创建
db = SQLAlchemy()
# 定义session专用redis
redis_session = None


def create_app(config_name):
    # 狗日的js代码中的静态文件路径写死了，我这里改了也没用啊
    # 打脸了，有用 - -       静态文件夹                  静态文件url匹配路径
    app = Flask(__name__, static_folder='jingtai', static_url_path='/static')
    # 这里一定要强制设置两个，不然会自动相等
    # app = Flask(__name__)
    # app初始化
    app.config.from_object(config_name)

    # db的创建
    # db = SQLAlchemy(app)
    # 延迟加载
    db.init_app(app)

    # 定义CSRF对象
    csrf = CSRFProtect(app)

    # 向app中添加自定义的路由转换器
    app.url_map.converters['re'] = RegexConverter

    # 在app创建的地方注册蓝图
    from ihome.api_1_0 import api
    app.register_blueprint(api)

    # 注册蓝图web_html
    import web_html
    app.register_blueprint(web_html.html)

    # redis对象,这是session外其他地方要用到的redis对象
    redis_store = redis.StrictRedis(port=Config.REDIS_PORT, host=Config.REDIS_HOST, db=11)
    # global redis_session
    # redis_session = redis.StrictRedis(port=Config.REDIS_PORT, host=Config.REDIS_HOST, db=10)

    # Session，session存到redis中，配置信息都在app中
    Session(app)

    # 项目日志

    return app, db
