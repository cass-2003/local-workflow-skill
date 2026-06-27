# 项目进度 · Project Progress

> 进度系统：回答“现在做到哪里、下一步是什么”。

---

## 当前焦点

把能力库从偏工程/安全/逆向的结构扩展为更均衡的通用工作流技能库，同时保持来源、许可、索引和路由可追溯。

## 进行中

- 验证并提交首批 community 技能扩容。

## 待办

- [ ] 在后续真实项目中 dogfood `project-inception-docs`，检查是否能稳定生成 `docs/INDEX.md` 和完整文档包 — 关联 `REQ-002`
- [ ] 在真实项目中 dogfood `07-artifact-contracts.md`，检查 `audit` / `fix` / `docs-sync` 是否稳定生成报告、索引和四态回写 — 关联 `REQ-009`
- [ ] 在真实项目中 dogfood `08-autonomous-project-loop.md`，检查“继续推进项目”是否会先规划、再循环执行/自审/修复/commit — 关联 `REQ-010`
- [ ] 在真实项目中 dogfood `State Restore` 与 `Loop Record`，检查 agent 是否会主动替换占位状态并写回下一目标 — 关联 `REQ-011`
- [ ] 把桌面 HTA 面板做成仓库可选包装，或明确作为本机私有便利入口 — 关联 `REQ-012`
- [ ] 继续筛选许可清晰的开源 skill 源，补充教育学习、个人生产力、法务合规、内容运营、数据科学和行业知识等低覆盖领域 — 关联 `REQ-013`

## 阻塞

- 无。

## 已完成（近期）

- [x] 首批导入 30 个 MIT community 技能，新增 6 个业务/产品/管理/研究类领域，能力库更新为 439 技能 / 24 大类 — 2026-06-28（详情可见 LOG.md）
- [x] 新增 `tools/project-init/` 初始化、入口刷新和工作流自检脚本；启动四态模板改为显式待确认结构 — 2026-06-27（详情可见 LOG.md）
- [x] 加强 `State Restore` 与 `Loop Record` 契约，让入口模板、核心和 `project-workflow` 都要求开工恢复、收工回写 — 2026-06-27（详情可见 LOG.md）
- [x] 新增 `08-autonomous-project-loop.md`，并接入核心、适配入口、project-workflow 与项目初始化模板 — 2026-06-27（详情可见 LOG.md）
- [x] README 增加“自动产物契约”独立小节，明确 audit、implement/fix、docs-sync、validation 的默认落点 — 2026-06-27（详情可见 LOG.md）
- [x] 加硬仓库根与适配模板入口的 Artifact Contracts 规则，让 `AGENTS.md` / `CLAUDE.md` 直接要求自动审计产物、状态回写和索引同步 — 2026-06-27（详情可见 LOG.md）
- [x] 新增 `07-artifact-contracts.md`，并让新项目模板默认携带 `docs/audit/INDEX.md` 与通用审计模板 — 2026-06-27（详情可见 LOG.md）
- [x] 清理项目定制 skill，同步能力库为 409 技能 / 18 大类 / 项目定制 0 — 2026-06-26（详情可见 LOG.md）
- [x] 补齐开源治理文件：LICENSE、NOTICE、CONTRIBUTING、SECURITY、CODE_OF_CONDUCT、GitHub issue/PR 模板 — 2026-06-26（详情可见 LOG.md）
- [x] 补齐根 README 与启动模板 README 的项目地基说明 — 2026-06-26（详情可见 LOG.md）
- [x] 强化新项目地基门禁：Git、忽略文件、agent 入口、四态、文档入口、验证入口 — 2026-06-26（详情可见 LOG.md）
- [x] 按授权原位更新 18 个 Coffee/Coff0xc 技能并保存来源记录 — 2026-06-26（详情可见 LOG.md）
- [x] 沉淀 `project-inception-docs` 标准启动文档模板资产 — 2026-06-26（详情可见 LOG.md）
- [x] 完成 `project-inception-docs` 多文档启动包增强与索引计数同步 — 2026-06-26（详情可见 LOG.md）
- [x] 初始化本仓库根 `state/` 四态系统 — 2026-06-26（详情可见 LOG.md）
- [x] 完成本轮验证并准备原子 commit — 2026-06-26（详情可见 LOG.md）
- [x] 明确 `project-workflow` 的全局工作流入口职责 — 2026-06-26（详情可见 LOG.md）
- [x] 增加 Codex `AGENTS.md` 与 Claude Code `CLAUDE.md` 适配模板 — 2026-06-26（详情可见 Git 历史）

## Loop Record · 2026-06-28 · community-skill-expansion

- Goal: 降低能力库领域偏重，首批导入通用非工程类开源技能。
- Acceptance Criteria: 新技能许可清晰；不包含项目定制或私有路径；目录结构符合 `<domain>/community/<skill>/`；README、路由、分级、manifest、provenance 和状态文件同步。
- Validation Evidence: 已通过 manifest 计数校验（439 winners / 30 community / 通用 390 / 半通用 49）、community frontmatter 校验、旧索引残留扫描、密钥模式扫描、`git diff --check`、临时 manifest 生成 smoke test。
- Self-Audit: 初筛跳过 Anthropic 无根许可全量导入与 wshobson agent 角色库；只导入 MIT `alirezarezvani/claude-skills` 中通用业务/产品/管理/研究运营能力。
- Repairs: 新增 `community` 来源层并更新合并工具，避免后续 manifest 重建遗忘第三方导入。
- State/Docs Sync: 已同步 README、skills README、routing、TIERS、NOTICE、REQ/LOG/MEMORY/PROGRESS。
- Commit: 待创建原子 commit。
- Next Goal: 继续补教育学习、个人生产力、法务合规、内容运营、数据科学和行业知识等低覆盖领域。
- Stop Reason: 本轮先收敛为首批可验证导入，避免一次性搬运过多第三方内容。
