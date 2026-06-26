# 工作流骨架（10 阶段）

定义一条适合多数项目的标准流程，让扫描、恢复、执行、验证、同步、交付有固定顺序。任何 Agent runtime 都按这套顺序推进。

## Phase 0 · Workspace Scan

- **目的**：看清仓库里有哪些规则、工作流、技能、文档、验证入口；避免带旧假设开工。
- **输出**：可能的权威层、可能的任务域、可能的验证入口。

## Phase 1 · State Restore

- **目的**：先恢复项目状态再行动。
- **动作**：至少寻找四态系统 —— 日志 / 需求 / 记忆 / 进度（见 `02-state-systems.md`）。
- **缺失处理**：若项目里还没有可承载四态系统的本地文件，先按模板初始化最小可用的四态骨架，再进入后续阶段；不要在"完全失忆"状态下直接开发。
- **输出**：最近发生了什么、当前目标与约束、已有知识与基线、当前进度与阻塞。

## Phase 2 · Intent Classification

- **目的**：判断任务更像 status / audit / implement / fix / review / docs-sync / git-delivery / evolution 中的哪一类。
- **输出**：主意图、次意图、初步范围。

## Phase 3 · Authority Resolution

- **目的**：判断该信任哪一层规则、哪一层技能、哪一层文档（见 `04-authority.md`）。
- **输出**：rules source / workflow source / execution source / truth-docs source / fallback chain。

## Phase 4 · Route & Delegate

- **目的**：让合适的执行能力承担合适的工作（见 `03-routing.md`）。
- **规则**：编排权保留在工作流层；执行细节优先委托给项目本地能力；无本地能力时才用最接近的全局兜底。

## Phase 5 · Execute

- **目的**：按任务类型完成分析、修改、修复、评审或同步。
- **规则**：先读后改；只做必要改动；明确区分事实、推断与假设。

## Phase 6 · Validation Gate

- **目的**：防止"完成只靠口头声明"（见 `05-validation.md`）。
- **输出**：已验证的内容、使用的命令或证据、未验证的部分及原因。

## Phase 7 · Docs & State Sync

- **目的**：让四态系统与当前成果一致。
- **常见触发**：实现了新功能 / 修复了已知问题 / 结论或风险变化 / 计划进度或用法变化。
- **动作**：把变化分别回写到日志、需求、记忆、进度对应的承载文件。
- **首次初始化补充**：若本轮刚初始化了四态系统，至少补齐当前目标、当前焦点、最近一次变更、已确认的关键约束，让下个会话能直接恢复。

## Phase 8 · Git & Delivery Gate

- **目的**：在 commit / push / PR / handoff 前确认 ready。
- **检查项**：diff 是否已检查、validation 是否匹配范围、docs sync 是否已考虑、是否存在不应隐式执行的破坏性 Git 动作。
- **Git 纪律**：至少确认当前分支、`git status`、`git diff --staged`（若准备 commit）；禁止把未审查的暂存内容、无关改动或敏感信息带入提交。
- **默认提交策略**：若当前仓库受 Git 管理、已完成一个单一逻辑变更、验证与四态回写都已完成，且用户或项目规则未禁止，则默认创建一个原子 commit。
- **自动化边界**：可以默认 auto-commit；不要默认 auto-push、auto-merge、auto-PR，也不要在验证不足或变更混杂时自动提交。

**诚实交付状态**（只给当前证据支持得起的结论）：

- not ready for delivery
- ready for commit
- ready for branch or PR flow
- ready for handoff without Git action

**Handoff 摘要**（交接时简洁包含）：

- 改了什么
- 验证了什么
- 还有哪些不确定或未验证
- 下一步最有价值的动作是什么

## Phase 9 · Evolution

- **目的**：把重复模式转成长期可复用资产（见 `06-evolution.md`）。
- **输出**：observation、suggestion，或显式说明暂不需要沉淀。

## 轻量任务的裁剪

可以跳过不必要阶段，但**不要跳过**：
- Phase 1 状态恢复推理
- Phase 3 权威判断
- Phase 6 验证推理
