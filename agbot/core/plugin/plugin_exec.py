import datetime
from datetime import datetime

from fishbase import logger

from .plugin_context import PluginContext
from .plugin_manager_dynamic import PluginsManagerDynamic
from ..model.context import VerticalContext
from ..utils import resolve_placeholder
from ...constant.ag_enum import TestStatus


class PluginExecutor:

    def __init__(self):
        self.__plugin_manager = PluginsManagerDynamic("plugin")

    def __do_execute(self,
                     vertical_ctx: VerticalContext,
                     plugin_id: str,
                     plugin_ctx: PluginContext):
        conf_dict_raw = vertical_ctx.job_context.job_model.plugin_table.get(plugin_id)
        assert conf_dict_raw is not None, '[{}] not found'.format(plugin_id)

        conf_dict, replacement = resolve_placeholder(conf_dict_raw, vertical_ctx)
        plugin_ctx.conf = conf_dict
        plugin_ctx.replacement.extend(replacement)

        plugin_path = conf_dict['plugin']
        self.__plugin_manager.run_plugin(plugin_path, conf_dict, vertical_ctx)
        plugin_ctx.end_time = datetime.now()
        plugin_ctx.status = TestStatus.PASSED

    def do_execute(self,
                   vertical_ctx: VerticalContext,
                   plugin_id: str,
                   plugin_ctx: PluginContext
                   ):
        try:
            self.__do_execute(vertical_ctx, plugin_id, plugin_ctx)
        except BaseException as e:
            logger.exception('PluginExecutor error: {}, cause: {}, tc_data_dict: {}'
                             .format(plugin_id, str(e), str(vertical_ctx.tc_context)))
            plugin_ctx.end_time = datetime.now()
            plugin_ctx.status = TestStatus.ERROR
            raise e
