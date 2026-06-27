# 产物契约：自动审计、文档与状态落点

这份文件定义“工作流动作应该留下什么文件证据”。它不是替代四态系统，而是补齐四态系统之外的结构化产物位置，让 Agent 不把审计、验收、修复和同步只留在对话里。

## 默认目录

| 动作 | 默认产物 | 必须同步 |
|---|---|---|
| status | 对话摘要；必要时更新 `state/PROGRESS.md` | `state/PROGRESS.md` |
| planning | `docs/planning/PROJECT-ROADMAP.md`、`docs/planning/NEXT-ACTIONS.md` 或项目等价文档 | `state/PROGRESS.md`、`docs/INDEX.md` |
| autonomous-loop | 路线图 + 每轮实现/验证/自审/修复产物 | `state/LOG.md`、`state/PROGRESS.md`、相关索引 |
| audit / acceptance | `docs/audit/<YYYY-MM-DD>-<scope>-audit.md` | `docs/audit/INDEX.md`、`state/LOG.md`、`state/PROGRESS.md` |
| review | 对话 findings；重要结论写入 `docs/audit/` 或相关设计文档 | `state/LOG.md` |
| implement | 代码 + 相关 docs / state | `state/LOG.md`、`state/PROGRESS.md`、必要时 `docs/INDEX.md` |
| fix | 代码 + 回归验证记录 | `state/LOG.md`、`state/PROGRESS.md`、相关 audit 报告 |
| docs-sync | 被同步的文档、索引、状态文件 | `docs/INDEX.md`、`state/LOG.md` |
| validation | 测试输出摘要；需要长期保存时写入 `docs/testing/` | `state/LOG.md` |

## 审计报告最低结构

审计报告至少包含：

- `# 审计范围与基线`
- `# TL;DR`
- `# 应有能力清单`
- `# 缺失项清单`
- `# 偏差与误判修正`
- `# 下一步计划`
- `# 待确认事项`
- `# 验证证据`

所有能力项必须显式归类为 `已实现`、`部分实现`、`未实现` 或 `未验证`。不能只复述旧报告；Critical / High 或 P0 / P1 结论必须回读对应源码、配置、测试或权威文档。

## 自主推进产物

进入自主推进循环时，不能只在对话里决定“下一步做什么”。至少要保证项目内可恢复：

- 初始规划：路线图、候选工作包、当前第一目标、验收标准。
- 每轮执行：实现或修复了什么、验证证据、自审结论、剩余缺口。
- 循环交接：下一候选目标，或明确 stop reason。

若项目已有等价的 roadmap、plan、todo、issue 或 sprint 文档，优先更新等价物；否则使用 `docs/planning/PROJECT-ROADMAP.md`、`docs/planning/NEXT-ACTIONS.md` 和 `state/PROGRESS.md`。

## 索引规则

- 新增审计报告后，更新 `docs/audit/INDEX.md` 的“当前优先查看”或“历史报告”。
- 新增重要文档后，更新 `docs/INDEX.md` 的目录表和阅读顺序。
- 若项目有 `docs/_update-log.md`，把面向文档读者的变更流水同步进去；机器恢复状态仍以四态系统为准。
- 历史路径不用批量改写，当前入口和新增引用必须使用最新路径。

## 自动化边界

- 可以默认生成审计、状态、计划、日志和索引产物。
- 不要默认删除、归档或移动旧文档；先核对引用关系。
- 不要默认覆盖已有报告；同一轮复审优先新建带日期或范围的报告，再在索引中标明取代关系。
- 不要为了凑文件生成空文档；每个产物必须有事实、证据、假设或明确待确认项。

## 交付前检查

完成声明前至少确认：

- 本轮动作对应的产物已经写入或明确说明不需要写入。
- 四态系统已同步最近变化。
- 新增报告或文档已进索引。
- 验证证据能支撑最终结论。
