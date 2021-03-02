import time

from parsel import Selector
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains

from customerScrapy.Tools.chromeBrower import chromeBrower
from customerScrapy.dborm import getsession


class parseCustomer:

    def __init__(self, login_cookies):
        self.DBSession = getsession()
        self.browser = chromeBrower().get_brower()
        self.browser.get('https://made-in-china.com/')
        self.main_handle = self.browser.current_window_handle
        self.browser.maximize_window()
        for cookie in login_cookies:
            self.browser.add_cookie(cookie)

    ''' 解析客户信息 '''

    def parse_customer_info(self, customers):
        for customer in customers:
            # 新开一个窗口，通过执行js来新开一个窗口
            js = 'window.open("%s");' % customer.showroom
            self.browser.execute_script(js)
            time.sleep(1)
        handles = self.browser.window_handles
        main_customer_info = []
        # 跳转到客户信息页面
        for handle in handles:
            if self.main_handle != handle:
                self.browser.switch_to.window(handle)
                if self.__check_is_element_exist('Contact Us'):
                    # 跳转到联系我们页面
                    ActionChains(self.browser).move_to_element(
                        self.browser.find_element_by_xpath(
                            "//*[contains(@class,'sr-nav-main')]/li[last()]/a")).click().perform()
                else:
                    # 不包含 Contact us 的

                    pass
                time.sleep(2)
        customer_handles = self.browser.window_handles
        # 跳转到客户信息页面
        for handle in handles:
            if self.main_handle != handle:
                self.browser.switch_to.window(handle)
                if self.__check_is_element_exist('Click Here'):
                    try:
                        ActionChains(self.browser).move_to_element(
                            self.browser.find_element_by_xpath(
                                "//*[@class='contact-info']/div[last()]/*[@class='info-fields']/a[@class='link-web']")).click().perform()
                    except NoSuchElementException as e:
                        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                        print(self.browser.title + '没有网站等点击元素')
                        print('网址为：' + self.browser.current_url)
                        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    print(self.browser.window_handles)
                    for phandle in handles:
                        if self.main_handle != phandle and phandle not in customer_handles:
                            pass
                    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                else:
                    pass
        time.sleep(5000)
        #     handles = self.browser.window_handles
        #     # 跳转到客户联系信息页面
        #     for handle in handles:
        #         if self.main_handle != handle:
        #             self.customer_handle = handle
        #             self.browser.switch_to.window(handle)
        #     time.sleep(5)
        #     self.__get_customer_info()
        #     print(True)
        # else:
        #     print(False)

    '''验证元素是否存在'''

    def __check_is_element_exist(self, element):
        flag = True
        try:
            self.browser.find_elements_by_link_text(element)
            return flag
        except:
            flag = False
            return flag

    ''' 获取客户网站 '''

    def __get_customer_website(self):
        # 表示有网站
        website, title = '', ''
        if self.__check_is_element_exist('Click Here'):
            ActionChains(self.browser).move_to_element(
                self.browser.find_element_by_xpath(
                    "//*[@class='contact-info']/div[last()]/*[@class='info-fields']/a")).click().perform()
            handles = self.browser.window_handles
            for handle in handles:
                if handle != self.main_handle:
                    self.browser.switch_to.window(handle)
                    website = self.browser.current_url
                    title = self.browser.title
                    self.browser.close()

            # self.browser.switch_to.window(self.customer_handle)
        return {'website': website, 'tit'
                                    'le': title}

    '''解析页面获取 customer 信息'''

    def __get_customer_info(self):
        # 跳转到
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        website_info = self.__get_customer_website()
        website, title = website_info['website'], website_info['title']
        sel = Selector(text=html)
        contact_divs = sel.xpath("//*[contains(@class,'contact-info')]/*[contains(@class,'info-item')]")
        address, telephone, phone, contact, dept, position = '', '', '', '', '', ''
        for div in contact_divs:
            label = div.xpath("*[contains(@class,'info-label')]/text()").extract_first()
            text = div.xpath("*[contains(@class,'info-fields')]/text()").extract_first()
            if text:
                text = text.strip()
            if title:
                title = title.strip()
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
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(website)
        print(title)
        print(address, telephone, phone, contact, dept, position, website, title)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        self.browser.close()
        self.browser.switch_to.window(self.main_handle)
