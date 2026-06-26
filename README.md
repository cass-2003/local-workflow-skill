<div align="center">

# 🧭 Portable Agent Workflow

### 工具中立的多 Agent 项目工作流框架

*一套纯 Markdown 约定，让 Claude Code、Codex 等不同 AI Agent 在同一个项目里跑出一致行为。*

![status](https://img.shields.io/badge/status-alpha-orange)
![agents](https://img.shields.io/badge/agents-Claude_Code_·_Codex-5b6cf9)
![skills](https://img.shields.io/badge/skills-409-2ea44f)
![domains](https://img.shields.io/badge/domains-18-2ea44f)
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
│       10 阶段骨架 · 路由 · 权威解析 · 验证闸门 · 保守演进         │
│                            ↑ 读 / 写                           │
│  ★ framework/state-systems/   四态系统（地基）                  │
│       🗒️ 日志 · 📋 需求 · 🧠 记忆 · 📊 进度                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ Phase 4/5 委托 ↓
┌───────────────────────────▼─────────────────────────────────┐
│  🛠️ skills/   409 技能 / 18 领域大类（双层 <大类>/<来源>/）      │
│       安全 85 · 逆向 63 · 前端 27 · 编排 15 · 后端 25 · …       │
└─────────────────────────────────────────────────────────────┘
```

| 层 | 职责 | 关键不变量 |
|:--|:--|:--|
| 🔌 `adapters/` | 把核心挂载到各家 Agent 入口 | 保持薄，只触发 + 指路，不复制规范 |
| 🧠 `framework/core/` | 流程的唯一真相 | 改流程只改 core，适配器跟着指 |
| ★ `state-systems/` | 项目状态的持久落点 | 状态先于动作，开工先恢复 |
| 🛠️ `skills/` | 执行阶段委托的具体能力 | 去重优先级 `ours > codex > cskills` |

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
| 5 | **execute** | 先读后改，只做必要改动，区分事实/推断/假设 |
| 6 | **validation gate** | 完成必须有与范围匹配的证据，不靠口头声明 |
| 7 | **docs & state sync** | 把成果分类回写四态系统 |
| 8 | **git & delivery gate** | commit / push / PR 前过 readiness 检查 |
| 9 | **evolution** | 重复模式转成保守的沉淀建议（observe → suggest → approve → apply）|

> ⚖️ 轻量任务可裁剪阶段，但**不跳过**状态恢复、权威判断、验证推理。

</details>

---

## 🛠️ 能力库（409 技能 · 18 大类）

执行阶段委托的具体技能，三源合并去重，双层结构 `<领域大类>/<来源>/<skill>/`：

| 🏷️ 领域 | 数量 | 🏷️ 领域 | 数量 | 🏷️ 领域 | 数量 |
|:--|:-:|:--|:-:|:--|:-:|
| 安全工程 | 85 | 移动跨端 | 18 | 数据分析 | 7 |
| 逆向工程 | 63 | 云基础设施 | 17 | 硬件系统 | 8 |
| 前端 UI | 27 | AI 自动化 | 18 | 产品增长 | 8 |
| 工作流编排 | 15 | 内容创作 | 14 | | |
| 后端 API | 25 | 支付电商 | 12 | | |
| 通用工程 | 26 | 地图位置 | 11 | | |
| 质量交付 | 24 | 研究知识 | 10 | | |
| 编程语言 | 21 | | | | |

技能按通用性分级：**🟢 通用 360 · 🟡 半通用 49 · 🔵 项目定制 0**（见 [`skills/TIERS.md`](skills/TIERS.md)）。完整索引见 [`skills/README.md`](skills/README.md)。

---

## 🚀 快速上手

把框架用到一个目标项目：

```text
1. 先打项目地基：若目标目录没有 Git 且不在父级仓库中，让 Agent 执行 git init
2. 补齐 .gitignore、README.md、AGENTS.md / CLAUDE.md、docs/INDEX.md 和基础验证命令
3. 复制 framework/state-systems/templates/ 的四个文件到目标项目
   （或映射到项目已有的等价文档），并写入当前目标/约束/焦点
4. 让 Agent 第一次只做：scan + state restore + 路由分析，先不改业务代码
5. 状态恢复与路由稳定后，再带验证闸门和文档同步跑完整任务
6. 验证通过且本轮是单一逻辑改动时，默认允许 Agent 自动创建原子 commit
```

### 新项目地基门禁

每个新项目、空目录或首次接入 workflow 的项目，默认先补这几块地基：

| 地基项 | 默认动作 |
|:--|:--|
| Git | 没有 `.git/` 且不在父级仓库中时执行 `git init`；已有仓库只读状态，不重建、不改历史 |
| 忽略文件 | 生成或合并 `.gitignore`，覆盖依赖、构建产物、日志、环境变量、本地缓存和密钥 |
| Agent 入口 | 生成或更新 `AGENTS.md` / `CLAUDE.md`，指向四态系统和项目真相文档 |
| 四态系统 | 初始化或映射日志、需求、记忆、进度，并写入当前目标、约束、焦点和下一步 |
| 文档入口 | 保证 `README.md` 与 `docs/INDEX.md` 能说明项目状态、文档地图和验证入口 |
| 验证入口 | 记录 install / dev / test / lint / build 命令；未知就标 `待确认`，不伪造 |
| 首次提交 | 地基补齐并验证后创建原子 commit；不默认 push、merge、PR 或配置远端 |

> 🧱 想从一个想法直接开新项目，用 `project-inception-docs`：它会把 Git、忽略文件、Agent 入口、四态系统、README、PRD、架构、测试验收和运维文档一起打成启动包。

适合第一轮试跑的提示词：

```text
🗣️ 先扫描当前仓库，识别规则/技能/文档/验证入口，恢复四态系统状态，只做路由分析。
🗣️ 如果当前项目还没有 Git、.gitignore、AGENTS/CLAUDE、README、docs/INDEX 或四态系统，先补齐项目地基。
🗣️ 使用 project-inception-docs，把这个想法初始化成可开发项目，并生成启动文档包。
🗣️ 判断这个需求该走 audit / implement / fix / review，并说明验证与文档同步策略。
🗣️ 检查当前改动在 commit 前是否已满足验证、文档同步和交付三道闸门；满足时直接原子 commit。
```

> 🧪 想看完整跑一遍的样子？[`framework/validation/sample-project/`](framework/validation/sample-project/) 是个可直接重跑的最小样板，附 dogfood 验证报告。

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
│   ├─ core/                ★ 单一真相：10 阶段/状态/路由/权威/验证/演进
│   ├─ state-systems/       ★ 四态系统说明 + drop-in 模板
│   ├─ adapters/            各家 Agent 适配登记（CC / Codex）
│   └─ validation/          dogfood 样板 + 端到端验证报告
├─ 🛠️ skills/              能力库：409 技能 / 18 大类
│   ├─ README.md             领域索引
│   ├─ TIERS.md              分级（通用/半通用；项目定制不进入开源库）
│   ├─ _merge-manifest.csv   三源合并对照表
│   └─ <大类>/<来源>/<skill>/
└─ 🔧 tools/skill-merge/    可复现的能力库合并脚本
```

---

## 🗺️ 路线图

- [x] 🧱 中立核心（`framework/core/` + `state-systems/`）
- [x] 📑 四态系统 drop-in 模板
- [x] 🤖 Claude Code 适配器
- [x] 🤖 Codex 适配器
- [x] 🛠️ 三源合并丰富能力库（409 技能 / 18 大类）
- [x] 🏷️ 能力库分级标记 + 项目定制项清理
- [x] 🧪 Claude Code 侧端到端 dogfood 跑通
- [x] 🧪 Codex 侧端到端实测
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
