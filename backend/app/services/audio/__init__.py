"""音频分析模块（产品文档 §11.4）：负责"识别"，不做决策。

pipeline.py 串联：预处理 -> BPM -> Key -> 和弦识别 -> 段落检测。
MVP 全部基于 librosa；后续可替换为 madmom / essentia / 自研模型。
"""
