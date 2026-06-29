# 项目记忆 · Project Memory

> 记忆系统：回答“系统为什么这样设计、有哪些已知知识”。

---

## 架构与系统地图

- 本仓库维护四态工作流中立核心、适配器模板与能力库技能；`framework/core/` 是流程真相源，`skills/workflow-orchestration/ours/` 承载可被 agent 调用的工作流技能。
- `project-workflow` 是通用编排入口；`project-inception-docs` 是项目起步时从想法生成文档包和状态骨架的执行技能。

## 关键决策

### D-001 · 项目启动文档包采用分层生成

- **决定**：`project-inception-docs` 默认先生成核心包，按项目复杂度扩展工程实施包和治理迁移包。
- **为什么**：截图中的旧项目需要接近 19 个 Markdown 文档，但所有项目无条件生成全量文档会制造空壳和维护噪音。
- **影响**：后续 agent 应根据用户需求、旧项目资料和团队协作规模决定生成范围，并维护 `docs/INDEX.md` 作为入口。
- **时间**：2026-06-26

### D-002 · 本仓库自身使用四态系统

- **决定**：在仓库根新增 `state/LOG.md`、`state/REQUIREMENTS.md`、`state/MEMORY.md`、`state/PROGRESS.md`。
- **为什么**：本仓库是全局工作流母仓，如果自身不恢复状态，会和 Four-State Workflow 的默认纪律冲突。
- **影响**：后续重要技能、规则、计数、验证和交付变化应同步写入 `state/`。
- **时间**：2026-06-26

### D-003 · 启动文档模板采用分域目录

- **决定**：从一个真实项目文档集抽取标准模板时，保留 `docs/INDEX.md` + `docs/architecture/` + `docs/api/` + `docs/planning/` + `docs/testing/` + `docs/operations/` + `references/` + `state/` 的分域结构。
- **为什么**：真实样板证明扁平多文档容易膨胀，分域目录更利于首次阅读、开发接手、验收和运维。
- **影响**：后续 `project-inception-docs` 生成完整启动包时应优先使用该目录结构，而不是把所有 Markdown 平铺到 `docs/`。
- **时间**：2026-06-26

### D-004 · Coffee skill 授权导入采用原位更新

- **决定**：授权导入 `Coff0xc/coffee-skill` 时，不新增重复来源层，而是原位更新已存在的 18 个规范化 Coff0xc 技能目录，并保留本仓库 slug。
- **为什么**：这些技能此前已以去前缀形式存在于能力库；新增一套 `coffee/` 来源会造成重复触发和计数膨胀。
- **影响**：触发和索引仍使用现有 slug；上游授权、LICENSE、NOTICE、manifest 和映射记录放在 `tools/skill-merge/provenance/coffee-skill/`。
- **时间**：2026-06-26

### D-005 · 新项目先过地基门禁

- **决定**：新项目、空目录或首次接入 workflow 时，先检查并补齐 Git、`.gitignore`、agent 入口、四态系统、README、`docs/INDEX.md` 和验证命令，再进入业务开发。
- **为什么**：项目一旦跳过地基，后续日志、需求、验证、commit 和多 agent 接手都会失去稳定落点。
- **影响**：`project-inception-docs` 和核心工作流都应默认执行地基检查；没有 `.git/` 且不在父级仓库中时可默认 `git init`，但不默认 push、配置远端或改写已有历史。
- **时间**：2026-06-26

### D-006 · 开源仓库不携带项目定制 skill

- **决定**：本仓库定位为通用开源工作流与技能库，`skills/` 只保留通用或半通用能力；强绑具体项目、产品、旧命令封装或私有上下文的 skill 从公开库移除。
- **为什么**：项目定制 skill 会污染路由、泄露上下文，并让开源用户无法判断哪些能力可复用。
- **影响**：项目专属 skill 应保存在目标项目本地 `.codex/skills`、`.claude/skills`、`.agents/skills` 或私有仓库；本仓库只保留可迁移模板和通用 workflow。
- **时间**：2026-06-26

### D-007 · 审计与同步必须留下可发现产物

