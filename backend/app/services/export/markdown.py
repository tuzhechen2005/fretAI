"""Markdown 和弦谱导出（产品文档 §6.13 MVP 范围）。

输出：歌曲信息（Key/BPM/Capo/调弦）+ 和弦进行表格 + 编配说明。
不需要 LLM 参与——纯格式转换，见 DECISIONS.md #14（为什么 Export 不做成 Agent）。
"""
from app.schemas.arrangement import Arrangement
from app.schemas.song import SongAnalysisResult

TYPE_LABEL = {
    "acoustic_beginner": "木吉他新手版",
    "acoustic_strumming": "木吉他弹唱版",
    "electric_power_chord": "电吉他 Power Chord 版",
    "electric_original": "原曲感电吉他版",
    "high_position_triads": "高把位三和弦版",
}


def render_markdown(analysis: SongAnalysisResult, arrangement: Arrangement) -> str:
    lines = [
        f"# {TYPE_LABEL.get(arrangement.type, arrangement.type)}",
        "",
        f"- **Key**：{analysis.key}",
        f"- **BPM**：{round(analysis.bpm)}",
        f"- **拍号**：{analysis.time_signature}",
        f"- **难度**：{arrangement.difficulty}/10",
    ]
    if arrangement.capo is not None:
        lines.append(f"- **Capo**：第 {arrangement.capo} 品")
    lines.append(f"- **调弦**：{arrangement.tuning}")
    lines.append("")

    if arrangement.notes:
        lines.append(f"> {arrangement.notes}")
        lines.append("")

    lines.append("## 和弦进行")
    lines.append("")
    lines.append("| # | 和弦 | 指法 | 把位 |")
    lines.append("|---|------|------|------|")
    for i, chord in enumerate(arrangement.chords, start=1):
        lines.append(f"| {i} | {chord.display} | `{chord.fingering or '—'}` | {chord.position} |")

    return "\n".join(lines)
