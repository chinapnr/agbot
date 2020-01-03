# 2018.5.9 created, api unittest
import unittest
from random import Random

import requests


# 用于在测试py中获取固定长度的随机字符串使用
def random_str(randomlength=8):
    rdm_str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random_obj = Random()
    for i in range(randomlength):
        rdm_str += chars[random_obj.randint(0, length)]

    return rdm_str


# 2018.5.9 create by xin.guo
# api-user 单元测试过程
class ApiTestCase(unittest.TestCase):
    # dict_test 存放 测试 conf 中读取各类测试数据
    dt = {}
    server = '127.0.0.1:5000'

    # 2018.5.9 create by xin.guo
    # 每个测试之后进行的清理工作
    def tearDown(self):
        # print('do something after test. Clean up.')
        self.dt = {}

    # 2018.5.9 create by xin.guo
    # 测试最基本的 server 的测试接口
    # @unittest.skip('skip')
    def test_api_hello(self):
        url = ''.join([self.server, '/agbot/hello-world'])
        r = requests.get(url)
        assert r.status_code == 200

    # 2018.5.9 create by xin.guo
    # 测试创建测试任务接口, 不传参数情况
    # @unittest.skip('skip')
    def test_create_task_without_params(self):
        url = ''.join([self.server, '/agbot/task'])

        r = requests.post(url)
        # 没有传递参数报 400
        assert r.status_code == 400

    # 2018.5.9 create by xin.guo
    # 测试创建测试任务接口, 正常情况
    # @unittest.skip('skip')
    def test_create_task_success(self):
        url = ''.join([self.server, '/agbot/task'])

        info = {'task_id': random_str(8),
                'task_file_name': 'data/agbot_unittest_job_config.ini'}

        r = requests.post(url, data=info)
        # 成功返回 200
        assert r.status_code == 200

    # 2018.5.9 create by xin.guo
    # 测试创建测试任务接口, 不传参数情况
    # @unittest.skip('skip')
    def test_get_task_without_params(self):
        url = ''.join([self.server, '/agbot/task'])

        r = requests.get(url)
        # 没有传递参数报 400
        assert r.status_code == 400

    # 2018.5.9 create by xin.guo
    # 测试创建测试任务接口, 正常情况
    # @unittest.skip('skip')
    def test_get_task__success(self):
        url = ''.join([self.server, '/agbot/task'])

        r = requests.get(url, data={'task_id': '12345'})
        # 成功返回 200
        assert r.status_code == 200

api_testcase = unittest.TestLoader().loadTestsFromTestCase(ApiTestCase)

api_test_suit = unittest.TestSuite()
api_test_suit.addTests(api_testcase)

unit_test_result = unittest.TextTestRunner(verbosity=2).run(api_test_suit)



