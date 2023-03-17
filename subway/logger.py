# _author: Coke
# _date: 2023/3/16 15:32

from logging import config

import logging
import json
import os

_LOG_BYTES = 1024 * 1024 * 100
_LOG_COUNT = 10

INFO = 'INFO'
DEBUG = 'DEBUG'
ERROR = 'ERROR'
WARNING = 'WARNING'
CRITICAL = 'CRITICAL'


def get_conf() -> str:
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


def logger(level: INFO) -> None:
    """
    设置本次运行时的日志信息
    :param level: 日志等级
    :return:
    """

    base_conf = get_conf()

    if not os.path.exists(base_conf):
        return

    _path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log.log'))

    with open(base_conf, 'r', encoding='utf-8') as file:
        read_data = json.loads(file.read())
        read_data['root']['level'] = level
        read_data['handlers']['file']['filename'] = _path

    config.dictConfig(read_data)


if __name__ == '__main__':
    print(logger(INFO))
    for item in range(10):
        logging.info('Test')
