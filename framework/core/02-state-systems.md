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
- 对新项目或 workflow 首次接入，默认目标是补齐四态最小骨架，而不是长期容忍 missing。
- 推荐初始化位置优先级：项目已有 `state/` 目录 > `.agent-os/state/` > 仓库根文档；保持四类系统尽量集中，方便恢复。
- 初始化后立刻填入最小有效内容：当前目标、当前焦点、最近变更、关键约束；不要只复制空模板。

## 读：状态恢复输出模板

实质性工作开始前，状态恢复不是“确认文件存在”即可。至少要读取并摘要当前项目的四态主来源；若发现主来源仍是占位模板，必须标记为 `stale/placeholder`，并在本轮先补最小有效事实。

推荐读取顺序：

1. `project-progress`：当前焦点、活跃目标、下一步、阻塞。
2. `project-log`：最近变更、验证、部署、审计记录。
3. `project-memory`：架构事实、关键决策、已知坑、外部资源。
4. `project-requirements`：当前目标、验收标准、P0/P1、合规边界。

若项目同时有 `docs/INDEX.md` 或审计索引，也应读取它们来定位真相文档，而不是凭文件名随机打开。

### State Restore Gate

开始编码、审计、修复或提交前，agent 必须先完成下面的恢复闸门：

- 明确四态主来源分别是什么；缺失时创建或映射等价承载。
- 读取四态主来源，而不是只检查文件存在。
- 标记 `missing`、`stale`、`placeholder`、`conflict` 四类风险。
- 若遇到 `<任务>`、`<项目由哪些部分组成>`、`待补充`、`TBD` 等占位内容，先用当前仓库事实补最小可用内容；无法补齐时在进度系统记录原因和下一步。
- 在对话或交接中给出 `State Restore` 摘要；当恢复结论改变项目状态时，同步写回 `state/PROGRESS.md` 或等价进度系统。

```md
## State Restore

- Project log:        <承载文件 / missing>
- Project requirements: <承载文件 / missing>
- Project memory:     <承载文件 / missing>
- Project progress:   <承载文件 / missing>
- Stale or placeholder systems:
- Missing systems:
- Latest known goal:
- Latest known validation:
- Latest known blocker:
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

## 写：强触发条件

以下情况必须写回状态，不要只在对话里说明：

- 实现 / 修复 / 部署 / 验证 / 审计 / 文档同步完成。
- 当前目标、验收标准、下一步、阻塞、停止原因变化。
- 学到可复用的运行命令、环境坑、部署路径、凭据边界、外部依赖。
- 需求范围、优先级、合规约束或 done/open 状态变化。
- 自主推进循环结束一轮，或因为 stop condition 停止。

若判断无需写入，交付时要说明“未写状态的原因”。

### Loop Record

自主推进、审计修复、重要实现、验收预检或跨 agent 交接结束时，必须留下可恢复的循环记录。优先写入 `state/PROGRESS.md`，需要历史流水时同时追加 `state/LOG.md`。

```md
## Loop Record · <YYYY-MM-DD> · <scope>

- Goal:
- Acceptance Criteria:
- Validation Evidence:
- Self-Audit:
- Repairs:
- State/Docs Sync:
- Commit:
- Next Goal:
- Stop Reason:
```

`Stop Reason` 不能只写“完成”或“等待”；要写明下一步为什么不能由 agent 继续安全推进，或下一轮最小可执行目标是什么。

## 首次初始化建议

当工作流发现仓库尚无稳定状态承载时，建议一次性创建：

- `state/LOG.md`
- `state/REQUIREMENTS.md`
- `state/MEMORY.md`
- `state/PROGRESS.md`

模板来源：`../state-systems/templates/`

初始化后至少补：

- `LOG.md`：本次接入 workflow / 初始化四态的记录
- `REQUIREMENTS.md`：当前项目目标、首批需求或已知约束
- `MEMORY.md`：系统边界、关键依赖、现阶段已知决策
- `PROGRESS.md`：当前焦点、进行中、待办、阻塞
