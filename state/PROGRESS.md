# 项目进度 · Project Progress

> 进度系统：回答“现在做到哪里、下一步是什么”。

---

## 当前焦点

把能力库从偏工程/安全/逆向的结构扩展为更均衡的通用工作流技能库，同时保持来源、许可、索引和路由可追溯。

## 进行中

- 验证并提交第二批 community 技能扩容。

## 待办

- [ ] 在后续真实项目中 dogfood `project-inception-docs`，检查是否能稳定生成 `docs/INDEX.md` 和完整文档包 — 关联 `REQ-002`
- [ ] 在真实项目中 dogfood `07-artifact-contracts.md`，检查 `audit` / `fix` / `docs-sync` 是否稳定生成报告、索引和四态回写 — 关联 `REQ-009`
- [ ] 在真实项目中 dogfood `08-autonomous-project-loop.md`，检查“继续推进项目”是否会先规划、再循环执行/自审/修复/commit — 关联 `REQ-010`
- [ ] 在真实项目中 dogfood `State Restore` 与 `Loop Record`，检查 agent 是否会主动替换占位状态并写回下一目标 — 关联 `REQ-011`
- [ ] 把桌面 HTA 面板做成仓库可选包装，或明确作为本机私有便利入口 — 关联 `REQ-012`
- [ ] 继续筛选许可清晰的开源 skill 源，重点补数据科学、法务、HR、教育、创意制作、行业知识和本地化等仍较薄领域 — 关联 `REQ-014`

## 阻塞

- 无。

## 已完成（近期）

- [x] 第二批导入 78 个 MIT community 技能，能力库扩展到 517 技能 / 58 大类，覆盖至少 50 个领域大类 — 2026-06-28（详情可见 LOG.md）
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

- Goal: 降低能力库领域偏重，并把领域大类扩展到至少 50 个。
- Acceptance Criteria: 新技能许可清晰；不包含项目定制或私有路径；目录结构符合 `<domain>/community/<skill>/`；README、路由、分级、manifest、provenance 和状态文件同步；总领域数不少于 50。
- Validation Evidence: 已通过 manifest 计数校验（517 winners / 108 community / 通用 468 / 半通用 49）、领域计数校验（58 domains）、community frontmatter 校验、旧口径残留扫描、密钥模式扫描、redaction sample smoke test 和 `git diff --check`。
- Self-Audit: OpenAI/Codex 官方 skill 资料用于格式与触发机制参考；OpenAI `openai/skills` 仓库已 deprecated，不做重复导入；Anthropic 无根许可全量导入与 wshobson agent 角色库仍跳过；本轮只导入 MIT `alirezarezvani/claude-skills` 中通用非工程能力。
- Repairs: 新增营销、合规、研究、学习、生产力、销售、组织管理和发布类细粒度大类，避免继续偏向工程/安全/逆向。
- State/Docs Sync: 已同步 README、skills README、routing、TIERS、provenance、REQ/LOG/MEMORY/PROGRESS。
- Commit: 本轮提交使用 `feat: expand skill domains beyond fifty`。
- Next Goal: 后续继续补数据科学、法务、HR、教育、创意制作、行业知识和本地化等薄弱领域，并考虑建立 skill eval/触发测试样例。
- Stop Reason: 本轮目标是先达到 50+ 大类并完成可验证导入；更大规模导入需要下一轮按许可和触发质量继续筛选。
