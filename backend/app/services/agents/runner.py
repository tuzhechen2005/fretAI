"""通用 Agent 执行器：封装 Tool Use 循环，供各个具体 Agent 复用。

设计原则（对应 DECISIONS.md #6）：这里只负责"消息循环"这个机制本身，
不含任何具体业务逻辑——system prompt、tools 列表、要不要用工具，
全部由调用方（各个具体 Agent）传进来决定。
"""
import json

from app.schemas.trace import AgentTrace, ToolCallRecord, TraceStep
from app.services.agents.client import MODEL, client


async def run_agent_with_tools(
    system_prompt: str,
    user_message: str,
    tools: list[dict],
    tool_functions: dict,
    response_format: dict | None = None,
    force_tool_use: bool = False,
) -> AgentTrace:
    """跑一次完整的 Tool Use 循环，直到模型给出最终自然语言回复。

    循环而不是只判断一次：模型可能需要连续调用好几轮工具
    （比如先查一个事实，再基于这个事实决定要不要查第二个事实），
    只有当某一轮模型不再请求任何工具时，才算真正拿到了最终答案。

    返回 AgentTrace 而不是裸字符串：把每一轮"模型调用了什么工具、
    工具返回了什么"都记下来，方便调试/展示 Agent 的思考过程，
    调用方只需要用 trace.final_content 代替原来的 reply 字符串。

    force_tool_use：默认 False，等价于 tool_choice="auto"（模型自己判断
    要不要调用工具，可能完全跳过直接给答案）。设为 True 会在"第一轮"
    传 tool_choice="required"，强制模型必须调用某个工具，不给它"凭自己
    的知识直接拼答案"这个选项（详见 ISSUES.md #5：模型在明知有工具可用时，
    仍可能判断"任务太简单不需要工具"而绕过调用，返回没有真实依据的内容）。
    只在第一轮强制，因为模型必须能在拿到工具结果后正常收尾给出最终答案——
    如果每一轮都强制，模型会被迫不停地调用工具，永远无法结束循环。

    force_tool_use=True 时还会关闭 thinking mode（qwen3.5-flash 默认开启的
    混合推理机制）：DashScope 明确不允许在 thinking mode 下强制 tool_choice
    （报错 "tool_choice parameter does not support being set to required or
    object in thinking mode"），因为"先自由思考再决定"和"外部强制必须调用"
    这两种机制本身矛盾。enable_thinking 不是 OpenAI 标准参数，openai SDK
    不认识这个字段名，需要通过 extra_body 透传给 DashScope。

    force_tool_use=True 时，第一轮请求不会传 response_format：实测发现
    tool_choice="required" 和 response_format="json_object" 同时生效时
    会互相冲突——"必须输出 JSON" 的约束会压过"必须调用工具"，模型直接给出
    JSON 格式的最终内容、完全跳过工具调用（详见 ISSUES.md #5）。所以强制
    调用工具的第一轮只关心"有没有调用工具"，不携带 response_format；等
    拿到工具结果、进入生成最终答案的那一轮，才把 response_format 带上，
    这一轮已经不需要再强制工具（模型该收尾了），两个约束不会撞在同一次
    请求里。
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    steps: list[TraceStep] = []
    extra_body = {"enable_thinking": False} if force_tool_use else None

    first_tool_choice = "required" if force_tool_use else "auto"
    first_response_format = None if force_tool_use else response_format
    response = await client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools, response_format=first_response_format,
        tool_choice=first_tool_choice, extra_body=extra_body,
    )
    reply = response.choices[0].message

    while reply.tool_calls:
        messages.append(reply)

        tool_records = []
        for tool_call in reply.tool_calls:
            args = json.loads(tool_call.function.arguments)
            func = tool_functions[tool_call.function.name]
            result = func(**args)
            tool_records.append(
                ToolCallRecord(tool_name=tool_call.function.name, arguments=args, result=result)
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

        steps.append(TraceStep(role="tool_call", tool_calls=tool_records))

        response = await client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools, response_format=response_format,
            tool_choice="auto", extra_body=extra_body,
        )
        reply = response.choices[0].message

    steps.append(TraceStep(role="final", content=reply.content))

    return AgentTrace(steps=steps, final_content=reply.content)
