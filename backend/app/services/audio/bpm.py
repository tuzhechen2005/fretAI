"""BPM 检测与 beat tracking（librosa.beat.beat_track）。"""


def detect_bpm(y, sr) -> tuple[float, list[float]]:
    """返回 (bpm, beat_times)。beat_times 用于对齐和弦时间轴到小节。"""
    raise NotImplementedError
