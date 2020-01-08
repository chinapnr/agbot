# 插件文件必须实现 run 方法
# 参数 plugin_conf_dict： 插件配置
# 参数 param_dict： 参数字典
# 本 demo 实现了一个根据插件配置， 生成一个 md5 签名的功能
# 使用实例:
#   pm = PluginsManager()
#   pm.run_plugin('demo.demo_md5',
# {'sign_type':'md5','data_sign_params':'param1, param2'}, {'param1':'1','param2':'2','param3':'3'})

import hashlib


def run(plugin_conf_dict, vertical_ctx):
    '''
    实例中的插件配置
    [sign_conf]
    sign_type = md5
    data_sign_params = param1, param2
    '''

    data_params_name_str = plugin_conf_dict['data_sign_params']
    data_param_name_list = list(data_params_name_str.split(','))

    plain_text_dict = {}
    for data_param_name in data_param_name_list:
        if data_param_name in vertical_ctx.tc_context:
            plain_text_dict[data_param_name] = vertical_ctx.tc_context[data_param_name]

    md5_text = md5(plugin_conf_dict, plain_text_dict)
    print('demo md5_text:' + md5_text)


def md5(params_dict, plain_text_dict):
    if params_dict.get('sign_type') == 'md5':
        plain_text = ''
        # 获取签名明文
        if plain_text_dict is not None:
            for param_key in plain_text_dict.keys():
                # 拼接明文
                plain_text += param_key + '=' + plain_text_dict.get(param_key) + '|'
            data_bytes = bytes(plain_text, 'utf-8')
            return hashlib.md5(data_bytes).hexdigest()
