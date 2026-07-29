# FretAI 开发进度

> 每完成一项就把 `[ ]` 改成 `[x]`，并更新顶部总体进度。这个文件跟代码一起提交，跨会话可查。
> **注**：2026-07-23 起 `services/rules/` 已改名为 `services/tools/`（更贴合 Agent Tool Use 的角色），下文历史记录里出现的 `rules/` 均指这个目录，不再逐条改名。

**总体进度：约 90%**（里程碑 2-6 全部完成——4 个业务 Agent、API 端点串联、前端三页面全部跑通，上传→分析→编配→自然语言修改端到端闭环验证通过。剩余：里程碑 7 导出+收尾，以及和弦时间轴可视化/和弦指法图等简化项，视时间决定是否回补）

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
- [x] `power_chord.py` — Power Chord 转换（用 6 弦品格公式计算，覆盖全部 12 根音，不依赖指法库；后补：`prefer_position` 参数真正实现，可在多个八度候选里选最接近的品格，详见 ISSUES.md #3）
- [x] `capo.py` — Capo 推荐（枚举 0-7 品 + 按横按数排序，发现并修复了降号根音 bug）
- [x] `difficulty.py` — 难度评分（横按数 + 把位跨度 + 技巧数加权，已验证）
- [ ] `positions.py` — 把位优化算法（**跳过，放到最后有余力再做**；涉及动态规划，是规则系统里最难的一块，不是必需品）
- [x] `theory.py` — 调内和弦规则 `get_diatonic_chords`（复用 transpose.py 的 NOTES/FLAT_TO_SHARP，大调级数 I-vii° 计算，已验证 G major 结果正确；小调暂不支持，已知局限）

## 里程碑 3：音频上传 + 数据库（用户自己写——通用 Web 后端技能，与 Agent 无关但重要）
- [x] SQLite 建表（Song、Arrangement），建表脚本 `app/db/init_db.py`
- [x] 上传接口：接收音频文件，存本地 + 存数据库记录（curl -F 验证跑通）
- [x] 查询接口：根据 song_id 返回歌曲状态（含 404 情况验证）
- [x] 音频流接口：`GET /songs/{id}/audio`，用 FastAPI FileResponse 支持 Range 请求，curl 下载验证字节数一致

## 里程碑 4：音频分析（services/audio/，librosa）—— AI 多带写，重点讲输入输出含义
- [x] `preprocess.py` — librosa.load 读取音频，返回 (y, sr)（已用真实 mp3 验证，时长/采样率符合预期）
- [x] `bpm.py` — librosa.beat.beat_track 检测 BPM + 节拍时间点（已验证：117.45 BPM，接近 Thriller 真实 BPM 118-119；踩坑：新版 librosa 返回 tempo 是 numpy 数组不是纯 float，需要 .item() 转换）
- [x] `key.py` — chroma 特征 + Krumhansl-Schmuckler 模板匹配（已用合成 C 大三和弦测试音验证代码逻辑正确；真实歌曲 Thriller 检测偏差，判断为算法在复杂混音下的已知局限，详见 ISSUES.md #1）
- [x] `chords.py` — 按拍切片 + 24 种和弦模板（12大三+12小三）点积匹配 + 合并相邻同和弦（已用合成 C→G 和弦切换测试音验证：切换点精确，置信度 0.85 远高于 Thriller 真实数据的 0.27-0.31，确认低置信度是真实信号非 bug，详见 ISSUES.md #2）
- [x] `sections.py` — librosa.segment.agglomerative 聚类切段，固定 6 段，name 留空交给 Agent 层贴标签（已用 Thriller 验证：首尾相接总时长吻合，段落长度不均匀但符合"够用就好"的定位，详见 DECISIONS.md #8）
- [x] 接入 BackgroundTasks，串成完整 pipeline（upload_song 存文件建记录后立刻返回 pending，后台任务跑 analyze_song，依次经过 analyzing -> done/failed，结果序列化存进 Song.analysis；端到端验证：上传 -> 轮询状态 -> 直接查库确认 analysis 字段内容完整）

