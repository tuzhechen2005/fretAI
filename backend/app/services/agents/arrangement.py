"""Guitar Arrangement Agent（产品文档 §7.3）。

输入分析结果 + 用户画像，输出多个 Arrangement：
- 决策部分（选哪些版本、capo、目标把位）由 LLM 给出结构化参数；
- 具体指法、难度分数由规则系统计算（rules/capo、power_chord、positions、difficulty）；
- notes 字段由 LLM 生成"为什么这么编"的解释（产品文档 §10.2-10）。
"""
from app.schemas.arrangement import Arrangement
from app.schemas.profile import UserGuitarProfile
from app.schemas.song import SongAnalysisResult


async def generate_arrangements(
    analysis: SongAnalysisResult,
    profile: UserGuitarProfile,
) -> list[Arrangement]:
    raise NotImplementedError
