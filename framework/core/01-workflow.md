# 工作流骨架（10 阶段）

定义一条适合多数项目的标准流程，让扫描、恢复、执行、验证、同步、交付有固定顺序。任何 Agent runtime 都按这套顺序推进。

## Phase 0 · Workspace Scan

- **目的**：看清仓库里有哪些规则、工作流、技能、文档、验证入口；避免带旧假设开工。
- **新项目地基门禁**：若当前目录是新项目、空项目或首次接入 workflow，先确认是否存在 `.git/`、`.gitignore`、项目入口说明、四态系统和基础验证命令；缺失时先补最小地基，再进入实质开发。
- **初始化分类门禁**：用户说“初始化项目”时，先判断是空目录新想法、半初始化项目、已有项目后补 workflow、明确想法输入，还是直接地基请求；不要把所有情况都当成写模板动作。
- **需求访谈门禁**：空目录、新想法、或用户要求“先问问题/多轮收集/不要臆测”时，先进入需求访谈，不立刻生成完整文档包或业务代码；已有项目后补 workflow 时先 scan + State Restore。
- **Git 初始化规则**：若目标目录没有 `.git/` 且不是另一个仓库的子目录，默认执行 `git init`；若已有 `.git/`，只读取状态，不重建、不覆盖远端、不改历史。
- **输出**：可能的权威层、可能的任务域、可能的验证入口。

## Phase 1 · State Restore

- **目的**：先恢复项目状态再行动。
- **动作**：至少寻找四态系统 —— 日志 / 需求 / 记忆 / 进度（见 `02-state-systems.md`）。
- **缺失处理**：若项目里还没有可承载四态系统的本地文件，先按模板初始化最小可用的四态骨架，再进入后续阶段；不要在"完全失忆"状态下直接开发。
- **恢复记录**：实质性工作开始前，必须形成一段 `State Restore` 摘要，写明四态承载文件、是否占位/陈旧、最近目标、最近验证、阻塞和本轮假设。若状态文件仍是模板占位，先补最小真实事实，再继续开发。
- **输出**：最近发生了什么、当前目标与约束、已有知识与基线、当前进度与阻塞。

## Phase 2 · Intent Classification

- **目的**：判断任务更像 status / audit / implement / fix / review / docs-sync / git-delivery / evolution 中的哪一类。
- **输出**：主意图、次意图、初步范围。
- **产物契约**：如果意图是 audit / implement / fix / review / docs-sync / status，先确认本项目是否定义了对应产物位置；没有时使用 `07-artifact-contracts.md` 的默认契约。

## Phase 3 · Authority Resolution

- **目的**：判断该信任哪一层规则、哪一层技能、哪一层文档（见 `04-authority.md`）。
- **输出**：rules source / workflow source / execution source / truth-docs source / fallback chain。

## Phase 4 · Route & Delegate

- **目的**：让合适的执行能力承担合适的工作（见 `03-routing.md`）。
- **规则**：编排权保留在工作流层；执行细节优先委托给项目本地能力；无本地能力时才用最接近的全局兜底。

## Phase 5 · Execute

- **目的**：按任务类型完成分析、修改、修复、评审或同步。
- **规则**：先读后改；只做必要改动；明确区分事实、推断与假设。
- **自动产物**：审计、验收预检、重要实现、修复闭环、回归验证和文档同步不能只停留在对话里；应写入项目约定的报告、日志、计划或状态文件。
- **自主推进**：当用户授权持续推进项目时，先按 `08-autonomous-project-loop.md` 的初始项目规划闸门建立路线图和下一步工作包，再进入实现。
- **启动访谈**：当项目仍处于 idea / empty / unclear 状态时，先用 `project-inception-docs` 的 Discovery Interview 收集目标、角色、MVP、权限、数据、风险和验证方式，再生成启动文档。

## Phase 6 · Validation Gate

- **目的**：防止"完成只靠口头声明"（见 `05-validation.md`）。
- **输出**：已验证的内容、使用的命令或证据、未验证的部分及原因。

## Phase 7 · Docs & State Sync

- **目的**：让四态系统与当前成果一致。
- **常见触发**：实现了新功能 / 修复了已知问题 / 结论或风险变化 / 计划进度或用法变化。
- **动作**：把变化分别回写到日志、需求、记忆、进度对应的承载文件。
- **循环记录**：自主推进、审计修复、重要实现或交接前，必须在进度系统或日志系统留下 `Loop Record`：本轮目标、验收标准、验证证据、自审结论、修复结果、下一目标或停止原因。
- **首次初始化补充**：若本轮刚初始化了四态系统，至少补齐当前目标、当前焦点、最近一次变更、已确认的关键约束，让下个会话能直接恢复。
- **索引同步**：若新增或更新了审计报告、验收报告、架构文档、测试文档或计划文档，同时更新对应目录索引和 `docs/INDEX.md`，避免产物变成孤岛。

## Phase 8 · Git & Delivery Gate

- **目的**：在 commit / push / PR / handoff 前确认 ready。
- **检查项**：diff 是否已检查、validation 是否匹配范围、docs sync 是否已考虑、是否存在不应隐式执行的破坏性 Git 动作。
- **Git 纪律**：至少确认当前分支、`git status`、`git diff --staged`（若准备 commit）；禁止把未审查的暂存内容、无关改动或敏感信息带入提交。
- **提交闭环策略**：若当前仓库受 Git 管理、已完成可验证修改、验证与四态回写都已完成，且用户或项目规则未禁止，则必须创建原子 commit。
- **原子拆分**：一个 commit 只表达一个完整工作包及其必要测试、文档和状态同步；多逻辑变更必须拆成多个 commit 后再交付。
- **暂存纪律**：按明确路径 stage，禁止为了省事使用 `git add .` 或 `git add -A` 把未审查内容带入提交。
- **阻塞记录**：若因无 Git、验证失败、冲突、敏感信息或等待用户决策而不能 commit，交付时必须说明原因和下一步。
- **自动化边界**：可以默认 auto-commit；不要默认 auto-push、auto-merge、auto-PR，也不要在验证不足或变更混杂时强行提交。

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

## 自主推进循环

当任务不是单次交付，而是“继续推进项目 / 按计划开发 / 自动审计修复 / 推进到可用版本”时，使用 `08-autonomous-project-loop.md` 把本 10 阶段流程包成循环：

```text
project bootstrap planning
-> select goal
-> execute
-> validate
-> self-audit
-> repair findings
-> sync
-> commit closure
-> select next goal or stop with reason
```

循环不是无边界自动化。只有在目标清晰、风险可控、验证可做、变更仍是单一工作包时继续；遇到用户决策、外部凭据、高风险操作、连续失败或预算边界时停止并写明下一步。

## 轻量任务的裁剪

可以跳过不必要阶段，但**不要跳过**：
- Phase 1 状态恢复推理
- Phase 3 权威判断
- Phase 6 验证推理
