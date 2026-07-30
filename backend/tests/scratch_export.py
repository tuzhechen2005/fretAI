"""验证导出功能：render_markdown / render_pdf 用构造数据跑一遍，不依赖数据库。"""
from app.schemas.arrangement import Arrangement, ArrangedChord
from app.schemas.song import SongAnalysisResult
from app.services.export.markdown import render_markdown
from app.services.export.pdf import render_pdf

analysis = SongAnalysisResult(
    song_id="test-song",
    key="G major",
    bpm=118.5,
    time_signature="4/4",
    chords=[],
)

arrangement = Arrangement(
    arrangement_id="test-arr",
    song_id="test-song",
    type="acoustic_strumming",
    difficulty=4,
    capo=2,
    chords=[
        ArrangedChord(original="F#m", display="Em", fingering="022000", position=0),
        ArrangedChord(original="D", display="C", fingering="x32010", position=0),
        ArrangedChord(original="A", display="G", fingering="320003", position=0),
    ],
    notes="Capo 2 弹 Em-C-G，横按数量最少的方案。",
)

md = render_markdown(analysis, arrangement)
print("=== Markdown ===")
print(md)

pdf_bytes = render_pdf(analysis, arrangement)
print(f"\n=== PDF ===\n{len(pdf_bytes)} bytes, starts with: {pdf_bytes[:8]}")

with open("tests/scratch_export_output.pdf", "wb") as f:
    f.write(pdf_bytes)
print("已写入 tests/scratch_export_output.pdf")
