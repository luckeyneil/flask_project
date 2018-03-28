# -*- coding:utf-8 -*-

# manager: 主要管理 : 1.程序的启动(Manager()), 2.以及db的操作(Migrate, MigrateCommand,将db命令添加到manager中)
# config: 管理配置参数的，比如mysql路径，redis端口等
# ihome/__init__: 1.管理app的创建(Flask())，2.db的创建(SQLAlchemy())，3.csrf保护(CSRFProtect())，
#                    4.redis(redis.StrictRedis())，5.Session()，6.项目日志 等的创建
# ihome/api_1_0/__init__: 1.定义路由
import redis
from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.session import Session
from flask.ext.wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from config import *

from ihome import create_app

# app的创建
# 调用初始化方法，生成app和db
app, db = create_app(DevelopmentConfig)

# 程序启动对象
manager = Manager(app)
# db操作对象，如迁移
migrate = Migrate(app, db)

# 并添加到启动程序命令中
"""---------------------------一切命令最终要添加到manager中-------------------------------"""
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
