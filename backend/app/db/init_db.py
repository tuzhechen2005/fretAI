"""建表脚本：把 models.py 里定义的表结构真正写进 fretai.db。

用法：python -m app.db.init_db
"""
import asyncio

from app.db.database import Base, engine
from app.db import models  # noqa: F401  必须 import 才能让 Song/Arrangement 注册进 Base.metadata


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