## 里程碑 5：Agent 层（⭐ 用户明确的重点，会拆到最细）

**架构原则（2026-07-13 讨论确定）**：
1. 规则系统算"事实"（确定性、可复现），Agent 负责在事实里"挑选和解释"，不让 LLM 直接猜测和弦指法这类需要精确计算的内容。
2. **保留产品文档 §7 原本的 7 个 Agent 划分（不合并、不再拆细）**：Audio Analysis / Music Theory / Guitar Arrangement / Fingering / Style / Practice Coach / Export。每个 Agent 对应一个明确的"决策职责"，粒度是合适的。**但这条讲的是"粒度划分是对的"，不代表 MVP 要做全部 7 个**——搭骨架时（`services/agents/__init__.py`）已经明确裁剪：MVP 只做 Music Theory / Guitar Arrangement / Fingering / 自然语言 Editor 这 4 个业务 Agent；Style Agent 和 Practice Coach Agent 归入 Phase 2+，MVP 不做。Audio Analysis 的职责已经被里程碑 4 的 `services/audio/` 覆盖（不需要单独包一层 LLM Agent，纯信号处理即可）；Export 在里程碑 7 做，且大概率不需要 LLM 决策（纯格式转换）。
3. **不要为每个小功能单独开一个 agent**（比如不能有"横按判断 agent""品格计算 agent"这种）。细粒度功能永远停留在 tool 这一层——也就是 `rules/` 目录下已经写好的函数（transpose_chord / recommend_capo / to_power_chord / score_difficulty / get_voicings 等）。7 个 Agent 内部通过 Tool Use 按需调用这些函数，而不是互相之间再发消息、再拆子 agent。这样避免了 multi-agent 系统常见的通信复杂度暴增、调试困难的问题。

- [x] 打通一次最基础的 LLM API 调用（阿里云百炼 qwen3.5-flash，OpenAI 兼容接口，AsyncOpenAI 客户端，已验证 chat.completions.create 端到端跑通）
- [x] 理解 Tool Use：先跑通单工具版本，再升级到 to_power_chord + recommend_capo 双工具版本，用 TOOL_FUNCTIONS 字典按 tool_call.function.name 动态路由到真实函数。已验证模型能根据工具 description 正确区分"转 power chord"和"推荐 capo"两种意图（backend/tests/scratch_tool_use.py）
- [x] 抽出通用执行器 `services/agents/runner.py`（run_agent_with_tools，while 循环支持多轮工具调用），用 recommend_capo 场景回归验证，重构后行为与手写脚本一致
- [x] 验证阿里云百炼支持 `response_format={"type": "json_object"}` 强制 JSON 输出模式（scratch_json_format_test.py），为 Music Theory Agent 需要返回结构化 ChordEvent 列表做准备
- [x] 验证 tools + response_format 组合可用：runner.py 加了可选的 response_format 参数透传给两次 API 调用，用 recommend_capo 场景测试，模型能正常在"调用工具"和"最终返回纯 JSON"之间正确切换，不互相干扰（scratch_json_tool_combo.py）
- [x] Music Theory Agent：`review_chords(key, chords)` 实现完成——system prompt 要求判断调内/离调、结合前后文推理、只对确实可能出错的位置提出修正；接 get_diatonic_chords 工具查调内和弦事实；用 response_format=json_object 返回 {"corrections": [{"index", "chord", "reason"}]}；代码里对越界 index 做了防御（跳过而不是崩溃）。用经典案例 G-D-B-C（G major）验证：正确识别出 B 不在调内，结合前后文给出有依据的修正（判断为 vi 级 Em），并保留了对原始低置信度的引用
- [x] Guitar Arrangement Agent：生成木吉他弹唱版 + 电吉他 Power Chord 版（MVP 范围裁剪，暂不做产品文档里另外 4 种版本）。架构上没有用 Tool Use——`_build_acoustic_arrangement`/`_build_power_chord_arrangement` 纯 Python 直接调用 recommend_capo/get_voicings/to_power_chord/score_difficulty 组装数据（决策已经被规则系统排序确定，不需要 LLM 参与选择），只用 LLM 生成最后的 notes 解释文字，response_format=json_object 输出 `{"acoustic_notes", "power_chord_notes"}`。用 F#m-D-A-E 案例验证：木吉他版结果与产品文档 §7.1 完全一致（Capo 2 弹 Em-C-G-D）；顺带验证了 tools=[] 空列表传给百炼 API 不会报错，模型会直接跳过工具调用给出最终回复
- [x] Fingering Agent：`optimize_fingering(chords, user_request)` 实现完成——LLM 判断请求是否属于"power chord 换把位"这一支持的场景（不支持时诚实拒绝，不做假功能），提取 prefer_position 数字，调用 to_power_chord 生成结果。用产品文档 §9.2 场景验证：不支持场景（换开放和弦把位）被正确诊断拒绝；支持场景端到端测试暴露出 to_power_chord 品格选择的系统性局限（4 个和弦里只有 2 个真正落在"5 品附近"），详见 ISSUES.md #4，判断为超出 Fingering Agent 范畴、留给未来的把位优化 Agent（§6.8）解决
- [x] Editor：`apply_edit(arrangement, message)` 实现完成——第一个真正用上多工具 Tool Use 动态路由的 Agent（LLM 自己判断该调用 transpose_progression 还是 to_power_chord）；范围裁剪为只支持转调 + 改 power chord（optimize_positions 从未实现，"换低把位""不要横按"这类暂不支持）；用 model_copy 保证不污染原始 Arrangement 对象。用 F#m-D-A-E 案例验证：降两调、改 power chord 两种场景都正确。踩坑：第一版输出格式只让 LLM 返回和弦名字符串列表，导致 power chord 场景下 fingering/position 是写死的空值——修复为代码层面用 _build_arranged_chord 按和弦名格式（是否以"5"结尾）重新查真实指法，不依赖 LLM 转述数字

