"""排查 ISSUES.md #5：直接用最小场景测试 tool_choice="required" 是否真的
强制百炼模型调用工具，不经过 runner.py/editor.py 这些封装层，隔离变量。
"""
import asyncio

from app.services.agents.client import MODEL, client


async def main():
    messages = [
        {"role": "system", "content": "你是一个吉他编配助手，最终请用 json 格式返回。"},
        {"role": "user", "content": "把这些和弦 ['F#m', 'D', 'A', 'E'] 转成 power chord"},
    ]
    tools = [{
        "type": "function",
        "function": {
            "name": "to_power_chord_batch",
            "description": "批量转换和弦为 power chord",
            "parameters": {
                "type": "object",
                "properties": {"chords": {"type": "array", "items": {"type": "string"}}},
                "required": ["chords"],
            },
        },
    }]
    response = await client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools,
        tool_choice="required", extra_body={"enable_thinking": False},
        response_format={"type": "json_object"},
    )
    msg = response.choices[0].message
    print("finish_reason:", response.choices[0].finish_reason)
    print("tool_calls:", msg.tool_calls)
    print("content:", msg.content)


asyncio.run(main())
