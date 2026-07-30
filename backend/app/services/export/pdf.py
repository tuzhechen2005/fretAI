"""PDF 导出：复用 render_markdown 的内容，转成 HTML 后用 weasyprint 渲染成 PDF。

最初设想是 reportlab（见 requirements.txt 早期版本），实际改用 markdown+weasyprint：
reportlab 是坐标式绘图 API，表格/排版都要手写；markdown->HTML->PDF 能直接复用
render_markdown 已经写好的拼装逻辑，样式用 CSS 描述，改起来更直观，见 DECISIONS.md。
"""
import markdown as markdown_lib
from weasyprint import HTML

from app.schemas.arrangement import Arrangement
from app.schemas.song import SongAnalysisResult
from app.services.export.markdown import render_markdown

PDF_STYLE = """
<style>
  /* -apple-system 是 WebKit 私有字体关键字，weasyprint 底层用的是标准 CSS 引擎
     （非浏览器内核），不认识这个值——直接写系统里实际装的中文字体名。 */
  body { font-family: "PingFang SC", "Heiti SC", sans-serif; padding: 2em; }
  h1 { font-size: 1.5em; }
  h2 { font-size: 1.1em; margin-top: 1.5em; color: #444; }
  table { border-collapse: collapse; width: 100%; margin-top: 0.5em; }
  th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 0.9em; }
  th { background: #f5f5f5; }
  blockquote { color: #666; border-left: 3px solid #ddd; padding-left: 1em; margin-left: 0; }
</style>
"""


def render_pdf(analysis: SongAnalysisResult, arrangement: Arrangement) -> bytes:
    md_text = render_markdown(analysis, arrangement)
    body_html = markdown_lib.markdown(md_text, extensions=["tables"])
    # 缺 charset 声明时 weasyprint 会按默认编码猜测解析字符串，导致多字节
    # UTF-8 中文字符被从中间拆开、渲染成乱码/字符丢失，必须显式声明。
    full_html = (
        f"<!DOCTYPE html><html><head><meta charset=\"utf-8\">{PDF_STYLE}</head>"
        f"<body>{body_html}</body></html>"
    )
    return HTML(string=full_html).write_pdf()
