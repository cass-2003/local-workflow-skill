# Routing Matrix

## Purpose

把模糊请求稳定映射到正确的工作流路线，不只靠关键词硬猜。

## Primary Routes

| 用户意图 | 常见表达 | 主路由 | 常见次路由 |
|---|---|---|---|
| status | 状态、进度、现在到哪了、当前情况 | `status` | truth docs |
| audit | 审计、差距分析、基线检查、验收预检 | `audit` | `review` |
| implement | 实现、开发、做功能、新增能力 | `implement` | `validation` |
| fix | 修复、repair、close findings、批量修 bug | `fix` | `review` |
| review | review、检查 diff、找风险、代码评审 | `review` | `validation` |
| docs sync | 更新文档、同步计划、归档、补记录 | `sync-docs` | `status` / `audit` |
| git delivery | commit、push、branch、PR、merge | Git 相关 skill | `validation` / `sync-docs` |
| workflow evolution | 优化 skill、流程、路径、编排 | `project-workflow` | `sync-docs` |

## Disambiguation Rules

- “检查最近改动有没有问题”通常是 `review`，不是 `audit`。
- “关闭审计缺口”通常是 `fix`，不是 `audit`。
- “按需求做功能”通常是 `implement`，不是 `review`。
- “更新计划或记录”通常是 `sync-docs`，不是 `status`。
- “为什么这套流程开始混乱”通常先走 workflow evolution，而不是直接编码。

## Scope Overrides

范围可以覆盖关键词判断：

- 仓库级基线比对：更像 `audit`
- 单个 diff 检查：更像 `review`
- 只看状态、不改内容：更像 `status`
- 代码 + 文档 + 验证一起做：更像 `implement` 或 `fix`
- 只做交付打包：更像 Git flow

## Routing Output Template

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
