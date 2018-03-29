# -*- coding:utf-8 -*-
import logging
from flask import session

from . import api
# 需要在其他文件的地方用到数据库, 可能会引发循环导入问题. 因此蓝图模块可以延迟注册
# from ihome import db


# 实现蓝图路由
@api.route('/')
def hello_world():
    session['name'] = 'xiaoming'

    """
    logging.debug("This is a debug log.")
    logging.info("This is a info log.")
    logging.warning("This is a warning log.")
    logging.error("This is a error log.")
    logging.critical("This is a critical log.")
    # 也可以这样写：
    logging.log(logging.DEBUG, "This is a debug log.")
    logging.log(logging.INFO, "This is a info log.")
    logging.log(logging.WARNING, "This is a warning log.")
    logging.log(logging.ERROR, "This is a error log.")
    logging.log(logging.CRITICAL, "This is a critical log.")
    """

    return 'Hello ihome!'