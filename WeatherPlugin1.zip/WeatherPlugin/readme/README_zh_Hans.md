# 天气插件

发送「天气 地名」即可查询台湾中央气象署 36 小时天气预报，例如：
`天气 臺北市`

## 使用前设置

1. 前往 https://opendata.cwa.gov.tw 注册账号并申请免费的 Authorization API Key
2. 打开 `components/event_listener/default.py`，把 `CWA_API_KEY` 改成你申请到的 key
3. 地名需要使用中央气象署的官方全名（繁体），例如：臺北市、高雄市、臺中市，
   简体或简称可能查不到结果

## 有不确定性的地方

数据集代号 `F-C0032-001` 以及字段名（`Wx`、`MinT`、`MaxT`、`PoP`）是基于
通用知识写的，没有做过实时核实。如果回复出现"解析数据出错"，需要去查一下
气象署当前的 API 文档，确认这个数据集的实际字段名是否有变化，再调整
`components/event_listener/default.py` 里的解析部分。
