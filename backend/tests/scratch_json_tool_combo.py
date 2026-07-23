import asyncio
from app.services.agents.runner import run_agent_with_tools
from app.services.tools.capo import recommend_capo

capo_tool_schema = {
    "type": "function",
    "function": {
        "name": "recommend_capo",
        "description": "给出0-7品不同capo的指法方案，返回推荐方案",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "原歌曲的调性"},
                "chords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "原歌曲的和弦",
                },
            },
            "required": ["key", "chords"],
        },
    },
}


async def main():
    reply = await run_agent_with_tools(
        system_prompt=(
            "你是一个吉他乐理助手。请调用工具获取 capo 推荐方案，"
            '然后只返回 JSON，格式为 {"best_capo": 数字, "reason": "一句话原因"}，不要有任何其他文字。'
        ),
        user_message="这首歌是 Ab major 调，和弦是 Ab、Db、Eb，帮我推荐一下怎么用 capo 弹更简单",
        tools=[capo_tool_schema],
        tool_functions={"recommend_capo": recommend_capo},
        response_format={"type": "json_object"},
    )
    print("原始返回:", reply)

    import json
    parsed = json.loads(reply)
    print("解析后:", parsed)


asyncio.run(main())
