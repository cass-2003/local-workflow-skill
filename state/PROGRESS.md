# 项目进度 · Project Progress

> 进度系统：回答“现在做到哪里、下一步是什么”。

---

## 当前焦点

把能力库从偏工程/安全/逆向的结构扩展为更均衡、可发现的通用工作流技能库，并补齐 App / 小程序等真实项目常见开发能力；同时把跨 agent 工作流纪律（状态恢复、产物同步、原子 commit 闭环、项目启动访谈）同步到所有入口和模板。

## 进行中

- 第三方授权来源已并入 `community` 展示层，正在做一致性验证和提交。

## 待办

- [ ] 在后续真实项目中 dogfood `project-inception-docs`，检查是否能稳定生成 `docs/INDEX.md` 和完整文档包 — 关联 `REQ-002`
- [ ] 在真实项目中 dogfood `07-artifact-contracts.md`，检查 `audit` / `fix` / `docs-sync` 是否稳定生成报告、索引和四态回写 — 关联 `REQ-009`
- [ ] 在真实项目中 dogfood `08-autonomous-project-loop.md`，检查“继续推进项目”是否会先规划、再循环执行/自审/修复/commit — 关联 `REQ-010`
- [ ] 在真实项目中 dogfood `State Restore` 与 `Loop Record`，检查 agent 是否会主动替换占位状态并写回下一目标 — 关联 `REQ-011`
- [ ] 把桌面 HTA 面板做成仓库可选包装，或明确作为本机私有便利入口 — 关联 `REQ-012`
- [ ] 继续筛选许可清晰的开源 skill 源，重点补数据科学、法务、HR、教育、创意制作、行业知识和本地化等仍较薄领域 — 关联 `REQ-014`
- [ ] 在真实前后端项目中 dogfood 新增的设计系统、前端性能、状态数据流、认证授权、事务一致性、API 错误可观测性技能，检查触发质量和执行粒度 — 关联 `REQ-015`
- [ ] 继续审计 `openai/plugins` 中其它有明确许可的官方 skill，重点看 GitHub、Notion、Cloudflare、Vercel、Netlify 等是否能无重复补强 — 关联 `REQ-016`
- [ ] 在真实 App / 小程序项目中 dogfood 新增的移动端架构、离线同步、推送、发布运营、小程序登录支付和跨端适配技能 — 关联 `REQ-017`

## 阻塞

- 无。

## 已完成（近期）

- [x] 将第三方授权来源统一并入 `community` 展示层，公开导览不再单独高亮商业来源 — 2026-06-29（详情可见 LOG.md）
- [x] 新增 8 个 App / 小程序通用 `ours` 技能，能力库扩展到 565 技能 / 58 大类 — 2026-06-28（详情可见 LOG.md）
- [x] 同步 Codex、Claude Code、`.agents`、workflow core、adapters、启动模板和 git/commit skills 的 commit 闭环纪律 — 2026-06-28（详情可见 LOG.md）
- [x] 为项目初始化加入 Project Classification Gate 与 Discovery Interview，空目录/新想法先多轮需求访谈 — 2026-06-29（详情可见 LOG.md）
- [x] 新增能力库人类导览和按目标快速找入口，让用户理解 565 技能 / 58 大类覆盖范围 — 2026-06-29（详情可见 LOG.md）
- [x] 导入 34 个许可证明确的 OpenAI 官方 plugin skill，能力库扩展到 557 技能 / 58 大类 — 2026-06-28（详情可见 LOG.md）
- [x] 新增 6 个前端 UI / 后端 API 通用 `ours` 技能，能力库扩展到 523 技能 / 58 大类 — 2026-06-28（详情可见 LOG.md）
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

## Loop Record · 2026-06-28 · frontend-backend-foundation-skills

