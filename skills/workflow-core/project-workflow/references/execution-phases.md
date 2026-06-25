# Execution Phases

## Purpose

定义一条适合多数项目的标准工作流，让扫描、恢复、执行、验证、同步和交付有固定顺序。

## Phase 0: Workspace Scan

目的：

- 看清仓库里有哪些 instructions、rules、workflows、skills、docs
- 避免带着旧假设开工

输出：

- 可能的权威层
- 可能的任务域
- 可能的验证入口

## Phase 1: State Restore

目的：

- 先恢复项目状态，再决定怎么行动

至少寻找四类状态系统：

- `project-log`
- `project-requirements`
- `project-memory`
- `project-progress`

输出：

- 最近发生了什么
- 当前目标和约束是什么
- 有哪些已有知识和基线
- 当前做到哪里、还有什么阻塞

## Phase 2: Intent Classification

目的：

- 判断当前任务更像 status、audit、implement、fix、review、docs sync、git delivery 还是 workflow evolution

输出：

- 主意图
- 次意图
- 初步范围

## Phase 3: Authority Resolution

目的：

- 判断该信任哪一层的规则、哪一层的技能、哪一层的文档

输出：

- rules source
- workflow source
- execution skills source
- truth docs source
- fallback chain

## Phase 4: Route And Delegate

目的：

- 让合适的 skill 承担合适的工作

规则：

- 编排权保留在当前 workflow skill
- 执行细节优先委托给项目本地 skill
- 没有本地 skill 时才使用最接近的全局 fallback

## Phase 5: Task Execution

目的：

- 按当前任务类型完成分析、修改、修复、评审或同步

规则：

- 先读后改
- 只做必要改动
- 区分事实、推断和假设

## Phase 6: Validation Gate

目的：

- 防止“完成只靠口头声明”

输出：

- 已验证的内容
- 使用的命令或证据
- 未验证的部分和原因

## Phase 7: Docs And State Sync

目的：

- 确保项目状态面与当前成果一致

常见触发：

- 实现了新功能
- 修复了已知问题
- 结论或风险发生变化
- 计划、进度或使用方式发生变化

## Phase 8: Git And Delivery Gate

目的：

- 在 commit、push、PR、handoff 前确认已经 ready

检查项：

- diff 是否已检查
- validation 是否匹配范围
- docs sync 是否已考虑
- 是否存在不应隐式执行的破坏性 Git 动作

## Phase 9: Workflow Evolution

目的：

- 把重复模式转成更长期可复用的流程资产

输出：

- observation
- suggestion
- 或显式说明暂不需要沉淀
