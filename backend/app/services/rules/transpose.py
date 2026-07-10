"""和弦转调：整体升降 n 个半音，保留和弦性质（m/7/sus/slash 等）。

示例：B - F# - G#m - E  降 4 半音 ->  G - D - Em - C
"""


def transpose_chord(chord: str, semitones: int) -> str:
    NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    # 第一步：判断根音是 1 个字符还是 2 个字符
    # 提示：根音带升号的情况，第二个字符是 "#"
    if len(chord) > 1 and chord[1] == "#":
        root = chord[:2]      # 取前两个字符，比如 "F#"
        quality = chord[2:]   # 剩下的部分，比如 "m"
    else:
        root = chord[:1]      # 只取前 1 个字符
        quality = chord[1:]   # 剩下的部分

    index = (NOTES.index(root) + semitones) % 12
    new_root = NOTES[index]
    return new_root + quality


def transpose_progression(chords: list[str], semitones: int) -> list[str]:
    return [transpose_chord(c, semitones) for c in chords]