- Goal: 补强前端 UI 与后端 API 的高频基础工程技能，让真实项目开发时能路由到设计系统、状态数据流、性能、认证授权、事务一致性和 API 可观测性。
- Acceptance Criteria: 新技能是通用 `ours`；frontmatter 只有 `name` / `description`；manifest、README、skills README、TIERS、路由矩阵和四态系统计数一致；不引入项目定制、私有路径或敏感信息。
- Validation Evidence: 已通过新增 skill frontmatter 校验、manifest 计数校验（523 winners / 通用 474 / 半通用 49 / 58 domains / frontend-ui 30 / backend-api 28）、README 表格求和校验（523）、密钥模式扫描和 `git diff --check`；旧口径扫描只命中历史日志/历史 Loop Record 与合并历史说明。
- Self-Audit: 本轮不继续扩大新领域数量，而是补核心开发链路短板；新增 6 个技能均不绑定具体框架，适合作为真实项目的基础路由。
- Repairs: 收敛 manifest 噪音，只保留 6 个新增 WIN 行，避免生成器顺序漂移和外部来源路径问题污染 diff。
- State/Docs Sync: 已同步 README、skills README、routing、TIERS、REQ/LOG/MEMORY/PROGRESS。
- Commit: 待验证通过后使用 `feat: enrich frontend and backend skills`。
- Next Goal: 在真实前后端项目中 dogfood 新 skill 的触发质量，并继续补数据科学、法务、HR、教育、创意制作、行业知识和本地化等薄弱领域。
- Stop Reason: 本轮是单一范围的能力库补强；验证和 commit 后停止，不自动 push。

## Loop Record · 2026-06-28 · openai-plugin-skill-import

- Goal: 从 OpenAI 官方 `openai/plugins` 中合并一批可开源再分发、真实项目高频可用的 Codex plugin skill。
- Acceptance Criteria: 只导入许可明确的 skill；不重复导入已有 slug；归入 `codex` 来源层；保留 bundled resources 与 provenance；frontmatter 归一化为 `name` / `description`；manifest、README、skills README、TIERS、routing 和四态计数一致。
- Validation Evidence: 已通过 manifest 计数校验（557 winners / 通用 474 / 半通用 83 / 58 domains / codex 271）、新增 34 个 skill frontmatter 与 quick_validate 校验、README 表格求和校验（557）、高置信密钥扫描和 `git diff --check`；宽松密钥扫描只命中占位符、变量名和已有 Cloudflare/Netlify 示例。
- Self-Audit: `openai/plugins` 根目录没有统一 LICENSE，因此只导入 Render、Expo、Airtable、Supabase/Postgres 中有明确 MIT 许可声明的 34 个 skill；跳过已存在的 `render-deploy` 和许可不明确的大量官方 plugin skill。
- Repairs: 移除官方 skill frontmatter 中 validator 不接受的 `license`、`version`、`metadata`、`compatibility` 等字段，把许可与来源移入 provenance。
- State/Docs Sync: 已同步 README、skills README、routing、TIERS、provenance、REQ/LOG/MEMORY/PROGRESS。
- Commit: 待验证通过后使用 `feat: import licensed openai plugin skills`。
- Next Goal: 继续审计 GitHub、Notion、Cloudflare、Vercel、Netlify 等官方插件是否有明确可再分发许可，并在真实项目中 dogfood Render/Expo skill 触发质量。
- Stop Reason: 本轮只做许可明确的官方子集导入；更大规模导入需要逐插件许可审计。

## Loop Record · 2026-06-28 · app-miniprogram-skill-expansion

