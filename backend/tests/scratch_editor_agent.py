import asyncio

from app.schemas.arrangement import Arrangement, ArrangedChord
from app.services.agents.editor import apply_edit


async def main():
    arrangement = Arrangement(
        arrangement_id="test-arr",
        song_id="test-song",
        type="acoustic_strumming",
        difficulty=1,
        chords=[
            ArrangedChord(original="F#m", display="F#m", fingering="244222", position=2),
            ArrangedChord(original="D", display="D", fingering="xx0232", position=0),
            ArrangedChord(original="A", display="A", fingering="x02220", position=0),
            ArrangedChord(original="E", display="E", fingering="022100", position=0),
        ],
    )

    print("=== 测试 1：降两调 ===")
    new_arr, explanation = await apply_edit(arrangement, "降两调")
    print("新和弦:", [c.original for c in new_arr.chords])
    print("说明:", explanation)
    print("原始 arrangement 有没有被改动:", [c.original for c in arrangement.chords])

    print()
    print("=== 测试 2：改成 power chord ===")
    new_arr2, explanation2 = await apply_edit(arrangement, "改成 power chord")
    print("新和弦:", [(c.original, c.display, c.fingering, c.position) for c in new_arr2.chords])
    print("说明:", explanation2)


asyncio.run(main())
