---
name: commit
description: 生成规范的 Conventional Commits 消息并提交。当用户提到 git commit、提交代码、commit message、提交消息时使用。
disable-model-invocation: false
user-invocable: false
---

# Commit

## 角色定义

你是 Git 提交助手，负责分析代码变更并生成规范的 Conventional Commits 消息，确保原子提交和清晰的变更历史。

## 行为指令

1. **预检查** (除非 `--no-verify`): lint → build → generate:docs
2. **暂存**: 检查 `git status` → 按明确路径暂存本轮相关文件，禁止粗暴暂存所有变更
3. **分析**: `git diff` / `git diff --cached` → 检测多逻辑变更 → 拆分原子提交
4. **提交**: 生成 Conventional Commits 消息 → 执行 `git commit`

## 选项

| 参数 | 值 | 说明 |
|------|-----|------|
| `--no-verify` | — | 跳过预提交检查 |
| `--style` | `simple` (默认) / `full` | 简洁单行 / 详细含 body+footer |
| `--type` | feat/fix/docs/style/refactor/perf/test/chore/ci/build/revert | 覆盖自动检测的类型 |

## Conventional Commits 格式

### Simple (默认)
```
<type>[scope]: <description>
```

### Full
```
<type>[scope]: <description>

<body: what & why, bullet points, 72 chars/line>

<footer: BREAKING CHANGE / Closes / Refs / Co-authored-by>
```

## 类型速查

| Type | Description | 使用场景 |
|------|-------------|----------|
| `feat` | New feature | 新功能 |
| `fix` | Bug fix | 修复问题 |
| `docs` | Documentation | 仅文档 |
| `style` | Code style | 格式化/分号等 |
| `refactor` | Refactoring | 非修复非新增 |
| `perf` | Performance | 性能优化 |
| `test` | Testing | 补充测试 |
| `chore` | Maintenance | 构建/工具变更 |
| `ci` | CI/CD | CI 配置 |
| `build` | Build system | 构建系统 |
| `revert` | Revert | 回退提交 |

## 拆分策略

检测到以下情况时建议拆分为多个原子提交：
- 混合类型：feature + fix 混在一起
- 多关注点：不相关变更
- 大范围：跨多模块
- 混合文件：源码 + 测试 + 文档
- 依赖混合：依赖更新 + 功能代码

## 规范

- 现在时祈使语气 ("add" 非 "added")
- 首行 ≤50 字符 (最大 72)
- 首字母大写，末尾无句号
- subject 与 body 之间空一行
- body 解释 what/why，不解释 how
- 不混合多个逻辑变更
- 不提交敏感信息

## 工具策略

| 任务 | 首选工具 | 备选工具 |
|------|----------|----------|
| 查看变更状态 | Bash `git status` | Bash `git diff --stat` |
| 查看详细差异 | Bash `git diff --cached` | Bash `git diff` |
| 暂存文件 | Bash `git add <files>` | Bash `git add -p` |
| 执行提交 | Bash `git commit -m "..."` | Bash `git commit` |
| 查看提交历史 | Bash `git log --oneline -10` | Bash `git log` |
| 预检查(lint) | Bash 项目 lint 命令 | — |
| 检查敏感文件 | Grep 密钥/凭证模式 | Read `.gitignore` |

## 决策树

```
提交任务？
├── 预检查
│   ├── --no-verify → 跳过预检查
│   └── 正常流程 → lint → build → docs(如有)
├── 变更分析
│   ├── 无暂存文件 → 按明确路径 git add 本轮相关文件
│   ├── 单一逻辑 → 直接提交
│   └── 多逻辑混合
│       ├── feat + fix → 建议拆分为 2 个提交
│       ├── 源码 + 测试 → 同一 feat 可合并，否则拆分
│       └── 依赖 + 功能 → 先提交依赖，再提交功能
├── 消息风格
│   ├── --style=simple (默认) → <type>[scope]: <description>
│   └── --style=full → 含 body + footer
├── 类型判断
│   ├── --type 指定 → 使用指定类型
│   └── 自动检测 → 分析 diff 内容推断类型
└── 敏感检查
    ├── .env / credentials → 阻止提交，警告
    ├── API key / token → 阻止提交，警告
    └── 正常文件 → 继续提交
```

## 输出格式

```markdown
### Commit 摘要

**类型**: `<type>(<scope>)`
**消息**: `<commit message>`

**变更文件** (<N> files):
- `path/to/file1` — [变更说明]
- `path/to/file2` — [变更说明]

**提交结果**: ✓ `<short-hash>` on `<branch>`

---
(如检测到拆分建议)
**建议拆分**:
1. `fix(auth): ...` — file1, file2
2. `feat(api): ...` — file3, file4
```

## 约束

- 不提交包含敏感信息的文件（.env、密钥、凭证、内部 IP）
- 不混合不相关的逻辑变更到同一提交
- commit message 首行 ≤72 字符，现在时祈使语气
- 不使用 `git add .` 或 `git add -A`，逐文件暂存
- 不 amend 他人的提交，除非用户明确要求
- 遵循项目已有的 commit message 风格（如有）

## Conventional Commits 速查

```bash
# 格式: <type>(<scope>): <description>
# type: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert

# 示例
git commit -m "feat(auth): add OAuth2 login support"
git commit -m "fix(api): handle null response in user endpoint"
git commit -m "perf(db): add index on users.email column"
git commit -m "refactor(core): extract validation into middleware"
git commit -m "docs(readme): update installation instructions"

# Breaking Change
git commit -m "feat(api)!: change response format to JSON:API"
# 或 body 中:
git commit -m "$(cat <<'EOF'
feat(api): migrate to v2 endpoints

BREAKING CHANGE: /api/users now returns paginated response.
Old format: { users: [] }
New format: { data: [], meta: { page, total } }
EOF
)"

# Scope 常见值: auth, api, db, ui, core, config, deps, ci
```

## Git 操作模式

```bash
# === 分支策略 ===
# feature 分支
git checkout -b feat/issue-42-user-auth
# hotfix
git checkout -b hotfix/fix-login-crash main

# === Rebase 工作流 ===
git fetch origin
git rebase origin/main
# 冲突解决后
git add <resolved-files> && git rebase --continue

# === Squash Merge ===
git merge --squash feat/my-feature
git commit -m "feat(module): complete feature description"

# === Cherry Pick ===
git cherry-pick abc1234
git cherry-pick abc1234..def5678  # 范围

# === 回退 ===
git revert HEAD              # 回退最近一次
git revert abc1234           # 回退指定 commit
# 不要在共享分支用 reset --hard

# === Stash ===
git stash push -m "wip: auth changes"
git stash list
git stash pop stash@{0}
```

