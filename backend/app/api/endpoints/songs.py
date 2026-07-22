"""音频上传与歌曲管理（产品文档 §6.1）。"""
import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Song
from fastapi import HTTPException

router = APIRouter()


@router.post("")
async def upload_song(file: UploadFile, db: AsyncSession = Depends(get_db)):
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

    return {"id": song.id, "filename": song.filename, "status": song.status}



@router.get("")
async def list_songs():
    raise NotImplementedError


@router.get("/{song_id}")
async def get_song(song_id: str, db: AsyncSession = Depends(get_db)):
    """返回歌曲基本信息与分析状态（pending / analyzing / done / failed）。"""
    song = await db.get(Song, song_id)
    if song is None:
        raise HTTPException(404, "Song not found") 

    return {"id": song.id, "filename": song.filename, "status": song.status}


@router.get("/{song_id}/audio")
async def stream_audio(song_id: str):
    """返回音频文件供前端播放器使用（支持 Range 请求）。"""
    raise NotImplementedError
