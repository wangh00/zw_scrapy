# Scrapy settings for zw_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import os
from logging.handlers import RotatingFileHandler


BOT_NAME = "zw_scrapy"

SPIDER_MODULES = ["zw_scrapy.spiders"]
NEWSPIDER_MODULE = "zw_scrapy.spiders"
# Scrapy-Redis相关配置
# 确保request存储到redis中
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 确保所有爬虫共享相同的去重指纹
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 设置redis为item pipeline
ITEM_PIPELINES = {
    "zw_scrapy.pipelines.ZwScrapyPipeline": 299,
    # 'scrapy_redis.pipelines.RedisPipeline': 300
}

# 在redis中保持scrapy-redis用到的队列，不会清理redis中的队列，从而可以实现暂停和恢复的功能。
SCHEDULER_PERSIST = True

# 设置连接redis信息
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

GZIP_PIPELINE_OUTPUT_DIR = 'zw'

SAVE_FILE = r'\\192.168.1.171\d\zw_test'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "zw_scrapy (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
DEFAULT_REQUEST_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "^sec-ch-ua": "^\\^Google",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^\\^Windows^^^",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "zw_scrapy.middlewares.ZwScrapySpiderMiddleware": 50,
# }
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy_fingerprint.fingerprintmiddlewares.FingerprintMiddleware': 543, #ja3指纹
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware':None,
    "zw_scrapy.middlewares.RotateUserAgentMiddleware": 400,
    "zw_scrapy.middlewares.URLFetchLimitMiddleware": 540,
    "zw_scrapy.middlewares.ZwScrapyDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "zw_scrapy.pipelines.ZwScrapyPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 6
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 当爬虫在运行过程中累计发生了 5 个错误，Scrapy 将自动关闭爬虫。
CLOSESPIDER_ERRORCOUNT = 5

# 通过启动 Web 服务，可以方便地监控和管理 Scrapy 爬虫
# WEBSERVICE_ENABLED=True


LOG_ENABLED = True
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy.log'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
# LOG_STDOUT=True
# 爬虫在运行过程中的内存使用情况，并且可以及时发现和解决内存泄漏等问题，以提高爬虫的稳定性和性能
# STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'


# 当爬虫正在处理的页面数量达到 SCRAPER_SLOT_MAX_ACTIVE_SIZE 时，如果有新的请求到达，Scrapy 将会等待一段时间，直到有活跃的页面被处理完成，然后再开始处理新的请求。这有助于避免爬虫同时处理过多的页面，导致资源消耗过大或者服务器被封禁。
# SCRAPER_SLOT_MAX_ACTIVE_SIZE

# logger = create_logger()

ZW_ERROR_WORD = ['对不起，服务器忙，请稍后再操作', '您的操作过于频繁，请输入验证码']

# github:https://github.com/tieyongjie/scrapy-fingerprint 修改ja3指纹，(有bug)
DOWNLOAD_HANDLERS = {
    'http': "zw_scrapy.downloadhandler.FingerprintDownloadHandler",
    'https': "zw_scrapy.downloadhandler.FingerprintDownloadHandler",
}
PROXY_URL='http://192.168.1.171:38118'

URL_FETCH_LIMIT = 10000

# scrapy.extensions.httpcache.RFC2616Policy 是 Scrapy 的一个 HTTP 缓存策略类，用于控制 HTTP 缓存的行为。该类实现了 RFC2616 中定义的 HTTP 缓存规则，可以帮助 Scrapy 在爬取过程中更有效地利用 HTTP 缓存，减少不必要的网络请求。
# HTTPCACHE_ENABLED = True
# HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'

# 重试中间件只需要设置这两个参数就行，不需要激活
# RETRY_TIMES = 3  # 设置重试次数为 3 次
# RETRY_HTTP_CODES = [500, 502, 503, 504, 408,403]  # 设置需要重试的 HTTP 状态码

