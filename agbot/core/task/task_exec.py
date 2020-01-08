from abc import abstractmethod
from datetime import datetime
from typing import Dict

from fishbase import logger

from .task_context import TaskContext
from .task_detail import TaskDetail
from ..model.context import VerticalContext
from ..utils import event_loop
from ...db.db_tool import DBUtils
from ...db.table_task_log import TableTaskLog, update_task_with_task_id

_context_processor_list = []


def register_context_processor(context_processor):
    if context_processor not in _context_processor_list:
        _context_processor_list.append(context_processor)


class TaskExecCommon:

    def __init__(self, sys_conf_dict: Dict):
        self.__sys_conf_dict = sys_conf_dict

    def before_do_execute(self, task_ctx: TaskContext, task_detail: TaskDetail):
        log_dict = dict()
        log_dict['sys_date'] = str(datetime.today().strftime('%Y%m%d'))
        log_dict['task_id'] = task_ctx.task_model.id
        log_dict['task_src'] = task_ctx.task_model.task_src
        log_dict['task_status'] = task_ctx.status.value
        log_dict['start_time'] = task_ctx.start_time
        log_dict['crt_sys'] = task_ctx.task_model.crt_sys
        log_dict['crt_user'] = task_ctx.task_model.crt_user
        # 配置统一读取，新加参数 job_list
        log_dict['job_list'] = ','.join([job_detail.job_model.id for job_detail in task_detail.job_detail_list])
        DBUtils.add(TableTaskLog, log_dict)

    def process_task_context(self, task_ctx: TaskContext):
        for ctx_processor in _context_processor_list:
            try:
                ctx_processor(VerticalContext(self.__sys_conf_dict, task_ctx))
            except BaseException as e:
                logger.exception('TaskExecCommon ctx_processor error: {}, cause: {}, job_ctx: {}'
                                 .format(task_ctx.task_model.id, str(e), str(task_ctx)))

        task_log_dict = dict()
        task_log_dict['task_id'] = task_ctx.task_model.id
        task_log_dict['task_status'] = task_ctx.status.value
        task_log_dict['end_time'] = task_ctx.end_time
        task_log_dict['error_info'] = str(task_ctx.error.message)[:1024] if task_ctx.error is not None else None
        update_task_with_task_id(task_log_dict)


class TaskExecutor:

    def __init__(self,
                 sys_conf_dict: Dict,
                 executor):
        self.__sys_conf_dict = sys_conf_dict
        self.__executor = executor
        self.__task_exec_common = TaskExecCommon(sys_conf_dict)

    async def execute(self, task_detail: TaskDetail):
        task_ctx = TaskContext(task_detail.task_model, datetime.now())
        await self.before_do_execute(task_ctx, task_detail)
        await self.do_execute(task_ctx, task_detail)
        await self.process_task_context(task_ctx)
        return task_ctx

    async def before_do_execute(self, task_ctx, task_detail: TaskDetail) -> TaskContext:
        await event_loop.run_in_executor(self.__executor,
                                         self.__task_exec_common.before_do_execute,
                                         task_ctx,
                                         task_detail)
        return task_ctx

    async def process_task_context(self, task_ctx: TaskContext):
        await event_loop.run_in_executor(self.__executor,
                                         self.__task_exec_common.process_task_context,
                                         task_ctx)

    @abstractmethod
    async def do_execute(self, task_ctx: TaskContext, task_detail: TaskDetail):
        pass
