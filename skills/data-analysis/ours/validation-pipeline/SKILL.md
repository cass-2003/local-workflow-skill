---
name: validation-pipeline
description: "J-SOP 项目级验证流水线规范。覆盖扩展端 (npx tsc --noEmit / npm run build / biome check) + 服务端 (go build / go vet / go test -race) + git diff --check (CRLF/whitespace) + 烟测 (admin/user-panel/index 三面板加载) + sensitive 资产扫描。当用户提到验证、validation、编译检查、type-check、go build、smoke test、烟测、CRLF、合规检查、PR 检查时使用。"
---

# Validation Pipeline Skill — J-SOP 提交前检查规范

## 何时使用

- **每次** commit 前
- 部署前最终检查
- PR review 时验证作者是否做过基本检查
- 排查"昨天还能跑今天编译失败"

## 一、四级验证矩阵

| 级别 | 内容 | 时长 | 必须 |
|---|---|---|---|
| **L1: 静态** | tsc / go vet / biome | <30s | ✅ 每次 commit |
| **L2: 编译** | vite build / go build | <2min | ✅ 每次 commit |
| **L3: 烟测** | 三面板加载 + 关键流程 | <5min | ✅ 部署前 |
| **L4: 回归** | 自动化测试套件 | <30min | 大版本前 |

## 二、扩展端 (j-sop-extension/)

### L1: 静态检查

```bash
cd j-sop-extension

# TypeScript 类型检查（不输出，只检查）
npx tsc --noEmit
# 预期：exit 0，无 "error TS" 输出
# Windows PowerShell 计数：
npx tsc --noEmit 2>&1 | Select-String "error TS" | Measure-Object | ForEach-Object { $_.Count }
# 应输出 0

# Biome lint（J-SOP 用 biome 不是 eslint）
npm run lint
# 修复：
npm run lint:fix
```

### L2: 编译

```bash
npm run build
# 预期：dist/manifest.json + dist/assets/*.js 生成
# 已知告警：dynamic import warning（vite 对某些 lazy import 的提示，不阻塞）
```

### L3: 烟测（手动）

1. 打开 `chrome://extensions` → 重新加载 j-sop-extension
2. **Popup**：点击扩展图标 → 看到 4 个 tab，每个 tab 内容渲染
3. **1688 SRP**：访问 `https://s.1688.com/...?keywords=test` → 看到加入对比按钮注入
4. **1688 PDP**：访问 `https://detail.1688.com/offer/...html` → 看到"加入选品库"按钮 + 一件代发筛选生效
5. **Amazon SRP**：访问 `https://amazon.co.jp/s?k=test` → 看到选品过滤 sprite 字段读取
6. **店小秘编辑页**：从 1688 PDP 加入选品库 → 自动跳转 DXM 编辑页 → AI 文案对话框可打开

## 三、服务端 (j-sop-license-server/)

### L1+L2: 编译

```bash
cd j-sop-license-server

# 编译
go build ./...
# 预期：exit 0，生成 j-sop-license-server.exe（Windows）

# go vet（捕获常见错误，如未关闭 rows、错误 format string）
go vet ./...
# 预期：exit 0
```

### L3: 烟测

```bash
# 启动
./j-sop-license-server -port 8088 -admin-token=test123 &

# 公开端点
curl http://localhost:8088/api/status                    # 应返回 {"version":"..."}
curl http://localhost:8088/                              # 应返回 index.html

# Admin 端点
curl -H "Authorization: Bearer test123" http://localhost:8088/api/admin/stats
# 应返回统计 JSON

# 三面板浏览器加载（手动）
# - http://localhost:8088/         → 登录/注册页
# - http://localhost:8088/admin.html       → admin 面板
# - http://localhost:8088/user-panel.html  → 用户面板
# 每个面板：F12 console 应无 error；切换语言 zh/en/ja 应正常
```

### L4: 测试套件

```bash
# 单测（如有）
go test ./... -v

# Race 检测（必须！并发 bug 致命）
go test -race ./...

# 覆盖率（可选）
go test -cover ./...
```

## 四、Git 卫生检查

```bash
# 1. 空白 / CRLF / merge marker（J-SOP 必须）
git diff --cached --check
# 预期：exit 0
# 常见问题：
#  - "trailing whitespace"  → 用编辑器 trim trailing
#  - "indent with tabs"     → 风格统一（TS 用空格，Go 用 tab）
#  - "<<<<<<< HEAD"         → 未解决的 merge conflict

# 2. 文件大小卡门（防误提交大 binary）
git diff --cached --stat | awk '{ if ($3+0 > 1000) print }'
# 单文件 >1000 行变更要审视

# 3. 敏感信息扫描（J-SOP 必须）
git diff --cached | rg -i 'password|api[-_]?key|secret|token' | rg -v 'test|example|TODO'
# 命中要逐行确认是否真泄露

# 4. emoji / unicode 异常（J-SOP V27.27 后规则）
git diff --cached | rg '[\x{1F300}-\x{1F9FF}]'
# 业务文案用 emoji 是允许的，代码注释 / 日志不要
```

