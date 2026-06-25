# 路由矩阵：意图 → 执行能力

把模糊请求稳定映射到正确的工作流路线和能力库技能，不只靠关键词硬猜。

## 主路由（按意图）

| 用户意图 | 常见表达 | 主路由 | 常见次路由 |
|---|---|---|---|
| status | 状态、进度、现在到哪了、当前情况 | `status` | 读四态系统 |
| audit | 审计、差距分析、基线检查、验收预检 | `audit` | `review` |
| implement | 实现、开发、做功能、新增能力 | `implement` | `validation` |
| fix | 修复、repair、close findings、批量修 bug | `fix` | `review` |
| review | review、检查 diff、找风险、代码评审 | `review` | `validation` |
| docs sync | 更新文档、同步计划、归档、补记录 | `sync-docs` | `status` / `audit` |
| git delivery | commit、push、branch、PR、merge | git flow | `validation` / `sync-docs` |
| evolution | 优化流程、路径、编排规则 | `evolution` | `sync-docs` |

## 二级路由：执行能力 → 能力库（`skills/`）

`implement` / `fix` 真正动手时，按问题域委托到能力库对应类别：

| 问题域 | 能力库类别 | 代表技能 |
|---|---|---|
| 通用工程模式 | `engineering-core/` | api-versioning、rate-limiting、idempotency、pagination、structured-logging |
| 后端 / 基础设施 | `backend-infra/` | background-jobs、dockerfile-best、websocket-impl |
| 前端 / 插件 / 抓取 | `frontend-extension/` | chrome-mv3-ext、css-modern-2025、dom-scraping、preact-popup |
| 同步 / 校验 / 数据约束 | `data-sync-validation/` | validation-schema、validation-pipeline、sync-bidirectional |
| 语言运行时通用能力 | `language-runtime/` | datetime-timezones |
| 项目命令封装 | `source-commands/` | audit / fix / implement / review / status / sprint / sync-docs |
| 工作流编排本身 | `workflow-core/` | local-workflow（样本）、project-workflow（CC 实例） |

> 能力库随筛选会变化，权威以 `skills/` 实际目录为准；新增类别时回这里补一行。

## 消歧规则

- "检查最近改动有没有问题"通常是 `review`，不是 `audit`。
- "关闭审计缺口"通常是 `fix`，不是 `audit`。
- "按需求做功能"通常是 `implement`，不是 `review`。
- "更新计划或记录"通常是 `sync-docs`，不是 `status`。
- "为什么这套流程开始混乱"通常先走 `evolution`，而不是直接编码。

## 范围覆盖

范围可以覆盖关键词判断：

- 仓库级基线比对 → `audit`
- 单个 diff 检查 → `review`
- 只看状态不改内容 → `status`
- 代码 + 文档 + 验证一起做 → `implement` 或 `fix`
- 只做交付打包 → git flow

## 路由输出模板

```md
## Routing Decision

- User intent:
- Primary route:
- Secondary route:
- Skill library target:   <能力库类别 / 具体技能 / none>
- Scope:
- Domain escalation:
- Fallback used:
- Notes:
```
