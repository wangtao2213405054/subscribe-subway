# 自动预约北京地铁进站服务

## 1. 简介

这是一个用于自动预约北京市地铁进站服务的程序，用户只需要设置好预约的线路、车站和预计进站时间等信息，程序就能够在预约开放时间内自动完成进站预约申请，并在预约成功后发送通知，提醒用户到达地铁车站。

## 2. 使用说明

### 2.1 准备工作

在使用自动预约程序之前，需要完成以下准备工作：

1. 安装 Python3.6 及以上开发环境。
2. 安装程序所需要的依赖库：requests、click。可通过( python setup.py install )安装所有依赖
3. 打开 [北京地铁预约页面](https://webui.mybti.cn/#/login) 抓取接口 Headers 中的 authorization 字段内容
4. 配置 conf/conf.json 文件或者程序中指定自己的配置文件, 格式如下:
```json
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

### 2.2 运行程序

1. 打开控制台（Terminal）或命令行窗口。
2. 进入程序所在目录的 subway 目录之中，并运行 `python main.py` 命令。(可通过运行 `python main.py --help` 命令查看所需参数)
3. 程序会在预约成功后发送钉钉通知，提醒用户到达地铁车站。

### 2.3 注意事项

- 本程序仅用于测试和学习目的，禁止用于商业用途。
- 请勿滥用进站预约服务，以免影响其他乘客的出行。
- 运行程序前请确认已经安装依赖库和配置好浏览器和驱动程序。
- 程序仅支持预约北京地铁5号线天通苑站、6号线草房站、昌平线沙河站，其他线路不在预约范围内。
- 如有需要，可以根据具体情况修改程序代码，但需要遵守相关法律法规和服务协议。

## 3. 结语

本程序是为方便用户自动预约北京市地铁进站服务而开发的，旨在提高出行效率，减少人员聚集，保障公共安全。用户需要遵守相关法律法规和服务协议，合理使用进站预约服务，共同营造安```
