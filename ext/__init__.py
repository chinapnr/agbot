from agbot.core.job import job_exec
from agbot.core.task import task_exec
from . import context_processor_excel
from . import context_processor_mail
from . import context_processor_mty


def register(sys_conf_dict):
    if sys_conf_dict['system']['ext']['context_processor_excel'].get('enabled') == True:
        task_exec.register_context_processor(context_processor_excel.task_context_processor)
    if sys_conf_dict['system']['ext']['context_processor_mty'].get('enabled') == True:
        job_exec.register_context_processor(context_processor_mty.job_context_processor)
        task_exec.register_context_processor(context_processor_mty.task_context_processor)
    if sys_conf_dict['system']['ext']['context_processor_mail'].get('enabled') == True:
        task_exec.register_context_processor(context_processor_mail.task_context_processor)
