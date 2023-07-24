# _author: Coke
# _date: 2023/7/24 14:00

from subway import Subway

import threading
import json


class RewriteSubway(Subway):
    """ 线程抢票 """

    def start_task(self, start_time: float) -> list:
        """
        通过线程启动任务
        :param start_time:
        :return:
        """

        task_result = []
        subway_result = []
        for item in json.loads(self.file_content).get('userAgent'):

            _continue = self.task_continue(item)
            if _continue:
                continue

            item['startTime'] = start_time
            item['level'] = self.logger_level
            item['logPath'] = self.log_path
            item['logConf'] = self.log_conf
            result = threading.Thread(
                target=self.task,
                kwargs=dict(
                    kwargs=item,
                    subway_result=subway_result
                )
            )
            result.start()
            task_result.append(result)

        for thread in task_result:
            thread.join()

        return subway_result
