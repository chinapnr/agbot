# @Time    : 2018/6/09  16:01
# @Desc      : selenium函数实现

import json
import re
import time

from fishbase.fish_logger import logger
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.support.ui import Select

from tp.ui.ui_tools import find_element


class SeleniumFunction(object):
    def __init__(self, driver):
        self.driver = driver  # type: webdriver.Chrome

    # 执行 waitForAlert
    # create by xin.guo 2018.3.22
    def execute_wait_for_alert(self, **kwargs):
        target = kwargs['target']
        for i in range(60):
            try:
                return self.execute_assert_not_visible(target)
            except Exception:
                pass
            time.sleep(1)
        else:
            return False

    # 执行 assertNotVisible
    # create by xin.guo 2018.3.22
    def execute_assert_not_visible(self, target):
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        if target is not None and target is not '' and target != alert_text:
            return False
        alert.accept()
        return True

    # 执行 type
    # create by xin.guo 2018.11.22
    def execute_type(self, **kwargs):
        exec_element = kwargs['exec_element']
        exec_param = kwargs['exec_param']

        exec_element.clear()
        exec_element.send_keys(exec_param)
        return True

    # 执行 select
    # create by xin.guo 2018.3.22
    def execute_select(self, **kwargs):
        exec_element = kwargs['exec_element']
        exec_param = kwargs['exec_param']
        exec_param = exec_param[6:]
        Select(exec_element).select_by_visible_text(exec_param)
        return True

    # 执行 selectFrame
    # create by xin.guo 2018.3.22
    def execute_select_frame(self, **kwargs):
        target = kwargs['target']
        # 用 index 定位
        pattern = '^index=.*'
        if re.match(pattern, target):
            self.driver.switch_to.frame(int(target[6:]))
            return True

        # 定位到父 iFrame
        if target == 'relative=parent':
            self.driver.switch_to.parent_frame()
            return True

        return False

    # 执行 doubleClick
    # create by xin.guo 2018.3.22
    def execute_double_click(self, **kwargs):
        exec_element = kwargs['exec_element']
        ActionChains(self.driver).double_click(exec_element).perform()
        return True

    # 执行 mobileTap
    # create by jun.hu 2018.5.22
    def execute_mobile_tap(self, **kwargs):
        exec_element = kwargs['exec_element']
        TouchActions(self.driver).tap(exec_element).perform()
        return True

    # 执行 pause
    # create by yang.xu 2018.6.13
    def execute_pause(self, **kwargs):
        target = kwargs['target']
        if target:
            time.sleep(int(target))
        else:
            exec_param = kwargs['exec_param']
            time.sleep(int(exec_param))

        return True

    # 执行 click_and_hold
    # create by yanan.wu 2018.6.7
    def execute_click_and_hold(self, **kwargs):
        exec_element = kwargs['exec_element']
        ActionChains(self.driver).click_and_hold(exec_element).perform()
        return True

    # 执行 drag_and_drop_by_offset
    # create by yanan.wu 2018.6.7
    def execute_drag_and_drop(self, **kwargs):
        exec_element = kwargs['exec_element']
        exec_param = kwargs['exec_param']
        try:
            exec_param_list = exec_param.split(',')
            ActionChains(self.driver).drag_and_drop_by_offset(
                exec_element, int(exec_param_list[0]),
                int(exec_param_list[1])).perform()
        except UnexpectedAlertPresentException:
            logger.error('drag error')
            return False
        return True

    # 执行 assert_text
    # create by xin.guo 2018.9.5
    def execute_assert_text(self, **kwargs):
        exec_element = kwargs['exec_element']
        exec_param = kwargs['exec_param']
        try:
            logger.info('assert_text:预测值:%s, 实际值:%s', exec_param, exec_element.text)
            if exec_param == exec_element.text:
                return True
            return False
        except Exception:
            logger.error('assert_text error')
            return False

    # 执行 delete_cookie_named
    # create by xin.guo 2018.9.5
    def execute_delete_cookie_named(self, **kwargs):
        exec_param = kwargs['exec_param']
        try:
            # 删除某个 cookie
            self.driver.delete_cookie(exec_param)
            return True
        except Exception:
            logger.error('delete_cookie_named error')
            return False

    # 执行 delete_all_cookies
    # create by xin.guo 2018.9.5
    def execute_delete_all_cookies(self, **kwargs):
        try:
            # 删除所有 cookie
            self.driver.delete_all_cookies()
            return True
        except Exception:
            logger.error('delete_all_cookies error')
            return False

    # 执行 refresh
    # create by xin.guo 2018.9.5
    def execute_refresh(self, **kwargs):
        try:
            self.driver.refresh()
            return True
        except Exception:
            logger.error('refresh error')
            return False

    # 执行 assert_attribute
    # create by xin.guo 2018.12.25
    def execute_assert_attribute(self, **kwargs):
        exec_element = kwargs['exec_element']
        exec_param = kwargs['exec_param']
        try:
            if exec_param == exec_element.get_attribute:
                return True
            return False
        except Exception:
            logger.error('assert_text error')
            return False

    # 执行 switch_to 后一个窗口
    # create by jun.hu 2018.5.20
    def execute_switch_to_window(self, **kwargs):
        try:
            # target 指向 window 的序号 默认为1
            handle_index = 1 if not kwargs.get('target') else int(kwargs.get('target'))
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[handle_index])
            return True
        except Exception as _:
            logger.error('switch_to windows error')
            return False

    # 执行 assert_as_json
    # create by xin.guo 2019.5.24
    def execute_assert_as_json(self, **kwargs):
        exec_element = kwargs['exec_element']
        exec_param = kwargs['exec_param']

        # 默认 text 内容为 json 格式，将 text 读做 dict
        # 根据 param 中表达式进行断言，只断言 '=' 的场景，并且表达式以 ',' 分割
        try:
            text_dict = json.loads(exec_element.text)
            logger.info('ui 测试 assert_as_json 实际执行结果为 {}'.format(text_dict))
            for assert_expression in exec_param.split(','):
                key, expected_value = assert_expression.split('=')
                if text_dict[key] == expected_value:
                    continue
                else:
                    return False

            return True
        except Exception:
            logger.error('assert_as_json error')
            return False

    # 执行 moveToElementClick 解决 hover 的问题
    # create by jun.hu 2019.6.25
    def execute_move_to_element_click(self, **kwargs):
        try:
            exec_element = kwargs['exec_element']
            # 滑动的元素
            exec_param = kwargs['exec_param']
            # 需要根据 exec_param 找到 hover 所在层
            hover_element = find_element(self.driver, exec_param)
            if not hover_element:
                return False
            # 向下滑动
            ActionChains(self.driver).move_to_element(hover_element).click(exec_element).perform()
            return True
        except Exception as ex:
            logger.exception(ex)
            return False
