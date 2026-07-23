"""音频分析结果：Key / BPM / 和弦时间轴 / 段落结构（产品文档 §6.1、§6.2、§6.3）。"""
from fastapi import APIRouter

from app.services.tools.transpose import transpose_progression

router = APIRouter()


@router.get("/{song_id}/analysis")
async def get_analysis(song_id: str):
    """返回 SongAnalysisResult（schemas/song.py），含置信度与候选和弦。"""
    raise NotImplementedError


@router.post("/transpose-preview")
async def transpose_preview(chords: list[str], semitones: int):
    """调试用：直接传和弦列表和半音数，返回转调结果，不依赖数据库。"""
    return {"original": chords, "transposed": transpose_progression(chords, semitones)}


@router.post("/{song_id}/transpose")
async def transpose(song_id: str, semitones: int):
    """一键升降调：整体移调后返回更新的和弦时间轴（纯规则计算，不重跑音频分析）。"""
    raise NotImplementedError


@router.patch("/{song_id}/chords/{chord_index}")
async def correct_chord(song_id: str, chord_index: int, chord: str):
    """用户手动修正某个和弦（产品文档 §14，修正数据保留用于后续优化）。"""
    raise NotImplementedError
