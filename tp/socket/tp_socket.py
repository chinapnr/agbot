# @Time ? ?: 2018/7/10? 16:23
# @Desc    : tp_socket执行插件
import json
import socket

from fishbase.fish_logger import logger

from ..base.tp_base import TpBase, Conf, VerticalContext


# SqlTestPoint
class SocketTestPoint(TpBase):

    # 类的初始化过程
    # 2018.3.12 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = SocketTestPointEnum
        self.__jfetch_conf_dict = {}
        self.resp_dict = {}
        self.vertical_context = vertical_context

    # 准备请求参数
    # 2018.3.12 create by yanan.wu #748921
    # 2018.5.22 edit by yang.xu #848884
    def build_request(self):

        try:
            # 获取请参
            # TpBase.build_params(self, tc_ctx_dict)

            self.req_param['req_data'] = self.tp_conf.get('req_data')
            self.req_param['socket_address'] = self.tp_conf.get('socket_address')
            self.req_param['charset'] = self.tp_conf.get('charset')
            return self.req_param

        except Exception as e:
            logger.exception('SocketTestPoint build_params error, cause: %s', str(e))
            raise Exception('SocketTestPoint build_params error, make sure [cache_key, cache_type] is correct')

    # 测试案例的执行
    # 2018.3.12 create by yanan.wu #748921
    # 2018.6.19 edit by xin.guo #869614
    def execute(self, request):
        s = None
        try:
            host_port = request['socket_address'].split(':')
            s = socket.socket()
            s.settimeout(5)
            s.connect((host_port[0], int(host_port[1])))
            s.sendall(request['req_data'].encode(request['charset']))
            recv_str = s.recv(1024)
            recv_str = recv_str.decode(request['charset'])
            try:
                resp_dict = {'result_value': json.loads(recv_str)}
            except:
                resp_dict = {'result_value': recv_str}
            self.resp_dict = resp_dict
            return self.resp_dict, ''
        except Exception as e:
            logger.exception('SocketTestPoint execute error, cause: %s', str(e))
            raise Exception('SocketTestPoint execute error, cause: ' + str(e))
        finally:
            if s is not None:
                s.close()

    # 后处理
    def post_handler(self):
        pass


# SQL配置文件枚举
class SocketTestPointEnum(Conf):
    req_data = 'req_data', '请求参数', False, ''
    socket_address = 'socket_address', 'socket_address', True, ''
    expect_data = 'expect_data', '期望返回结果', False, ''
    tp_name = 'tp_name', '测试点的名称', True, ''
    before_execute = 'before_execute', '插件, 测试点执行前', False, ''
    after_execute = 'after_execute', '插件, 测试点执行后', False, ''
    req_wait_time = 'req_wait_time', '请求等待时间', False, ''