"""段落结构检测（Intro/Verse/Chorus/...）：自相似矩阵 + novelty 分段。

MVP 可先只输出无标签的分段边界，标签由 Agent 结合和弦重复模式推断。
"""
from app.schemas.song import Section


def detect_sections(y, sr) -> list[Section]:
    raise NotImplementedError
