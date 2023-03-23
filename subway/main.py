# _author: Coke
# _date: 2023/3/16 17:16

from typing import Optional

import multiprocessing
import threading
import datetime
import logging
import click
import time
import json
import os
import sys


def conf(path: Optional[str]) -> dict:
    """
    获取配置文件中的抢票信息
    :param path: 指定配置文件路径, 如不指定则使用项目 conf/conf.json 文件
    :return:
    """
    conf_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'conf',
        'conf.json'
    )) if path is None else path

    with open(conf_path, 'r', encoding='utf-8') as file:
        return json.loads(file.read())


def timeliness(path) -> None:
    """
    鉴定用户列表中的 Token 过期时间, 如果小于 1天 或 失效则进行通知
    :return:
    """

    while True:
        _conf = conf(path)
        users = _conf.get('UserAgent')
        _token, _sign = _conf.get('dingTalkToken'), _conf.get('dingTalkSign')
        _ding = message.DingTalk(_token, _sign)

        for user in users:
            overdue = utils.decode(user.get('token'))
            if overdue < time.time():
                _message = f'{user.get("name")} 用户 Token 已过期'
                logging.info(_message)
                _ding.text(_message)
            elif overdue - time.time() < 86400:
                _message = f'{user.get("name")} 用户 Token 即将过期'
                logging.info(_message)
                _ding.text(_message)
            else:
                logging.info(f'{user.get("name")} 用户 Token 还有 {round((overdue - time.time()) / 86400, 1)} 天过期')

        now = datetime.datetime.now()
        today = now - datetime.timedelta(
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
            microseconds=now.microsecond
        )
        tomorrow = (today + datetime.timedelta(days=1, hours=10)).timestamp()
        utils.timer(tomorrow)


@click.command()
@click.option(
    '--subscribe',
    '-s',
    help='设置抢票时间段, 官方提示为每日12点、20点方法次日预约名额, 默认值为 "12,20" 如需多个时间点请以英文 , 分割',
    default='12,20'
)
@click.option(
    '--processes',
    '-ps',
    help='进程池最多同时运行的数量, 默认最多同时启动 5 个线程',
    default=5
)
@click.option(
    '--dingtalk',
    '-dt',
    help='是否启动钉钉机器人通知, 启动为 1 , 默认不启动 0, 如需启动请在配置文件中指定钉钉机器人的 webhook 和 sign',
    default=0
)
@click.option(
    '--path',
    '-p',
    help='指定的配置文件路径, 如不指定则使用项目下 conf/conf.json 文件',
    default=''
)
def command(subscribe: str, processes: int, dingtalk: int, path: str) -> None:
    subscribe = list(map(lambda x: int(x), subscribe.split(',')))
    dingtalk = bool(dingtalk)
    path = path if path else None
    run(subscribeTime=subscribe, processes=processes, dingTalk=dingtalk, confPath=path)


