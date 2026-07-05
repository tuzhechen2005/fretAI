"""吉他编配版本生成（产品文档 §6.5、§6.6、§6.7、§7.3、§7.4）。"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/{song_id}/arrangements")
async def generate_arrangements(song_id: str):
    """基于分析结果生成多个版本：木吉他低把位版（含 Capo 推荐）、
    电吉他 Power Chord 版等，每个版本附难度评分与 Agent 推荐原因。"""
    raise NotImplementedError


@router.get("/{song_id}/arrangements")
async def list_arrangements(song_id: str):
    raise NotImplementedError


@router.get("/{song_id}/arrangements/{arrangement_id}")
async def get_arrangement(song_id: str, arrangement_id: str):
    raise NotImplementedError


@router.get("/chords/{chord_name}/voicings")
async def get_voicings(chord_name: str):
    """多把位和弦图：返回一个和弦的多个指法版本（开放 / 横按 / 三和弦 / power chord）。"""
    raise NotImplementedError
