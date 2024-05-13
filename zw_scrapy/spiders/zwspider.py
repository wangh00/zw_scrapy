import json
import logging
import time
from scrapy import Request
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
import scrapy
from scrapy import signals
from scrapy.crawler import logger


from scrapy_redis.spiders import RedisSpider
from zw_scrapy.errorcheck import FrequentOperationError
from zw_scrapy.settings import ZW_ERROR_WORD


class ZwspiderSpider(RedisSpider):
    name = "zwspider"
    redis_key = 'zwspider:start_urls'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.paused = False

    def make_request_from_data(self, data):
        # 从队列中获取 JSON 字符串
        json_data = json.loads(data.decode('utf-8'))
        json_data['file_path'] = '{}\{}\{}.html'.format(json_data['file_name'][:4],json_data['file_name'][4:8],json_data['file_name'])
        # 只提取 URL
        url = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&dbname=CJFDLAST2013&filename='+json_data['file_name']
        json_data['parse_url']=url
        print(json_data)
        logger.info(json_data)
        # 构造请求
        # FingerprintRequest(url,callback=self.parse,meta=json_data)
        return scrapy.Request(url,callback=self.parse,meta=json_data,errback=self.handle_error)

    def parse(self, response):
        meta=response.meta
        item = {
            'file_path': meta['file_path'],
            'content': response.text,
            'id': meta['id']
        }
        yield item

    def handle_error(self, failure):
        # 在这里处理请求异常
        request = failure.request
        if hasattr(request, 'meta'):
            # 可以从请求的元数据中获取额外信息
            meta = request.meta
            print(f"Error processing request: {request.url}, meta: {meta}")
            self.logger.error(f"Error processing request: {request.url}, meta: {meta}")
        else:
            print(f"Error processing request: {request.url}")
            self.logger.error(f"Error processing request: {request.url}")