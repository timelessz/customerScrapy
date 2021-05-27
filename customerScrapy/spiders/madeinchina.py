import time
import scrapy
from customerScrapy.Model import Industry, Customer
from customerScrapy.Tools.parseProductNextList import parseProductNextList
from customerScrapy.dborm import getsession


class MadeinchinaSpider(scrapy.Spider):
    name = 'madeinchina'
    allowed_domains = ['made-in-china.com']
    start_urls = ['https://made-in-china.com/']
    category_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'customerScrapy.pipelines.madeInChinaPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'customerScrapy.middlewares.CustomerscrapyDownloaderMiddleware': 543,
        },
        'DOWNLOAD_DELAY': 5
    }

    def __init__(self):
        # 定义保存登录成功之后的cookie的变量
        self.login_cookies = []
        self.DBSession = getsession()

    '''系统登录 '''

    def __get_cookies(self):
        if not self.login_cookies:
            # cookies = Login().get_cookies()
            cookies = []
            if cookies:
                self.login_cookies = cookies
                print('=====================', self.login_cookies)
                return True
            else:
                print('cookies get error')
                return False

    '''开始数据请求 '''

    def start_requests(self):
        # 分类列表
        self.__get_cookies()
        for cat_id in self.category_ids:
            industrys = self.DBSession.query(Industry).filter_by(cat_id=cat_id).all()
            for industry in industrys:
                if industry.current_page_num and industry.current_page_num >= 10:
                    continue
                if industry.current_page_num and industry.current_page_num >= 10:
                    continue
                if industry.all_page_num and industry.all_page_num < 20:
                    continue
                if industry.all_page_num and industry.current_page_num and industry.current_page_num >= industry.all_page_num:
                    continue
                if industry.cus_list_link == '%s':
                    continue
                # 遍历 所有的行业分类
                for com_info in parseProductNextList(industry, self.login_cookies).yield_company_url():
                    if not com_info:
                        continue
                    # 更新cookies
                    self.login_cookies = com_info['login_cookies']
                    # 首先判断是不是数据库中已经有了
                    customer = self.__check_add_customer(com_info, industry.id)

    ''' 判断是不是该公司已经存在 '''

    def __check_add_customer(self, com_info, industry_id):
        en_name = com_info['en_name']
        customer = self.DBSession.query(Customer).filter_by(en_name=en_name).first()
        if customer is None:
            print('''''''''''''''''''''''''''''''''''''''''''''''''''''''')
            print('addddddddddddddddddddddddddddddddddddddddddddddddddd')
            print('''''''''''''''''''''''''''''''''''''''''''''''''''''''')
            currenttime = int(time.time())
            customer = Customer(
                industry_id=industry_id,
                name='',
                en_name=com_info['en_name'],
                address='',
                city='',
                province=com_info['province'],
                contact='',
                telephone='',
                mobile='',
                fax='',
                showroom=com_info['link'],
                website='',
                type=com_info['type'],
                created_at=currenttime,
                updated_at=currenttime,
            )
            self.DBSession.add(customer)
            self.DBSession.commit()
        return customer
