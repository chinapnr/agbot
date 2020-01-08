import asyncio
from abc import ABCMeta
from datetime import datetime

from fishbase import logger

from .job_context import JobContext
from .job_detail import JobDetail
from ..job.job_exec import JobExecCommon
from ..task.task_context import TaskContext
from ..tc.tc_context import TcContext
from ..tc.tc_exec import TcExecutor
from ..utils import event_loop, chunks
from ...constant.ag_enum import TestStatus
from ...tools.ag_error import Scope, ErrorType, ErrorInfo


class JobExecutorCoroutine:
    __metaclass__ = ABCMeta

    def __init__(self,
                 sys_conf_dict: dict,
                 executor):

        # 全局配置
        self.__sys_conf_dict = sys_conf_dict
        self.__executor = executor
        self.__tc_executor = TcExecutor(sys_conf_dict)
        self.__job_exec_common = JobExecCommon(sys_conf_dict)

    async def execute(self,
                      task_ctx: TaskContext,
                      job_detail: JobDetail) -> JobContext:
        job_ctx = JobContext(job_detail.job_model, datetime.now())
        await self.before_do_execute(task_ctx, job_ctx, job_detail)
        await self.do_execute(task_ctx, job_ctx, job_detail)
        await self.process_job_context(task_ctx, job_ctx)
        return job_ctx

    async def before_do_execute(self,
                                task_ctx: TaskContext,
                                job_ctx: JobContext,
                                job_detail: JobDetail):
        await event_loop.run_in_executor(self.__executor,
                                         self.__job_exec_common.before_do_execute,
                                         task_ctx,
                                         job_ctx,
                                         job_detail)

    async def process_job_context(self, task_ctx: TaskContext, job_ctx: JobContext):
        await event_loop.run_in_executor(self.__executor,
                                         self.__job_exec_common.process_job_context,
                                         task_ctx,
                                         job_ctx)

    async def do_execute(self,
                         task_ctx: TaskContext,
                         job_ctx: JobContext,
                         job_detail: JobDetail):
        try:
            tc_context_list = []
            tc_matrix = list(chunks(job_detail.tc_detail_list, job_detail.job_model.concurrency))
            for tc_detail_list in tc_matrix:
                tc_task_list_chunk = [event_loop.run_in_executor(self.__executor, self.__tc_execute_process,
                                                                 task_ctx, job_ctx, tc_detail)
                                      for tc_detail in tc_detail_list]
                tc_ctx_list_chunk = await asyncio.gather(*tc_task_list_chunk)
                tc_context_list.extend(tc_ctx_list_chunk)

            job_ctx.end_time = datetime.now()
            job_ctx.tc_context_list = tc_context_list
            job_ctx.status = TestStatus.PASSED \
                if all(tc_ctx.status == TestStatus.PASSED for tc_ctx in tc_context_list) \
                else TestStatus.NOT_PASSED
        except BaseException as e:
            logger.exception(
                'JobExecutorCoroutine do_execute error; job: {}; cause: {}'.format(str(job_detail), str(e)))
            job_ctx.status = TestStatus.ERROR
            job_ctx.end_time = datetime.now()
            job_ctx.error = ErrorInfo(Scope.JOB, ErrorType.RUNTIME_ERROR, str(e))

    def __tc_execute_process(self, task_ctx, job_ctx, tc_detail):
        tc_ctx = TcContext(tc_detail, datetime.now())
        try:
            self.__tc_executor.before_do_execute(task_ctx, job_ctx, tc_ctx)
            self.__tc_executor.do_execute(task_ctx, job_ctx, tc_ctx)
            self.__tc_executor.process_tc_context(task_ctx, job_ctx, tc_ctx)
        except BaseException as e:
            logger.exception(
                'JobExecutorCoroutine __tc_execute_process error; tc: {}; cause: {}'.format(str(tc_detail), str(e)))
            tc_ctx.end_time = datetime.now()
            tc_ctx.status = TestStatus.ERROR
            tc_ctx.error = ErrorInfo(Scope.TC, ErrorType.RUNTIME_ERROR, str(e))
        return tc_ctx
