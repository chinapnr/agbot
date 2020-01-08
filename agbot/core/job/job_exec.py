from datetime import datetime

from fishbase import logger

from .job_context import JobContext, JobAnalysis
from .job_detail import JobDetail
from ..model.context import VerticalContext
from ..task.task_context import TaskContext
from ..tc.tc_detail import weight_high
from ...constant.ag_enum import TestStatus
from ...db.db_tool import DBUtils
from ...db.table_job_log import update_job, TableJobLog

_context_processor_list = []


def register_context_processor(context_processor):
    if context_processor not in _context_processor_list:
        _context_processor_list.append(context_processor)


class JobExecCommon:

    def __init__(self,
                 sys_conf_dict: dict):
        # 全局配置
        self.__sys_conf_dict = sys_conf_dict

    def before_do_execute(self,
                          task_ctx: TaskContext,
                          job_ctx: JobContext,
                          job_detail: JobDetail):
        job_record = {
            'sys_date': str(datetime.today().strftime('%Y%m%d')),
            'task_id': task_ctx.task_model.id,
            'job_id': job_detail.job_model.id,
            'job_desc': job_detail.job_model.desc,
            'job_status': job_ctx.status.value,
            'start_time': job_ctx.start_time
        }
        # Job 运行请求记录到数据库
        # 修改数据库录入，使用 session_scope
        DBUtils.add(TableJobLog, job_record)

    def process_job_context(self, task_ctx: TaskContext, job_ctx: JobContext):
        for ctx_processor in _context_processor_list:
            try:
                ctx_processor(VerticalContext(self.__sys_conf_dict, task_ctx, job_ctx))
            except BaseException as e:
                logger.exception('JobExecCommon ctx_processor error: {}, cause: {}, job_ctx: {}'
                                 .format(job_ctx.job_model.id, str(e), str(job_ctx)))

        job_record = {
            'task_id': task_ctx.task_model.id,
            'job_id': job_ctx.job_model.id,
            'job_status': job_ctx.status.value,
            'end_time': job_ctx.end_time
        }
        if len(job_ctx.tc_context_list) > 0:
            self.__analysis(job_ctx)
            job_record['job_score'] = str(round(job_ctx.analysis.tc_total_score / job_ctx.analysis.tc_total_weight, 2))
            job_record['pass_rate'] = str(round(job_ctx.analysis.tc_pass_num / job_ctx.analysis.tc_total_num, 2))
            job_record['key_unpass_num'] = job_ctx.analysis.tc_key_unpass_num

        if job_ctx.error is not None:
            job_record['error_info'] = str(job_ctx.error.message)[:1024]
        update_job(job_record)

    def __analysis(self, job_ctx: JobContext):
        analysis = JobAnalysis()
        analysis.tc_total_num = len(job_ctx.tc_context_list)
        analysis.tc_total_weight = sum(map(lambda tc_ctx: tc_ctx.tc_detail.weight,
                                           job_ctx.tc_context_list))
        analysis.tc_total_score = sum(map(lambda tc_ctx: self.__get_tc_score(tc_ctx),
                                          job_ctx.tc_context_list))
        analysis.tc_pass_num = sum(map(lambda tc_ctx: 1,
                                       filter(lambda tc_ctx: tc_ctx.status == TestStatus.PASSED,
                                              job_ctx.tc_context_list)))
        analysis.tc_key_unpass_num = sum(map(lambda tc_ctx: 1,
                                             filter(lambda tc_ctx: self.__is_key_unpass_tc(tc_ctx),
                                                    job_ctx.tc_context_list)))
        job_ctx.analysis = analysis

    def __get_tc_score(self, tc_ctx):
        if tc_ctx.status == TestStatus.PASSED:
            return 100 * int(tc_ctx.tc_detail.weight)
        else:
            return 0

    def __is_key_unpass_tc(self, tc_ctx):
        return tc_ctx.tc_detail.weight >= weight_high and tc_ctx.status != TestStatus.PASSED
