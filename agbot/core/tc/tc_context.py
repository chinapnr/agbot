from datetime import datetime
from typing import List, Union

from .tc_detail import TcDetail
from ..plugin.plugin_context import PluginContext
from ..tp.tp_context import TpContext
from ...constant.ag_enum import TestStatus
from ...tools.ag_error import ErrorInfo


class TcContext:
    tc_detail: TcDetail
    error: ErrorInfo
    replacement: List
    status: TestStatus
    tp_and_plugin_context_list: List[Union[TpContext, PluginContext]]

    def __init__(self,
                 tc_detail: TcDetail,
                 start_time: datetime):
        self.tc_detail = tc_detail
        self.tp_and_plugin_context_list = []
        self.start_time = start_time
        self.end_time = None
        self.status = TestStatus.INIT
        self.replacement = []
        self.seq_id = None
        self.error = None

    @property
    def current_tp_context(self) -> TpContext:
        return list(filter(lambda ctx: isinstance(ctx, TpContext), self.tp_and_plugin_context_list))[-1]

    def __str__(self):
        repr_str = ("<TcContext("
                    "tc_detail={tc_detail} "
                    "start_time={start_time} "
                    "end_time={end_time} "
                    "status={status} "
                    ")>".format(
                        tc_detail=self.tc_detail,
                        start_time=self.start_time,
                        end_time=self.end_time,
                        status=self.status))
        return repr_str

    def __repr__(self):
        return self.__str__()


