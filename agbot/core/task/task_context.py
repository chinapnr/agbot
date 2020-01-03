from typing import List

from .task_model import TaskModel
from ..job.job_context import JobContext
from ...constant.ag_enum import TestStatus
from ...tools.ag_error import ErrorInfo


class TaskContext:
    error: ErrorInfo
    job_context_list: List[JobContext]

    def __init__(self,
                 task_model: TaskModel,
                 start_time
                 ):
        self.task_model = task_model
        self.job_context_list = []
        self.start_time = start_time
        self.end_time = None
        self.status = TestStatus.INIT
        self.error = None

    def __str__(self):
        repr_str = ("<JobContext("
                    "task_model={task_model}, "
                    "start_time={start_time} "
                    "status={status} "
                    ")>".format(
                        task_model=self.task_model,
                        start_time=self.start_time,
                        status=self.status))
        return repr_str

    def __repr__(self):
        return self.__str__()


