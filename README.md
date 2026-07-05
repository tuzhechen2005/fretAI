# FretAI

面向吉他手的 AI 扒带与编配 Agent。**不是只告诉你是什么和弦，而是告诉你怎么弹。**

> 产品详情见 [产品文档.md](./产品文档.md)。当前阶段：**Phase 1 可演示 MVP**（前后端分离 Web 版，暂不做移动 App）。

## 项目结构

```
fretAI/
├── 产品文档.md
├── frontend/                  # Next.js + Tailwind + Web Audio API
│   └── src/
│       ├── app/               # 页面路由
│       │   ├── page.tsx                     # 首页：上传音频 + 选择目标
│       │   └── songs/[id]/
│       │       ├── page.tsx                 # 分析页：波形 + 和弦时间轴 + 播放控制
│       │       └── arrangements/page.tsx    # 编配页：多版本对比 + 自然语言修改 + 导出
│       ├── components/
│       │   ├── player/        # 音频播放、波形、变速、循环
│       │   ├── timeline/      # 和弦时间轴（随播放高亮）
│       │   ├── chord/         # 和弦图（指法 diagram）
│       │   └── fretboard/     # 指板可视化（Phase 2）
│       ├── lib/               # API client、音频工具
│       └── types/             # 与后端 schema 对应的 TS 类型
│
└── backend/                   # Python + FastAPI
    ├── app/
    │   ├── main.py            # 应用入口
    │   ├── core/              # 配置
    │   ├── api/endpoints/     # 路由：songs / analysis / arrangements / chat / export
    │   ├── schemas/           # Pydantic 模型（对应产品文档 §12 数据结构）
    │   ├── db/                # SQLAlchemy（MVP 用 SQLite，后续换 PostgreSQL）
    │   └── services/
    │       ├── audio/         # 音频分析：预处理、BPM、Key、和弦识别、段落检测
    │       ├── agents/        # LLM Agent：乐理纠错、编配、指法、解释、自然语言修改
    │       ├── rules/         # 规则系统：转调、Capo 推荐、Power Chord、把位库、难度评分
    │       └── export/        # 导出：Markdown / PDF
    ├── storage/uploads/       # 上传音频存放（MVP 本地文件，后续换对象存储）
    └── tests/
```

## 架构分工（对应产品文档 §11.5）

```
音频模型负责识别（services/audio）
规则系统负责约束（services/rules）
Agent 负责决策和解释（services/agents）
```

## MVP 范围（对应产品文档 §10.2）

- [ ] 音频上传
- [ ] Key / BPM 识别
- [ ] 和弦时间轴
- [ ] 一键升调 / 降调
- [ ] 木吉他低把位版 + Capo 推荐
- [ ] 电吉他 Power Chord 版
- [ ] 多把位和弦图
- [ ] Agent 解释编配原因
- [ ] 自然语言修改编配
- [ ] 导出 Markdown / PDF

## MVP 技术简化决策

| 文档建议 | MVP 实际采用 | 原因 |
|---|---|---|
| PostgreSQL | SQLite | 单机可跑，零配置，SQLAlchemy 后续无缝迁移 |
| Celery + Redis | FastAPI BackgroundTasks | 分析任务单机串行即可，避免引入中间件 |
| Object Storage | 本地 `storage/uploads/` | Demo 阶段够用 |
| madmom / essentia | librosa | 依赖简单，BPM/Key/Chroma 均可覆盖 |

## 本地开发

### 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 填入 ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

访问：http://localhost:3000
