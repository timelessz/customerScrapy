import time
from urllib.parse import urlparse

from parsel import Selector
from selenium.webdriver import ActionChains

from customerScrapy.Tools.chromeBrower import chromeBrower
from customerScrapy.dborm import getsession


class parseProductNextList:

    def __init__(self, industry, login_cookies):
        self.industry = industry
        if industry.current_page_num is None or not industry.current_page_num:
            industry.current_page_num = 0
        self.current_page_num = industry.current_page_num
        if industry.all_page_num is None or not industry.all_page_num:
            industry.all_page_num = 0
        self.all_page_num = industry.all_page_num
        self.DBSession = getsession()
        self.browser = chromeBrower().get_brower()
        self.browser.get('https://made-in-china.com/')
        # self.browser.maximize_window()
        for cookie in login_cookies:
            self.browser.add_cookie(cookie)
        if industry.cus_list_link is not None:
            self.nextpage_link_template = industry.cus_list_link
            self.__get_nextpage_link()
            print(self.nextpage_link)
            self.browser.get(self.nextpage_link)
        else:
            print(industry.link)
            self.browser.get('https:' + industry.link)
        self.__set_industry_pageinfo()
        time.sleep(10)

    '''生成继续请求客户列表的 url'''

    def __get_nextpage_link(self):
        nextpage_link = self.nextpage_link_template % (str(int(self.current_page_num) + 1))
        self.nextpage_link = "https:" + nextpage_link

    ''' 设置 某industry 信息 '''

    def __set_industry_pageinfo(self):
        # 进入列表页面首先切换 页面每页的数量为  50条每页
        page_info = self.__get_page_info()
        current_page_num, all_page_num, page_size, cus_list_link = page_info['current_page_num'], page_info['page_num'], \
                                                                   page_info['page_size'], page_info['cus_list_link']
        self.current_page_num = current_page_num
        self.nextpage_link_template = cus_list_link
        change_status = self.__change_default_page_num(page_size)
        # 第二次访问
        if change_status:
            page_info = self.__get_page_info()
            all_page_num, page_size, cus_list_link = page_info['page_num'], page_info['page_size'], page_info[
                'cus_list_link']
            # 换页面问题 导致 从第一页重新开始了
        self.all_page_num = all_page_num
        self.industry.all_page_num = all_page_num
        self.industry.cus_list_link = cus_list_link
        self.DBSession.commit()

    ''' 更新获取当前遍历完成的页码 '''

    def __update_current_page(self):
        self.industry.current_page_num = self.current_page_num
        self.DBSession.commit()

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
                if href:
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
                if href:
                    url = urlparse('https:' + href)
                    href = 'https://' + url.netloc
                type = ''
            province = node.xpath(baseXpath + "li[3]/span/text()").extract_first()
            if not href:
                continue
            if province:
                province = province.strip().split(',')[0]
            yield {'en_name': title, 'link': href, 'province': province, 'type': type,
                   'login_cookies': self.browser.get_cookies()}
        if self.exec_click_next_page():
            for com in self.yield_company_url():
                yield com

    '''切换默认页50条'''

    def __change_default_page_num(self, page_size):
        if page_size != 50 and self.browser.find_element_by_xpath("//*[@class='num-per-page']/a[last()]"):
            # 切换分页数量
            self.browser.execute_script('window.scrollTo(0,1000000)')
            ActionChains(self.browser).move_to_element(
                self.browser.find_element_by_xpath("//*[@class='num-per-page']/a[last()]")).click().perform()
            time.sleep(2)
            self.__get_nextpage_link()
            self.browser.get(self.nextpage_link)
            return True
        return False

    ''' 获取当前页 总页数 每页数量 '''

    def __get_page_info(self):
        html = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        sel = Selector(text=html)
        # 每页大小
        page_size = sel.xpath("//*[@class='num-per-page']/a[@class='selected']/text()").extract_first()
        # 总共页数
        all_page_num = sel.xpath("//*[@class='page-num']/a[last()-1]/text()").extract_first()
        if all_page_num:
            all_page_num = all_page_num.strip()
        # 当前页码
        current_page_num = sel.xpath("//*[@class='page-num']/strong[last()-1]/text()").extract_first()
        if (current_page_num and current_page_num.strip() == '...') or current_page_num is None:
            current_page_num = sel.xpath("//*[@class='page-num']/strong[last()]/text()").extract_first()
        if current_page_num:
            current_page_num = current_page_num.strip()
        cus_list_link = sel.xpath("//*[@class='page-num']/a[last() and @class!='page-dis']/@href").extract_first()
        return {'current_page_num': current_page_num, 'page_num': all_page_num, 'page_size': page_size,
                'cus_list_link': cus_list_link[:cus_list_link.rfind('-')] + '-%s.html'}

    ''' 执行 点击下一步操作 '''

    def exec_click_next_page(self):
        if int(self.current_page_num) <= int(self.all_page_num) and int(self.current_page_num) < 20:
            # 切换下一页
            self.browser.execute_script('window.scrollTo(0,1000000)')
            ActionChains(self.browser).move_to_element(
                self.browser.find_element_by_link_text('Next')).click().perform()
            self.industry.current_page_num = int(self.current_page_num) + 1
            self.industry.all_page_num = self.all_page_num
            self.current_page_num = int(self.current_page_num) + 1
            self.DBSession.commit()
            return True
        return False
