# Portable Agent Workflow（四态工作流框架）

> 一个**工具中立**的多 Agent 项目工作流框架。
> 同一套约定，能在 Claude Code、Codex 等不同 Agent runtime 上跑出一致行为。

## 这是什么

不同的 AI 编码 Agent（Claude Code、Codex、Cursor……）各有各的配置格式、各有各的入口文件，但它们在一个真实项目里需要的东西其实是同一套：

- 知道**最近发生了什么**
- 知道**当前要满足什么**
- 知道**系统为什么这样设计**
- 知道**现在做到哪里**

这四件事，就是本框架的核心 —— **四态系统**。

本框架不绑定任何一家 Agent。它把"一个项目该怎么被 Agent 持续推进"抽象成一层**工具中立的核心约定**，再通过**后置的适配层**把这层约定翻译成各家 Agent 的原生格式。

## 设计原则

1. **状态先于动作**：任何实质性工作之前，先从四态系统恢复项目状态，不靠记忆、不靠假设。
2. **纯文本承载**：四态系统全部用 Markdown 文件承载。任何 Agent、任何编辑器、任何人都能读写，零运行时依赖。
3. **中立核心，适配后置**：核心约定不提任何一家 Agent 的私有概念；各家差异隔离在 `adapters/`。
4. **约定优于代码**：框架定义"读写约定"和"流程闸门"，不强制特定脚本或工具链。
5. **保守演进**：重复模式先观察、聚类、建议，经批准再沉淀，不让规则无约束膨胀。

## 架构总览

```text
framework/
├─ FRAMEWORK.md            # 本文件：总设计
├─ core/                   # 工具中立的工作流核心（CC / Codex 都读这一层）
│  ├─ 00-overview.md       #   核心总览与阅读顺序
│  ├─ 01-workflow.md       #   10 阶段工作流骨架
│  ├─ 02-state-systems.md  #   四态系统的发现与读写规则
│  ├─ 03-routing.md        #   意图 → 执行能力 的路由矩阵
│  ├─ 04-authority.md      #   多层规则的权威解析
│  ├─ 05-validation.md     #   验证闸门 / 文档闸门 / 交付闸门
│  └─ 06-evolution.md      #   重复模式的保守沉淀机制
├─ state-systems/          # 四态系统的可直接落地模板
│  ├─ README.md            #   四态系统说明
│  └─ templates/           #   drop-in Markdown 模板
│     ├─ LOG.md            #     日志系统
│     ├─ REQUIREMENTS.md   #     需求系统
│     ├─ MEMORY.md         #     记忆系统
│     └─ PROGRESS.md       #     进度系统
└─ adapters/               # 各家 Agent 的适配层（后置，先留计划）
   └─ README.md

skills/                    # 能力库：执行阶段委托的具体技能
                           #   双层结构 <领域大类>/<来源>/<skill>/，434 技能 / 19 大类
                           #   来源 ours｜codex｜cskills，去重优先级 ours>codex>cskills
```

两层职责分工：

- `framework/` 是**大脑**：决定何时恢复状态、如何路由、何时验证、何时交付。
- `skills/` 是**双手**：执行阶段真正干活的具体能力（API 版本化、限流、容器化……）。

## 四态系统（核心）

| 系统 | 回答的问题 | 默认承载文件 | 典型内容 |
|---|---|---|---|
| 日志系统 `project-log` | 最近发生了什么 | `LOG.md` | 变更记录、运行记录、部署记录、工作日志 |
| 需求系统 `project-requirements` | 当前要满足什么 | `REQUIREMENTS.md` | PRD、验收标准、审计基线、功能清单 |
| 记忆系统 `project-memory` | 为什么这样设计 | `MEMORY.md` | 架构决策、研究结论、运维手册、系统地图 |
| 进度系统 `project-progress` | 现在做到哪里 | `PROGRESS.md` | sprint 计划、todo、里程碑、阻塞项 |

