import json
import os
from copy import copy
from os.path import dirname
from typing import List, Dict, Optional, Tuple

from fishbase import logger, fish_common as ffc

from .task_model import TaskModel
from ..job.job_ctl import FileJobCtl
from ..job.job_detail import JobDetail, FileJobDetailLoader
from ..tc.tc_detail import TcDetail
from ..utils import get_file_encoding, is_not_blank
from ...agbot_config import agbot_config
from ...constant.ag_constant import TASK_CONF_FILE_NOT_EXISTS, TASK_CONF_FILE_READ_ERROR
from ...tools.ag_error import CommonException


class TaskDetail:
    task_model: TaskModel

    def __init__(self,
                 task_model: TaskModel,
                 job_detail_list: List[JobDetail],
                 ):
        self.task_model = task_model
        self.job_detail_list = job_detail_list  # type: List[JobDetail]

    def __str__(self):
        repr_str = ("<TaskContentConfig(task_model={task_model},"
                    "job_detail_list={job_detail_list})>".
                    format(
                        task_model=self.task_model,
                        job_detail_list=self.job_detail_list))
        return repr_str

    def __repr__(self):
        return self.__str__()


class TaskDetailLoader:

    def load(self) -> TaskDetail:
        pass


class FileTaskDetailLoader(TaskDetailLoader):
    """
    加载任务配置
    """

    def __init__(self,
                 task_id: str,
                 task_file_id: str,
                 job_id_list: List[str]):
        """
        :param task_id: 任务 id
        :param task_file_id:  任务文件唯一标志
        """
        if task_file_id.startswith('data/'):
            full_path = os.path.join(agbot_config.basedir, task_file_id).replace('/', os.sep)
        else:
            full_path = task_file_id.replace('/', os.sep)
        if not os.path.exists(full_path):
            raise CommonException(TASK_CONF_FILE_NOT_EXISTS, status_code=400,
                                  msg_dict={'info': full_path})

        self.task_file_full_path = full_path
        logger.info('task_file_full_path: {}'.format(self.task_file_full_path))

        self.task_file_id = task_file_id
        self.task_id = task_id
        self.job_id_list = job_id_list

    def load(self) -> TaskDetail:
        """
        加载任务配置
        :return:
        """
        task_conf, job_ctl_list = self.__resolve_file_job_ctl_list()
        job_detail_list = []
        for job_ctl in job_ctl_list:
            if self.job_id_list is not None and job_ctl.job_id not in self.job_id_list:
                continue
            file_job_detail_loader = FileJobDetailLoader(job_ctl)
            try:
                job_detail = file_job_detail_loader.load()
            except Exception as e:
                raise RuntimeError('load {} failure, cause: {}'.format(job_ctl.job_id, str(e)))
            job_detail_list.append(job_detail)
        task_model = TaskModel(self.task_id, 'file:' + self.task_file_id, {})
        if task_conf.get('job_concurrency') is not None:
            task_model.job_concurrency = int(task_conf.pop('job_concurrency'))
        task_model.pass_through = task_conf
        return TaskDetail(task_model, job_detail_list)

    # 解析走 file 配置的 job
    def __resolve_file_job_ctl_list(self) -> Tuple[Dict, List[FileJobCtl]]:
        task_file_name = self.task_file_full_path
        encoding = get_file_encoding(task_file_name)
        # 读入 job_config_back.ini
        temp = ffc.conf_as_dict(task_file_name, encoding=encoding, case_sensitive=True)

        if not temp[0] or temp[2] < 1:
            # 没有找到 job 编排文件, 更新 task 状态为 F, 并结束

            # 2019.6.13 edit by jun.hu
            # self._write_task_error_info(task_file_name)
            # 任务错误推动猫头鹰
            # process_task_result(self.task_id, self._sys_conf_dict)

            logger.error(
                'task execute error, task_id: ' + self.task_id + ', cause read file error: ' + task_file_name)
            raise CommonException(TASK_CONF_FILE_READ_ERROR, status_code=400,
                                  msg_dict={'info': task_file_name})

        task_file_section = temp[1]

        logger.info('task_file_section: %s', json.dumps(task_file_section, ensure_ascii=False))

        task_conf = task_file_section.pop('task_conf') if 'task_conf' in task_file_section else {}
        job_ctl_list = []
        for job_id, value in task_file_section.items():
            if value['tc_file_directory'].startswith('data/'):
                tc_file_dir_abs = os.path.join(agbot_config.basedir, value['tc_file_directory'].replace('/', os.sep))
            else:
                tc_file_dir_abs = os.path.join(dirname(self.task_file_full_path),
                                               value['tc_file_directory'].replace('/', os.sep))

            if value.get('attachment_directory') is not None:
                if value['attachment_directory'].startswith('data/'):
                    attachment_dir_abs = os.path.join(agbot_config.basedir,
                                                      value['attachment_directory'].replace('/', os.sep))
                else:
                    attachment_dir_abs = os.path.join(dirname(self.task_file_full_path),
                                                      value['attachment_directory'].replace('/', os.sep))
            else:
                attachment_dir_abs = None
            job_ctl = FileJobCtl(job_id, value['job_desc'], tc_file_dir_abs, attachment_dir_abs)
            job_ctl_list.append(job_ctl)

        return task_conf, job_ctl_list


