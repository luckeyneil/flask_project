# -*- coding:utf-8 -*-
import logging

import datetime
from flask import jsonify
from flask import request

from ihome import db
from ihome.api_1_0 import api
from ihome.models import Order, House
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET


@api.route("/orders", methods=["POST"])
@login_required
def save_order():
    """保存订单"""
    # 一. 获取数据
    # 获取用户id
    user_id = g.user_id
    # 获取参数,校验参数
    order_data = request.get_json()
    if not order_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 进一步获取详细参数信息,house_id/start_date/end_date
    house_id = order_data.get("house_id")
    start_date_str = order_data.get("start_date")
    end_date_str = order_data.get("end_date")

    # 二. 校验参数完整性
    # 2.1 完整性校验
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 2.2 对日期格式化,datetime
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        # 断言订单天数至少1天
        assert start_date <= end_date
        # 计算预订的天数
        days = (end_date - start_date).days + 1
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期格式错误")

    # 三. 业务逻辑处理
    # 3.1 查询房屋是否存在
    try:
        # House.query.filter_by(id=house_id).first()
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取房屋信息失败")
    # 校验查询结果
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 3.2 判断用户是否为房东
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不能预订自己的房屋")

    # 3.3 查询是否被别人预定
    try:
        # 查询时间冲突的订单数
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date,
                                   Order.end_date >= start_date).count()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="检查出错，请稍候重试")
    # 校验查询结果
    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已被预订")

    # 3.4 计算房屋总价
    amount = days * house.price
    # 生成模型类对象,保存订单基本信息:房屋/用户/订单的开始日期/订单的结束日期/天数/价格/总价
    order = Order()
    order.house_id = house_id
    order.user_id = user_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = amount
    # 3.5 保存订单数据到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        # 提交数据如果发生异常,需要进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单失败")

    # 四. 返回数据
    # 前端对应服务器的操作如果是更新资源或新建资源,可以返回对应的信息,
    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})
