"""Tool Use 最小可行验证：只接一个工具（to_power_chord），
跑通"模型决策调用 -> 我们真正执行 -> 把结果喂回模型 -> 模型给出最终回复"这一整套流程。
先跑通这一个工具，验证机制通了，再考虑要不要接更多工具、加更多参数。
"""
import asyncio
import json

from app.services.agents.client import client, MODEL
from app.services.rules.power_chord import to_power_chord
from app.services.rules.capo import recommend_capo


tools = [
    {
        "type": "function",
        "function": {
            "name": "to_power_chord",
            "description": "将任意和弦转换成对应的 power chord（根音+五度音），返回显示名、指法和把位",
            "parameters": {
                "type": "object",
                "properties": {
                    "chord": {
                        "type": "string",
                        "description": "要转换的和弦名，比如 F#m、C、Am",
                    }
                },
                "required": ["chord"],
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "recommend_capo",
        "description": "给出0-7把位不同capo的指法方案，返回推荐方案", 
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "原歌曲的调性", 
                },
                "chords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "原歌曲的和弦", 
                }
            },
            "required": ["key", "chords"],
        },
    },
}

]

TOOL_FUNCTIONS = {
    "to_power_chord": to_power_chord,
    "recommend_capo": recommend_capo,  # 提示：跟上面那行格式一样
}


async def main():
    messages = [
        {
            "role": "user",
            "content": "这首歌是 Ab major 调，和弦是 Ab、Db、Eb，帮我推荐一下怎么用 capo 弹更简单",
        }
    ]

    # 第一次调用：把工具清单和用户的话一起发给模型，让它自己决定要不要用工具
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
    )
    reply = response.choices[0].message
    print("=== 模型第一次的回复 ===")
    print(reply)

    if not reply.tool_calls:
        print("模型没有选择调用工具，直接回复了：", reply.content)
        return

    # 模型决定要调用某个工具，把这次"决策"也加进对话历史
    messages.append(reply)

    for tool_call in reply.tool_calls:
        print("\n=== 模型请求调用的工具 ===")
        print("工具名:", tool_call.function.name)
        print("参数:", tool_call.function.arguments)

        # 真正执行工具（这一步 LLM 从头到尾都没有真的跑代码，是我们自己在跑）
        args = json.loads(tool_call.function.arguments)
        func = TOOL_FUNCTIONS[tool_call.function.name] 
        result = func(**args)
        print("真实执行结果:", result)

        # 把执行结果作为一条新消息加回对话历史，role 是 "tool"
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )

    # 第二次调用：带着工具执行结果，再问一次模型，让它给出面向用户的最终回复
    final_response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
    )
    print("\n=== 模型的最终回复 ===")
    print(final_response.choices[0].message.content)


asyncio.run(main())
