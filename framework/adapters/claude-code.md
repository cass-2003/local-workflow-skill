# 适配器 · Claude Code

> 状态：**已登记**（框架路线图阶段 3）。

## 适配器实例

Claude Code 在 skills 目录里发现并触发 `SKILL.md`，所以本适配器的可执行入口必须落在 skills 位置，而不在 `adapters/` 下。本文件只做**登记与映射**，真正的入口是：

➡️ **`../../skills/workflow-orchestration/ours/project-workflow/SKILL.md`**

## 工作方式

- `SKILL.md`：薄入口。frontmatter 提供触发语义，正文保留 CC 风格的编排框架（Core Responsibilities / Routing Rules / Guardrails / Output Discipline）。
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

## 单一真相原则

- 流程规范只在 `../core/*` 维护。改流程 → 改 core，不改适配器内的指针。
- 适配器只负责"在 CC 里被触发 + 指路"。新增 CC 专属约定（触发词、输出纪律）才写在 `SKILL.md` 正文。

## 触发示例

```text
请使用 $project-workflow 先扫描当前仓库，恢复四态系统状态，只做路由分析。
请使用 $project-workflow 判断这个需求该走 audit / implement / fix / review，并说明验证与文档同步策略。
请使用 $project-workflow 检查当前改动在 commit 前是否已满足验证、文档同步和交付三道闸门。
```
