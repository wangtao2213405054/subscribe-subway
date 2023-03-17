# subscribe-subway
北京地铁进站预约程序

---
# 描述
定时预约进站码, 可以在后台一直运行, 并会过滤法定节假日

如果配置了 钉钉机器人消息通知 则会通知 Token 到期时间及抢票结果

程序运行后如果在 12 点 未抢到票则会在 20 点继续抢

---
# 使用教程
1. 打开 [北京地铁预约页面](https://webui.mybti.cn/#/login)
2. 登陆需要抢票的用户
3. 打开浏览器检查模式(右击检查(Inspect)或快捷键(windows: Ctrl + Shift + i, mac: Command + Shift + i ))
4. 切換至网络, 在网站中切换底部 Tab 后查看请求的接口, 抓取接口 Headers 中的 authorization 字段
5. 将抓取的 authorization 内容配置到conf/conf.json文件的 Token 中, 配置格式如下:
```angular2html
{
  "dingTalkToken": "",
  "dingTalkSign": "",
  "UserAgent": [
    {
      "lineName": "昌平线",
      "stationName": "沙河站",
      "timeSlot": "0720-0730",
      "name": "Coke",
      "mobile": "18888888888",
      "token": "EFGHZDBhMTEtMmM2MC00OGI2LTg3MGMtNjE3N2Q0NjlhNjIxLDE2MTA5NzE3MDUwOTIsTXFIeHlKb2JMRFovSTcrQnpPNFRkdXhzSTc4PQ=="
    },
    {
      "lineName": "昌平线",
      "stationName": "沙河站",
      "timeSlot": "0750-0800",
      "name": "CokeTwo",
      "mobile": "18888888888",
      "token": "EFGHZDBhMTEtMmM2MC00OGI2LTg3MGMtNjE3N2Q0NjlhNjIxLDE2MTA5NzE3MDUwOTIsTXFIeHlKb2JMRFovSTcrQnpPNFRkdXhzSTc4PQ=="
    }
  ]
}
```
# 参数解析
```python
dingTalkToken = ""  # 钉钉机器人的 webhook
dingTalkSign = ""  # 钉钉机器人的加签密钥
UserAgent = []  # 需要抢票的用户列表
lineName = "昌平线"  # 要抢票的线路, 可选值: 昌平线、5号线、6号线
stationName = "沙河站"  # 要抢票的站点, 可选择: 沙河站、天通苑站、草房站
timeSlot = "0750-0800"  # 抢票时段, 如早上6:30 ~ 6:40 则需要输入 0630-0640
name = "name"  # 这是一个列表的 Key, 当存在多个抢票用户时, 可根据此 Key 来区分用户
mobile = "18888888888"  # 手机号, 预留字段, 可忽略
token = ""  # token 对应了地铁预约程序的 authorization 字段
```
---
1. 配置文件可以修改, 或可自己创建文件保持目录结构即可
2. `run()` 函数中可以通过 `confPath` 参数来指定自己的配置文件路径, 不指定默认为conf/conf.json 文件
3. 支持钉钉机器人通知, 需要配置钉钉机器人的 webhook 和 sign, 并且需要将 `run()` 函数中的 `dingTalk` 设置为 True
```python
run(confPath='confPath.json', dingTalk=True)
```
# 构建包
1. 运行 `python setup.py sdist`
2. 安装包构建完成后会在dist 目录下生成一个`subscribe-subway-capital*.tar.gz`文件
3. 使用 `pip install subscribe-subway-capital*.tar.gz`即可
4. 导入使用
```python
import subway


if __name__ == '__main__':
    subway.run(confPath='', dingTalk=True)
```