"""Agent 层（产品文档 §7、§11.5）：LLM 负责决策和解释，不做底层识别。

MVP 保留四个 Agent：
    theory       Music Theory Agent：低置信度和弦纠错、slash chord / 借用和弦判断
    arrangement  Guitar Arrangement Agent：决定生成哪些版本、调用规则系统组装
    fingering    Fingering Agent：解析用户把位/难度要求，驱动 positions 优化
    editor       自然语言修改：解析用户指令 -> 结构化操作 -> 调规则系统重编配

Style / Practice Coach Agent 属于 Phase 2+，暂不建。
"""
