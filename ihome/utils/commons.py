# -*- coding:utf-8 -*-
from flask import g
from flask import session, jsonify
from six import wraps
from werkzeug.routing import BaseConverter

from ihome.utils.response_code import RET


class RegexConverter(BaseConverter):
    def __init__(self, url_map, re_role):
        super(RegexConverter, self).__init__(url_map)
        self.regex = re_role


def login_required(view_func):
    """检验用户的登录状态"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None:
            # 表示用户已经登录
            # 使用g对象保存user_id，在视图函数中可以直接使用
            # 比如后面设置头像的时候, 仍然需要获取session的数据. 为了避免多次访问redis服务器. 可以使用g变量
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            resp = {
            "errno": RET.SESSIONERR,
            "errmsg": "用户未登录"
            }
            return jsonify(resp)
    return wrapper
