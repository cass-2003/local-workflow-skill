---
name: implement
description: "Team 模式并行实现功能。拆分任务分配给多个实现代理，并行编码。触发词：实现、implement、开发、写代码、做功能。"
---

## J-SOP Team 模式功能实现

### 上下文恢复
1. 读取 `docs/SPRINT-PLAN.md` 了解当前 Day 和待做任务
2. 读取 `docs/audit/AUDIT-SUMMARY.md` 了解已修复/待修问题
3. 读取 `docs/audit/AUDIT-R10-DEEP.md` 或 `AUDIT-R11-DEEP.md`（如实现 R10/R11）
4. `npx tsc --noEmit` 确认当前编译状态

### 执行流程

1. **需求分析**：确认 PRD 编号 + 验收标准 + 当前代码状态
2. **任务拆分**：按文件依赖分组，确定并行度
3. **TeamCreate** 创建实现团队
4. **每组一个 Agent**：使用 `jsop-implementer` agent 定义，prompt 中注入：
   - 具体功能描述
   - 涉及文件列表
   - 期望的消息类型/数据流
   - 验收标准
5. **编译验证**：全部完成后 `tsc --noEmit` + `go build`
6. **回归检查**：运行 `jsop-regression-checker`
7. **文档更新**：运行 `jsop-doc-syncer`
8. **关闭团队**

### 并行分组原则
- **类型组**：types.ts + selectors.ts（其他组依赖，必须先完成）
- **SW 组**：service-worker.ts 新 handler
- **CS 组**：content-scripts 业务逻辑（可多个并行，只要不改同一文件）
- **Server 组**：Go 后端（与前端完全独立）
- **UI 组**：popup/panel 展示

### 注意事项
- 类型组必须最先完成，其他组才能开始
- 如果需要新消息类型，types.ts 先改，SW 再改，CS 最后
- 图片处理（R11）DOM 替换方案需要先 Spike 验证
