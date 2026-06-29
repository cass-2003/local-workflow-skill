# 项目日志 · Project Log

> 日志系统：回答“最近发生了什么”。追加新条目在最上方，重要决策同步到 `MEMORY.md`。

---

## 2026-06-29

- `change` 将第三方授权来源统一并入 `community` 展示层，避免公开导览单独高亮商业来源。
  - 触发：用户指出第三方授权来源在能力库 README 中写得过于明显，不应单独分离展示。
  - 范围：移动 17 个领域下的旧来源目录到同领域 `community/`；更新 manifest、skills README、根 README、架构、路由、合并工具说明与四态系统。
  - 验证：待执行目录残留扫描、manifest 计数、公开口径扫描、README 来源统计和 `git diff --check` 检查。

- `docs` 增强能力库可发现性，让用户按场景理解 565 个技能覆盖什么。
  - 触发：用户指出 README 的能力库段落只有数量表，不知道有哪些类型、分类和领域的 skill。
  - 范围：新增 `skills/CATALOG.md` 人类导览版目录；根 README 增加“按目标快速找”；`skills/README.md` 顶部增加导览入口和常用问法。
  - 验证：待执行链接存在、关键词覆盖、README 表格和 `git diff --check` 检查。

- `change` 为项目初始化加入分类门禁与多轮需求访谈模式。
  - 触发：用户希望新建目录后说“初始化项目”时，agent 先询问想做什么，并按用户端、租户端、管理端、授权端等角色多轮收集需求；已有项目后补 workflow 时则先扫描和恢复现状。
  - 范围：新增 `project-discovery-interview.md`，更新 `project-inception-docs`、核心 workflow、README、启动模板和四态系统。
  - 验证：关键词覆盖、模板同步、全局入口命中、frontmatter 校验和 `git diff --check` 均已完成；diff check 仅有 Windows LF/CRLF 提示。

## 2026-06-28

- `change` 加硬跨 agent commit 闭环纪律，要求可验证修改默认进入原子 commit。
  - 触发：用户指出规则不应只改 Codex，所有 agent 入口和技能源头都要同步。
  - 范围：同步 Codex/Claude/`.agents` 全局入口、母仓 `AGENTS.md` / `CLAUDE.md`、workflow core、Codex/Claude adapters、启动模板、`project-inception-docs`、commit/git 相关技能和本机技能镜像。
  - 验证：检查关键规则命中、旧弱表述和 `git add .` / `git add -A` 残留；执行 `git diff --check` 与 Git 状态检查。

- `change` 补强 App 开发与小程序通用工程技能，能力库推进到 565 技能 / 58 大类。
  - 触发：用户希望多加一些 app 开发、小程序之类的 skill。
  - 范围：新增 8 个 `mobile-crossplatform/ours` 技能，覆盖 App 架构、离线同步、推送通知、发布运营、小程序架构、微信小程序工程、登录支付闭环、Taro/uniapp 跨端工程。
  - 验证：同步 manifest、README、skills README、TIERS、路由矩阵和四态系统；执行 frontmatter、quick_validate、计数、README 表格求和、密钥模式和 `git diff --check` 校验。

- `change` 合并一批 OpenAI 官方 plugins 中许可证明确的 Codex skill，能力库推进到 557 技能 / 58 大类。
  - 触发：用户要求定 goal，合并官方的一些 Codex skill。
  - 范围：从 `openai/plugins` 筛选 34 个明确 MIT 许可的 skill，导入 Render、Expo、Airtable 与 Supabase/Postgres；跳过已存在的 `render-deploy` 和根仓库未声明许可的插件内容。
  - 验证：保留 provenance；规范 frontmatter 为 `name` / `description`；同步 manifest、README、skills README、TIERS、路由矩阵和四态系统；执行计数、frontmatter、密钥模式和 `git diff --check` 校验。

- `change` 补强前端 UI 与后端 API 的通用基础工程技能，能力库推进到 523 技能 / 58 大类。
  - 触发：用户指出前端 UI、后端等核心开发领域还需要继续丰富，避免能力库只在安全/逆向/通用工程上强。
  - 范围：新增 6 个 `ours` 技能：`design-system-implementation`、`frontend-state-data-flow`、`frontend-performance`、`auth-access-control`、`database-transaction-consistency`、`api-error-observability`。
  - 验证：同步 manifest、README、skills README、TIERS、路由矩阵和四态系统；执行 frontmatter、计数、旧口径残留、密钥模式和 `git diff --check` 校验。

- `change` 第二批扩容 community 技能，把能力库推进到 517 技能 / 58 大类。
  - 触发：用户要求 README 与能力库继续丰富，并明确至少覆盖 50 个领域大类；同时参考 Codex/OpenAI skill 规范和开源 skill 库。
  - 范围：继续从 MIT 许可 `alirezarezvani/claude-skills` 筛选 78 个通用技能，新增 SEO、内容策略、文案编辑、付费获客、邮件营销、增长实验、品牌策略、合规质量、研究学习、个人生产力、客户成功、收入运营、销售赋能、组织管理、Markdown 发布等领域。
  - 验证：README、skills README、TIERS、路由矩阵、manifest 和 provenance 已同步到 517 / 58；community frontmatter 统一为 `name` / `description`；已执行计数、大类、frontmatter、密钥模式和 `git diff --check` 校验。

- `change` 首批扩容 community 技能，降低能力库领域偏重。
  - 触发：用户指出当前能力库领域不够丰富，安全/逆向/工程偏重明显，需要从开源 skill 库补充其他领域。
  - 范围：从 MIT 许可 `alirezarezvani/claude-skills` 筛选 30 个通用技能，新增业务运营、商业策略、财务指标、产品管理、项目管理、研究运营 6 个领域；跳过 router/index、私有上下文和偏角色扮演的 executive persona。
  - 验证：新增 provenance 记录，规范 community `SKILL.md` frontmatter，更新 README、skills README、路由矩阵、TIERS、NOTICE、manifest，并执行结构/许可/计数校验。

