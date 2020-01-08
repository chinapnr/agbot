# coding=utf-8
import json
import logging
import os
import sys

import fishbase.fish_common as ffc
import fishbase.fish_file as fff
from fishbase.fish_logger import logger, SafeFileHandler

from .tools.ag_common import dict_update_deep


def _set_log_file(local_file=None):
    """
    设置日志记录，按照每天一个文件，记录包括 info 以及以上级别的内容；
    日志格式采取日志文件名直接加上日期，比如 fish_test.log.2018-05-27

    :param:
        * local_fie: (string) 日志文件名
    :return: 无

    举例如下::

        from fishbase.fish_logger import *
        from fishbase.fish_file import *

        _log_abs_filename = get_abs_filename_with_sub_path('log', 'fish_test.log')[1]

        set_log_file(_log_abs_filename)

        logger.info('test fish base log')
        logger.warn('test fish base log')
        logger.error('test fish base log')

        print('log ok')

    """

    default_log_file = 'default.log'

    _formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(pathname)s#%(funcName)s[ln:%(lineno)d] %(message)s')

    if local_file is not None:
        default_log_file = local_file

    _tfh = SafeFileHandler(filename=default_log_file, encoding='utf-8')
    _tfh.suffix = "%Y-%m-%d.log"
    _tfh.setLevel(logging.INFO)
    _tfh.setFormatter(_formatter)

    logger.setLevel(logging.INFO)

    logger.addHandler(_tfh)


class AgbotConfig(ffc.SingleTon):
    _log_abs_filename = ''
    _conf_ini_abs_filename = ''
    _conf_json_abs_filename = ''
    _file_path = os.path.split(os.path.realpath(__file__))[0]
    basedir = os.path.abspath(os.path.dirname(_file_path) + os.path.sep + ".")
    sys_conf_dict = {}

    # 类初始化过程
    # 2017.1.13
    def __init__(self):
        # 创建需要的路径
        AgbotConfig.create_need_path()
        # 生成需要的各类绝对路径名称
        AgbotConfig.create_need_abs_filename()

        # 日志格式
        _set_log_file(AgbotConfig._log_abs_filename)

        sys_conf_dict = {}
        json_conf_dict = self.read_conf_json(AgbotConfig._conf_json_abs_filename)
        ini_conf_dict = self.read_conf_ini(AgbotConfig._conf_ini_abs_filename)
        dict_update_deep(sys_conf_dict, json_conf_dict)
        dict_update_deep(sys_conf_dict, ini_conf_dict)
        AgbotConfig.sys_conf_dict = sys_conf_dict

        logger.info('agbot config load OK!')

    # 创建应用程序所需要的基本路径
    @staticmethod
    def create_need_path():
        # 创建日志路径 log
        fff.check_sub_path_create('log')

        # 创建sqlite db 路径
        fff.check_sub_path_create('db')

    # 创建app使用的各个长文件名
    @staticmethod
    def create_need_abs_filename():
        AgbotConfig._log_abs_filename = \
            fff.get_abs_filename_with_sub_path('log', 'agbot.log')[1]

        AgbotConfig._conf_ini_abs_filename = \
            fff.get_abs_filename_with_sub_path('conf', 'agbot_conf.ini')[1]

        AgbotConfig._conf_json_abs_filename = \
            fff.get_abs_filename_with_sub_path('conf', 'agbot_conf.json')[1]

    @staticmethod
    def read_conf_json(conf_file):
        json_conf_dict = {}
        with open(conf_file, 'rt') as f:
            content = f.read()
            if len(content) > 0:
                try:
                    conf_dict = json.loads(content, encoding='utf-8')
                except:
                    logger.error(
                        'agbot config {conf_file} read failed!'.format(
                            conf_file=AgbotConfig._conf_ini_abs_filename))
                    sys.exit(0)
                json_conf_dict.update(dict(conf_dict))
        return json_conf_dict

    @staticmethod
    def read_conf_ini(conf_file):
        # 读取 server conf 文件中的所有信息
        temp = ffc.conf_as_dict(conf_file, case_sensitive=True)
        if not temp[0]:
            logger.error(
                'agbot config {conf_file} read failed!'.format(
                    conf_file=AgbotConfig._conf_ini_abs_filename))
            sys.exit(0)
        return temp[1]


agbot_config = AgbotConfig()
