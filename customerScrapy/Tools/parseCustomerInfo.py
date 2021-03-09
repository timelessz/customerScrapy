import time
from builtins import len

from parsel import Selector
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains, DesiredCapabilities

from customerScrapy.Model import Customer
from customerScrapy.Tools.chromeBrower import chromeBrower
from customerScrapy.dborm import getsession


class parseCustomer:

    def __init__(self, login_cookies):
        # get直接返回，不再等待界面加载完成
        self.DBSession = getsession()
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"
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
            time.sleep(5)
        handles = self.browser.window_handles
        # 跳转到客户信息页面
        for handle in handles:
            if self.main_handle != handle:
                self.browser.switch_to.window(handle)
                if self.__check_is_element_exist('Contact Us'):
                    # 跳转到联系我们页面
                    ActionChains(self.browser).move_to_element(
                        self.browser.find_element_by_link_text("Contact Us")).click().perform()
                if self.__check_is_element_exist('Contact'):
                    # 跳转到联系我们页面
                    ActionChains(self.browser).move_to_element(
                        self.browser.find_element_by_link_text("Contact")).click().perform()
            time.sleep(5)
        handles = self.browser.window_handles
        customer_handles = self.browser.window_handles
        # 跳转到客户信息页面
        for handle in handles:
            if self.main_handle == handle:
                continue
            self.browser.switch_to.window(handle)
            # 包含点击操作的
            if self.__check_is_element_exist('Contact Us'):
                company_info = self.__get_customer_info()
                if not company_info:
                    continue
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                print('获取的pro公司信息')
                print(company_info)
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            elif self.__check_is_element_exist('Contact'):
                # 金牌会员操作
                company_info = self.__get_gold_customer_info()
                if not company_info:
                    continue
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                print('获取的pro公司信息')
                print(company_info)
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            else:
                # 不包含 Contact us 的 直接获取联系方式保存
                company_info = self.__get_notpro_customer_info()
                if not company_info:
                    continue
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                print('获取的非 pro公司信息')
                print(company_info)
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            # 包含 Contact US 的页面
            website, title = '', ''
            if self.__check_is_element_exist('Click Here'):
                try:
                    # 分析客户信息保存下来
                    # ActionChains(self.browser).move_to_element(
                    #     self.browser.find_element_by_xpath(
                    #         "//*[@class='contact-info']/div[last()]/*[@class='info-fields']/a[@class='link-web']")).click().perform()
                    ActionChains(self.browser).move_to_element(
                        self.browser.find_element_by_link_text('Click Here')).click().perform()
                    # 求差集
                    time.sleep(5)
                    new_handles = list(set(self.browser.window_handles).difference(set(customer_handles)))
                    if len(new_handles) == 1:
                        self.browser.switch_to.window(new_handles[0])
                        website = self.browser.current_url
                        customer_handles.append(new_handles[0])
                        title = self.browser.title
                        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                        print(website)
                        print(title)
                        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                except NoSuchElementException as e:
                    break
            company_info['website'] = website
            company_info['title'] = title
            print(company_info)
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('最终需要保存的信息')
            print(company_info)
            customer = self.DBSession.query(Customer).filter(Customer.en_name == company_info['en_name']).first()
            if customer:
                customer.website, customer.website_title, customer.address, customer.telephone, customer.mobile, customer.contact, customer.dept, customer.position = \
                    company_info['website'], company_info['title'], company_info['address'], company_info['telephone'], \
                    company_info['phone'], company_info['contact'], \
                    company_info['dept'], company_info['position']
                self.DBSession.commit()
                print('保存成功')
            else:
                print('保存失敗')
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        handles = self.browser.window_handles
        for c_handle in handles:
            if self.main_handle == c_handle:
                continue
            self.browser.switch_to.window(c_handle)
            self.browser.close()
        self.browser.switch_to.window(self.main_handle)
        time.sleep(5)

    '''获取非madeinchina 微网站元素'''

    def __get_notpro_customer_info(self):
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        sel = Selector(text=html)
        com_name = sel.xpath("//*[contains(@class,'com-name-txt')]/descendant::h1/text()").extract_first()
        if not com_name:
            return None
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(self.browser.current_url)
        print(com_name + '不存在联系我们的页面')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        contact_divs = sel.xpath("//*[contains(@class,'info-cont-wp')]/*[contains(@class,'item')]")
        address, telephone, phone, contact, dept, position = '', '', '', '', '', ''
        for div in contact_divs:
            label = div.xpath("*[contains(@class,'label')]/text()").extract_first()
            text = div.xpath("*[contains(@class,'info')]/text()").extract_first()
            if text:
                text = text.strip()
            if label:
                label = label.strip()
            if label == 'Address:':
                address = text
            elif label == 'Telephone:':
                telephone = text
        contact = sel.xpath(
            "//*[contains(@class,'person')]/div[contains(@class,'txt')]/*[contains(@class,'name')]/text()").extract_first()
        dept_position = sel.xpath(
            "//*[contains(@class,'person')]/div[contains(@class,'txt')]/*[contains(@class,'manager')]")
        if dept_position and len(dept_position) == 2:
            position = dept_position[0].xpath('text()').extract_first()
            dept = dept_position[1].xpath('text()').extract_first()
        if dept:
            dept = dept.strip()
        if position:
            position = position.strip()
        return {'address': address, 'telephone': telephone, 'phone': phone, 'contact': contact, 'dept': dept,
                'position': position, 'en_name': com_name.strip()}

    '''验证元素是否存在'''

    def __check_is_element_exist(self, element):
        try:
            if self.browser.find_elements_by_link_text(element):
                return True
            else:
                return False
        except:
            return False

    '''解析开启微官网的获取 customer 信息'''

    def __get_customer_info(self):
        # 跳转到
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        sel = Selector(text=html)
        com_name = sel.xpath("//*[contains(@class,'title-txt')]/a/h1/text()").extract_first()
        if com_name:
            com_name = com_name.strip()
        else:
            return None
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(self.browser.current_url)
        print(com_name + '存在联系我们的页面')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        contact_divs = sel.xpath("//*[contains(@class,'contact-info')]/*[contains(@class,'info-item')]")
        address, telephone, phone, contact, dept, position = '', '', '', '', '', ''
        address = sel.xpath('//*[contains(@class,"contact-address")]/text()').extract_first()
        if address:
            address = address.strip()
        for div in contact_divs:
            label = div.xpath("*[contains(@class,'info-label')]/text()").extract_first()
            text = div.xpath("*[contains(@class,'info-fields')]/text()").extract_first()
            if text:
                text = text.strip()
            if label:
                label = label.strip()
            if label == 'Telephone:':
                telephone = text
            elif label == 'Mobile Phone:':
                phone = text
        contact = sel.xpath("//*[contains(@class,'info-name')]/text()").extract_first()
        contact_info_divs = sel.xpath(
            "//*[contains(@class,'contact-customer')]/div[contains(@class,'contact-customer-info')]/div[contains(@class,'info-detail')]/div[contains(@class,'info-item')]")
        if contact_info_divs and len(contact_info_divs) == 2:
            dept = contact_info_divs[0].xpath("text()").extract_first()
            position = contact_info_divs[1].xpath("text()").extract_first()
        if dept:
            dept = dept.strip()
        if position:
            position = position.strip()
        return {'address': address, 'telephone': telephone, 'phone': phone, 'contact': contact, 'dept': dept,
                'position': position, 'en_name': com_name}

    def __get_gold_customer_info(self):
        # 跳转到
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        sel = Selector(text=html)
        com_name = sel.xpath(
            "//*[contains(@class,'contact-info')]/*[contains(@class,'other-info')]/div[1]/span/text()").extract_first()
        if com_name:
            com_name = com_name.strip()
        else:
            return None
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(self.browser.current_url)
        print(com_name + '存在联系我们的页面')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        address, telephone, phone, contact, dept, position = '', '', '', '', '', ''
        address = sel.xpath('//*[contains(@class,"com-address")]/text()').extract_first()
        if address:
            address = address.strip()
        contact_divs = sel.xpath("//*[contains(@class,'contact-info')]/*[contains(@class,'other-info')]/div")
        for div in contact_divs:
            label = div.xpath("span[contains(@class,'th')]/@title").extract_first()
            text = div.xpath("span[contains(@class,'td')]/text()").extract_first()
            if text:
                text = text.strip()
            if label:
                label = label.strip()
            if label and label == 'Telephone':
                telephone = text
            elif label == 'Mobile Phone':
                phone = text
        contact = sel.xpath(
            "//*[contains(@class,'contact-info')]/*[contains(@class,'main-info')]/*[contains(@class,'cnt')]/*[contains(@class,'info-person')]/text()").extract_first()
        contact_info_divs = sel.xpath(
            "//*[contains(@class,'contact-info')]/*[contains(@class,'main-info')]/*[contains(@class,'cnt')]/*[not(contains(@class,'info-person'))]")
        if contact_info_divs:
            dept = contact_info_divs[0].xpath("text()").extract_first()
            position = contact_info_divs[1].xpath("text()").extract_first()
        if contact:
            contact = contact.strip()
        if dept:
            dept = dept.strip()
        if position:
            position = position.strip()
        return {'address': address, 'telephone': telephone, 'phone': phone, 'contact': contact, 'dept': dept,
                'position': position, 'en_name': com_name}
