---
name: fix
description: "Team 模式批量修复审计问题。并行派发修复代理，按优先级修复 Critical>High>Medium。触发词：修复、fix、批量修复。"
---

## J-SOP 批量修复

### 上下文恢复
1. 读取 `docs/audit/AUDIT-SUMMARY.md` 了解待修复清单
2. 读取 `docs/SPRINT-PLAN.md` 了解当前进度
3. `npx tsc --noEmit` 检查编译状态

### 执行规范
1. TeamCreate 创建修复团队
2. 按文件依赖分组（SW组/CS组/DXM组/Server组/Shared组）
3. 每组一个 Sonnet 代理（mode: bypassPermissions）
4. 代理 prompt 含：问题ID+文件路径+修复方案+先Read再改+tsc确认+注释标注ID
5. 全部完成后验证编译+更新文档+关闭团队

### 分组策略
- SW组：service-worker.ts + messages.ts + storage.ts
- CS组：amazon/*.ts + alibaba/*.ts
- DXM组：dianxiaomi/*.ts
- Server组：j-sop-license-server/*.go
- Shared组：types.ts + selectors.ts + config.ts + constants.ts
