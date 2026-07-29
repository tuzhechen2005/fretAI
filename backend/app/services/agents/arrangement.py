"""Guitar Arrangement Agent（产品文档 §7.3）。

输入分析结果 + 用户画像，输出多个 Arrangement：
- 决策部分（选哪些版本、capo、目标把位）由 LLM 给出结构化参数；
- 具体指法、难度分数由规则系统计算（tools/capo、power_chord、positions、difficulty）；
- notes 字段由 LLM 生成"为什么这么编"的解释（产品文档 §10.2-10）。
"""
from app.schemas.profile import UserGuitarProfile
from app.schemas.song import SongAnalysisResult
from app.schemas.trace import AgentTrace
import uuid
from app.schemas.arrangement import Arrangement, ArrangedChord
from app.services.tools.capo import recommend_capo
from app.services.tools.power_chord import to_power_chord
from app.services.tools.voicings import get_voicings
from app.services.tools.difficulty import score_difficulty
import json
from app.services.agents.runner import run_agent_with_tools



NOTES_SYSTEM_PROMPT = """你是一个吉他编配助手。给你两个已经计算好的吉他编配方案（木吉他弹唱版、电吉他 Power Chord 版），
请分别写一句话解释"为什么这样编配对用户有帮助"（比如提到横按情况、难度、适合的场景）。

只返回 JSON，格式：
{"acoustic_notes": "...", "power_chord_notes": "..."}
"""

def _build_acoustic_arrangement(song_id: str, key: str, chords: list[str]) -> Arrangement:
    capo_options = recommend_capo(key, chords)
    best = capo_options[0]  # 已经排好序了，第一个是横按最少的方案

    arranged_chords = []
    voicings_for_difficulty = []
    for chord in best["played_chords"]:
        voicings = get_voicings(chord)
        open_voicing = next((v for v in voicings if v["kind"] == "open"), voicings[0] if voicings else None)
        if open_voicing is None:
            continue
        voicings_for_difficulty.append(open_voicing)
        arranged_chords.append(
            ArrangedChord(
                original=chord,
                display=chord,
                fingering=open_voicing["fingering"],
                position=open_voicing["position"],
            )
        )

    difficulty, _ = score_difficulty(voicings_for_difficulty, [])

    return Arrangement(
        arrangement_id=str(uuid.uuid4()),
        song_id=song_id,
        type="acoustic_strumming",
        difficulty=difficulty,
        capo=best["capo"],
        chords=arranged_chords,
    )

def _build_power_chord_arrangement(song_id: str, chords: list[str]) -> Arrangement:
    arranged_chords = []
    voicings_for_difficulty = []

    for chord in chords:
        power = to_power_chord(chord)
        arranged_chords.append(
            ArrangedChord(
                original=chord,
                display=power["display"],
                fingering=power["fingering"],
                position=power["position"],
            )
        )
        voicings_for_difficulty.append(
            {"barre": False, "position": power["position"]}
        )

    difficulty, _ = score_difficulty(voicings_for_difficulty, [])

    return Arrangement(
        arrangement_id=str(uuid.uuid4()),
        song_id=song_id,
        type="electric_power_chord",
        difficulty=difficulty,
        chords=arranged_chords,
    )



async def generate_arrangements(
    analysis: SongAnalysisResult,
    profile: UserGuitarProfile,
) -> tuple[list[Arrangement], AgentTrace]:
    song_id = analysis.song_id
    key = analysis.key
    chords = [c.chord for c in analysis.chords]

    acoustic = _build_acoustic_arrangement(song_id, key, chords)
    power_chord = _build_power_chord_arrangement(song_id, chords)

    summary = (
        f"木吉他弹唱版：capo {acoustic.capo}，难度 {acoustic.difficulty}/10，"
        f"和弦：{[c.display for c in acoustic.chords]}\n"
        f"电吉他 Power Chord 版：难度 {power_chord.difficulty}/10，"
        f"和弦：{[c.display for c in power_chord.chords]}"
    )
    trace = await run_agent_with_tools(
        system_prompt=NOTES_SYSTEM_PROMPT,
        user_message=summary,
        tools=[],
        tool_functions={},
        response_format={"type": "json_object"},
    )
    notes = json.loads(trace.final_content)

    acoustic.notes = notes["acoustic_notes"]
    power_chord.notes = notes["power_chord_notes"]

    return [acoustic, power_chord], trace
