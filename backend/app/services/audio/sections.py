"""段落结构检测（Intro/Verse/Chorus/...）：自相似矩阵 + novelty 分段。

MVP 可先只输出无标签的分段边界，标签由 Agent 结合和弦重复模式推断。

思路：把整首歌的 chroma 特征喂给 librosa 的聚类分段算法
（librosa.segment.agglomerative），按内容相似度自动切出 k 个段落边界，
再把"帧序号"换算成"秒"，包装成 Section 列表（name 先留空，
交给 Agent 层结合和弦重复模式推断具体是 Verse 还是 Chorus）。
"""
import librosa

from app.schemas.song import Section

# 目标切成几段：MVP 先固定一个粗略值，不做智能判断"这首歌该分几段"
DEFAULT_NUM_SEGMENTS = 6


def detect_sections(y, sr) -> list[Section]:
    duration = librosa.get_duration(y=y, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    # 歌曲太短时，段数不能超过实际能切的帧数，做个保护性收窄
    num_segments = min(DEFAULT_NUM_SEGMENTS, chroma.shape[1])
    if num_segments < 2:
        return [Section(name="", start=0.0, end=duration)]

    boundary_frames = librosa.segment.agglomerative(chroma, num_segments)
    boundary_times = librosa.frames_to_time(boundary_frames, sr=sr)

    # boundary_times 是每段的"起点"，需要补上整首歌的终点，才能配对出每段的 (start, end)
    boundary_times = sorted(boundary_times.tolist())
    if not boundary_times or boundary_times[0] != 0.0:
        boundary_times = [0.0] + boundary_times
    boundary_times.append(duration)

    sections = []
    for start, end in zip(boundary_times[:-1], boundary_times[1:]):
        sections.append(Section(name="", start=start, end=end))

    return sections
