from app.services.agents.arrangement import _build_power_chord_arrangement

arrangement = _build_power_chord_arrangement(
    song_id="test-song",
    chords=["F#m", "D", "A", "E"],
)

print("类型:", arrangement.type)
print("难度:", arrangement.difficulty)
print("和弦数量:", len(arrangement.chords))
for c in arrangement.chords:
    print(f"  {c.original} -> {c.display}, 指法 {c.fingering}, 把位 {c.position}")
