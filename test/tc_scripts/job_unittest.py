# @Time    : 2018/3/29  20:00
# @Author    :  qingqing.xiang

from agbot.job.base import *
from agbot_test.unittest_box import *


# 2018.3.21 create by Qingqing.Xiang
# tools下job_box.py 单元测试过程
# @unittest.skip('skip')
class ToolsJobBoxTestCase(BaseUnitTestCase):
    # 初始化，获取函数入参测试数据
    def init_resolve_job_data(self, tc_section):
        self.job_conf_dict = eval(self.dt[tc_section]['job_conf_dict'])

    def init_resolve_job_schedule(self, tc_section):
        self.job_conf_dict = eval(self.dt[tc_section]['job_conf_dict'])
        self.sub_path = eval(self.dt[tc_section]['sub_path'])

    # resolve_job_data函数测试
    def test_20001_resolve_job_data_type_01_correct(self):
        # 测试为tc_type 01
        self.init_resolve_job_data('resolve_job_data_job_conf_dict_type_01_correct')
        try:
            temp = resolve_job_data(self.job_conf_dict)
            assert temp[0] is True
            assert temp[1] is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    def test_20002_resolve_job_data_type_02_correct(self):
        # 测试为tc_type 02
        self.init_resolve_job_data('resolve_job_data_job_conf_dict_type_02_correct')
        try:
            temp = resolve_job_data(self.job_conf_dict)
            assert temp[0] is True
            assert temp[1] is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    def test_20003_resolve_job_data_type_03_correct(self):
        # 测试为tc_type 03
        self.init_resolve_job_data('resolve_job_data_job_conf_dict_type_03_correct')
        try:
            temp = resolve_job_data(self.job_conf_dict)
            assert temp[0] is True
            assert temp[1] is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    def test_20004_resolve_job_data_type_01_02_correct(self):
        # 测试为tc_type 01,02混合
        self.init_resolve_job_data('resolve_job_data_job_conf_dict_type_01_02_correct')
        try:
            temp = resolve_job_data(self.job_conf_dict)
            assert temp[0] is True
            assert temp[1] is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    def test_20005_resolve_job_data_file_not_exist(self):
        # 测试数据文件：tc_api_filename不存在，tc_type为01
        self.init_resolve_job_data('resolve_job_data_file_not_exist')
        try:
            temp = resolve_job_data(self.job_conf_dict)
            assert temp[0] is False
            assert temp[1] is None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2, str(e))

    # @unittest.skip('skip')
    def test_20006_resolve_job_data_tc_data_deli(self):
        # 测试数据文件：tc_api_filename存在，配置数据以，分隔
        self.init_resolve_job_data('resolve_job_data_tc_data_deli')
        try:
            temp = resolve_job_data(self.job_conf_dict)
            assert temp[0] is True
            self.assertIn('\'1\':', temp[1]['tc_api_abs_filename'], 'deli分隔符为：","  读入数据不正确')
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)
    # TODO resolve_job_data 44-45行，由于read_to_dict函数问题，不能覆盖，待修复后补充

    # resolve_job_schedule 函数测试
    def test_20101_resolve_job_schedule_correct(self):
        self.init_resolve_job_schedule('resolve_job_schedule_correct')
        try:
            # 获取编排数据成功
            temp = resolve_job_schedule(self.sub_path, self.job_conf_dict)
            assert temp[0] is True
            assert temp[1] is not None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    def test_20102_resolve_job_schedule_file_not_exist(self):
        self.init_resolve_job_schedule('resolve_job_schedule_file_not_exist')
        try:
            # 获取编排数据失败，编排数据文件不存在
            temp = resolve_job_schedule(self.sub_path, self.job_conf_dict)
            assert temp[0] is False
            self.assertEqual(temp[1], 90008)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    def test_20103_resolve_job_schedule_file_data_wrong(self):
        self.init_resolve_job_schedule('resolve_job_schedule_file_data_wrong')
        try:
            # 文件存在，格式为.txt，读取不到数据
            # TODO tools.job_box.py 69-73行，temp不一定包含temp[1],未做异常处理。待修复后，案例补充
            temp = resolve_job_schedule(self.sub_path, self.job_conf_dict)
            assert temp[0] is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)


# 2018.3.26 create by Qingqing.Xiang
# autogo下job.py 单元测试过程
# @unittest.skip('skip')
class AutoGoJobTestCase(BaseUnitTestCase):
    def init(self, tc_section):
        job_name = eval(self.dt[tc_section]['job_name'])
        conf_dict = eval(self.dt[tc_section]['conf_dict'])
        job_conf_dict = eval(self.dt[tc_section]['job_conf_dict'])
        self.job = JobBase(job_name, conf_dict, job_conf_dict[job_name])

    # @unittest.skip('skip')
    # job_init 函数暂无内容，预留单元测试函数
    def test_21001_init_correct(self):
        self.init('job_init')
        try:
            temp = self.job.init()
            assert temp is None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # @unittest.skip('skip')
    # job.destroy 函数暂无内容，预留单元测试函数
    def test_21201_destroy_correct(self):
        self.init('job_init')
        try:
            temp = self.job.destroy()
            assert temp is None
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # job.resolve 函数单元测试, 测试case编号：213XX
    # 入参均正确
    # @unittest.skip('skip')
    def test_21301_resolve_job_correct(self):
        self.init('job_init')
        try:
            temp = self.job.resolve()
            assert temp[0] is True
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # schedule_conf_file 不存在
    # @unittest.skip('skip')
    def test_21302_resolve_job_schedule_file_not_exist(self):
        self.init('resolve_job_schedule_file_not_exis')
        try:
            temp = self.job.resolve()
            assert temp is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # tc_data_conf_file 不存在
    # @unittest.skip('skip')
    def test_21303_resolve_job_schedule_file_not_exist(self):
        self.init('resolve_job_tc_data_file_not_exist')
        try:
            temp = self.job.resolve()
            print(temp)
            assert temp is False
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)

    # execute 函数，测试case 编号214XX
    def test_21401_execute_correct(self):
        self.init('execute_correct')
        try:
            self.job.resolve()
            temp = self.job.execute()
            print(temp)
        except Exception as e:
            logger.info(str(e))
            self.assertEqual(1, 2)
    

tools_job_box_test_case = unittest.TestLoader().loadTestsFromModule(ToolsJobBoxTestCase)
autogo_job_test_case = unittest.TestLoader().loadTestsFromTestCase(AutoGoJobTestCase)

job_test_suit = unittest.TestSuite()
job_test_suit.addTests(tools_job_box_test_case)
job_test_suit.addTests(autogo_job_test_case)

unit_test_result = unittest.TextTestRunner(verbosity=2).run(job_test_suit)
