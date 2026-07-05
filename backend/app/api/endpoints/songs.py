"""音频上传与歌曲管理（产品文档 §6.1）。"""
from fastapi import APIRouter, UploadFile

router = APIRouter()


@router.post("")
async def upload_song(file: UploadFile):
    """上传音频文件，保存到 storage 并创建 Song 记录，触发后台分析任务。"""
    raise NotImplementedError  # TODO: 保存文件 -> 建 Song 记录 -> BackgroundTasks 触发分析


@router.get("")
async def list_songs():
    raise NotImplementedError


@router.get("/{song_id}")
async def get_song(song_id: str):
    """返回歌曲基本信息与分析状态（pending / analyzing / done / failed）。"""
    raise NotImplementedError


@router.get("/{song_id}/audio")
async def stream_audio(song_id: str):
    """返回音频文件供前端播放器使用（支持 Range 请求）。"""
    raise NotImplementedError
