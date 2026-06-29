# 项目需求 · Project Requirements

> 需求系统：回答“当前要满足什么”。需求应有可验证验收口径。

---

## 当前目标

把本仓库维护成可被 Codex、Claude Code 等 agent 共同使用的四态工作流与技能库母仓；项目开发时优先恢复状态、路由技能、生成必要文档、验证后同步状态并默认进入原子 commit 闭环。

## 需求清单

| ID | 需求 | 验收标准 | 状态 | 关联进度 |
|----|------|----------|------|----------|
| REQ-001 | `project-workflow` 能作为全局工作流编排入口使用 | 规则中明确扫描、状态恢复、路由、验证、同步、交付和演进顺序 | done | PROGRESS#已完成 |
| REQ-002 | `project-inception-docs` 能从想法生成项目启动文档包 | 技能列出核心包、工程实施包、治理迁移包，并覆盖截图里的多文档产物 | done | PROGRESS#已完成 |
| REQ-003 | 本仓库自身具备四态承载文件 | 根目录存在 `state/LOG.md`、`state/REQUIREMENTS.md`、`state/MEMORY.md`、`state/PROGRESS.md` 且包含当前目标 | done | PROGRESS#已完成 |
| REQ-004 | 完成可验证修改后默认进入原子 commit 闭环 | commit 前检查 status、diff、验证结果和状态同步；多逻辑变更拆成多个原子 commit；且不自动 push/merge/PR | done | PROGRESS#已完成 |
| REQ-005 | `project-inception-docs` 提供可复制的标准启动文档模板资产 | skill 内存在 `references/startup-doc-package.md` 与 `assets/templates/startup-docs/`，覆盖产品、架构、API、AI、计划、测试、运维、安全、迁移和四态模板 | done | PROGRESS#已完成 |
| REQ-006 | 授权 Coffee skill 导入可追溯且不产生重复触发 | 18 个 Coff0xc 技能原位更新，保留本地 slug，并保存 LICENSE/NOTICE/manifest/import mapping | done | PROGRESS#已完成 |
| REQ-007 | 新项目必须先补齐可持续开发地基 | 首次接入时检查 Git、`.gitignore`、agent 入口、四态系统、README、docs/INDEX 和验证命令；缺 Git 时默认初始化但不默认 push | done | PROGRESS#已完成 |
| REQ-008 | 本仓库必须保持开源通用，不携带项目定制 skill | manifest、README、路由表和分级文档显示项目定制项为 0；强绑具体项目/产品/旧命令封装的 skill 不进入 `skills/` | done | PROGRESS#已完成 |
| REQ-009 | 工作流应自动留下审计、验证、文档和状态产物 | 核心包含 `07-artifact-contracts.md`；新项目模板包含 `docs/audit/INDEX.md` 与审计模板；AGENTS/CLAUDE 入口声明审计、实现、修复和 docs-sync 不只停留在对话里 | done | PROGRESS#已完成 |
| REQ-010 | 自主推进应先规划、再按工作包循环执行/自审/修复/提交 | 核心包含 `08-autonomous-project-loop.md`；入口模板要求路线图、下一步工作包、单目标循环、停止条件和默认原子 commit | done | PROGRESS#已完成 |
| REQ-011 | 状态系统必须可恢复而非仅存在 | 核心和入口模板要求开工前输出 `State Restore` 摘要，识别占位/陈旧状态，并在每轮结束写入 `Loop Record`，包含目标、验收、验证、自审、修复、同步、commit、下一目标或停止原因 | done | PROGRESS#已完成 |
| REQ-012 | 项目初始化和入口刷新能力应可复现 | 仓库内提供 `tools/project-init/Initialize-PortableAgentProject.ps1` 与 `Validate-PortableAgentWorkflow.ps1`；支持完整初始化、只刷新托管入口、保留项目专属内容，并有 smoke test | done | PROGRESS#已完成 |
| REQ-013 | 能力库领域覆盖应减少安全/逆向/工程偏重 | 首批导入许可清晰、可追溯、通用的 community 技能，新增业务运营、商业策略、财务指标、产品管理、项目管理、研究运营领域；索引、路由、分级和来源记录同步 | done | PROGRESS#已完成 |
| REQ-014 | 能力库至少覆盖 50 个领域大类 | 第二批导入许可清晰、可追溯、通用的 community 技能；README、skills README、路由、分级和 manifest 显示不少于 50 个大类，且项目定制项仍为 0 | done | PROGRESS#已完成 |
| REQ-015 | 前端 UI 与后端 API 应具备高频基础工程技能 | 新增通用 `ours` 技能覆盖设计系统落地、前端状态/数据流、前端性能、认证授权、事务一致性、API 错误与可观测性；manifest、README、skills README、TIERS、路由和四态系统计数一致 | done | PROGRESS#已完成 |
| REQ-016 | 官方 Codex plugin skill 导入必须许可清晰且可追溯 | 只导入 `openai/plugins` 中明确 MIT/Apache 等可再分发许可的 skill；保存 provenance；不重复导入已有 slug；manifest、README、skills README、TIERS、路由和四态系统计数一致 | done | PROGRESS#已完成 |
| REQ-017 | App 与小程序开发应具备项目级工程骨架技能 | 新增通用 `ours` 技能覆盖 App 架构、离线同步、推送、发布运营、小程序架构、微信小程序、登录支付和 Taro/uniapp 跨端；manifest、README、skills README、TIERS、路由和四态系统计数一致 | done | PROGRESS#已完成 |
| REQ-018 | 项目初始化应先分类并支持多轮需求访谈 | “初始化项目”先区分空目录新想法、半初始化、已有项目后补 workflow、明确想法或直接地基请求；空目录/新想法默认先按角色多轮提问，不臆测生成完整文档；启动模板和全局入口同步该规则 | done | PROGRESS#global-project-discovery-interview |
| REQ-019 | 能力库应让用户看得懂有哪些领域和使用场景 | 根 README 提供按目标快速找能力；`skills/CATALOG.md` 提供人类导览版目录；`skills/README.md` 顶部指向导览、完整索引、分级和 manifest | done | PROGRESS#skill-catalog-discoverability |
| REQ-020 | 第三方授权 skill 来源不应在公开导览中单独高亮 | 目录结构、README、skills README、路由和合并工具公开说明只展示 `ours / codex / community` 三层；原始来源与许可保留在 provenance / manifest 审计资料中 | done | PROGRESS#third-party-source-flattening |
| REQ-021 | UI 规范禁止 emoji 充当生产图标 | `UIdesign`、UI quality checklist 和 `design-system-implementation` 明确要求使用 SVG/vector icon system 或统一矢量图标库；emoji 不作为导航、状态、工具栏、按钮或空状态图标 | done | PROGRESS#ui-vector-icon-policy |

