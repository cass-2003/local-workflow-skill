# 项目需求 · Project Requirements

> 需求系统：回答“当前要满足什么”。需求应有可验证验收口径。

---

## 当前目标

把本仓库维护成可被 Codex、Claude Code 等 agent 共同使用的四态工作流与技能库母仓；项目开发时优先恢复状态、路由技能、生成必要文档、验证后同步状态并默认做原子 commit。

## 需求清单

| ID | 需求 | 验收标准 | 状态 | 关联进度 |
|----|------|----------|------|----------|
| REQ-001 | `project-workflow` 能作为全局工作流编排入口使用 | 规则中明确扫描、状态恢复、路由、验证、同步、交付和演进顺序 | done | PROGRESS#已完成 |
| REQ-002 | `project-inception-docs` 能从想法生成项目启动文档包 | 技能列出核心包、工程实施包、治理迁移包，并覆盖截图里的多文档产物 | done | PROGRESS#已完成 |
| REQ-003 | 本仓库自身具备四态承载文件 | 根目录存在 `state/LOG.md`、`state/REQUIREMENTS.md`、`state/MEMORY.md`、`state/PROGRESS.md` 且包含当前目标 | done | PROGRESS#已完成 |
| REQ-004 | 完成单一范围变更后默认原子提交 | commit 前检查 status、diff、验证结果，且不自动 push/merge/PR | done | PROGRESS#已完成 |
| REQ-005 | `project-inception-docs` 提供可复制的标准启动文档模板资产 | skill 内存在 `references/startup-doc-package.md` 与 `assets/templates/startup-docs/`，覆盖产品、架构、API、AI、计划、测试、运维、安全、迁移和四态模板 | done | PROGRESS#已完成 |

## 约束与非目标

- 约束：项目本地 `AGENTS.md`、`CLAUDE.md`、rules、skills 和 truth docs 优先于全局兜底。
- 约束：技能内容保持精简，不为单个 skill 增加无必要 README、CHANGELOG 等杂物。
- 约束：自动 commit 只在验证充分、变更单一且无敏感信息时执行。
- 非目标：不默认自动 push、merge 或创建 PR。
