"""PDF 导出：MVP 先由 Markdown 渲染为简单排版 PDF（reportlab）。"""
from app.schemas.arrangement import Arrangement
from app.schemas.song import SongAnalysisResult


def render_pdf(analysis: SongAnalysisResult, arrangement: Arrangement) -> bytes:
    raise NotImplementedError
