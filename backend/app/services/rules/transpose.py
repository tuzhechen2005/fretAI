"""和弦转调：整体升降 n 个半音，保留和弦性质（m/7/sus/slash 等）。

示例：B - F# - G#m - E  降 4 半音 ->  G - D - Em - C
"""


def transpose_chord(chord: str, semitones: int) -> str:
    raise NotImplementedError


def transpose_progression(chords: list[str], semitones: int) -> list[str]:
    return [transpose_chord(c, semitones) for c in chords]