## 里程碑 6：前端页面

### 第一步：API 端点串联（把里程碑 5 写好的 Agent 函数接到路由上，之前只有函数本身、端点还是 NotImplementedError）
- [x] `runner.py` 加 `AgentTrace` 返回结构（记录每轮 Tool Use 的工具名/参数/结果，不只是最终字符串），4 个 Agent 文件（arrangement/editor/theory/fingering）同步改造调用点和返回签名，为调试/前端展示 Agent 思考过程做准备
- [x] `arrangements.py`：`generate_arrangements`（查库拿 analysis → 反序列化 → 调 Guitar Arrangement Agent → 存库）、`list_arrangements`、`get_arrangement` 三个端点实现完成，用真实歌曲端到端验证跑通
- [x] `chat.py`：`modify_arrangement` 接 Editor Agent 的 `apply_edit`，编辑语义定为覆盖原 arrangement_id（不保留历史版本）。端到端测试暴露并解决了一整条排查链——大批量和弦（176个）场景下 LLM 完全不调用 `to_power_chord` 工具、直接编造结果（"lazy tool use"），根因不是数量而是模型判断任务无需工具；解法是新增批量工具 `to_power_chord_batch` + `runner.py` 加 `force_tool_use` 用 `tool_choice="required"` 强制调用，过程中连续踩坑并解决：qwen3.5-flash thinking mode 与 tool_choice 冲突（需 `extra_body={"enable_thinking": False}`）、`response_format=json_object` 要求 messages 含小写"json"、`tool_choice="required"` 与 `response_format` 同时生效会互相冲突（改成分两次请求规避）；另外修复了组装逻辑用错字典 key、LLM 传参数类型不可靠（字符串"5"而非整数 5，加 `int()` 容错）两个衍生 bug。最终用真实歌曲 176 和弦完整验证通过。完整排查过程详见 ISSUES.md #5
- [x] `analysis.py`：`get_analysis`（查库反序列化返回）、`transpose`（取和弦列表调 `transpose_progression`，`zip` 配对写回每个 `ChordEvent.chord`）、`correct_chord`（定点修改指定 index 的和弦，标记 `user_corrected=True`，越界 index 返回 422）三个端点实现完成，抽了 `_get_analyzed_song` 共用前置校验（404/409）。用真实歌曲验证：单独修正 `chords[0]` 不影响其余和弦；`transpose(semitones=-2)` 后所有和弦整体降 2 半音（`Am→Gm`、`C#→B` 等）且和弦性质不变，持久化生效
- [ ] `export.py`：里程碑 7 范围

