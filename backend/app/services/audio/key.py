"""调性检测：chroma 特征 + Krumhansl-Schmuckler key profile 相关性。"""


def detect_key(y, sr) -> tuple[str, float]:
    """返回 (key, confidence)，如 ("E minor", 0.87)。"""
    raise NotImplementedError
