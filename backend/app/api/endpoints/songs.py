"""音频上传与歌曲管理（产品文档 §6.1）。"""
import uuid

from fastapi import APIRouter, Depends, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db, async_session
from app.db.models import Song
from fastapi.responses import FileResponse
from app.services.audio.pipeline import analyze_song



router = APIRouter()

async def _run_analysis(song_id: str, file_path: str):
    """后台任务：跑音频分析，把结果写回数据库。"""
    async with async_session() as db:
        song = await db.get(Song, song_id)
        song.status = "analyzing"
        await db.commit()

        try:
            result = await analyze_song(song_id, file_path)
            song.analysis = result.model_dump()
            song.status = "done"
        except Exception:
            song.status = "failed"

        await db.commit()

@router.post("")
async def upload_song(file: UploadFile,     background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """上传音频文件，保存到 storage 并创建 Song 记录，触发后台分析任务。"""
    song_id = str(uuid.uuid4())
    file_path = f"{settings.upload_dir}/{song_id}_{file.filename}"

    # 第一步：把上传的文件内容读出来，写到硬盘
    content = await file.read()
    with open(file_path, "wb") as f:   # 提示：写文件用什么模式？内容是 bytes 类型
        f.write(content)

    # 第二步：创建一条 Song 记录，加进这次数据库会话
    song = Song(id=song_id, filename=file.filename, file_path=file_path, status="pending")  # 提示：初始状态是什么
    db.add(song)
    await db.commit()

    background_tasks.add_task(_run_analysis, song_id, file_path)
    return {"id": song.id, "filename": song.filename, "status": song.status}



@router.get("")
async def list_songs(db: AsyncSession = Depends(get_db)):
    """按上传时间倒序返回所有歌曲的基本信息，供首页展示历史记录。"""
    result = await db.execute(select(Song).order_by(Song.created_at.desc()))
    songs = result.scalars().all()
    return [
        {"id": s.id, "filename": s.filename, "status": s.status, "created_at": s.created_at}
        for s in songs
    ]


@router.get("/{song_id}")
async def get_song(song_id: str, db: AsyncSession = Depends(get_db)):
    """返回歌曲基本信息与分析状态（pending / analyzing / done / failed）。"""
    song = await db.get(Song, song_id)
    if song is None:
        raise HTTPException(404, "Song not found") 

    return {"id": song.id, "filename": song.filename, "status": song.status}


@router.get("/{song_id}/audio")
async def stream_audio(song_id: str,  db: AsyncSession = Depends(get_db)):
    """返回音频文件供前端播放器使用（支持 Range 请求）。"""
    song = await db.get(Song, song_id)
    if song is None:
        raise HTTPException(404, "Song not found") 

    return FileResponse(song.file_path) 

