import json
import pickle
import re
from datetime import timedelta

import redis
import requests
from fishbase import logger

from agbot.agbot_config import agbot_config
from agbot.constant.ag_enum import TestStatus
from agbot.core.model.context import VerticalContext
from agbot.core.tp.tp_context import TpContext

redis_url = re.split('[@:/]', agbot_config.sys_conf_dict['system']['redis']['url'])
redis_client = redis.Redis(host=redis_url[1], port=redis_url[2], password=redis_url[0], db=redis_url[3])


def __process_tc_context(vertical_ctx: VerticalContext, mty_interface_id):
    tp_list = []
    for tp_ctx in filter(lambda ctx: isinstance(ctx, TpContext), vertical_ctx.tc_context.tp_and_plugin_context_list):
        if tp_ctx.status == TestStatus.PASSED:
            tp_result = 1
        else:
            tp_result = 0

        tp_list_dict = {'caseName': vertical_ctx.tc_context.tc_detail.id,
                        'requestData': tp_ctx.request.content if tp_ctx.request else '',
                        'jmxId': mty_interface_id,
                        'responseCode': tp_ctx.response.code if tp_ctx.response else 0,
                        'responseData': tp_ctx.response.content if tp_ctx.response else tp_ctx.error.message,
                        'resultId': vertical_ctx.task_context.task_model.id,
                        'stepName': tp_ctx.name,
                        'spendTime': (tp_ctx.end_time - tp_ctx.start_time).total_seconds(),
                        'updateBy': vertical_ctx.task_context.task_model.crt_user,
                        'success': tp_result}
        tp_list.append(tp_list_dict)

    param_dict = {'json': json.dumps(tp_list)}

    response = requests.post(vertical_ctx.sys_conf_dict['mty']['savestep_url'], param_dict, timeout=5)
    resp_json = response.json()
    assert response.status_code == 200 and resp_json.get(
        'respCode') == 'S', 'mty_process_tc_context error: {}_{}, {}, {}'.format(
        vertical_ctx.task_context.task_model.id,
        vertical_ctx.tc_context.tc_detail.id,
        response.status_code,
        resp_json
    )


def _get_mty_interface_id(vertical_ctx: VerticalContext):
    redis_key = 'agbot_mty_interface_id_{}'.format(vertical_ctx.task_context.task_model.id)
    interface_id_txt = redis_client.hget(redis_key, vertical_ctx.job_context.job_model.id)
    if interface_id_txt is None:
        return None

    return pickle.loads(interface_id_txt)


def _set_mty_interface_id(vertical_ctx: VerticalContext, job_mty_interface_id):
    redis_key = 'agbot_mty_interface_id_{}'.format(vertical_ctx.task_context.task_model.id)
    interface_id_txt = pickle.dumps(job_mty_interface_id)
    redis_client.hset(redis_key, vertical_ctx.job_context.job_model.id, interface_id_txt)
    redis_client.expire(redis_key, timedelta(days=10))


def _create_mty_interface_id(vertical_ctx: VerticalContext):
    # 获取 interfaceId
    param_interface_dict = {'json': json.dumps({'jmxPath': vertical_ctx.job_context.job_model.desc,
                                                'resultId': vertical_ctx.task_context.task_model.id,
                                                'updateBy': vertical_ctx.task_context.task_model.crt_user})}
    # 获取测试平台 interfaceId
    response = requests.post(
        vertical_ctx.sys_conf_dict['mty']['saveinterface_url'], param_interface_dict)

    if 'S' == response.json().get('respCode'):
        return response.json().get('interfaceid')
    else:
        logger.error('mty_job_context_processor error, create interfaceId failure; {}_{}'.format(
            vertical_ctx.task_context.task_model.id, vertical_ctx.job_context.job_model.id))
        return None


def job_context_processor(vertical_ctx: VerticalContext):
    if vertical_ctx.task_context.task_model.crt_sys != 'automation':
        return
    mty_interface_id = _get_mty_interface_id(vertical_ctx)
    if mty_interface_id is None:
        mty_interface_id = _create_mty_interface_id(vertical_ctx)
        if mty_interface_id is None:
            return
        _set_mty_interface_id(vertical_ctx, mty_interface_id)

    tc_ctx_dict = {tc_ctx.tc_detail.id: tc_ctx for tc_ctx in vertical_ctx.job_context.tc_context_list}
    for tc_ctx in tc_ctx_dict.values():
        try:
            __process_tc_context(VerticalContext(vertical_ctx.sys_conf_dict,
                                                 vertical_ctx.task_context,
                                                 vertical_ctx.job_context,
                                                 tc_ctx),
                                 mty_interface_id)
        except Exception as e:
            logger.exception('mty_process_tc_context error: {}_{}, {}'.format(
                vertical_ctx.task_context.task_model.id,
                vertical_ctx.tc_context.tc_detail.id,
                str(e)))

    param_end_dict = {'json': json.dumps({
        'interfaceid': mty_interface_id
    })}

    try:
        # 推送 job 结束标识
        response = requests.post(vertical_ctx.sys_conf_dict['mty']['completeinterface_url'], param_end_dict)
        resp_json = response.json()
        assert response.status_code == 200 and resp_json.get('respCode') == 'S', \
            'mty_job_context_processor: {}_{}, {}_{}'.format(
                vertical_ctx.task_context.task_model.id,
                vertical_ctx.job_context.job_model.id,
                response.status_code,
                resp_json
            )
        logger.info('mty_job_context_processor success; {}_{}'.format(
            vertical_ctx.task_context.task_model.id, vertical_ctx.job_context.job_model.id))
    except Exception as e:
        logger.error(str(e))


def task_context_processor(vertical_ctx: VerticalContext):
    if vertical_ctx.task_context.task_model.crt_sys != 'automation':
        return

    # 拼装推送参数
    tc_dict = {'batchid': str(vertical_ctx.task_context.task_model.id),
               'respCode': 'S',
               'respDesc': ''}

    param_dict = {'json': json.dumps(tc_dict)}

    try:
        # 推送测试结果给测试平台

        response = requests.post(vertical_ctx.sys_conf_dict['mty']['complete_url'], param_dict, timeout=5)
        resp_json = response.json()
        assert response.status_code == 200 and resp_json.get('respCode') == 'S', 'Task 推送测试平台失败: {}, {}, {}'.format(
            response.status_code,
            resp_json,
            vertical_ctx.task_context.task_model.id,
        )
        logger.info('Task 推送测试平台成功; {}'.format(vertical_ctx.task_context.task_model.id))
    except Exception as e:
        logger.error(str(e))
