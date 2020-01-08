# @Time ? ?: 2018/7/10? 16:23
# @Desc    : tp_ftp执行插件
import io
import os
from ftplib import FTP

import paramiko
from fishbase.fish_logger import logger

from ..base.tp_base import TpBase, Conf, VerticalContext


class FtpTestPoint(TpBase):

    # 类的初始化过程
    # 2018.3.12 create by yanan.wu #748921
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = FtpTestPointEnum
        self.__jfetch_conf_dict = {}
        self.resp_dict = {}
        self.file_download = None
        self.vertical_context = vertical_context

    # 准备请求参数
    # 2018.3.12 create by yanan.wu #748921
    # 2018.5.22 edit by yang.xu #848884
    def build_request(self):
        try:
            # 获取请参
            # TpBase.build_params(self, tc_ctx_dict)
            self.req_param[FtpTestPointEnum.req_data.key] = self.tp_conf.get(FtpTestPointEnum.req_data.key)
            self.req_param[FtpTestPointEnum.address.key] = self.tp_conf.get(FtpTestPointEnum.address.key)
            self.req_param[FtpTestPointEnum.username.key] = self.tp_conf.get(FtpTestPointEnum.username.key)
            self.req_param[FtpTestPointEnum.password.key] = self.tp_conf.get(FtpTestPointEnum.password.key)
            self.req_param[FtpTestPointEnum.server_type.key] = self.tp_conf.get(FtpTestPointEnum.server_type.key)
            return self.req_param

        except Exception as e:
            logger.exception('FtpTestPoint build_params error, cause: %s', str(e))
            raise Exception('FtpTestPoint build_params error, make sure [cache_key, cache_type] is correct')

    # 测试案例的执行
    # 2018.3.12 create by yanan.wu #748921
    # 2018.6.19 edit by xin.guo #869614
    def execute(self, request):
        ftp = None
        try:
            host_port = request[FtpTestPointEnum.address.key].split(':')

            if request[FtpTestPointEnum.server_type.key] == 'sftp':
                sf = paramiko.Transport(host_port[0], int(host_port[1]))
                sf.connect(username=request[FtpTestPointEnum.username.key], password=request[FtpTestPointEnum.password.key])
                sftp = paramiko.SFTPClient.from_transport(sf)
                # sftp下载需要先新建本地文件
                cur_path = os.getcwd()
                file_path = os.path.join(cur_path, '/download' + request[FtpTestPointEnum.req_data.key])
                create_file(file_path)
                sftp.get(request[FtpTestPointEnum.req_data.key], file_path)
                # 读取本地文件
                file_object = open(file_path, 'rb')
                try:
                    file_context = file_object.read()
                finally:
                    file_object.close()
                resp_dict = {'result_value': file_context}
                # 删除文件
                os.remove(file_path)
            elif request[FtpTestPointEnum.server_type.key] == 'ftp':
                ftp = FTP()
                ftp.connect(host_port[0], int(host_port[1]))
                ftp.login(request[FtpTestPointEnum.username.key], request[FtpTestPointEnum.password.key])
                self.file_download = io.BytesIO()
                ftp.retrbinary('RETR %s' % request[FtpTestPointEnum.req_data.key], self.file_download.write)
                resp_dict = {'result_value': self.file_download}
            else:
                logger.exception('FtpTestPoint execute error, cause: %s', 'server_type配置错误')
                raise Exception('FtpTestPoint execute error, cause: ' + 'server_type配置错误')
            self.resp_dict = resp_dict
            return self.resp_dict, ''

        except Exception as e:
            logger.exception('FtpTestPoint execute error, cause: %s', str(e))
            raise Exception('FtpTestPoint execute error, cause: ' + str(e))
        finally:
            if ftp is not None:
                ftp.close()

    # 后处理
    def post_handler(self):
        if self.file_download is not None:
            self.file_download.close()


# SQL配置文件枚举
class FtpTestPointEnum(Conf):
    req_data = 'req_data', '请求参数', False, ''
    address = 'address', 'ip:port', True, ''
    username = 'username', '用户名', True, ''
    password = 'password', '密码', True, ''
    server_type = 'server_type', '服务器类型', True, ''
    expect_data = 'expect_data', '期望返回结果', False, ''
    before_execute = 'before_execute', '插件, 测试点执行前', False, ''
    after_execute = 'after_execute', '插件, 测试点执行后', False, ''


# 建立文件夹
def create_file(file_path):
    file_dir_list = file_path.split('/')
    file_dir = ''
    for i in range(0, len(file_dir_list) - 1):
        file_dir = file_dir + file_dir_list[i] + '/'

    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        fobj = open(file_path, 'w')
        fobj.close()



