"""Music Theory Agent（产品文档 §7.2）。

对音频识别结果做乐理层面纠错：
1. 判断和弦是否符合调性，不符合时给出借用/属和弦解释或修正建议。
2. 结合前后进行修正低置信度和弦。
3. 根据贝斯音判断 slash chord。
输出仍是 ChordEvent 列表，只更新 chord / candidates / reason 字段。
"""
from app.schemas.song import ChordEvent


async def review_chords(key: str, chords: list[ChordEvent]) -> list[ChordEvent]:
    raise NotImplementedError
