from datetime import datetime
from typing import Dict

from fishbase import logger

from .tc_context import TcContext
from ..job.job_context import JobContext
from ..model.context import VerticalContext
from ..plugin.plugin_context import PluginContext
from ..plugin.plugin_exec import PluginExecutor
from ..task.task_context import TaskContext
from ..tp.tp_context import TpContext
from ..tp.tp_exec import TpExecutor
from ..utils import resolve_placeholder
from ...constant.ag_enum import TestStatus
from ...db.db_tool import DBUtils
from ...db.table_testcase_log import TableTestCaseLog
from ...tools.ag_error import Scope, ErrorType, ErrorInfo

_context_processor_list = []


def register_context_processor(context_processor):
    _context_processor_list.append(context_processor)


class TcExecutor:

    def __init__(self, sys_conf_dict: Dict):
        self.__plugin_executor = PluginExecutor()
        self.__tp_executor = TpExecutor()
        self.__sys_conf_dict = sys_conf_dict

    def before_do_execute(self,
                          task_ctx: TaskContext,
                          job_ctx: JobContext,
                          tc_ctx: TcContext):
        tc_detail = tc_ctx.tc_detail
        tc_log_dict = {'sys_date': str(datetime.today().strftime('%Y%m%d')),
                       'job_id': job_ctx.job_model.id,
                       'task_id': task_ctx.task_model.id,
                       'tc_id': tc_detail.id,
                       'test_result': tc_ctx.status.value,
                       'tc_flag': ','.join(tc_detail.flag_list),
                       'tc_weight': tc_detail.weight
                       }
        tc_log_obj = DBUtils.add(TableTestCaseLog, tc_log_dict, is_flush=True)
        tc_ctx.seq_id = tc_log_obj.tc_seq_id

    def __do_execute(self,
                     task_ctx: TaskContext,
                     job_ctx: JobContext,
                     tc_ctx: TcContext):
        vertical_ctx = VerticalContext(self.__sys_conf_dict, task_ctx, job_ctx, tc_ctx)

        for pre_plugin_id in job_ctx.job_model.pretreatment:
            pre_plugin_ctx = PluginContext(pre_plugin_id, datetime.now())
            tc_ctx.tp_and_plugin_context_list.append(pre_plugin_ctx)
            self.__plugin_executor.do_execute(vertical_ctx, pre_plugin_id, pre_plugin_ctx)

        conf_dict_raw = {
            'start_with': job_ctx.job_model.start_with
        }
        conf_dict, replacement = resolve_placeholder(conf_dict_raw, vertical_ctx)
        tc_ctx.replacement.extend(replacement)

        tc_ctx.status = TestStatus.PASSED
        for tp_id in conf_dict['start_with'].split(','):
            tp_ctx = TpContext(tp_id, datetime.now())
            tc_ctx.tp_and_plugin_context_list.append(tp_ctx)
            self.__tp_executor.do_execute(vertical_ctx, tp_id, tp_ctx)
            if tp_ctx.status == TestStatus.SKIP:
                tc_ctx.tp_and_plugin_context_list.remove(tp_ctx)

        tc_ctx.end_time = datetime.now()
        tc_ctx.status = TestStatus.PASSED \
            if all(tp_ctx.status == TestStatus.PASSED for tp_ctx in tc_ctx.tp_and_plugin_context_list) \
            else TestStatus.NOT_PASSED

    def do_execute(self,
                   task_ctx: TaskContext,
                   job_ctx: JobContext,
                   tc_ctx: TcContext):
        tc_detail = tc_ctx.tc_detail
        try:
            self.__do_execute(task_ctx, job_ctx, tc_ctx)
        except BaseException as e:
            logger.exception('TcExecutor error: {}, cause: {}, tc_ctx: {}'
                             .format(tc_detail.id, str(e), str(tc_ctx)))
            tc_ctx.end_time = datetime.now()
            tc_ctx.status = TestStatus.ERROR
            tc_ctx.error = ErrorInfo(Scope.TC, ErrorType.RUNTIME_ERROR, str(e))

    def process_tc_context(self,
                           task_ctx: TaskContext,
                           job_ctx: JobContext,
                           tc_ctx: TcContext):
        tc_log_dict = {
            'start_time': tc_ctx.start_time,
            'end_time': tc_ctx.end_time,
            'test_result': tc_ctx.status.value,
            'placeholder_info': '\n'.join(["{} = {}".format(k, v)
                                           for k, v in tc_ctx.replacement])
        }
        if tc_ctx.error is not None:
            tc_log_dict['error_info'] = str(tc_ctx.error.message)[:1024]
        DBUtils.update(TableTestCaseLog,
                       {'tc_seq_id': tc_ctx.seq_id},
                       tc_log_dict)
        vertical_ctx = VerticalContext(self.__sys_conf_dict, task_ctx, job_ctx, tc_ctx)
        for tp_ctx in tc_ctx.tp_and_plugin_context_list:
            if not isinstance(tp_ctx, TpContext):
                continue
            self.__tp_executor.process_tp_context(
                vertical_ctx,
                tp_ctx)

        for ctx_processor in _context_processor_list:
            try:
                ctx_processor(vertical_ctx)
            except BaseException as e:
                logger.exception('TcExecutor ctx_processor error: {}, cause: {}, tc_ctx: {}'
                                 .format(tc_ctx.tc_detail.id, str(e), str(tc_ctx)))