**里程碑 6 第一步完成**：`arrangements.py`/`chat.py`/`analysis.py` 全部端点接通并验证，前端所需的后端能力已就绪。

### 第二步：前端页面（对着已有骨架填内容，骨架已就绪：types/index.ts、lib/api.ts、三个页面空壳、四个组件目录 README）
- [x] 上传组件（`components/upload/UploadForm.tsx`）：文件选择 + 调用 `api.uploadSong` + 跳转 `/songs/[id]`，三态状态机（idle/uploading/error）。浏览器验证通过
- [x] 分析页（`components/analysis/AnalysisView.tsx`）：`useEffect` 递归 `setTimeout` 轮询歌曲状态直到 `done`/`failed`，用 `cancelled` 标记位处理组件卸载时的竞态；展示 Key/BPM/拍号 + 和弦列表（平铺展示，非时间轴可视化）。**简化范围**：波形图、按小节排列的时间轴、播放高亮、段落结构展示未做，留待后续需要时再补
- [x] 编配页（`components/chord/ArrangementsView.tsx` + `ArrangementCard.tsx`）：进页面先 `listArrangements` 查已有编配，没有才触发 `generateArrangements`（避免重复调用 LLM）；卡片展示难度/capo/和弦列表/notes；父组件（ArrangementsView）作为编配列表唯一数据源，子组件通过 `onUpdated` 回调上报变更，用 `arrangement_id` 精确定位替换。**简化范围**：和弦指法图（ChordDiagram SVG 品格图）未做，用文字标签 + title 提示代替
- [x] 自然语言修改输入框：接入 `ArrangementCard` 底部，调用 `api.modifyArrangement`，回车或点击提交，成功后通过回调更新父组件状态、展示 Agent 回复文字
- [x] 修复骨架阶段遗留的类型不匹配：`lib/api.ts` 的 `generateArrangements`/`modifyArrangement` 返回类型跟里程碑 6 第一步实际实现的后端响应格式对不上（缺 `trace` 字段、`generateArrangements` 少一层 `{arrangements, trace}` 包装、`modifyArrangement` 误用 JSON body 而后端实际用查询参数），补充 `AgentTrace`/`ToolCallRecord`/`TraceStep` 前端类型并订正
- [x] 三个页面全部浏览器手动验证通过：上传 → 分析（轮询展示）→ 编配（生成 + 自然语言修改）完整闭环跑通

## 里程碑 7：导出 + 收尾
- [ ] Markdown 导出
- [ ] PDF 导出
- [ ] 完整走一遍：上传 → 分析 → 编配 → 修改 → 导出
- [ ] 简历项目描述打磨（对照产品文档 §17）

## 里程碑 8：MVP 完成后 —— 迁移到 LangChain / LangGraph（求职策略，非必需但计划做）
**为什么**：用户判断 LangChain/LangGraph 是 AI 应用岗面试高频问题，希望简历上两种能力都有——既讲得清 Tool Use 底层原理（手写验证过），也会用业界标准工具。计划顺序：先用手写的 `runner.py` 把核心 Agent 全部实现并验证正确，再重构迁移到框架，这样能清楚讲出"框架帮我省了哪些代码、我为什么放心交给它"。
- [ ] 用 LangChain 重新实现现有 Agent 的工具绑定（对比手写版本，理解框架封装了什么）
- [ ] 评估是否用 LangGraph 重新编排多 Agent 协作流程（比如"纠错 -> 编配 -> 指法优化"的阶段流转）
- [ ] 保留手写版本作为对照/说明材料，不删除（面试可以直接对比讲解）

