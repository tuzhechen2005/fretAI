import asyncio
import json
from app.services.agents.client import client, MODEL


async def main():
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个助手，必须只返回 JSON，不要有任何其他文字。格式：{\"answer\": \"...\"}",
            },
            {"role": "user", "content": "1+1等于几？"},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    print("原始返回内容:", content)

    parsed = json.loads(content)
    print("解析后的字典:", parsed)


asyncio.run(main())
