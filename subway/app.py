# _author: Coke
# _date: 2023/7/10 19:57

import tkinter.messagebox
import customtkinter
import subprocess
import threading
import time
import json
import sys
import os

try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from subway.main import Subway
    from subway import utils
except ImportError as e:
    raise ImportError('请进入项目路径 subscribe-subway/subway 目录运行此脚本')

customtkinter.set_appearance_mode("Dark")  # 设置主题颜色: "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # 设置组件风格: "blue" (standard), "green", "dark-blue"


class APP(customtkinter.CTk):
    """ 主页面视图 """

    WIDTH = 700
    HEIGHT = 450
    APPNAME = '地铁抢票程序'

    def __init__(self):
        super(APP, self).__init__()
        self.subway_threading = None  # 创建抢票线程对象
        self.set_windows()
        self.log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'log.log'))

        # 设置权重
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = SidebarView(self, self.log_path, width=140, corner_radius=0)

        # 设置运行程序按钮
        self.running_button = customtkinter.CTkButton(self, text="运行任务", command=self.run_subway_task)
        self.running_button.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        # 设置日志记录盒
        self.textbox = customtkinter.CTkTextbox(master=self, corner_radius=0, wrap='none', state='normal')
        self.textbox.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.textbox.bind('<KeyPress>', self.disable_textbox)  # 禁用键盘事件
        self.textbox.tag_config("success", foreground="#67C23A")
        self.textbox.tag_config("brand", foreground="#409EFF")
        self.textbox.tag_config("warning", foreground="#E6A23C")
        self.textbox.tag_config("danger", foreground="#F56C6C")
        self.textbox.tag_config("info", foreground="#909399")

    @staticmethod
    def disable_textbox(_):
        """ 禁用日志记录盒键盘输入事件 """
        return "break"

    def set_windows(self):
        """ 设置窗口信息 """
        self.title(self.APPNAME)
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}')
        self.minsize(self.WIDTH, self.HEIGHT)

    def run_subway_task(self):
        """ 运行抢票任务 """
        if self.subway_threading is None or not self.subway_threading.is_alive():
            self.subway_threading = threading.Thread(
                target=Subway(
                    subscribeTime=[12, 20],
                    dingTalk=bool(self.sidebar_frame.dingtalk_switch.get()),
                    app=self.textbox,
                    level=self.sidebar_frame.logger_select.get(),
                    confPath=os.path.abspath(os.path.join(os.path.dirname(__file__), 'conf', 'conf.json')),
                    logConf=os.path.abspath(os.path.join(os.path.dirname(__file__), 'conf', 'log.json')),
                    logPath=self.log_path
                ).run,
                daemon=True
            )
            self.subway_threading.start()
            threading.Thread(target=self.action_listener, daemon=True).start()  # 启动按钮监听事件
        else:
            tkinter.messagebox.showerror('温馨提示', '抢票任务已启动, 请勿重复点击！')

    def action_listener(self):
        """ 启动一个线程来监听线程是否处于运行状态, 并将 UI组件 状态更新 """
        self.running_button.configure(state='disabled')
        self.sidebar_frame.logger_select.configure(state='disabled')
        self.sidebar_frame.dingtalk_switch.configure(state='disabled')
        while True:
            if self.subway_threading is None or not self.subway_threading.is_alive():
                self.running_button.configure(state="normal")
                self.sidebar_frame.logger_select.configure(state='normal')
                self.sidebar_frame.dingtalk_switch.configure(state='normal')
            else:
                self.running_button.configure(state='disabled')
                self.sidebar_frame.logger_select.configure(state='disabled')
                self.sidebar_frame.dingtalk_switch.configure(state='disabled')
            time.sleep(1)


