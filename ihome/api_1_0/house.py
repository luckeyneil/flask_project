# -*- coding:utf-8 -*-
# import json
import logging

from flask import jsonify, json

from ihome import constants
from ihome import redis_store
from ihome.models import Area
from ihome.utils.response_code import RET
from . import api


@api.route('/areas')
def get_area_info():
    """
    获取所有地区信息
    :return: json
    """
    # 一. 逻辑处理

    '''
    1. 读取redis中的缓存数据
    2. 没有缓存, 去查询数据库
    3. 为了将来读取方便, 在存入redis的时候, 将数据转为JSON字典字符串
    4. 将查询的数据, 存储到redis中
    '''

    # 1.读取redis
    try:
        area_json = redis_store.get('areas_info')

    except Exception as e:
        logging.error(e)
        return jsonify(
            errno=RET.DBERR,
            errmsg='redis读取失败'
        )
    print 'redis中area_json:', area_json
    # 2.redis有，直接返回

    # 3.redis没有，到mysql中查询
    if not area_json:
        try:
            areas = Area.query.all()
        except Exception as e:
            logging.error(e)
            return jsonify(
            errno=RET.DBERR,
            errmsg='mysql读取失败'
            )

        """将获取到的地区查询集每个都转化成字典，并保存入一个列表中，然后将这个列表放到一个大的字典data中"""
        area_dict = {
            'areas': [area.to_dict() for area in areas]
            }
        # 查询完毕，存入redis
        area_json = json.dumps(area_dict)   # 转码成json格式再存入redis
        redis_store.setex('areas_info', constants.AREA_INFO_EXPIRE_TIME, area_json)
        print 'mysql中area_json:', area_json

    # 二. 返回数据
    area_dict = json.loads(area_json)
    return jsonify(
        errno=RET.OK,
        errmsg='获取信息成功',
        data=area_dict,
    )


