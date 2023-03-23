# _author: Coke
# _date: 2023/3/16 13:06

from typing import Union, Dict, List
from requests.exceptions import ReadTimeout
from urllib3.exceptions import ReadTimeoutError

import traceback
import datetime
import requests
import logging

DOMAIN = 'https://webapi.mybti.cn'  # 域名
FORMAT = '%Y%m%d'  # 格式化时间


class Metro:
    """ 地铁相关接口 """

    def __init__(self, token):
        self.token = token  # 地铁系统的 Authorization 字段

    def request(self, method: str, uri: str, **kwargs) -> Union[Dict, List, str, int, None]:
        """
        基于 requests 库进行了二次业务封装
        所有跟 clientele 服务器做交互的库都应该调用此方法
        :param method: 请求类型
        :param uri:  请求的路径
        :param kwargs: 参考 requests.request
        :return: 返回服务器返回消息体中的 data 数据
        """

        _error = kwargs.pop('exceptions', ())
        default = kwargs.pop('default', False)
        url = f'{DOMAIN}{uri}'

        header = dict(
            Host='webapi.mybti.cn',
            Connection='keep-alive',
            Accept='application/json, text/plain, */*',
            Origin='https://webui.mybti.cn',
            Authorization=self.token,
            Referer='https://webui.mybti.cn/'
        )
        logging.debug(f'请求信息: {uri}')
        logging.debug(f'{kwargs.get("json")}')

        try:
            response = requests.request(method, url, headers=header, **kwargs)

            if response.status_code != 200:
                _message = f'服务器内部错误, 接口: {uri} 状态码: {response.status_code}'
                logging.error(_message)
                return default

            body = response.json()
            logging.debug(f'响应信息: {body}')
            return body

        except _error:
            logging.debug(traceback.format_exc())
            return {}

    def shakedown(self, **kwargs) -> bool:
        """
        发送抢票信息
        :param kwargs:
                lineName: 需要填写要抢票的线路
                stationName: 要抢票的站点名称
                enterDate: 需要抢哪天的票
                timeSlot: 时间段信息
                snapshotWeekOffset: 0
        :return: 返回 True or False
        """

        line_name = kwargs.pop('lineName', '昌平线')
        station_name = kwargs.pop('stationName', '沙河站')
        tomorrow = datetime.date.today() + datetime.timedelta(1)
        enter_date = kwargs.pop('enterDate', tomorrow.strftime(FORMAT))
        time_slot = kwargs.pop('timeSlot', '0630-0640')
        snapshot_week_offset = kwargs.pop('snapshotWeekOffset', 0)

        body = dict(
            lineName=line_name,
            snapshotWeekOffset=snapshot_week_offset,
            stationName=station_name,
            enterDate=enter_date,
            timeSlot=time_slot,
            snapshotTimeSlot='0630-0930'
        )
        uri = '/Appointment/CreateAppointment'
        response = self.request('POST', uri, json=body, timeout=2, exceptions=(ReadTimeout, ReadTimeoutError))
        return isinstance(response, dict) and isinstance(response.get('balance'), int) and response.get('balance') > 0

    def balance(self, **kwargs) -> List:
        """
        获取余票信息
        :param kwargs:
                stationName: 站点名称
                enterDates: 查询时段 开始天数~结束天数
                timeSlot: 查询预约时段, 0630-0930
        :return: 返回当前所有可预约的时段
        """
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)

        station_name = kwargs.pop('stationName', '沙河站')
        enter_dates = kwargs.pop('enterDates', [
            today.strftime(FORMAT),
            tomorrow.strftime(FORMAT)
        ])
        time_slot = kwargs.pop('timeSlot', '0630-0930')

        body = dict(
            stationName=station_name,
            enterDates=enter_dates,
            timeSlot=time_slot
        )
        response = self.request('POST', '/Appointment/GetBalance', json=body, default=[])

        return list(filter(lambda x: x.get('balance') and not x.get('status'), response))

    def appointment(self, **kwargs) -> bool:
        """
        获取当前是否存在进站码, 当传递 kwargs 参数后则会匹配站点信息是否符合
        :param kwargs:
                stationName: 站点名称, 格式: 沙河站
                arrivalTime: 查询预约时段, 格式: 0640-0650
                timeout: 接口超时时间, 如果为 None 则一直等待
        :return: 返回预约是否存在, 存在此阶段预约则返回 True, 否则为 False
        """

        station_name = kwargs.pop('stationName', None)
        arrival_time = kwargs.pop('arrivalTime', None)
        timeout = kwargs.pop('timeout', None)

        params = dict(
            status=0,
            lastid=''
        )
        response = self.request(
            'GET',
            '/AppointmentRecord/GetAppointmentList',
            params=params,
            timeout=timeout,
            exceptions=(ReadTimeout, ReadTimeoutError)
        )

        if not response:
            return False

        if isinstance(response, list) and (station_name and arrival_time):
            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(1)
            _times = list(map(lambda x: f'{x[:2]}:{x[2:]}', arrival_time.split('-')))
            _format = f"{tomorrow.month}月{tomorrow.day}日 ({'~'.join(_times)})"
            for item in response:
                _station = item.get('stationName')
                _arrival = item.get('arrivalTime')
                if _station == station_name and _arrival == _format:
                    return True

            return False

        return True


if __name__ == '__main__':
    _token = "YjA2YWM0ODMtNzQwOS00MjcyLWE3YWQtNzg5MWM5MDJlZjkzLDE2Nzk2Njg5OTk3MDkseStu" \
             "MS9aNFpCZGpvVW54N3Y1RGppMG5odHJJPQ=="
    data = {"lineName": '昌平线', "snapshotWeekOffset": 0, "stationName": '沙河站', "enterDate": '20230317',
            "snapshotTimeSlot": "0630-0930", "timeSlot": '0630-0640'}
    _metro = Metro(_token)
    print(_metro.appointment(stationName='天通苑站', arrivalTime='0630-0650'))
