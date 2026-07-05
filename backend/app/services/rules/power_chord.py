"""Power Chord 转换（产品文档 §6.6）：任意和弦 -> 根音 5 和弦。

支持 6 弦根音 / 5 弦根音两套位置，可指定目标把位区域（如"5 品附近"）。
"""


def to_power_chord(chord: str, prefer_position: int | None = None) -> dict:
    """返回 {"display": "F#5", "fingering": "244xxx", "position": 2}。"""
    raise NotImplementedError