## 五、Commit Message 规范

J-SOP 用 Conventional Commits + 中英混合：

```
<type>(<scope>): <subject>

<body — 中英任一>

<footer — 可选 issue/sprint 引用>
```

**type**：`feat / fix / docs / refactor / chore / test / perf / style / build`

**scope**：`alibaba / amazon / dianxiaomi / popup / sw / sync / panel / license / sprint / audit / cleanup / ...`

**subject**：≤72 字符，祈使语气，不结句号

```
feat(alibaba): toggle for auto-applying 1688 dropship native filter
fix(panel): debounce save button to prevent double submit
docs(sprint): record V27.46 supplement for sprint24 v2 audit
chore(deps): bump vite from 5.4.0 to 6.0.0
```

## 六、PR / 提交前清单

每次 `git commit` 之前**逐条**确认：

- [ ] **L1 静态**：`npx tsc --noEmit` exit 0
- [ ] **L1 lint**：`npm run lint` 无 error（warning 可接受）
- [ ] **L2 ext build**：`npm run build` 成功
- [ ] **L2 server build**（如改 Go）：`go build ./...` exit 0
- [ ] **go vet**：（如改 Go）exit 0
- [ ] **git check**：`git diff --cached --check` exit 0
- [ ] **secret scan**：`git diff --cached` 无密钥/token
- [ ] **commit msg**：符合 Conventional Commits + scope 准确
- [ ] **SPRINT-PLAN sync**（如有功能性改动）：在 §1.1 加一行
- [ ] **doc sync**（如有用户可见改动）：更新 `docs/_update-log.md` 或 README
- [ ] **chrome reload**（如改扩展）：重新加载扩展跑过烟测
- [ ] **三语 i18n**（如改 HTML/popup 文案）：zh/en/ja 都加

## 七、一键检查脚本（PowerShell）

```powershell
# scripts/precommit-check.ps1
$ext = "j-sop-extension"
$srv = "j-sop-license-server"

Write-Host "=== L1: TypeScript 类型检查 ==="
$tsc = & npx --prefix $ext tsc --noEmit 2>&1
$tscErrors = ($tsc | Select-String "error TS").Count
if ($tscErrors -gt 0) { Write-Host "❌ TS errors: $tscErrors"; exit 1 }
Write-Host "✅ TS 0 errors"

Write-Host "=== L2: Go 编译 ==="
Push-Location $srv
$goOut = go build ./... 2>&1 | Out-String
$goErrors = ([regex]::Matches($goOut, 'error|Error')).Count
Pop-Location
if ($goErrors -gt 0) { Write-Host "❌ Go build errors: $goErrors`n$goOut"; exit 1 }
Write-Host "✅ Go build OK"

Write-Host "=== Git 卫生检查 ==="
git diff --cached --check
if ($LASTEXITCODE -ne 0) { Write-Host "❌ git diff --check 失败"; exit 1 }
Write-Host "✅ Git clean"

Write-Host "🎉 所有检查通过，可以 commit"
```

## 八、常见错误快速诊断

| 现象 | 原因 | 修复 |
|---|---|---|
| `Cannot find module '@shared/...'` | tsconfig.json paths 没配 | 加 `"paths": { "@shared/*": ["src/shared/*"] }` |
| `Type 'X' is not assignable to 'Y'` 但运行时正常 | 类型不严谨 | 不要 `as any`，改类型定义 |
| `npm run build` 卡住 | obfuscator 慢 | 临时 `NODE_ENV=development npm run build` 跳过 |
| Go build `cannot find package` | go.mod 没同步 | `go mod tidy` |
| `error: redefined: HandleX` | 同名 handler 在两个文件 | 重命名其一 |
| `database is locked` | SQLite 并发写 | `db.SetMaxOpenConns(1)` 已在 InitDB |
| `git diff --check` 报 trailing whitespace | 编辑器没 trim | VS Code 设置 `files.trimTrailingWhitespace: true` |
| Chrome "service worker registration failed" | manifest 语法错 | `cat dist/manifest.json | jq` 验证 JSON |

## 九、Don'ts

- ❌ commit 前不运行 tsc → CI 失败再说
- ❌ `--no-verify` 跳过 husky / pre-commit hook
- ❌ 用 `as any` 压制类型错误而不修复根因
- ❌ go vet 警告"unused variable"用 `_` 抹掉而非删除
- ❌ 改了 manifest.json 不重新加载扩展就 commit
- ❌ smoke test 只看 popup，不看三个 content script 站点
- ❌ commit msg 写"fix bug" / "update" 这种无信息量的
- ❌ 单 commit 超过 600 行变更（应该拆分）

## 十、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\package.json`（scripts.lint / type-check / build）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\tsconfig.json`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\biome.json`
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\go.mod`
- `@j:\J-SOP 伴随式自动化助手\.codex\rules\1.md`（J-SOP 项目主指南）
- `@j:\J-SOP 伴随式自动化助手\docs\SPRINT-PLAN.md`（验证记录归档）
