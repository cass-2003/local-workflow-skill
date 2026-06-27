# CLAUDE.md · 四态工作流（Claude Code 适配模板）

> 这是「四态工作流框架」的 **Claude Code 项目根入口模板**。把本文件复制到目标项目根，
> 让 Claude Code 在项目级先按四态工作流思考。流程规范的**单一真相**在框架中立核心，本文件只负责被触发并指路。

## 角色

Claude Code 可把仓库根的 `CLAUDE.md` 作为项目级说明入口。本适配器保持薄：

- 不复制流程规范
- 不替代项目真相文档
- 只声明默认工作方式，并指向中立核心

## 工作方式（10 阶段）

接到中等以上复杂度任务时，按固定顺序推进：

```text
scan → state restore → intent → authority → route → execute → validate → sync → deliver → evolve
```

- 任何实质性工作前，先从**四态系统**（日志 / 需求 / 记忆 / 进度）恢复项目状态。
- 若项目还没有稳定的四态承载文件，先用框架模板初始化最小骨架，并补齐当前目标/约束/焦点/最近变更。
- 完成必须有与范围匹配的验证证据，不靠口头声明。
- 变更后把成果分类回写四态系统。
- 若验证通过、四态已同步、且本轮是单一逻辑改动，则默认创建原子 commit。
- commit / push / PR 前过验证、文档、交付三道闸门；不要默认 auto-push 或 auto-merge。

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
| 审计/验证/文档/状态产物契约 | `.agent-os/framework/core/07-artifact-contracts.md` |

## 与 Claude Code Skill 的关系

- 项目级 `CLAUDE.md`：定义当前仓库的默认工作方式
- 执行级 `SKILL.md`：承载更细粒度的命令语义或专门能力

若项目内已安装 `project-workflow` 之类本地 skill，可把本文件视为项目级薄入口，而把执行细节委托给 skill。

## 触发示例

```text
按四态工作流先扫描仓库、恢复四态系统状态，只做路由分析，不改代码。
按四态工作流判断该走 audit / implement / fix / review，并说明验证与文档同步策略。
按四态工作流检查当前改动在 commit 前是否满足验证、文档同步、交付三道闸门。
若仓库缺少日志/需求/记忆/进度系统，先初始化最小四态骨架，再继续开发。
```
