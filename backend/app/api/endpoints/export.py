"""导出功能（产品文档 §6.13，MVP 只做 Markdown / PDF）。

纯格式转换，不经过 LLM——见 DECISIONS.md #14（为什么 Export 不做成 Agent）。
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Arrangement as ArrangementModel
from app.db.models import Song
from app.schemas.arrangement import Arrangement
from app.schemas.song import SongAnalysisResult
from app.services.export.markdown import render_markdown
from app.services.export.pdf import render_pdf

router = APIRouter()


@router.get("/{song_id}/arrangements/{arrangement_id}/export")
async def export_arrangement(
    song_id: str, arrangement_id: str, format: str = "markdown", db: AsyncSession = Depends(get_db)
):
    """format: markdown | pdf。返回和弦谱文件。"""
    song = await db.get(Song, song_id)
    if song is None or song.analysis is None:
        raise HTTPException(404, "Song not found or not analyzed yet")

    row = await db.get(ArrangementModel, arrangement_id)
    if row is None or row.song_id != song_id:
        raise HTTPException(404, "Arrangement not found")

    analysis = SongAnalysisResult.model_validate(song.analysis)
    arrangement = Arrangement.model_validate(row.data)

    if format == "markdown":
        content = render_markdown(analysis, arrangement)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{arrangement_id}.md"'},
        )
    if format == "pdf":
        content = render_pdf(analysis, arrangement)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{arrangement_id}.pdf"'},
        )
    raise HTTPException(422, f"Unsupported format: {format} (use 'markdown' or 'pdf')")
