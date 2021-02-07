import scrapy


class MadeinchinaSpider(scrapy.Spider):
    name = 'madeinchina'
    allowed_domains = ['made-in-china.com']
    start_urls = ['http://made-in-china.com/']
    #
    custom_settings = {
        'ITEM_PIPELINES': {
            'customerScrapy.pipelines.madeInChinaPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'customerScrapy.middlewares.CustomerscrapyDownloaderMiddleware': 543,
        },
        'DOWNLOAD_DELAY': 5
    }

    def parse(self, response):
        pass
