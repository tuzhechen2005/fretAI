"""Power Chord 转换（产品文档 §6.6）：任意和弦 -> 根音 5 和弦。

Power chord 在吉他上是一个"固定形状"，随品格整体平移即可，
不需要像开放和弦那样每个根音单独设计指法：

    6 弦（低音 E 弦）：第 N 品 -> 根音
    5 弦          ：第 N+2 品 -> 五度音

其中 N 就是"这个根音距离 6 弦空弦音 E 有几个半音"。
例如 E5 是 022xxx（N=0），F#5 是 244xxx（N=2），A5 是 577xxx（N=5）。
"""

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def to_power_chord(chord: str, prefer_position: int | None = None) -> dict:
    """返回 {"display": "F#5", "fingering": "244xxx", "position": 2}。"""
    # 这个函数会被 LLM 通过 Tool Use 调用（runner.py 的 func(**args) 直接透传参数），
    # JSON Schema 里声明的类型只是给模型的提示，不是强制校验——实测 qwen3.5-flash
    # 确实会把 prefer_position 传成字符串 "5" 而不是整数 5（ISSUES.md #5）。
    # 在这个系统边界上做一次容错转换，无法转换就当作没提供，不让类型问题让工具崩溃。
    if prefer_position is not None and not isinstance(prefer_position, int):
        try:
            prefer_position = int(prefer_position)
        except (TypeError, ValueError):
            prefer_position = None

    if len(chord) > 1 and chord[1] == "#":
        root = chord[:2]
    else:
        root = chord[:1]

    base_fret = (NOTES.index(root) - NOTES.index("E")) % 12

    if prefer_position is not None:
        # 枚举 base_fret 加减 12 的等效位置（也就是差一个八度），
        # 在合法范围内（0-20 品，多数吉他实际可弹范围），选离 prefer_position 最近的一个
        candidates = [f for f in (base_fret, base_fret + 12, base_fret - 12) if 0 <= f <= 20]
        fret = min(candidates, key=lambda f: abs(f - prefer_position))
    else:
        fret = base_fret

    if fret == 0:
        fingering = "022xxx"
    else:
        fingering = f"{fret}-{fret + 2}-{fret + 2}xxx"

    return {
        "display": root + "5",
        "fingering": fingering,
        "position": fret,
    }


def to_power_chord_batch(chords: list[str], prefer_position: int | None = None) -> list[dict]:
    """对一组和弦批量转换成 power chord，统一使用同一个 prefer_position。

    存在的意义：Editor Agent 在处理大批量和弦进行（比如一首歌 100+ 个和弦）时，
    如果让 LLM 逐个和弦调用 to_power_chord，每次调用都要一次完整的 API 往返，
    会既慢又容易让模型在重复劳动中"偷懒"、编造结果而不是真正调用工具。
    这里把"批量应用同一条确定性规则"收进一次工具调用，LLM 只需要把和弦
    整理成数组传进来，不需要在循环里反复决策。
    """
    return [to_power_chord(chord, prefer_position=prefer_position) for chord in chords]
