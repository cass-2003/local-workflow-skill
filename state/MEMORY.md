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

## 已知坑

- `quick_validate.py` 不接受 `disable-model-invocation`、`user-invocable` 等旧 frontmatter 字段；新增或更新 skill 时只保留允许字段。
- `Import-Csv` 读取中文 CSV 时可能出现列名/编码异常；manifest 计数可用文本行过滤或显式编码方式复核。