## 约束与非目标

- 约束：项目本地 `AGENTS.md`、`CLAUDE.md`、rules、skills 和 truth docs 优先于全局兜底。
- 约束：技能内容保持精简，不为单个 skill 增加无必要 README、CHANGELOG 等杂物。
- 约束：在 Git 仓库内完成可验证修改后默认 commit；多逻辑变更必须拆分；验证不足、冲突、敏感信息或等待用户决策时记录未提交原因。
- 约束：本仓库只保留通用或半通用 skill；项目定制 skill 应放在目标项目本地或私有仓库，不进入开源通用库。
- 约束：自动生成的审计、验收、验证和文档同步产物必须基于项目事实、证据或明确待确认项，不为了凑文件生成空壳。
- 约束：新项目需求访谈阶段不写业务代码、不生成完整文档包；只有用户确认、需求达到最低清晰度，或用户接受未知项标 `待确认` 时才进入生成阶段。
- 约束：能力库公开入口不能只展示数量；必须提供面向用户目标、领域分类和完整 slug 索引的多层导览。
- 约束：第三方授权来源统一并入 `community/` 展示层；不要在公开 README 和领域索引里单独突出某个授权包或商业属性。
- 约束：生产 UI 图标必须来自一致的 SVG/vector icon system；不要用 emoji 代替正式图标、状态标记或交互控件。
- 非目标：不默认自动 push、merge 或创建 PR。
