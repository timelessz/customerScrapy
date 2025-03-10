import copy
import time
from math import ceil

import scrapy
from customerScrapy.Model import Customer
from customerScrapy.Tools.Login import Login

from customerScrapy.Tools.parseCustomerInfo import parseCustomer
from customerScrapy.dborm import getsession


class MadeinchinaCustomerSpider(scrapy.Spider):
    name = 'madeinchinacustomer'
    allowed_domains = ['made-in-china.com']
    start_urls = ['https://made-in-china.com/']

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
            cookies = Login().get_cookies()
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
        customer_parser = parseCustomer(self.login_cookies)
        customers_query = self.DBSession.query(Customer).filter(Customer.contact == '', Customer.type == 'pro')
        customers_count_query = customers_query
        count = customers_count_query.count()
        per_group_customers = []
        limit = 10
        for i in range(1, ceil(count / limit)):
            customers = customers_query.offset((i - 1) * limit).limit(limit).all()
            for customer in customers:
                print('...................................')
                print(customer.id)
                print('...................................')
                per_group_customers.append(customer)
            customer_parser.parse_customer_info(per_group_customers)
            per_group_customers = []
        return

    ''' 判断是不是该公司已经存在 '''

    def __check_add_customer(self, com_info, industry_id):
        en_name = com_info['en_name']
        customer = self.DBSession.query(Customer).filter(Customer.en_name == en_name).first()
        if customer is None:
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
