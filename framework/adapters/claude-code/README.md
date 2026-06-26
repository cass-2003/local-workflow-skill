# Claude Code 项目根入口

这目录提供的是 **Claude Code 的项目根薄入口模板**，用于和 Codex 的 `AGENTS.md` 形成对称关系。

## 包含内容

- `CLAUDE.md`
  - 可复制到目标项目根
  - 声明四态工作流默认工作方式
  - 指向 `framework/core/*` 作为单一真相

## 适用场景

- 你希望 Claude Code 在进入一个新仓库时，先按四态工作流思考
- 你希望项目级入口和 Codex 的 `AGENTS.md` 保持对称
- 你想保留 skill 体系，但再加一层仓库根默认入口

## 不替代什么

这个模板不替代：

- `skills/workflow-orchestration/ours/project-workflow/SKILL.md`
- 项目内已有的本地领域 skill
- 项目真相文档（四态系统、README、spec、runbook）

它只做项目级薄入口，不做执行细节主源。
