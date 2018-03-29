# -*- coding:utf-8 -*-

# config: 管理配置参数的，比如mysql路径，redis端口等
from logging.handlers import RotatingFileHandler

import redis
import logging


class Config(object):
    """这是要添加到app中的属性，配置"""
    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mima@127.0.0.1/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SECREK_KEY, redis, Session

    # 配置redis的数据
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置SECREK_KEY
    SECRET_KEY = 'jlhqsDJKREWASDFGJhbhrsawqQshytrewa'

    # 配置session存储到redis中
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2  # 单位是秒, 设置session过期的时间
    SESSION_TYPE = 'redis'  # 指定存储session的位置为redis
    SESSION_USE_SIGNER = True # 对数据进行签名加密, 提高安全性
    SESSION_REDIS = redis.StrictRedis(port=REDIS_PORT, host=REDIS_HOST, db=10)  # 设置redis的ip和端口

    """--------------------下面是log日志配置-------------------------"""
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
    """--------------------上面是log日志配置-------------------------"""


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    # 配置数据库
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/ihome'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass
