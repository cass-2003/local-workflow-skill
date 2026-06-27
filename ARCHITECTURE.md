# 架构总览 · ARCHITECTURE

> 一句话：**四态系统**是核心，**framework/** 是大脑，**skills/** 是双手，**adapters/** 是各家 Agent 的插口。
> 同一套纯 Markdown 约定，能在 Claude Code、Codex 等不同 runtime 上跑出一致行为。

## 分层

```text
┌─────────────────────────────────────────────────────────────┐
│  适配层 adapters/   各家 Agent 的原生入口（薄，只负责被触发+指路）│
│    Claude Code → SKILL.md      Codex → AGENTS.md + agents/*.yaml │
└───────────────┬─────────────────────────────────────────────┘
│ 触发，指向 ↓
┌───────────────▼─────────────────────────────────────────────┐
│  大脑 framework/core/   工具中立的工作流核心（单一真相）         │
│    10 阶段骨架 · 路由 · 权威解析 · 验证闸门 · 产物契约 · 自主循环 · 保守演进 │
│                         ↑ 读/写                                │
│  核心状态 framework/state-systems/   ★ 四态系统                │
│    日志 LOG · 需求 REQUIREMENTS · 记忆 MEMORY · 进度 PROGRESS   │
└───────────────┬─────────────────────────────────────────────┘
                │ Phase 4/5 委托 ↓
┌───────────────▼─────────────────────────────────────────────┐
│  双手 skills/   409 技能 / 18 领域大类（双层 <大类>/<来源>/）   │
│    reverse 63 · security 85 · frontend 27 · …                  │
└─────────────────────────────────────────────────────────────┘
```

## 四态系统是地基

一个项目被多 Agent、多会话持续推进时，最需要四件事 —— 这就是核心：

| 系统 | 回答 | 默认承载 |
|---|---|---|
| 🗒️ 日志 `project-log` | 最近发生了什么 | `LOG.md` |
| 📋 需求 `project-requirements` | 当前要满足什么 | `REQUIREMENTS.md` |
| 🧠 记忆 `project-memory` | 为什么这样设计 | `MEMORY.md` |
| 📊 进度 `project-progress` | 现在做到哪里 | `PROGRESS.md` |

全部纯 Markdown 承载 → Agent 的上下文有了**可持久、可交接、可审计**的落点。这是它与普通 prompt 工程的根本区别，也是跨工具、跨会话协作的基础。

## 一次请求的端到端流转

```text
用户在 Claude Code / Codex 里触发
   → adapters 薄入口被命中，指向 framework/core
   → Phase 0 scan：看清仓库有哪些规则/技能/文档/验证入口
   → Phase 1 state restore：从四态系统恢复「最近/要满足/为什么/到哪了」
   → Phase 2-3 intent + authority：判断任务类型、解析该信任哪一层
   → Phase 4 route：core/03-routing 把问题域映射到 skills/<大类>
   → Phase 5 execute：委托对应技能干活，并按产物契约留下报告/日志/状态
   → Phase 6 validate：完成必须有与范围匹配的证据
   → Phase 7 sync：把成果分类回写四态系统，并同步文档入口/审计索引
   → Phase 8 deliver：commit/PR 前过三道闸门
   → Phase 9 evolve：重复模式转成保守的沉淀建议
```

当用户授权“继续推进项目 / 按计划开发 / 自动审计修复”时，core 先进入 `08-autonomous-project-loop.md`：补齐或更新路线图和下一步工作包，再按“实现 → 验证 → 自审 → 修复 → 同步 → commit → 选下一个目标”的循环推进，直到遇到明确停止条件。

## 目录责任

```text
local-skills-workspace/
├─ README.md            仓库门面与快速上手
├─ ARCHITECTURE.md      本文件：整张架构图
├─ state/               本仓库当前四态：日志/需求/记忆/进度
├─ framework/           大脑 + 核心状态
│  ├─ FRAMEWORK.md       总设计与路线图
│  ├─ core/              ★ 单一真相：10 阶段/状态/路由/权威/验证/产物/自主循环/演进
│  ├─ state-systems/     ★ 四态系统说明 + drop-in 模板
│  └─ adapters/          各家 Agent 适配登记 + 模板
│     ├─ claude-code.md   CC 适配器 → skills/.../project-workflow
│     └─ codex.md + codex/ Codex 模板（AGENTS.md + agents/workflow.yaml）
├─ skills/              双手：409 技能 / 18 大类
│  ├─ README.md          能力库索引
│  ├─ _merge-manifest.csv 三源合并对照表
│  └─ <大类>/<来源>/<skill>/  来源 = ours｜codex｜cskills
└─ tools/               可复现工具（合并能力库的脚本与说明）
```

## 关键不变量（改动时务必守住）

1. **单一真相在 core**：流程规范只在 `framework/core/*` 维护。改流程 → 改 core，不改适配器里的指针。
2. **适配器保持薄**：只负责「被触发 + 指路」，不复制规范。各家差异隔离在 `adapters/`。
3. **状态先于动作**：任何实质性工作前先从四态系统恢复状态，不靠记忆与假设。
4. **去重优先级 ours>codex>cskills**：同一能力保留一个赢家；根名不同的近义变体作为不同技能保留。
5. **纯文本承载**：四态系统与全部约定都是 Markdown，零运行时依赖。

## 三个池子如何收敛进双手

| 来源 | 数量 | 角色 |
|---|---|---|
| `ours` | 28 | 本仓库沉淀的通用工作流与可复用技能，去重最高优先 |
| `codex`（`~/.codex/skills`） | 218 | 主池，已含 `~/.claude/skills` 全部 |
| `cskills`（C_Skills） | 163 | 高度互补，逆向为主 |

合并去重并剔除项目定制项后 **409 技能 / 18 大类**。其中 `workflow-orchestration` 里的 `orchestration`（多 Agent 编排）、`skill-router`（skill 分诊）与 `project-inception-docs`（项目起始分析文档包）天然对应框架的**编排层**、**路由层**与**起始文档层**，可被 `core/03-routing` 直接复用。

## 路线图位置

已完成：中立核心 → 四态模板 → CC 适配器 → Codex 适配器 → 三源能力库合并 → 项目定制项清理。
`tools/project-init/` 提供可复现的项目初始化、入口刷新与工作流自检脚本；后续仍需抽公共适配层与全局安装说明。详见 `framework/FRAMEWORK.md` 与 `README.md` 路线图。
