# Local Skills Workspace

这是一个用于整理、抽取、泛化和发布本地 Codex skill 的工作区仓库。

它当前不是单一 skill 的发布页，而是一个“技能提炼中台”：

- 一部分内容保留项目来源样本，方便我们回看经验从哪里来。
- 一部分内容会被抽成通用 skill，方便迁移到其他项目或全局环境。
- 其余内容按类别整理，逐步筛选哪些适合保留为通用能力，哪些仍然属于项目定制能力。

当前仓库的核心目标，是基于 `J:\J-SOP 伴随式自动化助手` 的已有实践，沉淀出一套更通用的项目工作流 skill，而不是直接复制某个项目的特殊流程。

## 仓库定位

把这个仓库理解成三层会更准确：

1. 技能整理区
2. 技能抽象区
3. 技能发布前工作区

也就是说，这里既保存“从项目里抽出来的参考样本”，也保存“已经去项目化后的通用版本”。

## 当前结构

仓库已经按类别重整，当前主目录如下：

```text
.
├─ README.md
└─ skills
   ├─ workflow-core
   ├─ engineering-core
   ├─ backend-infra
   ├─ frontend-extension
   ├─ data-sync-validation
   ├─ language-runtime
   └─ source-commands
```

当前各分类下的主要内容：

| 分类 | 说明 | 当前示例 |
|---|---|---|
| `workflow-core` | 工作流总控、状态恢复、路由、交付和流程演进 | `local-workflow`、`project-workflow` |
| `engineering-core` | 通用工程模式 | `api-versioning`、`structured-logging`、`feature-flags`、`monorepo` |
| `backend-infra` | 偏后端与基础设施实践 | `background-jobs`、`dockerfile-best`、`websocket-impl` |
| `frontend-extension` | 偏前端/插件/抓取侧模式 | `chrome-mv3-ext`、`css-modern-2025`、`dom-scraping` |
| `data-sync-validation` | 同步、校验、数据约束 | `validation-schema`、`validation-pipeline`、`sync-bidirectional` |
| `language-runtime` | 语言与运行时通用能力 | `datetime-timezones` |
| `source-commands` | 明显源于项目命令封装的 skill | `source-command-audit`、`source-command-status` 等 |

## 目前最重要的两个 workflow skill

`workflow-core` 下面现在保留了两个不同角色的 skill：

### `local-workflow`

这是“项目经验抽取版样本”。

它来自 J-SOP 里的本地工作流设计，已经把核心结构整理得比较清楚，但仍然更偏“从项目里抽出来的稳定写法”。它适合作为参考母本，用来看：

- 一个真实项目里，工作流编排 skill 通常会长成什么样
- authority resolution、routing、validation、git gate 这些层如何拆开
- skill 演进机制如何被放进 workflow 里

### `project-workflow`

这是“通用版工作流模板”。

它不是直接绑定某个项目名、某些固定文件名或某套业务语义，而是把经验抽成更通用的骨架：

- 先扫描工作区
- 再恢复项目状态
- 再解析权威和路由
- 再执行、验证、同步、交付
- 最后把重复模式转成 skill 演进建议

如果说 `local-workflow` 更像“来源样本”，那 `project-workflow` 更像“可迁移模板”。

## 从 J-SOP 抽出来的稳定经验

这次抽取里，真正被认为“值得通用化”的，不是具体文件名，而是这些稳定模式：

1. 开工前先做权威解析，不要直接套全局默认。
2. 做任何实质性工作前，先从项目文档恢复状态。
3. 用意图和范围做路由，不只靠关键词。
4. 完成声明必须经过与范围匹配的验证闸门。
5. 发生重要变更后，要考虑文档与状态同步。
6. 交付前要有 Git readiness gate。
7. 重复模式出现后，要有保守的 skill 自动沉淀机制。

这些模式比“某个项目叫 `SPRINT-PLAN.md`”更稳定，也更适合带去别的仓库。

## 四个通用状态系统

`project-workflow` 现在把项目状态抽象成四个系统，而不是绑定具体文件：

- `project-log`
  用来回答“最近发生了什么”。
