import re

from selenium.common.exceptions import NoSuchElementException


def find_element(driver, target):
    """
    提供找到各种查找元素的方法
    :param driver: 浏览器驱动
    :param target: 选择信息
    :return:
    """
    pattern = '^http.*'
    if target is None or target is '' or re.match(pattern, target):
        return driver
    
    # 以 'id=' 开头的为 id 选择器
    pattern = '^id=.*'
    if re.match(pattern, target):
        return driver.find_element_by_id(target[3:])
    
    # 以 'name=' 开头的为 id 选择器
    pattern = '^name=.*'
    if re.match(pattern, target):
        return driver.find_element_by_name(target[5:])
    
    # 以 'link=' 开头的为 link 选择器
    pattern = '^link=.*'
    if re.match(pattern, target):
        link_text = target[5:]
        # 如果 link 用全量匹配，匹配不到的话，使用部分匹配，经过观察 ff 和 chrome 对同一个链接，html 代码会有不同
        try:
            return driver.find_element_by_link_text(link_text)
        except NoSuchElementException:
            return driver.find_element_by_partial_link_text(link_text)
    
    # 以 'xpath=' 开头的为 xpath 选择器
    pattern = '^xpath=.*'
    if re.match(pattern, target):
        return driver.find_element_by_xpath(target[6:])
    
    # 以 '//' 开头的为 xpath 选择器
    pattern = '^//.*'
    if re.match(pattern, target):
        return driver.find_element_by_xpath(target)
    
    # 以 'css' 开头的为 css 选择器
    pattern = '^css.*'
    if re.match(pattern, target):
        return driver.find_element_by_css_selector(target[4:])
    
    # 以 'class' 开头的为类名选择器
    pattern = '^class.*'
    if re.match(pattern, target):
        # class 的选择器，不能根据多个 class 定位到一个元素，转为使用 css 选择器能达到需求
        target = '.' + target[6:].replace(' ', '.')
        return driver.find_element_by_css_selector(target)

    # 其他的暂时返回 driver 对象
    return driver
