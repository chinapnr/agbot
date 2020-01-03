# coding=utf-8
# @Time    : 2018/10/09 16:31
# @Desc    : tp执行类

import collections
import json
import time
from datetime import datetime

from fishbase import logger

from .tp_context import TpContext, TpRequest, TpResponse
from .tp_interface import TpInterface
from .tp_model import TpConf
from ..model.context import VerticalContext
from ..plugin.plugin_context import PluginContext
from ..plugin.plugin_exec import PluginExecutor
from ..plugin.plugin_manager_static import PluginsManagerStatic
from ..utils import is_not_blank, resolve_placeholder, assert_no_config_missing
from ...constant.ag_enum import TestStatus
from ...db.db_tool import DBUtils
from ...db.table_testpoint_log import TableTestPointLog
from ...tools.ag_error import Scope, ErrorType, ErrorInfo
from ...tools.attr_dict import AttrDict


class ExpFunc:

    @staticmethod
    def json_loads(s, encoding=None):
        return AttrDict.from_nested_dict(json.loads(s, encoding=encoding))


_exp_env_global = {'func': ExpFunc()}


class TpExecutor:

    def __init__(self):
        self.__tp_manager = PluginsManagerStatic("tp")
        self.__plugin_executor = PluginExecutor()

    def __do_execute(self,
                     vertical_ctx: VerticalContext,
                     tp_id: str,
                     tp_ctx: TpContext):
        conf_dict_raw = vertical_ctx.job_context.job_model.tp_table.get(tp_id)
        assert conf_dict_raw is not None, '[{}] not found'.format(tp_id)

        precondition = conf_dict_raw.get(TpConf.precondition.key)
        if precondition is not None:
            test_status, env, e = self._run_python_exp(vertical_ctx, precondition)
            if e is not None:
                raise e
            if test_status == TestStatus.NOT_PASSED:
                tp_ctx.status = TestStatus.SKIP
                return

        tp_type = tp_id.split('_')[1]
        tp_ctx.type = tp_type

        before_plugin_id = conf_dict_raw.get(TpConf.before_execute.key)
        # before 插件
        if is_not_blank(before_plugin_id):
            before_plugin_ctx = PluginContext(before_plugin_id, datetime.now())
            vertical_ctx.tc_context.tp_and_plugin_context_list.append(before_plugin_ctx)
            try:
                self.__plugin_executor.do_execute(vertical_ctx, before_plugin_id, before_plugin_ctx)
            except BaseException as e:
                raise RuntimeError('plugin [{}] error: {}'.format(before_plugin_id, str(e))) from e

        # 替换占位符
        conf_dict, replacement = resolve_placeholder(conf_dict_raw, vertical_ctx)
        tp_ctx.conf = conf_dict
        tp_ctx.replacement.extend(replacement)

        # 执行tp
        try:
            tp_obj: TpInterface = self.__tp_manager.run_plugin(tp_type, conf_dict, vertical_ctx)
        except BaseException as e:
            raise RuntimeError('tp [{}] error: {}'.format(tp_id, str(e)))

        assert_no_config_missing(tp_id, tp_obj.get_conf_enum(), conf_dict)
        tp_ctx.name = conf_dict.get(TpConf.tp_name.key, '')

        tp_obj.pre_handler()

        request_content = tp_obj.build_request()
        tp_ctx.request = TpRequest(request_content)

        # tp等待
        if is_not_blank(conf_dict.get(TpConf.req_wait_time.key)):
            # 此处接口请求并发数与系统性能有关，休眠时间需要修改为可配置
            time.sleep(float(conf_dict.get(TpConf.req_wait_time.key)))

        resp_content, resp_code = tp_obj.execute(request_content)
        tp_ctx.response = TpResponse(resp_content, resp_code)

        after_plugin_id = conf_dict_raw.get(TpConf.after_execute.key)
        if is_not_blank(after_plugin_id):
            after_plugin_ctx = PluginContext(after_plugin_id, datetime.now())
            vertical_ctx.tc_context.tp_and_plugin_context_list.append(after_plugin_ctx)
            try:
                self.__plugin_executor.do_execute(vertical_ctx, after_plugin_id, after_plugin_ctx)
            except BaseException as e:
                raise RuntimeError('plugin [{}] error: {}'.format(after_plugin_id, str(e))) from e

        assert_way = conf_dict_raw.get(TpConf.assert_way.key, '').strip()
        if assert_way == 'python':
            expression = conf_dict.get(TpConf.assertion.key)
            assert is_not_blank(expression), 'missing [assertion]'
            test_status, env, e = self._run_python_exp(vertical_ctx, expression)
            tp_ctx.status = test_status
            tp_ctx.assertion = [{'assert_way': 'python', 'assertion': expression}, env]
            if tp_ctx.status == TestStatus.ERROR:
                raise e
        elif assert_way == 'plugin':
            assert_plugin_id = conf_dict_raw.get(TpConf.assertion.key)
            assert is_not_blank(assert_plugin_id), 'missing [assertion]'
            assert_plugin_ctx = PluginContext(after_plugin_id, datetime.now())
            vertical_ctx.tc_context.tp_and_plugin_context_list.append(assert_plugin_ctx)
            try:
                self.__plugin_executor.do_execute(vertical_ctx, assert_plugin_id, assert_plugin_ctx)
            except BaseException as e:
                raise RuntimeError('plugin [{}] error: {}'.format(assert_plugin_id, str(e))) from e
        else:
            # 只有当 current_tp_context.resp.content 是 dict才断言结果
            if isinstance(vertical_ctx.tc_context.current_tp_context.response.content, collections.Mapping):
                test_status = tp_obj.test_status()
                tp_ctx.status = test_status
            else:
                tp_ctx.status = TestStatus.NOT_PASSED

        assert isinstance(tp_ctx.status, TestStatus), 'tp_ctx.status must be a instance of TestStatus'
        tp_obj.post_handler()
        tp_ctx.end_time = datetime.now()

    def _run_python_exp(self, vertical_context, expression):
        env = {'resp': {tp_ctx.id: tp_ctx.response.content
                        for tp_ctx in filter(lambda c: isinstance(c, TpContext) and c.response is not None,
                                             vertical_context.tc_context.tp_and_plugin_context_list)},
               'global': vertical_context.task_context.task_model.global_var,
               'tc_data': vertical_context.tc_context.tc_detail.data}
        if vertical_context.tc_context.current_tp_context.response is not None:
            env['curr_resp'] = vertical_context.tc_context.current_tp_context.response.content
        env = AttrDict.from_nested_dict(env)

        python_exp_lines = expression.split('\n')
        python_exp_lines[-1] = '_python_exp_result=' + python_exp_lines[-1]
        python_exp_content = '\n'.join(python_exp_lines)
        try:
            exec(python_exp_content, _exp_env_global, env)
        except Exception as e:
            return TestStatus.ERROR, env, e
        python_exp_result = env.get('_python_exp_result')
        if python_exp_result:
            return TestStatus.PASSED, env, None
        else:
            return TestStatus.NOT_PASSED, env, None

    def do_execute(self,
                   vertical_ctx: VerticalContext,
                   tp_id: str,
                   tp_ctx: TpContext
                   ):
        """
        该函数不会抛出任何异常, 必定会返回一个最终态的TpContext
        :param vertical_ctx: vertical_ctx
        :param tp_id: tp_id
        :param tp_ctx: tp_ctx
        :return:
        """
        try:
            self.__do_execute(vertical_ctx, tp_id, tp_ctx)
        except BaseException as e:
            logger.exception('TpExecutor error: task_id:{}, tc_id:{}, tp_id:{}, cause: {}, tc_ctx: {}'
                             .format(vertical_ctx.task_context.task_model.id,
                                     vertical_ctx.tc_context.tc_detail.id,
                                     tp_id,
                                     str(e),
                                     str(vertical_ctx.tc_context)))
            tp_ctx.end_time = datetime.now()
            tp_ctx.status = TestStatus.ERROR
            tp_ctx.error = ErrorInfo(Scope.TP, ErrorType.RUNTIME_ERROR, str(e))

    def process_tp_context(self,
                           vertical_ctx: VerticalContext,
                           tp_ctx: TpContext):
        tp_log_dict = {'sys_date': str(datetime.today().strftime('%Y%m%d')),
                       'tp_type': tp_ctx.type,
                       'task_id': vertical_ctx.task_context.task_model.id,
                       'tc_seq_id': vertical_ctx.tc_context.seq_id,
                       'tp_id': tp_ctx.id,
                       'tp_result': tp_ctx.status.value,
                       'start_time': tp_ctx.start_time,
                       'end_time': tp_ctx.end_time,
                       'tp_name': tp_ctx.name,
                       'placeholder_info': '\n'.join(["{} = {}".format(k, v)
                                                      for k, v in tp_ctx.replacement])[:4000]
                       }
        if tp_ctx.error is not None:
            tp_log_dict['error_info'] = str(tp_ctx.error.message)[:4000]
        if tp_ctx.request is not None:
            tp_log_dict['requ_param'] = json.dumps(tp_ctx.request.content, ensure_ascii=False)[:4000]
        if tp_ctx.response is not None:
            tp_log_dict['result_value'] = json.dumps(tp_ctx.response.content, ensure_ascii=False)[:4000]
            tp_log_dict['resp_code'] = tp_ctx.response.code
        if tp_ctx.assertion is not None:
            tp_log_dict['assertion_info'] = json.dumps(tp_ctx.assertion, ensure_ascii=False)[:4000]
        DBUtils.add(TableTestPointLog, tp_log_dict, is_flush=True)
