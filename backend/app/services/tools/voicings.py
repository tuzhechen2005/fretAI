"""吉他指法库（产品文档 §6.7）：同一和弦的多把位版本。

MVP 用静态字典覆盖常用和弦（大/小/7/m7/sus/5），每个和弦含：
开放和弦、横按、高把位三和弦、power chord、octave 等 voicing，
标注指法字符串（如 "x02210"）、把位、是否横按。
"""

VOICING_DB: dict[str, list[dict]] = {
    # 常见开放和弦大三和弦
    "C": [
        {"fingering": "x32010", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "x35553", "position": 3, "barre": True, "kind": "barre"},
        {"fingering": "x3555x", "position": 3, "barre": False, "kind": "power"},
    ],
    "D": [
        {"fingering": "xx0232", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "x57775", "position": 5, "barre": True, "kind": "barre"},
        {"fingering": "x577xx", "position": 5, "barre": False, "kind": "power"},
    ],
    "E": [
        {"fingering": "022100", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "079900", "position": 7, "barre": True, "kind": "barre"},
        {"fingering": "022xxx", "position": 0, "barre": False, "kind": "power"},
    ],
    "G": [
        {"fingering": "320003", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "355433", "position": 3, "barre": True, "kind": "barre"},
        {"fingering": "3554xx", "position": 3, "barre": False, "kind": "power"},
    ],
    "A": [
        {"fingering": "x02220", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "577655", "position": 5, "barre": True, "kind": "barre"},
        {"fingering": "577xxx", "position": 5, "barre": False, "kind": "power"},
    ],
    "F": [
        {"fingering": "133211", "position": 1, "barre": True, "kind": "barre"},
        {"fingering": "xx3211", "position": 1, "barre": False, "kind": "power"},
    ],
    # 常见开放和弦小三和弦
    "Am": [
        {"fingering": "x02210", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "577555", "position": 5, "barre": True, "kind": "barre"},
        {"fingering": "xx7555", "position": 5, "barre": False, "kind": "triad"},
        {"fingering": "577xxx", "position": 5, "barre": False, "kind": "power"},
    ],
    "Em": [
        {"fingering": "022000", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "079800", "position": 7, "barre": True, "kind": "barre"},
        {"fingering": "022xxx", "position": 0, "barre": False, "kind": "power"},
    ],
    "Dm": [
        {"fingering": "xx0231", "position": 0, "barre": False, "kind": "open"},
        {"fingering": "x57765", "position": 5, "barre": True, "kind": "barre"},
        {"fingering": "x577xx", "position": 5, "barre": False, "kind": "power"},
    ],
}


def get_voicings(chord: str) -> list[dict]:
    """返回某个和弦的所有已知指法版本；找不到就返回空列表（交给上层决定怎么处理）。"""
    return VOICING_DB.get(chord, [])
