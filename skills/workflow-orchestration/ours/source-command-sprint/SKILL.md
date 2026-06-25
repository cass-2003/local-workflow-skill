---
name: "source-command-sprint"
description: "Sprint 计划管理。查看/更新冲刺进度，规划每日任务。触发词：sprint、冲刺、进度、每日计划。"
---

# source-command-sprint

Use this skill when the user asks to run the migrated source command `sprint`.

## Command Template

## J-SOP Sprint 管理

### 上下文恢复
1. 读取 `docs/SPRINT-PLAN.md`
2. 读取 `docs/_update-log.md`
3. 读取 `docs/audit/sprint20/sprint20-global-audit-2026-05-04-v3-post-ui-refactor.md`
4. 读取 `docs/客户整改需求清单-2026-04-30.md`
5. 读取 `docs/e2e/sprint20-e2e-master-plan-2026-05-04.md`
6. 读取 `docs/DELIVERY-PLAN-2026-04-23.md`
7. 如存在 `docs/audit/INDEX.md`，补充读取修复进度

### 操作
- `/sprint status`：当前进度、剩余工作日、下一步
- `/sprint plan`：按当前真实优先级重排任务
- `/sprint update`：把刚完成的工作同步进 Sprint 文档
- `/sprint next`：输出今天应做的具体任务

### 当前时间口径
- 起始：2026-04-09
- 当前版本：V27.32 (2026-05-04)
- 第一交付点：2026-04-29
- 完整交付上限：2026-05-09

### 当前优先级
1. P0 G3 颜色变体主图真机实测
2. P0 1688 选品库 B-NEW 链路 E2E
3. P0 §2.2.5/§2.2.6 客户验收
4. P1 Phase 2 后台面板拆分
5. P1 G4 ACOS 关停
6. P2 G1-UI 多变体勾选 + H3

### 规则
- 若 `SPRINT-PLAN` 与最新全局审计结论冲突，必须显式指出冲突
- 优先采用最新审计刷新与交付倒排结论，不沿用过时乐观判断
