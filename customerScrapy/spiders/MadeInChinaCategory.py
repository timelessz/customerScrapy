import scrapy


class MadeinchinacategorySpider(scrapy.Spider):
    name = 'MadeInChinaCategory'
    allowed_domains = ['made-in-china.com']
    start_urls = ['https://made-in-china.com/']

    def parse(self, response):

        pass
