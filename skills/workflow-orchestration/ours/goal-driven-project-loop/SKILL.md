---
name: goal-driven-project-loop
description: "目标驱动项目推进循环。用于多 agent 通用的持续推进工作流：State Restore、选择一个详细小目标、读取相关文件、实现或修复、验证、自审、修复发现、同步 docs/state/Loop Record、原子 commit，并继续选择下一个目标。当用户说继续推进、自己往下做、按计划开发、自动审计修复、推进到可用版本、不要做完一步就停、goal-driven loop、项目循环推进时使用。"
---

# Goal-Driven Project Loop

Use this skill when the user authorizes continued project progress rather than a single isolated answer. It is a thin execution wrapper over `framework/core/08-autonomous-project-loop.md`; do not fork the core rules.

## Core Loop

Run one small, complete, verifiable goal at a time:

```text
State Restore
-> choose one detailed small goal
-> read relevant files
-> implement or fix
-> validate
-> self-audit
-> repair in-scope findings
-> revalidate if repaired
-> sync docs/state/Loop Record
-> atomic commit
-> choose next goal or stop with reason
```

## Start Gate

Before editing:

1. Scan local authority: project `AGENTS.md` / `CLAUDE.md`, README, docs, state, rules, local skills, validation commands, and Git status.
2. Restore state from the four state systems or project equivalents: log, requirements, memory, progress.
3. If state is missing or placeholder-only, create or update the minimum truthful state before implementation.
4. If there is no roadmap or next work package, create or update planning artifacts first.
5. Pick exactly one goal for the current loop.

## Goal Contract

Write the active goal in recoverable form before doing substantial work:

```md
## Active Goal

- Goal:
- Why now:
- Acceptance Criteria:
- Scope Boundary:
- Validation Plan:
- Expected Files:
- Stop Conditions:
```

A valid goal must be small enough for one atomic commit. Split goals that combine unrelated features, refactors, docs, dependencies, or migrations.

## Execution Rules

- Read before changing: inspect the files, symbols, docs, and state records that define the target behavior.
- Delegate domain work to the relevant skill while keeping loop orchestration here.
- Prefer minimal, reversible changes that satisfy the active goal.
- Treat validation as part of the goal, not an optional afterthought.
- Run self-audit after implementation and before state sync.
- Repair Critical / High / P0 / P1 findings that are in scope; record out-of-scope findings as next candidate goals.
- Do not continue blindly when a decision, credential, destructive operation, production risk, or repeated validation failure requires stopping.

## State And Artifact Sync

Do not leave important progress only in chat. At loop end, sync the project’s equivalent artifacts:

- `state/LOG.md`: what changed, validation evidence, commit status.
- `state/PROGRESS.md`: active goal status, self-audit, next candidate goal, stop reason.
- `state/MEMORY.md`: durable architecture or workflow facts discovered during the loop.
- `state/REQUIREMENTS.md`: acceptance criteria or done/open status changes.
- `docs/audit/` and index files when the loop includes audit, acceptance preflight, or significant self-audit.

Use the project’s existing truth docs if it has different file names. Do not create duplicate truth sources when equivalents already exist.

## Commit Closure

If the project is a Git repository and the loop produced verified changes, create an atomic commit unless the user or project rules explicitly forbid it.

Before commit:

- Confirm validation evidence.
- Confirm docs/state sync.
- Inspect `git status` and the staged diff.
- Stage only relevant files; do not use blanket staging when unrelated changes exist.
- Exclude secrets, local-only credentials, generated noise, and other agents’ unrelated work.

Push, merge, PR, force operations, and destructive history changes still require explicit user instruction.

## Loop Record

Write or update a loop record before declaring the loop complete:

```md
## Loop Record · <YYYY-MM-DD> · <scope>

- Goal:
- Acceptance Criteria:
- Validation Evidence:
- Self-Audit:
- Repairs:
- State/Docs Sync:
- Commit:
- Next Goal:
- Stop Reason:
```

`Stop Reason` must say why the agent should stop or what the next smallest safe goal is. Do not write vague endings like “done” or “waiting” when a concrete next action exists.

## Relationship To Project Workflow

Use `project-workflow` for broad routing, authority resolution, and cross-skill orchestration. Use this skill as the concrete autonomous progress loop when the route is `autonomous-loop` or the user says “继续推进”.

If local project rules conflict with this skill, project-local rules win. If framework core changes, follow `framework/core/08-autonomous-project-loop.md` as the single source of truth.
