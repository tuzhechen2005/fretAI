"""音频预处理：格式转换（统一为 wav/单声道/22050Hz）、响度标准化。"""
import librosa


def load_and_normalize(file_path: str):
    y, sr = librosa.load(file_path)
    return y, sr