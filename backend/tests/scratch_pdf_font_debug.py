"""排查 weasyprint 中文渲染异常：分别测试不同字体来源，定位问题范围。"""
from weasyprint import HTML

CASES = {
    "no_font_family": "<html><body><p>木吉他弹唱版 中文测试</p></body></html>",
    "pingfang": '<html><head><style>body{font-family:"PingFang SC";}</style></head><body><p>木吉他弹唱版 中文测试</p></body></html>',
    "heiti": '<html><head><style>body{font-family:"Heiti SC";}</style></head><body><p>木吉他弹唱版 中文测试</p></body></html>',
    "songti": '<html><head><style>body{font-family:"Songti SC";}</style></head><body><p>木吉他弹唱版 中文测试</p></body></html>',
    "stheiti_direct": '<html><head><style>body{font-family:"STHeiti";}</style></head><body><p>木吉他弹唱版 中文测试</p></body></html>',
}

for name, html in CASES.items():
    out_path = f"tests/scratch_font_{name}.pdf"
    HTML(string=html).write_pdf(out_path)
    print(f"{name} -> {out_path}")
