# 适配器 · Codex

> 状态：**已登记并完成样板 dogfood**。模板就绪，`sample-project` 已补齐 Codex 入口并完成阶段 5 验证。

## 适配器实例

Codex 在仓库根发现 `AGENTS.md`，并可读取 `agents/*.yaml` 的角色描述。本适配器以这两者为入口：

➡️ **`codex/AGENTS.md`** — 薄入口，声明 10 阶段工作方式并指向中立核心
➡️ **`codex/agents/workflow.yaml`** — interface 描述（display_name / default_prompt）

## 与 CC 适配器的对称关系

| | Claude Code | Codex |
|---|---|---|
| 原生发现入口 | `SKILL.md`（skills 目录） | `AGENTS.md` + `agents/*.yaml`（仓库根） |
| 实例位置 | `../../skills/workflow-orchestration/ours/project-workflow/` | 本目录 `codex/`（模板，复制到目标项目根） |
| 规范来源 | `../core/*`（薄指针） | `../core/*`（薄指针） |
| 登记文件 | `claude-code.md` | 本文件 |

> 两者都只做"被触发 + 指路"，流程逻辑全部留在中立核心，单处维护。差异仅在各自的原生入口格式。

## 安装到目标项目

1. 把 `codex/AGENTS.md` 复制到目标项目根（若已有 `AGENTS.md`，把"工作方式 + 规范指针"两节并入）。
2. 把 `codex/agents/` 复制到目标项目（或并入既有 `agents/`）。
3. 把框架中立核心（`framework/core/` + `framework/state-systems/`）放到目标项目，推荐 `.agent-os/framework/`。
4. 按实际安装位置，校正 `AGENTS.md` 规范指针表里的路径前缀。

## 默认自动行为

接入后，Codex 侧默认按以下方式工作：

- 开工先 scan，再从四态系统恢复状态
- 若仓库缺少稳定的日志 / 需求 / 记忆 / 进度承载，先初始化最小四态骨架
- 执行完成后先过验证，再回写四态系统
- 若验证通过、四态已同步、且本轮是单一逻辑改动，则默认创建原子 commit

默认**不**自动做：

- push
- merge
- PR 创建
- 在验证不足或混合改动时强行 commit

## 单一真相原则

- 流程规范只在 `../core/*` 维护。改流程 → 改 core，不改 `AGENTS.md` / `workflow.yaml`。
- 新增 Codex 专属约定（触发词、角色描述）才写在 `AGENTS.md` 正文或 `workflow.yaml`。

## 端到端实测（阶段 5）

- [x] 在样板项目里验证 Codex 入口结构：`AGENTS.md` + `agents/workflow.yaml`
- [x] 对 `sample-project` 走一遍 scan / state restore / route / validate / sync 的完整流程
- [x] 与 CC 侧 dogfood 结果对齐，确认四态恢复、主路由、验证与回写模型一致

验证记录见 `../validation/dogfood-stage5-codex.md`。
