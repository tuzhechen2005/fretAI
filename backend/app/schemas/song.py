"""Song Analysis Result（产品文档 §12.1）。"""
from pydantic import BaseModel


class Section(BaseModel):
    name: str  # Intro / Verse / Chorus / Bridge / Solo / Outro
    start: float
    end: float


class ChordEvent(BaseModel):
    start: float
    end: float
    chord: str
    confidence: float
    candidates: list[str] = []
    reason: str | None = None  # 低置信度时的解释（产品文档 §14）
    user_corrected: bool = False


class SongAnalysisResult(BaseModel):
    song_id: str
    key: str  # e.g. "E minor"
    bpm: float
    time_signature: str = "4/4"
    sections: list[Section] = []
    chords: list[ChordEvent] = []
