import re

import paramiko
from fishbase.fish_logger import logger

from ..base.tp_base import TpBase, Conf, VerticalContext


# LogTestPoint
class LogSSHTestPoint(TpBase):

    # 类的初始化过程
    # 2018.6.11 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = LogSSHTestPointEnum
        self.vertical_context = vertical_context

    # 准备请求参数
    # 2018.6.11 create by yanan.wu #748921
    def build_request(self):
        try:
            # 获取请参
            self.req_param = {
                'ip': self.tp_conf.get('ip'),
                'port': self.tp_conf.get('port', LogSSHTestPointEnum.port.default),
                'username': self.tp_conf.get('username'),
                'password': self.tp_conf.get('password'),
                'path': self.tp_conf.get('path'),
                'tail_num': self.tp_conf.get('tail_num'),
                'regex': self.tp_conf.get('regex'),
                'charset': self.tp_conf.get('charset', LogSSHTestPointEnum.charset.default)
            }
            return self.req_param
        except RuntimeError as e:
            logger.error('tp->log:get req params error', str(e))
            raise Exception('tp->log:get req params error', str(e))

    # 测试案例的执行
    # 2018.6.11 create by yanan.wu #748921
    def execute(self, request):
        ssh = paramiko.SSHClient()
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(request.get('ip'),
                        request.get('port'),
                        username=request.get('username'),
                        password=request.get('password'))
            cmd = 'tail -{} {}'.format(request.get('tail_num'), request.get('path'))
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode()
            pattern = re.compile(request.get('regex'))
            find_result = pattern.findall(out)
            if find_result is None:
                resp = {'result_value': None}
            else:
                resp = {'result_value': find_result}
            return resp, ''
        except Exception as e:
            logger.error('tp->log:execute error, ' + str(e))
            raise Exception('tp->log:execute error, ' + str(e))
        finally:
            ssh.close()


# 日志配置文件枚举
class LogSSHTestPointEnum(Conf):
    tp_name = 'tp_name', 'tp 名称', True, ''
    expect_data = 'expect_data', '期望返回结果', True, ''
    ip = 'ip', 'ip', True, ''
    port = 'port', 'port', False, '22'
    username = 'username', '用户名', True, ''
    password = 'password', '密码', True, ''
    path = 'file_path', '文件路径', True, ''
    tail_num = 'tail_num', '倒数行数', True, ''
    regex = 'regex', '正则', True, ''
    charset = 'charset', '字符集', False, 'utf-8'