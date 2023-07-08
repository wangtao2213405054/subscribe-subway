# _author: Coke
# _date: 2023/7/8 20:02

from typing import Optional, Tuple, Type

import multiprocessing
import threading
import datetime
import logging
import click
import time
import json
import sys
import os


# 检查项目目录完整性
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from subway import metro, utils, logger, message
except ImportError as e:
    logging.error('请确保运行路径正确 ...')
    raise ImportError('请进入项目路径 subscribe-subway/subway 目录运行此脚本')


# 如果 Python 解释器版本低于 3.9 则退出程序
_current_version = sys.version_info
_expect_version = (3, 9)

if _current_version < _expect_version:
    raise RuntimeError(
        f'脚本需要 Python {_expect_version[0]}.{_expect_version[1]} 及以上版本, '
        f'当前 Python 为 {_current_version.major}.{_current_version.minor}'
    )


class Subway:
    """ 地铁抢票程序主入口 """

    def __init__(self, **kwargs):
        """
        初始化抢票程序
        :param kwargs:
                subscribeTime -> List: 可抢票的时段, [12, 20]
                processes -> int: 进程池最多同时运行的数量
                dingTalk -> bool: 是否启动钉钉机器人通知
                confPath -> str: 配置文件路径
        :return:
        """
        logger.logger(logger.INFO)
        self.subscribe_time = kwargs.pop('subscribeTime', [12, 20])
        self.processes = kwargs.pop('processes', 5)
        self.dingtalk = kwargs.pop('dingTalk', False)
        self.filename = kwargs.pop('confPath', None)

        # 如果未指定配置文件则使用默认配置文件
        if self.filename is None:
            self.filename = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                'conf',
                'conf.json'
            ))

        # 判断文件是否存在
        assert os.path.exists(self.filename), '配置文件路径不正确, 请检查'

        # 配置文件内容信息
        self.file_content: str = self._read_file_content()

        # 检查文件配置是否符合规范
        _check, _message = self._check_content(self.file_content)
        assert _check, _message

        # 创建一个用户通知容器
        self.user_notification = dict()

    def _read_file_content(self) -> str:
        """
        读取文件内容
        :return:
        """
        with open(self.filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    @staticmethod
    def _check_token(token: str) -> bool:
        """
        检查 Token 是否处于有效期
        :return: 未过期返回 (True, 过期时间) 否则返回 (False, 过期时间)
        """
        return utils.decode(token) > int(time.time())

    def _check_content(self, content: str) -> Tuple[bool, Type[Exception]]:
        """
        检查文件内容是否符合 项目 要求
        :param content: 要检查的内容
        :return: 如果符合 项目 要求则返回 (True, '成功') 否则返回 (False, 失败信息)
        """

        try:
            content: dict = json.loads(content)
            users = content.get('userAgent')
            head = f'{self.filename} 文件中'
            tail = f', 请参考 README 文件配置'

            assert isinstance(users, list), f'{head}没有存在 userAgent 或 userAgent 不为数组{tail}'

            assert len(users), f'{head} userAgent 未配置任何数据{tail}'

            required = ['lineName', 'stationName', 'timeSlot', 'token', 'name']
            for index, user in enumerate(users):

                # 校验 userAgent 中的数据类型
                assert isinstance(user, dict), f'{head} userAgent 的 item 非对象{tail}'

                # 如果此信息标记为非抢票模式则跳过
                if user.get('shakedown'):
                    continue

                tooltip = f'{user.get("name")} 用户'
                # 校验必填项, 必填项不可为空
                for item in required:
                    value = user.get(item)
                    assert item in user.keys() and value, f'{head} userAgent 的 {tooltip} {item} 未填写或为空{tail}'

                # 校验 Token 是否处于有效期
                assert self._check_token(user.get('token')), f'{head} userAgent 的 {tooltip} Token 已过期{tail}'

            return True, Exception
        except (ValueError, AssertionError) as e:
            logging.debug(f'校验 conf 文件内容失败: {e}')
            return False, e

    def async_task(self) -> None:
        """
        启动异步任务的钩子
        当前启动了 Token 预警通知 和 文件变更钩子
        :return:
        """
        _notification = threading.Thread(target=self.notification, daemon=True)
        _file_change = threading.Thread(target=self._check_file_change, daemon=True)
        _notification.start()
        _file_change.start()

    def run(self):
        """
        执行抢票任务的主入口, 过滤国家法定节假日
        :return:
        """
        # 启动异步程序
        self.async_task()

        # 当天的抢票状态
        ticket = list()

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
            for item in self.subscribe_time:
                runtime = (today + datetime.timedelta(hours=item)).timestamp()
                if time.time() < runtime:
                    start_time = runtime
                    logging.info(f'准备今天 {item} 抢明天的票!')
                    break

            # 如果当前运行时间已经超出了抢票时间则明天运行, 并初始化用户列表
            if start_time is None:
                ticket.clear()  # 当前结束后清空数据
                logging.info('已经错过今天抢票时间, 明天开始抢票~')
                utils.timer(tomorrow.timestamp())
                continue

            logging.debug(f'下次抢票时间为: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}')
            utils.timer(start_time - 10)

            # 启动进程池
            pool = multiprocessing.Pool(self.processes)
            task_result = []
            users = json.loads(self.file_content).get('userAgent')
            for item in users:
                # 如果用户 Token 已经过期则忽略此用户
                if not self._check_token(item.get('token')):
                    continue

                # 如果用户当前已经抢票成功则忽略
                if item.get('name') in ticket:
                    continue

                item['startTime'] = start_time
                result = pool.apply_async(self.task, kwds=item)
                task_result.append(result)

            pool.close()
            pool.join()

            _result = list(map(lambda x: x.get(), task_result))

            for item in _result:

                # 如果存在用户未抢到票, 则重置用户列表, 进行下次尝试
                if item.get('result'):
                    ticket.append(item.get('name'))

                _message = f'{item.get("name")}抢票: {"成功" if item.get("result") else "失败"}'
                logging.info(_message)

                if self.dingtalk:
                    _conf_data = json.loads(self.file_content)
                    _token, _sign = _conf_data.get('dingTalkToken'), _conf_data.get('dingTalkSign')
                    _ding = message.DingTalk(_token, _sign)
                    _ding.text(_message)

    @staticmethod
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

    def notification(self) -> None:
        """
        获取配置文件中的数据并发送钉钉通知
        异步调用此函数, 否则会出现死循环
        :return:
        """

        # 如果未启动 钉钉 则返回
        if not self.dingtalk:
            return

        while True:
            conf: dict = json.loads(self.file_content)
            users = conf.get('userAgent')
            token, sign = conf.get('dingTalkToken'), conf.get('dingTalkSign')
            ding = message.DingTalk(token, sign)

            # 遍历用户列表
            for user in users:
                user_name = user.get('name')
                user_token = user.get('token')

                # shakedown 视为废弃用户, 跳过消息
                if user.get('shakedown'):
                    logging.debug(f'{user_name} shakedown 参数为 True')
                    continue

                # 检查用户是否符合发送条件
                whether = self._check_notification(user_token, user_name)

                # 如果不需要则跳过此用户
                if whether is None:
                    logging.debug(f'{user_name} 不需要发送通知')
                    continue

                ding.text(whether)
                logging.info(whether)

            # 定时器为明天 10 点
            now = datetime.datetime.now()
            today = now - datetime.timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second,
                microseconds=now.microsecond
            )
            tomorrow = (today + datetime.timedelta(days=1, hours=10)).timestamp()
            utils.timer(tomorrow)

    def _check_notification(self, token: str, key: str, default: int = 86400) -> Optional[str]:
        """
        检查是否需要发送通知
        :param token: 需要检查的 token
        :param key: 用户的 Key
        :param default: token 小于 default 后会发送通知
        :return:
        """

        # 如果用户的 Key 不存在于通知容器中则添加
        if key not in self.user_notification:
            logging.debug(f'{key} 没有在用户容器中')
            self.user_notification[key] = None

        # 如果用户容器中的 Key 类型不是 dict 则进行初始化
        if not isinstance(self.user_notification[key], dict):
            logging.debug(f'{key} 用户在容器中未发送过任何通知')
            self.user_notification[key] = dict(
                overdue=True,
                warning=True
            )

        overdue = utils.decode(token)
        if overdue < int(time.time()) and self.user_notification.get(key).get('overdue'):
            self.user_notification[key]['overdue'] = False
            return f'{key} 用户 Token 已过期'
        elif 0 < overdue - int(time.time()) < default and self.user_notification.get(key).get('warning'):
            self.user_notification[key]['warning'] = False
            return f'{key} 用户 Token 将在 {round((overdue - int(time.time())) / 3600, 1)} 小时后过期'

    def _check_file_change(self, interval: float = 5.0) -> None:
        """
        检查文件是否出现变更
        异步调用此函数, 否则会出现死循环
        :return:
        """

        while True:
            # 检查文件内容是否发生变化
            new_content = self._read_file_content()
            if new_content != self.file_content and self._check_content(new_content):
                logging.info('文件发生变化')

                # 处理文件内容变化的逻辑
                self.file_content = new_content
                self.user_notification.clear()

            # 每隔一段时间检查一次文件内容变化
            time.sleep(interval)


__subscribe = '设置抢票时间段, 官方提示为每日12点、20点方法次日预约名额, 默认值为 "12,20" 如需多个时间点请以英文 , 分割'
__processes = '进程池最多同时运行的数量, 默认最多同时启动 5 个线程'
__dingtalk = '是否启动钉钉机器人通知, 启动为 1 , 默认不启动 0, 如需启动请在配置文件中指定钉钉机器人的 webhook 和 sign'
__path = '指定的配置文件路径, 如不指定则使用项目下 conf/conf.json 文件'


@click.command()
@click.option('--subscribe', '-s', help=__subscribe, default='12,20')
@click.option('--processes', '-ps', help=__processes, default=5)
@click.option('--dingtalk', '-dt', help=__dingtalk, default=0)
@click.option('--path', '-p', help=__path, default='')
def command(subscribe: str, processes: int, dingtalk: int, path: str) -> None:
    subscribe = list(map(lambda x: int(x), subscribe.split(',')))
    dingtalk = bool(dingtalk)
    path = path if path else None
    Subway(subscribeTime=subscribe, processes=processes, dingTalk=dingtalk, confPath=path).run()


if __name__ == '__main__':
    command()
