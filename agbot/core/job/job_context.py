from typing import List

from .job_model import JobModel
from ..tc.tc_context import TcContext
from ...constant.ag_enum import TestStatus
from ...tools.ag_error import ErrorInfo


class JobAnalysis:
    def __init__(self):
        # 当前 job 中 tc 累加权重
        self.tc_total_weight = 0
        # 当前 job 中 tc 累加的加权分数
        self.tc_total_score = 0
        # 当前 job 中 tc 案例总数
        self.tc_total_num = 0
        # 当前 job 中 tc 案例通过数
        self.tc_pass_num = 0
        # 当前 job 中关键案例未通过数
        self.tc_key_unpass_num = 0


class JobContext:
    analysis: JobAnalysis
    error: ErrorInfo
    tc_context_list: List[TcContext]

    def __init__(self,
                 job_model: JobModel,
                 start_time
                 ):
        self.job_model = job_model
        self.tc_context_list = []
        self.start_time = start_time
        self.end_time = None
        self.status = TestStatus.INIT
        self.error = None
        self.analysis = None

    def __str__(self):
        repr_str = ("<JobContext("
                    "job_model={job_model}, "
                    "tc_context_list={tc_context_list} "
                    ")>".format(
                        job_model=self.job_model,
                        tc_context_list=self.tc_context_list))
        return repr_str

    def __repr__(self):
        return self.__str__()


