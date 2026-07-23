"""难度评分（产品文档 §13）：横按数、把位跨度、平均换把距离、
和弦复杂度、特殊技巧、特殊调弦等维度加权，输出 1-10 分与原因列表。
"""


def score_difficulty(voicings: list[dict], techniques: list[str]) -> tuple[int, list[str]]:
    """返回 (score, reasons)。"""
    score = 1  # 基础分：哪怕全是开放和弦，也不该是 0 分
    reasons = []

    barre_count = sum(1 for v in voicings if v["barre"])
    if barre_count > 0:
        score += barre_count * 2
        reasons.append(f"包含 {barre_count} 个横按")

    positions = [v["position"] for v in voicings]
    span = max(positions) - min(positions)
    if span > 5:
        score += 2
        reasons.append(f"最大把位跨度 {span} 品，换把较大")

    if techniques:
        score += len(techniques)
        reasons.append(f"需要额外技巧：{', '.join(techniques)}")

    score = min(score, 10)  # 封顶 10 分
    return score, reasons
