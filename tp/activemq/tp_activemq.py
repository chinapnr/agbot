import json

import stomp
from fishbase.fish_logger import logger

from ..base.tp_base import TpBase, TestStatus, Conf, VerticalContext


# ActiveMqTestPoint
class ActiveMqTestPoint(TpBase):

    # 类的初始化过程
    # 2018.12.05 create by yang.xu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.vertical_context = vertical_context
        self.conf_enum = ActiveMqTestPointEnum
        self.__header = {}

    # 准备请求参数
    # 2018.12.05 create by yang.xu #748921
    def build_request(self):

        try:
            # 获取请参
            TpBase.build_request(self)
            return self.req_param

        except Exception as e:
            logger.exception('tp->active mq:build params error', str(e))
            raise Exception('active mq测试,构建参数时错误，测试脚本没有找到或者解析失败')

    # 测试案例的执行
    # 2018.12.05 create by yang.xu #748921
    def execute(self, request):
        # 发起接口调用请求并接收响应
        try:
            host = self.tp_conf.get(ActiveMqTestPointEnum.host.key)
            port = self.tp_conf.get(ActiveMqTestPointEnum.port.key)
            user_name = self.tp_conf.get(ActiveMqTestPointEnum.port.key)
            password = self.tp_conf.get(ActiveMqTestPointEnum.password.key)
            destination = self.tp_conf.get(ActiveMqTestPointEnum.destination.key)

            conn = stomp.Connection10(host_and_ports=[(host, port)])
            conn.start()
            conn.connect(username=user_name, password=password)
            conn.send(destination=destination, body=json.dumps(request), headers={'amq-msg-type': 'text'})
            conn.disconnect()
            logger.info('tp->active mq:消息发送成功，destination=' + destination + 'msg=' + json.dumps(request))
            result = {'result_value': True}
            return result, ''

        except ConnectionError as e:
            logger.error('tp->active mq:connection error:', str(e))
            raise RuntimeError('active mq测试，调用被测系统时连接异常')
        except Exception as e:
            logger.exception('tp->active mq:runtime error:', str(e))
            raise RuntimeError('active mq测试，调用被测系统时执行异常')

    # 预期结果的校验
    def test_status(self):
        if self.vertical_context.tc_context.current_tp_context.response.content.get('result_value') is True:
            return TestStatus.PASSED
        else:
            return TestStatus.NOT_PASSED

    # 后处理
    def post_handler(self):
        pass


# ActiveMq 配置文件枚举
class ActiveMqTestPointEnum(Conf):
    req_data = 'req_data', '请求参数', False, ''
    host = 'host', '目标系统地址', True, ''
    port = 'port', '目标系统端口', True, ''
    username = 'username', '目标系统用户名', False, '01'
    password = 'password', '目标系统密码', False, ''
    destination = 'destination', 'queue or topic', True, ''
    tp_name = 'tp_name', '测试点的名称', True, ''
    before_execute = 'before_execute', '插件, 测试点执行前', False, ''
    after_execute = 'after_execute', '插件, 测试点执行后', False, ''