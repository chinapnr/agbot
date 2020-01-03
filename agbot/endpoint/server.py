# coding=utf-8
# agbot server api 类
# 2018.4.18 created by xin.guo
import json
from concurrent.futures.thread import ThreadPoolExecutor

from flask import request, jsonify

from agbot.agbot_config import agbot_config
from agbot.constant.ag_constant import *
from agbot.constant.ag_enum import TestStatus
from agbot.core.task.task_context import TaskContext
from agbot.core.task.task_detail import TaskDetail, ParameterTaskDetailLoader
from agbot.core.task.task_exec import TaskExecCommon
from agbot.core.task.task_exec_celery import TaskExecutorCelery
from agbot.core.task.task_model import TaskModel
from agbot.core.utils import event_loop
from agbot.db.table_job_log import TableJobLog
from agbot.db.table_task_log import *
from agbot.db.table_testcase_log import TableTestCaseLog
from agbot.db.table_testpoint_log import TableTestPointLog
from agbot.endpoint.server_conf import app, CommonException
from agbot.tools.ag_error import ErrorInfo, Scope, ErrorType

_thread_pool = ThreadPoolExecutor(max_workers=8)
_task_executor = TaskExecutorCelery(agbot_config.sys_conf_dict, _thread_pool)
_task_exec_common = TaskExecCommon(agbot_config.sys_conf_dict)


async def _load_and_execute_task(task_detail_loader,
                                 task_id,
                                 task_src,
                                 global_var,
                                 crt_sys,
                                 crt_user
                                 ):
    # task_content 配置
    try:
        task_detail = task_detail_loader.load()  # type: TaskDetail
    except Exception as e:
        logger.exception('load task detail error: {}, {}'.format(task_id, str(e)))
        task_model = TaskModel(task_id, task_src, global_var)
        task_model.crt_sys = crt_sys
        task_model.crt_user = crt_user
        task_ctx = TaskContext(task_model, datetime.now())
        _task_exec_common.before_do_execute(task_ctx, TaskDetail(task_model, []))
        task_ctx.status = TestStatus.ERROR
        task_ctx.end_time = datetime.now()
        task_ctx.error = ErrorInfo(Scope.TASK, ErrorType.ILLEGAL_ARGUMENT, str(e))
        _task_exec_common.process_task_context(task_ctx)
        return

    await _task_executor.execute(task_detail)


@app.route('/agbot/hello-world')
def get_hello():
    return jsonify({'data': 'Hello World!'})


# 提交测试任务
# 2018.4.23 created by xin.guo
@app.route('/agbot/task', methods=['POST'])
def create_task():
    # 获得传入参数
    try:
        task_id = request.form.get('task_id')
        task_file_id = request.form.get('task_file_name')
        task_create_system = request.form.get('task_create_system')
        task_create_user = request.form.get('task_create_user')
        # job 执行顺序，可空，为空时，按job_conf.ini中job配置顺序执行
        job_name_list = request.form.get('task_job_list')
        # agsite 对应项目名称
        task_agsite_project_name = request.form.get('project_name')
        tc_flag = request.form.get('flag')
        global_var_str = request.form.get('global_var')
        if global_var_str is not None:
            global_var = json.loads(global_var_str)
        else:
            global_var = {}
        job_specific_str = request.form.get('job_specific')
        if job_specific_str is not None:
            job_specific = json.loads(job_specific_str)
        else:
            job_specific = {}
    except Exception:
        raise CommonException(USER_INFO_FROM_ARGS_ERROR, status_code=400)
    
    if not task_id:
        raise CommonException(REQUEST_PARAM_ILLEGAL, status_code=400,
                              msg_dict={'param_name': 'task_id'})
    
    if all([not task_file_id, not task_agsite_project_name]):
        raise CommonException(REQUEST_PARAM_ILLEGAL, status_code=400,
                              msg_dict={'param_name': 'task_file_name' + ',' + 'tar_project'})
    
    # 默认调用者为匿名
    if not task_create_system:
        task_create_system = ''
    
    # 默认调用者为匿名
    if not task_create_user:
        task_create_user = ''
    
    logger.info('start task-------------------------------------------task_id:'
                + task_id + ',task_create_system:' + task_create_system
                + ',task_create_system:' + task_create_system + ',task_file_name:' +
                str(task_file_id) + ',project_name:' + str(task_agsite_project_name))
    
    # 查询该 task 是否已经存在, 若存在返回该 task 已经存在
    # 2019.03.01 edit by jun.hu
    _, tab_task_log = DBUtils.query(TableTaskLog, filter_dict={'task_id': task_id})
    
    if tab_task_log:
        raise CommonException(TASK_ALREADY_EXISTS, status_code=409)
    
    # 2019.5.7 edit by jun.hu
    # 新加检查配置文件是否都 ok，文件是否存在，编码格式是否正确，是否能正确读取配置等，并将错误状态同步返回
    task_detail_loader = ParameterTaskDetailLoader(
        task_id,
        task_file_id,
        job_name_list,
        job_specific,
        tc_flag,
        global_var,
        task_create_system,
        task_create_user
    )

    try:
        _thread_pool.submit(event_loop.run_until_complete,
                            _load_and_execute_task(task_detail_loader,
                                                   task_id,
                                                   task_file_id,
                                                   global_var,
                                                   task_create_system,
                                                   task_create_user))
    except BaseException as e:
        logger.error('启动task失败, cause {}'.format(str(e)))
        raise CommonException(TASK_START_ERROR, status_code=500)
    
    # 返回状态
    return jsonify({'return_code': COMMON_SUCCESS}), 200


