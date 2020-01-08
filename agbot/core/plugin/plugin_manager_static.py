from fishbase import logger


class PluginsManagerStatic(object):
    """
    1. 现阶段插件是用来进行请求或者响应参数的处理
    2. 暂时规定插件必须实现 run 方法
    3. 使用实例:
        pm = PluginsManager()
        pm.run_plugin('demo.demo_md5',
        {'sign_type':'md5','data_sign_params':'param1, param2'}, {'param1':'1','param2':'2','param3':'3'})
    """

    def __init__(self, package):
        self.__plugin_dict = {}
        try:
            pr = __import__(package)
            pr.register(self)
        except Exception as e:
            logger.exception('plugins_path not found: %s; cause: %s', package, str(e))
            raise RuntimeError('plugins_path not found: {}; cause: {}'.format(package, str(e))) from e

    def run_plugin(self, plugin_name, plugin_conf_dict, ctx):
        try:
            plugin = self.__plugin_dict[plugin_name]
            return plugin.run(plugin_conf_dict, ctx)
        except Exception as e:
            logger.exception('run  plugin error: %s; cause: %s', plugin_name, str(e))
            raise e

    def add_plugin(self, plugin_dict):
        self.__plugin_dict.update(plugin_dict)
