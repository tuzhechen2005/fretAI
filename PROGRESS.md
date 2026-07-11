# FretAI 开发进度

> 每完成一项就把 `[ ]` 改成 `[x]`，并更新顶部总体进度。这个文件跟代码一起提交，跨会话可查。

**总体进度：约 18%**（骨架搭建完成，规则系统跑通 transpose + voicings + power_chord）

---

## 里程碑 1：后端能跑起来（地基）
- [x] 项目骨架搭建（FastAPI + Next.js）
- [x] 后端 venv 环境跑通，`/health` 接口可访问
- [ ] `/docs` 页面理解（路由 vs 实现的区别）

## 里程碑 2：规则系统（services/rules/，纯 Python，无 AI 无数据库）
- [x] `transpose.py` — 单个和弦转调 `transpose_chord`
- [x] 把 `transpose_chord` 接到一个调试用 API 接口，用 curl 验证跑通
- [x] `voicings.py` — 和弦指法库（7 个常用开放和弦：C/D/E/G/A/Am/Em/Dm）
- [x] `power_chord.py` — Power Chord 转换（用 6 弦品格公式计算，覆盖全部 12 根音，不依赖指法库）
- [ ] `capo.py` — Capo 推荐
- [ ] `difficulty.py` — 难度评分
- [ ] `positions.py` — 把位优化算法（较难，可放最后）

## 里程碑 3：音频上传 + 数据库
- [ ] SQLite 建表（Song）
- [ ] 上传接口：接收音频文件，存本地 + 存数据库记录
- [ ] 查询接口：根据 song_id 返回歌曲状态

## 里程碑 4：音频分析（services/audio/，librosa）
- [ ] BPM 检测
- [ ] Key 检测
- [ ] 和弦识别（chroma + 模板匹配）
- [ ] 段落检测
- [ ] 接入 BackgroundTasks，串成完整 pipeline

## 里程碑 5：Agent 层（重点，产品的核心差异化）
- [ ] 打通一次最基础的 LLM API 调用（理解 messages / system prompt）
- [ ] 理解 Tool Use（LLM 怎么"调用"我们写的规则函数）
- [ ] Music Theory Agent：低置信度和弦纠错
- [ ] Guitar Arrangement Agent：生成多版本编配 + 解释原因
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

## 已验证会踩的坑（备忘）
- **Python 环境混用**：机器上同时有 pyenv 3.9.18 和系统 Python 3.14，`uvicorn` 命令可能解析到错误环境。启动时用 `python -m uvicorn ...` 而不是直接 `uvicorn ...`，先 `which python` 确认在 `.venv` 里。
- **`.venv` 已改用系统 Python 3.14**（原 pyenv 3.9.18 不支持 `int | None` 这种新版类型写法，schemas/ 里大量用到）。重建命令：`rm -rf .venv && /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m venv .venv`
