# 适配层（后置）

> 状态：**计划中**。当前阶段刻意只交付中立核心，适配器后置，避免过早抽象。

## 适配层要解决什么

中立核心（`../core/` + `../state-systems/`）是纯 Markdown 约定，任何能读写文本、能按文档推理的 Agent 都能消费。但各家 Agent 的**入口约定**不同 —— 用户在各自工具里"怎么触发这套流程"不一样。适配层就负责把中立核心**挂载/翻译**到各家原生入口。

## 中立核心 → 各家入口的映射设想

| Agent runtime | 原生入口 | 适配方式（设想） |
|---|---|---|
| Claude Code | `SKILL.md` / `CLAUDE.md` / `.claude/skills` | 一个薄 `SKILL.md`，frontmatter 描述触发词，正文指向 `../core/*` |
| Codex | `AGENTS.md` / `agents/*.yaml` | `AGENTS.md` 挂载工作流，`agents/*.yaml` 描述角色，正文指向 `../core/*` |
| Cursor | `.cursor/rules/*` | 规则文件引用四态系统与工作流骨架 |
| 其他 | 各自 rules / instructions | 同理：薄入口 + 指向中立核心 |

共同模式：**入口文件保持薄**，只负责"被触发"和"指路"，真正的流程逻辑全部留在中立核心，单处维护。

## 现状里已有的两个半成品

- `../../skills/workflow-core/project-workflow`：已经是本框架在 **Claude Code** 上的事实实例（含 `agents/openai.yaml`）。阶段 3 会把它正式登记为 CC 适配器，并把它的 `references/*` 收敛为指向 `../core/*` 的薄引用，消除与中立核心的重复。
- `../../skills/workflow-core/local-workflow`：J-SOP 来源样本，保留作参考母本，不作为适配器。

## 落地顺序（见 FRAMEWORK.md 路线图）

1. 阶段 3 — Claude Code 适配器
2. 阶段 4 — Codex 适配器
3. 阶段 5 — CC + Codex 两边端到端实测，再回头抽公共适配模式

> 在两个真实 runtime 跑通前，不在这里写更多结构 —— 先让核心约定经受实测，再沉淀适配层。
