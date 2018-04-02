# -*- coding:utf-8 -*-
import logging
import random

from flask import make_response, jsonify
from flask import request
from ihome.utils.response_code import RET

from ihome import constants
from ihome import redis_store
from ihome.api_1_0 import api
from ihome.libs.yuntongxin.SendTemplateSMS import CCP
from ihome.models import User
from ihome.utils.captcha.captcha import captcha


# print 'verify_code/redis_store:',redis_store

@api.route('/image_codes/<image_code_id>')
def get_image_codes(image_code_id):
    # 生成了验证码
    # 名称，验证码内容，图片
    name, text, image_data = captcha.generate_captcha()

    # 保存到redis中 setex: 可以设置数据并设置有效期
    # 需要三个参数: key , expiretime, value
    try:
        redis_store.setex('image_code_%s' % image_code_id, 300, text)
    except Exception as e:
        logging.error(e)
        # resp = {
        #     'errno': RET.DBERR,
        #     'errmsg': '保存验证码失败'
        # }
        # return jsonify(resp)
        """---------------简写jsonify-----------------"""
        print '保存验证码失败'
        return jsonify(
            errno=RET.DBERR,
            errmsg='保存验证码失败'
        )

    # 返回图片
    resp = make_response(image_data)
    # 设置返回的类型为图片格式
    resp.headers['Content-Type'] = 'image/jpg'

    # captcha.generate_captcha()
    return resp


# 发送短信验证码的请求，需求参数，这里正则为什么不能加 ^ ？？？？？
@api.route('/sms_codes/<re(r"1[34578]\d{9}$"):mobile>')
def get_sms_codes(mobile):
    """
    这是点击获取验证码的视图函数
    :param mobile: 手机号码
    :return: json
    """
    # 一. 获取参数
    # mobile
    # image_code
    # image_code_id
    # 因为是get，参数是存在args中
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    print '[image_code_id, image_code]:', [image_code_id, image_code]

    # 二. 验证参数的完整性及有效性
    if not all([image_code_id, image_code]):
        return jsonify(
            errno=RET.PARAMERR,
            errmsg='缺少参数'
        )

    # 三. 处理业务逻辑

    # 1. try: 从redis中获取真实的图片验证码
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        logging.error(e)
        return jsonify(
            errno=RET.DBERR,
            errmsg='redis读取失败'
        )

    # 2. 判断图像验证码是否过期
    # 一般从数据库中获取了一个空值NULL 就是None
    if not real_image_code:
        return jsonify(
            errno=RET.NODATA,
            errmsg='验证码已过期，请重新获取'
        )

    # 3. try:无论验证成功与否, 都执行删除redis中的图形验证码
    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        logging.error(e)

        # 一般来说, 只要是删除数据库出错, 都不应该返回错误信息. 因为这个操作, 不是用户做错了
        # 此时, 只需要记录日志即可

    # 4. 判断用户填写的验证码与真实验证码是否一致, 需要转换小(大)写后在比较
    if real_image_code.lower() != image_code.lower():
        return jsonify(
            errno=RET.PARAMERR,
            errmsg='验证码错误，请重新获取输入'
        )

    # 5. try:判断用户手机号是否注册过--> 在短信发送之前, 节省资源
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        # return jsonify()
        # 理论上应该返回错误信息, 但是注册的时候还需要去验证, 去获取数据库.
        # 因此, 考虑到用户体验, 我们这一次就放过去, 让用户先接受验证码, 知道注册的时候再去判断
    else:
        # 如果查询成功, 再次判断user是否存在
        # 如果数据库没有数据, 返回一个NULL --> None
        if user:
            return jsonify(
                errno=RET.DATAEXIST,
                errmsg='手机号已注册，请直接登录或更换手机号注册'
            )

    # 6. 创建/生成6位验证码
    sms_code = '%06d' % random.randint(0, 999999)
    print 'sms_code:', sms_code

    # 7. try:将短信验证码保存redis中
    try:
        # 保存到redis中 setex: 可以设置数据并设置有效期
        # 需要三个参数: key , expiretime, value
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRE_TIME, sms_code)
    except Exception as e:
        logging.error(e)
        return jsonify(
            errno=RET.DBERR,
            errmsg='redis保存失败'
        )

    # 8. try:发送验证码
    ccp = CCP()
    try:
        # 第一个是手机号, 第二个发短信模板需要的参数[验证码, 过期时间], 第三个短信的模板编号
        # result 如果发送短信成功, 就会返回0, 如果失败,就会返回-1
        res = ccp.send_template_sms(mobile, [sms_code, constants.CCP_SMS_CODE_EXPIRE_TIME], 1)
        print 'res:', res
    except Exception as e:
        logging.error(e)
        return jsonify(
            errno=RET.THIRDERR,
            errmsg='调用第三方工具失败'
        )

    # 四. 返回数据
    if res == 0:
        # 0, 表示发送短信成功
        return jsonify(
            errno=RET.OK,
            errmsg='发送短信成功'
        )
    else:
        # -1, 表示发送短信失败
        return jsonify(
            errno=RET.THIRDERR,
            errmsg='短信发送失败'
        )
        # return 'get_sms_codes'
