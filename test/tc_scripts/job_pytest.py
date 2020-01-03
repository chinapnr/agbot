# @Time    : 2018/5/28  14:13
# @Desc    : job 模块中测试方法

from ast import literal_eval

from agbot.job.base import replace_placeholder_params, process_tc_result
from agbot_test.tc_scripts.pytest_base import PytestBase


class JobBase():
    def __init__(self, tc_id):
        self.tc_id = tc_id


class TestJob(PytestBase):

    # 初始化，获取函数入参测试数据
    def init(self, tc_section):
        self.placeholder_conf = literal_eval(
            self.dt[tc_section]['placeholder_conf'])
        self.tc_id = self.dt[tc_section]['tc_id']

    def test_replace_placeholder_params_success(self):
        # 准备参数
        self.init('replace_placeholder_params')
        job = JobBase(self.tc_id)
        job.tc_placeholder_dict = {}
        job.job_tc_dict = {'tp_conf': {'placeholder_conf': self.placeholder_conf}}
        replace_placeholder_params(job, self.tc_id)
        assert job.tc_placeholder_dict is not None

    def test_process_tc_result_success(self):
        # 准备参数
        self.sys_conf_dict = literal_eval(
            self.dt['process_tc_result']['sys_conf_dict'])
        self.test_dict = literal_eval(
            self.dt['process_tc_result']['test_dict'])
        try:
            process_tc_result(self.test_dict.get('task_id'),
                              self.test_dict.get('job_id'),
                              self.test_dict.get('tc_id'),
                              self.sys_conf_dict)
            assert 1 == 1
        except Exception as e:
            print(e)
            assert 1 == 2






