# _author: Coke
# _date: 2023/3/16 15:32

from logging import config

import logging
import tkinter
import json
import time
import os

_LOG_BYTES = 1024 * 1024 * 100
_LOG_COUNT = 10

INFO = 'INFO'
DEBUG = 'DEBUG'
ERROR = 'ERROR'
WARNING = 'WARNING'
CRITICAL = 'CRITICAL'

_LEVEL = dict(
    CRITICAL=50,
    ERROR=40,
    WARNING=30,
    INFO=20,
    DEBUG=10
)


class LoggingOutput:
    """ 二次封装了一下 logging 方法, 支持 customtkinter.CTkTextbox 数据传递 """

    def __init__(self, level, handle=None, progress=False):
        self.level = _LEVEL.get(level)
        self.handle = handle
        self.progress = progress
        self._format = '%Y-%m-%d %H:%M:%S'
        base_conf = self._get_conf()
        self.log_list = []
        if not os.path.exists(base_conf):
            return

        _path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log.log'))

        with open(base_conf, 'r', encoding='utf-8') as file:
            read_data = json.loads(file.read())
            read_data['root']['level'] = level
            read_data['handlers']['file']['filename'] = _path

        config.dictConfig(read_data)

    @staticmethod
    def _get_conf() -> str:
        """
        获取日志配置文件路径
        :return:
        """
        conf_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'conf',
            'log.json'
        ))
        return conf_path

    def message(self, msg, level, color):
        message = f'{time.strftime(self._format)} {level}: {msg}\n'
        if not self.progress:
            self.handle.insert(tkinter.END, message, color)
            self.handle.see(tkinter.END)
        else:
            self.log_list.append([msg, level, color])

    def info(self, msg, *args, **kwargs):
        if self.level <= _LEVEL.get(INFO):
            if self.handle is not None:
                self.message(msg, INFO, 'success')
            logging.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.level <= _LEVEL.get(DEBUG):
            if self.handle is not None:
                self.message(msg, DEBUG, 'info')
            logging.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.level <= _LEVEL.get(ERROR):
            if self.handle is not None:
                self.message(msg, ERROR, 'danger')
            logging.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.level <= _LEVEL.get(WARNING):
            if self.handle is not None:
                self.message(msg, WARNING, 'warning')
            logging.warning(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.level <= _LEVEL.get(CRITICAL):
            if self.handle is not None:
                self.message(msg, CRITICAL, 'danger')
            logging.critical(msg, *args, **kwargs)


if __name__ == '__main__':
    obj = LoggingOutput(INFO)
    for item in range(10):
        obj.info('Test')
