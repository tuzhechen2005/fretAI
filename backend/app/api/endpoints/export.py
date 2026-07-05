"""导出功能（产品文档 §6.13，MVP 只做 Markdown / PDF）。"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{song_id}/arrangements/{arrangement_id}/export")
async def export_arrangement(song_id: str, arrangement_id: str, format: str = "markdown"):
    """format: markdown | pdf。返回和弦谱文件。"""
    raise NotImplementedError