# 单条测试案例设置标签过滤
# 2018.11.25 create by yanan.wu #748921
def __tc_flag_filter(self, tc_data):
    # self.__tc_flag 即请求参数中的 flag，用于指定跳过不执行的 tc
    if self.__tc_flag:
        tc_flag_set = set(self.__tc_flag.strip().split(','))
        tc_data_flag = tc_data.get('tc_flag')

        if tc_data_flag:
            tc_data_flag_set = set(tc_data_flag.strip().split(','))
            # 如果有交集，才执行该数据指向的 tc
            if tc_flag_set.intersection(tc_data_flag_set):
                return True
            else:
                return False
        else:
            return False
    return True


# 查询测试任务
# 2018.4.23 created by xin.guo
@app.route('/agbot/task', methods=['GET'])
def get_task():
    # 获取传入参数
    try:
        task_id = request.args.get('task_id')
    except:
        raise CommonException(USER_INFO_FROM_ARGS_ERROR, status_code=400)
    
    if not task_id:
        raise CommonException(REQUEST_PARAM_ILLEGAL, status_code=400,
                              msg_dict={'param_name': 'task_id'})
    
    # 查询该 task 是否存在, 若不存在返回该 task 不存在
    _, tab_task_log_list = DBUtils.query(TableTaskLog, {'task_id': task_id})
    
    if not tab_task_log_list:
        raise CommonException(TASK_NOT_EXISTS, status_code=401)
    tab_task_log = tab_task_log_list[0]
    
    tab_job_log_list = []
    tab_tc_log_list = []
    
    _, tab_job_obj_list = DBUtils.query(TableJobLog, filter_dict={'task_id': task_id}, first=False)
    
    # 查询 job 执行结果
    if tab_job_obj_list is not None and len(tab_job_obj_list) > 0:
        tab_job_log_list = [item.to_dict() for item in tab_job_obj_list]
    
    _, tab_tc_obj_list = DBUtils.query(TableTestCaseLog, filter_dict={'task_id': task_id}, first=False)
    
    # 查询 tc 执行结果
    if tab_tc_obj_list is not None and len(tab_tc_obj_list) > 0:
        tab_tc_log_list = [item.to_dict() for item in tab_tc_obj_list]
    
    tab_task_log_dict = tab_task_log.to_dict()
    
    result_dict = {'return_code': '90000',
                   'message': '成功'}
    result_dict.update(tab_task_log_dict)
    result_dict.update({'tab_job_log_list': tab_job_log_list})
    result_dict.update({'tab_tc_log_list': tab_tc_log_list})
    
    # 返回结果
    return result_dict, 200


# 查询测试结果
# 2018.9.29 created by yanan.wu
@app.route('/agbot/test-case', methods=['GET'])
def get_testcase():
    # 获取传入参数
    try:
        tc_seq_id = request.args.get('tc_seq_id')
    except:
        raise CommonException(USER_INFO_FROM_ARGS_ERROR, status_code=400)
    
    # 查询 test_case
    _, tab_tc_obj_list = DBUtils.query(TableTestCaseLog, filter_dict={'tc_seq_id': tc_seq_id})
    if not tab_tc_obj_list:
        raise CommonException(TASK_NOT_EXISTS, status_code=401)
    tab_tc_log = tab_tc_obj_list[0]
    
    _, tab_tp_log_list = DBUtils.query(TableTestPointLog,
                                       filter_dict={'tc_seq_id': tc_seq_id},
                                       order_dict={'crt_datetime': 'asc'},
                                       first=False)
    
    tp_list = []
    if tab_tp_log_list:
        for tab_tp_log in tab_tp_log_list:
            if tab_tp_log.tp_result == TestStatus.PASSED.value:
                tp_result = 1
            else:
                tp_result = 0
            
            tp_list_dict = {'tp_type': tab_tp_log.tp_type,
                            'tp_id': tab_tp_log.tp_id,
                            'error_info': tab_tp_log.error_info,
                            'requ_param': tab_tp_log.requ_param,
                            'resp_data': tab_tp_log.result_value,
                            'tp_name': tab_tp_log.tp_name,
                            'cost_time': tab_tp_log.cost_time,
                            'tp_result': tp_result}
            tp_list.append(tp_list_dict)
    
    # 返回结果
    return jsonify({'return_code': '90000',
                    'message': '成功',
                    'test_result': tab_tc_log.test_status,
                    'cost_time': tab_tc_log.cost_time,
                    'error_info': tab_tc_log.error_info,
                    'tp_list': tp_list}), 200
