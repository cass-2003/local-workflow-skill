# 能力库 · Skill Library

框架执行阶段（工作流 Phase 4/5）委托的具体技能。由 `../framework/core/03-routing.md` 的二级路由按问题域选用。

> 这一层是框架的"双手"。大脑（何时恢复状态、如何路由、何时验证交付）在 `../framework/`。

## 类别索引

### `workflow-core/` — 工作流编排
- **local-workflow** — J-SOP 来源样本（参考母本，非适配器）
- **project-workflow** — 去项目化的 Claude Code 实例（待登记为 `adapters/` 的 CC 适配器）

### `engineering-core/` — 通用工程模式（18）
api-versioning · concurrency-patterns · dependency-injection · environment-config · error-handling-patterns · feature-flags · graceful-shutdown · http-caching · idempotency-design · memory-leaks · migration-zero-downtime · monorepo · pagination · rate-limiting-algorithms · regex-patterns · string-encoding · structured-logging · typescript-advanced

### `backend-infra/` — 后端与基础设施
background-jobs · dockerfile-best · echo-go-server · websocket-impl

### `frontend-extension/` — 前端 / 插件 / 抓取
anti-detection · chrome-mv3-ext · css-modern-2025 · dom-scraping · i18n-trio · panel-ui · preact-popup

### `data-sync-validation/` — 同步 / 校验 / 数据约束
sync-bidirectional · validation-pipeline · validation-schema

### `language-runtime/` — 语言运行时通用能力
datetime-timezones

### `source-commands/` — 项目命令封装
audit · fix · implement · review · sprint · status · sync-docs

## 通用度标记（待办，框架路线图阶段 6）

每个 skill 后续会标注：

- **通用**：纯工程模式，跨项目可直接复用（多数 `engineering-core/*`、`language-runtime/*`）。
- **半通用**：去项目化后可通用（部分 `frontend-extension/*`、`data-sync-validation/*`）。
- **项目定制**：强绑 J-SOP，保留作场景样本（`source-commands/*`、`echo-go-server`、`i18n-trio`、`panel-ui`、`dom-scraping`）。

标记完成前，以各 `SKILL.md` 的 `description` 为准。
