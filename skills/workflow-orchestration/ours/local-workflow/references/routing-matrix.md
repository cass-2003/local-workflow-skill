# Routing Matrix

## Purpose

Turn ambiguous workflow requests into stable routes so the orchestrator can pick the right local or global skill without relying on fragile keyword matching alone.

Route by:

- user intent
- expected output
- change scope
- whether the task is inspection, implementation, repair, synchronization, or delivery

## Primary Intents

| Intent | Typical wording | Primary route | Secondary route |
|---|---|---|---|
| status | status, progress, where are we, current state | `status` | docs truth sources |
| audit | audit, gap analysis, baseline check, acceptance check | `audit` | `review` for narrow diff-only inspection |
| implement | build, implement, add feature, develop | `implement` | `validation` after execution |
| fix | fix, repair, close issues, batch fix | `fix` | `review` if inspection is actually the main task |
| review | review, inspect diff, check changes, code review | `review` | `validation` for stronger evidence |
| docs sync | update docs, sync docs, archive, update plan | `sync-docs` | status/audit outputs as inputs |
| git delivery | commit, branch, PR, merge, push | `git-workflow` / `commit` | local validation first |
| workflow evolution | improve skill, update workflow, standardize process | `local-workflow` evolution flow | project-local skill update path |

## Disambiguation Rules

Use these rules to avoid common misroutes:

- "review current diff" is not `audit`
- "find bugs in recent changes" is `review`, not `fix`
- "close audit findings" is `fix`, not `audit`
- "build feature from spec" is `implement`, not `review`
- "update plan/docs after work" is `sync-docs`, not `status`
- "show current truth" is usually `status`, not code review
- "why is this process stale or drifting" is workflow evolution first, not implementation

## Scope Overrides

Scope can override keyword-based routing:

- repo-wide baseline comparison -> `audit`
- single diff inspection -> `review`
- non-code state summary -> `status`
- code plus docs plus verification -> `implement` or `fix`
- delivery packaging only -> Git flow

## Domain Escalation

If a specialized local domain skill exists, keep orchestration ownership here but delegate execution through that domain skill.

Examples:

- server/backend changes -> local server skill
- browser extension changes -> local extension skill
- validation-heavy change -> local validation skill
- workflow-only change -> local-workflow references plus docs sync path

## Fallback Rules

If no matching local skill exists:

1. keep the route category
2. use the closest machine-global generic skill
3. preserve local authority and validation rules
4. do not let the fallback override project-local constraints

## Practical Routing Procedure

Use this quick procedure:

1. identify whether the task is inspection, implementation, repair, synchronization, delivery, or workflow design
2. estimate scope: single diff, single module, cross-module, repo-wide, or workflow-only
3. select the primary route
4. decide whether a secondary route is needed for validation or docs sync
5. decide whether domain escalation is needed

## Routing Output Template

Produce a short internal routing record:

```md
## Routing Decision

- User intent:
- Primary route:
- Secondary route:
- Scope:
- Domain escalation:
- Fallback used:
- Notes:
```

This makes orchestration decisions reviewable instead of implicit.

## Minimal Working Examples

```md
## Routing Decision

- User intent: review current diff
- Primary route: `review`
- Secondary route: `validation`
- Scope: single diff
- Domain escalation: none
- Fallback used: none
- Notes: inspection task, not baseline audit
```

```md
## Routing Decision

- User intent: improve local workflow and fix drift
- Primary route: `local-workflow`
- Secondary route: `sync-docs`
- Scope: workflow-only
- Domain escalation: none
- Fallback used: none
- Notes: evolution-first task
```
