---
name: "source-command-fix"
description: "批量修复审计问题。按优先级修复 Critical > High > Medium。触发词：修复、fix、批量修复。"
---

# source-command-fix

Use this skill when the user asks to run the migrated source command `fix`.

## Command Template

## J-SOP 批量修复

### 上下文恢复
1. 读取当前审计结论，优先：
   - `docs/audit/sprint18/sprint18-global-audit-2026-04-27-v6.md`
   - `docs/audit/sprint20/sprint20-global-audit-2026-05-04-v3-post-ui-refactor.md`
   - `docs/audit/INDEX.md`
2. 读取 `docs/SPRINT-PLAN.md`
3. 验证当前编译状态：
   - Extension：`cd "/j/J-SOP 伴随式自动化助手/j-sop-extension" && npx tsc --noEmit`
   - License Server：`cd "/j/J-SOP 伴随式自动化助手/j-sop-license-server" && go build ./...`
   - 不要在仓库根目录直接执行 `go build ./...`；仓库根不是 Go module

### 执行规则
1. 按 `Critical > High > Medium` 修复
2. 按文件依赖分组（Shared/CS/DXM/SW/Server/UI）
3. 修改前先 Read 当前文件，不凭印象
4. 只做最小必要改动，不顺手改无关代码
5. 完成后重新验证编译
6. 如修复影响计划、审计或使用方式，更新相关文档