- `project-requirements`
  用来回答“当前要满足什么”。
- `project-memory`
  用来回答“系统为什么这样设计”。
- `project-progress`
  用来回答“现在做到哪里了”。

这个抽象非常关键，因为不同项目会把这四类信息放在不同地方，但工作流本身其实都需要它们。

## skill 自动沉淀 / 补全优化

这里也保留了我们前面一直在讨论的“自动沉淀”机制，但刻意采用了保守流程。

默认链路不是“看到问题就自动改 skill”，而是：

1. `observe`
2. `cluster`
3. `suggest`
4. `approve`
5. `apply`
6. `verify`

典型触发信号：

- 引用路径失效
- 规则层和技能层发生漂移
- 同一类路由判断反复出现
- 同一类验证缺口反复出现
- 同一段人工解释反复被重说

这样做的目的，是让经验沉淀有审计链路，而不是让 skill 无约束膨胀。

## 哪些 skill 更偏通用，哪些仍需继续筛

目前可以粗分成两类：

### 更接近通用能力

- `workflow-core/project-workflow`
- `engineering-core/*`
- `backend-infra/background-jobs`
- `backend-infra/dockerfile-best`
- `backend-infra/websocket-impl`
- `data-sync-validation/validation-schema`
- `language-runtime/datetime-timezones`

这些通常描述的是工程模式、结构模式或跨项目复用逻辑。

### 仍带较强项目或场景绑定

- `source-commands/*`
- `frontend-extension/anti-detection`
- `frontend-extension/dom-scraping`
- `frontend-extension/chrome-mv3-ext`
- `data-sync-validation/sync-bidirectional`
- `data-sync-validation/validation-pipeline`
- `backend-infra/echo-go-server`

这些并不是没价值，而是更需要继续筛：

- 有些适合保留为“场景 skill”
- 有些需要明显去项目化后才能变成通用 skill
- 有些可能更适合只保留为参考样本，而不是直接发布

## 推荐用法

更推荐这样使用这个仓库：

1. 先把项目经验整理进分类目录。
2. 再区分“来源样本”和“通用模板”。
3. 优先把工作流骨架、验证闸门、状态系统这类稳定模式抽出来。
4. 对高场景绑定 skill 继续做筛选和去项目化改写。
5. 在多个项目试跑后，再决定哪些适合独立发布。

## 快速试跑

如果你要把 `project-workflow` 先拿到另一个项目里试跑，最小路径可以很简单：

1. 把 `skills/workflow-core/project-workflow/` 放进目标项目的本地 skills 目录。
2. 确认目标项目里至少存在一部分可被识别的本地层，例如 instructions、rules、skills、docs、验证脚本。
3. 第一次使用时，先让它只做扫描、状态恢复和路由判断，不要一上来就改代码。
4. 等 authority resolution 和 routing 稳定后，再让它带着验证闸门和 docs sync 一起跑完整任务。

比较适合第一轮试跑的提示词：

- `请使用 $project-workflow 先扫描当前仓库，识别 rules、skills、docs 和验证入口，只做状态恢复与路由分析。`
- `请使用 $project-workflow 先判断这个需求应该走 audit、implement、fix 还是 review，再说明验证和文档同步策略。`
- `请使用 $project-workflow 帮我检查当前改动在 commit 前是否已经满足 validation、docs sync 和交付闸门。`

## 下一步建议

这个仓库后面最值得继续增强的方向有三类：

1. 继续补 `project-workflow` 的前向测试样例。
2. 继续筛各分类 skill，给出“通用 / 半通用 / 项目定制”的标记。
3. 为自动沉淀机制补一套更标准的 observation 和 suggestion 产物模板。

## 当前结论

如果从“是否已经具备一个可复用的通用工作流骨架”这个角度看，答案已经是有了：

- `local-workflow` 负责保留来源经验
- `project-workflow` 负责承接通用化版本
- 其他分类 skill 作为后续筛选和继续提炼的素材库

这样仓库就不再只是“某一个 skill 的发布仓”，而是一个真正能持续整理、筛选、抽象和发布 skill 的工作区。