- Goal: 补强 App 开发与小程序项目级通用技能，让真实移动端项目能路由到架构、离线同步、推送、发布、小程序登录支付和跨端适配能力。
- Acceptance Criteria: 新技能是通用 `ours`；frontmatter 只有 `name` / `description`；不重复已有框架/厂商技能；manifest、README、skills README、TIERS、routing 和四态计数一致；不引入项目定制、私有路径或敏感信息。
- Validation Evidence: 已通过 manifest 计数校验（565 winners / 通用 482 / 半通用 83 / 58 domains / mobile-crossplatform 37 / ours 42）、新增 8 个 skill quick_validate 校验、README 表格求和校验（565）、密钥模式扫描和 `git diff --check`。
- Self-Audit: 本轮没有继续堆 Flutter/React Native/uniapp 入口，而是补 App / 小程序真实项目更常见的横切工程能力；这些能力可和已有框架技能组合使用。
- Repairs: 新增 8 个 `mobile-crossplatform/ours` 技能，并把路由代表技能改为优先显示项目级骨架能力。
- State/Docs Sync: 已同步 README、skills README、routing、TIERS、REQ/LOG/MEMORY/PROGRESS。
- Commit: 待验证通过后使用 `feat: add app and miniprogram skills`。
- Next Goal: 在真实 App / 小程序项目中 dogfood 新 skill 的触发质量，并继续补移动端测试、埋点分析、地图定位、媒体上传等细分能力。
- Stop Reason: 本轮是单一范围的移动端/小程序能力补强；验证和 commit 后停止，不自动 push。

## Loop Record · 2026-06-28 · global-commit-closure

- Goal: 把“完成可验证修改后默认进入原子 commit 闭环”同步到所有 agent 入口、初始化模板、workflow core 和相关 git/commit skills。
- Acceptance Criteria: Codex、Claude Code、`.agents` 全局入口和母仓源文件都不再只写“倾向/允许 commit”；启动模板和 adapters 要求多逻辑变更拆成多个 commit；commit/git skills 不再鼓励 `git add .` / `git add -A` 粗暴暂存；push/merge/PR 仍需用户明确要求。
- Validation Evidence: 已执行旧弱规则扫描（无 `默认倾向` / `prefer an atomic commit` / `After a validated single-scope change` 残留）、危险 stage 示例扫描（`git add .` / `git add -A` 仅保留在禁止/反例语境）、commit closure 关键词扫描、`git diff --check`（仅 Windows LF/CRLF 提示）和 Git diff/stat 检查。
- Self-Audit: 本轮只调整通用工作流纪律和镜像同步，不引入项目定制 skill；第三方来源技能尽量不扩大改动，只修会误导提交纪律的通用技能文档。
- Repairs: 已把弱表述“prefer / 符合条件时 / 单一逻辑才默认”替换为“完成可验证修改后进入 commit 闭环；多逻辑变更拆分”；同步本机 `.agents` 与 `.codex` 技能镜像。
- State/Docs Sync: 已同步 README、REQ、MEMORY、LOG、PROGRESS，并更新本 Loop Record。
- Commit: 待验证通过后使用 `docs: enforce atomic commit closure`。
- Next Goal: 在真实项目初始化和持续推进场景中 dogfood，确认 Codex/CC 是否会自动拆分提交并记录无法提交原因。
- Stop Reason: 本轮目标是规则源头与本机镜像同步；验证和 commit 后停止，不自动 push。

## Loop Record · 2026-06-29 · global-project-discovery-interview

- Goal: 把“初始化项目先分类；空目录/新想法先多轮需求访谈；已有项目后补 workflow 先扫描恢复”固化为工作流模式。
- Acceptance Criteria: `project-inception-docs` 包含 Project Classification Gate 与 Discovery Interview；新增访谈 reference；核心 workflow、README、启动模板和四态系统同步；本机全局入口与技能镜像同步；验证通过后原子 commit。
- Validation Evidence: 已执行 Project Classification / Discovery Interview / project-discovery-interview 关键词扫描、全局入口命中检查、本机 `.agents` 与 `.codex` 技能镜像存在检查、`project-inception-docs` frontmatter 轻量校验、项目定制词扫描和 `git diff --check`（仅 Windows LF/CRLF 提示）。
- Self-Audit: 本轮只改变通用初始化流程，不引入具体“表情包小程序”项目定制内容；示例问题保持通用角色框架，避免污染开源技能库。
- Repairs: 已新增访谈 reference，并将“初始化项目”从单步写文件动作改为分类门禁 + 访谈门禁 + 地基/文档生成门禁。
- State/Docs Sync: 已同步 README、REQ、MEMORY、LOG、PROGRESS、本机全局入口和 `.agents` / `.codex` 技能镜像。
- Commit: 待验证通过后使用 `docs: add project discovery interview workflow`。
- Next Goal: 在真实空目录项目中 dogfood，确认 agent 会先提问并在用户确认后再初始化文档和地基。
- Stop Reason: 本轮目标是工作流规则源头与模板同步；验证和 commit 后停止，不自动 push。

