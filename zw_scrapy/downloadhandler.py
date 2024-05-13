import asyncio
import random
from time import time
from urllib.parse import urldefrag

import scrapy
from scrapy.http import HtmlResponse
from scrapy.spiders import Spider
from scrapy.http import Response

from twisted.internet.defer import Deferred
from twisted.internet.error import TimeoutError

from curl_cffi.requests import AsyncSession
from curl_cffi import const
from curl_cffi import curl


def as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))



def parse_proxy(proxy: str):
    """ 解析代理
        http://871235132009631744:EEBMLsbW@114.102.9.102:42422
    """
    proxy_split = proxy.split(':')
    if 'sock' not in proxy_split[0] and 'http' not in proxy_split[0]:
        scheme = 'http'
    else:
        scheme = proxy_split[0]
        proxy = proxy.split('/')[-1]
    if '@' in proxy:
        usr_pwd = proxy.split('@')[0]
        user = usr_pwd.split(':')[0] if usr_pwd else ''
        password = usr_pwd.split(':')[-1] if usr_pwd else ''
        host_port = proxy.split('@')[-1]
        host = host_port.split(':')[0] if host_port else ''
        port = host_port.split(':')[-1] if host_port else ''
    else:
        user = ''
        password = ''
        host = proxy.split(':')[0]
        port = proxy.split(':')[-1]
    return scheme, user, password, host, port

class FingerprintDownloadHandler:

    def __init__(self, *args):
        print(args)
        if args:
            self.scheme=args[0]
            self.user = args[1]
            self.password = args[2]
            self.server = args[3]
            self.proxy_port = args[4]
            if self.user:
                proxy_meta = "%(scheme)s://%(user)s:%(pass)s@%(host)s:%(port)s" % {
                    "scheme":self.scheme,
                    "host": self.server,
                    "port": self.proxy_port,
                    "user": self.user,
                    "pass": self.password,
                }
            else:
                proxy_meta = "%(scheme)s://%(host)s:%(port)s" % {
                    "scheme": self.scheme,
                    "host": self.server,
                    "port": self.proxy_port,
                }
            print(proxy_meta)
            self.proxies = {
                "http": proxy_meta,
                "https": proxy_meta,
            }
        else:
            self.proxies = None

    @classmethod
    def from_crawler(cls, crawler):
        proxy_url = crawler.settings.get("PROXY_URL")
        # scheme, user, password, host, port = parse_proxy(proxy_url)
        if proxy_url:
            s = cls(*parse_proxy(proxy_url))
        else:
            s=cls()
        return s

    async def _download_request(self, request):
        async with AsyncSession() as s:
            impersonate = request.meta.get("impersonate") or random.choice([
                "chrome99", "chrome101", "chrome110", "edge99", "edge101",
                "chrome107"
            ])

            timeout = request.meta.get("download_timeout") or 30

            try:
                response = await s.request(
                    request.method,
                    request.url,
                    data=request.body,
                    headers=request.headers.to_unicode_dict(),
                    proxies=self.proxies,
                    timeout=timeout,
                    impersonate=impersonate)
            except curl.CurlError as e:
                if e.code == const.CurlECode.OPERATION_TIMEDOUT:
                    url = urldefrag(request.url)[0]
                    raise TimeoutError(
                        f"Getting {url} took longer than {timeout} seconds."
                    ) from e
                raise e

            response = HtmlResponse(
                request.url,
                encoding=response.encoding,
                status=response.status_code,
                # headers=response.headers,
                body=response.content,
                request=request
            )
            return response

    def download_request(self, request: scrapy.Request,
                         spider: Spider) -> Deferred:
        del spider
        start_time = time()
        d = as_deferred(self._download_request(request))
        d.addCallback(self._cb_latency, request, start_time)

        return d

    @staticmethod
    def _cb_latency(response: Response, request: scrapy.Request,
                    start_time: float) -> Response:
        request.meta["download_latency"] = time() - start_time
        return response
