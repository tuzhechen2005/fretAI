"""难度评分（产品文档 §13）：横按数、把位跨度、平均换把距离、
和弦复杂度、特殊技巧、特殊调弦等维度加权，输出 1-10 分与原因列表。
"""


def score_difficulty(voicings: list[dict], techniques: list[str]) -> tuple[int, list[str]]:
    """返回 (score, reasons)。"""
    raise NotImplementedError
