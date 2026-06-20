# Local Workflow Skill

一个面向 Codex 本地技能体系的“工作流总控”技能原型。

它不负责替代项目文档，也不负责覆盖项目里已经存在的 `audit`、`implement`、`fix`、`review`、`sync-docs`、`git-workflow` 等专项 skill。它的职责更像一层编排器：先判断当前仓库真正该听谁的，再把任务送到合适的本地能力上，并在完成前补齐验证、文档同步与交付闸门。

这个仓库适合两类用途：

- 作为项目内 workflow skill 的起点模板
- 作为后续沉淀为全局通用 skill 的前向测试样本

## 它解决什么问题

在一个真实项目里，工作流信息通常散落在很多层：

- 根目录指令文件，如 `AGENTS.md`、`README.md`
- 本地规则目录，如 `.codex/rules/`
- 本地 workflow 包装层，如 `.codex/workflows/`
- 本地执行技能，如 `.codex/skills/`、`.agents/skills/`
- 插件镜像、副本目录、历史迁移路径
- 项目真相文档，如 `docs/`、状态记录、审计记录、runbook

没有总控 skill 时，经常会出现这些问题：

- 明明项目内已有规则，但执行时先套了全局默认
- 同一类请求在不同会话里被路由到不同 skill
- 做完修改后没有走验证闸门，或者验证范围和改动范围不匹配
- 文档同步、计划更新、Git 交付经常被遗漏
- skill 镜像、副本、旧路径逐渐漂移，却没有统一的修复入口

`local-workflow` 的核心价值，就是把这些分散步骤收束成一条稳定、可复用、可演进的本地流程。

## 核心能力

- 权威源解析：优先识别当前仓库真正有效的本地规则、workflow 和 skill，而不是直接套用机器全局默认。
- 任务路由：按用户意图、输出类型、变更范围，把请求路由到合适的 `status`、`audit`、`implement`、`fix`、`review`、`sync-docs` 或 Git skill。
- 执行编排：把“扫描工作区、解析权威源、路由、执行、验证、同步、交付”串成一致的阶段化流程。
- 验证闸门：要求完成声明必须附带证据，避免“看过代码就算完成”。
- 交付闸门：在 commit、push、PR 或 handoff 之前，确认 diff、验证和文档同步都已经考虑过。
- 演进机制：当发现路径陈旧、镜像漂移、重复解释或重复手工判断时，先记录和建议，再在批准后更新 skill。

## 适用场景

- 你想给一个项目建立统一的本地 workflow 入口。
- 你的仓库已经有 `.codex`、`.agents`、`docs` 等多层结构，但缺一个“应该先看哪里、该怎么串起来”的总控规则。
- 你希望把 `status / audit / implement / fix / review / sync-docs / git` 这些动作接成连续流程，而不是每次重新口头约定。
- 你正在从单次对话式协作，逐步沉淀到可复用的项目工作流。
- 你希望后续把某个项目里跑顺的流程，提炼成机器级全局 skill。

## 不负责什么

这个 skill 的边界也需要明确：

- 不替代项目文档本身
- 不替代具体领域 skill 的执行细节
- 不把单次任务状态硬编码成长期规则
- 不默认直接修改 skill，自我演进默认只到 `suggest`
- 不绕过项目内已有约束去强行执行全局默认流程

换句话说，它是“编排层”，不是“所有能力都自己做”的超级 skill。

## 工作流总览

`local-workflow` 为较完整任务定义了一个统一阶段序列：

1. `workspace scan`
2. `intent classification`
3. `authority resolution`
4. `skill delegation`
5. `task execution`
6. `validation gate`
7. `documentation and state sync`
8. `git and delivery gate`
9. `skill evolution`

这条链路的意义是：

- 在开始执行前，先知道“本仓库该听谁的”
- 在开始编辑前，先知道“这到底是 review、fix 还是 implement”
- 在准备交付前，先知道“证据够不够、文档要不要同步”
- 在重复模式出现时，先知道“应该沉淀成 skill，还是只是一次性现象”

## 仓库结构

当前仓库只包含 skill 本体和必要参考文件，结构刻意保持简洁：

```text
.
├─ README.md
└─ local-workflow
   ├─ SKILL.md
   ├─ agents
   │  └─ openai.yaml
   └─ references
      ├─ authority-resolution.md
      ├─ routing-matrix.md
      ├─ execution-phases.md
      ├─ validation-gates.md
      ├─ git-and-handoff.md
      └─ skill-evolution.md
```

## 文件职责说明

主 `SKILL.md` 保持精简，只承担总纲职责；细节全部下沉到 `references/`，这是这个仓库最重要的设计约束之一。

| 文件 | 作用 |
|---|---|
| `local-workflow/SKILL.md` | 定义角色、核心原则、路由入口、阶段顺序和 reference 装载规则 |
| `local-workflow/references/authority-resolution.md` | 规定如何判断当前仓库的本地权威源，以及如何识别迁移、漂移和镜像冲突 |
| `local-workflow/references/routing-matrix.md` | 规定如何把请求稳定路由到合适的 workflow/skill，避免只靠关键词猜测 |
| `local-workflow/references/execution-phases.md` | 定义完整任务从扫描到交付再到演进的执行阶段 |
| `local-workflow/references/validation-gates.md` | 定义验证等级、验证选择顺序、完成声明要求 |
| `local-workflow/references/git-and-handoff.md` | 定义交付前检查、Git 触发条件和 handoff 表达方式 |
| `local-workflow/references/skill-evolution.md` | 定义观察、聚类、建议、批准、应用、验证这条 skill 演进链路 |
| `local-workflow/agents/openai.yaml` | 为 skill 提供最小代理元信息，便于在技能系统中展示与调用 |

