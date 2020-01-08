# @Time    : 2018/12/28 16:23
# @Desc    : test_zk 执行插件

import time

from fishbase.fish_logger import logger
from kazoo.client import KazooClient

from ..base.tp_base import TpBase, Conf, VerticalContext


# ZKTestPoint
class ZkTestPoint(TpBase):
    # 类的初始化过程
    # 2018.3.12 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = ZkTestPointEnum
        self.resp_dict = {}
        self.vertical_context = vertical_context

    # 准备请求参数
    # 2018.12.28 create by xin.guo #748921
    def build_request(self):

        try:
            # 获取请参
            self.req_param['zk_url'] = self.tp_conf.get('zk_url')
            self.req_param['node_path'] = self.tp_conf.get('node_path')
            self.req_param['node_value'] = self.tp_conf.get('node_value')
            self.req_param['is_update_timestamp'] = self.tp_conf.get('is_update_timestamp', False)
            self.req_param['is_delete_node'] = self.tp_conf.get('is_delete_node', False)
            return self.req_param

        except Exception as e:
            logger.exception('zkTestPoint build_params error, cause: %s', str(e))
            raise Exception('zkTestPoint build_params error, make sure param is correct')

    # 测试案例的执行
    # 2018.12.28 create by xin.guo #748921
    def execute(self, request):
        zk = KazooClient(hosts=request['zk_url'])
        try:
            zk.start()
            path_ = request['node_path']
            value_ = request['node_value'].encode('utf-8')
            is_update_timestamp_ = request.get('is_update_timestamp', False)
            is_delete_node_ = request.get('is_delete_node', None)

            if zk.exists(path_):
                if is_delete_node_:
                    zk.delete(path_, recursive=True)
                    return self.resp_dict, ''
                if is_update_timestamp_:
                    zk.set(path_ + '/TIMESTAMP', ZkTestPoint.get_timestamp_bytes())
                if value_:
                    zk.set(path_, value_)
                else:
                    data_, stat_ = zk.get(path_)
                    if data_:
                        self.resp_dict['result_value'] = data_.decode()
            elif value_:
                # 新加节点时也需要添加 '/TIMESTAMP' 节点
                zk.create(path_, value_, makepath=True)
                zk.create(path_ + '/TIMESTAMP', ZkTestPoint.get_timestamp_bytes(), makepath=True)

            return self.resp_dict, ''
        except Exception as e:
            logger.exception('zkTestPoint execute error, cause: %s', str(e))
            raise Exception('zkTestPoint execute error, cause: ' + str(e))
        finally:
            zk.stop()

    # 后处理
    def post_handler(self):
        pass

    @staticmethod
    def get_timestamp_bytes():
        value = int(time.time() * 1000)
        res_list = [value >> 56 & 255,
                    value >> 48 & 255,
                    value >> 40 & 255,
                    value >> 32 & 255,
                    value >> 24 & 255,
                    value >> 16 & 255,
                    value >> 8 & 255,
                    value & 255]
        res = bytes(res_list)
        return res


# test_zk 配置文件枚举
class ZkTestPointEnum(Conf):
    zk_url = 'zk_url', 'zk_url', True, ''
    node_path = 'node_path', 'node_path', True, ''
    node_value = 'node_value', 'node_value', False, ''
    is_update_timestamp = 'is_update_timestamp', '是否更新时间戳', False, ''
    is_delete_node = 'is_delete_node', '是否删除节点', False, ''
    expect_data = 'expect_data', '期望返回结果', False, ''
    tp_name = 'tp_name', '测试点的名称', False, ''

    before_execute = 'before_execute', '插件, 测试点执行前', False, ''
    after_execute = 'after_execute', '插件, 测试点执行后', False, ''
    req_wait_time = 'req_wait_time', '请求等待时间', False, ''