## Loop Record · 2026-06-29 · skill-catalog-discoverability

- Goal: 让用户不用阅读 565 个 skill slug，也能理解能力库有哪些领域、适合哪些任务、该从哪里进入。
- Acceptance Criteria: 根 README 有按目标快速找能力；新增 `skills/CATALOG.md` 覆盖主要场景、领域地图和常用触发说法；`skills/README.md` 顶部指向导览、完整索引、TIERS 和 manifest；四态系统同步。
- Validation Evidence: 已通过 `skills/CATALOG.md` / `skills/README.md` / `skills/TIERS.md` / `_merge-manifest.csv` 链接存在检查、能力库导览关键词覆盖扫描、README 入口片段检查和 `git diff --check`（仅 Windows LF/CRLF 提示）。
- Self-Audit: 本轮只增强文档可发现性，不改变技能数量、manifest、路由规则或技能内容；避免在根 README 展开过长 slug 列表。
- Repairs: 新增人类导览层，把“数量表”前置补成“按目标找能力”。
- State/Docs Sync: 已同步 README、skills README、CATALOG、REQ、MEMORY、LOG、PROGRESS。
- Commit: 待验证通过后使用 `docs: add skill catalog guide`。
- Next Goal: 后续可考虑从 manifest 自动生成 CATALOG 的场景表，降低手工同步成本。
- Stop Reason: 本轮目标是文档可发现性改造；验证和 commit 后停止，不自动 push。

## Loop Record · 2026-06-29 · third-party-source-flattening

- Goal: 不在公开能力库导览里单独高亮第三方授权包的商业来源，把已授权导入内容按领域并入通用 `community` 展示层。
- Acceptance Criteria: `skills/` 下不再存在旧第三方来源目录；`skills/README.md` 来源表只展示 `ours / codex / community`；manifest 仍保持 565 winners / 58 domains；公开 README、架构、路由和工具说明不再出现旧来源标签或商业属性展示口径；provenance 和内部审计资料保留来源可追溯。
- Validation Evidence: 已通过目录残留扫描（旧第三方来源目录为 0）、manifest 计数校验（565 winners / 58 domains / codex 271 / community 252 / ours 42）、公开口径扫描（README、skills README、ARCHITECTURE、framework、merge README 无旧来源标签或商业属性命中）、skills README 来源统计扫描和 `git diff --check`（仅 Windows LF/CRLF 提示）。
- Self-Audit: 本轮只调整来源分层和公开展示，不删除技能内容、不改变 skill 触发语义；授权来源不在公开入口突出，但 provenance 仍保留用于审计。
- Repairs: 将 17 个领域下的旧第三方来源目录移动到同领域 `community/`，并把合并工具的可选外部来源变量改为中性 `PAW_EXTERNAL_SKILLS_*`。
- State/Docs Sync: 已同步 README、skills README、ARCHITECTURE、routing、merge tools、REQ/LOG/MEMORY/PROGRESS。
- Commit: 待验证通过后使用 `chore: flatten third party skill sources`。
- Next Goal: 后续可继续让 `skills/CATALOG.md` 从 manifest 自动生成，减少手工维护来源/领域表的成本。
- Stop Reason: 本轮目标是来源展示收敛；验证和 commit 后停止，不自动 push。
