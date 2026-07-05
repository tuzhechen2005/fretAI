"""把位优化算法（产品文档 §6.8）：对整段和弦进行 voicing 组合选择。

用动态规划在各和弦的候选 voicing 之间求最小代价路径，
代价 = 换把距离 + 横按惩罚 + 偏离目标把位惩罚。
"""


def optimize_positions(
    chords: list[str],
    prefer_position: int | None = None,
    avoid_barre: bool = False,
) -> list[dict]:
    """返回每个和弦选定的 voicing 列表。"""
    raise NotImplementedError
