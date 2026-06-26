# Contributing

Thanks for helping improve Portable Agent Workflow. This repo is meant to stay
portable and project-neutral, so contributions should improve reusable workflow,
state, adapter, or skill behavior.

## What Belongs Here

- Generic workflow rules, state templates, adapters, validation notes, and docs.
- Generic or semi-generic skills that can be reused across projects.
- Vendor/product-specific skills when they are broadly reusable and clearly
  documented.
- Merge tooling improvements that remain path-portable and reproducible.

## What Does Not Belong Here

- Skills tied to a private project, internal product name, client, workspace,
  server, account, or local absolute path.
- Runtime command wrappers that only make sense in one private setup.
- Secrets, credentials, private hostnames, tokens, private keys, or `.env` data.
- Large generated artifacts that are not needed to understand or validate a
  skill.

## Skill Checklist

- Add or update a `SKILL.md` with clear frontmatter and a reusable description.
- Keep examples generic; replace private names with placeholders.
- Prefer references/assets only when they are needed by the skill.
- Update `skills/_merge-manifest.csv`, `skills/README.md`, and `skills/TIERS.md`
  when counts or routing-visible entries change.
- If importing external material, preserve its license and add provenance notes.

## Workflow Checklist

- Follow the Four-State Workflow: scan, restore state, clarify intent, resolve
  authority, route, execute, validate, sync state, deliver, evolve.
- Update `state/LOG.md`, `state/REQUIREMENTS.md`, `state/MEMORY.md`, or
  `state/PROGRESS.md` when the repository truth changes.
- Run the smallest validation that matches the change.
- Before committing, inspect `git status`, `git diff`, and staged diff. Do not
  use broad staging if unrelated local changes exist.

## Pull Requests

- Keep each PR focused on one logical change.
- Explain what changed, how it was validated, and whether docs/state were
  updated.
- Mention any license or provenance impact.
