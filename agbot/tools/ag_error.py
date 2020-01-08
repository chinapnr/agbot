from enum import Enum

from fishbase.fish_logger import logger

from ..constant.ag_constant import *


class Scope(Enum):
    TP = 'tp'
    TC = 'tc'
    JOB = 'job'
    TASK = 'task'


class ErrorType(Enum):
    ILLEGAL_ARGUMENT = 400
    RUNTIME_ERROR = 500


class ErrorInfo:

    def __init__(self,
                 scope: Scope,
                 status: ErrorType,
                 message: str):
        self.scope = scope
        self.status = status
        self.message = message


# 通用异常
class CommonException(Exception):
    # 默认的返回码
    status_code = ErrorType.ILLEGAL_ARGUMENT

    # 定义 return_code，作为更细颗粒度的错误代码
    # 定义 msg_dict, 作为显示具体元素的 dict
    def __init__(self,
                 biz_code=None,
                 status_code=None,
                 msg_dict=None):
        Exception.__init__(self)
        self.biz_code = biz_code

        if status_code is not None:
            self.status_code = status_code

        if msg_dict is not None:
            self.msg_dict = msg_dict
        else:
            self.msg_dict = None


    # 构造要返回的错误代码和错误信息的 dict
    def to_dict(self):
        rv = {'biz_code': self.biz_code}
        # 增加 dict key: return code

        # 增加 dict key: message, 具体内容由常量定义文件中通过 return_code 转化而来
        if self.msg_dict is not None:
            s = EMSG[self.biz_code].format(**self.msg_dict)
        else:
            s = EMSG[self.biz_code]

        rv['message'] = s

        # 日志打印
        logger.warning(s)

        return rv

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()
