# State Systems

## Purpose

帮助 workflow skill 在不同项目里识别“状态到底存在哪里”，而不是依赖固定文件名。

## The Four Systems

### 1. `project-log`

回答“最近发生了什么”。

常见承载体：

- update log
- changelog
- deployment log
- work journal
- issue activity summary

查找线索：

- 文件名包含 `update`、`log`、`changes`、`journal`
- 最近更新记录
- 与提交或运行记录关联的文档

### 2. `project-requirements`

回答“当前必须满足什么”。

常见承载体：

- PRD
- spec
- 客户需求清单
- 验收标准
- audit baseline

查找线索：

- 文件名包含 `prd`、`requirements`、`spec`、`acceptance`
- 审计基线、验收口径、功能清单

### 3. `project-memory`

回答“系统为什么这样设计、有哪些已知知识”。

常见承载体：

- architecture docs
- research notes
- runbook
- system map
- 操作文档

查找线索：

- 文件名包含 `architecture`、`research`、`runbook`、`operations`、`map`
- 说明结构、背景、依赖和既有决策的文档

### 4. `project-progress`

回答“现在做到哪里、下一步是什么”。

常见承载体：

- sprint plan
- roadmap
- todo
- milestone board
- blockers list

查找线索：

- 文件名包含 `sprint`、`plan`、`roadmap`、`todo`、`milestone`
- 当前阶段、剩余事项、阻塞项、下一步

## Discovery Rules

- 不要求四类系统都存在独立文件。
- 同一个文件可以同时承担两类系统。
- 优先选择更新更近、被其他本地层反复引用、与当前代码更一致的来源。
- 如果多个来源承担同一系统，优先保留“更本地、更新、更明确”的那个作为主来源。

## Output Template

```md
## State Restore

- Project log:
- Project requirements:
- Project memory:
- Project progress:
- Missing systems:
- Notes:
```