- **决定**：新增 `framework/core/07-artifact-contracts.md` 作为审计、验收、验证、文档同步和状态同步的默认产物契约；新项目模板默认带 `docs/audit/INDEX.md` 与 `docs/audit/TEMPLATE-GLOBAL-AUDIT.md`。
- **为什么**：真实项目中稳定的审计报告、索引、日志和计划文件能让 agent 自动恢复上下文，而只停留在对话里的结论无法跨会话复用。
- **影响**：后续 `audit` / `acceptance` 默认写报告并更新索引；`implement` / `fix` 默认同步 `state/LOG.md` 与 `state/PROGRESS.md`；文档结构变化默认同步 `docs/INDEX.md`。
- **时间**：2026-06-27

### D-008 · 持续推进前先做项目规划，再进入自主循环

- **决定**：新增 `framework/core/08-autonomous-project-loop.md`，把“继续推进项目”类请求定义为：先确认或生成路线图和下一步工作包，再按单一工作包循环执行、验证、自审、修复、同步和提交。
- **为什么**：仅有 10 阶段 checklist 会让 agent 完成一个局部动作后自然停下；真实项目推进需要先判断阶段、拆目标、定义验收标准，并把自审缺口转成下一轮目标。
- **影响**：`project-workflow` 新增 `autonomous-loop` / `planning` 路由；新项目模板新增 `docs/planning/下一步工作包.md`，并增强 `state/PROGRESS.md` 的 Active Goal / Current Loop / Next Candidate Goals。
- **时间**：2026-06-27

### D-009 · 状态恢复与循环记录成为运行时契约

- **决定**：开工前必须形成 `State Restore` 摘要，收工前必须写入 `Loop Record`；占位状态不能视为有效记忆。
- **为什么**：真实项目测试显示，初始化过 `AGENTS.md` / `CLAUDE.md` 和 `state/` 仍不足以保证 agent 自动读写记忆；必须把“读了什么、写了什么、下一步是什么”变成可检查产物。
- **影响**：核心、适配器、启动模板和 `project-workflow` 技能都要求识别占位/陈旧状态，并把自主循环的目标、验收、验证、自审、修复、同步、commit 和停止原因写回项目状态。
- **时间**：2026-06-27

### D-010 · 项目初始化器进入开源仓库

- **决定**：把本机项目初始化/入口刷新能力沉淀到 `tools/project-init/`，并提供 `Validate-PortableAgentWorkflow.ps1` 自检脚本。
- **为什么**：桌面面板和本机脚本已成为真实项目接入 workflow 的关键路径；若不进入仓库，其他环境无法复现，也无法用 Git 审计和测试防回归。
- **影响**：后续项目接入优先使用仓库内脚本；本机桌面面板只是包装层。入口刷新默认替换托管块并保留项目专属内容。
- **时间**：2026-06-27

### D-011 · 第三方开源 skill 使用 community 来源层

- **决定**：许可清晰的第三方开源 skill 不放入 `ours`，统一放入 `skills/<domain>/community/<skill>/`，并保存 provenance。
- **为什么**：`ours` 应表示本仓库原创或维护的技能；community 能清晰表达第三方导入，避免来源、版权和后续更新责任混淆。
- **影响**：去重优先级为 `ours > codex > community`；community 用来补覆盖缺口，不覆盖已有更权威的本地技能。
- **时间**：2026-06-28

### D-012 · 领域扩容采用细粒度大类而非继续堆工程类

- **决定**：为满足 50+ 领域覆盖，优先新增营销、合规、研究、学习、生产力、销售、组织管理和发布类细粒度大类，而不是继续把所有非工程技能塞进少数宽泛目录。
- **为什么**：用户目标是让能力库在真实项目、运营、内容、合规和协作场景中更均衡可路由；过粗分类会让隐式触发和二级路由不稳定。
- **影响**：`framework/core/03-routing.md` 需要用分组行概括长尾领域；具体选择仍以 `skills/README.md` 和各技能 `description` 为准。
- **时间**：2026-06-28

### D-013 · 高频核心工程缺口优先沉淀为 ours

- **决定**：当前端 UI、后端 API、数据流、认证、事务、可观测性等高频工程缺口没有足够明确的本仓库技能时，优先补充为 `ours`，前提是内容通用、非项目定制、可跨框架复用。
- **为什么**：community 导入适合扩领域宽度，但核心开发流程需要可维护、可审计、可按本仓库工作流演进的基础技能；这些技能会被真实项目频繁路由。
- **影响**：新增核心技能时保持 `SKILL.md` 精简、frontmatter 只有 `name` / `description`，并同步 manifest、索引、路由、分级和四态系统。
- **时间**：2026-06-28

