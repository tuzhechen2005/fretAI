"""Fingering Agent（产品文档 §7.4）。

把用户要求（"5 品附近""不要大跳""避免横按"）转成 positions.optimize_positions
的参数，并对结果生成可读说明。
"""
from app.schemas.arrangement import ArrangedChord


async def optimize_fingering(
    chords: list[str],
    constraints: dict,
) -> tuple[list[ArrangedChord], str]:
    """返回 (优化后的指法列表, 说明文本)。"""
    raise NotImplementedError
