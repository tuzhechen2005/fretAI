"""Agent Tool Use 循环的执行轨迹（trace），用于调试/前端展示"思考过程"。

不是产品文档里定义的数据结构，是里程碑 6 为了排查 Agent 内部行为新增的。
"""
from pydantic import BaseModel


class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: dict
    result: object  # 工具函数的原始返回值，通常是 dict 或 list


class TraceStep(BaseModel):
    role: str  # "tool_call" | "final"
    tool_calls: list[ToolCallRecord] = []
    content: str | None = None  # 最终轮才有


class AgentTrace(BaseModel):
    steps: list[TraceStep]
    final_content: str
