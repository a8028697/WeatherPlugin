# Please refer to https://docs.langbot.app/en/plugin/dev/tutor.html for the
# LangBot plugin event listener format this file follows.
from __future__ import annotations

import aiohttp

from langbot_plugin.api.definition.components.common.event_listener import EventListener
from langbot_plugin.api.entities import events, context
from langbot_plugin.api.entities.builtin.platform import message as platform_message


# ========== 配置区，按需修改 ==========

# 在 https://opendata.cwa.gov.tw 注册后申请到的 Authorization Key
# 格式类似 "CWA-B7821276-0E1F-4023-919D-AB106FC88BC2"
CWA_API_KEY = "请填入你申请到的 CWA Authorization Key"

# 触发关键词前缀，比如输入 "天气 臺北市" 或 "天气 高雄市"
TRIGGER_PREFIX = "天气"

# 36小时天气预报数据集代号（据我所知目前是 F-C0032-001，
# 建议先用你的 Key 手动请求一次确认这个代号仍然有效）
DATASET_ID = "F-C0032-001"

CWA_API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATASET_ID}"

# =======================================


def _extract_text(message_chain) -> str:
    try:
        parts = []
        for comp in message_chain:
            text = getattr(comp, "text", None)
            if text:
                parts.append(text)
        return "".join(parts).strip()
    except Exception:
        return ""


async def _query_weather(location_name: str) -> str:
    """请求 CWA 36 小时天气预报，返回格式化好的文字。"""
    params = {
        "Authorization": CWA_API_KEY,
        "format": "JSON",
        "locationName": location_name,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CWA_API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return f"请求气象署 API 失败，状态码：{resp.status}"
                data = await resp.json()
    except Exception as e:
        return f"请求气象署 API 时发生错误：{e}"

    try:
        locations = data["records"]["location"]
        if not locations:
            return f"查不到「{location_name}」的天气资料，请确认地名是否正确（需使用官方全名，例如：臺北市、高雄市）。"

        loc = locations[0]
        elements = {el["elementName"]: el["time"] for el in loc["weatherElement"]}

        wx = elements.get("Wx", [{}])[0].get("parameter", {}).get("parameterName", "未知")
        min_t = elements.get("MinT", [{}])[0].get("parameter", {}).get("parameterName", "?")
        max_t = elements.get("MaxT", [{}])[0].get("parameter", {}).get("parameterName", "?")
        pop = elements.get("PoP", [{}])[0].get("parameter", {}).get("parameterName", "?")

        return (
            f"【{loc['locationName']}】未来预报\n"
            f"天气现象：{wx}\n"
            f"气温：{min_t}°C ~ {max_t}°C\n"
            f"降雨机率：{pop}%\n"
            f"（数据来源：中央气象署气象资料开放平台）"
        )
    except Exception as e:
        return f"解析气象署 API 返回数据时出错：{e}\n（可能是数据集字段有变动，需要检查 API 文档）"


class DefaultEventListener(EventListener):

    async def initialize(self):
        await super().initialize()

        @self.handler(events.PersonMessageReceived)
        async def on_person_message(event_context: context.EventContext):
            await self._handle(event_context)

        # 如果需要在群聊里也能触发，需自行核实事件类名后取消注释：
        # @self.handler(events.GroupMessageReceived)
        # async def on_group_message(event_context: context.EventContext):
        #     await self._handle(event_context)

    async def _handle(self, event_context: context.EventContext):
        msg_chain = getattr(event_context.event, "message_chain", None)
        text = _extract_text(msg_chain) if msg_chain is not None else ""

        if not text.startswith(TRIGGER_PREFIX):
            return

        location_name = text[len(TRIGGER_PREFIX):].strip()
        if not location_name:
            await event_context.reply(
                platform_message.MessageChain([
                    platform_message.Plain(text=f"请在「{TRIGGER_PREFIX}」后面加上地名，例如：{TRIGGER_PREFIX} 臺北市"),
                ])
            )
            return

        if CWA_API_KEY.startswith("请填入"):
            await event_context.reply(
                platform_message.MessageChain([
                    platform_message.Plain(text="还没有配置 CWA API Key，请先在插件代码里填入你申请到的 Authorization Key。"),
                ])
            )
            return

        reply_text = await _query_weather(location_name)

        await event_context.reply(
            platform_message.MessageChain([
                platform_message.Plain(text=reply_text),
            ])
        )
