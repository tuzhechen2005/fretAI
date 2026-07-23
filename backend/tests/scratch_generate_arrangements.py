import asyncio

from app.schemas.profile import UserGuitarProfile
from app.schemas.song import ChordEvent, SongAnalysisResult
from app.services.agents.arrangement import generate_arrangements


async def main():
    analysis = SongAnalysisResult(
        song_id="test-song",
        key="F# minor",
        bpm=92,
        chords=[
            ChordEvent(start=0.0, end=2.0, chord="F#m", confidence=0.9),
            ChordEvent(start=2.0, end=4.0, chord="D", confidence=0.9),
            ChordEvent(start=4.0, end=6.0, chord="A", confidence=0.9),
            ChordEvent(start=6.0, end=8.0, chord="E", confidence=0.9),
        ],
    )
    profile = UserGuitarProfile()

    arrangements = await generate_arrangements(analysis, profile)

    for a in arrangements:
        print(f"=== {a.type} ===")
        print("难度:", a.difficulty, " Capo:", a.capo)
        print("和弦:", [c.display for c in a.chords])
        print("说明:", a.notes)
        print()


asyncio.run(main())
