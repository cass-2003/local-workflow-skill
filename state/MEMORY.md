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

## 已知坑

- `quick_validate.py` 不接受 `disable-model-invocation`、`user-invocable` 等旧 frontmatter 字段；新增或更新 skill 时只保留允许字段。
- `Import-Csv` 读取中文 CSV 时可能出现列名/编码异常；manifest 计数可用文本行过滤或显式编码方式复核。
- `assets/templates/startup-docs/` 是输出资产，可以包含要复制到目标项目的 `README.md`；这不违反 skill 根目录不放杂项 README 的约束。
- `coffee-skill` 上游 `SKILL.md` 的 frontmatter `name` 是 `coff0xc-*`；导入到本仓库时必须归一化为本地目录 slug，否则 `quick_validate.py` 会失败。
- 对已有 Git 仓库只读状态并补缺口；不要把已有项目重新 `git init`，也不要覆盖 remote、分支或历史。
