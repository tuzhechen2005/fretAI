"""User Guitar Profile（产品文档 §12.3）。MVP 阶段可先用请求参数代替持久化画像。"""
from typing import Literal

from pydantic import BaseModel


class UserGuitarProfile(BaseModel):
    user_id: str | None = None
    main_instrument: Literal["acoustic_guitar", "electric_guitar", "both"] = "both"
    level: Literal["beginner", "lower_intermediate", "intermediate", "advanced"] = "beginner"
    can_barre: bool = False
    knows_pentatonic: bool = False
    preferred_styles: list[str] = []
    tuning: str = "standard"
    goal: Literal["easy", "close_to_original", "singing", "band", "practice"] = "easy"
