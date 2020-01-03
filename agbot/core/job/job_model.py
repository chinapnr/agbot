from abc import abstractmethod
from typing import List, Dict, Tuple

from .job_ctl import JobCtl
from ...constant.ag_enum import Conf


class JobConf(Conf):
    execution_chain = 'execution_chain', 'tp执行链', True, ''
    pretreatment = 'pretreatment', '预处理', False, ''
    data_range = 'data_range', '数据范围', False, '1,999999'
    tc_id = 'tc_id', '案例标识', False, ''
    concurrency = 'concurrency', '并发数', False, '2'


class JobAttachment:

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def content(self) -> bytes:
        pass


class JobModel:

    attachment: List[JobAttachment]

    def __init__(self,
                 id: str,
                 desc: str,
                 job_ctl: JobCtl,
                 concurrency: int,
                 pretreatment: List[str],
                 plugin_table: Dict[str, Dict[str, str]],
                 tp_table: Dict[str, Dict[str, str]],
                 start_with: str,
                 data_range: Tuple[int, int],
                 tc_id: str,
                 attachment: List[JobAttachment]):
        """
        :type id: job id
        :type desc: job desc
        :type job_ctl: job 加载控制器
        :type concurrency: 并发数
        :type pretreatment: 预处理插件列表
        :type plugin_table: plugin_id, plugin的具体配置
        :type tp_table: tp_id, tp的具体配置
        :type start_with: 第一个运行的tp_id
        :type data_range: 案例配置中的 data_range
        :type tc_id: 案例配置中的 tc_id
        :type attachment: 附件列表
        """
        self.id = id
        self.desc = desc
        self.job_ctl = job_ctl
        self.concurrency = concurrency
        self.pretreatment = pretreatment
        self.plugin_table = plugin_table
        self.tp_table = tp_table
        self.start_with = start_with
        self.data_range = data_range
        self.tc_id = tc_id
        self.attachment = attachment

    def __str__(self):
        repr_str = ("<JobModel("
                    "id={id}, "
                    "desc={desc}, "
                    "concurrency={concurrency}, "
                    "pretreatment={pretreatment}, "
                    "start_with={start_with},"
                    "data_range={data_range}"
                    ")>".format(
                        id=self.id,
                        desc=self.desc,
                        concurrency=self.concurrency,
                        pretreatment=self.pretreatment,
                        start_with=self.start_with,
                        data_range=self.data_range))
        return repr_str

    def __repr__(self):
        return self.__str__()



