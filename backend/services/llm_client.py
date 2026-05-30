from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from config import settings


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    if not settings.DASHSCOPE_API_KEY or settings.DASHSCOPE_API_KEY.startswith("sk-请替换"):
        raise RuntimeError(
            "DASHSCOPE_API_KEY 未配置，请在 backend/.env 中设置阿里云百炼 API Key"
        )
    return OpenAI(
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL,
    )
