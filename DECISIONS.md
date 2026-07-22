# FretAI 技术决策记录

> 面试复习专用：记录"为什么选这个不选那个"，而不是"做了什么"。
> [PROGRESS.md](PROGRESS.md) 追踪进度，这个文件追踪判断和权衡过程。
> 按时间顺序排列，每条包含：最初设想 → 实际决策 → 为什么改 → 代价/权衡。

---

## 1. 数据库：PostgreSQL（产品文档原案）→ SQLite（MVP 实际采用）

**最初设想**：产品文档 §11.3 列出的后端技术栈是 `FastAPI + Celery/RQ + Redis + PostgreSQL + PyTorch + librosa`，按"生产级系统"的标准配置设想——支撑高并发、多用户、复杂查询。

**实际决策**：MVP 阶段改用 SQLite。

**为什么改**：
1. **零运维成本**：PostgreSQL 需要单独启动数据库服务、配置用户名密码、建 database；SQLite 是一个文件，装完 Python 包直接能用。MVP 阶段验证核心功能，不该在数据库运维上花时间。
2. **单机场景足够**：本地开发/演示阶段没有真实并发写入压力，SQLite 单文件完全够用。
3. **迁移路径清晰、代价小**：因为从一开始就用 **SQLAlchemy ORM**（`app/db/models.py` 里的 `class Song(Base): ...`），业务代码从未手写过 SQL，全部通过 ORM 的 Python API 操作数据库。换数据库理论上只需要改 `DATABASE_URL` 这一行连接字符串（`sqlite+aiosqlite:///./fretai.db` → `postgresql+asyncpg://user:pass@host/db`），模型定义和业务逻辑代码不用动。

**代价/权衡**：SQLite 不支持真正的高并发写入（写操作会锁表），不适合生产多用户场景；如果以后真的要上生产，需要迁移到 PostgreSQL 并处理好数据搬迁、语法方言差异（比如 JSON 类型在两者中的支持程度不同）。

**面试话术**：先讲清楚"为什么最初文档写的是 Postgres"，再讲"MVP 阶段主动降级为什么合理"，最后强调"因为用了 ORM，这个决策是可逆的、迁移成本低"——这展示的是"审慎的技术判断"而不是"图省事"。

---

## 2. 分析结果存储：关系表拆分 → JSON 列

**最初设想**：把 `SongAnalysisResult`（调性、BPM、和弦时间轴、段落结构等嵌套数据）拆成规范的多张关系表（比如单独一张 chords 表、一张 sections 表，用外键关联 song_id）。

**实际决策**：直接把整个分析结果序列化成 JSON，存进 `songs.analysis` 这一个字段（`app/db/models.py`）。

**为什么改**：MVP 阶段对这份数据的访问模式几乎全是"整体读出、整体展示给前端"，很少需要"单独查询某一个和弦"这种细粒度操作。一开始就拆多表会引入当前用不上的复杂度（多表 JOIN、外键维护、级联更新），属于过度设计（这是一种 **YAGNI** 判断——You Aren't Gonna Need It）。

**代价/权衡**：牺牲了"对 JSON 内部字段做高效 SQL 查询"的能力（比如"查询所有包含 Am 和弦的歌"这类需求，JSON 列比关系表查询起来慢、也更别扭）。代码注释里也明确写了"换 PostgreSQL 后可迁移为 JSONB"，作为已知的未来优化方向。

**面试话术**：主动承认这是权衡不是"最优解"，展示你算过账、知道代价在哪、也想好了后续演进路径（JSONB）。

---

## 3. 任务队列：Celery + Redis（产品文档原案）→ FastAPI BackgroundTasks（MVP 阶段，尚未实现）

**最初设想**：音频分析是耗时操作，产品文档建议用 Celery（分布式任务队列）+ Redis（消息中间件）做异步处理，支持水平扩展、任务重试、多 worker 并发。

**计划中的决策**：MVP 阶段用 FastAPI 内置的 `BackgroundTasks` 代替。

**为什么改**：单机 MVP 场景，分析任务串行执行完全跑得动，不需要引入 Redis 这个额外的中间件依赖、也不需要维护独立的 Celery worker 进程。`BackgroundTasks` 是 FastAPI 自带的能力，请求处理完可以立刻返回给用户，同时在后台继续跑分析任务，不用引入新组件。

**代价/权衡**：`BackgroundTasks` 没有任务持久化（如果服务重启，正在跑的后台任务会丢失，用户需要重新触发分析）、没有重试机制、也不能跨进程/跨机器扩展。如果以后要支持多用户高并发同时上传分析，需要迁回 Celery + Redis 这套方案。

**面试话术**：这是一条还没真正实现但已经想清楚的决策，可以讲"我知道生产级方案是什么，但 MVP 阶段判断这个复杂度暂时不需要"。

---

## 4. 音频处理库：madmom / essentia（产品文档原案）→ librosa（MVP 计划采用）

**最初设想**：产品文档提到 madmom、essentia 这些更专业的音乐信息检索（MIR）库，功能更强（比如 madmom 的节拍检测在学术界评测中往往更准）。

**计划中的决策**：MVP 统一用 librosa。