class SidebarView(customtkinter.CTkFrame):
    """ 侧边栏视图 """

    def __init__(self, master: any, log_path, **kwargs):
        super(SidebarView, self).__init__(master, **kwargs)
        self.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        self.log_path = log_path
        # 配置文件窗口
        self.config_window = None

        # 设置侧边栏标题
        self.logo_label = customtkinter.CTkLabel(
            self,
            text="SubwayTkinter",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 设置侧边栏配置文件按钮
        self.config_button = customtkinter.CTkButton(self, text="打开配置", command=self.open_config_window)
        self.config_button.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        # 设置打开详细日志的钩子
        self.logger_button = customtkinter.CTkButton(self, text="详细日志", command=self.open_log_file)
        self.logger_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # 设置是否发送钉钉通知
        self.dingtalk_switch = customtkinter.CTkCheckBox(
            self,
            text='是否发送钉钉通知'
        )
        self.dingtalk_switch.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")

        # 设置日志等级选取
        self.logger_label = customtkinter.CTkLabel(self, text="日志等级:", anchor="w")
        self.logger_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.logger_select = customtkinter.CTkOptionMenu(
            self,
            values=['INFO', 'DEBUG']
        )
        self.logger_select.grid(row=8, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.logger_select.set('INFO')

    def open_config_window(self):
        """ 打开配置文件窗口 """
        if self.config_window is None or not self.config_window.winfo_exists():
            self.config_window = ConfigWindow(self)  # 如果窗口为 None 或已销毁，则创建窗口
        else:
            self.config_window.focus()  # 如果窗口存在则打开他

    def open_log_file(self):
        """ 打开详细日志的钩子 """
        if sys.platform.startswith('win'):
            subprocess.Popen(['start', self.log_path], shell=True)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', self.log_path])
        elif sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', self.log_path])
        else:
            tkinter.messagebox.showerror('温馨提示', '未知的操作系统, 无法打开文件')


class ConfigWindow(customtkinter.CTkToplevel):
    """ 配置文件窗口 """

    WIDTH = 700
    HEIGHT = 450
    NAME = '配置文件'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conf', 'conf.json'))

        # 设置窗口信息
        self.set_windows()
        self.user_index = 1
        # 设置权重
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 设置令牌标签 和 输入框
        self.logger_label = customtkinter.CTkLabel(
            self,
            text="钉钉机器人令牌:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        self.logger_label.grid(row=0, column=0, pady=10)
        self.webhook_input = customtkinter.CTkEntry(
            self,
            placeholder_text="请输入钉钉机器人 Webhook, 不配置此项无法接受钉钉机器人消息推送"
        )
        self.webhook_input.grid(row=0, column=1, columnspan=3, padx=(0, 20), pady=10, sticky="nsew")

        # 设置签名标签 和 输入框
        self.logger_label = customtkinter.CTkLabel(
            self,
            text="钉钉机器人签名:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        self.logger_label.grid(row=1, column=0, pady=10)
        self.sign_input = customtkinter.CTkEntry(
            self,
            placeholder_text="请输入钉钉机器人 Sign, 不配置此项无法接受钉钉机器人消息推送"
        )
        self.sign_input.grid(row=1, column=1, columnspan=3, padx=(0, 20), pady=10, sticky="nsew")

        users = self.update_config_value()

        # 设置 Tab
        self.config_tab = ConfigTabView(self, users)
        self.config_tab.grid(row=2, column=0, rowspan=4, columnspan=4, padx=20, pady=10, sticky="nsew")

        if not users:
            self.command_add_user()

        # 设置删除用户按钮
        self.delete_user = customtkinter.CTkButton(
            self,
            text="删除用户",
            command=self.command_delete_user,
            fg_color='#F56C6C'
        )
        self.delete_user.grid(row=6, column=0, padx=(20, 10), pady=10, sticky="we")

        # 设置添加用户按钮
        self.add_user = customtkinter.CTkButton(
            self,
            text="添加用户",
            command=self.command_add_user,
            fg_color='#67C23A'
        )
        self.add_user.grid(row=6, column=1, padx=10, pady=10, sticky="we")

        # 设置关闭配置文件窗口按钮
        self.channel_button = customtkinter.CTkButton(
            self,
            text="取消",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=self.command_channel_window
        )
        self.channel_button.grid(row=6, column=2, padx=10, pady=10, sticky="we")

        # 设置确认配置按钮
        self.enter_button = customtkinter.CTkButton(
            self,
            text="确认",
            command=self.command_enter_button
        )
        self.enter_button.grid(row=6, column=3, padx=(10, 20), pady=10, sticky="we")

        # print(self.get_config_value())

    def set_windows(self):
        """ 设置窗口信息 """
        self.title(self.NAME)
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}')
        self.minsize(self.WIDTH, self.HEIGHT)

    @property
    def default_json(self) -> dict:
        """ 默认的配置文件 JSON """
        return dict(
            dingTalkToken='',
            dingTalkSign='',
            userAgent=[]
        )

    def update_config_value(self) -> list:
        """ 获取配置文件信息 """

        if not os.path.exists(self.conf_path):
            with open(self.conf_path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(self.default_json, indent=2, ensure_ascii=False))

        with open(self.conf_path, 'r', encoding='utf-8') as file:
            conf = json.loads(file.read())
        self.webhook_input.insert(0, conf.get('dingTalkToken', ''))
        self.sign_input.insert(0, conf.get('dingTalkSign', ''))
        users = conf.get('userAgent', [])
        return users

    def command_delete_user(self):
        """ 删除当前选中的用户 """
        if len(self.config_tab.get_tab_list.keys()) <= 1:
            tkinter.messagebox.showerror('温馨提示', '至少保留一位用户哦~')
            return

        current_tab = self.config_tab.get()

        # 控制展示的 Tab, 如果当前 tab 是最后一个则展示他的前一个 tab 如果非最后一个则展示其后面的一个tab
        name_list = self.config_tab.get_name_list
        index = name_list.index(current_tab)
        if index == len(name_list) - 1:
            self.config_tab.set(name_list[-2])
        else:
            self.config_tab.set(name_list[index + 1])

        self.config_tab.delete(current_tab)

    def command_add_user(self):
        """ 添加用户的钩子 """
        if len(self.config_tab.get_tab_list.keys()) >= 5:
            tkinter.messagebox.showinfo('温馨提示', '最多添加五位用户~')
            return

        default = f'新用户 {self.user_index}'
        # 如果不存在与列表中则进行添加, 如果存在则将 Tab 切换至指定标签页
        if default not in self.config_tab.get_tab_list.keys():
            self.config_tab.add(default)
            self.config_tab.set_tab_view(default)
            self.config_tab.set(default)
            self.user_index += 1
        else:
            self.config_tab.set(default)

    def command_channel_window(self):
        """ 取消按钮的钩子 """
        if self.winfo_exists():
            self.destroy()

    def command_enter_button(self):
        """ 确认按钮的钩子 """
        # 获取 Tabs 数据并验证其完整性
        content = self.config_tab.get_tabs_value()
        check = self._check_config(content)
        if check:
            tkinter.messagebox.showerror('温馨提示', check)
            return

        # 将验证完成的数据写入 Json 文件中
        with open(self.conf_path, 'w', encoding='utf-8') as file:
            write_data = dict(
                dingTalkToken=self.webhook_input.get(),
                dingTalkSign=self.sign_input.get(),
                userAgent=content
            )
            file.write(json.dumps(write_data, indent=2, ensure_ascii=False))

        # 关闭弹窗
        if self.winfo_exists():
            self.destroy()

    @staticmethod
    def _check_config(users):
        """ 检查配置列表是否正确, 如果正确则返回 None 否则返回失败信息 """
        required = dict(
            name='用户名称',
            lineName='预约线路',
            stationName='预约站点',
            timeSlot='预约时间',
            token='地铁令牌'
        )
        for user in users:
            # 如果此信息标记为非抢票模式则跳过
            if user.get('shakedown'):
                continue

            tooltip = f'{user.get("name")}'
            # 校验必填项, 必填项不可为空
            for key, value in required.items():
                required_value = user.get(key)
                if key not in user.keys() or not required_value:
                    return f'{tooltip} {value} 未填写'

            # 校验 Token 是否处于有效期
            if utils.decode(user.get('token')) < int(time.time()):
                return f'{tooltip} Token 不正确或已过期'


class ConfigTabView(customtkinter.CTkTabview):
    """ 配置文件标签视图 """

    def unbind(self, sequence=None, funcid=None): ...

    def bind(self, sequence=None, command=None, add=None): ...

    def __init__(self, master, users, **kwargs):
        super(ConfigTabView, self).__init__(master, **kwargs)
        self.users = users
        self.update_users_tab()
        self.time_interval = utils.time_interval()

        # 为 Tabs 设置 UI
        for tab in self.get_tab_list.keys():
            user = list(filter(lambda x: x.get('name') == tab, users))[0]
            self.set_tab_view(tab, user)

    def handle_focusout(self, _):
        """ 用户名称输入框聚焦结束后的钩子, 当用户名称改变时调用这个钩子 """
        # name = self.get_tab_list.get(self.get()).username_input.get()
        # self._segmented_button._buttons_dict.get(self.get()).configure(text=name)

    def set_tab_view(self, tab: str, user: dict = None):
        """ 这是 Tab 中的视图信息 """

        if user is None:
            user = {}

        tab_frame = self.tab(tab)  # 获取 Tab 的 <customtkinter.CTkFrame> 对象

        # 设置网格权重
        tab_frame.grid_columnconfigure(3, weight=1)
        tab_frame.grid_rowconfigure(3, weight=0)

        # 设置用户名称 和 输入框
        tab_frame.username_label = customtkinter.CTkLabel(
            tab_frame,
            text="用户名称:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        tab_frame.username_label.grid(row=0, column=0, padx=(20, 10), pady=10)
        tab_frame.username_input = customtkinter.CTkEntry(
            tab_frame,
            placeholder_text="请输入用户名称, 多个用户请保持唯一"
        )
        tab_frame.username_input.grid(row=0, column=1, columnspan=3, padx=(0, 20), pady=10, sticky="nsew")
        tab_frame.username_input.insert(0, tab)
        # 原生组件是通过name为 key 的, 所以会导致更新的错误, 除非重写其组件
        # tab_frame.username_input.bind("<FocusOut>", self.handle_focusout)

        # 设置地铁令牌 和 输入框
        tab_frame.token_label = customtkinter.CTkLabel(
            tab_frame,
            text="地铁令牌:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        tab_frame.token_label.grid(row=1, column=0, padx=(20, 10), pady=10)
        tab_frame.token_input = customtkinter.CTkEntry(
            tab_frame,
            placeholder_text="请输入北京地铁预约中的 Authorization 字段"
        )
        tab_frame.token_input.grid(row=1, column=1, columnspan=3, padx=(0, 20), pady=10, sticky="nsew")
        if user.get('token'):
            tab_frame.token_input.insert(0, user.get('token'))

        # 设置地铁线路 和 选项卡
        tab_frame.line_label = customtkinter.CTkLabel(
            tab_frame,
            text="地铁站点:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        line_list = ['昌平线-沙河站', '5号线-天通苑站', '6号线-草房站']
        tab_frame.line_label.grid(row=2, column=0, padx=(20, 10), pady=10)
        tab_frame.line_select = customtkinter.CTkOptionMenu(
            tab_frame,
            values=line_list
        )
        select_item = f'{user.get("lineName")}-{user.get("stationName")}'
        if select_item in line_list:
            tab_frame.line_select.set(select_item)

        tab_frame.line_select.grid(row=2, column=1, columnspan=2, padx=(0, 20), pady=10, sticky="ew")

        # 设置预约时间 和 选项卡
        tab_frame.time_label = customtkinter.CTkLabel(
            tab_frame,
            text="进站时间:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        tab_frame.time_label.grid(row=3, column=0, padx=(20, 10), pady=10)
        tab_frame.time_select = customtkinter.CTkOptionMenu(
            tab_frame,
            values=list(self.time_interval.keys())
        )
        tab_frame.time_select.grid(row=3, column=1, columnspan=2, padx=(0, 20), pady=10, sticky="ew")
        time_list = [key for key, value in self.time_interval.items() if value == user.get('timeSlot')]
        if time_list:
            tab_frame.time_select.set(time_list[0])

        # 设置是否抢票 和 输入框
        tab_frame.shakedown_label = customtkinter.CTkLabel(
            tab_frame,
            text="用户屏蔽:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor='w'
        )
        tab_frame.shakedown_label.grid(row=4, column=0, padx=(20, 10), pady=10)
        tab_frame.shakedown_switch = customtkinter.CTkSwitch(
            tab_frame,
            text="是否屏蔽此用户(开启后此用户将不会参与抢票等活动)"
        )
        tab_frame.shakedown_switch.grid(row=4, column=1, columnspan=3, padx=(0, 20), pady=10, sticky="nsew")
        tab_frame.shakedown_switch.select() if user.get('shakedown') else tab_frame.shakedown_switch.deselect()

        return tab_frame

    @property
    def get_tab_list(self) -> dict:
        """ 获取当前所有的标签页 """
        return self._tab_dict

    @property
    def get_name_list(self) -> list:
        """ 返回当前Tab列表(有序) """
        return self._name_list

    def update_users_tab(self):
        """ 将用户信息更新到 Tab 中 """

        for user in self.users:
            name = user.get('name')
            if name not in self.get_tab_list.keys():
                self.add(name)

    def get_tab_value(self, tab) -> dict:
        """ 获取 Tab 中的数据信息 """

        if isinstance(tab, str):
            tab = self.tab(tab)

        line, station = tab.line_select.get().split('-')

        return dict(
            lineName=line,
            stationName=station,
            timeSlot=self.time_interval.get(tab.time_select.get()),
            name=tab.username_input.get(),
            shakedown=bool(tab.shakedown_switch.get()),
            token=tab.token_input.get()
        )

    def get_tabs_value(self) -> list:
        """ 获取当前 Tabs 中的所有数据 """
        return [self.get_tab_value(item) for item in self.get_tab_list.values()]


if __name__ == '__main__':
    _app = APP()
    _app.mainloop()
