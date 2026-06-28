# CLAUDE.md

This repository is the source workspace for Portable Agent Workflow: a generic,
Markdown-first workflow framework and curated skill library for multiple coding
agents.

Claude Code should treat this file as a thin project entry. The workflow truth
lives in `framework/core/`; repository state lives in `state/`.

## Default Workflow

For substantial work, follow:

```text
scan -> state restore -> intent -> authority -> route -> execute -> validate -> sync -> deliver -> evolve
```

Read:

- `framework/core/01-workflow.md`
- `framework/core/02-state-systems.md`
- `framework/core/03-routing.md`
- `framework/core/04-authority.md`
- `framework/core/05-validation.md`
- `framework/core/06-evolution.md`
- `framework/core/07-artifact-contracts.md`
- `framework/core/08-autonomous-project-loop.md`

Update `state/LOG.md`, `state/REQUIREMENTS.md`, `state/MEMORY.md`, and
`state/PROGRESS.md` when repository truth changes.

Before substantial work, produce a `State Restore` summary from these files:
state sources, stale/placeholders, latest goal, latest validation, blocker, and
current assumptions. If placeholders or stale entries remain, replace what can
be confirmed from repository facts before editing workflow behavior.

## Artifact Contracts

Do not leave substantial audit, acceptance, implementation, fix, validation, or
docs-sync work only in chat.

- For `audit` / `acceptance` / `验收预检`, create or update a report under
  `docs/audit/` when the target project has that directory, and update
  `docs/audit/INDEX.md`.
- For implementation or fixes, update the relevant state files, especially
  `state/LOG.md` and `state/PROGRESS.md`; update docs when behavior, usage,
  architecture, validation, or risk changes.
- For docs changes, update `docs/INDEX.md` or the relevant directory index so
  new files are discoverable.
- Before commit, confirm validation evidence, state sync, index sync, and
  `git status`; split multiple logical changes into multiple atomic commits.

## Autonomous Project Progress

When the user asks to continue a project, move forward by plan, auto-audit and
fix, or otherwise make real project progress, first check whether the project
has a usable roadmap and next-action plan. If not, create or update those
planning artifacts before implementation. Then follow
`framework/core/08-autonomous-project-loop.md`: select one small goal, confirm
acceptance criteria, implement, validate, self-audit, repair in-scope findings,
sync state/docs, commit when eligible, and either select the next goal or stop
with a clear reason.

Every autonomous loop, audit/fix loop, important implementation, or handoff
must leave a `Loop Record` in `state/PROGRESS.md` or `state/LOG.md`: goal,
acceptance criteria, validation evidence, self-audit, repairs, state/docs sync,
commit, next goal, and stop reason.

## Skill Library Policy

Keep this repository generic and open-source friendly. Do not add skills tied
to private projects, local paths, servers, accounts, or one-off command
wrappers. Put project-specific skills in the target project or a private repo.

In a Git repository, every completed and validated change must enter the
commit closure unless the user explicitly says not to commit. Each commit must
represent one complete work package, including required tests, docs, and state
updates. Split multiple logical changes into multiple atomic commits, stage by
explicit paths, and do not use `git add .` or `git add -A` as a shortcut.
Do not auto-push, merge, or open a PR unless explicitly requested.
