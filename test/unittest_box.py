# @Time    : 2018/3/29  19:34
# @Author    :  qingqing.xiang

import unittest

import fishbase.fish_common as ffc
import fishbase.fish_file as fff
from fishbase import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# 添加基类，读取配置文件数据
class BaseUnitTestCase(unittest.TestCase):
    # dict_test 存放 测试 conf 中读取各类测试数据
    dt = {}

    # 整个测试之前只运行一次
    @classmethod
    def setUpClass(cls):
        # 测试 conf 文件的绝对路径
        test_conf_abs_filename = \
            fff.get_abs_filename_with_sub_path('..\\', 'autogo_unittest.conf')[1]
        logger.info(test_conf_abs_filename)

        # 读取 test conf 文件中的测试信息
        BaseUnitTestCase.dt = ffc.conf_as_dict(test_conf_abs_filename)[1]


def chrome_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver
