# @Time    : 2018/7/10  21:16
# @Desc    : 日志检查插件
from enum import Enum

from .es import LogESTestPoint
from .ssh import LogSSHTestPoint
from ..base.tp_base import TpBase, Conf, VerticalContext


# LogTestPoint
class LogTestPoint(TpBase):

    # 类的初始化过程
    # 2018.6.11 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = LogTestPointEnum
        channel = self.tp_conf.get(LogTestPointEnum.channel.key, LogTestPointEnum.channel.default)
        if channel == Channel.ES.value:
            self.agent = LogESTestPoint(tp_conf, vertical_context)
        elif channel == Channel.SSH.value:
            self.agent = LogSSHTestPoint(tp_conf, vertical_context)

    # 准备请求参数
    # 2018.6.11 create by yanan.wu #748921
    def build_request(self):
        return self.agent.build_request()

    # 测试案例的执行
    # 2018.6.11 create by yanan.wu #748921
    def execute(self, request):
        return self.agent.execute(request)

    # 预期结果的校验
    # 2018.6.11 create by yanan.wu #748921
    def test_status(self):
        return self.agent.test_status()

    # 后处理
    def post_handler(self):
        return self.agent.post_handler()


# 日志检查类型
# 2018.6.12 create by yanan.wu #806640
class Channel(Enum):
    # 行数校验
    ES = 'es'
    # 正则校验
    SSH = 'ssh'


# 日志配置文件枚举
class LogTestPointEnum(Conf):
    tp_name = 'tp_name', 'tp 名称', True, ''
    channel = 'channel', '渠道', True, Channel.ES.value
