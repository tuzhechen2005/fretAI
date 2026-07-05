"""Guitar Arrangement（产品文档 §12.2）。"""
from typing import Literal

from pydantic import BaseModel

ArrangementType = Literal[
    "acoustic_beginner",      # 木吉他低把位 / 新手版
    "acoustic_strumming",     # 木吉他弹唱版
    "electric_power_chord",   # 电吉他 Power Chord 版
    "electric_original",      # 原曲感电吉他版（Phase 2）
    "high_position_triads",   # 高把位三和弦版（Phase 2）
]


class ArrangedChord(BaseModel):
    original: str            # 原曲和弦，如 "F#m"
    display: str             # 编配后显示，如 "Em"（capo 后）或 "F#5"
    fingering: str           # 指法，如 "244xxx"
    position: int            # 把位
    technique: list[str] = []  # palm_mute / open_strum / ...


class Arrangement(BaseModel):
    arrangement_id: str
    song_id: str
    type: ArrangementType
    difficulty: int          # 1-10（产品文档 §13）
    capo: int | None = None
    tuning: str = "standard"
    chords: list[ArrangedChord] = []
    notes: str = ""          # Agent 编配说明与推荐原因
