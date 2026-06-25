---
name: "source-command-status"
description: "快速查看项目状态。一条命令了解编译状态、Sprint 进度、修复进度、全局缺口、最近更新、Git 变更和下一步。触发词：status、状态、进度、现在到哪了。"
---

# source-command-status

Use this skill when the user asks to run the migrated source command `status`.

## Command Template

## J-SOP 快速状态检查（项目地址为 J:\J-SOP 伴随式自动化助手）

### 执行步骤
1. **编译状态**
   - 固定项目根目录：`J:\J-SOP 伴随式自动化助手`（Bash 路径：`/j/J-SOP 伴随式自动化助手`）
   - Extension：`cd "/j/J-SOP 伴随式自动化助手/j-sop-extension" && npx tsc --noEmit`
   - License Server：`cd "/j/J-SOP 伴随式自动化助手/j-sop-license-server" && go build ./...`
   - 不要在仓库根目录直接执行 `go build ./...`；仓库根不是 Go module
   - 构建命令不要和文档读取/Git 状态放在同一并行批次；构建失败会取消同批次工具调用
2. **Sprint 进度**
   - 读取 `docs/SPRINT-PLAN.md`
   - 至少提取：工作记录条数、当前所处时间段、剩余工作日、是否进入缓冲区
3. **修复进度**
   - 优先读取 `docs/audit/INDEX.md`（当前主索引）
   - 若不存在，则在 `docs/audit/sprint20/` 下查找最近的 v2-baseline / closure 报告
   - 提取修复总数、Critical / High / Medium 完成情况
4. **最近更新**
   - 读取 `docs/_update-log.md` 前 20 行
5. **全局缺口**
   - 优先读取：
     - `docs/audit/sprint20/sprint20-global-audit-2026-05-04-v3-post-ui-refactor.md`
     - `docs/audit/sprint18/sprint18-global-audit-2026-04-27-v6.md`
     - `docs/NEXT-STEPS-2026Q2.md`
     - 若存在，提取：
     - Critical 缺口数
     - 当前最大阻塞项
     - 当前推荐下一步
      若不存在，则回退为 `SPRINT-PLAN` 剩余工作
6. **Git 状态**
   - 读取 `git diff --stat HEAD` 摘要

### 输出要求
- 必须先给一屏摘要，再给补充明细
- 如果某个文件缺失，必须写明 fallback 来源
- 如果 `SPRINT-PLAN` 与最新全局审计冲突，必须单列 `冲突`
- 状态判断优先级：当前命令输出 > 最新全局审计刷新 > NEXT-STEPS > SPRINT-PLAN > 历史汇总

### 摘要必须包含
- build status
- sprint progress
- fix progress
- global gap summary
- latest update
- git diff summary
- next step

### 输出格式（一屏搞定）

```
⚡ J-SOP 项目状态 (YYYY-MM-DD)

📅 Sprint: Day N / 20~30 天 | 剩余 N 工作日
🔨 编译: TS ✅ 0 errors | Go ✅ 0 errors
🐛 修复: N/50 (N%) | Critical N/8 | High N/16 | Medium N/23
🚨 全局缺口: Critical N | 最大阻塞 [缺口名]
📝 最近: [上次完成的工作摘要]
📊 验收概率:
  场景1 Amazon:  ██████░░░░ N%
  场景2 搜图:    █████████░ N%
  场景3 1688:    ████████░░ N%
  场景4 DXM:     ██████░░░░ N%
  场景5 草稿:    █████████░ N%

🎯 下一步: [具体任务]
```

### 补充明细（摘要后 3~6 行内）

补充明细必须尽量短，但至少包含：

- `Sprint 已完成记录数`
- `修复进度来源`
- `全局缺口来源`
- `Git 变更概览`
- 如有冲突：`⚠️ 冲突: Sprint-Plan 与 Global Audit 的优先级不一致`

### 状态判断优先级

当多个文档结论不一致时，按以下优先级采用：

1. 当前编译/命令输出
2. `docs/audit/sprint20/sprint20-global-audit-2026-05-04-v3-post-ui-refactor.md`
3. `docs/NEXT-STEPS-2026Q2.md`
4. `docs/SPRINT-PLAN.md`
5. 历史 `docs/audit/INDEX.md` 指向的归档报告
