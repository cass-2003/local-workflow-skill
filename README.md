<div align="center">

# 🧭 Portable Agent Workflow

### 工具中立的多 Agent 项目工作流框架

*一套纯 Markdown 约定，让 Claude Code、Codex 等不同 AI Agent 在同一个项目里跑出一致行为。*

![status](https://img.shields.io/badge/status-alpha-orange)
![agents](https://img.shields.io/badge/agents-Claude_Code_·_Codex-5b6cf9)
![skills](https://img.shields.io/badge/skills-565-2ea44f)
![domains](https://img.shields.io/badge/domains-58-2ea44f)
![format](https://img.shields.io/badge/core-pure_Markdown-lightgrey)
![deps](https://img.shields.io/badge/runtime_deps-0-blue)

</div>

---

## ✨ 这是什么

不同的 AI 编码 Agent（Claude Code、Codex、Cursor……）各有各的配置格式、各有各的入口文件，但它们在一个真实项目里需要的东西其实是同一套：**知道最近发生了什么、当前要满足什么、为什么这样设计、现在做到哪里。**

本框架把"一个项目该怎么被 Agent 持续推进"抽象成一层**工具中立的核心约定**，再用**后置的适配层**把它翻译成各家 Agent 的原生格式。核心全部用 Markdown 承载 —— 零运行时依赖，任何能读写文本、能按文档推理的 Agent 都能消费。

> 🧠 **大脑** `framework/` 决定何时做什么 · 🛠️ **双手** `skills/` 决定具体怎么做 · 🔌 **插口** `adapters/` 对接各家 Agent

---

## 🧩 核心理念：四态系统

一个项目被多 Agent、多会话持续推进时，最需要的是这四件事 —— 这就是框架的地基，**全部用纯 Markdown 文件承载**：

| 系统 | 回答的问题 | 默认承载 | 典型内容 |
|:--|:--|:--|:--|
| 🗒️ **日志** `project-log` | 最近发生了什么 | `LOG.md` | 变更/部署/运行记录 |
| 📋 **需求** `project-requirements` | 当前要满足什么 | `REQUIREMENTS.md` | PRD、验收标准、基线 |
| 🧠 **记忆** `project-memory` | 为什么这样设计 | `MEMORY.md` | 架构决策、研究结论 |
| 📊 **进度** `project-progress` | 现在做到哪里 | `PROGRESS.md` | 计划、todo、阻塞项 |

普通 prompt 工程的上下文是**易失**的：会话一结束、工具一切换，Agent 就"失忆"。四态系统给上下文四个**可持久、可交接、可审计**的落点：

- 🔁 **跨会话** — 新会话先读四态系统就能恢复，不靠用户重述
- 🤝 **跨 Agent** — Claude Code 写的状态，Codex 也能读（都是纯 Markdown）
- 🔍 **可审计** — 每次变更回写对应系统，历史可回看
- 🧾 **可恢复** — 开工前形成 `State Restore` 摘要，收工前留下 `Loop Record`

> 💡 不强制固定文件名。框架认的是四个**角色**，已有项目可把 `CHANGELOG.md`、`PRD.md` 等认领为对应系统。

---

## 🏗️ 架构总览

```text
┌─────────────────────────────────────────────────────────────┐
│  🔌 adapters/   各家 Agent 原生入口（薄，只负责"被触发 + 指路"）  │
│       Claude Code → SKILL.md       Codex → AGENTS.md + *.yaml   │
└───────────────────────────┬─────────────────────────────────┘
                            │ 触发，指向 ↓
┌───────────────────────────▼─────────────────────────────────┐
│  🧠 framework/core/   工具中立的工作流核心（单一真相）           │
│       10 阶段骨架 · 路由 · 权威解析 · 验证闸门 · 产物契约 · 自主循环 · 保守演进 │
│                            ↑ 读 / 写                           │
│  ★ framework/state-systems/   四态系统（地基）                  │
│       🗒️ 日志 · 📋 需求 · 🧠 记忆 · 📊 进度                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ Phase 4/5 委托 ↓
┌───────────────────────────▼─────────────────────────────────┐
│  🛠️ skills/   565 技能 / 58 领域大类（双层 <大类>/<来源>/）      │
│       安全 85 · 逆向 63 · Render/Expo/前后端等领域持续扩展       │
└─────────────────────────────────────────────────────────────┘
```

| 层 | 职责 | 关键不变量 |
|:--|:--|:--|
| 🔌 `adapters/` | 把核心挂载到各家 Agent 入口 | 保持薄，只触发 + 指路，不复制规范 |
| 🧠 `framework/core/` | 流程与产物契约的唯一真相 | 改流程只改 core，适配器跟着指 |
| ★ `state-systems/` | 项目状态的持久落点 | 状态先于动作，开工先恢复 |
| 🛠️ `skills/` | 执行阶段委托的具体能力 | 去重优先级 `ours > codex > community` |

---

## 🔄 10 阶段工作流

中等以上复杂度的任务，按固定顺序推进：

```text
0️⃣ scan ─▶ 1️⃣ state restore ─▶ 2️⃣ intent ─▶ 3️⃣ authority ─▶ 4️⃣ route
                                                                      │
9️⃣ evolve ◀─ 8️⃣ deliver ◀─ 7️⃣ sync ◀─ 6️⃣ validate ◀─ 5️⃣ execute ◀─┘
```

<details>
<summary>📖 展开看每个阶段在做什么</summary>

| # | 阶段 | 目的 |
|:-:|:--|:--|
| 0 | **workspace scan** | 看清仓库有哪些规则、技能、文档、验证入口 |
| 1 | **state restore** | 从四态系统恢复项目状态（不靠记忆与假设） |
| 2 | **intent classify** | 判断任务类型：status / audit / implement / fix / review / sync / evolve |
| 3 | **authority resolve** | 解析该信任哪一层规则、技能、文档 |
| 4 | **route & delegate** | 按问题域路由到 `skills/` 对应能力 |
| 5 | **execute** | 先读后改，只做必要改动，区分事实/推断/假设；审计/验收/同步等动作留下文件产物 |
| 6 | **validation gate** | 完成必须有与范围匹配的证据，不靠口头声明 |
| 7 | **docs & state sync** | 把成果分类回写四态系统，并同步审计/文档索引 |
| 8 | **git & delivery gate** | commit / push / PR 前过 readiness 检查 |
| 9 | **evolution** | 重复模式转成保守的沉淀建议（observe → suggest → approve → apply）|

> ⚖️ 轻量任务可裁剪阶段，但**不跳过**状态恢复、权威判断、验证推理。

</details>

---

## 🧾 自动产物契约

工作流不是只让 Agent “想得更有顺序”，还要求关键动作留下可恢复、可审计的文件产物。默认契约见 [`framework/core/07-artifact-contracts.md`](framework/core/07-artifact-contracts.md)。

| 任务类型 | 默认产物 | 同步要求 |
|:--|:--|:--|
| `audit` / 验收预检 | `docs/audit/<日期>-<范围>-audit.md` | 更新 `docs/audit/INDEX.md`、`state/LOG.md`、`state/PROGRESS.md` |
| `implement` / `fix` | 代码变更 + 必要文档 | 更新 `state/LOG.md`、`state/PROGRESS.md`；行为、架构、验证或风险变化时同步 docs |
| `docs-sync` | 被同步的文档与索引 | 更新 `docs/INDEX.md` 或相关目录索引，避免新文件变成孤岛 |
| `validation` / 回归验证 | 验证命令、结果、证据摘要 | 必要时写入 `docs/testing/`，并在 `state/LOG.md` 记录验证范围 |

新项目通过 `project-inception-docs` 初始化时，会默认带上 `docs/audit/INDEX.md`、`docs/audit/TEMPLATE-GLOBAL-AUDIT.md`，并在 `AGENTS.md` / `CLAUDE.md` 中写入 Artifact Contracts。这样你说“审计一下”“验收预检”“修复这个缺口”时，Agent 不应只在聊天里给结论，而要把报告、索引、日志和进度同步好。

## 🔁 自主推进模式

当用户说“继续推进项目”“按计划开发”“自动审计修复”这类话时，Agent 不应只做一个临时任务就停下。默认流程是：先检查或生成项目路线图和下一步工作包，再选择一个小而完整的目标，完成实现、验证、自审、修复、状态同步和原子 commit 闭环；之后回到路线图选择下一个目标，直到遇到需要用户决策、验证环境缺失、高风险操作或预算边界。

核心规则见 [`framework/core/08-autonomous-project-loop.md`](framework/core/08-autonomous-project-loop.md)。默认推荐产物包括路线图、下一步工作包、初始审计报告和 `state/PROGRESS.md` 中的当前循环状态；本仓库启动模板使用 `docs/planning/开发路线图.md` 与 `docs/planning/下一步工作包.md`，已有项目可映射到自己的等价文档。

为了避免“文件存在但 agent 仍然失忆”，入口模板还要求两条运行时记录：

- `State Restore`：开工前说明四态来源、占位/陈旧项、当前目标、最近验证、阻塞和本轮假设。
- `Loop Record`：每轮结束前写明目标、验收标准、验证证据、自审、修复、状态/文档同步、commit、下一目标或停止原因。

## 🧭 项目启动访谈

“初始化项目”不是单纯写文件动作，而是项目启动流程入口。Agent 需要先判断当前目录状态，再决定是访谈、后补 workflow，还是直接打最小地基。

| 场景 | 默认动作 |
|:--|:--|
| 空目录 / 新想法 | 先进入需求访谈，不立刻生成完整文档包 |
| 已给产品想法 | 按用户端、管理端、租户端、授权端、内容来源、商业化、合规、技术交付等角色多轮提问 |
| 已有项目后补 workflow | 先 scan + State Restore，识别现有代码、文档、Git 和验证入口，再补缺口 |
| 用户要求直接打地基 | 生成最小地基，未知项标 `待确认`，下一步继续访谈 |

访谈模式每轮输出 `已确认 / 待确认 / 冲突或风险 / 下一轮问题`，直到用户确认可以生成文档、初始化地基或开始开发。详细规则见 [`project-discovery-interview.md`](skills/workflow-orchestration/ours/project-inception-docs/references/project-discovery-interview.md)。

---

## 🛠️ 能力库（565 技能 · 58 大类）

执行阶段委托的具体技能，四源合并去重，双层结构 `<领域大类>/<来源>/<skill>/`。如果你只是想知道“这个库到底会什么”，先看人类导览版：

- [`skills/CATALOG.md`](skills/CATALOG.md)：按场景、领域和常用说法找能力
- [`skills/README.md`](skills/README.md)：完整领域索引和 skill slug
- [`skills/TIERS.md`](skills/TIERS.md)：通用 / 半通用分级

### 按目标快速找

| 你想做什么 | 推荐领域 |
|:--|:--|
| 新项目从想法开始、先问需求、生成 PRD/架构/路线图 | `workflow-orchestration`、`product-management`、`frontend-ui`、`backend-api` |
| Web / 管理后台 / UI / 设计系统 | `frontend-ui`、`quality-delivery`、`content-authoring` |
| 后端 / API / 数据库 / 认证授权 | `backend-api`、`data-analysis`、`engineering-core`、`security-engineering` |
| App / 小程序 / 跨端 / 登录支付 | `mobile-crossplatform`、`payments-commerce`、`maps-location` |
| AI Agent / RAG / Prompt / 自动化 | `ai-automation`、`ai-governance-compliance`、`research-knowledge` |
| 云部署 / DevOps / SRE / CI | `cloud-infra`、`quality-delivery`、`engineering-core` |
| 测试 / 代码审计 / 重构 / Git 交付 | `quality-delivery`、`engineering-core` |
| 安全 / 渗透 / 合规 / 隐私 | `security-engineering`、`security-compliance`、`privacy-compliance` |
| 逆向 / 二进制 / 固件 / 驱动 | `reverse-engineering`、`hardware-systems` |
| 产品 / 增长 / 运营 / 营销 | `product-management`、`product-growth`、`growth-experiments`、`content-strategy` |
| 商业 / 销售 / 收入 / 组织协作 | `commercial-strategy`、`sales-enablement`、`revenue-operations`、`business-operations` |
| 研究 / 学习 / 文档 / 知识管理 | `research-knowledge`、`research-ops`、`literature-review`、`markdown-publishing` |

### 领域数量概览

| 🏷️ 领域 | 数量 | 🏷️ 领域 | 数量 | 🏷️ 领域 | 数量 |
|:--|:-:|:--|:-:|:--|:-:|
| 安全工程 | 85 | 逆向工程 | 63 | 云基础设施 | 37 |
| 移动跨端 | 37 | 前端 UI | 30 | 后端 API | 29 |
| 通用工程 | 26 | 质量交付 | 24 | 编程语言 | 21 |
| AI 自动化 | 18 | 内容创作 | 14 | 支付电商 | 12 |
| 地图位置 | 11 | 研究知识 | 10 | 数据分析 | 9 |
| 硬件系统 | 8 | 产品增长 | 8 | 产品管理 | 8 |
| 商业策略 | 7 | 业务运营 | 6 | 其余长尾领域 | 102 |

技能按通用性分级：**🟢 通用 482 · 🟡 半通用 83 · 🔵 项目定制 0**（见 [`skills/TIERS.md`](skills/TIERS.md)）。完整索引见 [`skills/README.md`](skills/README.md)。

---

## 🚀 快速上手

把框架用到一个目标项目：

```text
1. 先判断项目状态：空目录新想法、半初始化项目、已有项目后补 workflow、明确想法输入或直接地基请求
2. 空目录或新想法先做需求访谈；已有项目先 scan + State Restore；用户明确直接打地基时才生成最小模板
3. 若目标目录没有 Git 且不在父级仓库中，让 Agent 执行 git init
4. 补齐 .gitignore、README.md、AGENTS.md / CLAUDE.md、docs/INDEX.md 和基础验证命令
5. 复制 framework/state-systems/templates/ 的四个文件到目标项目
   （或映射到项目已有的等价文档），并写入当前目标/约束/焦点
6. 让 Agent 第一次只做：scan + state restore + 路由分析，先不改业务代码
7. 状态恢复与路由稳定后，再带验证闸门和文档同步跑完整任务
8. 验证通过且状态同步后，默认要求 Agent 创建原子 commit；多逻辑变更先拆成多个 commit
```

也可以直接使用仓库内初始化器：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\project-init\Initialize-PortableAgentProject.ps1 `
  -ProjectPath "C:\path\to\project" `
  -ProjectName "My Project" `
  -Idea "One-sentence goal" `
  -RefreshAgentEntries `
  -EnsureIndexes
```

只刷新已有项目的 `AGENTS.md` / `CLAUDE.md` 工作流托管块，并保留项目专属说明：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\project-init\Initialize-PortableAgentProject.ps1 `
  -ProjectPath "C:\path\to\project" `
  -AgentEntriesOnly
```

### 新项目地基门禁

每个新项目、空目录或首次接入 workflow 的项目，默认先补这几块地基：

| 地基项 | 默认动作 |
|:--|:--|
| 初始化分类 | 先判断空目录新想法 / 半初始化 / 已有项目后补 / 明确想法 / 直接地基请求 |
| 需求访谈 | 空目录、新想法或用户要求先问问题时，先多轮收集需求，不直接臆测生成文档 |
| Git | 没有 `.git/` 且不在父级仓库中时执行 `git init`；已有仓库只读状态，不重建、不改历史 |
| 忽略文件 | 生成或合并 `.gitignore`，覆盖依赖、构建产物、日志、环境变量、本地缓存和密钥 |
| Agent 入口 | 生成或更新 `AGENTS.md` / `CLAUDE.md`，指向四态系统和项目真相文档 |
| 四态系统 | 初始化或映射日志、需求、记忆、进度，并写入当前目标、约束、焦点和下一步 |
| 文档入口 | 保证 `README.md` 与 `docs/INDEX.md` 能说明项目状态、文档地图和验证入口 |
| 验证入口 | 记录 install / dev / test / lint / build 命令；未知就标 `待确认`，不伪造 |
| 首次提交 | 地基补齐并验证后进入原子 commit 闭环；多逻辑变更拆成多个 commit；不默认 push、merge、PR 或配置远端 |

> 🧱 想从一个想法直接开新项目，用 `project-inception-docs`：它会把 Git、忽略文件、Agent 入口、四态系统、README、PRD、架构、测试验收和运维文档一起打成启动包。

适合第一轮试跑的提示词：

```text
🗣️ 先扫描当前仓库，识别规则/技能/文档/验证入口，恢复四态系统状态，只做路由分析。
🗣️ 初始化这个空目录项目前，先进入需求访谈模式，按角色问我问题，不要先写文件。
🗣️ 如果当前项目还没有 Git、.gitignore、AGENTS/CLAUDE、README、docs/INDEX 或四态系统，先补齐项目地基。
🗣️ 使用 project-inception-docs，把这个想法初始化成可开发项目，并生成启动文档包。
🗣️ 判断这个需求该走 audit / implement / fix / review，并说明验证与文档同步策略。
🗣️ 检查当前改动在 commit 前是否已满足验证、文档同步和交付三道闸门；满足时按工作包拆分并直接原子 commit。
```

> 🧪 想看完整跑一遍的样子？[`framework/validation/sample-project/`](framework/validation/sample-project/) 是个可直接重跑的最小样板，附 dogfood 验证报告。

仓库维护者可运行工作流自检：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\project-init\Validate-PortableAgentWorkflow.ps1
```

---

## 🔌 跨 Agent 通用性

核心是纯 Markdown，**任何能读写文本的 Agent 都能消费**。差异隔离在薄薄的适配层：

| Agent | 原生入口 | 适配方式 | 状态 |
|:--|:--|:--|:-:|
| **Claude Code** | `SKILL.md` / `CLAUDE.md` | 项目根 `CLAUDE.md` + 执行级 `SKILL.md` 双入口，正文都指向 `core/*` | ✅ |
| **Codex** | `AGENTS.md` / `agents/*.yaml` | `AGENTS.md` 挂载，正文指向 `core/*` | ✅ |
| **Cursor 等** | `.cursor/rules` 等 | 同理：薄入口 + 指向中立核心 | 🔜 |

> 共同模式：**入口保持薄**，只负责"被触发"和"指路"，流程逻辑全留在核心，单处维护。

---

## 📁 仓库结构

```text
.
├─ 📄 README.md            仓库门面（本文件）
├─ 📄 AGENTS.md / CLAUDE.md 本仓库的 Agent 本地工作流入口
├─ 📄 LICENSE / NOTICE     许可证与第三方来源说明
├─ 📄 ARCHITECTURE.md      整张架构图（看全局先读这个）
├─ 📊 state/               本仓库当前四态：日志/需求/记忆/进度
├─ 🧠 framework/           框架本体
│   ├─ FRAMEWORK.md         总设计 + 路线图
│   ├─ core/                ★ 单一真相：10 阶段/状态/路由/权威/验证/产物/演进
│   ├─ state-systems/       ★ 四态系统说明 + drop-in 模板
│   ├─ adapters/            各家 Agent 适配登记（CC / Codex）
│   └─ validation/          dogfood 样板 + 端到端验证报告
├─ 🛠️ skills/              能力库：565 技能 / 58 大类
│   ├─ README.md             领域索引
│   ├─ TIERS.md              分级（通用/半通用；项目定制不进入开源库）
│   ├─ _merge-manifest.csv   四源合并对照表
│   └─ <大类>/<来源>/<skill>/
└─ 🔧 tools/               可复现工具
    ├─ skill-merge/         能力库合并脚本
    └─ project-init/        项目初始化、入口刷新与工作流自检脚本
```

---

## 🗺️ 路线图

- [x] 🧱 中立核心（`framework/core/` + `state-systems/`）
- [x] 📑 四态系统 drop-in 模板
- [x] 🤖 Claude Code 适配器
- [x] 🤖 Codex 适配器
- [x] 🛠️ 四源合并丰富能力库（565 技能 / 58 大类）
- [x] 🏷️ 能力库分级标记 + 项目定制项清理
- [x] 🧪 Claude Code 侧端到端 dogfood 跑通
- [x] 🧪 Codex 侧端到端实测
- [x] 🔧 开源化项目初始化与入口刷新脚本
- [~] 🔌 抽取公共适配层 / 全局安装说明

---

## 📜 许可证与来源

本仓库原创的框架文档、适配器模板、合并脚本、状态模板和仓库维护技能默认使用 MIT License。部分导入或镜像技能保留各自目录内的 `LICENSE` / `NOTICE`，重新分发子集时需要一并保留。

贡献边界见 [`CONTRIBUTING.md`](CONTRIBUTING.md)：通用或半通用 skill 可以进入本仓库；强绑具体项目、私有产品、服务器、账号、本机路径或旧命令封装的 skill 应放在目标项目本地或私有仓库。

---

## 🧠 设计原则

```text
1. 状态先于动作   任何实质性工作前，先从四态系统恢复状态
2. 纯文本承载     四态系统全是 Markdown，零运行时依赖
3. 中立核心       核心不提任何一家 Agent 的私有概念，差异隔离在 adapters/
4. 约定优于代码   框架定义读写约定与流程闸门，不强制特定脚本
5. 保守演进       重复模式先观察、聚类、建议，经批准再沉淀
```

---

<div align="center">

*源于可迁移的多 Agent 工作流实践，持续去项目化为通用骨架。*

**🧭 大脑决定何时做什么，双手决定具体怎么做，状态让一切可持久、可交接、可审计。**

</div>