## 核心设计原则

### 1. 本地优先，不从全局往里套

先看项目内 instruction files、rules、workflows、skills、truth docs，再把机器全局 skill 作为兜底，而不是反过来。

### 2. 按角色解析权威，而不是只找一个“唯一真相”

不同层承担不同职责：

- 规则约束看本地 rules
- 命令语义看本地 workflow wrappers
- 执行细节看本地 skills
- 业务真相看当前 docs 与当前代码
- 全局 skills 只做通用 fallback

### 3. 编排归编排，执行归执行

`local-workflow` 负责判断和调度，但不应吞掉 `audit`、`review`、`implement` 等专项 skill 的边界。

### 4. 完成必须有证据

任何“已完成”都应和实际验证范围匹配。看过文件不等于跑通过，跑过类型检查也不等于用户可见行为已经确认。

### 5. 默认建议演进，不默认直接改 skill

skill 体系一旦自动膨胀，很容易反过来制造混乱。因此默认停在 `suggest`，只在明确批准后进入 `apply`。

### 6. 主文件精简，细节外置

主 `SKILL.md` 不承担过长、过细、过项目化的细节，复杂规则全部进入 `references/`，这样更利于维护和迁移。

## 推荐使用方式

### 方式一：先作为项目内原型使用

推荐先把 `local-workflow/` 放到项目内技能目录，例如：

```text
.codex/skills/local-workflow/
```

然后用真实任务跑几轮，例如：

- 工作流梳理
- 审计到修复的连续任务
- 文档同步与交付动作
- skill 漂移检查

这样能更快发现你自己项目里的 authority layer、命令语义和验证方式是否和这个模板契合。

### 方式二：稳定后再全局化

当它在多个项目里都跑得顺，并且 references 里的规则不再明显依赖单仓库结构时，再考虑把它提炼到机器级全局 skill 目录。

换句话说，比较推荐的顺序是：

1. 项目内试跑
2. 记录观察与偏差
3. 调整 references
4. 做前向测试
5. 再决定是否全局化

## 接入建议

如果你要把它接入自己的技能体系，建议至少检查下面几件事：

1. 当前仓库是否已经存在 `.codex/rules/`、`.codex/workflows/`、`.codex/skills/` 或 `.agents/skills/`
2. 当前仓库的“真相文档”在哪里，例如 `docs/`、状态文档、runbook 或审计报告
3. 当前仓库是否已经有固定的验证脚本或验证 skill
4. 当前仓库是否已经有 commit / PR / 交付类 skill
5. 是否存在旧目录、镜像目录或插件副本需要纳入 authority resolution

如果这些层已经存在，这个 skill 的收益会非常明显；如果仓库还是非常轻量，它也可以作为未来扩展的总纲。

## skill 自动沉淀 / 补全优化机制

这个仓库已经把“skill 自动沉淀”的逻辑纳入设计，但刻意采用了保守策略。

它不是发现一次问题就直接改 skill，而是遵循这条链路：

1. `observe`
2. `cluster`
3. `suggest`
4. `approve`
5. `apply`
6. `verify`

典型触发信号包括：

- 引用路径不存在
- 同一类路由决策重复出现
- 同一种验证缺口反复出现
- 镜像 skill 和主 skill 发生漂移
- 同一段手工解释在多个任务里重复出现

这种设计的目的，是把“沉淀经验”从一次性记忆，变成可审计、可回放、可批准的演进过程，而不是让 skill 自己无约束膨胀。

## 前向测试建议

在把它推广为全局 skill 之前，建议至少做一轮真实 forward-test，重点观察：

- authority resolution 是否真的选中了当前项目的本地主权威源
- routing 是否稳定地区分了 `audit`、`review`、`fix`、`implement`
- validation gate 是否与任务真实风险匹配
- docs sync 是否在应该发生时发生
- git delivery gate 是否避免了“代码改了但没有检查 readiness”的情况
- evolution 逻辑是否先建议修主源，而不是直接去修镜像

如果 forward-test 能稳定通过，这个 skill 就已经具备进一步推广的基础。

## 当前状态

当前仓库可以视为一个 `v1` 原型版本，已经具备：

- 精简主 skill
- 六个核心 reference 文件
- 基础 agent 元信息
- 中文仓库级说明文档
- 面向后续全局化的结构准备

它适合作为“起步即能用”的模板，但仍然鼓励在真实项目中继续打磨，而不是直接视为终稿。

## Roadmap

后续可以继续增强的方向包括：

- 增加更多面向真实仓库的 forward-test 样例
- 抽出更标准的 observation / suggestion 模板产物
- 增加与常见本地 workflow skill 的协同示例
- 为不同仓库形态补充更具体的 authority resolution 例子
- 在多个项目试跑后，再收敛成更稳的全局版

## 适合谁

这个仓库会特别适合以下人群：

- 正在为自己的 Codex / 本地 skill 体系建立统一流程的人
- 已经有多个 skill，但缺少总控编排层的人
- 想把零散对话经验沉淀为长期可复用 workflow 的人
- 想在“项目内先试跑，再全局推广”的方式下稳步演进技能体系的人

如果你要的不是“再多一个 skill”，而是“给现有 skill 体系一个稳定工作流外壳”，那它就是为这个目标设计的。
