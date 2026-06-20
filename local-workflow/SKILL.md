---
name: local-workflow
description: Orchestrate local project workflows by discovering project authority sources, routing tasks to the right local or global skills, enforcing validation and documentation gates, and proposing skill evolution when repeated patterns, stale references, or mirrored-skill drift are detected. Use when the user asks for workflow setup, workflow standardization, cross-skill coordination, or a local process for status, audit, implement, fix, review, doc sync, or git delivery.
---

# Local Workflow

## Role

Use this skill as a local workflow orchestrator.

- Prefer project-local authority over machine-global defaults.
- Route work to existing local skills whenever possible.
- Enforce validation and documentation gates before claiming completion.
- Detect repeated patterns, stale references, and mirrored drift, then propose skill evolution.

Do not use this skill as a replacement for project docs, project-local domain skills, or repository-specific baselines.

## Authority Discovery

Inspect local instruction files first, then inspect project-local rules, workflows, and execution skills.

- Prefer local rule files for hard constraints.
- Prefer local workflow wrappers for command semantics.
- Prefer local skills for execution detail.
- Inspect plugin mirrors only after identifying the local primary source.
- Use machine-global skills only as fallback.
- When local copies disagree, prefer the most local valid source.

For detailed resolution logic, read `references/authority-resolution.md`.

## Routing Rules

Route by user intent, expected output, and scope.

- Use `status` for current state and progress summaries.
- Use `audit` for baseline comparison, gap analysis, and acceptance-oriented inspection.
- Use `implement` for new behavior or multi-file feature work.
- Use `fix` for repairing known issues or closing tracked gaps.
- Use `review` for diff inspection, bug finding, and change-risk evaluation.
- Use `sync-docs` when project memory, plans, or audit outputs must be updated.
- Use Git skills for commit, branch, PR, merge, or delivery actions.
- Use workflow evolution mode when the task is to improve skills, routing, or local process design.

Keep orchestration ownership here, but delegate execution through specialized local skills when they exist.

For routing details and ambiguity handling, read `references/routing-matrix.md`.

## Execution Phases

For substantial work, follow this phase order:

1. workspace scan
2. intent classification
3. authority resolution
4. skill delegation
5. task execution
6. validation gate
7. documentation and state sync
8. Git and delivery gate
9. skill evolution

Trivial one-step work may skip unnecessary phases, but do not skip authority checks or validation reasoning when the task meaningfully changes code, docs, or workflow truth.

For detailed phase behavior, read `references/execution-phases.md`.

## Validation And Delivery Gates

Do not claim completion without evidence.

- Match validation scope to change scope.
- Prefer project-local validation skills and repo-native verification commands.
- If validation is skipped, say so explicitly.
- After meaningful changes, check whether docs, plans, or project state records must be synchronized.
- Before Git delivery actions, inspect the actual diff and ensure required gates have run.

For detailed validation rules, read `references/validation-gates.md`.
For Git and handoff rules, read `references/git-and-handoff.md`.

## Skill Evolution

Capture repeated workflow patterns without rewriting skills impulsively.

- Record observations when stale paths, drift, or repeated manual decisions appear.
- Default to `suggest`, not `apply`.
- Only apply skill updates with explicit approval.
- Update the true primary source before touching mirrors.
- Prefer moving bulky or variant-specific logic into references instead of growing the main skill body.

For lifecycle rules and suggestion thresholds, read `references/skill-evolution.md`.

## Reference Loading Guide

- Read `references/authority-resolution.md` when multiple local rule or skill families exist, or when references appear stale.
- Read `references/routing-matrix.md` when intent is ambiguous or several routes seem plausible.
- Read `references/execution-phases.md` for substantial, multi-step, or cross-skill work.
- Read `references/validation-gates.md` before claiming completion on any meaningful change.
- Read `references/git-and-handoff.md` before commit, PR, merge, push, or delivery actions.
- Read `references/skill-evolution.md` when repeated patterns, stale references, or mirrored drift appear.
