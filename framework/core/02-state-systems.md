# 四态系统：发现与读写规则

帮助工作流在不同项目里识别"状态到底存在哪里"，而不是依赖固定文件名。这是整个框架的核心。

## 四态系统

### 1. 日志系统 `project-log`

回答"最近发生了什么"。

- **默认承载**：`LOG.md`
- **常见等价物**：update log、changelog、deployment log、work journal、issue 活动摘要
- **发现线索**：文件名含 `update / log / changes / journal`；最近更新记录；与提交或运行记录关联的文档

### 2. 需求系统 `project-requirements`

回答"当前必须满足什么"。

- **默认承载**：`REQUIREMENTS.md`
- **常见等价物**：PRD、spec、客户需求清单、验收标准、audit baseline
- **发现线索**：文件名含 `prd / requirements / spec / acceptance`；审计基线、验收口径、功能清单

### 3. 记忆系统 `project-memory`

回答"系统为什么这样设计、有哪些已知知识"。

- **默认承载**：`MEMORY.md`
- **常见等价物**：architecture docs、research notes、runbook、system map、操作文档
- **发现线索**：文件名含 `architecture / research / runbook / operations / map`；说明结构、背景、依赖与既有决策的文档

### 4. 进度系统 `project-progress`

回答"现在做到哪里、下一步是什么"。

- **默认承载**：`PROGRESS.md`
- **常见等价物**：sprint plan、roadmap、todo、milestone board、blockers list
- **发现线索**：文件名含 `sprint / plan / roadmap / todo / milestone`；当前阶段、剩余事项、阻塞项、下一步

## 发现规则

- 状态文件不一定在仓库根：先扫常见承载目录 `state/`、`docs/`、`.agent-os/`、`.codex/`、`.claude/`，再按上面的文件名线索匹配。
- 不要求四类系统都有独立文件。
- 同一个文件可以同时承担两类系统。
- 优先选更新更近、被其他本地层反复引用、与当前代码更一致的来源。
- 多个来源承担同一系统时，保留"更本地、更新、更明确"的那个作为主来源。
- 项目里**完全没有**某系统时，按需用 `state-systems/templates/` 下的模板新建，或在状态记录里标记 missing。

## 读：状态恢复输出模板

```md
## State Restore

- Project log:        <承载文件 / missing>
- Project requirements: <承载文件 / missing>
- Project memory:     <承载文件 / missing>
- Project progress:   <承载文件 / missing>
- Missing systems:
- Notes:
```

## 写：回写约定

在 Phase 7（Docs & State Sync）把成果分类回写：

| 发生了什么 | 写到哪个系统 |
|---|---|
| 做了一次变更 / 部署 / 运行 | 日志系统 |
| 需求、验收口径、基线变化 | 需求系统 |
| 产生了新的架构决策 / 结论 / 已知坑 | 记忆系统 |
| 任务推进、阻塞、下一步变化 | 进度系统 |

回写时保持**追加而非覆盖**（日志/进度尤其如此），让历史可回看。
