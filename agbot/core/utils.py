# coding=utf-8
# @Time    : 2018/3/14 16:31
# @Desc    : 任务类
import asyncio
import collections
import os
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, List

from fishbase.fish_file import *
from fishbase.fish_logger import logger

# BaseJob 任务类
# 2018.3.14 create by jie.lu #748921
# 2018.3.15 edit by yanan.wu #770276
# from .tc import TcContext
from ..core.model.context import VerticalContext
from ..core.tp.tp_context import TpContext
from ..tools.ag_common import read_nesting_value

event_loop = asyncio.new_event_loop()
thread_pool = ThreadPoolExecutor(max_workers=100)


# 生成当前路径下指定后缀的完整文件名
# 2018.7.9 create by yanan.wu #904499
# 2019.03.07 edit by jun.hu 修改通过 basedir 获取文件路径
def get_abs_filenames_by_suffix(file_dir, suffix):
    if not os.path.isdir(file_dir):
        return False, None
    try:
        abs_filenames_list = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if file.endswith(suffix):
                    abs_filenames_list.append(os.path.join(root, file))
        flag = True
        return flag, abs_filenames_list
    
    except:
        flag = False
        return flag, None


# 判断当前文件的编码格式
# 2018.8.6 create by yanan.wu #931475
def get_file_encoding(file):
    # 读入文件
    file = open(file, 'rb')
    buf = file.read()
    result = chardet.detect(buf)
    encoding = result['encoding']
    if encoding.startswith('utf-8'):
        result_encoding = encoding
    elif encoding.startswith('UTF-8'):
        result_encoding = encoding
    else:
        result_encoding = 'GB2312'
    logger.info('get file encoding %s, %s as %s', file.name, encoding, result_encoding)
    # 关闭文件操作
    file.close()
    return result_encoding


# 确认str不为空白
def is_not_blank(text):
    return text is not None and len(text.strip()) > 0


def assert_no_config_missing(unit_name, conf_type, conf_dict):
    """
    断言，没有配置丢失
    :param unit_name: 判断对象名称  eg: job_conf
    :param conf_type:  配置字典需要满足的配置类 eg: conf.JobConf
    :param conf_dict: 配置字典
    """
    if conf_type:
        return True
    
    must_key = [c.key for c in conf_type if c.require]
    missing_list = [key for key in must_key if not is_not_blank(conf_dict.get(key))]
    assert len(missing_list) == 0, ['missing value for [' + key + '] in [' + unit_name + ']' for key in
                                    missing_list]


# 替换conf_dict中的占位符, 若无值可替换则保留占位符
def resolve_placeholder(conf_dict: Dict[str, str],
                        vertical_ctx: VerticalContext,
                        ignore_values: List = None):
    interpreted = {}
    replacement = []
    for conf_k, conf_v in conf_dict.items():

        if isinstance(conf_k, str) and isinstance(conf_v, (collections.Mapping, collections.abc.Mapping)):
            conf_v_interpreted, conf_v_replacement = resolve_placeholder(conf_v, vertical_ctx, ignore_values)
            interpreted[conf_k] = conf_v_interpreted
            replacement.extend(conf_v_replacement)
        elif isinstance(conf_k, str) and isinstance(conf_v, str):
            temp_k, replacement_k = get_placeholder_value(conf_k, vertical_ctx, ignore_values)
            replacement.extend(replacement_k)
            temp_v, replacement_v = get_placeholder_value(conf_v, vertical_ctx, ignore_values)
            replacement.extend(replacement_v)
            conf_k = temp_k or conf_k
            conf_v = temp_v or conf_v
            interpreted[conf_k] = conf_v
        else:
            interpreted[conf_k] = conf_v
            continue

    return interpreted, replacement


# 2019.6.6 edit by jun.hu
# 获取占位符的值，需要替换占位符的字符换也有可能是字符串
def get_placeholder_value(old_str: str,
                          vertical_ctx: VerticalContext,
                          ignore_values: List = None):
    temp_str = old_str
    pattern = re.compile(r'\${[\w.]+}')
    mark_list = pattern.findall(old_str)
    replacement = []

    env_dict = {}
    env_dict.update(vertical_ctx.tc_context.tc_detail.data)
    env_dict['resp'] = {tp_ctx.id: tp_ctx.response.content
                        for tp_ctx in filter(lambda c: isinstance(c, TpContext) and c.response is not None,
                                             vertical_ctx.tc_context.tp_and_plugin_context_list)}
    env_dict['global'] = vertical_ctx.task_context.task_model.global_var

    for mark in mark_list:
        key = mark[2:-1]
        key_nesting_list = key.split('.')
        replace_v = read_nesting_value(env_dict,
                                       key_nesting_list)
        if replace_v is not None:
            if ignore_values is None or replace_v not in ignore_values:
                temp_str = temp_str.replace(mark, str(replace_v))
                replacement.append((mark, replace_v))
    return temp_str, replacement


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def rotate(matrix):
    new_matrix = []
    width = max([len(l) for l in matrix])
    for i in range(width):
        new_l = []
        for l in matrix:
            if len(l) > i:
                new_l.append(l[i])
        new_matrix.append(new_l)
    return new_matrix
