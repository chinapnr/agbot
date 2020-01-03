# @Time    : 2018/9/27  14:39
# @Desc    : shell执行插件

import time
from datetime import datetime

import paramiko
from fishbase.fish_logger import logger

from ..base.tp_base import TpBase, TestStatus, Conf, VerticalContext

SSH_PORT = 22


# ShellTestPoint
class ShellTestPoint(TpBase):

    # 类的初始化过程
    # 2018.9.27 create by yang.xu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.__tc_start_time = ''
        self.vertical_context = vertical_context

    # 准备请求参数
    # 2018.9.27 create by yang.xu #748921
    def build_request(self):
        tc_ctx = self.vertical_context.tc_context
        try:
            # 获取 tc 执行起始时间
            time_struct = time.mktime(tc_ctx.start_time.timetuple())
            self.__tc_start_time = datetime.utcfromtimestamp(
                time_struct).strftime('%Y-%m-%dT%H:%M:%S')

            # 请求参数
            self.req_param[ShellTestPointEnum.host.key] = self.tp_conf.get(ShellTestPointEnum.host.key)
            if self.tp_conf.get(ShellTestPointEnum.port.key) is None:
                self.req_param[ShellTestPointEnum.port.key] = SSH_PORT
            else:
                self.req_param[ShellTestPointEnum.port.key] = self.tp_conf.get(ShellTestPointEnum.port.key)

            self.req_param[ShellTestPointEnum.user_name.key] = self.tp_conf.get(ShellTestPointEnum.user_name.key)
            self.req_param[ShellTestPointEnum.password.key] = self.tp_conf.get(ShellTestPointEnum.password.key)
            self.req_param[ShellTestPointEnum.shell_cmd.key] = self.tp_conf.get(ShellTestPointEnum.shell_cmd.key)
            self.req_param[ShellTestPointEnum.shell_file_path.key] = self.tp_conf.get(ShellTestPointEnum.shell_file_path.key)
            return self.req_param

        except RuntimeError as e:
            logger.error('tp->log:get req params error %s', str(e))
            raise Exception('tp->log:get req params error' + str(e))

    # 测试案例的执行
    # 2018.9.27 create by yang.xu #748921
    # 2018.11.21 增加端口不填时，默认端口22 edit by yang.xu
    def execute(self, request):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            host = self.tp_conf.get(ShellTestPointEnum.host.key)
            user_name = self.tp_conf.get(ShellTestPointEnum.user_name.key)
            password = self.tp_conf.get(ShellTestPointEnum.password.key)

            # 默认不填端口为22
            port = self.tp_conf.get(ShellTestPointEnum.port.key)
            if port is None:
                port = SSH_PORT

            ssh.connect(host, port=port, username=user_name, password=password, allow_agent=False, look_for_keys=False)

            shell_cmd = self.tp_conf.get(ShellTestPointEnum.shell_cmd.key)
            shell_file_path = self.tp_conf.get(ShellTestPointEnum.shell_file_path.key)

            # 选择shell命令或脚本路径
            if shell_cmd is not None:
                cmd = shell_cmd
            elif shell_file_path is not None:
                cmd = 'sh %s' % shell_file_path
            else:
                logger.error('tp->shell:execute error %s', 'shell命令为空')
                raise Exception('tp->shell:execute error　shell命令为空')

            stdin, stdout, stderr = ssh.exec_command(cmd)
            out_info = stdout.read().decode('utf-8')
            err_info = stderr.read().decode('utf-8')
            ssh.close()
            result = {'result': True}
            if err_info:
                result = {'result': err_info}
                logger.info('tp->shell:execute failed: %s', err_info)
            logger.info('tp->shell:execute success: %s', out_info)
            return result, ''
        except Exception as e:
            logger.error('tp->shell:execute error %s', str(e))
            raise Exception('tp->shell:execute error' + str(e))

    # 执行结果
    # 2018.9.27 create by yang.xu #748921
    def test_status(self):
        tc_ctx = self.vertical_context.tc_context
        if tc_ctx.current_tp_context.response.content.get('result') is True:
            return TestStatus.PASSED
        else:
            return TestStatus.NOT_PASSED

    # 后处理
    def post_handler(self):
        pass


# shell配置文件枚举
class ShellTestPointEnum(Conf):
    tp_name = 'tp_name', 'tp 名称', True, ''
    host = 'host', '服务器地址', True, ''
    port = 'port', '端口号', True, ''
    user_name = 'user_name', '用户名', True, ''
    password = 'password', '密码', True, ''
    shell_file_path = 'shell_file_path', '执行文件路径', False, ''
    shell_cmd = 'shell_cmd', 'shell命令', False, ''
