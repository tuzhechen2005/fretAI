from app.services.rules.transpose import transpose_progression
from app.services.rules.capo import recommend_capo
from app.services.rules.power_chord import to_power_chord
from app.services.rules.voicings import get_voicings
from app.services.rules.difficulty import score_difficulty

# 场景：产品文档 §9.2 的例子，F#m - D - A - E
original_chords = ["F#m", "D", "A", "E"]

print("=== 原和弦 ===")
print(original_chords)

print("\n=== 降四个半音之后 ===")
print(transpose_progression(original_chords, -4))

print("\n=== 推荐的变调夹 ===")
for r in recommend_capo("F# minor", original_chords)[:3]:
    print(r)

print("\n=== 4. 电吉他 Power Chord 版 ===")
power_versions = [to_power_chord(c) for c in original_chords]
for p in power_versions:
    print(p)

print("\n=== 5. Am 的所有指法 + 难度评分 ===")
am_voicings = get_voicings("Am")
print(am_voicings)
print("难度:", score_difficulty(am_voicings, []))