import pickle
import re
from datetime import datetime, timedelta
from typing import Dict

import celery
import redis
from celery import Celery, chain, chord, group
from fishbase import logger

import ext
from .task_context import TaskContext
from .task_detail import TaskDetail
from .task_exec import TaskExecutor, TaskExecCommon
from ..job.job_context import JobContext
from ..job.job_detail import JobDetail
from ..job.job_exec import JobExecCommon
from ..tc.tc_context import TcContext
from ..tc.tc_exec import TcExecutor
from ..utils import event_loop, chunks, rotate
from ...agbot_config import agbot_config
from ...constant.ag_enum import TestStatus
from ...tools.ag_error import ErrorInfo, Scope, ErrorType

_celery_tc_executor = TcExecutor(agbot_config.sys_conf_dict)
_celery_job_exec_common = JobExecCommon(agbot_config.sys_conf_dict)
_celery_task_exec_common = TaskExecCommon(agbot_config.sys_conf_dict)

_celery_app = Celery('tasks')
_celery_app.config_from_object('conf.celery_conf')
redis_url = re.split('[@:/]', agbot_config.sys_conf_dict['system']['redis']['url'])
redis_client = redis.Redis(host=redis_url[1], port=redis_url[2], password=redis_url[0], db=redis_url[3])
ext.register(agbot_config.sys_conf_dict)