**关键约定**：框架不强制固定文件名。上表是默认落地形态；当 Agent 进入一个**已有项目**时，先在项目里**发现**这四类状态真正存在哪里（见 `core/02-state-systems.md`），再恢复状态。

四态系统是这个框架与"普通 prompt 工程"的根本区别：它让 Agent 的上下文有了**可持久、可交接、可审计**的落点，从而支持多 Agent、多会话、跨工具协作。

## 工作流骨架（10 阶段）

中等以上复杂度的任务，按固定顺序推进：

```text
0. workspace scan      扫描仓库有哪些规则、技能、文档、验证入口
1. state restore       从四态系统恢复项目状态
2. intent classify     判断任务类型（status/audit/implement/fix/review/sync/git/evolve）
3. authority resolve   解析该信任哪一层规则、技能、文档
4. route & delegate    路由到合适的执行能力
5. execute             先读后改，只做必要改动，区分事实/推断/假设
6. validation gate     完成必须有与范围匹配的证据，不靠口头声明
7. docs & state sync    把成果同步回四态系统
8. git & delivery gate  commit/push/PR 前确认 ready
9. evolution           重复模式转成保守的沉淀建议
```

轻量任务可跳过不必要阶段，但**不要跳过**状态恢复、权威判断、验证推理。详见 `core/01-workflow.md`。

## 跨 Agent 通用性：中立核心 + 适配后置

本框架的"通用"靠两层实现：

1. **中立核心（已建）**：`core/` 和 `state-systems/` 完全不提任何一家 Agent 的私有概念。一个 Agent 只要能读写 Markdown、能按文档推理，就能消费这层约定 —— 这已经覆盖了 Claude Code、Codex、Cursor 等绝大多数工具。

2. **适配层（后置）**：各家 Agent 的"入口约定"不同 —— Claude Code 用 `SKILL.md` / `CLAUDE.md`，Codex 用 `AGENTS.md` / `agents/*.yaml`，Cursor 用 `.cursor/rules`。适配层负责把中立核心**翻译/挂载**到各家入口，让用户在各自工具里用原生方式触发同一套流程。详见 `adapters/README.md`。

> 当前阶段刻意只交付**中立核心**，不急着写适配器。先让核心约定在一两个 runtime 上跑通，再回头抽公共适配层，避免过早抽象。

## 落地方式

把本框架用到一个目标项目时：

1. 复制 `state-systems/templates/` 下的四个文件到目标项目（或映射到项目已有的等价文档）。
2. 让 Agent 第一次只做 `workspace scan` + `state restore` + 路由分析，先不改代码。
3. 等状态恢复与路由稳定后，再带验证闸门和文档同步跑完整任务。
4. 重复模式出现时，走 `core/06-evolution.md` 的保守沉淀流程。

## 与现有 skill 的关系

- `../skills/workflow-orchestration/ours/local-workflow`：**来源样本**，保留 J-SOP 的原始本地工作流写法，作为参考母本。
- `../skills/workflow-orchestration/ours/project-workflow`：**去项目化的 Claude Code 形态**，本质上是本框架在 CC 上的第一个实例。后续会在 `adapters/` 里正式登记它与中立核心的映射关系。
- 其余 `../skills/*`：执行阶段的能力库，由路由层（`core/03-routing.md`）按需委托。详见 `../skills/README.md`。

## 路线图

- [x] 阶段 1：中立核心（`core/` + `state-systems/`）
- [x] 阶段 2：四态系统 drop-in 模板
- [x] 阶段 3：Claude Code 适配器（project-workflow 已登记为 CC 实例，references 收敛为指向 core 的薄指针）
- [x] 阶段 4：Codex 适配器（`adapters/codex/` 模板：`AGENTS.md` + `agents/workflow.yaml`，指向 core）
- [ ] 阶段 5：在 CC + Codex 两边各跑通一次端到端实测
- [ ] 阶段 6：给能力库 skill 打"通用 / 半通用 / 项目定制"标记
