# 项目进度 · Project Progress

> 进度系统：回答“现在做到哪里、下一步是什么”。

---

## 当前焦点

把通用工作流从“有流程骨架”推进到“默认留下审计、验证、文档和状态产物”，并持续避免项目定制内容回流。

## 进行中

- 无。

## 待办

- [ ] 在后续真实项目中 dogfood `project-inception-docs`，检查是否能稳定生成 `docs/INDEX.md` 和完整文档包 — 关联 `REQ-002`
- [ ] 在真实项目中 dogfood `07-artifact-contracts.md`，检查 `audit` / `fix` / `docs-sync` 是否稳定生成报告、索引和四态回写 — 关联 `REQ-009`

## 阻塞

- 无。

## 已完成（近期）

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
