# FretAI 开发进度

> 每完成一项就把 `[ ]` 改成 `[x]`，并更新顶部总体进度。这个文件跟代码一起提交，跨会话可查。

**总体进度：约 65%**（里程碑 2、3、4 完成；里程碑 5 Agent 层：LLM API 调用 + Tool Use 机制均已打通）

---

## 里程碑 1：后端能跑起来（地基）
- [x] 项目骨架搭建（FastAPI + Next.js）
- [x] 后端 venv 环境跑通，`/health` 接口可访问
- [ ] `/docs` 页面理解（路由 vs 实现的区别）

## 里程碑 2：规则系统（services/rules/，纯 Python，无 AI 无数据库）
依赖关系：voicings（数据基础）← transpose（独立算法）← power_chord / capo（依赖前两者）
- [x] `transpose.py` — 单个和弦转调 `transpose_chord`
- [x] 把 `transpose_chord` 接到一个调试用 API 接口，用 curl 验证跑通
- [x] `voicings.py` — 和弦指法库（7 个常用开放和弦：C/D/E/G/A/Am/Em/Dm）
- [x] `power_chord.py` — Power Chord 转换（用 6 弦品格公式计算，覆盖全部 12 根音，不依赖指法库）
- [x] `capo.py` — Capo 推荐（枚举 0-7 品 + 按横按数排序，发现并修复了降号根音 bug）
- [x] `difficulty.py` — 难度评分（横按数 + 把位跨度 + 技巧数加权，已验证）
- [ ] `positions.py` — 把位优化算法（**跳过，放到最后有余力再做**；涉及动态规划，是规则系统里最难的一块，不是必需品）

## 里程碑 3：音频上传 + 数据库（用户自己写——通用 Web 后端技能，与 Agent 无关但重要）
- [x] SQLite 建表（Song、Arrangement），建表脚本 `app/db/init_db.py`
- [x] 上传接口：接收音频文件，存本地 + 存数据库记录（curl -F 验证跑通）
- [x] 查询接口：根据 song_id 返回歌曲状态（含 404 情况验证）
- [x] 音频流接口：`GET /songs/{id}/audio`，用 FastAPI FileResponse 支持 Range 请求，curl 下载验证字节数一致

## 里程碑 4：音频分析（services/audio/，librosa）—— AI 多带写，重点讲输入输出含义
- [x] `preprocess.py` — librosa.load 读取音频，返回 (y, sr)（已用真实 mp3 验证，时长/采样率符合预期）
- [x] `bpm.py` — librosa.beat.beat_track 检测 BPM + 节拍时间点（已验证：117.45 BPM，接近 Thriller 真实 BPM 118-119；踩坑：新版 librosa 返回 tempo 是 numpy 数组不是纯 float，需要 .item() 转换）
- [x] `key.py` — chroma 特征 + Krumhansl-Schmuckler 模板匹配（已用合成 C 大三和弦测试音验证代码逻辑正确；真实歌曲 Thriller 检测偏差，判断为算法在复杂混音下的已知局限，详见 DECISIONS.md #7）
- [x] `chords.py` — 按拍切片 + 24 种和弦模板（12大三+12小三）点积匹配 + 合并相邻同和弦（已用合成 C→G 和弦切换测试音验证：切换点精确，置信度 0.85 远高于 Thriller 真实数据的 0.27-0.31，确认低置信度是真实信号非 bug，详见 DECISIONS.md #8）
- [x] `sections.py` — librosa.segment.agglomerative 聚类切段，固定 6 段，name 留空交给 Agent 层贴标签（已用 Thriller 验证：首尾相接总时长吻合，段落长度不均匀但符合"够用就好"的定位，详见 DECISIONS.md #9）
- [x] 接入 BackgroundTasks，串成完整 pipeline（upload_song 存文件建记录后立刻返回 pending，后台任务跑 analyze_song，依次经过 analyzing -> done/failed，结果序列化存进 Song.analysis；端到端验证：上传 -> 轮询状态 -> 直接查库确认 analysis 字段内容完整）

