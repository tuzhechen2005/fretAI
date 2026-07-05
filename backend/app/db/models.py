"""ORM 模型。MVP 三张表：Song、Analysis、Arrangement。

分析结果和编配结果以 JSON 列存储（结构见 app/schemas/），
避免 MVP 阶段过度设计关系表；换 PostgreSQL 后可迁移为 JSONB。
"""
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str]
    file_path: Mapped[str]
    status: Mapped[str] = mapped_column(default="pending")  # pending/analyzing/done/failed
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # SongAnalysisResult


class Arrangement(Base):
    __tablename__ = "arrangements"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    song_id: Mapped[str]
    type: Mapped[str]
    data: Mapped[dict] = mapped_column(JSON)  # schemas.arrangement.Arrangement
