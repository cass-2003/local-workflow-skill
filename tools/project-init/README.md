# Project Init Tools

Reusable initializer and validation tools for Portable Agent Workflow.

These scripts are the open-source version of the local project foundation tools.
They avoid hardcoded machine paths by resolving the repository root from this
directory by default.

## Scripts

| Script | Purpose |
|---|---|
| `Initialize-PortableAgentProject.ps1` | Initialize or refresh a target project with Git, `.gitignore`, `AGENTS.md`, `CLAUDE.md`, README, docs, and Four-State files. |
| `Validate-PortableAgentWorkflow.ps1` | Check the workflow repo for required contracts and run a small initializer smoke test. |

## Initialize A Project

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\project-init\Initialize-PortableAgentProject.ps1 `
  -ProjectPath "C:\path\to\project" `
  -ProjectName "My Project" `
  -Idea "One-sentence goal" `
  -RefreshAgentEntries `
  -EnsureIndexes
```

## Refresh Only Agent Entries

This refreshes only the managed Portable Agent Workflow block in `AGENTS.md`
and `CLAUDE.md`. It preserves project-specific sections outside the managed
block and does not initialize Git or write README/docs/state files.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\project-init\Initialize-PortableAgentProject.ps1 `
  -ProjectPath "C:\path\to\project" `
  -AgentEntriesOnly
```

## Validate This Repository

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\project-init\Validate-PortableAgentWorkflow.ps1
```

Use `-SkipSmoke` to skip the temporary project smoke test.
