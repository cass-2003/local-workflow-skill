# Execution Phases

## Purpose

Define the standard loop the workflow orchestrator should follow for substantial work so routing, verification, and documentation sync happen in a consistent order.

Use all phases for substantial or cross-skill work.
For trivial one-step work, skip only phases that are clearly irrelevant, but do not skip authority checks or validation reasoning when project truth changes.

## Phase 0: Workspace Scan

Purpose:

- identify whether the repository already has local workflow infrastructure
- avoid acting from stale assumptions

Actions:

- inspect repository root instruction files
- inspect project-local workflow folders such as `.codex`, `.agents`, `.claude`, or similar
- inspect docs that serve as state or truth sources
- inspect build/test scripts if validation is likely required

Outputs:

- active authority locations
- likely task domain
- likely verification commands

## Phase 1: Intent Classification

Purpose:

- decide whether the task is mainly status, audit, implement, fix, review, docs sync, Git delivery, or workflow evolution

Questions:

- Is the user asking for current state only
- Is the user asking for comparison against a baseline
- Is the user asking for new code or changed behavior
- Is the user asking to repair known issues
- Is the user asking to inspect a diff
- Is the user asking to sync project documents or planning artifacts
- Is the user asking to package, commit, branch, or ship work

Outputs:

- primary intent
- possible secondary route
- initial scope estimate

## Phase 2: Authority Resolution

Purpose:

- determine which local layer should be trusted first

Actions:

- resolve rule source
- resolve workflow-wrapper source
- resolve execution-skill source
- detect stale or mirrored copies
- identify global fallback only if needed

Outputs:

- active local rule family
- active workflow entry family
- active execution skill family
- truth-doc source
- drift warnings
- fallback chain

## Phase 3: Skill Delegation

Purpose:

- call the most appropriate local skill instead of restating its logic

Actions:

- route to the best matching local workflow or domain skill
- keep orchestration ownership in `local-workflow`
- preserve local authority and validation gates during delegation

Outputs:

- primary delegated skill
- secondary delegated skill, if any
- explicit fallback decision if no local skill exists

## Phase 4: Task Execution

Purpose:

- perform the requested work while respecting local constraints

Rules:

- read before editing
- prefer minimal necessary change
- preserve project-local conventions
- distinguish facts, assumptions, and inferred next steps

Outputs:

- completed analysis, edits, or decisions
- list of affected files or workflow surfaces

## Phase 5: Validation Gate

Purpose:

- prevent "done by assertion"

Actions:

- choose validation level based on change scope
- use project-local validation skills when available
- record what was validated and what was skipped

Outputs:

- validation evidence
- validation gaps, if any

## Phase 6: Documentation And State Sync

Purpose:

- ensure project memory is updated when work changes project truth

Triggers:

- feature implementation
- bug fix
- audit conclusion changes
- status model changes
- task-plan changes
- user-facing usage changes

Outputs:

- synced docs or explicit note that no sync was needed

## Phase 7: Git And Delivery

Purpose:

- ensure safe packaging of the work

Actions:

- inspect unstaged or staged diff
- invoke Git skills when branch, commit, PR, or merge actions are needed
- avoid destructive operations unless explicitly requested

Outputs:

- delivery decision
- commit or handoff-ready state

## Phase 8: Skill Evolution

Purpose:

- turn repeated useful patterns into structured skill improvements

Actions:

- capture observations
- cluster repeated signals
- emit suggestions
- apply only with explicit approval

Outputs:

- observation or suggestion record
- skill-evolution follow-up if warranted
