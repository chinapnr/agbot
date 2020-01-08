from ...constant.ag_enum import Conf


class TpConf(Conf):
    tp_name = 'tp_name', '测试点的名称', True, ''
    req_wait_time = 'req_wait_time', '请求等待时间', False, ''
    before_execute = 'before_execute', '插件, 测试点执行前', False, ''
    after_execute = 'after_execute', '插件, 测试点执行后', False, ''
    assert_way = 'assert_way', '断言方式', False, ''
    assertion = 'assertion', '断言tp是否通过', False, ''
    precondition = 'precondition', '前置条件', False, ''
