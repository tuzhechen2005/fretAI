import asyncio
from app.services.agents.runner import run_agent_with_tools
from app.services.rules.capo import recommend_capo


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
        system_prompt="你是一个吉他乐理助手，请你根据现有工具列表，并且根据用户提问，返回最适合用户的指法",
        user_message="这首歌是 Ab major 调，和弦是 Ab、Db、Eb，帮我推荐一下怎么用 capo 弹更简单",
        tools=[capo_tool_schema],
        tool_functions={"recommend_capo": recommend_capo},
    )
    print(reply)


asyncio.run(main())