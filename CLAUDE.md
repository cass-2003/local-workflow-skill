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

Update `state/LOG.md`, `state/REQUIREMENTS.md`, `state/MEMORY.md`, and
`state/PROGRESS.md` when repository truth changes.

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
  `git status`.

## Skill Library Policy

Keep this repository generic and open-source friendly. Do not add skills tied
to private projects, local paths, servers, accounts, or one-off command
wrappers. Put project-specific skills in the target project or a private repo.

After a validated single-scope change, prefer an atomic commit. Do not
auto-push, merge, or open a PR unless explicitly requested.
