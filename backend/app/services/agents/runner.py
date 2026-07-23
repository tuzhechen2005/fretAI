"""通用 Agent 执行器：封装 Tool Use 循环，供各个具体 Agent 复用。

设计原则（对应 DECISIONS.md #6）：这里只负责"消息循环"这个机制本身，
不含任何具体业务逻辑——system prompt、tools 列表、要不要用工具，
全部由调用方（各个具体 Agent）传进来决定。
"""
import json

from app.services.agents.client import MODEL, client


async def run_agent_with_tools(
    system_prompt: str,
    user_message: str,
    tools: list[dict],
    tool_functions: dict,
) -> str:
    """跑一次完整的 Tool Use 循环，直到模型给出最终自然语言回复。

    循环而不是只判断一次：模型可能需要连续调用好几轮工具
    （比如先查一个事实，再基于这个事实决定要不要查第二个事实），
    只有当某一轮模型不再请求任何工具时，才算真正拿到了最终答案。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    response = await client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    reply = response.choices[0].message

    while reply.tool_calls:
        messages.append(reply)

        for tool_call in reply.tool_calls:
            args = json.loads(tool_call.function.arguments)
            func = tool_functions[tool_call.function.name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

        response = await client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        reply = response.choices[0].message

    return reply.content
