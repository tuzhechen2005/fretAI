"""自然语言修改编配（产品文档 §9.2）。

用户示例指令：
    "把副歌改成 5 品附近的 power chord，不要大跳"
    "再简单一点，我不想跳到 9 品"
    "降两调"
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Arrangement as ArrangementModel
from app.schemas.arrangement import Arrangement
from app.services.agents.editor import apply_edit

router = APIRouter()


@router.post("/{song_id}/arrangements/{arrangement_id}/chat")
async def modify_arrangement(
    song_id: str, arrangement_id: str, message: str, db: AsyncSession = Depends(get_db)
):
    """LLM 解析用户意图 -> 调用规则系统重新编配 -> 返回新版本 + 解释。"""
    row = await db.get(ArrangementModel, arrangement_id)
    if row is None or row.song_id != song_id:
        raise HTTPException(404, "Arrangement not found")

    arrangement = Arrangement.model_validate(row.data)
    new_arrangement, explanation, trace = await apply_edit(arrangement, message)

    row.data = new_arrangement.model_dump()
    row.type = new_arrangement.type
    await db.commit()

    return {"arrangement": new_arrangement, "reply": explanation, "trace": trace}
