import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


# webDriverWait 类继承类，为了重写 until 方法
# 2019.4.23 create by xin.guo
class AgWait(WebDriverWait):

    def until(self, method, message=''):
        """重写 WebDriverWait 的 util 方法，将真实错误原因进行返回"""
        last_exception = None

        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if value:
                    return value
            except self._ignored_exceptions as exc:
                last_exception = exc
            time.sleep(self._poll)
            if time.time() > end_time:
                break

        if last_exception:
            raise last_exception
        else:
            raise TimeoutException()
