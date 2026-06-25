# Client Compatibility

Use this reference when installing, sharing, or debugging `Dev` across coding agents.

## Format Rules

- Directory must be `dev`.
- `SKILL.md` must start with YAML frontmatter.
- `name` must match the directory name.
- The display label can be `Dev`; the machine-readable skill name remains lowercase `dev`.
- `description` should front-load trigger words because some clients trim skill descriptions.
- Keep core behavior in the markdown body; optional client-specific frontmatter may be ignored elsewhere.

## Locations

| Client | Best local location | Notes |
|---|---|---|
| CC Switch | `~/.cc-switch/skills/dev/SKILL.md` | When `skillStorageLocation` is `cc_switch`, also register the skill in `cc-switch.db`. |
| Codex | `~/.agents/skills/dev/SKILL.md` | Codex reads AgentSkills-compatible folders from `.agents/skills`. |
| Claude Code | `~/.claude/skills/dev/SKILL.md` | Claude Code documents `.claude/skills` as the personal skill path. |
| OpenCode | `~/.agents/skills/dev/SKILL.md` or `~/.config/opencode/skills/dev/SKILL.md` | OpenCode scans `.opencode`, `.claude`, and `.agents`; avoid duplicate names. |
| OpenClaw | `~/.agents/skills/dev/SKILL.md` or `~/.openclaw/skills/dev/SKILL.md` | OpenClaw uses AgentSkills-compatible folders and applies workspace precedence. |

## Duplicate Name Rule

If a client lists this skill twice, keep one active copy for that client session:

- For Codex/OpenClaw/OpenCode, prefer the `.agents/skills` copy.
- For Claude Code, prefer the `.claude/skills` copy.
- For CC Switch, prefer the `.cc-switch/skills/dev` copy and its database entry.
- If using OpenCode while both global `.agents` and `.claude` copies exist, either remove one copy for that session or configure skill visibility so only one appears.

## Verification Prompts

Try these after installation:

```text
Use Dev to build a small dashboard module in this repo. Make low-risk decisions yourself and only ask for production, deletion, paid API, or remote changes.
```

```text
I want a RAG app end to end: upload docs, index them, chat with citations, and test the main flow. Minimize questions.
```

Expected behavior: the agent should inspect the repo, record assumptions, classify risk, plan modules, implement in small loops, verify, review, and report concise results.