## 里程碑 5：Agent 层（⭐ 用户明确的重点，会拆到最细）

**架构原则（2026-07-13 讨论确定）**：
1. 规则系统算"事实"（确定性、可复现），Agent 负责在事实里"挑选和解释"，不让 LLM 直接猜测和弦指法这类需要精确计算的内容。
2. **保留产品文档 §7 原本的 7 个 Agent 划分（不合并、不再拆细）**：Audio Analysis / Music Theory / Guitar Arrangement / Fingering / Style / Practice Coach / Export。每个 Agent 对应一个明确的"决策职责"，粒度是合适的。
3. **不要为每个小功能单独开一个 agent**（比如不能有"横按判断 agent""品格计算 agent"这种）。细粒度功能永远停留在 tool 这一层——也就是 `rules/` 目录下已经写好的函数（transpose_chord / recommend_capo / to_power_chord / score_difficulty / get_voicings 等）。7 个 Agent 内部通过 Tool Use 按需调用这些函数，而不是互相之间再发消息、再拆子 agent。这样避免了 multi-agent 系统常见的通信复杂度暴增、调试困难的问题。

- [x] 打通一次最基础的 LLM API 调用（阿里云百炼 qwen3.5-flash，OpenAI 兼容接口，AsyncOpenAI 客户端，已验证 chat.completions.create 端到端跑通）
- [x] 理解 Tool Use：先跑通单工具版本，再升级到 to_power_chord + recommend_capo 双工具版本，用 TOOL_FUNCTIONS 字典按 tool_call.function.name 动态路由到真实函数。已验证模型能根据工具 description 正确区分"转 power chord"和"推荐 capo"两种意图（backend/tests/scratch_tool_use.py）
- [ ] Music Theory Agent：低置信度和弦纠错
- [ ] Guitar Arrangement Agent：生成多版本编配 + 解释原因（会用到 capo/power_chord/difficulty 的输出）
- [ ] Fingering Agent：把用户的把位要求转成规则系统参数
- [ ] Editor：自然语言修改编配（"降两调""换低把位"）

## 里程碑 6：前端页面
- [ ] 上传组件 + 跳转分析页
- [ ] 和弦时间轴展示（含播放高亮）
- [ ] 编配页：多版本卡片 + 和弦图
- [ ] 自然语言修改输入框

## 里程碑 7：导出 + 收尾
- [ ] Markdown 导出
- [ ] PDF 导出
- [ ] 完整走一遍：上传 → 分析 → 编配 → 修改 → 导出
- [ ] 简历项目描述打磨（对照产品文档 §17）

---

## 已知局限（备忘，面试可诚实提及）
- `recommend_capo` 目前只按"横按数量"排序，没有惩罚"capo 品数过高"（比如 capo=6 这种实际很少用的方案，会和 capo=1 并列最优）。后续可以给 `barre_count` 加一个"capo 越大惩罚越多"的权重。
- `transpose_chord` 统一把降号（b）翻译成升号（#）表示，输出不会保留原始的降号记谱习惯（比如 Ab 调的和弦转出来会显示成 G# 而不是 Ab）。
- `recommend_capo(key, chords)` 的 `key` 参数目前完全没有在函数体内被使用（只用了 `chords`），是个"看起来需要但实际没用上"的参数，Tool Use 测试中意外发现（模型传了简化过的 key 值也不影响结果，因为反正没用到）。后续要么删掉、要么用它做更精细的推荐（比如区分大小调影响排序）。

## 已验证会踩的坑（备忘）
- **Python 环境混用**：机器上同时有 pyenv 3.9.18 和系统 Python 3.14，`uvicorn` 命令可能解析到错误环境。启动时用 `python -m uvicorn ...` 而不是直接 `uvicorn ...`，先 `which python` 确认在 `.venv` 里。
- **`.venv` 已改用系统 Python 3.14**（原 pyenv 3.9.18 不支持 `int | None` 这种新版类型写法，schemas/ 里大量用到）。重建命令：`rm -rf .venv && /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m venv .venv`
