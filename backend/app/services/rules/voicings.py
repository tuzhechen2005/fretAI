"""吉他指法库（产品文档 §6.7）：同一和弦的多把位版本。

MVP 用静态字典覆盖常用和弦（大/小/7/m7/sus/5），每个和弦含：
开放和弦、横按、高把位三和弦、power chord、octave 等 voicing，
标注指法字符串（如 "x02210"）、把位、是否横按。
"""

VOICING_DB: dict[str, list[dict]] = {
    # "Am": [
    #     {"fingering": "x02210", "position": 0, "barre": False, "kind": "open"},
    #     {"fingering": "577555", "position": 5, "barre": True, "kind": "barre"},
    #     ...
    # ]
}


def get_voicings(chord: str) -> list[dict]:
    raise NotImplementedError
