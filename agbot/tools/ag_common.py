# @Time    : 2018/2/24  10:51
# @Desc    : 业务相关公共方法


import collections
import json
import re
from ast import literal_eval
from urllib import parse

import six
from fishbase.fish_logger import logger


# 根据指定顺序获取有序字典
# 输入：
# index_list: 指定顺序
# params_name_dict: 参数名称字典
# tp: 参数数据列表，格式：[param1,param2,...]
# 输出：
# (flag, ordered_dict)
# flag: True/False
# ordered_dict: 有序字典
# ---
# 2018.3.27 create by yanan.wu #783365
def get_ordered_dict(index_list, params_name_dict, tp):
    try:
        ordered_dict = collections.OrderedDict()
        # 获取请参有序字典
        for index in index_list:
            ordered_dict[params_name_dict[index]] = tp[index - 1]
    except IndexError as e:
        flag = False
        logger.error('Index Error, test_case ' + tp[0], str(e))
        return flag, None

    flag = True
    return flag, ordered_dict


# 获取签名明文串
# 输入：
# params_dict: 配置参数字典
# req_params_dict: 请参字典
# 输出：
# plain_text: 签名信息明文字符串
# ---
# 2018.3.27 create by yanan.wu #783365
def get_plain_text(sign_params_name_list, req_params_dict):
    # 声明签名信息明文串
    plain_text = ''

    # 构造商户签名信息明文字符串
    for param_name in sign_params_name_list:
        if param_name in req_params_dict.keys():
            plain_text += req_params_dict.get(param_name)
    return plain_text


# 自动化测试接口调用结果返回参数检查
# 输入：
# response : HTTP 请求响应对象
# test_case_seq : 测试案例编号
# expect_resp_code : 期待的接口返回码
# 输出：
# (Boolean, test_case_seq) : 元组
# db_check_sql_flag:检查结果 True - 通过
# result : 接口请求响应报文
# ---
# 2018.2.9 edit by qingqing.xiang, code optimized #737798
# 2018.2.9 edit by jie.lu #737798, code specification optimized #737798
# 2018.2.13 edit by David Yi
# 2018.3.27 edit by yanan.wu
# 2018.4.16 抽象为两个 Json 串是否包含:source_json 是否包含在 target_json 中 edit by jie.lu
def json_contain(source_json, target_json):
    # 判断接口返回值与预期返回值是否一致
    key_list = source_json.keys()
    for key in key_list:
        if not target_json.get(key) == source_json.get(key):
            return False
    return True


# 根据指定的顺序对字段的 value 值进行排序
# 输入：
# key_list: 指定顺序的列表
# params_data_list: 待排序的数据
# 输出：
# (flag, sorted_list)
# flag: True/False
# sorted_list: 排序后的返回值
# ---
# 2018.3.8 create by yanan.wu #761860
def get_sorted_list(key_list, params_data_list):
    flag = True
    sorted_list = []
    for _, params_data_dict in enumerate(params_data_list):
        s = ''
        for _, key in enumerate(key_list):
            try:
                s += params_data_dict[key]
            except KeyError:
                flag = False
                return flag, None
        sorted_list.append(s)
    return flag, sorted_list


# 后台接口案例数据列表转换为字典格式
# 输入：
# tc_api_list: 后台接口案例数据列表
# 输出：
# tc_api_dict: 转换后的字典
# ---
# 2018.3.14 create by yanan.wu #757866
def convert_params(tc_list):
    tc_dict = {}
    for tc in tc_list:
        tc_dict[tc[0]] = tc
    return tc_dict


# URL ?与参数部分的地址拼接
# 输入：
# data: ? 参数名与 value 值组合的 dict
# 输出：
# urls：? 与参数拼接后的字符串
# 2018.3.8 edit by qingqing.xiang
def parse_url(data):
    item = data.items()
    urls = "?"
    for key, value in item:
        temp_str = key + "=" + value
        urls = urls + temp_str + "&"
    # 去掉最后一个&字符
    urls = urls[:len(urls) - 1]
    return urls


# 实现单个字符 urldecode
# 输入：
# obj_str: 编码串
# ---
# 2018.4.10 create by yanan.wu #802968
def get_urldecode(obj_str):
    return parse.unquote(obj_str)


# 驼峰形式字符串转成下划线形式
# 输入：
# hunp_str: 驼峰形式字符串
# 2018.6.13 create by yang.xu #869689
def hump2underline(hunp_str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


# 读取嵌套字典中的值
# data 数据，必须为dict或list
# key列表,必须为key或index
def read_nesting_value(data, keys):
    value = None
    for i, k in enumerate(keys):
        # noinspection PyBroadException
        # 尝试能否转成list或dict，可行则转，不可行pass
        try:
            data = literal_eval(data)
            data = json.loads(data)
        except Exception:
            pass

        if isinstance(data, dict):
            value = data.get(k)
            data = value
            if value is None:
                return None
        elif isinstance(data, list):
            value = data[int(k)]
            data = value
            if value is None:
                return None
        else:
            return None
    return value


def dict_update_deep(d, u):
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, (collections.Mapping, collections.abc.Mapping)):
            d[k] = v
        elif isinstance(v, (collections.Mapping, collections.abc.Mapping)):
            d[k] = dict_update_deep(dv, v)
        else:
            d[k] = v
    return d
