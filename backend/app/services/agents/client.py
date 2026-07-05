"""Anthropic client 封装：统一模型、系统提示与工具调用入口。"""
from anthropic import AsyncAnthropic

from app.core.config import settings

client = AsyncAnthropic(api_key=settings.anthropic_api_key)

MODEL = "claude-sonnet-5"
