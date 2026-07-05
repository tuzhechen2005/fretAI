"""自然语言修改编配（产品文档 §9.2）。

用户示例指令：
    "把副歌改成 5 品附近的 power chord，不要大跳"
    "再简单一点，我不想跳到 9 品"
    "降两调"
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/{song_id}/arrangements/{arrangement_id}/chat")
async def modify_arrangement(song_id: str, arrangement_id: str, message: str):
    """LLM 解析用户意图 -> 调用规则系统重新编配 -> 返回新版本 + 解释。"""
    raise NotImplementedError
