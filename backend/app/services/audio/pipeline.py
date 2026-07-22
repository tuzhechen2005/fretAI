"""音频分析总入口：由后台任务调用，产出 SongAnalysisResult。"""
from app.schemas.song import SongAnalysisResult
from app.services.audio.preprocess import load_and_normalize
from app.services.audio.bpm import detect_bpm
from app.services.audio.key import detect_key
from app.services.audio.chords import recognize_chords
from app.services.audio.sections import detect_sections


async def analyze_song(song_id: str, file_path: str) -> SongAnalysisResult:
    """预处理 -> BPM/beat -> Key -> chord recognition -> section detection。

    各步骤见同目录 preprocess / bpm / key / chords / sections。
    """
    y, sr = load_and_normalize(file_path)
    bpm, beat_times = detect_bpm(y, sr)
    key, key_confidence = detect_key(y, sr)
    chords = recognize_chords(y, sr, beat_times)
    sections = detect_sections(y, sr)

    return SongAnalysisResult(
        song_id=song_id,
        key=key,
        bpm=bpm,
        sections=sections,
        chords=chords,
    )