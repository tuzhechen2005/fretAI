"""LLM client 封装：统一模型、系统提示与工具调用入口。

用阿里云百炼（DashScope）的 OpenAI 兼容接口，所以用 openai 这个 SDK，
只是把 base_url 指向阿里云——这也是 OpenAI 接口格式事实上成为行业
标准的体现，换供应商基本不用改调用代码，只改 base_url/model/api_key。
"""
from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)

MODEL = settings.llm_model
