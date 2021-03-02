from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class chromeBrower:
    ''' 浏览器 '''

    def __init__(self):
        chrome_options = Options()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # 禁用图片的加载
                # 'javascript': 2,  # 禁用js，可能会导致通过js加载的互动数抓取失效
            }
        }
        settings = get_project_settings()
        # 添加 crx 拓展
        # chrome_options.add_extension('d:\crx\AdBlock_v2.17.crx')
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(
            executable_path=settings.get('CHROME_OPTIONS_BINARY_LOCATION'),
            chrome_options=chrome_options
        )

    def get_brower(self):
        return self.browser
