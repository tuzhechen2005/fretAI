"""和弦转调：整体升降 n 个半音，保留和弦性质（m/7/sus/slash 等）。

示例：B - F# - G#m - E  降 4 半音 ->  G - D - Em - C
"""

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# 降号根音统一翻译成等音的升号写法（Ab == G#），
# 这样 NOTES.index(root) 只需要认识升号一种记法。
FLAT_TO_SHARP = {
    "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#",
}


def transpose_chord(chord: str, semitones: int) -> str:
    # 第一步：判断根音是 1 个字符还是 2 个字符
    # 根音带升号（#）或降号（b）时是 2 个字符
    if len(chord) > 1 and chord[1] in ("#", "b"):
        root = chord[:2]      # 取前两个字符，比如 "F#" 或 "Ab"
        quality = chord[2:]   # 剩下的部分，比如 "m"
    else:
        root = chord[:1]      # 只取前 1 个字符
        quality = chord[1:]   # 剩下的部分

    root = FLAT_TO_SHARP.get(root, root)  # 降号 -> 升号，其余不变

    index = (NOTES.index(root) + semitones) % 12
    new_root = NOTES[index]
    return new_root + quality


def transpose_progression(chords: list[str], semitones: int) -> list[str]:
    return [transpose_chord(c, semitones) for c in chords]
