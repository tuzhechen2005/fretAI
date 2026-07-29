"""音频分析结果：Key / BPM / 和弦时间轴 / 段落结构（产品文档 §6.1、§6.2、§6.3）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Song
from app.schemas.song import SongAnalysisResult
from app.services.tools.transpose import transpose_progression

router = APIRouter()


async def _get_analyzed_song(song_id: str, db: AsyncSession) -> Song:
    song = await db.get(Song, song_id)
    if song is None:
        raise HTTPException(404, "Song not found")
    if song.status != "done" or song.analysis is None:
        raise HTTPException(409, f"Song analysis not ready (status={song.status})")
    return song


@router.get("/{song_id}/analysis")
async def get_analysis(song_id: str, db: AsyncSession = Depends(get_db)):
    """返回 SongAnalysisResult（schemas/song.py），含置信度与候选和弦。"""
    song = await _get_analyzed_song(song_id, db)
    return song.analysis


@router.post("/transpose-preview")
async def transpose_preview(chords: list[str], semitones: int):
    """调试用：直接传和弦列表和半音数，返回转调结果，不依赖数据库。"""
    return {"original": chords, "transposed": transpose_progression(chords, semitones)}


@router.post("/{song_id}/transpose")
async def transpose(song_id: str, semitones: int, db: AsyncSession = Depends(get_db)):
    """一键升降调：整体移调后返回更新的和弦时间轴（纯规则计算，不重跑音频分析）。"""
    song = await _get_analyzed_song(song_id, db)
    analysis = SongAnalysisResult.model_validate(song.analysis)

    original_chords = [c.chord for c in analysis.chords]
    transposed_chords = transpose_progression(original_chords, semitones)
    for chord_event, new_chord in zip(analysis.chords, transposed_chords):
        chord_event.chord = new_chord

    song.analysis = analysis.model_dump()
    await db.commit()

    return song.analysis


@router.patch("/{song_id}/chords/{chord_index}")
async def correct_chord(song_id: str, chord_index: int, chord: str, db: AsyncSession = Depends(get_db)):
    """用户手动修正某个和弦（产品文档 §14，修正数据保留用于后续优化）。"""
    song = await _get_analyzed_song(song_id, db)
    analysis = SongAnalysisResult.model_validate(song.analysis)

    if chord_index < 0 or chord_index >= len(analysis.chords):
        raise HTTPException(422, f"chord_index {chord_index} out of range (0-{len(analysis.chords) - 1})")

    analysis.chords[chord_index].chord = chord
    analysis.chords[chord_index].user_corrected = True

    song.analysis = analysis.model_dump()
    await db.commit()

    return song.analysis