### D-014 · 官方插件技能也必须逐项验许可

- **决定**：从 OpenAI 官方 `openai/plugins` 导入 skill 时，不按根仓库整体默认许可处理；只导入 skill frontmatter、插件 README 或插件 LICENSE 明确 MIT/Apache 等可再分发许可的子集。
- **为什么**：`openai/plugins` 根目录没有仓库级 LICENSE；官方来源能证明出处，但不能替代开源再分发许可判断。
- **影响**：OpenAI plugin skill 统一进入 `codex` 来源层，保留 provenance；未声明许可、过度垂直或已存在的 skill 只作为参考，不原样导入。
- **时间**：2026-06-28

### D-015 · 移动端补项目级骨架优先于继续堆框架名

- **决定**：App / 小程序能力扩容优先补 `ours` 通用工程骨架，如架构、离线同步、推送、发布运营、登录支付和跨端适配，而不是继续重复 Flutter、React Native、uniapp、微信小程序等框架名技能。
- **为什么**：现有库已有多种框架/平台入口；真实项目更缺的是能把需求落到可维护工程结构、发布流程和平台约束的项目级技能。
- **影响**：后续移动端扩容应先看 `mobile-crossplatform/ours` 是否已有横切能力，再补厂商/框架细节；新增 skill 仍保持 `SKILL.md` 精简、frontmatter 只有 `name` / `description`。
- **时间**：2026-06-28

### D-016 · Commit 闭环是跨 agent 默认交付纪律

- **决定**：Codex、Claude Code、共享 `.agents` 入口、项目初始化模板、核心 workflow 和 git/commit skills 都采用同一条规则：在 Git 仓库内完成可验证修改后默认必须创建原子 commit；多逻辑变更拆成多个 commit。
- **为什么**：仅写“倾向/允许原子 commit”会让不同 agent 在完成修改后停在未提交状态，破坏跨会话恢复、审计和多人协作。
- **影响**：后续入口和技能不得把 commit 写成可选建议；阻塞 commit 时必须说明原因和下一步。push、merge、PR 和历史改写仍需要用户明确要求。
- **时间**：2026-06-28

### D-017 · 初始化项目先分类，空项目先访谈

- **决定**：把“初始化项目”定义为项目启动流程入口，而不是立即写模板文件。Agent 必须先区分空目录新想法、半初始化项目、已有项目后补 workflow、明确想法输入和直接地基请求。
- **为什么**：真实使用中，用户新建目录后说“初始化项目”往往还没有完整需求；如果 agent 直接生成 PRD/docs/state，会把臆测写成项目事实，后续跨 agent 协作会继承错误上下文。
- **影响**：`project-inception-docs` 新增 Discovery Interview reference；空目录/新想法默认先按角色多轮提问，已有项目默认先 scan + State Restore。只有用户确认、需求足够清晰或允许未知项标 `待确认` 时，才生成完整文档和地基。
- **时间**：2026-06-29

### D-018 · 能力库入口采用“场景导览 + 完整索引”双层结构

- **决定**：根 README 不再只展示技能数量表，而是先提供按用户目标查找的能力导览；完整 slug 和来源细节留在 `skills/README.md`，人类可读能力地图放在 `skills/CATALOG.md`。
- **为什么**：565 个技能和 58 个领域对新用户是噪音；用户需要先知道“我想做小程序/后端/API/安全/增长时该看哪里”，再进入完整索引。
- **影响**：新增或调整大类时，后续要同步 `skills/CATALOG.md` 的场景导览、根 README 的速查表、`skills/README.md` 的完整索引和四态记录。
- **时间**：2026-06-29

### D-019 · 第三方授权来源统一并入 community 展示层

- **决定**：不再在公开 README、领域索引和目录结构里单独展示第三方授权包的原始来源标签；已导入内容统一落到 `skills/<domain>/community/<skill>/`。
- **为什么**：公开能力库应强调领域能力和授权清晰，而不是把某个授权来源的商业属性单独高亮；具体许可和来源仍通过 provenance / manifest 保持可审计。
- **影响**：来源层收敛为 `ours / codex / community`；合并工具可选外部来源使用 `PAW_EXTERNAL_SKILLS_*`，输出仍归入 community；新增授权来源时不得在用户导览中制造新的来源孤岛。
- **时间**：2026-06-29

