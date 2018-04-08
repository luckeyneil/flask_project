# -*- coding:utf-8 -*-
# import json
import logging

from datetime import datetime
from flask import g
from flask import jsonify, json
from flask import request
from flask import session

from ihome import constants, db
from ihome import redis_store
from ihome.libs.image_storage import storage
from ihome.models import Area, House, Facility, HouseImage, User, Order
from ihome.utils.commons import login_required
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
    print 'redis中area_json:', area_json, type(area_json)
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
        area_json = json.dumps(area_dict)  # 转码成json格式再存入redis
        redis_store.setex('areas_info', constants.AREA_INFO_EXPIRE_TIME, area_json)
        print 'mysql中area_json:', area_json, type(area_json)

    # 二. 返回数据
    """----------------------------方式一：强转为字典再返回----------------------------------"""
    # area_dict = json.loads(area_json)
    # return jsonify(
    #     errno=RET.OK,
    #     errmsg='获取信息成功',
    #     data=area_dict,
    # )

    """----------------------------方式二：请求钩子强行返回json格式----------------------------------"""
    return '{"errno": %s, "errmsg": "获取信息成功", "data": %s}' % (RET.OK, area_json)


@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
    """保存房屋的基本信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "area_id":"1",
        "facility":["7","8"]
    }
    """
    # 一. 获取参数
    house_data = request.get_json()
    if house_data is None:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 二. 校验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断单价和押金格式是否正确
    # 前端传送过来的金额参数是以元为单位，浮点数，数据库中保存的是以分为单位，整数
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        return jsonify(errno=RET.DATAERR, errmsg="参数有误")

    # 三. 保存信息
    # 1. 创建房屋对象
    user_id = g.user_id
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 2. 处理房屋的设施信息
    facility_id_list = house_data.get("facility")
    if facility_id_list:
        # 表示用户勾选了房屋设施
        # 过滤用户传送的不合理的设施id
        # select * from facility where id in (facility_id_list)
        try:
            """---------------------------flask的查询时的in的用法------------------------------"""
            facility_list = Facility.query.filter(Facility.id.in_(facility_id_list)).all()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        # 为房屋添加设施信息
        if facility_list:
            house.facilities = facility_list

    # 3. 保存数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 四. 返回
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST"])
@login_required
def save_house_image():
    """保存房屋的图片"""
    # 获取参数 房屋的图片、房屋编号
    house_id = request.form.get("house_id")
    image_file = request.files.get("house_image")

    # 校验参数
    if not all([house_id, image_file]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 1. 判断房屋是否存在
    # 2. 上传房屋图片到七牛中
    # 3. 保存图片信息到数据库中
    # 4. 处理房屋基本信息中的主图片
    # 5. 统一提交数据
    # 1. 判断房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 2. 上传房屋图片到七牛中
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存房屋图片失败")

    # 3. 保存图片信息到数据库中
    house_image = HouseImage(
        house_id=house_id,
        url=file_name
    )
    db.session.add(house_image)

    # 4. 处理房屋基本信息中的主图片
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    # 5. 统一提交数据
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片信息失败")

    # 每次保存了图片之后，应该删除首页轮播图缓存
    try:
        redis_store.delete('home_page_data')
    except Exception as e:
        logging.error(e)
        # return jsonify(
        #     errno=RET.DBERR,
        #     errmsg='redis删除失败'
        # )

    image_url = constants.QINIU_URL_PATH + file_name
    return jsonify(errno=RET.OK, errmsg="保存图片成功", data={"image_url": image_url})


@api.route("/users/houses", methods=["GET"])
@login_required
def get_user_houses():
    """获取房东发布的房源信息条目"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses

        # houses = House.query.filter_by(user_id=user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转换为字典存放到列表中
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """获取主页幻灯片展示的房屋基本信息"""
    # 从缓存中尝试获取数据
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        logging.error(e)
        ret = None
    if ret:
        logging.info("hit house index info redis")
        # 因为redis中保存的是json字符串，所以直接进行字符串拼接返回
        return '{"errno":0, "errmsg":"OK", "data":%s}' % ret
    else:
        try:
            # 查询数据库，返回房屋订单数目最多的5条数据
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询无数据")

        houses_list = []
        for house in houses:
            # 如果房屋未设置主图片，则跳过
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # 将数据转换为json，并保存到redis缓存
        json_houses = json.dumps(houses_list)
        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            logging.error(e)

        print '主页轮播图mysql中json_houses:', json_houses
        return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋详情"""
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

    # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        logging.error(e)
        ret = None
    if ret:
        logging.info("hit house info redis")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret)

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转换为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")

    # 存入到redis中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        logging.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_house)
    return resp


