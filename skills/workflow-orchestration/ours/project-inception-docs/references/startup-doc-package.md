# Startup Documentation Package

This reference defines the standard startup documentation package extracted from a real project doc set. Use it when a user asks to turn an idea, screenshot, rough notes, or existing scattered docs into a complete project-start package.

## Directory Layout

```text
.
├─ README.md
├─ .gitignore
├─ AGENTS.md
├─ CLAUDE.md          # optional when Claude Code is used
├─ docs/
│  ├─ INDEX.md
│  ├─ PRD.md
│  ├─ 信息架构-页面原型.md
│  ├─ 信息架构-交互规范.md
│  ├─ api/
│  │  └─ API设计.md
│  ├─ architecture/
│  │  ├─ 技术架构.md
│  │  ├─ 数据模型.md
│  │  ├─ AI工作流.md
│  │  ├─ Prompt模板规范.md
│  │  └─ 技术决策记录.md
│  ├─ planning/
│  │  ├─ 开发路线图.md
│  │  ├─ 工程初始化方案.md
│  │  ├─ 当前工程状态.md
│  │  ├─ 指标埋点.md
│  │  └─ 风险成本.md
│  ├─ testing/
│  │  └─ 测试验收计划.md
│  └─ operations/
│     ├─ 部署运维.md
│     └─ 安全合规.md
├─ references/
│  └─ 参考项目迁移清单.md
└─ state/
   ├─ LOG.md
   ├─ REQUIREMENTS.md
   ├─ MEMORY.md
   └─ PROGRESS.md
```

## Package Tiers

- **Core product package**: `README.md`, `docs/INDEX.md`, `docs/PRD.md`, `docs/信息架构-页面原型.md`, `docs/信息架构-交互规范.md`.
- **Architecture package**: `docs/architecture/技术架构.md`, `数据模型.md`, `AI工作流.md`, `Prompt模板规范.md`, `技术决策记录.md`, plus `docs/api/API设计.md`.
- **Delivery package**: `docs/planning/开发路线图.md`, `工程初始化方案.md`, `当前工程状态.md`, `docs/testing/测试验收计划.md`.
- **Governance package**: `docs/planning/指标埋点.md`, `风险成本.md`, `docs/operations/部署运维.md`, `安全合规.md`, `references/参考项目迁移清单.md`, and `state/*.md`.

## Generation Rules

1. Pass the foundation gate before content expansion: initialize Git when missing, add `.gitignore`, create or update `README.md`, `docs/INDEX.md`, Four-State files, and agent entry files when useful.
2. Create `docs/INDEX.md` first; it is the reading map and must link to every generated doc.
3. Keep `README.md` short and project-facing; keep deep implementation details in `docs/`.
4. Use directory domains instead of a flat pile of files: product at `docs/`, architecture at `docs/architecture/`, API at `docs/api/`, delivery planning at `docs/planning/`, testing at `docs/testing/`, operations at `docs/operations/`.
5. Mark assumptions and unknowns explicitly. Do not turn an idea into false certainty.
6. Every implementation-facing document should include acceptance or validation hooks.
7. Every AI-heavy project should include both `AI工作流.md` and `Prompt模板规范.md`.
8. Every project with non-trivial architecture should include `技术决策记录.md`.
9. Every generated package should be checked for broken links and placeholder residue.

## Foundation Gate

Before writing business-specific docs for a new or uninitialized project, ensure:

- Git is initialized with `git init` unless the directory is already inside a Git worktree.
- `.gitignore` exists and covers dependencies, build output, logs, local environment files, caches, and secrets.
- `AGENTS.md` exists for Codex-oriented projects; add `CLAUDE.md` only when Claude Code is part of the workflow or the user asks for it.
- `state/LOG.md`, `state/REQUIREMENTS.md`, `state/MEMORY.md`, and `state/PROGRESS.md` exist and contain non-empty project facts.
- `README.md` and `docs/INDEX.md` expose quick start, current status, doc map, and validation commands.
- `docs/planning/工程初始化方案.md` records initial commands, repo layout, environment placeholders, and first implementation order.
- `docs/planning/当前工程状态.md` records current Git status, initialized artifacts, verified commands, and remaining gaps.
- The first foundation change is committed atomically after validation when project rules allow auto-commit.

## Document Responsibilities

| Document | Responsibility |
|---|---|
| `README.md` | Project door, current status, quick start, doc links |
| `.gitignore` | Ignore generated, local, secret, dependency, and cache files |
| `AGENTS.md` | Project-local Codex entry, workflow expectations, truth doc pointers |
| `CLAUDE.md` | Optional Claude Code entry with the same workflow and state pointers |
| `docs/INDEX.md` | Reading order, doc map, current decision summary |
| `docs/PRD.md` | Product position, users, MVP, non-goals, flows, requirements, acceptance |
| `docs/信息架构-页面原型.md` | Page map, key objects, screens, state design, page priority |
| `docs/信息架构-交互规范.md` | Layout, components, empty/loading/error states, copy tone |
| `docs/architecture/技术架构.md` | Stack, layers, modules, data flow, state sync, security boundary |
| `docs/architecture/数据模型.md` | Entities, tables, relationships, indexes, retention |
| `docs/api/API设计.md` | API principles, common response, resources, async jobs, polling |
| `docs/architecture/AI工作流.md` | AI stages, components, provider adapter, quality, cost |
| `docs/architecture/Prompt模板规范.md` | Prompt categories, fields, compiler inputs, versioning, review checklist |
| `docs/architecture/技术决策记录.md` | ADR list with decision, rationale, alternatives, impact |
| `docs/planning/开发路线图.md` | Phases, task breakdown, demo standard, milestones |
| `docs/planning/工程初始化方案.md` | Target repo layout, apps/packages, env vars, first commands |
| `docs/planning/当前工程状态.md` | Current code state, running services, verified commands, next step |
| `docs/planning/指标埋点.md` | North-star metric, funnel, events, quality/cost metrics |
| `docs/planning/风险成本.md` | Technical, product, cost, security, compliance risks |
| `docs/testing/测试验收计划.md` | Test types, acceptance cases, quality gates, residual risks |
| `docs/operations/部署运维.md` | Environments, services, config, deploy, logs, backup, rollback |
| `docs/operations/安全合规.md` | Secrets, upload/URL security, permissions, audit, release checklist |
| `references/参考项目迁移清单.md` | What to reuse, rewrite, drop, and verify from references |

## Completion Checklist

- `docs/INDEX.md` links to all generated docs.
- Git repository exists or the reason for not initializing Git is recorded.
- `.gitignore` and agent entry files are present when expected.
- Each doc has a version/date/status line when useful.
- PRD includes MVP, non-goals, acceptance criteria, risks, and metrics.
- Architecture docs identify modules, data flow, async jobs, errors, and security boundaries.
- Delivery docs include runnable first commands and validation expectations.
- Testing docs include at least happy path, failure path, quality gates, and manual acceptance.
- Operations/security docs do not contain real secrets.
- `state/` is initialized or updated if the repository uses Four-State Workflow.
- A first atomic commit is created after validation when auto-commit is permitted.
