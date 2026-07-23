"""Music Theory Agent（产品文档 §7.2）。

对音频识别结果做乐理层面纠错：
1. 判断和弦是否符合调性，不符合时给出借用/属和弦解释或修正建议。
2. 结合前后进行修正低置信度和弦。
3. 根据贝斯音判断 slash chord。
输出仍是 ChordEvent 列表，只更新 chord / candidates / reason 字段。
"""
import json

from app.schemas.song import ChordEvent
from app.services.agents.runner import run_agent_with_tools
from app.services.tools.theory import get_diatonic_chords

SYSTEM_PROMPT = """你是一个吉他乐理专家，负责检查一首歌的和弦识别结果是否符合乐理逻辑。

你有一个工具可以查询某个大调的调内自然和弦（7 个音级）。

任务：
1. 对每个和弦，判断它是否是当前调性的调内和弦。
2. 如果不是调内和弦，结合前后的和弦进行，判断这是：
   - 识别错误（原始识别可能出错，应该修正成什么）
   - 还是合理的乐理现象（比如借用和弦、属和弦），不需要修改
3. 只有你判断"原始识别确实可能出错"时，才提出修正建议。

最后只返回 JSON，格式：
{"corrections": [{"index": 数字, "chord": "修正后的和弦", "reason": "一句话原因"}]}
如果没有需要修正的，返回 {"corrections": []}
"""

diatonic_tool_schema = {
    "type": "function",
    "function": {
        "name": "get_diatonic_chords",
        "description": "给定大调调性，返回这个调内的 7 个自然和弦（按级数 I 到 vii°排列）",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "调性，比如 'G major'"},
            },
            "required": ["key"],
        },
    },
}


async def review_chords(key: str, chords: list[ChordEvent]) -> list[ChordEvent]:
    chord_list_text = "\n".join(
        f"{i}: {c.chord}（置信度 {c.confidence}）" for i, c in enumerate(chords)
    )
    user_message = f"调性：{key}\n和弦进行：\n{chord_list_text}"

    reply = await run_agent_with_tools(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=[diatonic_tool_schema],
        tool_functions={"get_diatonic_chords": get_diatonic_chords},
        response_format={"type": "json_object"},
    )

    result = json.loads(reply)

    for correction in result["corrections"]:
        index = correction["index"]
        if index < 0 or index >= len(chords):
            continue  # 越界，跳过这条不合理的修正
        chords[index].chord = correction["chord"]
        chords[index].reason = correction["reason"]

    return chords