@api.route("/houses", methods=["GET"])
def get_search_house_list():
    """搜索功能，获取房屋列表信息"""
    # 一. 获取参数
    start_date_str = request.args.get("sd", "")  # 想要查询的起始时间
    end_date_str = request.args.get("ed", "")  # 想要查询的终止时间
    area_id = request.args.get("aid", "")  # 区域id
    sort_key = request.args.get("sk", "new")  # 排序关键字
    page = request.args.get("p", 1)  # 页数

    # 二. 校验参数
    # 2.1判断日期
    try:
        start_date = None
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date

    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    # 2.2判断页数
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1

    # 三. 业务逻辑处理

    # 3.1 先从redis缓存中获取数据
    try:
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        logging.error(e)
        resp_json = None

    if resp_json:
        # 表示从缓存中拿到了数据
        print 'search的redis中的resp_json:', resp_json
        return resp_json

    # 3.2 定义查询数据的参数空列表，最多两个条件，区域和时间
    filter_params = []

    # 3.3 处理区域信息
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 3.4 处理时间, 获取不冲突的房屋信息
    try:
        conflict_orders_li = []    # 定义冲突的订单对象的列表
        if start_date and end_date:
            # 从订单表中查询冲突的订单，进而获取冲突的房屋id
            """
            要获取冲突的房屋对象，即获取除了 不冲突的房屋 以外的对象，
            不冲突的房屋，即两种情况:
                要么搜索的截止日期在订单的开始日期之前（order.begin_date>search_end_date）,
                要么搜索的开始日期在订单的结束日期之后（order.end_date<search_begin_date）,
                下面<bd=begin_date, ed=end_date, s_ed=search_end_date, s_bd=search_begin_date>,
            冲突的房屋，即对所有不冲突的房屋取反，即 not(order.bd>s_ed or order.ed<s_bd)
            即 order.bd<=ed and order.ed>=bd
            """
            conflict_orders_li = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            # 从订单表中查询冲突的订单，进而获取冲突的房屋id
            conflict_orders_li = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            # 从订单表中查询冲突的订单，进而获取冲突的房屋id
            conflict_orders_li = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if conflict_orders_li:
        conflict_house_id_li = [order.house_id for order in conflict_orders_li]
        # 添加条件，查询不冲突的房屋
        filter_params.append(House.id.notin_(conflict_house_id_li))

    # 3.5 排序
    if sort_key == "booking":
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:   # sort_key='new'或不填
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 3.6 分页  sqlalchemy的分页
    try:
        # paginate(self, page=None, per_page=None, error_out=True)
        #                                 页数     每页数量                          错误输出
        house_page = house_query.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 3.7 将数据转为JSON
    house_li = house_page.items  # 当前页中的数据结果
    total_page = house_page.pages  # 总页数

    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    # 将结果转换json字符串
    resp = dict(errno=RET.OK, errmsg="查询成功", data={"houses": houses, "total_page": total_page, "current_page": page})
    resp_json = json.dumps(resp)

    # 3.8 将结果缓存到redis中
    if page <= total_page:
        # 用redis的哈希类型保存分页数据
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)
        try:
            # 使用redis中的事务
            pipeline = redis_store.pipeline()
            # 开启事务
            pipeline.multi()
            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, constants.HOUSE_LIST_PAGE_REDIS_EXPIRES)
            # 执行事务
            pipeline.execute()
        except Exception as e:
            pipeline.discard()
            logging.error(e)

    # 四. 数据返回
    print 'search的mysql中的resp_json:', resp_json
    return resp_json
