---
name: project-workflow
description: Orchestrate a generic project workflow by scanning repository authority sources, restoring state from project truth docs, routing work to the right execution skill, enforcing validation and documentation sync gates, and capturing reusable process improvements. Use when a repository needs a reusable local workflow for status, audit, implement, fix, review, docs sync, git delivery, or workflow standardization.
---

# Project Workflow

> **角色**：这是「四态工作流框架」在 **Claude Code** 上的适配器实例。
> 流程规范的**单一真相**在框架中立核心 `../../../../framework/core/*`；本 skill 只负责在 CC 里被触发并指路。
> 适配登记见 `../../../../framework/adapters/claude-code.md`。

将此 skill 用作“项目工作流编排层”。

- 先识别仓库内真正有效的规则、技能、文档和验证入口，再决定如何执行。
- 先恢复项目状态，再进入审计、编码、修复、评审、同步或交付动作。
- 统一补齐验证闸门、文档闸门和交付闸门，避免只做局部动作。
- 在重复模式出现时，记录并建议沉淀为更稳定的 skill 或 reference。

不要把这个 skill 当成领域执行器、项目文档替身或“无条件覆盖其他 skill 的总规则”。

## Core Responsibilities

- 恢复上下文：确认当前仓库有哪些 instruction、rules、workflows、skills、truth docs。
- 解析权威：按角色识别“硬约束、命令语义、执行细节、项目真相、全局兜底”分别由谁负责。
- 任务路由：把用户请求稳定送到 `status`、`audit`、`implement`、`fix`、`review`、`sync-docs` 或 Git 相关技能。
- 控制阶段：让扫描、执行、验证、同步、交付和沉淀保持固定顺序。
- 沉淀经验：发现重复模式、旧路径、镜像漂移、重复解释时，转成可追踪的演进建议。

## Workflow Skeleton

对中等以上复杂度的任务，按下面的顺序思考和执行：

1. workspace scan
2. state restore
3. intent classification
4. authority resolution
5. route and delegate
6. task execution
7. validation gate
8. docs and state sync
9. git and delivery gate
10. workflow evolution

轻量任务可以跳过不必要阶段，但不要跳过状态判断、权威判断和验证推理。

详细阶段说明见 `references/execution-phases.md`。

## Four State Systems

多数项目至少有以下四类状态面：

- `project-log`
  记录最近发生了什么，例如 update log、变更记录、运行记录、部署记录。
- `project-requirements`
  记录当前要满足什么，例如 PRD、需求单、验收清单、审计基线。
- `project-memory`
  记录为什么这么做、系统是怎样的，例如架构文档、研究笔记、操作手册、资产地图。
- `project-progress`
  记录现在做到哪里，例如 sprint plan、todo、里程碑、当前阻塞项。

不要硬编码固定文件名。先在项目内发现这些状态系统的真实承载位置，再恢复状态。

四类系统的判定方式见 `references/state-systems.md`。

## Routing Rules

- 看当前状态、进度、真相摘要时，优先路由到 `status`。
- 做基线比对、缺口分析、验收预检时，优先路由到 `audit`。
- 做新功能、多文件实现、从需求落地代码时，优先路由到 `implement`。
- 修已知问题、关闭审计缺口、做回归修补时，优先路由到 `fix`。
- 检查 diff、找变更风险、做 code review 时，优先路由到 `review`。
- 补计划、补记录、补文档、补归档时，优先路由到 `sync-docs`。
- 做 commit、branch、push、PR、handoff 时，优先走 Git 相关技能。
- 做项目起始分析、文档体系搭建、PRD/技术架构/验收包生成时，优先路由到 `project-inception-docs`。
- 优化 skill、流程、路径、编排规则时，留在 `project-workflow` 的演进模式中。

如果项目里存在更具体的本地领域 skill，保留此 skill 的编排权，但把执行委托出去。

详细路由矩阵见 `references/routing-matrix.md`。

## Guardrails

- 不要从机器全局 skill 直接往项目里套，先看项目本地结构。
- 不要只凭关键词决定路由，要结合意图、范围、产物类型。
- 不要把“看过文件”当成“已经完成”，完成必须有与范围匹配的证据。
- 不要绕过文档和状态同步，尤其是需求、风险、进度、交付状态发生变化时。
- 不要发现重复模式就立刻改 skill，默认先观察、聚类、建议，再等待批准。

## Reference Loading Guide

规范单处维护在框架中立核心；下列 reference 仅作 CC 内的薄指针，按需直接读 core：

- 项目结构复杂、存在多个本地规则层时 → `../../../../framework/core/04-authority.md`
- 任务语义模糊、多条路线像候选时 → `../../../../framework/core/03-routing.md`
- 任务跨扫描/实现/验证/同步/交付多阶段时 → `../../../../framework/core/01-workflow.md`
- 需确认日志/需求/记忆/进度从哪里恢复时 → `../../../../framework/core/02-state-systems.md`
- 准备声明完成、提交、交付或 handoff 时 → `../../../../framework/core/05-validation.md` + `01-workflow.md`(Phase 8)
- 审计、验收、验证、文档同步或状态同步需要留下文件产物时 → `../../../../framework/core/07-artifact-contracts.md`
- 发现旧路径、漂移、重复解释、重复手工决策时 → `../../../../framework/core/06-evolution.md`

## Output Discipline

在内部至少形成两条可回看的简短记录：

```md
## Authority Resolution

- Rules source:
- Workflow source:
- Execution skills source:
- Truth docs source:
- Global fallback source:
- Drift detected:
- Notes:
```

```md
## Routing Decision

- User intent:
- Primary route:
- Secondary route:
- Scope:
- Domain escalation:
- Fallback used:
- Notes:
```

让关键判断可复查，而不是完全隐式。
