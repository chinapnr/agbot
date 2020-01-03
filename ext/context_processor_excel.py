from datetime import datetime

import pandas
from fishbase import fish_file
from fishbase import logger

from agbot.core.model.context import VerticalContext
from agbot.db.db_tool import DBUtils
from agbot.db.table_job_log import TableJobLog
from agbot.db.table_task_log import TableTaskLog
from agbot.db.table_testcase_log import TableTestCaseLog
from agbot.db.table_testpoint_log import TableTestPointLog


def task_context_processor(vertical_ctx: VerticalContext):
    task_id = vertical_ctx.task_context.task_model.id

    # 查询该 task 是否存在, 若不存在返回该 task 不存在
    _, tab_task_log_list = DBUtils.query(TableTaskLog, {'task_id': task_id})

    if not tab_task_log_list:
        logger.exception('task_id 错误，没有该任务')

    tab_task_log = tab_task_log_list[0]
    tab_task_log_dict = tab_task_log.to_dict()
    task_ctx = vertical_ctx.task_context
    tab_task_log_dict['task_status'] = task_ctx.status.value
    tab_task_log_dict['error_info'] = str(task_ctx.error.message)[:1024] if task_ctx.error is not None else None
    tab_task_log_dict['end_time'] = datetime.now()
    tab_task_log_dict['cost_time'] = (tab_task_log_dict['end_time'] - task_ctx.start_time).total_seconds() * 1000

    tab_job_log_list = []
    tab_tc_log_list = []
    tab_tp_log_list = []

    _, tab_job_obj_list = DBUtils.query(TableJobLog, filter_dict={'task_id': task_id}, first=False)

    # 查询 job 执行结果
    if tab_job_obj_list is not None and len(tab_job_obj_list) > 0:
        tab_job_log_list = [item.to_dict() for item in tab_job_obj_list]

    _, tab_tc_obj_list = DBUtils.query(TableTestCaseLog, filter_dict={'task_id': task_id}, first=False)

    # 查询 tc 执行结果
    if tab_tc_obj_list is not None and len(tab_tc_obj_list) > 0:
        tab_tc_log_list = [item.to_dict() for item in tab_tc_obj_list]

    # 查询 tp 执行结果
    _, tab_tp_obj_list = DBUtils.query(TableTestPointLog, filter_dict={'task_id': task_id}, first=False)

    if tab_tp_obj_list is not None and len(tab_tp_obj_list) > 0:
        for item in tab_tp_obj_list:
            temp_dict = item.to_dict()
            flag, tab_tc_obj = DBUtils.query(TableTestCaseLog,
                                             filter_dict={'tc_seq_id': getattr(item, 'tc_seq_id')},
                                             first=True)
            tc_id = tab_tc_obj[0].tc_id if flag and tab_tc_obj else ''
            temp_dict.update({'tc_id': tc_id})
            tab_tp_log_list.append(temp_dict)

    tp_df = pandas.DataFrame(tab_tp_log_list)
    if len(tab_tp_log_list) > 0:
        tp_df = tp_df.ix[:, tab_tp_log_list[0].keys()]
    tc_df = pandas.DataFrame(tab_tc_log_list)
    if len(tab_tc_log_list) > 0:
        tc_df = tc_df.ix[:, tab_tc_log_list[0].keys()]
    job_df = pandas.DataFrame(tab_job_log_list)
    if len(tab_job_log_list) > 0:
        job_df = job_df.ix[:, tab_job_log_list[0].keys()]
    task_df = pandas.DataFrame([tab_task_log_dict])
    task_df = task_df.ix[:, tab_task_log_dict.keys()]

    csv_filename = vertical_ctx.sys_conf_dict.get('excel_context_file_name',
                                                  '{task_id}_result.xlsx') \
        .format(task_id=vertical_ctx.task_context.task_model.id)
    fish_file.check_sub_path_create('result')
    csv_file_path = fish_file.get_abs_filename_with_sub_path('result', csv_filename)[1]

    # 将结果保存至多个 sheet
    with pandas.ExcelWriter(csv_file_path) as writer:
        task_df.to_excel(writer, index=False, sheet_name='task')
        job_df.to_excel(writer, index=False, sheet_name='job')
        tc_df.to_excel(writer, index=False, sheet_name='tc')
        tp_df.to_excel(writer, index=False, sheet_name='tp')

    logger.info('result excel saved to {}'.format(csv_file_path))
