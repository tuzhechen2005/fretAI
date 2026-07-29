"""排查：chat 端点用真实歌曲的 130+ 和弦编配测试"改成 power chord"时，
LLM 完全没调用 to_power_chord 工具，直接在 JSON 里抄了原样和弦。

隔离变量：绕开数据库和 HTTP 层，直接调 apply_edit，
用一个只有 4 个和弦的木吉他编配（非 power chord），控制"和弦数量"这一个变量。
"""
import asyncio

from app.schemas.arrangement import Arrangement, ArrangedChord
from app.services.agents.editor import apply_edit


async def main():
    arrangement = Arrangement(
        arrangement_id="test-short",
        song_id="test-song",
        type="acoustic_strumming",
        difficulty=3,
        chords=[
            ArrangedChord(original="F#m", display="F#m", fingering="244222", position=2),
            ArrangedChord(original="D", display="D", fingering="xx0232", position=0),
            ArrangedChord(original="A", display="A", fingering="x02220", position=0),
            ArrangedChord(original="E", display="E", fingering="022100", position=0),
        ],
    )

    new_arrangement, explanation, trace = await apply_edit(arrangement, "改成power chord")

    print("=== trace steps ===")
    for step in trace.steps:
        print(f"role={step.role}")
        for tc in step.tool_calls:
            print(f"  tool={tc.tool_name} args={tc.arguments} result={tc.result}")
        if step.content:
            print(f"  content={step.content}")

    print("\n=== new arrangement chords ===")
    for c in new_arrangement.chords:
        print(c)

    print(f"\n=== explanation ===\n{explanation}")


asyncio.run(main())
