import asyncio
from datetime import datetime
from typing import List

from fishbase import logger

from .task_context import TaskContext
from .task_detail import TaskDetail
from .task_exec import TaskExecutor
from ..job.job_context import JobContext
from ..job.job_exec_coroutine import JobExecutorCoroutine
from ..utils import chunks
from ...constant.ag_enum import TestStatus
from ...tools.ag_error import Scope, ErrorType, ErrorInfo


class TaskExecutorCoroutine(TaskExecutor):

    def __init__(self,
                 sys_conf_dict,
                 executor):
        TaskExecutor.__init__(self, sys_conf_dict, executor)
        self.__job_executor = JobExecutorCoroutine(sys_conf_dict, executor)
        self.__executor = executor
        pass

    async def do_execute(self, task_ctx: TaskContext, task_detail: TaskDetail):
        try:
            job_matrix = list(chunks(task_detail.job_detail_list, task_ctx.task_model.job_concurrency))
            job_ctx_list: List[JobContext] = []
            for job_chunk in job_matrix:
                execute_job_future_list = [
                    self.__job_executor.execute(task_ctx, job_detail)
                    for job_detail in job_chunk]
                job_ctx_list.extend(await asyncio.gather(*execute_job_future_list))

            task_ctx.end_time = datetime.now()
            task_ctx.job_context_list = job_ctx_list
            task_ctx.status = TestStatus.PASSED \
                if all(job_ctx.status == TestStatus.PASSED for job_ctx in job_ctx_list) \
                else TestStatus.NOT_PASSED
        except BaseException as e:
            logger.exception('TaskExecutorCoroutine do_execute error, task_id={}, cause: {}'
                             .format(task_detail.task_model.id, str(e)))
            task_ctx.status = TestStatus.ERROR
            task_ctx.end_time = datetime.now()
            task_ctx.error = ErrorInfo(Scope.TASK, ErrorType.RUNTIME_ERROR, str(e))
