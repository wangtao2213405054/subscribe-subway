# _author: Coke
# _date: 2023/3/16 11:16

from requests.exceptions import ConnectionError, ReadTimeout
from urllib3.exceptions import ReadTimeoutError

import requests
import base64
import time


def decode(token) -> int:
    """
    将 base64 加密的 token解密并返回 token 过期时间
    :param token: 需要解析的 base64 token
    :return: 解密后的时间戳
    """

    try:
        _decode = base64.b64decode(token)
        timestamp = int(_decode.decode().split(',')[1]) / 1000
        return int(timestamp)
    except (Exception, ):
        return -1


def holiday(date) -> bool:
    """
    获取当前日期是否为节假日
    :param date: 要获取的日期, 格式: 20230316
    :return: 如果是节假日返回 True, 否则为 False
    """
    try:
        response = requests.request('GET', 'https://tool.bitefu.net/jiari', params=dict(d=date))
        if response.status_code != 200:
            return False
    except (ConnectionError, ReadTimeout, ReadTimeoutError):
        return False

    return bool(response.json())


def timer(start) -> None:
    """
    定时器, 阻塞程序直到到达指定时间
    :param start: 程序需要开始的时间
    :return:
    """

    while start >= time.time():
        time.sleep(0.1)


if __name__ == '__main__':
    _token = ''
    print(decode(_token))
