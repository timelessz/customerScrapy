# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time

from scrapy import signals

# useful for handling different item types with a single interface
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from customerScrapy.Tools.chromeBrower import chromeBrower


class CustomerscrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MadeInChinaCategoryScrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.browser = chromeBrower().get_brower()
        self.timeout = get_project_settings().get('SELENIUM_TIMEOUT')
        self.wait = WebDriverWait(self.browser, self.timeout)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
        #            executable_path=crawler.settings.get('CHROME_OPTIONS_BINARY_LOCATION'))
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        try:
            self.browser.get(request.url)
            cookies = request.cookies
            for cookie in cookies:
                self.browser.add_cookie(cookie)
            time.sleep(2)
            response = HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                    status=200)
            return response
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 参考这个  https://blog.csdn.net/killeri/article/details/80525825
class CustomerscrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.browser = chromeBrower().get_brower()
        self.timeout = get_project_settings().get('SELENIUM_TIMEOUT')
        self.wait = WebDriverWait(self.browser, self.timeout)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
        #            executable_path=crawler.settings.get('CHROME_OPTIONS_BINARY_LOCATION'))
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        try:
            # if request.url == 'https://www.made-in-china.com/':
            self.browser.get(request.url)
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
        ActionChains(self.browser).move_to_element(self.browser.find_element_by_link_text("Sign In")).perform()
        # down_data_click = WebDriverWait(self.browser, 5).until(
        #     EC.element_to_be_clickable((By.XPATH, "div/div[1]/div/div[3]/div/div[3]/div[1]/div[1]/div/a[1]"))
        # )
        time.sleep(2)
        # down_data_click.click()
        return

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
