import time
from urllib.parse import urlparse

from parsel import Selector

from customerScrapy.Tools.chromeBrower import chromeBrower
from customerScrapy.dborm import getsession


class parseCustomer:

    def __init__(self, customer, login_cookies):
        self.DBSession = getsession()
        self.browser = chromeBrower().get_brower()
        self.browser.get('https://made-in-china.com/')
        self.browser.maximize_window()
        for cookie in login_cookies:
            self.browser.add_cookie(cookie)
        self.browser.get('https:' + customer.showroom)
        time.sleep(10)


    ''' 生成每个公司页面的url '''

    def yield_company_url(self):
        # 更新数据
        xpath = "//div[contains(@class,'list-node ')]"
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        sel = Selector(text=html)
        divs = sel.xpath(xpath)
        for node in divs:
            baseXpath = "*[contains(@class,'list-node-content')]/*[contains(@class,'pro-extra')]/*[contains(@class,'company-info')]/"
            axpath = "*[contains(@class,'compnay-name-li')]/a"
            a = node.xpath(baseXpath + axpath)
            if a:
                # 在线直接能访问的
                href = a.xpath('@href').extract_first()
                print(href)
                url = urlparse('https:' + href)
                href = 'https://' + url.netloc
                title = a.xpath('@title').extract_first()
                if not title:
                    title = a.xpath('span/@title').extract_first()
                type = 'pro'
            else:
                #  没在线或者其他原因找不到官网的情况
                titlexpath = "*[contains(@class,'compnay-name-li')]/span"
                span = node.xpath(baseXpath + titlexpath)
                title = span.xpath('@title').extract_first()
                href = node.xpath("*[contains(@class,'list-node-content')]/div[1]/div[1]/h2/a/@href").extract_first()
                print(href)
                url = urlparse('https:' + href)
                href = 'https://' + url.netloc
                type = ''
            province = node.xpath(baseXpath + "li[3]/span/text()").extract_first().strip()
            if province:
                province = province.split(',')[0]
            yield {'en_name': title, 'link': href, 'province': province, 'type': type,
                   'login_cookies': self.browser.get_cookies()}
        if self.exec_click_next_page():
            for com in self.yield_company_url():
                yield com


