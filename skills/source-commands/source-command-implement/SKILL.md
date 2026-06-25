---
name: "source-command-implement"
description: "并行实现功能。拆分任务分配给多个实现代理，并行编码。触发词：实现、implement、开发、写代码、做功能。"
---

# source-command-implement

Use this skill when the user asks to run the migrated source command `implement`.

## Command Template

## J-SOP 功能实现

### 上下文恢复
1. 读取 `docs/SPRINT-PLAN.md` 了解当前优先级和交付口径
2. 读取相关审计结论，确认当前缺口与约束
3. 读取需求相关文档 / PRD / 基线说明
4. 验证当前编译状态：
   - Extension：`cd "/j/J-SOP 伴随式自动化助手/j-sop-extension" && npx tsc --noEmit`
   - License Server：`cd "/j/J-SOP 伴随式自动化助手/j-sop-license-server" && go build ./...`

### 执行流程
1. 确认目标功能、验收标准、影响模块
2. 按依赖和文件边界拆分任务
3. 若涉及共享类型，先改 `types.ts` / 共享契约
4. 实现后验证：
   - Extension：`cd "/j/J-SOP 伴随式自动化助手/j-sop-extension" && npx tsc --noEmit`
   - License Server：`cd "/j/J-SOP 伴随式自动化助手/j-sop-license-server" && go build ./...`（如相关）
   - 不要在仓库根目录直接执行 `go build ./...`；仓库根不是 Go module
5. 若影响计划、审计、使用方式，同步文档

### 约束
- 类型/消息契约优先于业务实现
- 不改同一文件的无关部分
- 需要新消息类型时，按 `types -> SW -> CS/UI` 顺序推进
