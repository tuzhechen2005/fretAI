"""Fingering Agent（产品文档 §7.4）。

第一版范围裁剪：只支持"调整 power chord 换把位"这一种场景
（其他请求类型如"换开放和弦把位"暂不支持，诚实告知用户）。
"""
import json

from app.schemas.arrangement import ArrangedChord
from app.schemas.trace import AgentTrace
from app.services.agents.runner import run_agent_with_tools
from app.services.tools.power_chord import to_power_chord

SYSTEM_PROMPT = """你是一个吉他指法调整助手。用户会给你一段和弦进行，
以及一句自然语言要求（比如"5 品附近，不要大跳"）。

你的任务：
1. 判断这个要求是不是关于"调整 power chord 的把位"。
2. 如果是，从用户的话里提取出一个大概的目标品格数字（prefer_position）。
   如果用户没提到具体数字（比如只说"低把位"），你可以给一个合理的估计
   （比如"低把位"约等于 0-3 品，"5 品附近"就是 5）。
3. 如果用户的要求不是关于 power chord 换把位（比如要求换开放和弦的指法），
   设置 supported 为 false。

只返回 JSON，格式：
{"supported": true/false, "prefer_position": 数字或null, "explanation": "一句话说明"}
"""


async def optimize_fingering(
    chords: list[str],
    user_request: str,
) -> tuple[list[ArrangedChord] | None, str, AgentTrace]:
    """返回 (优化后的指法列表, 说明文本, trace)。如果请求不被支持，指法列表是 None。"""
    user_message = f"和弦进行：{chords}\n用户要求：{user_request}"

    trace = await run_agent_with_tools(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=[],
        tool_functions={},
        response_format={"type": "json_object"},
    )
    parsed = json.loads(trace.final_content)

    if not parsed["supported"]:
        return None, parsed["explanation"], trace

    prefer_position = parsed["prefer_position"]
    arranged_chords = [
        ArrangedChord(
            original=chord,
            display=(power := to_power_chord(chord, prefer_position=prefer_position))["display"],
            fingering=power["fingering"],
            position=power["position"],
        )
        for chord in chords
    ]

    return arranged_chords, parsed["explanation"], trace
