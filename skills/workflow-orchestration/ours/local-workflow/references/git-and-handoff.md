# Git And Handoff

## Purpose

Define how the workflow orchestrator should prepare work for safe delivery without replacing the detailed logic already handled by dedicated Git skills.

## When To Invoke Git Skills

Invoke Git skills when the task involves:

- commits
- branch creation or switching
- pull requests
- merge strategy decisions
- delivery packaging that depends on repository state

Do not bypass local validation and authority checks just because the user asked for Git delivery.

## Pre-Commit Checks

Before commit-oriented actions:

- inspect the actual diff
- confirm the validation gate has run at the right scope
- confirm docs or state sync has been considered
- confirm no destructive Git action is being implied silently

If the change is not ready for delivery, report that clearly instead of forcing a commit flow.

## Delivery Actions

Possible delivery states:

- not ready for delivery
- ready for commit
- ready for branch/PR flow
- ready for final handoff without Git action

Choose the smallest honest delivery claim that the evidence supports.

## Handoff Summary Format

Handoff should stay concise and include:

- what changed
- what was validated
- what remains uncertain or intentionally unvalidated
- what the next useful action is

Do not overclaim completion when evidence is partial.

## Destructive-Action Guardrails

Treat these as guarded actions:

- force push
- hard reset
- destructive branch deletion
- other history-rewriting or remote-mutating actions

Do not perform them unless explicitly requested and clearly justified by the task.
