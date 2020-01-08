from ..job.job_context import JobContext
from ..task.task_context import TaskContext
from ..tc.tc_context import TcContext


class VerticalContext:

    def __init__(self,
                 sys_conf_dict,
                 task_context: TaskContext = None,
                 job_context: JobContext = None,
                 tc_context: TcContext = None):
        self.sys_conf_dict = sys_conf_dict
        self.task_context = task_context
        self.job_context = job_context
        self.tc_context = tc_context