## 里程碑 9：工业级工程能力补强（面试深度导向，MVP 完成后统一做）
**目标**：不是要真的 7x24 上线运维，而是让每个环节都经得住面试官追问——"你怎么知道这次改动是变好了""并发下会怎样""怎么监控这个系统"。2026-07-23 头脑风暴整理，做的时候可以每项单独拆细。

### Eval 与数据
- [ ] **Eval 评测体系**：建 20-50 首已知正确答案的歌作为 Golden Set（延续 key.py/chords.py 已经用过的"合成测试音验证"方法论，从单个案例升级到系统性批量评测）；量化 Key 准确率、和弦逐段准确率（按时间加权）、BPM 误差范围；每次改动后自动跑一遍做回归对比
- [ ] **LLM 输出质量评测**：Agent 给出的编配解释是否合理、有没有乐理错误——调研并尝试 "LLM-as-judge" 方法论
- [ ] **数据飞轮闭环设计**：`ChordEvent.user_corrected` 字段目前只是存在，设计一版"如果收集到 1000 条用户修正记录，怎么分析、怎么反哺规则阈值调整"的流程（哪怕先用模拟数据跑一遍）
- [ ] **自动化测试**：把现在这些手动跑脚本验证的案例（合成音频测试、transpose 边界情况等）迁移成 pytest 测试用例，能自动跑、能接入 CI

### 延迟与并发
- [ ] **多 Agent 编排延迟分析**：区分哪些步骤能并行（比如 Key 检测和 BPM 检测互相独立，可同时跑）、哪些必须串行（编配 Agent 依赖纠错 Agent 结果），画出关键路径
- [ ] **流式输出（Streaming）**：LLM 回复改成边生成边推给前端，改善感知延迟
- [ ] **压力测试**：写压测脚本（locust 或简单并发 curl），实测验证 DECISIONS.md #9 里"analyze_song 同步阻塞"的理论判断，拿到具体数字而不是停留在理论
- [ ] **LLM API 限流与重试**：设计退避重试（exponential backoff）策略，应对供应商的速率限制（rate limit）
- [ ] **超时与降级策略**：LLM API 响应慢/超时时，是否降级成"只返回规则系统结果，不含 AI 解释"

### 上下文管理（Context Management）
- [ ] **上下文窗口限制的故障处理**：多轮 Tool Use 循环里 `messages` 只会追加不会裁剪，理论上可能超过模型 token 上限直接报错——这是需要处理的真实故障场景，不是可选项
- [ ] **裁剪策略选型**：评估滑动窗口（只保留最近 N 轮）、摘要压缩（用 LLM 把早期历史总结成一句话）、关键信息筛选（工具执行结果很长时，喂给模型前先筛选/裁剪）三种做法的适用场景
- [ ] **区分两种粒度的上下文**：单次用户提问内部的 Tool Use 循环增长 vs 同一会话里多次用户提问的对话历史管理，是两个不同粒度的问题，分别设计
- [ ] **跨 Agent 上下文传递设计**：编配 Agent 需要纠错 Agent 的结果时，传完整对话历史还是只传精简结论，权衡信息完整度和上下文膨胀

### 缓存
- [ ] **缓存层级划分**：音频分析结果缓存（按文件内容 hash 去重，避免重复跑 librosa）vs LLM 调用结果缓存（要单独讨论，因为 LLM 输出不是完全确定性的，哪些场景适合缓存、哪些不该缓存要想清楚）
- [ ] **缓存失效策略**：规则系统代码更新后，旧缓存要失效——缓存 key 需要包含代码版本信息，不能只按输入内容做 key
- [ ] **缓存介质选型**：从进程内内存字典起步（够 demo），讨论多进程/多机器场景下为什么需要 Redis（呼应 DECISIONS.md #3 "MVP 不用 Redis"的决策，补一句"如果要做真正的分布式缓存，Redis 就是绕不开的选择"）

