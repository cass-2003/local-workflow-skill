---
name: status
description: "快速查看项目状态。一条命令了解编译状态、Sprint 进度、修复进度、全局缺口、最近更新、Git 变更和下一步。触发词：status、状态、进度、现在到哪了。"
---

## J-SOP 快速状态检查（项目地址为 J:\J-SOP 伴随式自动化助手\）

### 执行步骤（全自动，不停顿）

1. **编译状态**

```bash
# Windows / PowerShell 优先，不要使用 grep / tail
# Extension
npx tsc --noEmit 2>&1 | Select-String "error TS" | Measure-Object | ForEach-Object { $_.Count }

# License Server
$out = go build ./... 2>&1 | Out-String; ([regex]::Matches($out, 'error')).Count
```

2. **Sprint 进度**
   读取 `docs/SPRINT-PLAN.md`，至少提取：
   - `### 1.1` 工作记录条数
   - 当前所处 `Day N`
   - 剩余工作日 / 是否已进入缓冲区

3. **修复进度**
   优先读取：
   - `docs/audit/AUDIT-SUMMARY.md`
   若不存在，自动在 `docs/audit/` 下查找最近可用的 `AUDIT-SUMMARY.md`
   提取修复总数、Critical / High / Medium 完成情况

4. **最近更新**
   读取 `docs/_update-log.md` 前 20 行

5. **全局缺口**
   优先读取：
   - `docs/audit/AUDIT-GLOBAL-2026Q2.md`
   - `docs/NEXT-STEPS-2026Q2.md`
   若存在，提取：
   - Critical 缺口数
   - 当前最大阻塞项
   - 当前推荐下一步
   若不存在，则回退为 `SPRINT-PLAN` 剩余工作

6. **Git 状态**

```bash
git diff --stat HEAD | Select-Object -Last 1
```

### 输出要求

- 必须先给一屏摘要，再给补充明细
- 如果某个文件缺失，必须写明 fallback 来源
- 如果编译命令输出为空但 exit code=0，应按 0 error 处理
- 如果 `SPRINT-PLAN` 与 `AUDIT-GLOBAL` 结论冲突，必须单列一行 `⚠️ 冲突`

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
2. `docs/audit/AUDIT-GLOBAL-2026Q2.md`
3. `docs/NEXT-STEPS-2026Q2.md`
4. `docs/SPRINT-PLAN.md`
5. 历史 `AUDIT-SUMMARY.md`
