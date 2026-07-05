"""音频分析总入口：由后台任务调用，产出 SongAnalysisResult。"""
from app.schemas.song import SongAnalysisResult


async def analyze_song(song_id: str, file_path: str) -> SongAnalysisResult:
    """预处理 -> BPM/beat -> Key -> chord recognition -> section detection。

    各步骤见同目录 preprocess / bpm / key / chords / sections。
    """
    raise NotImplementedError
