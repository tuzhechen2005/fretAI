"""音频预处理：格式转换（统一为 wav/单声道/22050Hz）、响度标准化。"""


def load_and_normalize(file_path: str):
    raise NotImplementedError  # librosa.load + 归一化
