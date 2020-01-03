# @Time    : 2018/6/19  20:48
# @Desc    : log 测试类

from ast import literal_eval

from agbot.testpoint.log import LogTestPoint
from agbot_test.tc_scripts.pytest_base import PytestBase


class TestLog(PytestBase):

    def test_execute_success(self):
        # 准备参数
        log_test_point = LogTestPoint('1', '1', '1', '{}', literal_eval(self.dt['log_execute']['tp_conf_dict']), '[]', '{}')
        log_test_point.elk_conf_dict = literal_eval(
            self.dt['log_execute']['elk_conf_dict'])
        log_test_point.params = literal_eval(
            self.dt['log_execute']['params'])
        log_test_point.tc_start_time = self.dt['log_execute']['tc_start_time']
        try:
            LogTestPoint.execute
            assert 1 == 1
        except Exception as e:
            print(e)
            assert 1 == 2

    def test_check_expect_success(self):
        # 准备参数
        log_test_point = LogTestPoint('1', '1', '1', '{}', literal_eval(
            self.dt['log_execute']['tp_conf_dict']), '[]', '{}')
        log_test_point.expect_result = literal_eval(
            self.dt['log_execute']['expect_result'])
        log_test_point.result = literal_eval(
            self.dt['log_execute']['result'])

        try:
            LogTestPoint.check_expect(log_test_point)
            assert 1 == 1
        except Exception as e:
            print(e)
            assert 1 == 2



