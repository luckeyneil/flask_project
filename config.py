# -*- coding:utf-8 -*-

# config: 管理配置参数的，比如mysql路径，redis端口等


import redis

class Config(object):
    """这是要添加到app中的属性，配置"""
    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SECREK_KEY, redis, Session

    # 配置redis的数据
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置SECREK_KEY
    SECRET_KEY = 'jlhqsDJKREWASDFGJhbhrsawqQshytrewa'

    # 配置session存储到redis中
    PERMANENT_SESSION_LIFETIME = 3600*24*2 # 单位是秒, 设置session过期的时间
    SESSION_TYPE = 'redis' # 指定存储session的位置为redis
    SESSION_USE_SIGNER = True # 对数据进行签名加密, 提高安全性
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=10)  # 设置redis的ip和端口

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    # 配置数据库
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/ihome'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass


