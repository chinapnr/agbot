import os
# 程序从这里入口，需要主动添加路径
import sys
from concurrent.futures.thread import ThreadPoolExecutor

import click
import fishbase.fish_common as common
import fishbase.fish_file as fff
from fishbase.fish_logger import logger

import ext
from agbot.agbot_config import agbot_config
from agbot.core.task.task_detail import ParameterTaskDetailLoader, TaskDetail
from agbot.core.task.task_exec_coroutine import TaskExecutorCoroutine
from agbot.core.utils import event_loop
from agbot.db.db_base import ParserSessionScope, Base
from agbot.db.db_tool import DBUtils
from agbot.db.table_task_log import TableTaskLog

_file_path = os.path.split(os.path.realpath(__file__))[0]
# 项目路径添加，为执行 python cmd.py 添加路径
_project_path = os.path.abspath(os.path.dirname(_file_path) + os.path.sep + "..")
sys.path.insert(0, _project_path)
# _file_path 文件路径添加，为 agbot_cli.exe 添加路径
sys.path.insert(0, _file_path)
agbot_config.basedir = os.path.abspath('')
ext.register(agbot_config.sys_conf_dict)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

_thread_pool = ThreadPoolExecutor(max_workers=128)
task_executor = TaskExecutorCoroutine(agbot_config.sys_conf_dict, _thread_pool)


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    Autogo Bot command line tools
    """
    pass


@main.command('runtask', context_settings=CONTEXT_SETTINGS)
@click.option('--filename', '-f', help='task file name', required=True)
@click.option('--joblist', '-j', help='task job list', required=False, default=None)
@click.option('--flag', '-fl', help='task test flag', required=False, default=None)
def runtask(filename, joblist, flag):
    """
    start a task
    """
    if not filename:
        click.echo(click.style('file name error, please check !', fg='red'))
        sys.exit()
    create_sqlite_db()
    init_db_info()
    task_id = common.get_time_uuid().replace('-', '')
    try:
        task_detail_loader = ParameterTaskDetailLoader(
            task_id,
            filename,
            joblist,
            None,
            flag,
            None,
            'agbot-cmd',
            'agbot-cmd'
        )
        # task_content 配置
        task_detail = task_detail_loader.load()  # type: TaskDetail
        logger.info('start task-------------------------------------------task_id:' + task_id)
        # 检查任务是否已经存在
        _, tab_task_log = DBUtils.query(TableTaskLog, filter_dict={'task_id': task_id})
        if tab_task_log:
            click.echo(click.style('task already exists', fg='red'))
            sys.exit(-1)
        # 直接使用线程执行 task , 然后返回前端成功状态
        click.echo(click.style('task [{}] running, please wait ...'.format(task_id), fg='green'))
        event_loop.run_until_complete(task_executor.execute(task_detail))
    except Exception as e:
        logger.exception('runtask error, {}'.format(str(e)))
        click.echo(click.style('创建任务失败, 请检查脚本文件. 错误原因: {}'.format(str(e)), fg='red'))


# 生成 sqlite 数据库的 uri 字符串
def get_db_sqlite_uri(db_name):
    # 获得操作系统简称
    # platform = ffc.check_platform()
    # python 3.5 之后 uri 均为 //// , windows 和 nix 系统没有差异

    db_sqlite_uri = 'sqlite:///' + \
                    fff.get_abs_filename_with_sub_path('db', db_name)[1]

    # db_sqlite_uri = ''.join(['sqlite:///', os.path.join(basedir, 'db', db_name)])

    return db_sqlite_uri


def init_db_info():
    sqlite_uri = get_db_sqlite_uri(
        agbot_config.sys_conf_dict['system']['db']['url'])
    session_scope = ParserSessionScope.get_session_scope(sqlite_uri,
                                                         db_type=agbot_config.sys_conf_dict['system']['db']['type'],
                                                         pool_conf_dict=agbot_config.sys_conf_dict['system']['db'][
                                                             'connection_pool'])
    # 初始化 session_scope
    DBUtils.init_session_scope(session_scope)


# @main.command('initdb', context_settings=CONTEXT_SETTINGS)
def create_sqlite_db():
    """
    init sqlite db
    """

    sqlite_uri = get_db_sqlite_uri(
        agbot_config.sys_conf_dict['system']['db']['url'])

    # 如果 sqlite 文件路径已经存在，直接返回
    if os.path.exists(sqlite_uri):
        return ''

    # 初始化数据库
    logger.info('uri is {}'.format(sqlite_uri))
    engine = ParserSessionScope.get_engine(sqlite_uri, agbot_config.sys_conf_dict['system']['db']['connection_pool'])
    Base.metadata.create_all(engine)
