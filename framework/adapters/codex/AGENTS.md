# AGENTS.md · 四态工作流（Codex 适配模板）

> 这是「四态工作流框架」的 **Codex 适配模板**。把本文件（连同 `agents/`）复制到目标项目根，
> 让 Codex 以原生方式触发同一套流程。流程规范的**单一真相**在框架中立核心，本文件只负责被触发并指路。

## 角色

Codex 在仓库根发现 `AGENTS.md`。本适配器是薄入口：不复制规范，只声明工作方式并指向中立核心。

## 工作方式（10 阶段）

接到任务时按固定顺序推进：

```text
scan → state restore → intent → authority → route → execute → validate → sync → deliver → evolve
```

- 任何实质性工作前，先从**四态系统**（日志 / 需求 / 记忆 / 进度）恢复项目状态。
- 完成必须有与范围匹配的验证证据，不靠口头声明。
- 变更后把成果分类回写四态系统。
- commit / push / PR 前过验证、文档、交付三道闸门。

## 规范指针（单一真相在中立核心）

> 把目标项目里框架核心的实际位置替换到下面路径。若按推荐方式安装在 `.agent-os/framework/`，则如下：

| 需要什么 | 读这里 |
|---|---|
| 工作流 10 阶段细节 | `.agent-os/framework/core/01-workflow.md` |
| 四态系统发现/读写 | `.agent-os/framework/core/02-state-systems.md` |
| 意图→能力库路由 | `.agent-os/framework/core/03-routing.md` |
| 多层规则权威解析 | `.agent-os/framework/core/04-authority.md` |
| 验证/文档/交付闸门 | `.agent-os/framework/core/05-validation.md` |
| 重复模式保守沉淀 | `.agent-os/framework/core/06-evolution.md` |

## 触发示例

```text
按四态工作流先扫描仓库、恢复四态系统状态，只做路由分析，不改代码。
按四态工作流判断该走 audit / implement / fix / review，并说明验证与文档同步策略。
按四态工作流检查当前改动在 commit 前是否满足验证、文档同步、交付三道闸门。
```
