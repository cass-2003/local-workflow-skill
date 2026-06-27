# CLAUDE.md

## Project Workflow

- Start substantial work with: scan -> state restore -> intent -> authority -> route -> execute -> validate -> sync -> deliver -> evolve.
- Before business development, ensure the project foundation is ready: Git, `.gitignore`, README, docs index, Four-State files, validation commands, and this agent entry.
- If this directory has no `.git/` and is not inside another Git worktree, initialize Git before continuing.
- Prefer project-local truth docs over global memory.
- After a validated single-scope change, create an atomic commit by default; do not push unless explicitly requested.

## Autonomous Progress

- When asked to continue the project, move forward by plan, auto-audit/fix, or make real project progress, first check `docs/planning/开发路线图.md`, `docs/planning/下一步工作包.md`, and `state/PROGRESS.md`.
- If the roadmap or next work packages are missing or stale, update planning before implementation.
- Each loop should select one small goal, confirm acceptance criteria, implement or fix, validate, self-audit, repair in-scope findings, sync docs/state, and commit when eligible.
- Stop only for user decisions, external credentials, high-risk operations, missing validation environment, repeated failure, or budget/scope limits; write the stop reason and next smallest executable goal.

## State System

- Log: `state/LOG.md`
- Requirements: `state/REQUIREMENTS.md`
- Memory: `state/MEMORY.md`
- Progress: `state/PROGRESS.md`

## Documentation Entry

- Project overview: `README.md`
- Documentation map: `docs/INDEX.md`
- Initialization plan: `docs/planning/工程初始化方案.md`
- Current status: `docs/planning/当前工程状态.md`
- Roadmap: `docs/planning/开发路线图.md`
- Next actions: `docs/planning/下一步工作包.md`

## Artifact Contracts

- Do not leave substantial audit, acceptance, implementation, fix, validation, or docs-sync work only in chat.
- For `审计` / `audit` / `验收预检`, create or update a report in `docs/audit/` and update `docs/audit/INDEX.md`.
- Audit reports must include: 审计范围与基线, TL;DR, 应有能力清单, 缺失项清单, 偏差与误判修正, 下一步计划, 待确认事项, 验证证据.
- For implementation or fixes, update `state/LOG.md` and `state/PROGRESS.md`; update docs when behavior, usage, architecture, validation, or risk changes.
- For docs changes, update `docs/INDEX.md` and the relevant directory index so new files are discoverable.
- Before commit, confirm validation evidence, state sync, index sync, and `git status`; then create an atomic commit for a single-scope change.
