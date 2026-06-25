# 适配器 · Codex

> 状态：**已登记**（框架路线图阶段 4）。模板就绪，待真实 Codex runtime 端到端实测（阶段 5）。

## 适配器实例

Codex 在仓库根发现 `AGENTS.md`，并可读取 `agents/*.yaml` 的角色描述。本适配器以这两者为入口：

➡️ **`codex/AGENTS.md`** — 薄入口，声明 10 阶段工作方式并指向中立核心
➡️ **`codex/agents/workflow.yaml`** — interface 描述（display_name / default_prompt）

## 与 CC 适配器的对称关系

| | Claude Code | Codex |
|---|---|---|
| 原生发现入口 | `SKILL.md`（skills 目录） | `AGENTS.md` + `agents/*.yaml`（仓库根） |
| 实例位置 | `../../skills/workflow-core/project-workflow/` | 本目录 `codex/`（模板，复制到目标项目根） |
| 规范来源 | `../core/*`（薄指针） | `../core/*`（薄指针） |
| 登记文件 | `claude-code.md` | 本文件 |

> 两者都只做"被触发 + 指路"，流程逻辑全部留在中立核心，单处维护。差异仅在各自的原生入口格式。

## 安装到目标项目

1. 把 `codex/AGENTS.md` 复制到目标项目根（若已有 `AGENTS.md`，把"工作方式 + 规范指针"两节并入）。
2. 把 `codex/agents/` 复制到目标项目（或并入既有 `agents/`）。
3. 把框架中立核心（`framework/core/` + `framework/state-systems/`）放到目标项目，推荐 `.agent-os/framework/`。
4. 按实际安装位置，校正 `AGENTS.md` 规范指针表里的路径前缀。

## 单一真相原则

- 流程规范只在 `../core/*` 维护。改流程 → 改 core，不改 `AGENTS.md` / `workflow.yaml`。
- 新增 Codex 专属约定（触发词、角色描述）才写在 `AGENTS.md` 正文或 `workflow.yaml`。

## 端到端实测（阶段 5，待办）

- [ ] 在装了本模板的真实项目里，让 Codex 只做 scan + state restore + 路由分析
- [ ] 让 Codex 跑一次带验证闸门 + 文档同步的完整任务
- [ ] 与 CC 适配器对跑同一任务，核对四态系统读写是否一致
