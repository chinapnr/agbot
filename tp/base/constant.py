from enum import Enum


class SignType(Enum):
    RSA = '01'
    MD5_RSA = '02'
    CFCA = '03'
    HMAC256 = '04'
    TTY_MD5 = '05'
    TTY_CYPT = '06'


class TestPointType(Enum):
    API = 'api'
    SQL = 'sql'
    UI = 'ui'
    LOG = 'log'


class CheckExpectType(Enum):
    EQUAL = '01'
    UNEQUAL = '02'