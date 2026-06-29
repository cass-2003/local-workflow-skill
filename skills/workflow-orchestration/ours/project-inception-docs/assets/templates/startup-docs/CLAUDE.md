# CLAUDE.md

<!-- BEGIN PORTABLE AGENT WORKFLOW -->

## Project Workflow

- Start substantial work with: scan -> state restore -> intent -> authority -> route -> execute -> validate -> sync -> deliver -> evolve.
- Before business development, ensure the project foundation is ready: Git, `.gitignore`, README, docs index, Four-State files, validation commands, and this agent entry.
- If this directory has no `.git/` and is not inside another Git worktree, initialize Git before continuing.
- When the user says "初始化项目" in an empty or unclear project, first classify the project state and run a discovery interview before generating full docs or code.
- For existing projects that are only missing workflow files, scan and restore project state first; do not restart product discovery from scratch.
- Prefer project-local truth docs over global memory.
- After completed and validated changes in a Git repository, create atomic commit(s) by default; split multiple logical changes and do not push unless explicitly requested.

## Autonomous Progress

- When asked to continue the project, move forward by plan, auto-audit/fix, or make real project progress, first check `docs/planning/开发路线图.md`, `docs/planning/下一步工作包.md`, and `state/PROGRESS.md`.
- If the roadmap or next work packages are missing or stale, update planning before implementation.
- Each loop should select one small goal, confirm acceptance criteria, implement or fix, validate, self-audit, repair in-scope findings, sync docs/state, and enter commit closure when eligible.
- Stop only for user decisions, external credentials, high-risk operations, missing validation environment, repeated failure, or budget/scope limits; write the stop reason and next smallest executable goal.

## State System

- Log: `state/LOG.md`
- Requirements: `state/REQUIREMENTS.md`
- Memory: `state/MEMORY.md`
- Progress: `state/PROGRESS.md`

## State Restore Contract

- At the start of substantial work, read `state/PROGRESS.md`, then `state/LOG.md`, then `state/MEMORY.md`, then `state/REQUIREMENTS.md`; if any are missing, create or map an equivalent before coding.
- Also read `docs/INDEX.md` to find the project truth docs, and `docs/audit/INDEX.md` when audit reports exist.
- Do not treat placeholder text such as `<任务>` or `<项目由哪些部分组成>` as valid state. Replace placeholders with current project facts as soon as the project has real information.
- Prefer the newest project-local state and docs over chat memory or global rules.
- Before coding, audit, fixing, or committing, produce a `State Restore` summary with: state sources, stale/placeholders, latest goal, latest validation, blocker, and assumptions for this loop.
- If state files still contain placeholders like `<任务>`, `待补充`, or `TBD`, replace what can be confirmed from repository facts; record the rest as explicit open questions.

## State Write Contract

- After every implementation, fix, validation, audit, docs-sync, deploy, or project-planning loop, append a dated entry to `state/LOG.md`.
- When current focus, active goal, next action, blocker, validation result, or stop reason changes, update `state/PROGRESS.md`.
- When a durable decision, architecture fact, operational gotcha, external dependency, command, credential boundary, or recovery note is learned, update `state/MEMORY.md`.
- When scope, acceptance criteria, P0/P1 priority, compliance boundary, or done/open status changes, update `state/REQUIREMENTS.md`.
- After every autonomous loop, audit/fix loop, important implementation, or handoff, write a `Loop Record` to `state/PROGRESS.md` or `state/LOG.md`: goal, acceptance criteria, validation evidence, self-audit, repairs, state/docs sync, commit, next goal, and stop reason.
- Before commit, verify state sync happened or explicitly record why no state file needed a change.

## Documentation Entry

- Project overview: `README.md`
- Documentation map: `docs/INDEX.md`
- Initialization plan: `docs/planning/工程初始化方案.md`
- Current status: `docs/planning/当前工程状态.md`
- Roadmap: `docs/planning/开发路线图.md`
- Next actions: `docs/planning/下一步工作包.md`

## Discovery Interview

- Empty directory or new idea: ask what the project should do, who it serves, target platform, MVP, roles, data, permissions, risks, and validation plan before writing full docs.
- Existing project: scan code/docs/Git first, then ask only gap questions.
- Each interview round should summarize `confirmed / open questions / risks / next questions`.
- Do not treat assumptions as requirements; write unknowns as `待确认`.

## Artifact Contracts

- Do not leave substantial audit, acceptance, implementation, fix, validation, or docs-sync work only in chat.
- For `审计` / `audit` / `验收预检`, create or update a report in `docs/audit/` and update `docs/audit/INDEX.md`.
- Audit reports must include: 审计范围与基线, TL;DR, 应有能力清单, 缺失项清单, 偏差与误判修正, 下一步计划, 待确认事项, 验证证据.
- For implementation or fixes, update `state/LOG.md` and `state/PROGRESS.md`; update docs when behavior, usage, architecture, validation, or risk changes.
- For docs changes, update `docs/INDEX.md` and the relevant directory index so new files are discoverable.
- Before commit, confirm validation evidence, state sync, index sync, and `git status`; then create atomic commit(s), one complete work package per commit. Stage by explicit paths, not `git add .` or `git add -A`.

<!-- END PORTABLE AGENT WORKFLOW -->
