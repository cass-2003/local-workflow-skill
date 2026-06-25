---
name: "source-command-audit"
description: "按 .windsurf/rules/1.md / 2.md / 3.md 与最新模板执行 J-SOP 审计。触发词：审计、audit、代码审计、全局审计。"
---

# source-command-audit

Use this skill when the user asks to run the migrated source command `audit`.

## Command Template

## J-SOP 项目审计

### 必须遵守的规则
1. 总纲：`/.windsurf/rules/1.md`
2. 审计产出规范：`/.windsurf/rules/2.md`
3. 涉及 `j-sop-license-server` 时追加：`/.windsurf/rules/3.md`

### 上下文恢复
1. 优先读取基线文档（冲突优先级从高到低）：
   - `docs/PRD-PDF原件-提取整理-2026-05-04.md`（最高权威：PRD PDF 原件）
   - `docs/客户整改需求清单-2026-04-30.md`
   - `docs/自动化交接-整理版.md`
   - `docs/PRD-全文摘录.md`
   - `docs/Sprint21-plan-基于Ozon参考-2026-05-04.md`
   - `docs/Sprint22-plan-2026-05-04.md`
   - `docs/调研-卖家精灵登录机制-2026-05-05.md`
2. 读取 `docs/SPRINT-PLAN.md` 了解当前计划
3. 优先读取 `docs/audit/sprint20/sprint20-global-audit-2026-05-04-v3-post-ui-refactor.md`
4. 读取 `docs/NEXT-STEPS-2026Q2.md`
5. 如需历史上下文，再读取 `docs/audit/INDEX.md` 或最近可用总结

### 冲突优先级
当文档之间存在矛盾时，按以下顺序采用：
PRD PDF 原件 > 客户整改需求清单 > 自动化交接 > PRD全文摘录 > Sprint plans > V3分析 > sprint audits

### 审计模式
- `/audit all`：全量审计，至少覆盖 Amazon / 1688 / DXM / SW+Shared / License Server / Popup+Manifest
- `/audit server`：只审 `j-sop-license-server`，按 `3.md` 的接口与核心表执行
- `/audit e2e`：追踪 Amazon -> 1688 -> DXM -> 发布 / 草稿 / 巡查 / 卡密链路
- `/audit security`：覆盖 XSS / SSRF / CORS / 凭证 / 鉴权 / sync 安全
- `/audit regression`：验证最近修复是否引入新回归
- `/audit acceptance`：按 PRD 4.4 和三文档做验收预检，输出 PASS / FAIL / DEGRADED

### 执行要求
1. 结论必须显式区分：`已实现` / `部分实现` / `未实现` / `未验证`
2. 不能只复述旧报告；Critical / High 项至少回读对应源码或配置
3. 若 `SPRINT-PLAN` 与三份基线文档冲突，必须单列指出冲突
4. 优先套用：
   - `docs/audit/TEMPLATE-GLOBAL-AUDIT.md`
   - `docs/audit/TEMPLATE-SERVER-AUDIT.md`
5. 报告统一写入 `docs/audit/sprint{N}/`，并更新 `docs/audit/INDEX.md`

### 最终输出结构
- `# 审计范围与基线`
- `# TL;DR`
- `# 应有能力清单`
- `# 缺失项清单`
- `# 偏差与误判修正`
- `# 下一步计划`
- `# 待确认事项`
- `# 验证证据`
