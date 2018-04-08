# -*- coding:utf-8 -*-

# 配置参数

QINIU_URL_PATH = 'http://p6jcyuxjc.bkt.clouddn.com/'   # 七牛云读取域名

IMAGE_CODE_EXPIRE_TIME = 300   # 图片验证码过期时间，单位秒

SMS_CODE_EXPIRE_TIME = 300   # 短信验证码过期时间，单位秒

CCP_SMS_CODE_EXPIRE_TIME = 5   # 短信验证码过期时间,单位分钟

LOGIN_ERROR_MAX_COUNT = 5  # 登录最大错误次数

LOGIN_ERROR_COUNT_EXPIRE_TIME = 600  # 登录错误次数过期时间

AREA_INFO_EXPIRE_TIME = 600  # 地区信息过期时间

HOME_PAGE_DATA_REDIS_EXPIRES = 600  # 家目录的redis缓存过期时间

HOME_PAGE_MAX_HOUSES = 5  # 家目录最大显示房屋数

HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 600  # 房屋详情数据在redis中的过期时间

HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 5  # 房屋详情页评论展示数量

<<<<<<< HEAD
HOUSE_LIST_PAGE_CAPACITY = 3  # 搜索页每页显示的房屋数量
=======
HOUSE_LIST_PAGE_CAPACITY = 2  # 搜索页每页显示的房屋数量
>>>>>>> 1bef859a7ddcacac51fa8a30dd92516d6ae60aef

HOUSE_LIST_PAGE_REDIS_EXPIRES = 300  # 搜索页redis过期时间













# class A(object):
#     __money = 100
#
#     @property
#     def money(self):
#         raise AttributeError('就不告诉你')
#
#     @money.setter
#     def money(self, num):
#         self.__money = num
#
#     # @money.getter
#     # def money(self):
#     #     print self.__money
#     #     return self.__money
#
#     @money.deleter
#     def money(self):
#         del self.__money
#
#
# if __name__ == '__main__':
#     a = A()
#     a.money
#     # a.money = 20
#     # a.money
#     # a.money()






