import pickle

from kombu.serialization import register

from agbot.agbot_config import agbot_config
from agbot.db.db_base import ParserSessionScope
from agbot.db.db_tool import DBUtils
from agbot.endpoint.server_conf import ServerConfig

register('pickle', pickle.dumps, pickle.loads,
         content_type='pickle',
         content_encoding='utf-8')

BROKER_URL = 'amqp:////'
CELERY_RESULT_BACKEND = 'redis:'
CELERY_REDIS_MAX_CONNECTIONS = 50

BROKER_POOL_LIMIT = 100
BROKER_CONNECTION_TIMEOUT = 30
BROKER_CONNECTION_RETRY = True
BROKER_CONNECTION_MAX_RETRIES = None

CELERY_EVENT_SERIALIZER = 'pickle'
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERYD_HIJACK_ROOT_LOGGER = False

CELERY_IGNORE_RESULT = True
CELERY_TRACK_STARTED = True
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_WORKER_LOST_WAIT = 60
CELERYD_MAX_TASKS_PER_CHILD = 200

CELERY_EVENT_QUEUE_PREFIX = 'agbot-dev'
CELERY_ROUTES = {
    'tasks.execute_tc': 'agbot-dev.celery.tasks',
    'tasks.process_job_context': 'agbot-dev.celery.tasks',
    'tasks.process_task_context': 'agbot-dev.celery.tasks',
    'tasks.task_separator': 'agbot-dev.celery.tasks'
}

sqlalchemy_database_uri = ServerConfig.SQLALCHEMY_DATABASE_URI
session_scope = ParserSessionScope.get_session_scope(sqlalchemy_database_uri,
                                                     db_type=agbot_config.sys_conf_dict['system']['db']['type'],
                                                     pool_conf_dict=agbot_config.sys_conf_dict['system']['db'][
                                                         'connection_pool'])
DBUtils.init_session_scope(session_scope)
