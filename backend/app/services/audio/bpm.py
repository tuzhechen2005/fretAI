"""BPM 检测与 beat tracking（librosa.beat.beat_track）。"""
import librosa


def detect_bpm(y, sr) -> tuple[float, list[float]]:
    """返回 (bpm, beat_times)。beat_times 用于对齐和弦时间轴到小节。"""
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    if hasattr(tempo, "item"):
        tempo = tempo.item()
    return float(tempo), beat_times.tolist()

