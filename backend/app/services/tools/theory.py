"""调内和弦规则：给定调性，确定性地算出调内的自然和弦。

不依赖 LLM 回忆乐理知识，避免模型偶尔算错或前后不一致——
Music Theory Agent 判断"某个和弦是否离调/借用"时，应该调用这里
算出的事实，而不是自己凭记忆推算。

大调音阶级数与和弦性质的对应关系是固定的音乐理论规律：
    级数:    I    ii   iii  IV   V    vi   vii°
    性质:    大三  小三  小三  大三  大三  小三  减三
    半音偏移: 0    2    4    5    7    9    11

MVP 只做大调，小调音阶的对应规律不同，先跳过（已知局限）。
"""
from app.services.tools.transpose import NOTES, FLAT_TO_SHARP

# 大调音阶 7 个音级相对主音的半音偏移，与对应的和弦性质
MAJOR_SCALE_OFFSETS = [0, 2, 4, 5, 7, 9, 11]
MAJOR_SCALE_QUALITIES = ["", "m", "m", "", "", "m", "dim"]


def get_diatonic_chords(key: str) -> list[str]:
    """给定大调调性（如 "G major"），返回调内 7 个自然和弦（按级数 I-vii°排列）。

    小调调性目前原样按大调规则处理（已知局限，不精确）。
    """
    root = key.split()[0]  # "G major" -> "G"
    root = FLAT_TO_SHARP.get(root, root)
    root_index = NOTES.index(root)

    chords = []
    for offset, quality in zip(MAJOR_SCALE_OFFSETS, MAJOR_SCALE_QUALITIES):
        note = NOTES[(root_index + offset) % 12]
        chords.append(note + quality)

    return chords