### 架构演进与扩展性
- [ ] 把 DECISIONS.md #3 提到的 Celery + Redis 方案真正落地一次，对比 BackgroundTasks 的差异（吞吐量、可靠性）
- [ ] SQLite 在高并发写入下的锁问题分析，明确"什么条件下必须迁移到 PostgreSQL"

### 成本控制
- [ ] **成本/延迟量化对比**：实测 qwen-turbo/plus/max 在几个 Agent 任务上的延迟、成本、质量对比表，补充 DECISIONS.md #10 的"分阶段模型选型"决策
- [ ] **Token 用量优化**：审查工具描述/prompt 长度，设计对话历史裁剪策略（多轮 Tool Use 循环里 messages 会越来越长）

### 可观测性与运维
- [ ] **结构化日志**：记录每次 Agent 调用的 token 用量、耗时、调用了哪些工具、是否报错
- [ ] **Prompt/模型版本管理**：追踪"某次生成结果是用哪个版本的 prompt/模型产出的"，支持快速回滚

### 安全与鲁棒性
- [ ] 自然语言修改编配接口的 prompt 注入防护
- [ ] 工具调用参数校验（模型传了非法和弦名时不能让规则函数崩溃）

### 实验方法论
- [ ] 设计一份"如果要做 A/B 测试对比两版 prompt"的方案（对照组划分、评估指标），不一定要真的上线跑

---

## 里程碑 10：求职策略 —— 补一个 Java 技术栈项目（FretAI 完成之后，独立项目，不影响 FretAI 本身）
**背景（2026-07-24）**：用户看到网传数据（未经验证，具体数字存疑）说纯 AI Agent 项目简历响应率偏低，Java + Agent 组合响应率更高。讨论后达成共识：**不对 FretAI 做任何改动**（中途换技术栈成本高、收益存疑，Python 生态在音频处理/LLM SDK 上更成熟，FretAI 保持现状是对的选择）。计划是 FretAI 完成后，**另开一个独立的 Java（Spring Boot 之类）项目，也集成 LLM/Agent 相关能力**，用来补足"传统后端工程能力"这个技能点，两个项目并列展示、互相印证，而不是互相替代。
- [ ] FretAI 完成后再启动，不占用当前进度
- [ ] 选题待定：可以是全新场景，也可以是"用 Java 技术栈把 Agent 集成进一个更贴近企业存量系统场景"的项目（比如很多公司需要把 LLM 能力嫁接进已有 Java 系统，这本身也是真实的技能点）

### 模型选型的调研深度
- [ ] **横向对比调研**：针对"和弦纠错""编配解释"等具体任务，用相同测试用例对比多个候选模型（qwen-turbo/plus/max，可扩展到 GLM、DeepSeek 等同价位厂商）的准确率、响应速度、Tool Use 稳定性、成本，写清楚最终选型的权衡过程，不只是"有现成 key 所以用它"
- [ ] **Tool Use 可靠性专项测试**：不同模型在"结构化输出/工具调用"上的稳定性差异很大（会不会经常传格式错误的 JSON、误调用工具），需要专门测试而非假设"能跑=稳定"
- [ ] **国产模型 vs 国际模型的调研**：补一段为什么用阿里云百炼而不是 GPT-4o/Claude 的对比分析（成本、访问便利性、数据合规/是否出境等真实工程考量）
- [ ] **调研过程本身要留痕**：养成写"调研笔记"的习惯，即使最终决策没变，记录"比较过什么、排除了什么、为什么"，这份记录本身就是面试证据

### Agent Harness / 前沿技术调研
- [ ] **ReAct 模式对照说明**：`runner.py` 里的循环本质是简化版 ReAct（Reasoning + Acting 交替），补一段"我们实现的和标准 ReAct 差在哪"的分析
- [ ] **Reflection / Self-critique**：评估要不要让模型在给出最终答案前自我检查一遍（特别适合 Music Theory Agent 的纠错场景）
- [ ] **Structured Output 强校验**：现在依赖模型"自觉"生成合法 JSON 参数，调研 JSON mode / `instructor` / `outlines` 这类强制 schema 校验方案能否提高 Tool Use 可靠性
- [ ] **Multi-agent 框架调研记录**：补一段"调研过 AutoGen/CrewAI，为什么判断当前项目规模不需要它们"（呼应 DECISIONS.md #6 的架构原则，把"调研过程"也记录下来而不只是结论）
- [ ] **Context Engineering**：现在是把所有信息塞进 messages，调研动态检索相关知识/裁剪不相关历史等更精细的上下文管理做法
- [ ] **Evals-driven development**：调研"用 eval 驱动 prompt 迭代"这套开发流程方法论，评估要不要正式采用