## 2026-06-27

- `change` 开源化项目初始化与工作流自检工具，并降低启动四态模板的占位债。
  - 触发：审计发现关键初始化/刷新能力仍停留在本机脚本，启动模板 `state/` 仍有大量 `<...>` 占位，和“占位不能当记忆”的新契约冲突。
  - 验证：新增 `tools/project-init/Initialize-PortableAgentProject.ps1` 与 `Validate-PortableAgentWorkflow.ps1`；运行完整自检与初始化器烟测通过，确认 `AgentEntriesOnly` 会保留项目专属段且不初始化 Git / `.gitignore`。

- `change` 加强状态恢复与循环记录契约，避免项目初始化后仍然跨 agent 失忆。
  - 触发：用户在 `J:\协作`、`J:\novels\novel-factory`、`J:\无界画布-AI视觉工作台`、`J:\视频工作流` 等已初始化项目中测试发现，入口文件存在但日志/记忆/进度不总是自动触发。
  - 验证：核心 `01/02/08`、Codex/Claude 适配器、启动模板 `AGENTS.md` / `CLAUDE.md`、`project-workflow` 和 README 均补入 `State Restore` 摘要与 `Loop Record` 要求；后续用刷新脚本同步到本机和样例项目。

- `change` 新增自主项目推进循环，要求先做初始项目规划，再按工作包循环实现、验证、自审、修复、同步和提交。
  - 触发：用户反馈工作流使用时 agent 容易停下，希望它能自己定 goal、完成一段后自动审计、修复并继续推进项目。
  - 验证：新增 `framework/core/08-autonomous-project-loop.md`，并接入核心索引、路由矩阵、验证闸门、产物契约、仓库入口、适配模板、`project-workflow` 和 `project-inception-docs` 启动模板。

- `docs` 在 README 增加“自动产物契约”独立小节。
  - 触发：用户确认 README 需要把审计报告、状态回写和文档索引同步规则写得更明显。
  - 验证：新增小节链接 `framework/core/07-artifact-contracts.md`，并列出 audit、implement/fix、docs-sync、validation 的默认产物与同步要求。

- `change` 加硬仓库根与适配模板入口的 Artifact Contracts 规则。
  - 触发：用户指出仅有核心 `07-artifact-contracts.md` 不够，`AGENTS.md` / `CLAUDE.md` 等入口也应直接约束智能体自动产物行为。
  - 验证：检查仓库根 `AGENTS.md` / `CLAUDE.md`、Codex / Claude 适配模板和本机全局入口均包含 Artifact Contracts 段，明确审计写 `docs/audit/`、实现/修复回写 `state/LOG.md` 与 `state/PROGRESS.md`、文档变更更新索引。

- `change` 新增工作流产物契约，要求审计、验收、实现、修复、验证和文档同步留下可发现文件产物。
  - 触发：用户指出当前工作流不会像 J-SOP 样板项目一样自动审计、自动产出报告和同步日志/索引。
  - 验证：新增 `framework/core/07-artifact-contracts.md`，更新核心入口、适配模板、`project-workflow`、`project-inception-docs` 和启动模板；用临时项目烟测确认初始化会生成 `docs/audit/INDEX.md` 与 `docs/audit/TEMPLATE-GLOBAL-AUDIT.md`。

## 2026-06-26

- `change` 清理项目定制 skill，并把能力库同步为开源通用口径：409 技能、18 大类、项目定制 0。
  - 触发：用户确认本仓库要做成通用开源仓库，而不是携带个人/项目定制 skill。
  - 验证：同步 manifest、README、路由表、分级脚本、开源治理文件与四态系统，并执行一致性/敏感信息扫描。

- `change` 补齐 README 对新项目地基门禁的说明，并增强启动模板 README 的地基状态表。
  - 触发：检查发现根 README 尚未同步 Git 初始化、忽略文件、Agent 入口和首次提交规则。
  - 验证：检查 README 关键词覆盖、skill 校验、diff check 与 Git 提交闸门。

- `change` 强化项目启动地基门禁，要求新项目先补 Git、忽略文件、agent 入口、四态系统、文档索引和验证入口。
  - 触发：用户要求每个项目初始时，如果没有 Git 等基础设施就先初始化，把项目地基打好。
  - 验证：运行 skill frontmatter 校验、模板路径/关键词检查、diff 检查与 Git 提交闸门。

- `change` 按用户授权从 `Coff0xc/coffee-skill` 原位更新 18 个 Coff0xc 技能，并保存 LICENSE/NOTICE/manifest 来源记录。
  - 触发：用户希望把授权的 Coffee skill 纳入本地能力库。
  - 验证：检查 18 个目录文件数、frontmatter 名称归一化、skill quick_validate、来源记录位置和 Git diff。

- `change` 从真实项目文档集抽取标准启动文档包，并沉淀为 `project-inception-docs` 的 reference 与模板资产。
  - 触发：需要把真实项目中验证过的多文档结构转成可复用模板，支持新项目从想法自动生成文档包。
  - 验证：运行 skill frontmatter 校验、模板路径枚举、链接与占位检查。

- `change` 扩展 `project-inception-docs` 为项目启动文档包技能，并同步当时的能力库索引。
  - 触发：需要在项目起步时从想法自动生成 README、PRD、页面/信息架构、技术架构、数据模型、API、AI/Prompt 工作流、路线图、测试验收、部署运维、安全合规、迁移清单与四态系统。
  - 验证：运行 skill frontmatter 校验、一致性搜索、diff 检查与 manifest 计数检查。
