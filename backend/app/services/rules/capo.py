"""Capo 推荐（产品文档 §6.4）：枚举 capo 0-7，对每个方案评估
开放和弦占比、横按数量、常用指法族（G/C/D/E/Am/Em...），输出多方案排序。
"""
from app.services.rules.transpose import transpose_progression
from app.services.rules.voicings import get_voicings

def count_barres(chords: list[str]) -> int:
    count = 0
    for c in chords:
        voicings = get_voicings(c)
        has_open = any(v["kind"] == "open" for v in voicings)
        if not has_open:
            count += 1
    return count

def recommend_capo(key: str, chords: list[str]) -> list[dict]:
    """返回 [{capo, played_key, played_chords, pros, cons, difficulty}, ...]。"""
    result = []
    for capo in range(0,8):
        played_chords = transpose_progression(chords, -capo)
        result.append({
            "capo": capo,
            "played_chords": played_chords,
            "barre_count": count_barres(played_chords),
        })
    return sorted(result, key=lambda item: item["barre_count"]) 
