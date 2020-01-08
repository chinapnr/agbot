import json
import os
from typing import List, Dict, Tuple

from fishbase import csv_file_to_list, conf_as_dict

from .job_ctl import FileJobCtl
from .job_model import JobModel, JobConf, JobAttachment
from ..tc.tc_detail import TcDetail, weight_alias, weight_medial, weight_high
from ..utils import is_not_blank, get_abs_filenames_by_suffix, get_file_encoding
from ...tools.ag_common import dict_update_deep


class JobDetail:

    def __init__(self,
                 job_model: JobModel,
                 tc_detail_list: List[TcDetail],
                 ):
        """
        :type tc_detail_list: 数据列表
        :type job_model: job 模型
        """
        self.job_model = job_model
        self.tc_detail_list = tc_detail_list

    def __str__(self):
        repr_str = ("<JobDetail("
                    "tc_detail_list={tc_detail_list}, "
                    "job_model={job_model}"
                    ")>".format(
                        tc_detail_list=self.tc_detail_list,
                        job_model=self.job_model))
        return repr_str

    def __repr__(self):
        return self.__str__()


class JobDetailLoader:

    def load(self) -> JobDetail:
        pass


class FileJobAttachment(JobAttachment):

    def __init__(self,
                 file_path: str):
        self._file_path = file_path
        self._content = None

    @property
    def id(self) -> str:
        return self._file_path

    @property
    def content(self) -> bytes:
        if self._content is not None:
            return self._content

        with open(self._file_path, mode='rb') as f:
            self._content = f.read()
        return self._content


