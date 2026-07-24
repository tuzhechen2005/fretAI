import asyncio
import json

from app.services.agents.fingering import SYSTEM_PROMPT
from app.services.agents.runner import run_agent_with_tools


async def main():
    chords = ["F#m", "D", "A", "E"]
    user_message = f"和弦进行：{chords}\n用户要求：改成 5 品附近的 power chord，不要大跳"

    reply = await run_agent_with_tools(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=[],
        tool_functions={},
        response_format={"type": "json_object"},
    )
    print("原始 LLM 返回:", reply)
    parsed = json.loads(reply)
    print("解析后的 prefer_position:", parsed["prefer_position"])


asyncio.run(main())
