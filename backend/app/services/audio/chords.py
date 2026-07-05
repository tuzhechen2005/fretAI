"""和弦识别：逐帧 chroma -> 和弦模板匹配 -> 按 beat 对齐合并。

输出带置信度和候选和弦的 ChordEvent 列表（产品文档 §14），
低置信度的结果交给 Music Theory Agent 纠错。
"""
from app.schemas.song import ChordEvent


def recognize_chords(y, sr, beat_times: list[float]) -> list[ChordEvent]:
    raise NotImplementedError