class FileJobDetailLoader(JobDetailLoader):

    def __init__(self,
                 file_job_ctl: FileJobCtl):
        self.file_job_ctl = file_job_ctl

    def load(self) -> JobDetail:
        job_conf_dict = FileJobDetailLoader.__resolve_job_conf_dict(self.file_job_ctl)
        # 确认没有丢失配置 job_conf 必需，并且 job_conf 节的内容必需包含 JobConf
        job_conf_dict_job_conf: Dict[str, str] = job_conf_dict.get('job_conf')

        execution_chain_str: str = job_conf_dict_job_conf.get(JobConf.execution_chain.key, '')
        assert is_not_blank(execution_chain_str), 'illegal ' + JobConf.execution_chain.key

        # 获取 pretreatment 插件，多个插件间以 , 隔开
        pretreatment_str = job_conf_dict_job_conf.get(JobConf.pretreatment.key, '')
        pretreatment = [pre.strip() for pre in pretreatment_str.split(',')] if is_not_blank(pretreatment_str) else []
        # 获取 tp 数据范围，修改为 staticmethod
        data_range = FileJobDetailLoader.__resolve_range(job_conf_dict_job_conf)
        # 获取 tc_id
        tc_id = job_conf_dict_job_conf.get(JobConf.tc_id.key)
        # 并行 tc 数，默认为 1
        concurrency = int(job_conf_dict_job_conf.get(
            JobConf.concurrency.key,
            JobConf.concurrency.default
        ))

        tp_table = {}
        plugin_table = {}
        for k, v in job_conf_dict.items():  # type: (str, Dict[str, str])
            if k.startswith('tp_'):
                tp_table[k.strip()] = v
            elif k.startswith('plugin_') or k.startswith('plugins_'):
                plugin_table[k.strip()] = v

        tc_dict_list = self.__resolve_job_data()[data_range[0]: data_range[1] + 1]
        if len(tc_dict_list) == 0:
            raise ValueError('no data loaded for {}'.format(self.file_job_ctl))
        tc_detail_list = [TcDetail(d.get('tc_id') if is_not_blank(d.get('tc_id')) else str(data_range[0] + 1 + i),
                                   d.get('tc_flag', '').split(','),
                                   self._convert_tc_weight_to_int(d.get('tc_weight')),
                                   d)
                          for i, d in enumerate(tc_dict_list)]

        attachment = self.__load_attachment()
        job_model = JobModel(
            self.file_job_ctl.job_id,
            self.file_job_ctl.desc,
            self.file_job_ctl,
            concurrency,
            pretreatment,
            plugin_table,
            tp_table,
            execution_chain_str,
            data_range,
            tc_id,
            attachment
        )
        return JobDetail(
            job_model,
            tc_detail_list
        )

    def __load_attachment(self) -> List[JobAttachment]:
        attachment = []

        if self.file_job_ctl.attachment_dir is not None:
            for root, dirs, files in os.walk(self.file_job_ctl.attachment_dir):
                for file_name in files:
                    attachment.append(FileJobAttachment(os.path.join(root, file_name)))

        for root, dirs, files in os.walk(os.path.join(self.file_job_ctl.job_dir, 'attachment')):
            for file_name in files:
                attachment.append(FileJobAttachment(os.path.join(root, file_name)))

        for root, dirs, files in os.walk(self.file_job_ctl.job_dir):
            for file_name in files:
                non_attach_suffix = ['.txt', '.ini', '.csv', '.conf.json']
                if any(file_name.endswith(nas) for nas in non_attach_suffix):
                    continue
                attachment.append(FileJobAttachment(os.path.join(root, file_name)))
        return attachment

    # 封装 job 请求数据，获取 job 请求数据文件
    def __resolve_job_data(self):
        root_data_list = []
        temp = get_abs_filenames_by_suffix(self.file_job_ctl.job_dir, '.txt')
        if temp[0]:
            filename_txt_list = temp[1]
            container_txt_list = FileJobDetailLoader.__read_data_file(filename_txt_list,
                                                       deli=';')
        else:
            raise Exception('get data filename list error')

        temp = get_abs_filenames_by_suffix(self.file_job_ctl.job_dir, '.csv')
        if temp[0]:
            filename_csv_list = temp[1]
            container_csv_list = FileJobDetailLoader.__read_data_file(filename_csv_list,
                                                       deli=',')
        else:
            raise Exception('get data filename list error')

        container_list = container_txt_list + container_csv_list

        # 20190314 edit by jn.hu 新加逻辑，当测试案例数据文件不存在时提示缺少文件
        if not container_list:
            raise Exception('less test data')

        for data_list in container_list:
            # 合并数据
            root_data_list = FileJobDetailLoader.__merge_params(root_data_list, data_list)
        return root_data_list

    # 解析数据文件
    # 2018.8.6 create by yanan.wu #931475
    @staticmethod
    def __read_data_file(filename_list, deli=None):
        container_list = []
        if filename_list:
            for filename in filename_list:
                encoding = get_file_encoding(filename)
                # 读入数据文件
                data_list = csv_file_to_list(filename, deli=deli, encoding=encoding)
                data_list = FileJobDetailLoader.__convert_params(data_list)
                container_list.append(data_list)
        return container_list

    # 2019.4.10 create by jun.hu 添加注释，修改为列表生成式写法
    # 2018.7.9 create by yanan.wu #904499
    @staticmethod
    def __convert_params(source_list):
        """
        数据文件由列表转换为字典
        :param source_list: 按照行读取的数据文件列表 eg: [['k1', 'k2', 'k3'],
                                                       ['v01', 'v02', 'v03'],
                                                       ['v11', 'v12', 'v13']]
        :return: 数据字典组成的列表 eg: [{'k1': 'v01', 'k2': 'v02', 'k3': 'v03'},
                                       {'k1': 'v11', 'k2': 'v12', 'k3': 'v13'}]
        """
        # 进一步判断，当数据文件中的 param 和值数量不一致时需要抛出错误
        param_count = len(source_list[0])
        data_list = list()
        for index, item in enumerate(source_list[1:], 1):
            if len(item) != param_count:
                raise Exception('数据文件第 {} 行，值的长度和 param 长度不一致，请检查 !'.
                                format(str(index)))
            data_list.append(dict(zip(source_list[0], item)))
        # data_list = [dict(zip(source_list[0], item)) for item in source_list[1:]]
        return data_list

    # 将两个复杂列表合并
    # 2018.7.9 create by yanan.wu #904499
    @staticmethod
    def __merge_params(target_list, source_list):
        if not target_list:
            target_list = source_list
        else:
            for index, data_dict in enumerate(target_list):
                if index < len(source_list):
                    data_dict.update(source_list[index])
        return target_list

    # 封装 job 请求配置，读取测试案例 ini 中 tc_file_directory 对应的 tc_file
    @staticmethod
    def __resolve_job_conf_dict(file_job_ctl: FileJobCtl) -> Dict[str, Dict[str, str]]:

        job_conf_dict = {}
        conf_json = FileJobDetailLoader.__resolve_job_conf_json(file_job_ctl)
        if conf_json is not None:
            dict_update_deep(job_conf_dict, conf_json)
        conf_ini = FileJobDetailLoader.__resolve_job_conf_ini(file_job_ctl)
        if conf_ini is not None:
            dict_update_deep(job_conf_dict, conf_ini)

        if conf_json is None and conf_ini is None:
            raise Exception('get conf error for {} '.format(file_job_ctl.job_dir))

        return job_conf_dict

    @staticmethod
    def __resolve_job_conf_json(file_job_ctl: FileJobCtl):
        json_temp = get_abs_filenames_by_suffix(file_job_ctl.job_dir, '.conf.json')

        conf_files_list = json_temp[1]
        if json_temp[0] and len(conf_files_list) > 0:
            root_conf_dict = {}

            for conf_file in conf_files_list:
                try:
                    with open(conf_file, 'rt') as f:
                        content = f.read()
                    if len(content) > 0:
                        encoding = get_file_encoding(conf_file)
                        conf_dict = json.loads(content, encoding=encoding)
                        root_conf_dict.update(dict(conf_dict))
                except BaseException as e:
                    raise Exception('read json conf file error {}, {} '.format(conf_file, str(e)))
            return root_conf_dict
        else:
            return None

    @staticmethod
    def __resolve_job_conf_ini(file_job_ctl: FileJobCtl):
        ini_temp = get_abs_filenames_by_suffix(file_job_ctl.job_dir, '.ini')

        conf_files_list = ini_temp[1]
        if ini_temp[0] and len(conf_files_list) > 0:
            root_conf_dict = {}
            for conf_file in conf_files_list:
                encoding = get_file_encoding(conf_file)
                # 读入配置文件
                temp_tulple = conf_as_dict(conf_file, encoding=encoding, case_sensitive=True)

                if temp_tulple[0]:
                    conf_dict = temp_tulple[1]
                else:
                    raise Exception('read ini conf file error {} '.format(conf_file))
                root_conf_dict.update(dict(conf_dict))
            return root_conf_dict
        else:
            return None

    # 获取数据范围
    @staticmethod
    def __resolve_range(job_conf_dict_job_conf: Dict[str, str]) -> Tuple[int, int]:
        data_range_start = 0
        data_range_end = 999999
        # self.__resolve_job_conf_dict(self.file_job_ctl)
        data_range_str = job_conf_dict_job_conf.get(JobConf.data_range.key, JobConf.data_range.default)
        data_range_conf = [r.strip() for r in data_range_str.split(',')]
        if is_not_blank(data_range_conf[0]):
            # 配置的值从1开始
            data_range_start = int(data_range_conf[0]) - 1
        if is_not_blank(data_range_conf[1]):
            # 配置的值从1开始
            data_range_end = int(data_range_conf[1]) - 1
        return data_range_start, data_range_end

    @staticmethod
    def _convert_tc_weight_to_int(weight):
        if weight is None:
            return weight_medial
        if isinstance(weight, int):
            return weight
        if is_not_blank(weight):
            weight = weight_alias.get(weight, weight)
            weight = int(weight)
            if weight > weight_high:
                weight = weight_high
            return weight
        else:
            return weight_medial
