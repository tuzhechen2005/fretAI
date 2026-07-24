"""自然语言修改编配（产品文档 §9.2、§10.2-11）。

第一版范围裁剪：只支持"转调"和"改成 power chord"这两种指令类型。

LLM 将用户指令解析为结构化操作（tool use），再调用规则系统执行：
    "降两调"            -> transpose(semitones=-2)
    "换到低把位"        -> optimize_positions(prefer_position=0..3)
    "改成 power chord"  -> to_power_chord(...)
    "不要大横按"        -> optimize_positions(avoid_barre=True)
最后返回新 Arrangement + 修改说明。
"""

import json

from app.schemas.arrangement import Arrangement, ArrangedChord
from app.services.agents.runner import run_agent_with_tools
from app.services.tools.transpose import transpose_progression
from app.services.tools.power_chord import to_power_chord

SYSTEM_PROMPT = """你是一个吉他编配修改助手。用户会给你当前的和弦进行，
以及一句修改要求（比如"降两调"或"改成 power chord"）。

你有两个工具可以用：
1. transpose_progression：整体升降调
2. to_power_chord：把某个和弦转成 power chord（需要对每个和弦分别调用）

调用完工具后，把最终结果整理成 JSON 返回，格式：
{"new_chords": ["新和弦1", "新和弦2", ...], "explanation": "一句话说明你做了什么"}
"""

transpose_tool_schema = {
    "type": "function",
    "function": {
        "name": "transpose_progression",
        "description": "把一组和弦整体升高或降低若干个半音，和弦性质（大三/小三等）保持不变",
        "parameters": {
            "type": "object",
            "properties": {
                "chords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要转调的和弦列表，比如 ['F#m', 'D', 'A', 'E']",
                },
                "semitones": {
                    "type": "integer",
                    "description": "升降的半音数，正数表示升高，负数表示降低，比如降两调是 -4",
                },
            },
            "required": ["chords", "semitones"],
        },
    },
}

power_chord_tool_schema = {
    "type": "function",
    "function": {
        "name": "to_power_chord",
        "description": "把一个和弦转换成对应的 power chord（根音+五度音），返回显示名、指法和把位",
        "parameters": {
            "type": "object",
            "properties": {
                "chord": {
                    "type": "string",
                    "description": "要转换的和弦名，比如 F#m、C、Am",
                },
            },
            "required": ["chord"],
        },
    },
}

def _build_arranged_chord(chord: str) -> ArrangedChord:
    if chord.endswith("5"):
        root = chord[:-1]
        power = to_power_chord(root)
        return ArrangedChord(
            original=chord, display=power["display"],
            fingering=power["fingering"], position=power["position"],
        )
    return ArrangedChord(original=chord, display=chord, fingering="", position=0)


async def apply_edit(arrangement: Arrangement, message: str) -> tuple[Arrangement, str]:
    """返回 (新编配, Agent 回复文本)。"""
    original_chords = [c.original for c in arrangement.chords]
    user_message = f"当前和弦进行：{original_chords}\n修改要求：{message}"

    reply = await run_agent_with_tools(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=[transpose_tool_schema, power_chord_tool_schema],
        tool_functions={
            "transpose_progression": transpose_progression,
            "to_power_chord": to_power_chord,
        },
        response_format={"type": "json_object"},
    )
    result = json.loads(reply)

    new_chords = [_build_arranged_chord(chord) for chord in result["new_chords"]]

    new_arrangement = arrangement.model_copy(update={"chords": new_chords, "notes": result["explanation"]})

    return new_arrangement, result["explanation"]

