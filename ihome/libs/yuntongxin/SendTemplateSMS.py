# -*- coding: UTF-8 -*-
import logging

from CCPRestSDK import REST
import ConfigParser

# 主帐号
accountSid = '8a216da8627648690162804825b40152'

# 主帐号Token
accountToken = '5b3e411dc7524c2489361f8dc42c3742'

# 应用Id
appId = '8a216da8627648690162804826190159'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

# 初始化REST SDK(鉴权)，只需要做一次，因此，放到单例里面执行
class CCP(object):
    def __new__(cls):
        """实际上是把创建的实例对象当做类对象的一个属性了"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(CCP, cls).__new__(cls)
            # 初始化REST SDK
            cls.instance.rest = REST(serverIP, serverPort, softVersion)
            cls.instance.rest.setAccount(accountSid, accountToken)
            cls.instance.rest.setAppId(appId)

        return cls.instance

    def send_template_sms(self, to, datas, tempId):
        """

        :param to: 手机号码
        :param datas: 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        :param tempId: 模板Id
        :return:
        """
        try:
            result = self.rest.sendTemplateSMS(to, datas, tempId)
        except Exception as e:
            logging.error(e)
            raise e
        print '---------------------------------------------------------------'
        print result
        # {'statusMsg': u'\u3010\u8d26\u53f7\u3011\u4e3b\u8d26\u6237\u7ed1\u5b9a\u7684\u6d4b\u8bd5\u53f7\u7801\u4e2a\u6570\u4e3a\u96f6',
            # 'statusCode': '111188'}

        statuscode = result.get('statusCode')
        if statuscode == '000000':
            return 0
            # 3. 需要告诉服务器是否成功. 我们这里暂时定义, 返回0就是成功, 返回-1就是失败
        else:
            return -1

    # def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.iteritems():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)
#

            # sendTemplateSMS(手机号码,内容数据,模板Id)

if __name__ == '__main__':
    ccp = CCP()
    # 模板id是什么鬼东西？
    ccp.send_template_sms('17521069344', {'112233'}, 1)
    ccp.send_template_sms('17521069344', ['112233', '5'], 1)