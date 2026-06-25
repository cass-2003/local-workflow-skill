# 工作流骨架（10 阶段）

定义一条适合多数项目的标准流程，让扫描、恢复、执行、验证、同步、交付有固定顺序。任何 Agent runtime 都按这套顺序推进。

## Phase 0 · Workspace Scan

- **目的**：看清仓库里有哪些规则、工作流、技能、文档、验证入口；避免带旧假设开工。
- **输出**：可能的权威层、可能的任务域、可能的验证入口。

## Phase 1 · State Restore

- **目的**：先恢复项目状态再行动。
- **动作**：至少寻找四态系统 —— 日志 / 需求 / 记忆 / 进度（见 `02-state-systems.md`）。
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

## Phase 8 · Git & Delivery Gate

- **目的**：在 commit / push / PR / handoff 前确认 ready。
- **检查项**：diff 是否已检查、validation 是否匹配范围、docs sync 是否已考虑、是否存在不应隐式执行的破坏性 Git 动作。

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
