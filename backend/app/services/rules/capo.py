"""Capo 推荐（产品文档 §6.4）：枚举 capo 0-7，对每个方案评估
开放和弦占比、横按数量、常用指法族（G/C/D/E/Am/Em...），输出多方案排序。
"""


def recommend_capo(key: str, chords: list[str]) -> list[dict]:
    """返回 [{capo, played_key, played_chords, pros, cons, difficulty}, ...]。"""
    raise NotImplementedError
