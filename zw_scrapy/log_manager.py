# -*- coding: utf-8 -*-
# @Author  : xiao lin
# @Project : pq_military_taiwan
# @File    : log_manager.py
# @Soft    : PyCharm
# @Time    : 2022/12/27 14:09
# @Desc    : 日志管理
import logging
import sys
import time
from pathlib import Path
import colorlog


class LogManager:
    """
    日志管理器
    """
    handlers = dict()

    # _instance_lock = threading.Lock()
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(LogManager, "_instance"):
    #         with LogManager._instance_lock:
    #             if not hasattr(LogManager, "_instance"):
    #                 LogManager._instance = super().__new__(cls)
    #     return LogManager._instance

    def __init__(self, name=None, filename=None, level=logging.DEBUG, color=True):
        if name:
            self.name = Path(name).stem
        else:
            self.name = Path('root').stem
        filename_add_date = f"{self.name}_{time.strftime('%Y-%m-%d', time.localtime())}.log"
        # 获取调用者的信息
        calling_frame = sys._getframe(1)
        # 调用者的执行时的代码行
        # lineno = calling_frame.f_lineno
        # 调用者的文件名
        calling_filename = Path(calling_frame.f_code.co_filename)
        # 默认日志文件名
        self.filename = Path.joinpath(calling_filename.parent, "log", self.name, filename_add_date)
        if filename:
            if Path.is_absolute(Path(filename)):
                self.filename = Path.joinpath(Path.resolve(Path(filename)), self.name, filename_add_date)
            else:
                self.filename = Path.joinpath(calling_filename.parent, filename, self.name, filename_add_date)

        self.log_color_config = {
            'DEBUG': 'green',
            'INFO': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        }
        if color:
            self.console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s",
                log_colors=self.log_color_config)
        else:
            self.console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s")

        self.file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s")
        self.level = level

    def file_handler(self):
        # 创建目录，parents=True时，递归创建。
        if not Path.exists(Path(self.filename).parent):
            Path.mkdir(Path(self.filename).parent, parents=True)
        handler = logging.FileHandler(filename=self.filename, encoding='utf-8')
        handler.setFormatter(self.file_formatter)
        LogManager.handlers[self.name] = handler
        return handler

    def console_handler(self):
        # handler = logging.StreamHandler(io.TextIOWrapper(buffer=sys.stderr.buffer, encoding='utf8'))
        handler = logging.StreamHandler()
        handler.setFormatter(self.console_formatter)
        LogManager.handlers[self.name] = handler
        return handler

    def file_log(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.addHandler(self.file_handler())
        return logger

    def console_log(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.addHandler(self.console_handler())
        return logger

    def file_console_log(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.addHandler(self.file_handler())
        logger.addHandler(self.console_handler())
        return logger


if __name__ == '__main__':
    print(Path.resolve(Path(__file__)).parent.parent)
