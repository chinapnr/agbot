import json
import xml.etree.ElementTree as ET
from ast import literal_eval
from enum import Enum
from json import JSONDecodeError
from urllib import parse

import requests
from fishbase.fish_logger import logger
from requests import RequestException

from agbot.core.utils import resolve_placeholder
from tp.base import exp
from ..base.tp_base import TpBase, TestStatus, Conf, VerticalContext, get_params_dict


# ApiTestPoint
class ApiTestPoint(TpBase):
    
    # 类的初始化过程
    # 2018.3.12 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = ApiTestPointEnum
        self.__header = {}
        self.__resp_code = ''
        self.__file = {}
        self.vertical_context = vertical_context
    
    # 准备请求参数
    # 2018.3.12 create by yanan.wu #748921
    # 2018.5.22 edit by yang.xu #848884
    def build_request(self):
        tc_ctx_dict = self.vertical_context.tc_context
        try:
            # 获取请参
            TpBase.build_request(self)
            
            # 组装heard
            # 20190403 edit by jun.hu
            # 新加支持 http_header 配置字典写法
            head_dict = {}
            tc_data_dict = tc_ctx_dict.tc_detail.data
            tp_conf_header = self.tp_conf.get('http_header', None)
            if tp_conf_header:
                try:
                    # 默认配置支持字典的写法
                    self.__header = json.loads(tp_conf_header)
                except Exception as ex:
                    logger.info(str(ex))
                    # 字典取值发生错误时取逗号隔开的值
                    params_name_list = self.tp_conf.get('http_header').split(',')
                    for name in params_name_list:
                        head_dict[name] = tc_data_dict.get(name)
                    self.__header = head_dict
            
            if self.tp_conf.get('upload_file_path'):
                upload_file_path = self.tp_conf.get('upload_file_path')
                upload_file_path = upload_file_path.split('/')[-1]
                upload_file = next(filter(lambda a: a.id.endswith(upload_file_path),
                                          self.vertical_context.job_context.job_model.attachment),
                                   None)
                assert upload_file is not None, 'file not found: {}'.format(upload_file_path)
                files = {
                    self.tp_conf.get('upload_file_name'): upload_file.content
                }
                self.__file = files
            
            # 构造json请求参数
            if self.tp_conf.get('json_param_name'):
                json_param_dict = {}
                if self.tp_conf.get('req_json_data'):
                    params_name_list = self.tp_conf.get('req_json_data').split(',')
                    for name in params_name_list:
                        json_param_dict[name] = tc_data_dict.get(name)
                # json参数放入请参字典
                self.req_param[self.tp_conf.get('json_param_name')] = json.dumps(json_param_dict)

            return {'content': self.req_param, 'header': self.__header}
        
        except Exception as e:
            logger.exception('tp->api:build params error', str(e))
            raise Exception(str(e))
    
    # 测试案例的执行
    # 2018.3.12 create by yanan.wu #748921
    # 2018.6.19 edit by xin.guo #869614
    def execute(self, request):
        content = request.get('content')
        # 请求地址可从数据文件中读取
        api_url = self.tp_conf.get('http_url')
        # 获取 http 请求方法名称
        method = self.tp_conf.get('http_method')
        # 发起接口调用请求并接收响应
        try:
            # 反射得到 http 的方法
            exec_func = getattr(requests, method.lower())
            # 请求超时时间
            try:
                timeout = int(self.tp_conf.get('timeout', 10))
            except Exception as _:
                timeout = 10
            timeout = min(timeout, 120)
            
            # 20190315 edit by jun.hu
            #  根据  conf 中的 content-type 来决定请求数据组织方式
            if self.__header.get('Content-Type') == 'application/json':
                response = exec_func(api_url, json=content, headers=self.__header, files=self.__file, timeout=timeout)
            else:
                if method.lower() == 'delete':
                    response = exec_func(api_url, headers=self.__header, timeout=timeout)
                else:
                    files = self.__file
                    response = exec_func(api_url, content, headers=self.__header, files=files, timeout=timeout)
            
            self.__resp_code = str(response.status_code)

            try:
                content = response.json()
                logger.info('[{}, {}, {}] tp->api load as json: {}, {}'
                            .format(self.vertical_context.task_context.task_model.id,
                                    self.vertical_context.job_context.job_model.id,
                                    self.vertical_context.tc_context.tc_detail.id,
                                    response.status_code,
                                    content))
                return content, self.__resp_code
            except JSONDecodeError as e:
                logger.info('[{}, {}, {}] tp->api load as json error: {}, {}'
                            .format(self.vertical_context.task_context.task_model.id,
                                    self.vertical_context.job_context.job_model.id,
                                    self.vertical_context.tc_context.tc_detail.id,
                                    response.status_code,
                                    response.text))
                pass

            try:
                content = self.__get_xml_dict(response.text)
                logger.info('[{}, {}, {}] tp->api load as xml: {}, {}'
                            .format(self.vertical_context.task_context.task_model.id,
                                    self.vertical_context.job_context.job_model.id,
                                    self.vertical_context.tc_context.tc_detail.id,
                                    response.status_code,
                                    content))
                return content, self.__resp_code
            except Exception as e:
                logger.info('[{}, {}, {}] tp->api load as xml error: {}, {}'
                            .format(self.vertical_context.task_context.task_model.id,
                                    self.vertical_context.job_context.job_model.id,
                                    self.vertical_context.tc_context.tc_detail.id,
                                    response.status_code,
                                    response.text))
                pass
            
            if isinstance(response.text, str) and self.tp_conf.get('resp_default_key', ''):
                return {self.tp_conf.get('resp_default_key'): response.text}, self.__resp_code

            return response.text, self.__resp_code
        
        except RequestException as e:
            logger.error('[{}, {}, {}] tp->api连接异常'
                         .format(self.vertical_context.task_context.task_model.id,
                                 self.vertical_context.job_context.job_model.id,
                                 self.vertical_context.tc_context.tc_detail.id))
            raise RuntimeError('api连接异常, {}'.format(str(e)))
        except RuntimeError as e:
            logger.exception('[{}, {}, {}] tp->api运行时异常, {}'
                             .format(self.vertical_context.task_context.task_model.id,
                                     self.vertical_context.job_context.job_model.id,
                                     self.vertical_context.tc_context.tc_detail.id,
                                     str(e)))
            raise RuntimeError('api运行时异常, {}'.format(str(e)))
    
    # 预期结果的校验
    # 2018.3.12 create by yanan.wu #748921
    def test_status(self):
        tc_ctx = self.vertical_context.tc_context
        try:
            # 配置的期望参数名称
            if self.tp_conf.get('expect_data'):
                self.resolve_expect_data(tc_ctx)
                
                params_name_list = self.tp_conf.get('expect_data').split(',(?=(?:[^\"]*(?:"[^\"]*")?[^\"]*)*$)')
                # 如果期望判断首个值满足表达式，则认为是表达式
                if exp.is_exp(params_name_list[0]):
                    diff_key_set = set()
                    for e in params_name_list:
                        if not self.run_exp(e):
                            diff_key_set.add(e)
                    
                    if not diff_key_set:
                        return TestStatus.PASSED
                    else:
                        logger.info('[{}, {}, {}] tp->api 断言不通过: {} @ {}'
                                    .format(self.vertical_context.task_context.task_model.id,
                                            self.vertical_context.job_context.job_model.id,
                                            self.vertical_context.tc_context.tc_detail.id,
                                            params_name_list,
                                            self.vertical_context.tc_context
                                            ))
                        return TestStatus.NOT_PASSED
            
            # 获取数据文件期望返回的状态码
            if self.tp_conf.get('expect_resp_code'):
                if self.__resp_code != self.tp_conf.get('expect_resp_code'):
                    return TestStatus.NOT_PASSED
                else:
                    return TestStatus.PASSED
            
            # 是否需要 urldecode
            if self.tp_conf.get('resp_urldecode_name'):
                name_list = self.tp_conf.get('resp_urldecode_name').split(',')
                response_str = self.__response_urldecode(str(tc_ctx.current_tp_context.response.content), name_list)
            else:
                response_str = tc_ctx.current_tp_context.response.content
            
            if response_str is not None:
                # 校验期望值，验证返回码是否与期望返回码保持一致
                diff_key_set = set()
                diff_key_set = self.__expect_dict_check(self.expect_dict, tc_ctx.current_tp_context.response.content, diff_key_set)
                
                check_expect_flag = not diff_key_set
                check_type = self.tp_conf.get('check_type') \
                    if self.tp_conf.get('check_type') else CheckExpectType.EQUAL.value
                if CheckExpectType.UNEQUAL.value == check_type:
                    if check_expect_flag:
                        check_expect_flag = TestStatus.NOT_PASSED
                    else:
                        check_expect_flag = TestStatus.PASSED
                else:
                    if check_expect_flag:
                        check_expect_flag = TestStatus.PASSED
                    else:
                        check_expect_flag = TestStatus.NOT_PASSED
                
                logger.info('check result:' + str(
                    check_expect_flag) + ' diff set:' + str(diff_key_set))
            else:
                check_expect_flag = TestStatus.NOT_PASSED
                logger.info('check result:' + str(check_expect_flag) + ' target response is none.')
        
        except Exception as e:
            logger.exception('[{}, {}, {}] tp->api期望值判断异常: {} @ {}'
                             .format(self.vertical_context.task_context.task_model.id,
                                     self.vertical_context.job_context.job_model.id,
                                     self.vertical_context.tc_context.tc_detail.id,
                                     str(e),
                                     self.vertical_context.tc_context
                                     ))
            raise Exception('期望值判断异常: {}: {}'.format(str(e.__class__.__name__), str(e)))
        
        return check_expect_flag
    
    # 后处理
    def post_handler(self):
        pass
    
    # 对指定字段进行解码
    # 输入：
    # response_str: 待解码字符，json 形式
    # name_list: key 值列表
    # ---
    # 2018.4.10 create by yanan.wu #802968
    def __response_urldecode(self, response_str, name_list):
        # 转换为 json 格式
        response_dict = literal_eval(response_str)
        
        # 逐个对需要解码的字段进行解码
        for name in name_list:
            print(response_dict.get(name))
            response_dict[name] = self.__get_urldecode(response_dict.get(name))
        return str(response_dict)
    
    # 实现单个字符 urldecode
    # 输入：
    # obj_str: 编码串
    # ---
    # 2018.4.10 create by yanan.wu #802968
    def __get_urldecode(obj_str):
        return parse.unquote(obj_str)
    
    # 解析 xml 生成任务列表
    # create by yang.xu 2018.8.28
    def __get_xml_dict(self, response_str):
        root = ET.fromstring(response_str)
        root_dict = {}
        result_dict = {}
        root_dict = self.__ergodic_node(root, root_dict)
        result_dict[root.tag] = root_dict
        return result_dict
    
    # 遍历xml节点
    # create by yang.xu 2018.8.28
    def __ergodic_node(self, root, root_dict):
        # 判断是否有子节点
        for node in root:
            if 0 != len(node.getchildren()):
                child_dict = self.__ergodic_node(node, {})
                # 判断key是否已经存在
                if node.tag in root_dict.keys():
                    if type(root_dict.get(node.tag)) == list:
                        root_dict.get(node.tag).append(child_dict)
                    else:
                        temp_list = list()
                        temp_list.append(root_dict.get(node.tag))
                        temp_list.append(child_dict)
                        root_dict[node.tag] = temp_list
                else:
                    root_dict[node.tag] = child_dict
            else:
                self.__set_node_value(node, root_dict)
        
        if 0 == len(root.getchildren()):
            self.__set_node_value(root, root_dict)
        
        return root_dict
    
    # set节点的value值
    # create by yang.xu 2018.8.28
    def __set_node_value(self, node, node_dict):
        # 判断key是否已经存在
        if node.text is None:
            value = ''
        else:
            value = node.text
        
        if node.tag in node_dict.keys():
            if type(node_dict.get(node.tag)) == list:
                node_dict.get(node.tag).append(value)
            else:
                temp_list = list()
                temp_list.append(node_dict.get(node.tag))
                temp_list.append(value)
                node_dict[node.tag] = temp_list
        else:
            node_dict[node.tag] = value
    
    # 遍历dict，判断期望
    # create by yang.xu 2018.8.28
    # create by jun.hu 2019.5.13
    def __expect_dict_check(self, expect_dict, result, diff_key_set):
        # initial_result = result
        for ek, ev in expect_dict.items():
            temp_res = dict()
            # 这里是在取类似于 resp.result_value.0.key 形式的 value
            # todo 后续形如 resp 的取值均使用占位符 $，这样在替换占位符的时候就能进行统一替换
            ek_list = ek.split('.')
            for i in range(len(ek_list) - 1):
                temp_res = temp_res if temp_res else result
                if type(temp_res) == dict:
                    temp_res = temp_res.get(ek_list[i])
                else:
                    temp_res = temp_res[int(ek_list[i])]
                try:
                    temp_res = literal_eval(temp_res)
                except Exception as _:
                    pass
            
            if not temp_res:
                temp_res = result
            
            check_key = ek_list[len(ek_list) - 1]
            if type(temp_res) == dict:
                get_value = temp_res.get(check_key)
            elif type(temp_res) == list:
                get_value = temp_res[int(check_key)]
            else:
                diff_key_set.add(ek)
                continue
            
            if not ApiTestPoint.__is_number_str_equal(ev, get_value):
                diff_key_set.add(ek)
        
        return diff_key_set
    
    # create by jun.hu 2019.03.20
    @staticmethod
    def __is_number_str_equal(number_str, number):
        """
        判断返回报文期望值类型不相等的时候
        数字字符串是否和数字值相等
        eg: '12.04', 12.04 ==> True
        :param number_str: (string) 数字字符串
        :param number: (int, float, string) 返回报文中的数字
        :return:
        """
        try:
            if (type(number) != type(number_str) and
                    isinstance(number, (float, int)) and isinstance(number_str, str)):
                return True if float(number_str) == number else False
            else:
                return True if number_str == number else False
        except ValueError as ex:
            # float(number_str) 可能发生 ValueError 错误
            logger.error(str(ex))
            return False

    # 处理期望值中的占位符
    def resolve_expect_data(self, tc_ctx):
        # 存在四种格式的断言配置需要兼容 key:value,key:value; key=value,key=value; key==value; key,key
        logger.info("tp_api: {} 期望值替换占位符前为 {}".format(tc_ctx.current_tp_context.id, self.tp_conf.get('expect_data')))

        params_name_list = self.tp_conf.get('expect_data').split(',(?=(?:[^\"]*(?:"[^\"]*")?[^\"]*)*$)')
        # 处理 key==value 形式
        if not exp.is_exp(params_name_list[0]):
            params_name_list = self.tp_conf.get('expect_data').split(',')
            # 将 key=value;key,key;key:value 形式转换成字典，需要赋值 self.expect_dict
            expect_dict_raw = get_params_dict(params_name_list, tc_ctx.tc_detail.data)
            expect_dict, replacement = resolve_placeholder(expect_dict_raw,
                                                           self.vertical_context)
            expect = [expect_dict]
            self.expect_dict = expect_dict
        else:
            expect = []

        logger.info("tp_api: {} 期望值替换占位符后为 {}".format(tc_ctx.current_tp_context.id, expect))
        tc_ctx.current_tp_context.assertion = expect


# 期望结果检查类型
# 2018.7.04 create by yanan.wu #806640
class CheckExpectType(Enum):
    EQUAL = '01'
    UNEQUAL = '02'


# API配置文件枚举
class ApiTestPointEnum(Conf):
    req_data = 'req_data', '请求参数', False, ''
    expect_data = 'expect_data', '期望值', False, ''
    http_url = 'http_url', '目标系统地址', True, ''
    http_method = 'http_method', '接口调用方式', True, ''
    http_header = 'http_header', '请求头', False, '01'
    resp_urldecode_name = 'resp_urldecode_name', '需要decode的参数', False, ''
    check_type = 'check_type', '校验方式', False, ''
    tp_name = 'tp_name', '测试点的名称', True, ''
    before_execute = 'before_execute', '插件, 测试点执行前', False, ''
    after_execute = 'after_execute', '插件, 测试点执行后', False, ''
    content_type = 'content_type', 'api 请求 content-type', False, ''