class TcBase(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task_ctx = kwargs.get('task_ctx')
        job_ctx = kwargs.get('job_ctx')
        tc_ctx = kwargs.get('tc_ctx')
        logger.exception(
            'execute_tc error {}_{}_{}; cause: {}'.format(task_ctx.task_model.id,
                                                          job_ctx.job_model.id,
                                                          tc_ctx.tc_detail.id,
                                                          str(exc)))
        self.retry(exc=exc, countdown=60)


def save_tc_context(task_ctx: TaskContext,
                    job_ctx: JobContext,
                    tc_ctx: TcContext):
    redis_key = 'agbot_tc_context_list_{}_{}'.format(task_ctx.task_model.id, job_ctx.job_model.id)
    try:
        redis_client.sadd(redis_key, pickle.dumps(tc_ctx))
        redis_client.expire(redis_key, timedelta(days=10))
    except BaseException as e:
        logger.exception(
            'save_tc_context error {}_{}_{}; cause: {}'.format(task_ctx.task_model.id,
                                                               job_ctx.job_model.id,
                                                               tc_ctx.tc_detail.id,
                                                               str(e)))


@_celery_app.task(name='tasks.execute_tc',
                  bind=True,
                  base=TcBase,
                  acks_late=True,
                  reject_on_worker_lost=True,
                  soft_time_limit=1200,
                  time_limit=1500,
                  store_errors_even_if_ignored=True,
                  max_retries=3
                  )
def execute_tc(
        self,
        task_ctx: TaskContext,
        job_ctx: JobContext,
        tc_ctx: TcContext):
    tc_ctx.start_time = datetime.now()

    try:
        logger.info(
            'execute_tc start {}_{}_{}'.format(task_ctx.task_model.id, job_ctx.job_model.id, tc_ctx.tc_detail.id))
        _celery_tc_executor.do_execute(task_ctx, job_ctx, tc_ctx)
        save_tc_context(task_ctx, job_ctx, tc_ctx)
    except BaseException as e:
        logger.exception(
            'execute_tc error {}_{}_{}; cause: {}'.format(task_ctx.task_model.id,
                                                          job_ctx.job_model.id,
                                                          tc_ctx.tc_detail.id,
                                                          str(e)))
        tc_ctx.end_time = datetime.now()
        tc_ctx.status = TestStatus.ERROR
        tc_ctx.error = ErrorInfo(Scope.TC, ErrorType.RUNTIME_ERROR, str(e))
        save_tc_context(task_ctx, job_ctx, tc_ctx)
    finally:
        _celery_tc_executor.process_tc_context(task_ctx, job_ctx, tc_ctx)

    return {
        'task_id': task_ctx.task_model.id,
        'job_id': job_ctx.job_model.id,
        'tc_id': tc_ctx.tc_detail.id,
        'status': tc_ctx.status.value
    }


def save_job_context(task_ctx, job_ctx):
    redis_key = 'agbot_job_context_list_{}'.format(task_ctx.task_model.id)
    try:
        redis_client.sadd(redis_key, pickle.dumps(job_ctx))
        redis_client.expire(redis_key, timedelta(days=10))
    except BaseException as e:
        logger.exception(
            'save_job_context error {}_{}; cause: {}'.format(task_ctx.task_model.id, job_ctx.job_model.id,
                                                             str(e)))


def get_tc_context_list(task_ctx, job_ctx):
    redis_key_tc_ctx_values = 'agbot_tc_context_list_{}_{}'.format(task_ctx.task_model.id, job_ctx.job_model.id)
    tc_ctx_values = redis_client.smembers(redis_key_tc_ctx_values)
    tc_ctx_list = [pickle.loads(tc_ctx_v) for tc_ctx_v in tc_ctx_values]
    return tc_ctx_list


class JobBase(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task_ctx = kwargs.get('task_ctx')
        job_ctx = kwargs.get('job_ctx')
        logger.exception(
            'process_job_context error {}_{}; cause: {}'.format(task_ctx.task_model.id, job_ctx.job_model.id,
                                                                str(exc)))
        self.retry(exc=exc, countdown=60)


@_celery_app.task(name='tasks.process_job_context',
                  bind=True,
                  base=JobBase,
                  acks_late=True,
                  reject_on_worker_lost=True,
                  soft_time_limit=1200,
                  time_limit=1500,
                  store_errors_even_if_ignored=True,
                  max_retries=3
                  )
def process_job_context(
        self,
        task_ctx: TaskContext,
        job_ctx: JobContext):
    try:
        logger.info('process_job_context start {}_{}'.format(task_ctx.task_model.id, job_ctx.job_model.id))
        tc_ctx_list = get_tc_context_list(task_ctx, job_ctx)
        job_ctx.end_time = datetime.now()
        job_ctx.status = TestStatus.PASSED \
            if all(tc_ctx.status == TestStatus.PASSED for tc_ctx in tc_ctx_list) \
            else TestStatus.NOT_PASSED
        save_job_context(task_ctx, job_ctx)
        job_ctx.tc_context_list = tc_ctx_list
        _celery_job_exec_common.process_job_context(task_ctx, job_ctx)
    except BaseException as e:
        logger.exception(
            'process_job_context error {}_{}; cause: {}'.format(task_ctx.task_model.id, job_ctx.job_model.id, str(e)))
        self.retry(exc=e, countdown=60)


    return {
        'task_id': task_ctx.task_model.id,
        'job_id': job_ctx.job_model.id,
        'status': job_ctx.status.value
    }


class TaskBase(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task_ctx = kwargs.get('task_ctx')
        logger.exception('process_task_context error {}, cause: {}'.format(task_ctx.task_model.id, str(exc)))
        self.retry(exc=exc, countdown=60)


@_celery_app.task(name='tasks.process_task_context',
                  bind=True,
                  base=TaskBase,
                  acks_late=True,
                  reject_on_worker_lost=True,
                  soft_time_limit=1200,
                  time_limit=1500,
                  store_errors_even_if_ignored=True,
                  max_retries=3
                  )
def process_task_context(
        self,
        task_ctx: TaskContext
):
    try:
        redis_key = 'agbot_job_context_list_{}'.format(task_ctx.task_model.id)
        job_ctx_values = redis_client.smembers(redis_key)
        job_ctx_list = [pickle.loads(job_ctx_v) for job_ctx_v in job_ctx_values]
        for job_ctx in job_ctx_list:
            job_ctx.tc_context_list = get_tc_context_list(task_ctx, job_ctx)
        task_ctx.end_time = datetime.now()
        task_ctx.job_context_list = job_ctx_list
        task_ctx.status = TestStatus.PASSED \
            if all(job_ctx.status == TestStatus.PASSED for job_ctx in job_ctx_list) \
            else TestStatus.NOT_PASSED
        _celery_task_exec_common.process_task_context(task_ctx)
    except BaseException as e:
        logger.exception('process_task_context error {}, cause: {}'.format(task_ctx.task_model.id, str(e)))
        self.retry(exc=e, countdown=60)

    return {
        'task_id': task_ctx.task_model.id,
        'status': task_ctx.status.value
    }


class TaskExecutorCelery(TaskExecutor):

    def __init__(self,
                 sys_conf_dict: Dict,
                 executor):
        TaskExecutor.__init__(self, sys_conf_dict, executor)
        self.__executor = executor
        self.__job_exec_common = JobExecCommon(sys_conf_dict)

    async def process_task_context(self, task_ctx: TaskContext):
        pass

    async def do_execute(self, task_ctx: TaskContext, task_detail: TaskDetail):
        await event_loop.run_in_executor(self.__executor, self._do_execute, task_ctx, task_detail)

    def _do_execute(self, task_ctx, task_detail: TaskDetail):
        try:
            job_signature_list = [self.__create_job_signature(task_ctx, job_detail)
                                  for job_detail in task_detail.job_detail_list]

            job_matrix = rotate(list(chunks(job_signature_list, task_ctx.task_model.job_concurrency)))
            job_chain_list = [chain(job_chunk) for job_chunk in job_matrix]

            topology = chord(group(job_chain_list), body=process_task_context.si(task_ctx=task_ctx))
            topology.apply_async((),
                                 task_id='agbot_task_{}'.format(task_ctx.task_model.id),
                                 retry=True,
                                 retry_policy={
                                     'max_retries': 3,
                                     'interval_start': 0,
                                     'interval_step': 0.2,
                                     'interval_max': 0.2,
                                 })
        except BaseException as e:
            logger.exception('TaskExecutorCelery do_execute error, task_id={}, cause: {}'
                             .format(task_detail.task_model.id, str(e)))
            task_ctx.status = TestStatus.ERROR
            task_ctx.end_time = datetime.now()
            task_ctx.error = ErrorInfo(Scope.TASK, ErrorType.RUNTIME_ERROR, str(e))
            _celery_task_exec_common.process_task_context(task_ctx)

    def __create_job_signature(self,
                               task_ctx: TaskContext,
                               job_detail: JobDetail):
        job_ctx = JobContext(job_detail.job_model, datetime.now())
        self.__job_exec_common.before_do_execute(task_ctx,
                                                 job_ctx,
                                                 job_detail)
        try:
            tc_signature_list = [self.__create_tc_signature(task_ctx,
                                                            job_ctx,
                                                            tc_detail)
                                 for tc_detail in job_detail.tc_detail_list]

            tc_matrix = rotate(list(chunks(tc_signature_list, job_ctx.job_model.concurrency)))

            tc_chain_list = [chain(tc_chunk) for tc_chunk in tc_matrix]

            return chord(group(tc_chain_list),
                         body=process_job_context.si(task_ctx=task_ctx,
                                                     job_ctx=job_ctx))
        except BaseException as e:
            logger.exception(
                'create_job_signature error; task_id: {}, job_id: {}; cause: {}'.format(
                    str(task_ctx.task_model.id), str(job_ctx.job_model.id), str(e)))
            job_ctx.status = TestStatus.ERROR
            job_ctx.end_time = datetime.now()
            job_ctx.error = ErrorInfo(Scope.JOB, ErrorType.RUNTIME_ERROR, str(e))
            self.__job_exec_common.process_job_context(task_ctx, job_ctx)
            raise RuntimeError('create_job_signature error: {}'.format(job_ctx.job_model.id))

    def __create_tc_signature(self, task_ctx, job_ctx, tc_detail):
        tc_ctx = TcContext(tc_detail, datetime.now())
        _celery_tc_executor.before_do_execute(task_ctx,
                                              job_ctx,
                                              tc_ctx)
        return execute_tc.si(task_ctx=task_ctx,
                             job_ctx=job_ctx,
                             tc_ctx=tc_ctx)
