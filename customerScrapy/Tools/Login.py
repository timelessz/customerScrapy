import time

from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Login:
    login_url = 'https://login.made-in-china.com/sign-in/?baseNextPage=https%3A%2F%2Fwww.made-in-china.com%2F'

    def get_cookies(self):
        chrome_options = Options()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # 禁用图片的加载
                'javascript': 2,  # 禁用js，可能会导致通过js加载的互动数抓取失效
                'stylesheet': 2
            }
        }
        settings = get_project_settings()
        # 添加 crx 拓展
        # chrome_options.add_extension('d:\crx\AdBlock_v2.17.crx')
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(
            executable_path=settings.get('CHROME_OPTIONS_BINARY_LOCATION'),
            chrome_options=chrome_options)
        time.sleep(3)
        self.browser.get(self.login_url)
        self.browser.maximize_window()
        down_data_click = WebDriverWait(self.browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sign-in-submit"]')))
        element = self.browser.find_element_by_xpath('//*[@id="logonInfo.logUserName"]')
        element.send_keys(settings.get('LOGIN_USERNAME'))
        element = self.browser.find_element_by_xpath('//*[@id="logonInfo.logPassword"]')
        time.sleep(1)
        element.send_keys(settings.get('LOGIN_PASSWORD'))
        time.sleep(2)
        element.send_keys(Keys.ENTER)
        time.sleep(2)
        # 登录成功后获取cookie
        if "Made-in-China.com" in self.browser.title:
            cookies = self.browser.get_cookies()
            self.browser.quit()
            return cookies
        else:
            print("登录失败！")
            self.browser.quit()
            return False
