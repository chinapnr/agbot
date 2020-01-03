# @Time    : 2018/7/10  21:16
# @Desc    : 日志检查插件

import os
import re
import threading
import time
import xml.etree.ElementTree
from enum import Enum
from threading import Semaphore

from fishbase.fish_common import splice_url_params
from fishbase.fish_logger import logger
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from agbot.agbot_config import agbot_config
from agbot.core.utils import get_placeholder_value
from agbot.tools.ag_common import hump2underline
from .ag_wait import AgWait
from .selenium_function import SeleniumFunction
from .ui_tools import find_element
from ..base.tp_base import TpBase, TestStatus, Conf, VerticalContext

_root_conf_name = 'tp_ui'
# ui 自动化测试实现主程
# 2018.3.16 create by xin.guo 2018.3.13
class UiTestPoint(TpBase):

    # UI测试的最大同时执行数量
    _semaphore = threading.Semaphore(int(agbot_config.sys_conf_dict[_root_conf_name]['semaphore']))  # type: Semaphore

    # 初始化
    # create by xin.guo 2018.3.13
    def __init__(self, tp_conf, vertical_context: VerticalContext):
        TpBase.__init__(self, tp_conf, vertical_context)
        self.conf_enum = UiTestPointEnum
        self._simple_command_info = {'open': 'get',
                                      'click': 'click',
                                      'setTimeout': 'implicitly_wait',
                                      'submit': 'submit'}
        self._command_list = []
        self._tc_params_dict = None  # type: TcContext
        # execute 方法是否正常执行标识
        self._execute_flag = True
        self.vertical_context = vertical_context

    # 数据准备
    # create by xin.guo 2018.3.13
    # 2018.5.22 edit by yang.xu #848884
    def build_request(self):
        tc_params_dict = self.vertical_context.tc_context
        self._tc_params_dict = tc_params_dict
        script_name = self.tp_conf.get(UiTestPointEnum.script_file_path.key,
                                       self.tp_conf.get(UiTestPointEnum.script.key))
        script_name = script_name.split('/')[-1]
        xml_script = next(
            filter(lambda a: a.id.endswith(script_name), self.vertical_context.job_context.job_model.attachment), None)
        assert xml_script is not None, 'can not fond xml script {}'.format(script_name)
        xml_script_content_raw = xml_script.content.decode('utf-8')

        try:
            xml_script_content, replacement = get_placeholder_value(xml_script_content_raw, self.vertical_context)
            self.__extend_tp_replacement(replacement)

            # 获取命令列表
            self._command_list = self._get_command_list(xml_script_content)

            target_url = ''
            for command in self._command_list:

                # 请求参数作用于 open 函数的目标
                if command['command'] == 'open':
                    target_url = self._get_command_param(command['target'])
                    logger.info("ui 原始请求地址为 :{}".format(target_url))
                    # 组装页面地址
                    if UiTestPointEnum.req_data.key in self.tp_conf and self.tp_conf[UiTestPointEnum.req_data.key]:
                        TpBase.build_request(self)
                        target_url = target_url + splice_url_params(self.req_param)
                        logger.info("ui 请求地址，拼接参数后为 :{}".format(target_url))
                        flag = self._set_command_param(command['target'], target_url)
                        if not flag:
                            command['target'] = target_url
                    break
        except Exception as e:
            logger.exception('ui 测试脚本: %s ,没有找到或者解析失败', str(self.tp_conf))
            raise RuntimeError('ui 测试脚本:' + str(self.tp_conf) + ',没有找到或者解析失败')
        return {'url': target_url}

    # 执行
    # create by xin.guo 2018.3.13
    def execute(self, request):
        # 开始逐条执行命令, 捕获并输出异常, 有异常即认为该案例失败
        semaphore_acquired = False
        try:
            logger.info('ui waiting: {}'.format(self._semaphore._value))
            semaphore_acquired = self._semaphore.acquire()
            logger.info('ui executing: {}'.format(self._semaphore._value))
            # 加载浏览器驱动
            self._load_driver(self.tp_conf[UiTestPointEnum.browser_type.key], request)

            # 增加命令计数器，进行计数
            command_num = 0

            for command in self._command_list:
                command_num += 1
                try:
                    execute_result = AgWait(self._driver, 10, ignored_exceptions=Exception).until(
                        lambda x: self.__execute_command(command['command'],
                                                         self._get_command_param(
                                                             command['target']),
                                                         self._get_command_param(command['value'])))

                    # 2019.5.20 修改所有环境 ui 测试都等待时间
                    # local 环境下，每执行一个指令就等待 1s
                    time.sleep(1)
                    # 当最后一条执行的时候，等待 2s
                    if command_num == len(self._command_list):
                        time.sleep(2)

                    if not execute_result:
                        logger.info('ui 测试命令执行失败: 第' + str(command_num) + '条命令, command=' +
                                    command['command'] + ',target=' + command['target'] + ',value=' + command['value'])
                        self._execute_flag = False
                        raise RuntimeError('ui 测试命令执行失败: 第' + str(command_num) + '条命令, command=' +
                                           command['command'] + ',target=' + command['target'] + ',value=' +
                                           command['value'])
                except NoSuchElementException as e:
                    logger.exception('第' + str(command_num) + '条命令, ui 测试命令: %s ,没有找到指定页面元素', str(command))
                    self._execute_flag = False
                    raise RuntimeError('第' + str(command_num) +
                                       '条命令, ui 测试命令:' + str(command) + ',没有找到指定页面元素')
                except NoAlertPresentException as e:
                    logger.exception('第' + str(command_num) +
                                     '条命令, ui 测试命令: %s ,没有 alert 弹框, 建议脚本中添加等待时间',
                                     command['command'])
                    self._execute_flag = False
                    raise RuntimeError('第' + str(command_num) +
                                       '条命令, ui 测试命令:' + str(command) + ',没有 alert 弹框, 建议脚本中添加等待时间')
                except Exception as e:
                    logger.exception('第' + str(command_num) + '条命令, ui 测试命令: %s ,执行异常', str(command))
                    self._execute_flag = False
                    raise RuntimeError('第' + str(command_num) + '条命令, ui 测试命令:' + str(command) + ',执行异常')
                finally:
                    if not self._execute_flag:
                        shot_path = os.path.join(agbot_config.basedir, 'log/screenshot')
                        if not os.path.exists(shot_path):
                            os.makedirs(shot_path)
                        self._driver.save_screenshot(os.path.join(shot_path, '{}_{}_{}_{}.png'.format(
                            self.vertical_context.task_context.task_model.id,
                            self.vertical_context.job_context.job_model.id,
                            self.vertical_context.tc_context.tc_detail.id,
                            self.vertical_context.tc_context.current_tp_context.id
                        )))

            return {'execute_flag': self._execute_flag}, ''
        finally:
            try:
                # time.sleep(120)
                # 关闭页面, 释放对象
                # 本地环境，出现错误时，不退出
                if not self._execute_flag and self.vertical_context.sys_conf_dict[_root_conf_name][
                    'quit_on_error'] == 'false':
                    pass
                else:
                    self._driver.quit()
            finally:
                if semaphore_acquired:
                    self._semaphore.release()
                    logger.info('ui exit: {}'.format(self._semaphore._value))

    # 结果比对
    # create by xin.guo 2018.3.13
    def test_status(self):
        tc_ctx = self.vertical_context.tc_context
        if tc_ctx.current_tp_context.response.content['execute_flag']:
            return TestStatus.PASSED
        else:
            return TestStatus.NOT_PASSED

    # 获取浏览器驱动
    # create by xin.guo 2018.3.13
    # edited by xin.guo 2018.11.22 改为只使用无界面模式的 chrome
    # edited by yang.xu 2018.12.04 chrome静默模式
    # edited by jun.hu 2019.3.13 修改获取 driver 的路径
    # edited by jun.hu 2019.5.7 新加判断不同的操作系统使用不同的 driver
    def _load_driver(self, driver_type, req_param):
        # 之后驱动包应打入 docker 镜像, 不应再放置在工程目录下
        # 只使用 Chrome 无浏览器模式
        # local 环境下使用与 .exe 同一目录下的 /web_driver/chromedriver.exe
        if driver_type == BrowserType.FIREFOX.value:
            driver_name = 'geckodriver'
            option = webdriver.FirefoxOptions()
        else:
            # 默认是 chrome
            option = webdriver.ChromeOptions()
            driver_name = 'chromedriver'

        driver_path = None
        driver_dir = self.vertical_context.sys_conf_dict[_root_conf_name]['driver_dir']
        for root, dirs, files in os.walk(driver_dir):
            for file in files:
                if file.startswith(driver_name):
                    driver_path = os.path.join(root, file)
                    break

        assert driver_path is not None, 'unsupported browser: {}'.format(driver_type)

        logger.info('驱动文件路径为: {}'.format(driver_path))

        is_silent_mode = self.vertical_context.sys_conf_dict[_root_conf_name]['silent_mode'] == 'true'
        if is_silent_mode:
            # 静默模式
            option.add_argument('--disable-gpu')
            option.add_argument('--headless')
            option.add_argument('--no-sandbox')

        # 使用代理
        if self.tp_conf.get(UiTestPointEnum.proxy_server.key):
            # http://10.153.201.20:8443
            proxy_server = self.tp_conf.get(UiTestPointEnum.proxy_server.key)
            logger.info('ui 测试 添加代理 {}'.format(proxy_server))
            try:
                if driver_type == BrowserType.FIREFOX.value:
                    option.set_preference('network.proxy.type', 1)
                    # IP为你的代理服务器地址:如 ‘127.0.0.0’，字符串类型
                    ip = ':'.join(proxy_server.split(':')[:-1])
                    option.set_preference('network.proxy.http', ip)
                    port = int(proxy_server.split(':')[-1])
                    option.set_preference('network.proxy.http_port', port)
                else:
                    option.add_argument("--proxy-server=" + proxy_server)
            except Exception as ex:
                logger.exception('添加代理错误：{}'.format(ex))
                raise Exception(ex)

        try:
            # firefox
            if driver_type == BrowserType.FIREFOX.value:
                profile = webdriver.FirefoxProfile()
                # 使用手机模式打开
                if self.tp_conf.get(UiTestPointEnum.device_name.key):
                    device_name = self.tp_conf.get(UiTestPointEnum.device_name.key)
                    if device_name.lower().startswith('iphone'):
                        user_agent = ("Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) "
                                      "AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16")
                    else:
                        user_agent = ("Firefox 28/Android: Mozilla/5.0 (Android; Mobile; rv:28.0) "
                                      "Gecko/24.0 Firefox/28.0")
                    profile.set_preference("general.useragent.override", user_agent)

                # firefox 禁用缓存
                profile.set_preference("browser.cache.disk.enable", False)
                profile.set_preference("browser.cache.memory.enable", False)
                profile.set_preference("browser.cache.offline.enable", False)

                self._driver = webdriver.Firefox(executable_path=driver_path,
                                                 firefox_profile=profile,
                                                 firefox_options=option)
            else:
                # chrome 限制缓存
                option.add_argument('--disable-dev-shm-usage')
                if self.tp_conf.get(UiTestPointEnum.device_name.key):
                    # 使用手机模式打开
                    mobileEmulation = {'deviceName': self.tp_conf.get(UiTestPointEnum.device_name.key)}
                    option.add_experimental_option('mobileEmulation', mobileEmulation)
                self._driver = webdriver.Chrome(executable_path=driver_path, chrome_options=option)
        except Exception as ex:
            logger.exception(ex)
            raise Exception(ex)

        window_size = self.vertical_context.sys_conf_dict[_root_conf_name].get('window_size')
        if window_size:
            # 设定窗口尺寸以使截图范围更大
            window_size_tuple = window_size.split(',')
            self._driver.set_window_size(int(window_size_tuple[0]), int(window_size_tuple[1]))
        else:
            self._driver.maximize_window()

        # firefox + 手机模式 需要调整窗口大小
        # if driver_type == BrowserType.FIREFOX.value and self.tp_conf.get(UiTestPointEnum.device_name.key):
        #     self._driver.set_window_size(360, 640)

    # 执行单条命令
    # create by xin.guo 2018.3.13
    def __execute_command(self, command, target, exec_param):
        # 1. 获取页面元素对象
        exec_element = find_element(self._driver, target)

        # 2. 判断是简单命令还是特殊命令
        # 映射方法分两种, 简单方法(有现成对应命令)和需要特殊处理的方法
        # 如果是简单方法, 则将 ide 生成脚本的命令映射为 webdriver 的执行命令
        # 其他方法调用对应特殊方法
        if command in self._simple_command_info:
            # 简单命令
            return self.__execute_simple_command(exec_element, command, target,
                                                 exec_param)
        elif command is not None:
            exec_func = getattr(SeleniumFunction(self._driver), "execute_" + hump2underline(command))
            param_builder_dict = {'exec_element': exec_element, 'command': command,
                                  'target': target, 'exec_param': exec_param}
            return exec_func(**param_builder_dict)

        return False

    # 解析 xml 生成任务列表
    # create by xin.guo 2018.3.13
    def _get_command_list(self, file_content):
        command_list = []

        # 一个 selenese 代表一条命令
        root = xml.etree.ElementTree.fromstring(file_content)
        seleneses = root.findall('selenese')

        # 解析 selenese 列表, 生成执行列表
        for selenese in seleneses:
            command = {}
            if selenese.find('command') is not None:
                command['command'] = selenese.find('command').text
            if selenese.find('target') is not None:
                command['target'] = selenese.find('target').text
            if selenese.find('value') is not None:
                command['value'] = selenese.find('value').text

            command_list.append(command)

        return command_list

    # 执行简单命令
    # create by xin.guo 2018.3.13
    def __execute_simple_command(self, exec_element, command, target, exec_param):
        # 1. 将 ide 生成脚本的命令映射为 webdriver 的执行命令
        exec_command = self._simple_command_info[command]

        # 2. 执行
        func = getattr(exec_element, exec_command)
        if isinstance(exec_element, RemoteWebDriver):
            func(target)
        elif exec_param and exec_param is not '':
            func(exec_param)
        else:
            func()

        # 3. 等待一段时间
        time.sleep(1)

        return True

    # 注入参数
    # create by xin.guo 2018.3.13
    def _get_command_param(self, param):
        return param

    # edit by jun.hu 2019.6.6
    # 填充 tp 中的占位符
    def __extend_tp_replacement(self, replacement):
        # 获取当前的 tp_id
        self.vertical_context.tc_context.current_tp_context.replacement.extend(replacement)

    # 设定参数
    # create by xin.guo 2018.3.13
    def _set_command_param(self, param, value):
        if param is None:
            return False

        # 如果是 ${XXXX} 形式的参数, 则使用用外部参数替换
        pattern = '^\$\{.*\}$'
        if re.match(pattern, param):
            param_name = param[2:-1]
            tc_data_dict = self._tc_params_dict.tc_detail.data
            tc_data_dict[param_name] = value
            return True
        else:
            return False


# BrowserType 浏览器类型常量
# 2018.4.13 create by yanan.wu #806640
class BrowserType(Enum):
    CHROME = '01'
    FIREFOX = '02'
    IE = '03'


# ui 配置文件枚举
class UiTestPointEnum(Conf):
    browser_type = 'browser_type', '浏览器类型', False, ''
    script_file_path = 'script_file_path', 'ui 脚本名', False, ''
    script = 'script', '脚本id', False, ''
    req_data = 'req_data', '请求参数', False, ''
    proxy_server = 'proxy_server', '代理服务器', False, ''
    device_name = 'device_name', '请求设备', False, ''
