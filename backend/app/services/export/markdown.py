"""Markdown 和弦谱导出（产品文档 §6.13 MVP 范围）。

输出：歌曲信息（Key/BPM/Capo/调弦）+ 按段落排列的和弦表 + 指法图（文本）+ 编配说明。
"""
from app.schemas.arrangement import Arrangement
from app.schemas.song import SongAnalysisResult


def render_markdown(analysis: SongAnalysisResult, arrangement: Arrangement) -> str:
    raise NotImplementedError
