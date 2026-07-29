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
from app.schemas.trace import AgentTrace
from app.services.agents.runner import run_agent_with_tools
from app.services.tools.transpose import transpose_progression
from app.services.tools.power_chord import to_power_chord_batch

SYSTEM_PROMPT = """你是一个吉他编配修改助手。用户会给你当前的和弦进行，
以及一句修改要求（比如"降两调"或"改成 power chord"）。

你有两个工具可以用：
1. transpose_progression：把整组和弦一次性转调
2. to_power_chord_batch：把整组和弦一次性转成 power chord

两个工具都是一次调用处理整个和弦列表，不需要、也不应该对每个和弦分别调用一次。
把用户消息里给出的完整和弦进行整理成数组，一次性传给对应工具。

调用完工具后，把最终结果整理成 json 返回，格式：
{"new_chords": ["新和弦1", "新和弦2", ...], "explanation": "一句话说明你做了什么"}
"""

transpose_tool_schema = {
    "type": "function",
    "function": {
        "name": "transpose_progression",
        "description": "把一组和弦整体升高或降低若干个半音，和弦性质（大三/小三等）保持不变。一次调用处理整个列表。",
        "parameters": {
            "type": "object",
            "properties": {
                "chords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要转调的完整和弦列表，比如 ['F#m', 'D', 'A', 'E']",
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

power_chord_batch_tool_schema = {
    "type": "function",
    "function": {
        "name": "to_power_chord_batch",
        "description": "把一组和弦一次性转换成对应的 power chord（根音+五度音），返回每个和弦的显示名、指法和把位。一次调用处理整个列表，不要逐个和弦分别调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "chords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要转换的完整和弦列表，比如 ['F#m', 'D', 'A', 'E']",
                },
                "prefer_position": {
                    "type": ["integer", "null"],
                    "description": "用户指定的目标品格附近位置，比如'5品附近'就传5；用户没提具体数字就传null",
                },
            },
            "required": ["chords"],
        },
    },
}


async def apply_edit(arrangement: Arrangement, message: str) -> tuple[Arrangement, str, AgentTrace]:
    """返回 (新编配, Agent 回复文本, trace)。"""
    original_chords = [c.original for c in arrangement.chords]
    user_message = f"当前和弦进行：{original_chords}\n修改要求：{message}"

    trace = await run_agent_with_tools(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=[transpose_tool_schema, power_chord_batch_tool_schema],
        tool_functions={
            "transpose_progression": transpose_progression,
            "to_power_chord_batch": to_power_chord_batch,
        },
        response_format={"type": "json_object"},
        force_tool_use=True,
    )
    result = json.loads(trace.final_content)

    # 从 trace 里找最近一次 to_power_chord_batch 调用的真实结果（指法、把位），
    # 而不是靠 LLM 转述的和弦名字符串反推——避免"调用一次工具、组装时又重新查一次"的重复劳动，
    # 也避免依赖 LLM 老实转述数字（呼应 ISSUES.md #5：不能假设模型转述的细节可信）。
    #
    # 按调用顺序直接配对，不用和弦名字符串做字典 key 匹配：
    # tc.result[i] 就是 tc.arguments["chords"][i] 的转换结果，这是 API 调用本身
    # 保证的对应关系，不依赖"模型转述时是否保持了原始顺序"这类假设——
    # 用 tc.arguments（工具真实收到的输入）而不是 original_chords（编配原始列表）
    # 来配对，即使两者理论上应该一致，也不必依赖这个假设成立。
    power_chord_call = None
    for step in trace.steps:
        for tc in step.tool_calls:
            if tc.tool_name == "to_power_chord_batch":
                power_chord_call = tc

    if power_chord_call:
        new_chords = [
            ArrangedChord(
                original=original,
                display=power["display"], fingering=power["fingering"], position=power["position"],
            )
            for original, power in zip(power_chord_call.arguments["chords"], power_chord_call.result)
        ]
    else:
        new_chords = [ArrangedChord(original=chord, display=chord, fingering="", position=0)
                      for chord in result["new_chords"]]

    new_arrangement = arrangement.model_copy(update={"chords": new_chords, "notes": result["explanation"]})

    return new_arrangement, result["explanation"], trace