---

## 已知局限（备忘，面试可诚实提及）
- `recommend_capo` 目前只按"横按数量"排序，没有惩罚"capo 品数过高"（比如 capo=6 这种实际很少用的方案，会和 capo=1 并列最优）。后续可以给 `barre_count` 加一个"capo 越大惩罚越多"的权重。
- `transpose_chord` 统一把降号（b）翻译成升号（#）表示，输出不会保留原始的降号记谱习惯（比如 Ab 调的和弦转出来会显示成 G# 而不是 Ab）。
- `recommend_capo(key, chords)` 的 `key` 参数目前完全没有在函数体内被使用（只用了 `chords`），是个"看起来需要但实际没用上"的参数，Tool Use 测试中意外发现（模型传了简化过的 key 值也不影响结果，因为反正没用到）。后续要么删掉、要么用它做更精细的推荐（比如区分大小调影响排序）。
- Music Theory Agent 给出的乐理解释文字，偶尔会出现术语引用不够精确的情况（比如把 G 大调的 vii° 说成 "Bdim"，实际应该是 F#dim）——不影响核心判断结论（"B 不在调内、应该修正"这个结论是对的），但如果解释文字要直接展示给用户看，值得后续在 prompt 里加约束提高严谨度。也提醒一个更本质的点：Agent 给的修正是"一个有依据的合理猜测"，不是唯一正确答案（同一个离调和弦可能有好几种合理解释），这也是为什么要保留"候选项 + 用户可修正"机制（产品文档 §14）的原因。
- `to_power_chord` 只实现了 6 弦根音的 power chord 形状（公式：根音到 6 弦空弦 E 的半音距离 % 12），没有 5 弦根音的版本，也没有"选更合理把位"的判断。当根音在音高上低于 E（比如 D、C#、C）时，`% 12` 取模会把结果"绕" 到很高的品格（例如 D5 算出第 10 品，而不是更常用的 5 弦根音第 5 品附近版本 x577xx，这是产品文档 §7.1 例子里实际给出的指法）。用 Guitar Arrangement Agent 的验证案例（F#m-D-A-E）跑出来时发现这个偏差。完整解决方案（5 弦根音实现 + 智能选把位）属于产品文档 §6.8 把位优化 Agent 的范畴，不在当前 Guitar Arrangement Agent 里顺带解决。
- Guitar Arrangement Agent 生成的 `notes` 解释文字，喂给 LLM 的 summary 里只包含 `difficulty` 和和弦名（`display`），不包含具体的 `fingering`/`position` 数值，所以模型没有机会核对"品格是否合理"——比如上面那条 D5 品格偏高的问题，模型的解释里说"无需按品"，这个描述其实不准确（D5 实际在第 10 品）。根因是喂给 LLM 的信息本身不够细，不是 LLM 编造的。后续如果要让 notes 更精确，需要把具体指法数据也纳入 prompt。

## 已验证会踩的坑（备忘）
- **Python 环境混用**：机器上同时有 pyenv 3.9.18 和系统 Python 3.14，`uvicorn` 命令可能解析到错误环境。启动时用 `python -m uvicorn ...` 而不是直接 `uvicorn ...`，先 `which python` 确认在 `.venv` 里。
- **`.venv` 已改用系统 Python 3.14**（原 pyenv 3.9.18 不支持 `int | None` 这种新版类型写法，schemas/ 里大量用到）。重建命令：`rm -rf .venv && /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m venv .venv`
