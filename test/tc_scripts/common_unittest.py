# @Time    : 2018/3/29  20:13
# @Author    :  qingqing.xiang
# @Desc      :Files description

import json

from agbot_test.unittest_box import *
from tools.ag_common import *


class ToolsCommonTestCase(BaseUnitTestCase):
    # 初始化 check_resp_except 函数入参
    def init_check_resp_except(self, tc_section):
        self.tc_order = eval(self.dt[tc_section]['tc_order'])
        self.response = eval(self.dt[tc_section]['response'])
        self.tc_expect_resp_code = eval(self.dt[tc_section]['tc_expect_resp_code'])

    # 初始化 get_sorted_list 函数入参
    def init_get_sorted_list(self, tc_section):
        self.key_list = eval(self.dt[tc_section]['key_list'])
        self.params_data_list = eval(self.dt[tc_section]['params_data_list'])

    # 初始化 convert_params 函数入参
    def init_convert_params(self, tc_section):
        self.tc_list = eval(self.dt[tc_section]['tc_list'])

    # 初始化 parse_url 函数入参
    def init_parse_url(self, tc_section):
        self.tc_dict = eval(self.dt[tc_section]['tc_dict'])

    # 初始化 get_ordered_dict 函数入参
    def init_get_ordered_dict(self, tc_section):
        self.order_list = eval(self.dt[tc_section]['order_list'])
        self.params_name_list = eval(self.dt[tc_section]['params_name_list'])
        self.tc = eval(self.dt[tc_section]['tc'])

    # 初始化 get_plain_text 函数入参
    def init_get_plain_text(self, tc_section):
        self.params_dict = eval(self.dt[tc_section]['params_dict'])
        self.req_params_dict = eval(self.dt[tc_section]['req_params_dict'])

    # 初始化 check_sql_data 函数入参
    def init_check_sql_data(self, tc_section):
        self.sql_id = (self.dt[tc_section]['sql_id'])
        self.expect_result = (self.dt[tc_section]['expect_result'])
        self.result = (self.dt[tc_section]['result'])

    # @unittest.skip('skip')
    # check_resp_except 函数 case编号：300XX
    # 测试 check_resp_except_correct 函数，需要将tools.common 64行修改为 result = json.loads(response)
    def test_30001_check_resp_except_correct(self):
        self.init_check_resp_except('check_resp_except_correct')
        self.response = json.dumps(self.response)
        # try:
        temp = check_resp_except(self.tc_order, self.response, self.tc_expect_resp_code)
        assert temp is True
        # except AttributeError as e:
        #     logger.info(str(e))
        #     self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 实际结果与预期结果不一致
    def test_30002_check_resp_except_differ(self):
        self.init_check_resp_except('check_resp_except_differ')
        self.response = json.dumps(self.response)
        try:
            temp = check_resp_except(self.tc_order, self.response, self.tc_expect_resp_code)
            assert temp is False
        except AttributeError as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # common 中64行用response.json() 无法解析字典字符串,因为json不支持字符在单引号中，python字典里默认字符串是 单引号
    # @unittest.skip('skip')
    # response 不能使用json解析
    def test_30003_check_resp_except_response_cannot_decode(self):
        self.init_check_resp_except('check_resp_except_differ')
        self.response = json.dumps(self.response)
        try:
            temp = check_resp_except(self.tc_order, self.response, self.tc_expect_resp_code)
            assert temp is False
        except AttributeError as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # get_sorted_list 函数测试：case编号：301XX
    # 入参均正确
    def test_30101_get_sorted_list_correct(self):
        self.init_get_sorted_list('get_sorted_list_correct')
        try:
            temp = get_sorted_list(self.key_list, self.params_data_list)
            assert temp[0] is True
            self.assertEqual(temp[1], ['bazc'])
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 入参 key_list 中的key, 不存在于 params_data_list 中
    def test_30102_get_sorted_list_key_error(self):
        self.init_get_sorted_list('get_sorted_list_key_error')
        try:
            temp = get_sorted_list(self.key_list, self.params_data_list)
            assert temp[0] is False
            assert temp[1] is None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # convert_params 函数测试：case编号：302XX
    # 入参均正确
    def test_30201_convert_params(self):
        self.init_convert_params('convert_params_correct')
        try:
            temp = convert_params(self.tc_list)
            self.assertEqual(temp, {'a': 'a', 'c': 'c', 'b': 'b', 'z': 'z'})
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # parse_url_correct 函数测试：case编号：303XX
    # 入参均正确
    def test_30301_parse_url_correct(self):
        self.init_parse_url('parse_url_correct')
        try:
            temp = parse_url(self.tc_dict)
            assert temp
        except SyntaxError as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # get_ordered_dict 函数测试：case编号：304XX
    # @unittest.skip('skip')
    # 入参均正确
    def test_30401_get_ordered_dict_correct(self):
        self.init_get_ordered_dict('get_ordered_dict_correct')
        try:
            temp = get_ordered_dict(self.order_list, self.params_name_list, self.tc)
            assert temp[0] is True
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 入参 tc 数据长度不够，不存在 tc[3]
    def test_30403_get_ordered_dict_index_error(self):
        self.init_get_ordered_dict('get_ordered_dict_index_error')
        try:
            temp = get_ordered_dict(self.order_list, self.params_name_list, self.tc)
            assert temp[0] is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # get_plain_text 函数测试：case编号：305XX
    # @unittest.skip('skip')
    # 入参均正确
    def test_30501_get_plain_text_correct(self):
        self.init_get_plain_text('get_plain_text_correct')
        try:
            temp = get_plain_text(self.params_dict, self.req_params_dict)
            self.assertEqual(temp, 'ILOVEU')
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # params_dict 的key ‘z’不存在于req_params_dict 中
    def test_30502_get_plain_text_key_error(self):
        self.init_get_plain_text('get_plain_text_key_error')
        try:
            temp = get_plain_text(self.params_dict, self.req_params_dict)
            self.assertEqual(temp, 'IU')
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # check_sql_data 函数测试: case 编号：306XX
    # @unittest.skip('skip')
    # 入参均正确
    def test_30601_check_sql_data_correct(self):
        self.init_check_sql_data('check_sql_data_correct')
        try:
            temp = check_sql_data(self.sql_id, self.expect_result, self.result)
            assert temp[1] is True
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # 预期结果与实际结果不匹配
    # @unittest.skip('skip')
    def test_30602_check_sql_data_not_match(self):
        self.init_check_sql_data('check_sql_data_not_match')
        try:
            temp = check_sql_data(self.sql_id, self.expect_result, self.result)
            assert temp[1] is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 期望结果数据配置不正确
    def test_30603_check_sql_data_expect_wrong(self):
        self.init_check_sql_data('check_sql_data_expect_wrong')
        try:
            temp = check_sql_data(self.sql_id, self.expect_result, self.result)
            assert temp[1] is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 期望结果数据配置不正确
    def test_30604_check_sql_data_result_wrong(self):
        self.init_check_sql_data('check_sql_data_result_wrong')
        try:
            temp = check_sql_data(self.sql_id, self.expect_result, self.result)
            assert temp[1] is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)


tools_common_testcase = unittest.TestLoader().loadTestsFromTestCase(ToolsCommonTestCase)

common_test_suit = unittest.TestSuite()
common_test_suit.addTests(tools_common_testcase)
unit_test_result = unittest.TextTestRunner(verbosity=2).run(common_test_suit)
