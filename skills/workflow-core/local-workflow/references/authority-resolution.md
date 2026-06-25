# Authority Resolution

## Objective

Resolve which local layers are authoritative for the current repository so the workflow orchestrator can route and execute work without creating another conflicting rules layer.

Before routing work, answer:

1. where the active hard rules live
2. where command entry points live
3. where execution-detail skills live
4. which copies are mirrored, stale, migrated, or conflicting

## Candidate Source Families

Inspect these families in order of local relevance:

1. repository instruction files
   - `AGENTS.md`
   - `CLAUDE.md`
   - root `README*`
2. project-local rules
   - `.codex/rules/*`
   - equivalent local rule folders if present
3. project-local workflows
   - `.codex/workflows/*`
   - equivalent workflow-wrapper folders if present
4. project-local execution skills
   - `.codex/skills/*`
   - `.agents/skills/*`
   - equivalent local skill folders if present
5. plugin mirrors
   - `.agents/plugins/*`
6. project truth docs
   - `docs/*`
   - current status, sprint, audit, runbook, or baseline docs
7. machine-global fallback skills
   - global `~/.codex/skills`

## Resolution Procedure

Use this procedure in order:

1. identify repository instruction files
2. identify project-local rules
3. identify project-local workflow wrappers
4. identify project-local execution skills
5. identify plugin mirrors
6. identify current truth docs
7. identify machine-global fallback skills only if needed

Do not start from global fallbacks and work inward.

## Role-Based Resolution

Resolve authority by role, not by a single universal winner:

| Role | Preferred source |
|---|---|
| host instructions | local instruction files |
| hard constraints | project-local rules |
| command semantics | project-local workflow wrappers |
| execution detail | project-local skills |
| business truth | current docs plus current codebase |
| generic fallback | machine-global skills |

## Scoring Heuristic

If multiple candidates compete for the same role, prefer the candidate that scores highest on:

1. locality
   - repo-local beats machine-global
2. path validity
   - valid references beat missing-path references
3. freshness
   - current folder names and current doc names beat obsolete ones
4. specificity
   - local domain guidance beats generic fallback wording
5. consistency
   - sources aligned with adjacent local layers beat isolated outliers

## Drift Detection

Mark a source as drifted when one or more are true:

- it references a path family that no longer exists
- it assumes obsolete document names
- it conflicts with a more local and valid source
- it is a mirror copy whose content materially diverged from the local primary source
- it describes commands that no longer match the actual repo layout

## Migration Compatibility

If a source points at an obsolete family but a valid replacement family exists locally:

1. mark the old source as migrated-but-stale
2. map the old family to the valid replacement family
3. continue using the valid local family for execution
4. emit a skill-evolution suggestion to repair the stale reference

Do not fail hard just because a stale mirror still exists, unless no valid local fallback can be found.

## Tie-Break Rules

If two local candidates still conflict after scoring:

1. prefer rules over wrappers for constraints
2. prefer wrappers over skills for command semantics
3. prefer skills over plugin mirrors for execution detail
4. prefer current docs and current code over historical summaries for project truth

## Resolution Output Template

Produce a compact internal resolution record:

```md
## Authority Resolution

- Rules source:
- Workflow source:
- Execution skills source:
- Truth docs source:
- Global fallback source:
- Drift detected:
- Notes:
```

This record should be established before major routing or completion claims.

## Minimal Working Example

```md
## Authority Resolution

- Rules source: `.codex/rules/*`
- Workflow source: `.codex/workflows/*`
- Execution skills source: `.codex/skills/*`
- Truth docs source: `docs/*`
- Global fallback source: `~/.codex/skills`
- Drift detected: plugin mirror differs from project-local skill
- Notes: use local primary source and emit evolution suggestion for mirror drift
```
