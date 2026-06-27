# 自主项目推进循环

定义 agent 在获得明确授权后，如何先做项目级规划，再持续推进一段可验证工作，而不是每完成一个局部动作就停下等待。

这份文件不替代 `01-workflow.md` 的阶段骨架；它把阶段骨架包成一个可重复的项目推进循环。

## 触发条件

出现以下语义时，可以进入自主推进模式：

- 用户要求“继续推进项目”“自己往下做”“按计划开发”“不要停”“自动审计修复”“推进到可用版本”或等价表达。
- 项目本地规则显式要求 agent 自主拆目标、执行、审计、修复和提交。
- 当前任务是新项目启动、原型落地、审计缺口关闭或路线图推进，且用户没有限制只做分析。

若用户明确说“先不改代码”“只分析”“不要提交”“等我确认”，则不得进入执行循环，只能做相应的规划、审计或建议。

## 初始项目规划闸门

进入循环前，先确认项目是否已有可执行路线图。没有时先生成或更新项目规划，再开始实现。

规划至少回答：

- 当前项目阶段：空项目 / 原型期 / 功能开发期 / 修复期 / 重构期 / 交付前 / 维护期。
- 当前目标：项目想达到什么可用状态。
- 现状基线：已有代码、文档、状态、测试、构建、部署入口。
- 里程碑：按 P0 / P1 / P2 或阶段拆分的目标树。
- 工作包：每个工作包的范围、验收标准、验证方式、依赖和风险。
- 第一轮目标：下一步最小但完整、可验证、可提交的工作包。

推荐产物：

- `docs/planning/PROJECT-ROADMAP.md`：阶段路线图、里程碑、风险。
- `docs/planning/NEXT-ACTIONS.md`：下一批候选工作包与排序依据。
- `docs/audit/<YYYY-MM-DD>-initial-project-audit.md`：初始项目审计或验收基线。
- `state/PROGRESS.md`：当前目标、当前循环、下一步和阻塞。

若项目已有等价文档，优先更新项目本地等价文档，不要强行新增重复真相源。

## 工作包粒度

每轮只选择一个工作包。工作包必须满足：

- 范围单一，能用一个 commit 表达。
- 有明确验收标准。
- 有可执行或可解释的验证方式。
- 失败时能回写为缺口、阻塞或下一轮修复目标。

不合格的工作包必须先拆小。不要把“做完整项目”“优化全部代码”“修所有问题”直接作为一轮执行目标。

## 循环步骤

一轮自主推进按以下顺序执行：

```text
select goal
-> confirm acceptance criteria
-> implement or fix
-> validate
-> self-audit
-> repair findings
-> revalidate when repaired
-> sync docs and state
-> commit when eligible
-> select next goal or stop with reason
```

每轮开始前必须有可恢复的 `Active Goal`；每轮结束前必须写入 `Loop Record`。若没有写入，不能把本轮声明为完成，也不能默认提交。

### 1. Select Goal

从 `state/PROGRESS.md`、路线图、审计报告、需求文档或用户最新指令中选择下一轮目标。

优先级：

1. 用户明确指定的目标。
2. P0 / 主链路 / 阻塞交付的缺口。
3. 上一轮自审发现的 Critical / High / P0 / P1 问题。
4. 路线图中的下一项可验证工作包。
5. 文档、测试、工程卫生等低风险补强。

### 2. Implement Or Fix

执行时仍遵守 `01-workflow.md` 的扫描、权威、路由、验证和同步约束。需要领域能力时委托给相应 skill；工作流层保留编排权。

### 3. Validate

按 `05-validation.md` 选择与范围匹配的验证级别。验证不足时不要把目标标记为完成。

### 4. Self-Audit

每个重要实现或修复后做一次自审。自审可以轻量，但必须回答：

- 本轮验收标准是否满足。
- 是否引入行为、文档、测试、架构或安全风险。
- 是否有未验证项。
- 是否产生新的 P0 / P1 缺口。
- 下一步最合理目标是什么。

重要或跨模块改动时，把自审写入 `docs/audit/` 并更新索引。轻量改动至少把结论写入 `state/PROGRESS.md` 或 `state/LOG.md`。

### 5. Repair Findings

自审发现 Critical / High / P0 / P1 且属于本轮范围内的问题时，默认立即修复并重新验证。

以下情况不要硬修，应记录并停止或转为下一轮目标：

- 需要用户产品决策。
- 需要外部凭据、账号、付费服务或生产环境权限。
- 修复会扩大范围，破坏单一 commit 边界。
- 风险高于当前授权。

### 6. Sync And Commit

完成后按 `07-artifact-contracts.md` 同步产物，按 `05-validation.md` 和 `01-workflow.md` 的交付闸门判断是否 commit。

同步时至少更新：

- `state/LOG.md` 或等价日志：本轮做了什么、验证证据、提交状态。
- `state/PROGRESS.md` 或等价进度：当前目标状态、自审结论、下一候选目标、停止原因。
- `state/MEMORY.md` 或等价记忆：本轮学到的持久架构事实、命令、坑、边界。
- `state/REQUIREMENTS.md` 或等价需求：验收标准、范围、done/open 状态发生变化时更新。

满足以下条件时默认原子提交：

- 当前仓库受 Git 管理。
- 本轮是单一逻辑变更。
- 验证、自审、状态同步和索引同步已完成。
- `git status` / diff 已检查，没有无关或敏感文件。
- 用户或项目规则没有禁止自动提交。

不要默认 push、merge 或 PR。

## 停止条件

自主循环只有在以下情况下停止：

- 用户要求暂停、只分析、不要继续或不要改代码。
- 下一步需要用户做产品、架构、账号、费用、隐私或破坏性操作决策。
- 验证环境缺失，且无法给出可靠替代证据。
- 连续两轮修复仍无法关闭同一阻塞问题。
- 当前变更已不再是单一工作包，需要重新规划。
- 达到用户设定的时间、token、成本或轮次预算。
- 没有可执行的下一目标；只能留下路线图或 handoff。

停止时必须写清：

- 已完成什么。
- 验证了什么。
- 为什么停止。
- 下一步最小可执行目标是什么。

## 状态记录模板

`state/PROGRESS.md` 或等价进度系统应能承载：

```md
## Active Goal

- Goal:
- Acceptance Criteria:
- Validation:
- Scope Boundary:

## Current Loop

- Status: planning / implementing / validating / self-auditing / repairing / syncing / committed / stopped
- Last Action:
- Last Validation:
- Last Self-Audit:
- Stop Reason:

## Next Candidate Goals

- [ ] P0 ...
- [ ] P1 ...
- [ ] P2 ...
```

不要求每个项目逐字使用此模板，但这些信息必须能从项目进度系统恢复。

## 与演进机制的边界

自主推进项目进度时可以自动规划、实现、审计、修复、同步和提交；但修改通用 workflow、skill 或全局规则仍遵守 `06-evolution.md`：

- 先观察和建议。
- 获得明确批准后再改框架。
- 修改后验证并同步本机或项目入口。
