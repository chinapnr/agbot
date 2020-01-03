# coding=utf-8
import fishbase.fish_file as fff
from fishbase.fish_logger import logger
from flask import Flask, jsonify

import ext
from agbot.agbot_config import agbot_config
from agbot.constant.ag_constant import *
from agbot.db.db_base import ParserSessionScope
from agbot.db.db_tool import DBUtils
from agbot.tools.ag_error import CommonException


# 生成 sqlite 数据库的 uri 字符串
def get_db_sqlite_uri(db_name):
    # 获得操作系统简称
    # platform = ffc.check_platform()
    # python 3.5 之后 uri 均为 //// , windows 和 nix 系统没有差异

    db_sqlite_uri = 'sqlite:///' + \
                    fff.get_abs_filename_with_sub_path('db', db_name)[1]

    # db_sqlite_uri = ''.join(['sqlite:///', os.path.join(basedir, 'db', db_name)])

    return db_sqlite_uri


class ServerConfig:
    DEBUG = False
    ALLOW_IP = agbot_config.sys_conf_dict['server']['allow_ip']
    IP_PORT = agbot_config.sys_conf_dict['server']['ip_port']
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 60

    # 使用 sqlite 数据库
    if agbot_config.sys_conf_dict['system']['db']['type'] == 'sqlite':
        SQLALCHEMY_DATABASE_URI = get_db_sqlite_uri(
            agbot_config.sys_conf_dict['system']['db']['url'])
    elif agbot_config.sys_conf_dict['system']['db']['type'] == 'mysql':
        SQLALCHEMY_DATABASE_URI = agbot_config.sys_conf_dict['system']['db']['url']


# 初始化 flask app
# common, 实例 app 时指定静态文件夹位置;
app = Flask(__name__, static_folder='./static')
app.config.from_object(ServerConfig)
ext.register(agbot_config.sys_conf_dict)
logger.info('flask server conf setup!')

# 如果数据库类型是 sqlite，则没有 ping 方法
sqlalchemy_database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
is_sqlite_flag = True if 'sqlite' in sqlalchemy_database_uri else False
logger.info('db uri is {}'.format(sqlalchemy_database_uri))

session_scope = ParserSessionScope.get_session_scope(sqlalchemy_database_uri,
                                                     db_type=agbot_config.sys_conf_dict['system']['db']['type'],
                                                     pool_conf_dict=agbot_config.sys_conf_dict['system']['db'][
                                                         'connection_pool'])
# 初始化 session_scope
DBUtils.init_session_scope(session_scope)

# flask 错误处理，装饰器来控制使用 CustomFlaskErr
@app.errorhandler(CommonException)
def handle_flask_error(error):
    # response 的 json 内容为自定义错误代码和错误信息
    response = jsonify(error.to_dict())

    # response 返回 error 发生时定义的标准错误代码
    response.status_code = error.status_code

    return response


# edit 2018.3.7 by xin.guo
# flask 错误处理，装饰器来控制使用 Exception
@app.errorhandler(Exception)
def handle_flask_error(error):
    # 打印异常
    logger.exception(str(error))
    # response 的 json 内容为自定义错误代码和错误信息
    response = jsonify({'return_code': COMMON_ERROR,
                        'message': str(error)})

    # response 返回 error 发生时定义的标准错误代码
    response.status_code = 500
    return response
