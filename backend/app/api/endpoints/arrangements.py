"""吉他编配版本生成（产品文档 §6.5、§6.6、§6.7、§7.3、§7.4）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Arrangement as ArrangementModel
from app.db.models import Song
from app.schemas.profile import UserGuitarProfile
from app.schemas.song import SongAnalysisResult
from app.services.agents.arrangement import generate_arrangements as run_arrangement_agent
from app.services.tools.power_chord import to_power_chord
from app.services.tools.voicings import get_voicings as lookup_voicings

router = APIRouter()


@router.post("/{song_id}/arrangements")
async def generate_arrangements(song_id: str, db: AsyncSession = Depends(get_db)):
    """基于分析结果生成多个版本：木吉他低把位版（含 Capo 推荐）、
    电吉他 Power Chord 版等，每个版本附难度评分与 Agent 推荐原因。"""
    song = await db.get(Song, song_id)
    if song is None:
        raise HTTPException(404, "Song not found")
    if song.status != "done" or song.analysis is None:
        raise HTTPException(409, f"Song analysis not ready (status={song.status})")

    analysis = SongAnalysisResult.model_validate(song.analysis)
    profile = UserGuitarProfile()

    arrangements, trace = await run_arrangement_agent(analysis, profile)

    for arrangement in arrangements:
        db.add(ArrangementModel(
            id=arrangement.arrangement_id,
            song_id=song_id,
            type=arrangement.type,
            data=arrangement.model_dump(),
        ))
    await db.commit()

    return {"arrangements": arrangements, "trace": trace}


@router.get("/{song_id}/arrangements")
async def list_arrangements(song_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ArrangementModel).where(ArrangementModel.song_id == song_id))
    return [row.data for row in result.scalars().all()]


@router.get("/{song_id}/arrangements/{arrangement_id}")
async def get_arrangement(song_id: str, arrangement_id: str, db: AsyncSession = Depends(get_db)):
    arrangement = await db.get(ArrangementModel, arrangement_id)
    if arrangement is None or arrangement.song_id != song_id:
        raise HTTPException(404, "Arrangement not found")
    return arrangement.data


@router.get("/chords/{chord_name}/voicings")
async def get_voicings(chord_name: str):
    """多把位和弦图：返回一个和弦的多个指法版本（开放 / 横按 / 三和弦 / power chord）。"""
    return {"chord": chord_name, "voicings": lookup_voicings(chord_name)}


@router.get("/chords/{chord_name}/power-chord-preview")
async def power_chord_preview(chord_name: str):
    """调试用：直接查某个和弦的 power chord 版本，不依赖数据库。"""
    return to_power_chord(chord_name)
