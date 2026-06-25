---
name: monorepo
description: "Monorepo 工程实战。覆盖 pnpm workspaces / npm workspaces / Yarn / Turborepo / Nx / Rush / Bazel 选型、internal package 引用、共享 tsconfig 与 ESLint、跨包 type 推导、增量构建与缓存、affected detection、版本协调（Changesets / 独立 vs lock-step）、CI 任务依赖图、release 自动化、Git submodule vs subtree vs monorepo 心智、超大仓库性能（partial clone / sparse checkout）。当用户提到 monorepo、单仓多包、pnpm workspaces、Turborepo、Nx、Rush、Bazel、Changesets、affected、internal package、workspace protocol、sparse checkout 时使用。"
---

# Monorepo Skill — 单仓多包工程

## 何时使用

- 多个相关项目（前端 + 后端 + 共享库 + CLI）想统一管理
- Polyrepo 已有但跨仓改动协调成本高
- 想做 atomic commit 跨包改动
- 评估 Turborepo / Nx / Bazel 选型
- 优化 CI 时间（只跑受影响的包）

## 一、何时该用 Monorepo / 何时不该

### 适合

- ✅ 共享 type 定义 / SDK / config
- ✅ 跨包重构频繁（API + Frontend 一起改）
- ✅ 团队规模 ≤ 100 人（再大需要更复杂工具如 Bazel）
- ✅ 想单一 source of truth + atomic commit

### 不适合

- ❌ 完全独立的产品线（共享 < 10%）
- ❌ 不同语言混合且无统一构建（Bazel 例外）
- ❌ 需要不同访问权限（开源 vs 内部代码混合 → 用 polyrepo）
- ❌ 团队没有专人维护构建系统

## 二、JS / TS 生态选型

| 工具 | 角色 | 适合 |
|---|---|---|
| **pnpm workspaces** | 包管理器 | 任何规模，性能最好（硬链接 + 严格依赖） |
| **npm/yarn workspaces** | 包管理器 | 简单场景 |
| **Turborepo** | 任务编排 + 缓存 | 中型 / Vercel 系 / 配置简单 |
| **Nx** | 任务编排 + generator + plugin | 大型 / 需要代码生成 / Angular 友好 |
| **Rush** (Microsoft) | 大型 monorepo 治理 | 超大型 |
| **Bazel** (Google) | 多语言通用构建 | 跨语言 / 极大型 / 接受陡峭学习 |
| **Lerna** | 老牌（已被 Nx 收购） | 维护中，不推荐新项目 |

**推荐组合**（中型 TS 项目）：**pnpm workspaces + Turborepo + Changesets**。

## 三、pnpm workspace 标准布局

```
my-monorepo/
├── package.json                  # 根：私有，仅放工具依赖
├── pnpm-workspace.yaml
├── tsconfig.base.json            # 共享 TS 基础配置
├── turbo.json
├── .changeset/
│   └── config.json
├── apps/
│   ├── web/                      # Next.js 前端
│   ├── api/                      # Node.js 后端
│   └── docs/                     # 文档站
├── packages/
│   ├── ui/                       # 共享组件
│   ├── eslint-config/
│   ├── tsconfig/                 # 共享 tsconfig presets
│   ├── types/                    # 共享 type 定义
│   └── utils/
└── tools/
    └── scripts/                  # 私有脚本
```

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tools/*"
```

```json
// 根 package.json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "build": "turbo build",
    "dev":   "turbo dev",
    "lint":  "turbo lint",
    "test":  "turbo test",
    "changeset": "changeset",
    "release": "changeset version && pnpm install && changeset publish"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "@changesets/cli": "^2.27.0",
    "typescript": "^5.5.0"
  }
}
```

## 四、Internal Package 引用

```json
// apps/web/package.json
{
  "dependencies": {
    "@myco/ui": "workspace:*",        // 永远用工作区版本
    "@myco/types": "workspace:^",     // 锁 caret
    "@myco/utils": "workspace:1.0.0"  // 严格匹配
  }
}
```

**workspace protocol**：
- `workspace:*` — 任意工作区版本
- `workspace:^` — 兼容当前版本
- `workspace:~` — 同 minor
- 发布时 pnpm publish 自动替换为真实版本号

## 五、共享 tsconfig

```json
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "skipLibCheck": true,
    "esModuleInterop": true
  }
}
```

```json
// apps/web/tsconfig.json
{
  "extends": "@myco/tsconfig/base.json",
  "compilerOptions": {
    "jsx": "preserve",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*"]
}
```

**Project References**（大型项目）：

```json
// 根 tsconfig.json
{
  "files": [],
  "references": [
    { "path": "packages/types" },
    { "path": "packages/ui" },
    { "path": "apps/web" }
  ]
}
```

`tsc --build` 增量编译，依赖图自动并行。

## 六、Turborepo 任务编排

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],         // 先建依赖包
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "inputs": ["src/**", "package.json", "tsconfig.json"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

**核心机制**：
- **本地缓存**：基于 inputs hash，未变即复用 → `turbo build` 第二次秒级
- **远程缓存**（Vercel / 自建）：CI 间共享缓存 → 第一个跑过的同事提交后，CI 命中
- **依赖图**：`^build` = "先建该包的依赖"

```bash
turbo build --filter=web              # 只建 web 及其依赖
turbo build --filter=...^web          # 建 web 的所有依赖
turbo build --filter=[HEAD^1]         # 仅受 commit 影响的包
turbo run lint --since=main           # 自上次 main 起改过的
```

## 七、Affected Detection（CI 优化）

不要在 CI 上跑全量 — 跑受影响的：

```yaml
# .github/workflows/ci.yml
- name: Test affected
  run: pnpm turbo test --filter=...[origin/main]
```

Turborepo 的 `--filter` + git diff 自动计算依赖图。Nx 的 `nx affected:test --base=main` 同理。

效果：改一个 README 不跑测试；改 packages/ui 跑所有依赖 ui 的 app 的测试。

## 八、版本协调（Changesets）

```bash
# 开发者改完代码
pnpm changeset
# 交互式：选改了哪些包 + major/minor/patch + 写 changelog
```

生成 `.changeset/abc.md`：

```markdown
---
"@myco/ui": minor
"@myco/utils": patch
---

ui: 加 DatePicker；utils: 修 formatCurrency 千分位
```

发布时：

```bash
pnpm changeset version    # 把 .changeset/*.md 合并成 CHANGELOG + bump 版本
pnpm install              # lockfile 同步
pnpm changeset publish    # 推 npm
```

**两种发布策略**：
- **Independent**（推荐）：每个包独立 semver，按需 bump
- **Fixed (lock-step)**：所有包同版本号（React 风格）

## 九、Nx 替代 Turborepo

```json
// nx.json
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": { "cacheableOperations": ["build", "test", "lint"] }
    }
  },
  "targetDefaults": {
    "build": { "dependsOn": ["^build"] }
  }
}
```

**Nx 优势**：
- Generator：`nx generate @nx/react:app web` 一键脚手架
- Plugin 生态（React / Next / NestJS / Express / Cypress）
- Module Boundaries（包间引用规则约束）
- Nx Cloud 远程缓存

**Turborepo 优势**：
- 配置极简
- 与 Vercel / Next 深度集成

## 十、Bazel（超大型 / 多语言）

适用：Google 规模 / 跨 Java + Go + TS + Python。

```python
# BUILD.bazel
load("@npm//:defs.bzl", "npm_link_all_packages")
ts_library(
    name = "ui",
    srcs = glob(["src/**/*.ts"]),
    deps = [":types"],
)
```

**优势**：跨语言 / 极致增量 / 远程执行
**代价**：学习曲线陡 / TS 生态对接 (rules_js) 还在演进 / 工具链投资大

通常只有内部基础设施成熟的大公司才上 Bazel。

## 十一、超大仓库性能

```bash
# Partial clone（不下载历史 blob）
git clone --filter=blob:none https://...

