# @Time    : 2018/3/29  20:00
# @Author    :  qingqing.xiang

from agbot_test.unittest_box import *
from fishbase.file import *

from tp.ui.main import *


# 2018.4.1 create by Qingqing.Xiang
# auogo 下ui_tc.py 单元测试过程


# @unittest.skip('skip')
class AutogoUiTc(BaseUnitTestCase):
    def init(self, tc_section='ui_test_case_init'):
        job_id = eval(self.dt[tc_section]['job_id'])
        tc_id = eval(self.dt[tc_section]['tc_id'])
        conf_dict = eval(self.dt[tc_section]['conf_dict'])
        tc_conf_dict = eval(self.dt[tc_section]['tc_conf_dict'])
        tc_list = eval(self.dt[tc_section]['tc_list'])
        pad_list = eval(self.dt[tc_section]['pad_list'])
        abs_script_filename = eval(self.dt[tc_section]['abs_script_filename'])
        self.ui_test_case = UiTestPoint(job_id, tc_id, conf_dict, tc_conf_dict, tc_list, pad_list, abs_script_filename)

    def init_get_driver(self, tc_section):
        self.driver_type = eval(self.dt[tc_section]['driver_type'])
        # self.driver = ''

    def init_execute_command(self, tc_section):
        self.command = eval(self.dt[tc_section]['command'])
        self.target = eval(self.dt[tc_section]['target'])
        self.value = eval(self.dt[tc_section]['value'])

    def init_get_exec_element(self, tc_section):
        self.target = eval(self.dt[tc_section]['target'])

    def init_get_task_list(self, tc_section):
        file_name = eval(self.dt[tc_section]['file_name'])
        self.file = get_abs_filename_with_sub_path('data', file_name)[1]

    def init_get_command_param(self, tc_section):
        self.param = eval(self.dt[tc_section]['param'])

    # 实例化 UiTestCase 类
    def setUp(self):
        self.init('ui_test_case_init')

    # @unittest.skip('skip')
    def test_40101_get_driver_chrome_correct(self):
        self.init('ui_test_case_init')
        self.init_get_driver('get_driver_chrome_correct')
        self.ui_test_case.get_driver(self.driver_type)
        self.ui_test_case.driver.quit()

    # @unittest.skip('skip')
    def test_40102_get_driver_firefox_correct(self):
        self.init_get_driver('get_driver_firefox_correct')
        self.ui_test_case.get_driver(self.driver_type)
        self.ui_test_case.driver.quit()

    # @unittest.skip('skip')
    def test_40103_get_driver_ie_correct(self):
        self.init_get_driver('get_driver_ie_correct')
        self.ui_test_case.get_driver(self.driver_type)
        self.ui_test_case.driver.quit()

    # @unittest.skip('skip')
    def test_40104_get_driver_driver_type_not_exist(self):
        self.init_get_driver('get_driver_driver_type_not_exist')
        self.ui_test_case.get_driver(self.driver_type)
        try:
            self.ui_test_case.driver.quit()
        except AttributeError as e:
            logger.info('driver 不存在，未做异常处理' + str(e))
            self.assertEqual(1, 2, str(e))

    # @unittest.skip('skip')
    def test_40201_execute_command_in_simple_command_info(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_execute_command('execute_command_in_simple_command_info')
        self.ui_test_case.execute_command(self.command, self.target, self.value)
        self.ui_test_case.driver.quit()

    # @unittest.skip('skip')
    def test_40202_execute_command_alert_not_present(self):
        self.init('ui_test_case_init')
        self.ui_test_case.driver.find_element_by_id('kw').send_keys('unittest')
        self.ui_test_case.driver.find_element_by_id('su').click()
        # self.ui_test_case.get_driver('chrome')
        # driver = self.ui_test_case.driver
        # driver.get('http://test.chinapnr.com/muser/publicRequests?Version=10&CmdId=UserRegister'
        #            '&MerCustId=6000060000848098&'
        #            'BgRetUrl=http://192.168.0.200:8008/hftest/common/commonResult.jsp&'
        #            'RetUrl=&UsrId=152169653117303&UsrName=tc_name1521696&IdType=00&'
        #            'IdNo=321323152169653105&UsrMp=18152169653&UsrEmail=10086@139.com&'
        #            'CharSet=GBK&ChkValue=123')
        # driver.find_element_by_name("captcha").click()
        # driver.find_element_by_name("captcha").clear()
        # driver.find_element_by_name("captcha").send_keys("7skw")
        # driver.find_element_by_xpath("//a[@id='sms-submit-btn']/span").click()
        # self.init_execute_command('execute_command_alert_not_present')
        # temp = self.ui_test_case.execute_command(self.command, self.target, self.value)
        # driver.quit()
        # print(temp)

    # @unittest.skip('skip')
    def test_40301_get_exec_element_id(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_get_exec_element('get_exec_element_id')
        try:
            self.ui_test_case.get_exec_element(self.target)
            self.ui_test_case.driver.quit()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40302_get_exec_element_name(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_get_exec_element('get_exec_element_name')
        try:
            self.ui_test_case.get_exec_element(self.target)
            self.ui_test_case.driver.quit()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40303_get_exec_element_link(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_get_exec_element('get_exec_element_link')
        try:
            self.ui_test_case.get_exec_element(self.target)
            self.ui_test_case.driver.quit()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 以 'xpath=' 开头的为 xpath 选择器
    def test_40304_get_exec_element_xpath(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_get_exec_element('get_exec_element_xpath')
        try:
            self.ui_test_case.get_exec_element(self.target)
            self.ui_test_case.driver.quit()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # 以 '//' 开头的为 xpath 选择器
    def test_40305_get_exec_element_xpath_(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_get_exec_element('get_exec_element_xpath_')
        try:
            self.ui_test_case.get_exec_element(self.target)
            self.ui_test_case.driver.quit()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40306_get_exec_element_not_match_re(self):
        self.init('ui_test_case_init')
        self.ui_test_case.get_driver('chrome')
        self.init_get_exec_element('get_exec_element_not_match_re')
        try:
            self.ui_test_case.get_exec_element(self.target)
            self.ui_test_case.driver.quit()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40401_get_task_list_file_correct(self):
        self.init_get_task_list('get_task_list_file_correct')
        self.init('ui_test_case_init')
        try:
            self.ui_test_case.get_task_list(self.file)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40402_get_task_list_file_not_correct(self):
        self.init_get_task_list('get_task_list_file_not_correct')
        self.init('ui_test_case_init')
        try:
            self.ui_test_case.get_task_list(self.file)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40501_get_command_param_none(self):
        self.init_get_command_param('get_command_param_none')
        self.init('ui_test_case_init')
        try:
            temp = self.ui_test_case.get_command_param(self.param)
            assert temp is ''
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40502_get_command_param_input_url(self):
        self.init_get_command_param('get_command_param_input_url')
        self.init('ui_test_case_init')
        self.ui_test_case.build_request()
        try:
            temp = self.ui_test_case.get_command_param(self.param)
            self.ui_test_case.driver.quit()
            assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40503_get_command_param_input_param_exist(self):
        self.init_get_command_param('get_command_param_input_param_exist')
        self.init('ui_test_case_init')
        self.ui_test_case.build_request()
        try:
            temp = self.ui_test_case.get_command_param(self.param)
            self.ui_test_case.driver.quit()
            assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    def test_40504_get_command_param_input_param_not_exist(self):
        self.init_get_command_param('get_command_param_input_param_not_exist')
        self.init('ui_test_case_init')
        self.ui_test_case.build_request()
        try:
            self.ui_test_case.get_command_param(self.param)
            self.ui_test_case.driver.quit()
            # assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)
        finally:
            self.ui_test_case.driver.quit()

    # @unittest.skip('skip')
    def test_40505_get_command_param_not_match_re(self):
        self.init_get_command_param('get_command_param_input_param_not_match_re')
        self.init('ui_test_case_init')
        self.ui_test_case.build_request()
        try:
            temp = self.ui_test_case.get_command_param(self.param)
            self.ui_test_case.driver.quit()
            assert temp is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)
        finally:
            self.ui_test_case.driver.quit()

    # @unittest.skip('skip')
    def test_40601_execute(self):
        self.init('ui_test_case_init')
        self.ui_test_case.build_request()
        try:
            self.ui_test_case.execute()
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)


auogo_ui_tc_file_testcase = unittest.TestLoader().loadTestsFromTestCase(AutogoUiTc)

ui_test_suit = unittest.TestSuite()
ui_test_suit.addTests(auogo_ui_tc_file_testcase)

unit_test_result = unittest.TextTestRunner(verbosity=2).run(ui_test_suit)
