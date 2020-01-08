import json
import threading
from copy import copy

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from fishbase import logger

from agbot.agbot_config import agbot_config
from agbot.core.model.context import VerticalContext
from ..base.tp_base import TpBase

_root_conf_name = 'tp_app'


class AppTestPoint(TpBase):
    _semaphore = threading.Semaphore(int(agbot_config.sys_conf_dict[_root_conf_name]['semaphore']))

    def __init__(self, tp_conf, vertical_context: VerticalContext):
        super().__init__(tp_conf, vertical_context)
        self._inspect_results = {}

    def execute(self, request):
        script_file_name = self.tp_conf['script_file_name']
        script_file = next(
            filter(lambda a: a.id.endswith(script_file_name), self.vertical_context.job_context.job_model.attachment),
            None)
        assert script_file is not None, 'can not fond script file {}'.format(script_file_name)
        script_content = script_file.content.decode('utf-8')

        actions = json.loads(script_content)['actions']

        appium_conf = self.vertical_context.sys_conf_dict[_root_conf_name]['appium']
        desired_caps = copy(appium_conf['desired_caps'])
        desired_caps.update(request)

        driver = webdriver.Remote(command_executor=appium_conf['service'],
                                  desired_capabilities=desired_caps)
        driver.implicitly_wait(10)

        try:
            return self._do_execute(driver, actions)
        except BaseException as e:
            logger.exception('AppTestPoint error {}_{}_{}, {}'.format(
                self.vertical_context.task_context.task_model.id,
                self.vertical_context.job_context.job_model.id,
                self.vertical_context.tc_context.tc_detail.id,
                str(e)))
            raise e
        finally:
            driver.close_app()

    def _do_execute(self, driver, actions):
        touch_action = TouchAction(driver)
        for action in actions:
            a = getattr(touch_action, action['action'])
            if action['action'] == 'wait':
                touch_action.wait(action['ms'])
            else:
                el = self._find_element(driver, action)
                a(el)
        if len(actions) > 0:
            touch_action.perform()

        inspect_elements = self.tp_conf.get('inspect_elements')
        if inspect_elements is not None:
            for ie in inspect_elements:
                ele = self._find_element(driver, ie)
                if ele is not None:
                    attr = ele.get_attribute(ie['attr'])
                else:
                    attr = None
                self._inspect_results[ie['alias']] = attr

        return self._inspect_results, ''

    @staticmethod
    def _find_element(driver, el):
        by = el.get('find_by', 'id')
        return driver.find_element(by=by, value=el['target'])
