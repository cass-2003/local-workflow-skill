# Portable Agent Workflow · 四态工作流框架

一个**工具中立的多 Agent 项目工作流框架**。同一套纯 Markdown 约定，能在 Claude Code、Codex 等不同 Agent runtime 上跑出一致行为。

源于 `J:\J-SOP 伴随式自动化助手` 的实践，但已去项目化，沉淀为可迁移的通用骨架。

## 核心：四态系统

一个项目被多 Agent、多会话持续推进时，最需要的是四件事 —— 这就是框架的核心：

| 系统 | 回答 |
|---|---|
| 🗒️ 日志系统 | 最近发生了什么 |
| 📋 需求系统 | 当前要满足什么 |
| 🧠 记忆系统 | 为什么这样设计 |
| 📊 进度系统 | 现在做到哪里 |

四态系统全部用 Markdown 承载，让 Agent 的上下文有了**可持久、可交接、可审计**的落点 —— 这是它和普通 prompt 工程的根本区别，也是跨工具、跨会话协作的基础。

## 仓库结构

```text
.
├─ README.md
├─ framework/              # 框架本体（大脑）
│  ├─ FRAMEWORK.md         #   总设计 + 路线图，从这里读起
│  ├─ core/                #   工具中立的工作流核心（10 阶段 / 路由 / 权威 / 验证 / 演进）
│  ├─ state-systems/       #   四态系统说明 + drop-in 模板
│  └─ adapters/            #   各家 Agent 适配层（后置，先留计划）
└─ skills/                 # 能力库（双手）：执行阶段委托的具体技能
   ├─ workflow-core/        engineering-core/   backend-infra/
   ├─ frontend-extension/   data-sync-validation/
   └─ language-runtime/     source-commands/
```

两层分工：`framework/` 决定**何时做什么**（恢复状态、路由、验证、交付），`skills/` 决定**具体怎么做**（限流、容器化、双向同步……）。

## 设计原则

1. **状态先于动作** — 任何实质性工作前，先从四态系统恢复状态。
2. **纯文本承载** — 四态系统全是 Markdown，零运行时依赖，任何工具都能读写。
3. **中立核心，适配后置** — 核心不提任何一家 Agent 的私有概念，差异隔离在 `adapters/`。
4. **约定优于代码** — 框架定义读写约定与流程闸门，不强制特定脚本。
5. **保守演进** — 重复模式先观察、聚类、建议，经批准再沉淀。

## 工作流骨架（10 阶段）

```text
scan → state restore → intent → authority → route → execute → validate → sync → deliver → evolve
```

详见 `framework/core/01-workflow.md`。

## 快速上手

把框架用到一个目标项目：

1. 复制 `framework/state-systems/templates/` 的四个文件到目标项目（或映射到已有等价文档）。
2. 让 Agent 第一次只做 `scan + state restore + 路由分析`，先不改代码。
3. 状态恢复与路由稳定后，再带验证闸门和文档同步跑完整任务。

适合第一轮试跑的提示词：

- `先扫描当前仓库，识别规则/技能/文档/验证入口，恢复四态系统状态，只做路由分析。`
- `判断这个需求该走 audit / implement / fix / review，并说明验证与文档同步策略。`
- `检查当前改动在 commit 前是否已满足验证、文档同步和交付三道闸门。`

## 路线图

- [x] 中立核心（`framework/core/` + `state-systems/`）
- [x] 四态系统 drop-in 模板
- [x] 能力库接入路由层（`skills/README.md`）
- [ ] Claude Code 适配器（登记 project-workflow）
- [ ] Codex 适配器（`AGENTS.md` / `agents/*.yaml`）
- [ ] CC + Codex 端到端实测
- [ ] 给能力库 skill 打"通用 / 半通用 / 项目定制"标记

## 与来源经验的关系

真正被认为值得通用化的，不是具体文件名，而是这些稳定模式：开工前先做权威解析、实质工作前先恢复状态、用意图和范围路由、完成必须过验证闸门、变更后同步文档与状态、交付前有 Git readiness gate、重复模式走保守沉淀。这些比"某个项目叫 SPRINT-PLAN.md"更稳定，也更适合带去别的仓库。