def run(**kwargs) -> None:
    """
    循环执行抢票任务的主入口, 过滤国家法定节假日
    :param kwargs:
            subscribeTime -> List: 可抢票的时段, [12, 20]
            processes -> int: 进程池最多同时运行的数量
            dingTalk -> bool: 是否启动钉钉机器人通知
            confPath -> str: 配置文件路径
    :return:
    """
    logger.logger(logger.INFO)
    subscribe_time = kwargs.pop('subscribeTime', [12, 20])
    _processes = kwargs.pop('processes', 5)
    _ding_talk = kwargs.pop('dingTalk', False)
    _conf = kwargs.pop('confPath', None)

    if _conf is not None and not os.path.exists(_conf):
        click.echo('配置文件路径不正确, 请检查')
        return

    users = conf(_conf).get('UserAgent')  # 用户列表

    # 如果启用通知则启动 Token 时效监听
    if _ding_talk:
        _thread = threading.Thread(target=timeliness, args=(_conf,), daemon=True)
        _thread.start()

    while True:
        now = datetime.datetime.now()
        today = now - datetime.timedelta(
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
            microseconds=now.microsecond
        )
        tomorrow = (today + datetime.timedelta(days=1))
        logging.debug(f'今日: {today.strftime(metro.FORMAT)} 明日: {tomorrow.strftime(metro.FORMAT)}')
        # 如果为节假日则不需要进行抢票
        if utils.holiday(tomorrow.strftime(metro.FORMAT)):
            logging.info('明天是节假日, 不需要抢票哦~')
            utils.timer(tomorrow.timestamp())
            continue

        start_time = None
        # 获取当前时间距离可以抢票的时间戳
        for item in subscribe_time:
            runtime = (today + datetime.timedelta(hours=item)).timestamp()
            if time.time() < runtime:
                start_time = runtime
                logging.info(f'准备今天 {item} 抢明天的票!')
                break

        # 如果当前运行时间已经超出了抢票时间则明天运行, 并初始化用户列表
        if start_time is None:
            users = conf(_conf).get('UserAgent')
            logging.info('已经错过今天抢票时间, 明天开始抢票~')
            utils.timer(tomorrow.timestamp())
            continue

        logging.debug(f'下次抢票时间为: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}')
        utils.timer(start_time - 10)

        # 启动进程池
        pool = multiprocessing.Pool(_processes)
        task_result = []
        for item in users:
            item['startTime'] = start_time
            result = pool.apply_async(task, kwds=item)
            task_result.append(result)

        pool.close()
        pool.join()

        _result = list(map(lambda x: x.get(), task_result))
        # 如果存在用户未抢到票, 则重置用户列表, 进行下次尝试
        users = list(filter(lambda x: not x.get('result'), _result))

        for item in _result:
            _message = f'{item.get("name")}抢票: {"成功" if item.get("result") else "失败"}'
            logging.info(_message)

            if _ding_talk:
                _conf_data = conf(_conf)
                _token, _sign = _conf_data.get('dingTalkToken'), _conf_data.get('dingTalkSign')
                _ding = message.DingTalk(_token, _sign)
                _ding.text(_message)


def task(**kwargs) -> dict:
    """
    执行抢票程序任务
    :param kwargs:
            startTime -> int: 开始执行的时间
            lineName -> str: 线路名称
            stationName -> str: 站点名称
            timeSlot -> str: 抢票时段
            token -> str: 地铁系统的 Authorization 字段
            interval -> Union[int, float]: 抢票失败后的重试间隔
            frequency -> int: 抢票失败后的重试次数
    :return: 返回是否抢票成功
    """
    logger.logger(logger.INFO)
    _start = kwargs.pop('startTime', 0)
    _line = kwargs.pop('lineName', '昌平线')
    _station = kwargs.pop('stationName', '沙河站')
    time_slot = kwargs.pop('timeSlot', '0720-0730')
    token = kwargs.pop('token', None)
    interval = kwargs.pop('interval', 1)
    frequency = kwargs.pop('frequency', 7)
    kwargs['result'] = True

    _metro = metro.Metro(token)

    # 如果已存在当前时段的预约则终止
    exist = _metro.appointment(stationName=_station, arrivalTime=time_slot, timeout=2)
    if exist:
        logging.info('检测到已存在预约, 终止程序')
        return kwargs

    utils.timer(_start)

    for item in range(frequency):
        _balance = _metro.balance(stationName=_station, timeSlot=time_slot)
        if _balance or not item:
            logging.info(f'{_station}-{time_slot} 时段存在余票, 准备抢票')

            thread_list = []
            for _ in range(3):
                thread = threading.Thread(target=_metro.shakedown, kwargs=dict(
                    lineName=_line,
                    stationName=_station,
                    timeSlot=time_slot
                ))
                thread.start()
                thread_list.append(thread)
            for _thread in thread_list:
                _thread.join()

            result = _metro.appointment(stationName=_station, arrivalTime=time_slot, timeout=2)
            if result:
                break
        else:
            logging.info(f'{_station}-{time_slot} 时段已经没有余票了...')
        time.sleep(interval)

    else:
        logging.info(f'程序运行了 {frequency} 次, 没有抢到票...')
        kwargs['result'] = False

    # 由于高峰期接口容易超时, 最后程序运行完成后再进行一次断言
    kwargs['result'] = _metro.appointment(stationName=_station, arrivalTime=time_slot)
    return kwargs


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from subway import metro, utils, logger, message
    command()
