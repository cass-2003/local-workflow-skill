---
name: audit
description: "Team 模式全局代码审计。按 1.md/2.md/3.md 新规则，对照三份基线文档输出：应有能力清单、缺失项清单、风险分级、下一步计划、验证证据。触发词：审计、audit、代码审计、全局审计。"
---

## J-SOP 项目全局代码审计

### 必须遵守的规则
1. 总纲：`/.codex/rules/1.md`
2. 审计产出规范：`/.codex/rules/2.md`
3. 涉及 `j-sop-license-server` 时追加遵守：`/.codex/rules/3.md`

### 上下文恢复
1. 优先读取三份基线文档：
   - `docs/交接材料分析-2026Q2.md`
   - `docs/自动化交接-问答摘录.md`
   - `docs/PRD-全文摘录.md`
2. 读取 `docs/SPRINT-PLAN.md` 了解当前计划
3. 优先读取 `docs/audit/AUDIT-GLOBAL-2026Q2.md`
4. 如需历史上下文，再读取 `docs/audit/AUDIT-SUMMARY.md`；若缺失则在 `docs/audit/` 下查找最近可用版本

### 审计模式
**`/audit all`**：全量审计，至少覆盖 Amazon / 1688 / DXM / SW+Shared / License Server / Popup+Manifest

**`/audit server`**：只审 `j-sop-license-server`，按 `3.md` 的接口、核心表、按文件映射执行

**`/audit e2e`**：端到端链路审计，追踪 Amazon→1688→DXM→发布→完成

**`/audit security`**：安全深度扫描，覆盖 XSS / SSRF / CORS / 凭证 / 鉴权 / sync 安全

**`/audit regression`**：验证最近修复是否引入回归

**`/audit acceptance`**：按 PRD §4.4 和三文档做验收预检，输出 PASS / FAIL / DEGRADED

### 执行规范
1. 使用并行代理分模块审计，但最终必须合并成统一口径
2. 所有结论必须显式区分：`已实现` / `部分实现` / `未实现` / `未验证`
3. 不能只复述旧报告；Critical / High 项至少回读对应源码或配置
4. 若 `SPRINT-PLAN` 与三份基线文档冲突，必须单列指出冲突
5. 报告统一写入 `docs/audit/sprint{N}/`，并更新 `docs/audit/INDEX.md`

### 产物要求
- `/audit all`：至少输出 1 份全局报告 + 若干模块报告
- `/audit server`：至少输出 1 份 `license-server` 专项报告 + 如有必要附带全局结论摘录
- `/audit acceptance`：必须输出 5 场景验收结果，并在全局报告中映射到缺失项
- `/audit regression`：必须显式区分“旧问题未修”与“新回归”

优先套用以下模板文件：
- `docs/audit/TEMPLATE-GLOBAL-AUDIT.md`
- `docs/audit/TEMPLATE-SERVER-AUDIT.md`

### 最终输出格式
最终全局报告必须包含以下章节：
- `# 审计范围与基线`
- `# TL;DR`
- `# 应有能力清单`
- `# 缺失项清单`
- `# 偏差与误判修正`
- `# 下一步计划`
- `# 待确认事项`
- `# 验证证据`

### 最小表格字段
- **应有能力清单**：`能力` `来源文档` `验收口径` `当前状态` `证据`
- **缺失项清单**：`ID` `缺口` `来源` `当前实现` `影响` `风险等级` `建议工时`
- **下一步计划**：`优先级` `目标` `涉及模块/文件` `预估工时` `依赖/阻塞`

### 输出目标
审计的最终目标不是只产出“问题清单”，而是明确回答：
- 当前项目是否可验收
- 最大缺口是什么
- 哪些是完全缺失，哪些只是部分实现
- 风险等级如何分布
- 下一步先做什么
