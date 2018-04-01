# -*- coding:utf-8 -*-
from ihome import redis_store
from ihome.api_1_0 import api



# 图形验证码 & 短信验证接口
# /api/v1_0/image_codes

# image_codes--> 符合第三四条 : 只需要名词变复数 /  获取单个商品需要/后加id
from utils.captcha.captcha import captcha


@api.route('/image_codes/<image_code_id>')
def get_image_codes(image_code_id):

    # 生成了验证码
    # 名称，验证码内容，图片
    name, text, image_data = captcha.generate_captcha()

    # 保存到redis中 setex: 可以设置数据并设置有效期
    # 需要三个参数: key , expiretime, value
    redis_store

    return 'get_image_codes'




# captcha.generate_captcha()