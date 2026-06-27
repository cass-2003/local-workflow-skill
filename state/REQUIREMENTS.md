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
| REQ-006 | 授权 Coffee skill 导入可追溯且不产生重复触发 | 18 个 Coff0xc 技能原位更新，保留本地 slug，并保存 LICENSE/NOTICE/manifest/import mapping | done | PROGRESS#已完成 |
| REQ-007 | 新项目必须先补齐可持续开发地基 | 首次接入时检查 Git、`.gitignore`、agent 入口、四态系统、README、docs/INDEX 和验证命令；缺 Git 时默认初始化但不默认 push | done | PROGRESS#已完成 |
| REQ-008 | 本仓库必须保持开源通用，不携带项目定制 skill | manifest、README、路由表和分级文档显示项目定制项为 0；强绑具体项目/产品/旧命令封装的 skill 不进入 `skills/` | done | PROGRESS#已完成 |
| REQ-009 | 工作流应自动留下审计、验证、文档和状态产物 | 核心包含 `07-artifact-contracts.md`；新项目模板包含 `docs/audit/INDEX.md` 与审计模板；AGENTS/CLAUDE 入口声明审计、实现、修复和 docs-sync 不只停留在对话里 | done | PROGRESS#已完成 |
| REQ-010 | 自主推进应先规划、再按工作包循环执行/自审/修复/提交 | 核心包含 `08-autonomous-project-loop.md`；入口模板要求路线图、下一步工作包、单目标循环、停止条件和默认原子 commit | done | PROGRESS#已完成 |
| REQ-011 | 状态系统必须可恢复而非仅存在 | 核心和入口模板要求开工前输出 `State Restore` 摘要，识别占位/陈旧状态，并在每轮结束写入 `Loop Record`，包含目标、验收、验证、自审、修复、同步、commit、下一目标或停止原因 | done | PROGRESS#已完成 |
| REQ-012 | 项目初始化和入口刷新能力应可复现 | 仓库内提供 `tools/project-init/Initialize-PortableAgentProject.ps1` 与 `Validate-PortableAgentWorkflow.ps1`；支持完整初始化、只刷新托管入口、保留项目专属内容，并有 smoke test | done | PROGRESS#已完成 |
| REQ-013 | 能力库领域覆盖应减少安全/逆向/工程偏重 | 首批导入许可清晰、可追溯、通用的 community 技能，新增业务运营、商业策略、财务指标、产品管理、项目管理、研究运营领域；索引、路由、分级和来源记录同步 | done | PROGRESS#已完成 |

## 约束与非目标

- 约束：项目本地 `AGENTS.md`、`CLAUDE.md`、rules、skills 和 truth docs 优先于全局兜底。
- 约束：技能内容保持精简，不为单个 skill 增加无必要 README、CHANGELOG 等杂物。
- 约束：自动 commit 只在验证充分、变更单一且无敏感信息时执行。
- 约束：本仓库只保留通用或半通用 skill；项目定制 skill 应放在目标项目本地或私有仓库，不进入开源通用库。
- 约束：自动生成的审计、验收、验证和文档同步产物必须基于项目事实、证据或明确待确认项，不为了凑文件生成空壳。
- 非目标：不默认自动 push、merge 或创建 PR。
