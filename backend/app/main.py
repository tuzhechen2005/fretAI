from dotenv import load_dotenv

# 必须在导入 app.api.router 之前执行：router 会一路 import 到
# services/export/pdf.py 里的 `from weasyprint import HTML`，
# weasyprint 在导入时就要加载系统级 pango/glib 动态库，
# DYLD_LIBRARY_PATH 这类环境变量必须提前生效（见 .env 里的注释）。
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title="FretAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
