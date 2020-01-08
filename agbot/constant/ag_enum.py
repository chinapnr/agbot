# @Time    : 2018/4/4  12:39
# @Desc    : 常量类

from enum import Enum


# 测试状态
class TestStatus(Enum):
    # 初始化
    INIT = 'I'
    # 运行中
    RUNNING = 'R'
    # 通过
    PASSED = 'S'
    # 未通过
    NOT_PASSED = 'F'
    # 错误
    ERROR = 'E'
    # 跳过
    SKIP = 'K'


class Conf(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, key, desc, require, default):
        self.__key = key
        self.__desc = desc
        self.__require = require
        self.__default = default

    @property
    def key(self):
        return self.__key

    @property
    def desc(self):
        return self.__desc

    @property
    def require(self):
        return self.__require

    @property
    def default(self):
        return self.__default








