from typing import Dict, Type

from ..model.context import VerticalContext
from ...constant.ag_enum import Conf


class TpInterface(object):

    def __init__(self, tp_conf: Dict, vertical_context: VerticalContext):
        pass

    # 配置枚举
    def get_conf_enum(self) -> Type[Conf]:
        raise NotImplementedError

    # 预处理
    def pre_handler(self):
        raise NotImplementedError

    # 准备请求参数
    def build_request(self):
        raise NotImplementedError

    # 测试案例的执行
    def execute(self, request):
        raise NotImplementedError

    # 预期结果的校验
    def test_status(self):
        raise NotImplementedError

    # 后处理
    def post_handler(self):
        raise NotImplementedError