# Sparse checkout（只 checkout 部分目录）
git clone --filter=blob:none --no-checkout ...
git sparse-checkout init --cone
git sparse-checkout set apps/web packages/ui

# Git LFS（大文件）
git lfs track "*.psd"
```

工具：
- **scalar** (Microsoft / Git 内置) — 超大仓自动优化
- **VFS for Git** — 虚拟文件系统按需下载

## 十二、Don'ts

- ❌ 把所有 package 强 lock-step 同版本（除非 React 那种心智）— 浪费版本号
- ❌ 在根 package.json 装应用依赖 — 应在各 app 自己 package.json
- ❌ 不用 workspace protocol，写死版本号 — 内部包升级要手改一堆
- ❌ 跨包用相对路径 import：`'../../../packages/ui/src/Button'` — 用 package name `@myco/ui`
- ❌ 用 `npm install` 在子包目录（破坏 workspace）— 始终从根用 pnpm
- ❌ 不配 turbo / nx 缓存，每次 CI 全跑 — 浪费分钟数
- ❌ 跨包循环依赖 — 拆出共享底层包
- ❌ apps 互相 import — apps 是顶层消费者，不该被 import
- ❌ 不用 changeset 手改版本号 + changelog — 漏 / 不一致
- ❌ git 历史压扁（squash all PRs）但 monorepo — `git log` 在大文件上慢；保留合理粒度

## 十三、模块边界规则

```json
// .eslintrc 用 @nx/enforce-module-boundaries 或自家 plugin
{
  "rules": {
    "@nx/enforce-module-boundaries": ["error", {
      "depConstraints": [
        { "sourceTag": "type:app", "onlyDependOnLibsWithTags": ["type:lib", "type:ui"] },
        { "sourceTag": "type:lib", "onlyDependOnLibsWithTags": ["type:lib"] }
      ]
    }]
  }
}
```

防止：
- app 之间互相 import
- domain 内部包被外部 domain 直接 import（应通过 public API）

## 十四、CI 模板（GitHub Actions）

```yaml
name: CI
on: [pull_request, push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0       # affected detection 需要历史
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo lint test build --filter=...[origin/main]
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}      # 远程缓存
          TURBO_TEAM:  ${{ vars.TURBO_TEAM }}
```

## 十五、参考资料

- pnpm workspaces：https://pnpm.io/workspaces
- Turborepo handbook：https://turbo.build/repo/docs/handbook
- Nx documentation：https://nx.dev/getting-started/intro
- Changesets：https://github.com/changesets/changesets
- Monorepo.tools 比较矩阵：https://monorepo.tools/
- Google "Why Google Stores Billions of Lines of Code in a Single Repository"（2016 CACM）
- Microsoft Scalar / VFS for Git：https://github.com/microsoft/scalar
- "Trunk Based Development" + monorepo 心智：https://trunkbaseddevelopment.com/
