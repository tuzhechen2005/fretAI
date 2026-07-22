"""和弦识别：逐拍 chroma -> 和弦模板匹配 -> 生成 ChordEvent 列表。

思路（跟 key.py 是同一套方法论，粒度不同——key.py 对整首歌算一次，
这里对每两拍一个片段各算一次）：
1. 用 beat_times 把整首歌切成一段一段（每两拍一段，贴近和弦通常按拍换的规律）。
2. 每段单独算 chroma 特征。
3. 跟 24 种和弦模板（12 个大三和弦 + 12 个小三和弦）比较相关性，
   取最相关的作为这段的和弦，次相关的作为候选项。
4. 相邻片段如果和弦相同，合并成一个更长的 ChordEvent（避免同一个和弦被拆成好几段）。

输出带置信度和候选和弦的 ChordEvent 列表（产品文档 §14），
低置信度的结果交给 Music Theory Agent 纠错。
"""
import librosa
import numpy as np

from app.schemas.song import ChordEvent

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# 大三和弦模板：根音、大三度（+4 半音）、纯五度（+7 半音）三个位置为 1，其余为 0
MAJOR_TRIAD = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
# 小三和弦模板：根音、小三度（+3 半音）、纯五度（+7 半音）
MINOR_TRIAD = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])


def _best_chord_for_chroma(chroma_vec: np.ndarray) -> tuple[str, float, list[str]]:
    """给定一个 12 维 chroma 向量，返回 (最佳和弦, 置信度, 候选和弦列表)。"""
    scores: list[tuple[str, float]] = []

    for shift in range(12):
        major_template = np.roll(MAJOR_TRIAD, shift)
        minor_template = np.roll(MINOR_TRIAD, shift)

        major_score = float(np.dot(chroma_vec, major_template))
        minor_score = float(np.dot(chroma_vec, minor_template))

        scores.append((f"{NOTE_NAMES[shift]}", major_score))
        scores.append((f"{NOTE_NAMES[shift]}m", minor_score))

    scores.sort(key=lambda item: item[1], reverse=True)

    best_chord, best_score = scores[0]
    total = sum(s for _, s in scores) + 1e-9
    confidence = max(0.0, min(1.0, best_score / total * len(scores) / 4))

    candidates = [chord for chord, _ in scores[:3]]
    return best_chord, confidence, candidates


def recognize_chords(y, sr, beat_times: list[float]) -> list[ChordEvent]:
    if len(beat_times) < 2:
        return []

    # 每两拍切一段，得到一串 (start, end) 时间区间
    segment_bounds = beat_times[::2]
    if segment_bounds[-1] != beat_times[-1]:
        segment_bounds = segment_bounds + [beat_times[-1]]

    raw_events: list[ChordEvent] = []
    for start, end in zip(segment_bounds[:-1], segment_bounds[1:]):
        start_sample = int(start * sr)
        end_sample = int(end * sr)
        y_segment = y[start_sample:end_sample]

        if len(y_segment) == 0:
            continue

        chroma = librosa.feature.chroma_cqt(y=y_segment, sr=sr)
        chroma_vec = chroma.mean(axis=1)

        chord, confidence, candidates = _best_chord_for_chroma(chroma_vec)
        raw_events.append(
            ChordEvent(start=start, end=end, chord=chord, confidence=confidence, candidates=candidates)
        )

    # 合并相邻的相同和弦，避免同一个和弦被拆成好几个小段
    merged: list[ChordEvent] = []
    for event in raw_events:
        if merged and merged[-1].chord == event.chord:
            merged[-1].end = event.end
        else:
            merged.append(event)

    return merged
