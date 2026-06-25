# Validation Gates

## Validation Principle

Do not claim completion without evidence.

Validation scope must match change scope.

That means:

- a file read is not proof of runtime correctness
- a typecheck is not proof of user-visible behavior
- a docs edit is not proof that code matches docs
- a narrow check cannot justify a broad completion claim

## Validation Levels

| Level | Change type | Expected validation |
|---|---|---|
| V0 | analysis only | source inspection and consistency check |
| V1 | docs-only | path/reference verification and doc cross-check |
| V2 | local code edit in one module | focused typecheck/build/test for touched area |
| V3 | cross-module behavior change | multi-module validation and contract check |
| V4 | deployment-facing or high-risk change | stronger verification and smoke/regression checks |

## Validation Selection

Before choosing a validation level, inspect:

- changed files
- affected modules
- existence of project-local validation skills
- available repo scripts
- whether the task is code, docs, rules, workflow, or mixed

Use this selection order:

1. project-local validation skill, if present
2. project-local documented commands
3. obvious repo-native scripts
4. global generic minimal verification

## Recording Requirements

Always record:

- what was validated
- which command or evidence was used
- what was intentionally not validated
- why a broader gate was or was not required

If validation was skipped, state that explicitly.

## Workflow-Skill Validation

When the work is primarily workflow or skill design:

- validate internal consistency
- validate path existence
- validate that referenced authority layers really exist
- validate that no new duplicate truth source is introduced

This is the correct gate for workflow design work, where structural drift is the main risk.

## Completion Claim Rules

Before claiming completion:

- confirm that evidence covers the real scope of the change
- confirm that local project authority has been respected
- confirm that required docs or state sync has been considered
- confirm that any skipped checks are disclosed

Completion should remain provisional if evidence is weak, indirect, or narrower than the requested outcome.
