# @Time    : 2018/3/29  18:08
# @Author    :  qingqing.xiang

import fishbase.fish_file as fff
from fishbase import set_log_file, logger

if __name__ == '__main__':
    fff.check_sub_path_create('log')
    log_file = fff.get_abs_filename_with_sub_path('log', 'autogo_unittest.log')[1]
    set_log_file(log_file)
    logger.info('agbot unittest start')
    from agbot_test.tc_scripts.common_unittest import *
    from agbot_test.tc_scripts.jfetch_unittest import *
    from agbot_test.tc_scripts.job_unittest import *
    from agbot_test.tc_scripts.ui_unittest import *