**为什么改**：librosa 是 Python 音频处理生态里最主流、文档最全、安装最简单的库（纯 Python + 常见科学计算依赖，不需要编译 C++ 扩展）；madmom 和 essentia 安装门槛更高（尤其在 macOS 上编译依赖容易踩坑），MVP 阶段先用 librosa 覆盖 BPM、Key、chroma 特征、和弦模板匹配等核心需求，能满足功能验证目的。

**代价/权衡**：某些任务上 librosa 的开箱效果可能不如专门优化过的 madmom（比如更复杂的节拍跟踪场景），这是"能跑起来、验证产品概念"和"识别精度最优"之间的权衡，符合 MVP 阶段"先验证核心差异化，不追求单点最优"的整体目标（产品文档 §10.1 原话）。

---

## 5. Python 运行环境：pyenv 3.9.18 → 系统 Python 3.14

**背景**：本机同时装着 pyenv 管理的 Python 3.9.18 和系统自带的 Python 3.14（`/Library/Frameworks/Python.framework/...`）。项目最初用 pyenv 3.9.18 建的 `.venv`。

**踩的坑**：`app/schemas/` 里大量使用了 `int | None` 这种"联合类型"写法（PEP 604），这是 **Python 3.10 才引入**的语法。3.9 环境下运行会报 `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`。

**实际决策**：删除旧 `.venv`，改用系统 Python 3.14 重建（`rm -rf .venv && /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m venv .venv`）。

**为什么这么修，而不是把代码改成兼容 3.9 的写法（比如用 `Optional[int]` 代替 `int | None`）**：3.14 已经装在本机、不需要额外安装任何东西；改代码兼容旧语法属于"向后拉低标准"，而升级环境是"一次性成本、长期受益"，且 `|` 联合类型写法更简洁、是现在 Python 社区的主流写法。

**衍生的坑（同类问题的第二次踩坑）**：环境重建后是"干净"的，之前装过的第三方库（`sqlalchemy`、`aiosqlite`、`greenlet` 等）需要重新安装。第一次运行数据库相关代码时依次报了 `ModuleNotFoundError: No module named 'sqlalchemy'` → 装上后又报 `No module named 'greenlet'`（SQLAlchemy 异步模式底层依赖 greenlet 做协程调度，但不总是被自动装上）。**通用排障方法论**：`ModuleNotFoundError` 的排查第一反应不是怀疑代码逻辑，而是先确认当前虚拟环境里有没有装这个包（`which python` 确认在哪个环境、`pip list` 或直接 `pip install` 补装）。

**面试话术**：这条更适合放进"工程排障能力"而不是"架构设计"里讲——展示你遇到环境报错时，能快速定位是"版本不兼容"还是"依赖缺失"，而不是瞎猜。

---

## 6. Agent 架构粒度：细粒度多 Agent → 少数几个大类 Agent + 共享 Tools

**最初设想（来自产品文档 §7）**：7 个职责明确的 Agent（Audio Analysis / Music Theory / Guitar Arrangement / Fingering / Style / Practice Coach / Export）。

**讨论中曾经的疑虑**：要不要为更细的小功能（比如"横按判断""capo 品格计算"）也各自单独建一个 agent？

**最终决策（2026-07-13 确定）**：保留产品文档原本的 7 个 Agent 划分，不合并也不再往下拆更细的子 agent。所有细粒度、确定性的计算（转调、capo 推荐、power chord 转换、难度评分等）都停留在 `app/services/rules/` 这一层，作为 **tool** 被这 7 个 Agent 通过 Tool Use 按需调用，而不是各自再包装成独立的 agent。

**为什么这么判断（用户自己想清楚的）**：如果给每个小功能都建一个独立 agent，会导致：
1. 任务量随功能数量线性暴增，难以管理；
2. 多 agent 之间需要互相通信、同步状态，这是 multi-agent 系统公认的痛点（协调开销、调试困难、任何一环出错都难以定位是哪个 agent 的责任）；
3. 而单个 agent 内部通过 Tool Use 调用多个工具，本质上是"一个决策者、多个确定性工具"的模式，LLM 完全有能力在一次推理里自己判断该调用哪个工具、什么时候调用，不需要人为拆分成多个"角色"。

**架构原则总结**：规则系统负责算"事实"（确定性、可复现、不依赖 LLM），Agent 负责在这些事实基础上"做决策 + 用自然语言解释"。LLM 不直接猜测和弦指法这类需要精确计算的内容。

**面试话术**：这条是这个项目最能体现"AI 应用工程判断力"的决策——不是无脑串起多个 agent 摆酷，而是清楚"LLM 该做什么、不该做什么"，以及"哪些复杂度是真实存在的、哪些是自己制造出来的"。

---

## 决策记录写作习惯

以后每做一次"改变了原计划"的技术选型，或者踩到一个值得记住的坑，都补一条到这里，格式保持一致：**最初设想 → 实际决策 → 为什么改 → 代价/权衡 → （可选）面试话术**。跟 [PROGRESS.md](PROGRESS.md) 一起提交进 git，两个文件分工不同：PROGRESS 看"做到哪了"，这个文件看"为什么这么做、学到了什么"。
