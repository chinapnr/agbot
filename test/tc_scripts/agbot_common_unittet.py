# @Time    : 2018/5/10  19:32
# @Desc    : 单元测试过程

from ast import literal_eval

from agbot.testpoint.base import TpBase, get_sign_text
from agbot_test.unittest_box import BaseUnitTestCase, unittest
from db.table_job_log import write_job
from db.table_task_log import write_task
from db.table_testcase_log import write_tc
from db.table_testpoint_log import write_tp
from fishbase import logger


# AgbotCommonTestCase 业务公共函数测试类
# 2018.5.10 create by yanan.wu #748921
class AgbotCommonTestCase(BaseUnitTestCase):

    # 初始化，获取函数入参测试数据
    def init(self, tc_section):

        self.data_req_params_id = literal_eval(
            self.dt[tc_section]['data_req_params_id'])
        self.params_name_dict = literal_eval(
            self.dt[tc_section]['params_name_dict'])
        self.tp_list = literal_eval(self.dt[tc_section]['tp_list'])

    def init_get_sign_text(self, tc_section):
        self.req_params = literal_eval(self.dt[tc_section]['req_params'])
        self.plain_text_dict = literal_eval(
            self.dt[tc_section]['plain_text_dict'])
        self.params_dict = literal_eval(self.dt[tc_section]['params_dict'])
        self.tp_list = literal_eval(self.dt[tc_section]['tp_list'])

    def init_write_record(self, tc_section):
        dt = BaseUnitTestCase.dt
        self.task_log = literal_eval(dt[tc_section]['task_log_dict'])
        self.job_log = literal_eval(dt[tc_section]['job_log_dict'])
        self.tc_log = literal_eval(dt[tc_section]['tc_log_dict'])
        self.tp_log = literal_eval(dt[tc_section]['tp_log_dict'])

    def test_correct(self):
        # 准备参数
        self.init_write_record('write_record_param')
        print(str(self.task_log))
        temp = True
        assert temp is True

    # get_ordered_dict 函数测试
    def test_get_ordered_dict_success(self):
        # 测试为tc_type 01
        self.init('get_ordered_dict_param')
        try:
            temp = TpBase.get_ordered_dict(self.data_req_params_id,
                                                  self.params_name_dict,
                                                  self.tp_list)
            assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # get_sign_text 函数测试
    def test_get_sign_text_success(self):
        # 准备参数
        self.init_get_sign_text('get_sign_text_param')
        try:
            temp = get_sign_text(self.req_params, self.plain_text_dict,
                                 self.params_dict, self.tp_list)
            assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # write_task 函数测试
    def test_write_task_success(self):
        # 准备参数
        self.init_write_record('write_record_param')
        try:
            write_task(self.task_log)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # write_job 函数测试
    def test_write_job_success(self):
        # 准备参数
        self.init_write_record('write_record_param')
        try:
            write_job(self.job_log)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # write_tc 函数测试
    def test_write_tc_success(self):
        # 准备参数
        self.init_write_record('write_record_param')
        try:
            write_tc(self.tc_log)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # write_tp 函数测试
    def test_write_tp_success(self):
        # 准备参数
        self.init_write_record('write_record_param')
        try:
            write_tp(self.tp_log)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))


agbot_common_testcase = unittest.TestLoader().loadTestsFromTestCase(AgbotCommonTestCase)

agbot_common_test_suit = unittest.TestSuite()
agbot_common_test_suit.addTests(agbot_common_testcase)

unit_test_result = unittest.TextTestRunner(verbosity=2).run(agbot_common_test_suit)