class ParameterTaskDetailLoader(TaskDetailLoader):

    def __init__(self,
                 task_id: str,
                 task_file_id: str,
                 job_id_list: str,
                 job_specific: Dict,
                 tc_flag_list: str,
                 global_var: Dict,
                 task_create_system: str,
                 task_create_user: str
                 ):
        self.job_id_list = job_id_list.split(',') if is_not_blank(job_id_list) else None
        self.job_specific = job_specific
        self.tc_flag_list = tc_flag_list.split(',') if is_not_blank(tc_flag_list) else None
        self.global_var = global_var
        self.crt_sys = task_create_system
        self.crt_user = task_create_user
        self.delegate = FileTaskDetailLoader(task_id, task_file_id, self.job_id_list)

    def load(self) -> TaskDetail:
        task_detail_raw = self.delegate.load()
        job_detail_map = {job_detail.job_model.id: job_detail for job_detail in task_detail_raw.job_detail_list}
        job_detail_list_new = []
        job_id_list = self.job_id_list
        if job_id_list is None:
            job_id_list = [job_detail.job_model.id for job_detail in task_detail_raw.job_detail_list]
        for job_id in job_id_list:
            job_detail: Optional[JobDetail] = job_detail_map.get(job_id)
            if job_detail is None:
                continue
            tc_model_new = copy(job_detail.job_model)
            if self.job_specific is not None \
                and self.job_specific.get(job_id) is not None \
                    and self.job_specific.get(job_id).get("concurrency") is not None:
                tc_model_new.concurrency = int(self.job_specific.get(job_id).get("concurrency"))
            tc_detail_list_new = self.filter_tc(job_id, job_detail.tc_detail_list)

            job_detail_list_new.append(
                JobDetail(tc_model_new,
                          tc_detail_list_new
                          ))
        task_model_new = TaskModel(task_detail_raw.task_model.id,
                                   task_detail_raw.task_model.task_src,
                                   self.global_var)
        task_model_new.crt_sys = self.crt_sys
        task_model_new.crt_user = self.crt_user
        task_model_new.job_concurrency = task_detail_raw.task_model.job_concurrency
        task_model_new.pass_through = task_detail_raw.task_model.pass_through
        return TaskDetail(task_model_new, job_detail_list_new)

    def filter_tc(self, job_id: str, tc_detail_list: List[TcDetail]):

        if self.tc_flag_list is not None:
            tc_detail_list = list(
                filter(lambda d: len(set(self.tc_flag_list.split(",")) & set(d.flag_list)) > 0,
                       tc_detail_list))

        if self.job_specific is not None \
            and self.job_specific.get(job_id) is not None \
                and self.job_specific.get(job_id).get("tc_flag") is not None:
            tc_detail_list = list(
                filter(lambda d: len(
                    set(self.job_specific.get(job_id).get("tc_flag").split(",")) & set(d.flag_list)) > 0,
                       tc_detail_list))

        if self.job_specific is not None \
            and self.job_specific.get(job_id) is not None \
                and self.job_specific.get(job_id).get("tc_id") is not None:
            tc_detail_list = list(
                filter(lambda d: self.job_specific.get("tc_id") == d.id,
                       tc_detail_list))

        return tc_detail_list