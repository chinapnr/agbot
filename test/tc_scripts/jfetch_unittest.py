# @Time    : 2018/3/29  19:32
# @Author    :  qingqing.xiang
# @Desc      :  tools下Jfetch.py 单元测试过程

from agbot_test.unittest_box import *
from db.model import *
from tools.ag_fetch import *


# 2018.3.13 create by Qingqing.Xiang
# @unittest.skip('skip')
class ToolsJFetchTestCase(BaseUnitTestCase):
    # 初始化section，获取params_conf_dict，sql
    def init_query_records(self, tc_section):
        self.params_conf_dict = eval(self.dt[tc_section]['params_conf_dict'])
        # query_records函数需要传入的sql，且正确
        self.sql = self.dt[tc_section]['sql']

    def init_get_signature(self, tc_section):
        self.params = eval(self.dt[tc_section]['params'])
        self.app_key = eval(self.dt[tc_section]['app_key'])
        self.method = eval(self.dt[tc_section]['method'])

    # query_records返回True,结果不为null
    # @unittest.skip('skip')
    def test_10001_query_correct(self):
        # 获取函数入参：params_conf_dict，sql
        self.init_query_records('query_records_correct')
        temp = query_records(self.params_conf_dict, self.sql)
        # 判断返回结果是否为True
        assert temp[0] is True
        assert temp[1] != []

    # query_records返回True,结果为null
    # @unittest.skip('skip')
    def test_10002_query_correct_null(self):
        # 获取函数入参：params_conf_dict，sql
        self.init_query_records('query_records_correct_null')
        temp = query_records(self.params_conf_dict, self.sql)
        # 判断返回结果是否为True
        assert temp[0] is False
        assert temp[1] is None

    # query_records返回False, 连不上数据库
    # @unittest.skip('skip')
    def test_10003_ds_key_wrong(self):
        # 获取函数入参：params_conf_dict，sql
        self.init_query_records('query_records_ds_key_wrong')
        temp = query_records(self.params_conf_dict, self.sql)
        # 判断返回结果是否为False
        assert temp[0] is False
        assert temp[1] is None

    # query_records返回False, 请求接口异常
    @unittest.skip('skip')
    def test_10004_url_wrong(self):
        # 获取函数入参：params_conf_dict，sql
        # query_records函数需要传入的参数params_conf_dict,接口地址不存在
        self.init_query_records('query_records_url_wrong')
        try:
            temp = query_records(self.params_conf_dict, self.sql)
            # 判断返回结果是否为False
            assert temp[0] is False
            assert temp[1] is None
        except Exception as e:
            logger.info('test_url_wrong params: key error: ' + str(e))
            self.assertEqual(1, 2, str(e))

    # query_records返回False, 拼装参数异常
    # @unittest.skip('skip')
    def test_10005_get_req_params_wrong(self):
        # 获取函数入参：params_conf_dict，sql
        # query_records函数需要传入的参数params_conf_dict,参数不存在app_key
        self.init_query_records('query_records_params_wrong')
        try:
            temp = query_records(self.params_conf_dict, self.sql)
            # 判断返回结果是否为False
            assert temp[0] is False
            assert temp[1] is None
        except Exception as e:
            logger.info('test__get_req_params_wrong: params key error: ' + str(e))
            self.assertEqual(1, 2, str(e))

    # query_records返回False, 查询数据库超时：所查询数据太多
    # @unittest.skip('skip')
    def test_10006_runtime_error(self):
        # 获取函数入参：params_conf_dict，sql
        self.init_query_records('query_records_runtime')
        try:
            # 调用query_records函数
            temp = query_records(self.params_conf_dict, self.sql)
            # 判断返回结果是否为False
            assert temp[0] is False
            assert temp[1] is None
        except Exception as e:
            logger.info('test__get_req_params_wrong: params key error: ' + str(e))
            self.assertEqual(1, 2, str(e))
            # raise e

    # 获取签名 ，app_key为null
    def test_10101_get_signature_app_key_null(self):
        self.init_get_signature('get_signature_app_key_null')
        try:
            temp = get_signature(self.params, self.app_key, self.method)
            assert temp is ''
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))
    # 获取签名正确
    def test_10102_get_signature_correct(self):
        self.init_get_signature('get_signature_correct')
        try:
            temp = get_signature(self.params, self.app_key, self.method)
            assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # base64 加密函数测试
    def test_10201_base64_encode(self):
        try:
            base64_encode('test')
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

class ToolsJobTestCase(BaseUnitTestCase):
    def init_write_job(self,tc_section):
        self.job_id = eval(self.dt[tc_section]['job_id'])
        self.job_name = eval(self.dt[tc_section]['job_name'])
        self.cost_time = eval(self.dt[tc_section]['cost_time'])

    def test_0001_write_job(self):
        self.init_write_job('write_job_correct')
        write_db(self.job_id, self.job_name, self.cost_time)










tools_jfetch_testcase = unittest.TestLoader().loadTestsFromTestCase(ToolsJFetchTestCase)
tools_db_testcase = unittest.TestLoader().loadTestsFromTestCase(ToolsJobTestCase)


jfetch_test_suit = unittest.TestSuite()
jfetch_test_suit.addTests(tools_jfetch_testcase)
jfetch_test_suit.addTests(tools_db_testcase)


unit_test_result = unittest.TextTestRunner(verbosity=2).run(jfetch_test_suit)
