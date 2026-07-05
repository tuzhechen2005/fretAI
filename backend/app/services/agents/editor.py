"""自然语言修改编配（产品文档 §9.2、§10.2-11）。

LLM 将用户指令解析为结构化操作（tool use），再调用规则系统执行：
    "降两调"            -> transpose(semitones=-2)
    "换到低把位"        -> optimize_positions(prefer_position=0..3)
    "改成 power chord"  -> to_power_chord(...)
    "不要大横按"        -> optimize_positions(avoid_barre=True)
最后返回新 Arrangement + 修改说明。
"""
from app.schemas.arrangement import Arrangement


async def apply_edit(arrangement: Arrangement, message: str) -> tuple[Arrangement, str]:
    """返回 (新编配, Agent 回复文本)。"""
    raise NotImplementedError
