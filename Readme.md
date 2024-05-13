# scrapy是基于twisted事件驱动框架的一个python爬虫框架
## 本项目是根据知网文件名(filename)采集，借助redis实现分布式下载页面文件
## 项目包含一些自己学习中的笔记

### 运行 

>1.insert_redis.py向redis中插入data = {'id': line[0], 'file_name': line[1]}

>2.python.exe run.py
>> scrapy_fingerprint是重写了request类使用了curl_cffi请求,downloadhandler.py为scrapy_fingerprint.fingerprintmiddlewares.FingerprintMiddleware更改,源库存在bug，不支持socks代理

- 可以通过[AnotherRedisDesktopManager](https://github.com/qishibo/AnotherRedisDesktopManager)查看redis中的数据

## 仅供学习使用。
