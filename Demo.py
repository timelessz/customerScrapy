import time
from urllib.parse import urlparse

from scrapy import Selector, selector
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import switch_to
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CustomerscrapyDemo:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    url = 'https://www.made-in-china.com/'
    username = '834916321@qq.com'
    password = '201671zhuang'

    def __init__(self):
        chrome_options = Options()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # 禁用图片的加载
                # 'javascript': 2  # 禁用js，可能会导致通过js加载的互动数抓取失效
            }
        }
        # 添加 crx 拓展
        # chrome_options.add_extension('d:\crx\AdBlock_v2.17.crx')
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(executable_path='D:\chromeDriver\chromedriver.exe',
                                        options=chrome_options)
        self.wait = WebDriverWait(self.browser, 10)

    def process(self):
        self.browser.get('https://sinoder.en.made-in-china.com')
        self.browser.maximize_window()
        ActionChains(self.browser).move_to_element(
            self.browser.find_element_by_xpath("//*[contains(@class,'sr-nav-main')]/li[last()]/a")).click().perform()
        time.sleep(200)
        return
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        sel = Selector(text=html)
        contact_divs = sel.xpath("//*[contains(@class,'contact-info')]/div[contains(@class,'info-item')]")
        address, telephone, phone, contact, dept, position = '', '', '', '', '', ''
        for div in contact_divs:
            label = div.xpath("*[contains(@class,'info-label')]/text()").extract_first()
            text = div.xpath("*[contains(@class,'info-fields')]/text()").extract_first()
            if label == 'Address:':
                address = text
            elif label == 'Telephone:':
                telephone = text
            elif label == 'Mobile Phone:':
                phone = text
        contact_info_divs = sel.xpath(
            "//*[contains(@class,'contact-customer')]/div[contains(@class,'contact-customer-info')]/div[contains(@class,'info-detail')]/div")
        for div in contact_info_divs:
            contact = div.xpath("*[contains(@class,'info-name')]/text()").extract_first()
            dept = div.xpath("*[contains(@class,'info-item')]/text()").extract_first()
            position = div.xpath("*[contains(@class,'info-item')]/text()").extract_first()
        ActionChains(self.browser).move_to_element(
            self.browser.find_element_by_xpath("//a[contains(@class,'link-web')]")).click().perform()
        print(address, telephone, phone, contact, dept, position)
        return

        try:
            self.browser.get(self.url)
            self.browser.maximize_window()
            # self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="s-result-list sg-row"]')))
            self.__login()
            return None
            time.sleep(2)
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)
        return None

    def __login(self):
        # 鼠标滑动到注册页面
        try:
            print(self.browser.find_element_by_link_text("Sign In"))
            ActionChains(self.browser).move_to_element(
                self.browser.find_element_by_link_text("Sign In")).click().perform()
            down_data_click = WebDriverWait(self.browser, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="sign-in-submit"]')))
            element = self.browser.find_element_by_xpath('//*[@id="logonInfo.logUserName"]')
            element.send_keys(self.username)
            element = self.browser.find_element_by_xpath('//*[@id="logonInfo.logPassword"]')
            element.send_keys(self.password)
            time.sleep(2)
            element.send_keys(Keys.ENTER)
            time.sleep(1)
            ActionChains(self.browser).move_to_element(self.browser.find_element_by_xpath(
                '/html/body/div[1]/div[3]/div/div[2]/div[2]/div/ul/li[16]/a')).click().perform()
            # 打开更多分类
            "https://www.made-in-china.com/prod/catlist/"
            html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
            main_handle = self.browser.current_window_handle
            sel = Selector(text=html)
            divs = sel.xpath(
                "/html/body/div[1]/*[contains(@class,'catlist-wrap')]/*[contains(@class,'catlist-content')]/div")
            for div in divs:
                # 获取 type
                type_enname = div.xpath("*[contains(@class,'primary-classify')]/h2/text()").extract_first()
                categories_divs = div.xpath(
                    "*[contains(@class,'primary-classify-content')]/*[contains(@class,'sec-classify-wrap')]/*[contains(@class,'sec-classify')]")
                for cat_div in categories_divs:
                    c = cat_div.xpath('h3/a')
                    href = c.xpath('@href').extract_first()
                    # 获取行业大分类 category
                    text = c.xpath('text()').extract_first()
                    # 点击打开小分类的id 然后获取更多
                    print('%s:%s' % (text, href))
                    time.sleep(2)
                    js = 'window.open("%s")' % (href)
                    self.browser.execute_script(js)
                    time.sleep(1)
                    handles = self.browser.window_handles
                    for i in handles:
                        if i != main_handle:  # 如果句柄不是当前窗口的句柄
                            self.browser.switch_to.window(i)  # 切换窗口
                            # 获取详细的industry数据
                            industryhtml = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
                            i_sel = Selector(text=industryhtml)
                            cate_items = i_sel.xpath("//*[contains(@class,'cate-items')]//a[contains(@class,'item')]")
                            for cate in cate_items:
                                c_href = cate.xpath('@href').extract_first()
                                # 获取行业大分类 category
                                c_text = cate.xpath('h3/text()').extract_first()
                                print('子分类 %s:%s' % (c_text, c_href))
                                break
                            self.browser.close()
                            self.browser.switch_to.window(main_handle)
                            time.sleep(3)
            time.sleep(10)
            return
        except TimeoutException:

            return


def main():
    d = CustomerscrapyDemo()
    d.process()


if __name__ == "__main__":
    main()
