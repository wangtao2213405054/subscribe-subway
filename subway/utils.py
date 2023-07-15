# _author: Coke
# _date: 2023/3/16 11:16

from requests.exceptions import ConnectionError, ReadTimeout
from urllib3.exceptions import ReadTimeoutError

import datetime
import requests
import warnings
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
    :deprecated: 请访问 chinese_calendar.is_holiday
    :param date: 要获取的日期, 格式: 20230316
    :return: 如果是节假日返回 True, 否则为 False
    """
    warnings.warn(
        "此节假日服务器已经废弃", DeprecationWarning
    )
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


def time_interval(start_time: str = '06:30', end_time: str = '09:30') -> dict:
    """
    获取开始时间~结束时间每十分钟的时间区间
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 返回时间区间的字典, key: 06:30 ~ 06:40 value: 0630-0640
    """
    start_time = datetime.datetime.strptime(start_time, '%H:%M')
    end_time = datetime.datetime.strptime(end_time, '%H:%M')

    delta = datetime.timedelta(minutes=10)
    current_time = start_time

    time_dict = dict()
    while current_time < end_time:
        next_time = current_time + delta
        time_key = f"{current_time.strftime('%H:%M')} ~ {next_time.strftime('%H:%M')}"
        time_value = f"{current_time.strftime('%H%M')}-{next_time.strftime('%H%M')}"
        time_dict[time_key] = time_value
        current_time = next_time

    return time_dict


if __name__ == '__main__':
    _token = ''
    print(decode(_token))
