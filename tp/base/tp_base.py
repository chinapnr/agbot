import re
from typing import Type

from agbot.constant.ag_enum import TestStatus, Conf
from agbot.core.model.context import VerticalContext
from agbot.core.tp.tp_context import TpContext
from agbot.core.tp.tp_interface import TpInterface
from agbot.core.tp.tp_model import TpConf
from agbot.core.utils import is_not_blank
from tp.base import exp


class TpBase(TpInterface):
    # 类的初始化过程
    # 2018.3.12 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpInterface.__init__(self, tp_conf, vertical_context)
        self.tp_conf = tp_conf
        # 请求参数
        self.req_param = {}
        # 期望返回参数
        self.expect_dict = {}
        self.conf_enum = TpConf
        self.vertical_context = vertical_context

    # 配置枚举
    def get_conf_enum(self) -> Type[Conf]:
        return self.conf_enum

    # 预处理
    def pre_handler(self):
        pass

    # 准备请求参数
    def build_request(self):
        # 请求数据
        tc_data_dict = self.vertical_context.tc_context.tc_detail.data

        # 配置的请求参数名称
        if self.tp_conf.get('req_data'):
            req_data = self.tp_conf.get('req_data')
            if isinstance(req_data, str):
                params_name_list = req_data.split(',')
                self.req_param = get_params_dict(params_name_list, tc_data_dict)
            else:
                self.req_param = req_data
        return self.req_param

    # 测试案例的执行
    def execute(self, request):
        raise NotImplementedError

    # 预期结果的校验
    def test_status(self) -> TestStatus:
        try:
            if not is_not_blank(self.tp_conf.get('expect_data')):
                return TestStatus.PASSED
            else:
                expression = self.tp_conf.get('expect_data')
                passed = self.run_exp(expression)
                if passed:
                    return TestStatus.PASSED
                else:
                    return TestStatus.NOT_PASSED
        except Exception as e:
            raise Exception('test_result error, make sure [expect_data] is correct, cause: ' + str(e))

    def run_exp(self, expression):
        env = {'curr_resp': self.vertical_context.tc_context.current_tp_context.response.content,
               'resp': {tp_ctx.id: tp_ctx.response.content
                        for tp_ctx in filter(lambda c: isinstance(c, TpContext) and c.response is not None,
                                             self.vertical_context.tc_context.tp_and_plugin_context_list)},
               'global': self.vertical_context.task_context.task_model.global_var,
               'tc_data': self.vertical_context.tc_context.tc_detail.data}

        env.update(self.vertical_context.tc_context.current_tp_context.response.content)
        if self.vertical_context.tc_context.current_tp_context.assertion is None:
            self.vertical_context.tc_context.current_tp_context.assertion = []
        assertion = self.vertical_context.tc_context.current_tp_context.assertion
        assertion.extend([{'assert_way': 'exp', 'assertion': expression}, env])
        return exp.run(expression, env)

    # 后处理
    def post_handler(self):
        pass


# 根据参数列表获取指定参数
# 2018.7.10 create by yanan.wu #904499
def get_params_dict(name_list, data_dict):
    target_dict = {}
    for name in name_list:
        if re.compile('\=').search(name):
            real_name = name.split('=', 1)[0]
            target_dict[real_name] = name.split('=', 1)[1]
        else:
            target_dict[name] = data_dict.get(name)
    return target_dict