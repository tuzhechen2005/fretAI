"""调性检测：chroma 特征 + Krumhansl-Schmuckler key profile 相关性。

思路：
1. 用 librosa 算出这首歌 12 个音高类别（不分八度）各自的强度分布（chroma）。
2. 分别跟 24 种调（12 大调 + 12 小调）的"理论音高分布模板"做相关性比较，
   最相关的那个就是最可能的调性。模板来自 Krumhansl-Schmuckler key-finding
   算法（音乐心理学研究总结的、每种调里各音出现频率的经验分布）。
"""
import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Krumhansl-Schmuckler 的大调/小调音高分布模板（C 大调 / C 小调为基准，
# 其余调通过循环移位得到）。
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)


def detect_key(y, sr) -> tuple[str, float]:
    """返回 (key, confidence)，如 ("E minor", 0.87)。"""
    # 只用歌曲中段 60%（掐头去尾各 20%），减少前奏/尾奏等
    # 和声不明确段落对整体 chroma 分布的干扰
    total_len = len(y)
    start = int(total_len * 0.2)
    end = int(total_len * 0.8)
    y_trimmed = y[start:end]

    chroma = librosa.feature.chroma_cqt(y=y_trimmed, sr=sr)
    chroma_mean = chroma.mean(axis=1)  # 对中段取平均，得到 12 个音高类别的强度

    best_key = None
    best_score = -1.0
    all_scores = []

    for shift in range(12):
        major_template = np.roll(MAJOR_PROFILE, shift)
        minor_template = np.roll(MINOR_PROFILE, shift)

        major_score = np.corrcoef(chroma_mean, major_template)[0, 1]
        minor_score = np.corrcoef(chroma_mean, minor_template)[0, 1]

        all_scores.append(major_score)
        all_scores.append(minor_score)

        if major_score > best_score:
            best_score = major_score
            best_key = f"{NOTE_NAMES[shift]} major"
        if minor_score > best_score:
            best_score = minor_score
            best_key = f"{NOTE_NAMES[shift]} minor"

    # 用"最佳得分相对其余得分的领先程度"近似表示置信度，压到 0-1 区间
    confidence = float((best_score - np.mean(all_scores)) / (np.std(all_scores) + 1e-9))
    confidence = max(0.0, min(1.0, confidence / 3))  # 粗略归一化，避免超出 0-1

    return best_key, confidence
