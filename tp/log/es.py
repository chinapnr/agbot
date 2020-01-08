import re
import time
from datetime import datetime
from enum import Enum

from fishbase.fish_logger import logger

from .elk_connector import Es
from ..base.tp_base import TpBase, TestStatus, Conf, VerticalContext
from ..base.tp_base import get_params_dict


# LogTestPoint
class LogESTestPoint(TpBase):

    # 类的初始化过程
    # 2018.6.11 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = LogESTestPointEnum
        self.__tc_start_time = ''
        self.vertical_context = vertical_context

    # 准备请求参数
    # 2018.6.11 create by yanan.wu #748921
    def build_request(self):
        tc_ctx = self.vertical_context.tc_context

        try:
            # 获取请参
            self.req_param = {'index': self.tp_conf.get('index'),
                              'key_word': self.tp_conf.get('key_word')}
            # 获取 tc 执行起始时间
            time_struct = time.mktime(tc_ctx.start_time.timetuple())
            self.__tc_start_time = datetime.utcfromtimestamp(
                time_struct).strftime('%Y-%m-%dT%H:%M:%S')
            return self.req_param

        except RuntimeError as e:
            logger.error('tp->log:get req params error: {}'.format(str(e)))
            raise Exception(str(e))

    # 测试案例的执行
    # 2018.6.11 create by yanan.wu #748921
    def execute(self, request):
        try:
            es_conf = {}
            # 发起接口调用请求并接收响应
            es = Es(es_conf['server_ip'], es_conf['server_port'],
                    es_conf['auth_user'], es_conf['auth_password'])

            tp_utc_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
            resp = es.search_match(request.get(LogESTestPointEnum.index.key),
                                   self.__tc_start_time,
                                   tp_utc_time, 100,
                                   request.get(LogESTestPointEnum.key_word.key))
            return resp, ''
        except Exception as e:
            logger.error('tp->log: execute error: {}'.format(str(e)))
            raise Exception(str(e))

    # 预期结果的校验
    # 2018.6.11 create by yanan.wu #748921
    def test_status(self):
        tc_ctx = self.vertical_context.tc_context
        # 获取期望返回参数
        if self.tp_conf.get('expect_data'):
            params_name_list = self.tp_conf.get('expect_data').split(',')
            self.expect_dict = get_params_dict(params_name_list, tc_ctx.tc_detail.data)
        if self.tp_conf.get('check_type') == LogCheckType.ROWS_CHECK.value:
            if self.expect_dict.get(LogESTestPointEnum.expect_data.key) == str(tc_ctx.current_tp_context.response.content['hits']['total']):
                return TestStatus.PASSED
            else:
                return TestStatus.NOT_PASSED
        if self.tp_conf.get('check_type') == LogCheckType.REG_CHECK.value:
            for hit in tc_ctx.current_tp_context.response.content['hits']['hits']:
                match_obj = re.search(
                    self.expect_dict.get(LogESTestPointEnum.expect_data.key),
                    hit['_source']['message'])
                if match_obj:
                    return TestStatus.PASSED
            return TestStatus.NOT_PASSED

    # 后处理
    def post_handler(self):
        pass


# 日志检查类型
# 2018.6.12 create by yanan.wu #806640
class LogCheckType(Enum):
    # 行数校验
    ROWS_CHECK = '01'
    # 正则校验
    REG_CHECK = '02'


# 日志配置文件枚举
class LogESTestPointEnum(Conf):
    tp_name = 'tp_name', 'tp 名称', True, ''
    key_word = 'key_word', '查询关键字', False, ''
    index = 'index', '查询索引', True, ''
    check_type = 'check_type', '校验方式', True, '01'
    expect_data = 'expect_data', '期望返回结果', True, ''