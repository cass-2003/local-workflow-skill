# Skill Evolution

## Why Evolution Is Needed

Workflow systems drift over time.

Typical causes:

- stale path references
- mirrored copies diverging
- repeated manual explanations not yet captured
- validation rules changing while old instructions remain
- workflow wrappers lagging behind the current repo structure

This reference defines how to improve skills without turning the skill system into another source of chaos.

## Lifecycle States

Use this lifecycle:

1. `observe`
   - capture a signal
   - no file edits
2. `cluster`
   - group similar signals into a repeated pattern
3. `suggest`
   - emit a concrete update proposal
4. `approve`
   - user or workflow approval to proceed
5. `apply`
   - edit the relevant skill or reference
6. `verify`
   - confirm the update improves alignment and does not create duplication

Default mode is `suggest`.

## Observation Triggers

Create an observation when any of these happen:

- a referenced path is missing
- a better local authority source is discovered
- the same routing decision keeps recurring
- the same validation gap keeps recurring
- mirror copies drift in a recurring way
- a repeated workaround keeps being explained manually

## Observation Record Template

Use this structure when capturing an observation:

```md
## Skill Observation

- Signal:
- Where found:
- Affected source family:
- Repeat count:
- Immediate risk:
- Candidate target:
- Notes:
```

## Clustering Rules

Do not promote a single oddity too early.

Cluster signals when:

- the same issue appears in multiple tasks
- the same repair pattern appears in multiple tasks
- the same mismatch appears across multiple mirrored sources
- the same manual explanation is repeated often enough to justify codification

## Suggestion Thresholds

Default threshold:

- one strong structural drift signal plus one confirmation
or
- three repeated observations of the same reusable pattern

If the pattern is high-risk, require stronger evidence before suggesting an automatic structural change.

## Apply Rules

Only apply a skill update when both are true:

- the change is low-risk and structural
- explicit approval has been given for skill modification

Otherwise remain in `suggest`.

Do not patch mirrors first. Identify and update the true primary source before considering mirror synchronization.

## Evolution Targets

A suggestion can target:

- the global `local-workflow` skill
- a project-local skill
- a project-local reference file
- a project-local workflow wrapper
- project documentation instead of skill content

## Anti-Patterns

Avoid these:

- promoting one-off sprint state into global workflow
- rewriting the same rule into multiple layers
- growing `SKILL.md` with bulky detail that belongs in references
- silently changing skill behavior without traceable suggestion history
- treating every observation as an immediate edit

## Suggestion Template

Use this structure when emitting an evolution suggestion:

```md
## Skill Evolution Suggestion

- Target:
- Type: `add` / `replace` / `deprecate` / `move-to-reference`
- Reason:
- Evidence:
  - task/session:
  - files inspected:
  - repeated pattern:
- Suggested change:
- Risk if not updated:
```

Suggestions should make the skill system more coherent, not merely more verbose.

## Forward-Test Notes

When testing this skill in a real repository, pay special attention to:

- whether authority resolution chooses the correct local primary source
- whether routing selects the correct workflow family
- whether validation reasoning matches the actual task scope
- whether evolution logic suggests updates before editing mirrors
