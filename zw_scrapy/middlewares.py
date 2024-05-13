# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
import time
from traceback import print_exc

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from twisted.internet.error import TCPTimedOutError,ConnectionLost,TimeoutError,ConnectionRefusedError
from scrapy import signals, Request
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from twisted.internet.defer import Deferred
from collections import deque
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.exceptions import IgnoreRequest, NotConfigured, CloseSpider
from twisted.internet import reactor
from zw_scrapy.errorcheck import FrequentOperationError
from zw_scrapy.settings import ZW_ERROR_WORD

class ExceptionMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def process_exception(self, request, exception, spider):
        print('ExceptionMiddleware 异常',request,exception)
        # 捕捉异常时暂停爬虫
        if isinstance(exception, FrequentOperationError):
            # 更换代理
            print('捕捉异常时暂停爬虫')
            self.paused = True
            # 停止正在处理的请求
            spider.engine.pause()
            # 设置定时器，在一定时间后恢复爬虫
            time.sleep(30)  # 休眠10秒钟
            spider.engine.unpause()

    def spider_opened(self, spider):
        spider.logger.info("ExceptionMiddleware opened: %s" % spider.name)

class ZwScrapySpiderMiddleware:
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
        print('process_spider_input(传给parse之前):',response)
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        print('process_spider_output(parse出来之后):', response,result)
        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        print('ZwScrapySpiderMiddleware 异常',exception)
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
        spider.logger.info("Spider opened: %s" % spider.name)


class ZwScrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
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
        # request.meta['proxy'] = 'http://192.168.1.171:38118'
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        # print(request.meta)
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        resource_id = request.meta.get('id')
        # spider.crawler
        if response.status == 200 and not any(word in response.text for word in ZW_ERROR_WORD):
            spider.logger.info(f'{resource_id}请求完成')
            print(f'{resource_id}请求完成', request.headers)
            return response
        if response.status!=200:
            spider.logger.error(f'{resource_id}请求返回{response.status}')
            print(f'{resource_id}请求返回{response.status}')
            raise CloseSpider(reason=f"Response status code is not 200: {response.status}")
        else:
            print(f'{resource_id}代理被检测', request.headers)
            spider.logger.error(f'{resource_id}代理被检测')
        spider.crawler.engine.pause()
        time.sleep(60)
        spider.crawler.engine.unpause()
        return Request(request.meta['parse_url'], callback=request.callback, dont_filter=True, meta=request.meta)



    def process_exception(self, request, exception, spider):
        print('ZwScrapyDownloaderMiddleware 异常',request,exception)
        print_exc()
        if isinstance(exception, (TCPTimedOutError, ConnectionLost,TimeoutError,ConnectionRefusedError)):
            spider.logger.info('暂停spider')
            print('暂停spider')
            spider.crawler.engine.pause()
            time.sleep(60)
            spider.crawler.engine.unpause()
            # now_proxy=request.meta['proxy']
            # new_proxy = get_new_proxy(now_proxy)  # 获取新代理的方法
            # spider.logger.info(f'更换代理:{new_proxy}')
            # if new_proxy:
            #     request.meta['proxy'] = new_proxy
                # 重新发送请求
            return request
        else:
            raise IgnoreRequest(f"{request.meta} Request failed: {exception}")
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)





class RotateUserAgentMiddleware(UserAgentMiddleware):
    """避免被ban策略之一：使用useragent池。
    使用注意：需在settings.py中进行相应的设置。
    更好的方式是使用：
    pip install scrapy-fake-useragent
    DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    }
    """
    user_agent_list = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    def __init__(self, user_agent=''):
        super(RotateUserAgentMiddleware, self).__init__()
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            # 记录当前使用的useragent
            spider.logger.info('Current UserAgent: ' + ua)
            # request.headers.setdefault('user-agent', ua)
            request.headers['user-agent'] = ua

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    # for more visit http://www.useragentstring.com/pages/useragentstring.php

# url_limit_middleware.py



class URLFetchLimitMiddleware:
    def __init__(self, settings, *args, **kwargs):
        if not settings.getint('URL_FETCH_LIMIT'):
            raise NotConfigured
        self.max_urls = settings.getint('URL_FETCH_LIMIT')
        self.fetched_urls = deque(maxlen=self.max_urls)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        # if response.status != 200:
        #     return self._retry(request, reason=response_status_message(response.status), spider=spider)
        self.fetched_urls.append(request.url)
        if len(self.fetched_urls) >= self.max_urls:
            print(f"已达到 URL 抓取限制 {self.max_urls}。暂停 20 秒。")
            spider.logger.info(f"已达到 URL 抓取限制 {self.max_urls}。暂停 20 秒。")
            # d = Deferred()
            # reactor.callLater(60, d.callback, None)
            # return d
            spider.crawler.engine.pause()
            time.sleep(20)
            spider.crawler.engine.unpause()
            print('清空队列')
            self.fetched_urls.clear()
        return response