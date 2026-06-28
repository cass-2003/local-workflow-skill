# 适配器 · Claude Code

> 状态：**已登记**（框架路线图阶段 3）。

## 适配器实例

Claude Code 侧现在有两类入口：

1. **执行级 skill 入口**：skills 目录里的 `SKILL.md`
2. **项目根薄入口**：仓库根 `CLAUDE.md`

本文件做**登记与映射**。当前已存在的两个入口是：

➡️ **`../../skills/workflow-orchestration/ours/project-workflow/SKILL.md`**
➡️ **`claude-code/CLAUDE.md`**

## 工作方式

- `SKILL.md`：执行级薄入口。frontmatter 提供触发语义，正文保留 CC 风格的编排框架（Core Responsibilities / Routing Rules / Guardrails / Output Discipline）。
- `CLAUDE.md`：项目级薄入口。声明默认工作方式、四态恢复、验证同步与交付纪律，并指向中立核心。
- `references/*.md`：已全部收敛为**指向中立核心的薄指针**，不再复制规范，消除与 `../core/*` 的重复。
- `agents/openai.yaml`：保留 OpenAI 风格的 interface 描述（display_name / default_prompt），供混合环境识别。

## 中立核心 → CC 入口映射

| 中立核心 | CC 适配器内的指针 |
|---|---|
| `../core/01-workflow.md` | `references/execution-phases.md` + `references/git-and-handoff.md` |
| `../core/02-state-systems.md` | `references/state-systems.md` |
| `../core/03-routing.md` | `references/routing-matrix.md` |
| `../core/04-authority.md` | `references/authority-resolution.md` |
| `../core/05-validation.md` | `references/validation-gates.md` |
| `../core/06-evolution.md` | `references/skill-evolution.md` |
| `../core/07-artifact-contracts.md` | 项目根入口与 `project-workflow` 直接指向 core |
| `../core/08-autonomous-project-loop.md` | 项目根入口与 `project-workflow` 直接指向 core |

## 单一真相原则

- 流程规范只在 `../core/*` 维护。改流程 → 改 core，不改适配器内的指针。
- 适配器只负责"在 CC 里被触发 + 指路"。新增 CC 专属约定（触发词、输出纪律）才写在 `SKILL.md` 或 `CLAUDE.md` 薄入口。

## 默认自动行为

接入后，Claude Code 侧默认按以下方式工作：

- 开工先 scan，再从四态系统恢复状态
- 若仓库缺少稳定的日志 / 需求 / 记忆 / 进度承载，先初始化最小四态骨架
- 执行完成后先过验证，再回写四态系统
- 用户要求继续推进项目时，先检查或生成路线图和下一步工作包，再按自主循环执行、验证、自审、修复、同步和提交
- 在 Git 仓库中，完成可验证修改后默认必须创建原子 commit；多逻辑变更先拆成多个 commit

默认**不**自动做：

- push
- merge
- PR 创建
- 在验证不足、状态未同步或存在无关/敏感文件时强行 commit

## 触发示例

```text
请使用 $project-workflow 先扫描当前仓库，恢复四态系统状态，只做路由分析。
请使用 $project-workflow 判断这个需求该走 audit / implement / fix / review，并说明验证与文档同步策略。
请使用 $project-workflow 检查当前改动在 commit 前是否已满足验证、文档同步和交付三道闸门。
请使用 $project-workflow 继续推进这个项目：先做/更新路线图和下一步工作包，然后按自主循环实现、验证、自审、修复和提交。
```
