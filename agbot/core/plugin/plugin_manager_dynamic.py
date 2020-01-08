import importlib

from fishbase import logger


class PluginsManagerDynamic(object):
    """
    1. 现阶段插件是用来进行请求或者响应参数的处理
    2. 暂时规定插件必须实现 run 方法
    3. 使用实例:
        pm = PluginsManager()
        pm.run_plugin('demo.demo_md5',
        {'sign_type':'md5','data_sign_params':'param1, param2'}, {'param1':'1','param2':'2','param3':'3'})
    """
    def __init__(self, package):

        # 只加载指定 package 包下的插件
        self.__package = package
        try:
            __import__(package)
        except Exception as e:
            logger.exception('plugins_path not found: %s; cause: %s', package, str(e))
            raise RuntimeError('plugins_path not found: {}; cause: {}'.format(package, str(e))) from e

    def run_plugin(self, module_name, plugin_conf_dict, ctx):
        plugin = self.__dynamic_import(module_name)
        try:
            return plugin.run(plugin_conf_dict, ctx)
        except Exception as e:
            logger.exception('run  plugin error: %s; cause: %s', module_name, str(e))
            raise e

    # 加载插件
    def __dynamic_import(self, module_name):
        # 如果已经加载过了, 则直接返回插件
        # if module_name in self.__plugins:
        #     return self.__plugins[module_name]

        # 加载插件
        try:
            module = importlib.import_module('.' + module_name, self.__package)
            return module
        except Exception as e:
            logger.exception('import plugin error: %s; cause: %s', module_name, str(e))
            raise RuntimeError('import plugin error: {}; cause: {}'.format(module_name, str(e))) from e