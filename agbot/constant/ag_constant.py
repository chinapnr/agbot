cur_api_ver_list = ['v1.0.0']

# 正确返回信息
COMMON_SUCCESS = 90000

# 错误码信息
USER_INFO_FROM_ARGS_ERROR = 90100   # user info from post/get form/args error
COMMON_ERROR = 90101        # 统一错误码
REQUEST_PARAM_ILLEGAL = 90102  # 请求参数不合法

TASK_NOT_EXISTS = 10000  # task 不存在
TASK_ALREADY_EXISTS = 10001  # task 已存在
TASK_START_ERROR = 10002  # task 启动失败
TASK_CONF_FILE_NOT_EXISTS = 10010  # task 配置文件不存在
TASK_CONF_FILE_READ_ERROR = 10011

JOB_CONF_FILE_NOT_EXISTS = 10110  # job配置文件不存在
JOB_CONF_FILE_READ_ERROR = 10111  # job配置文件解析失败
JOB_DATA_FILE_NOT_EXISTS = 10112  # job数据文件不存在
JOB_DATA_FILE_READ_ERROR = 10113


EMSG = {
    COMMON_ERROR: 'system error',
    TASK_ALREADY_EXISTS: 'task already exists',
    TASK_NOT_EXISTS: 'task not exists',
    REQUEST_PARAM_ILLEGAL: 'request {param_name} is illegal',
    USER_INFO_FROM_ARGS_ERROR: 'user info from get/post form/arg error',
    JOB_CONF_FILE_NOT_EXISTS: 'job conf file not exists',
    JOB_CONF_FILE_READ_ERROR: 'job conf file read error: {info}',
    JOB_DATA_FILE_NOT_EXISTS: 'job data file not exists',
    JOB_DATA_FILE_READ_ERROR: 'job data file read error: {info}',
    TASK_START_ERROR: 'task starts failure',
    TASK_CONF_FILE_NOT_EXISTS: 'task file not exists : {info}',
    TASK_CONF_FILE_READ_ERROR: 'task file read error : {info}'
}
