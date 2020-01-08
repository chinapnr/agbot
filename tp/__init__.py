from . import activemq
from . import api
from . import app
from . import cache
from . import ftp
from . import log
from . import pegasus
from . import shell
from . import socket
from . import sql
from . import ui
from . import zk


def register(plugin_manager):
    plugin_dict = {
        'api': api,
        'activemq': activemq,
        'cache': cache,
        'ftp': ftp,
        'log': log,
        'pegasus': pegasus,
        'shell': shell,
        'socket': socket,
        'sql': sql,
        'ui': ui,
        'zk': zk,
        'app': app
    }

    plugin_manager.add_plugin(plugin_dict)