### D-020 · 生产 UI 图标必须使用矢量图标体系

- **决定**：UI / 设计系统任务中，emoji 不得作为生产图标、导航图标、状态标记、工具栏控件或空状态插画；必须使用项目现有 SVG/vector icon system，或统一选择 Lucide、Tabler、Heroicons、Phosphor、Fluent Icons 等矢量图标库。
- **为什么**：emoji 在不同平台的渲染、尺寸、对齐、语义和品牌一致性不可控，容易让正式界面显得廉价且不稳定。
- **影响**：`UIdesign`、UI quality checklist、research synthesis 和 `design-system-implementation` 都把 icon system 纳入实现与验收；后续 UI 交付要检查图标来源、风格、stroke/fill、尺寸、可访问名称和打包体积。
- **时间**：2026-06-29

### D-021 · 中文对照表作为能力库人类检索层

- **决定**：`skills/DOMAIN-GLOSSARY.zh-CN.md` 承载 58 个领域大类与 566 个 winner skill slug 的中文参考名，作为用户审阅目录结构和查找技能的入口。
- **为什么**：`skills/README.md` 和 `_merge-manifest.csv` 适合机器/维护者使用，但大量英文 slug 对中文用户不够直观；只列大类也不足以判断具体能力是否覆盖。
- **影响**：后续新增、删除、合并或移动 skill 时，需要同步中文对照表；中文参考名只服务人工检索，不替代每个 `SKILL.md` 的 description、触发条件和执行边界。
- **时间**：2026-06-29

### D-022 · “继续推进”需要可调用的目标驱动循环 skill

- **决定**：新增 `skills/workflow-orchestration/ours/goal-driven-project-loop/SKILL.md`，把“State Restore -> 小目标 -> 读文件 -> 实现 -> 验证 -> 自审/修复 -> docs/state/Loop Record -> 原子 commit -> 下一目标”固化为多 agent 通用执行入口。
- **为什么**：`08-autonomous-project-loop.md` 是 core 真相源，但真实触发时还需要一个具体 skill 名称承接“你继续推进”这类自然语言请求，否则容易只停在编排原则而缺少执行器。
- **影响**：`project-workflow` 和 `03-routing.md` 的 autonomous-loop 路由指向该 skill；core 仍是单一真相，后续修改循环原则先改 core，再同步 skill 的薄包装。
- **时间**：2026-06-29

## 已知坑

- `quick_validate.py` 不接受 `disable-model-invocation`、`user-invocable` 等旧 frontmatter 字段；新增或更新 skill 时只保留允许字段。
- `Import-Csv` 读取中文 CSV 时可能出现列名/编码异常；manifest 计数可用文本行过滤或显式编码方式复核。
- `assets/templates/startup-docs/` 是输出资产，可以包含要复制到目标项目的 `README.md`；这不违反 skill 根目录不放杂项 README 的约束。
- `coffee-skill` 上游 `SKILL.md` 的 frontmatter `name` 是 `coff0xc-*`；导入到本仓库时必须归一化为本地目录 slug，否则 `quick_validate.py` 会失败。
- 对已有 Git 仓库只读状态并补缺口；不要把已有项目重新 `git init`，也不要覆盖 remote、分支或历史。
- `tools/project-init/Initialize-PortableAgentProject.ps1 -AgentEntriesOnly` 只刷新 `AGENTS.md` / `CLAUDE.md` 托管块，不初始化 Git、不写 `.gitignore`、不覆盖 README/docs/state。
- community 导入需要同时更新 `tools/skill-merge/provenance/<source>/`、`skills/_merge-manifest.csv`、`skills/README.md`、`skills/TIERS.md` 和路由矩阵，否则后续 agent 会看到不一致的能力库地图。
- 第三方授权包的原始来源不要在公开导览里单独高亮；使用 `PAW_EXTERNAL_SKILLS_DIR` / `PAW_EXTERNAL_SKILLS_README` 作为可选导入入口，最终目录和索引统一归入 `community/`。
- `openai/plugins` 当前包含大量官方示例 plugin skill，但根仓库未提供统一 LICENSE；导入时要优先找插件目录 LICENSE、插件 README 许可段或 skill frontmatter `license` 字段。
- UI 任务若发现用 emoji 充当正式图标，应视为设计系统问题修复；只有聊天文本、文档示意或已有品牌规范明确要求时才可保留 emoji。
