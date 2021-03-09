import time

import scrapy
from scrapy import Selector
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from customerScrapy.Model import Type, Category, Industry
from customerScrapy.Tools.Login import Login
from customerScrapy.dborm import getsession


class MadeinchinacategorySpider(scrapy.Spider):
    name = 'madeinchinacategory'
    allowed_domains = ['made-in-china.com']
    start_urls = ['https://made-in-china.com/']
    login_url = 'https://login.made-in-china.com/sign-in/'

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'customerScrapy.pipelines.madeInChinaPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'customerScrapy.middlewares.MadeInChinaCategoryScrapyDownloaderMiddleware': 543,
        },
        'DOWNLOAD_DELAY': 5
    }

    def __init__(self):
        # 定义保存登录成功之后的cookie的变量
        self.login_cookies = []
        self.DBSession = getsession()

    def start_requests(self):
        cookies = Login().get_cookies()
        if cookies:
            self.login_cookies = cookies
        else:
            print('cookies get error')
            return
        print('=====================', self.login_cookies)
        # 分类列表
        starturl = 'https://www.made-in-china.com/prod/catlist/'
        request = scrapy.Request(url=starturl, cookies=self.login_cookies, callback=self.parse_type)
        # 获取类型以及大分类
        request.meta['type'] = 'typecategory'
        request.meta['url'] = starturl
        yield request

    def parse_type(self, response):
        sel = Selector(response)
        divs = sel.xpath(
            "/html/body/div[1]/*[contains(@class,'catlist-wrap')]/*[contains(@class,'catlist-content')]/div")
        for div in divs:
            # 获取 type
            type_enname = div.xpath("*[contains(@class,'primary-classify')]/h2/text()").extract_first()
            type_id = self.__add_type(type_enname)
            categories_divs = div.xpath(
                "*[contains(@class,'primary-classify-content')]/*[contains(@class,'sec-classify-wrap')]/*[contains(@class,'sec-classify')]")
            for cat_div in categories_divs:
                c = cat_div.xpath('h3/a')
                href = c.xpath('@href').extract_first()
                # 获取行业大分类 category
                text = c.xpath('text()').extract_first()
                cat_id = self.__add_category(href, text, type_id)
                # 点击打开小分类的id 然后获取更多
                request = scrapy.Request(url='https:' + href, cookies=self.login_cookies, callback=self.parse_industry)
                # 获取类型以及大分类
                request.meta['type'] = 'industry'
                request.meta['url'] = href
                request.meta['cat_id'] = cat_id
                yield request
        pass

    def parse_industry(self, response):
        cat_id = response.meta['cat_id']
        sel = Selector(response)
        cate_items = sel.xpath("//*[contains(@class,'cate-items')]//a[contains(@class,'item')]")
        for cate in cate_items:
            c_href = cate.xpath('@href').extract_first()
            # 获取行业大分类 category
            c_text = cate.xpath('h3/text()').extract_first()
            industry_id = self.__add_industry(c_href, c_text, cat_id)
            print('子分类 %s:%s' % (c_text, c_href))
        pass

    # 添加大分类
    def __add_type(self, type_enname):
        type = self.DBSession.query(Type).filter_by(en_name=type_enname).first()
        if type is not None:
            return type.id
        currenttime = int(time.time())
        type = Type(
            name='',
            en_name=type_enname,
            created_at=currenttime,
            updated_at=currenttime
        )
        self.DBSession.add(type)
        self.DBSession.flush()
        self.DBSession.commit()
        return type.id

    # 添加小分类
    def __add_category(self, href, text, type_id):
        cate = self.DBSession.query(Category).filter_by(en_name=text).first()

        if cate is not None:
            return cate.id
        currenttime = int(time.time())
        cate = Category(
            name='',
            en_name=text,
            link=href,
            type_id=type_id,
            created_at=currenttime,
            updated_at=currenttime
        )
        self.DBSession.add(cate)
        self.DBSession.flush()
        self.DBSession.commit()
        return cate.id

    # 添加行业
    def __add_industry(self, href, text, cat_id):
        industry = self.DBSession.query(Industry).filter_by(link=href).first()
        if industry is not None:
            print('/////////////////////////////')
            print(industry)
            print('存在存在存在存在存在存在存在存在存在存在存在存在存在存在存在存在存在存在存在存在')
            print('/////////////////////////////')
            return 0
        print('/////////////////////////////')
        print(industry)
        print('添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加添加')
        print('/////////////////////////////')
        currenttime = int(time.time())
        industry = Industry(
            name='',
            en_name=text,
            link=href,
            cat_id=cat_id,
            created_at=currenttime,
            updated_at=currenttime
        )
        self.DBSession.add(industry)
        self.DBSession.flush()
        self.DBSession.commit()
        return industry.id
