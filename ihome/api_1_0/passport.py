# -*- coding:utf-8 -*-

import logging
import re

from flask import request, jsonify, session

from ihome import redis_store, db
from ihome.models import User
# from ihome.utils import RET
from ihome.utils.response_code import RET
from . import api


# POST /avi/v1_0/users/
# 手机号   mobile
# 短信验证码 sms_code
# 密码    password

@api.route('/users', methods=['POST'])
def register():
    # 后台返回的是JSON数据, 同时也要求前端返回的是JSON数据
    # key=value&key=value
    # {"key": "value"}

    # 一. 获取参数
    # get request.args.get()
    # form request.form
    # request.get_json()
    # request.form
    # 只要后台发送了JSON数据, 我们就可以通过request.get_json()来获取我们需要的数据

    # 如果前端发送的ContentType不是JSON, 那么request.get_json()就没有办法获取数据

    resp_dict = request.get_json()
    mobile = resp_dict.get('mobile')
    sms_code = resp_dict.get('sms_code')
    password = resp_dict.get('password')

    # 二. 检查数据完整性及有效性
    # 2.1 检查数据完整性
    if not all([mobile, sms_code, password]):
        resp = {
            'errno': RET.PARAMERR,
            'errmsg': '参数不完整'
        }
        return jsonify(resp)

    # 2.2 检查手机号有效性
    # 以前定义的re的正则转换器, 是为了给flask的路由使用的. flask默认的路由规则很简单
    if not re.match(r'1[34578]\d{9}', mobile):
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '手机号格式错误'
        }
        return jsonify(resp)

    # 三. 业务逻辑处理
    # 1. try:从redis中获取短信验证码
    try:
        real_sms_code = redis_store.get('sms_code_' + mobile)
    except Exception as e:
        # 日志模块默认集成到了app中
        # current_app.logger.error(e)
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '获取短信验证码失败'
        }
        return jsonify(resp)

    # 2. 判断验证码是否过期
    if real_sms_code is None:
        resp = {
            'errno': RET.NODATA,
            'errmsg': '短信验证码已过期'
        }
        return jsonify(resp)

    # 3. 判断用户是否输出了正确的验证码
    if real_sms_code != sms_code:
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '短信验证码填写错误'
        }
        return jsonify(resp)

    # 4. try:删除短信验证码(如果验证出错重新发送的话, 浪费资源, 浪费用户时间) 跟之前的发送短信验证码3,4步是相反的
    try:
        redis_store.delete('sms_code_' + mobile)
    except Exception as e:
        logging.error(e)
        # 一般来说, 只要是删除数据库出错, 都不应该返回错误信息. 因为这个操作, 不是用户做错了
        # 此时, 只需要记录日志即可

    # 5. 把数据保存到数据库(如果重复注册, 会导致失败)
    # (1. 获取短信验证码的接口, 已经判断过是否注册了 2. 用户模型手机号和用户名已经加入了唯一值, 所以数据不可能重复添加)

    # 创建用户, 保存数据
    user = User(name=mobile, mobile=mobile)
    # 密码的处理, 应该交给模型类去处理.
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        # a. 记录日志
        logging.error(e)

        # b. 回滚操作
        db.session.rollback()

        # c. 返回错误数据
        resp = {
            'errno': RET.NODATA,
            'errmsg': '短信验证码已过期'
        }
        return jsonify(resp)

    # 6. 保存将来需要用到的session数据
    # db.session: 处理数据库的
    # Session (大写的, flask_session的) 将session数据从以前默认的cookie, 存放到redis中
    # session: flask自带的session, 这个才是用来设置数据的
    session['user_id'] = user.id
    session['user_name'] = mobile
    session['mobile'] = mobile

    # 四. 返回值, 注册成功返回的页面, 交由前端处理
    resp = {
        'errno': RET.OK,
        'errmsg': '注册成功'
    }
    return jsonify(resp)
