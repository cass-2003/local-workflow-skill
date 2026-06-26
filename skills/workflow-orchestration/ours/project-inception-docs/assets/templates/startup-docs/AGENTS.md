# AGENTS.md

## Project Workflow

- Start substantial work with: scan -> state restore -> intent -> authority -> route -> execute -> validate -> sync -> deliver -> evolve.
- Before business development, ensure the project foundation is ready: Git, `.gitignore`, README, docs index, Four-State files, validation commands, and this agent entry.
- If this directory has no `.git/` and is not inside another Git worktree, initialize Git before continuing.
- Prefer project-local truth docs over global memory.
- After a validated single-scope change, create an atomic commit by default; do not push unless explicitly requested.

## State System

- Log: `state/LOG.md`
- Requirements: `state/REQUIREMENTS.md`
- Memory: `state/MEMORY.md`
- Progress: `state/PROGRESS.md`

## Documentation Entry

- Project overview: `README.md`
- Documentation map: `docs/INDEX.md`
- Initialization plan: `docs/planning/工程初始化方案.md`
- Current status: `docs/planning/当前工程状态.md`
