# @Time    : 2018/5/28  14:05
# @Desc    : pytest 基类

import fishbase.fish_common as ffc
import fishbase.fish_file as fff


class PytestBase():
    # dict_test 存放 测试 conf 中读取各类测试数据
    dt = {}

    def setup(self):
        # 测试 conf 文件的绝对路径
        test_conf_abs_filename = (
            fff.get_abs_filename_with_sub_path('..\\', 'agbot_pytest.conf')[1])

        # 读取 test conf 文件中的测试信息
        self.dt = ffc.conf_as_dict(test_conf_abs_filename)[1]