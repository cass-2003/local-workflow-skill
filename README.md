# Local Workflow Skill

一个面向 Codex/本地技能体系的“本地工作流总控”技能原型。

它的目标不是替代项目文档，也不是重复各个项目内已有的 `audit`、`review`、`fix`、`implement` 技能，而是作为一层**工作流编排器**：

- 发现当前项目的本地权威源
- 把请求路由到合适的本地 skill 或全局 skill
- 在交付前施加验证与文档同步闸门
- 识别技能漂移、过期路径、镜像副本分叉，并提出 skill evolution 建议

## 适用场景

适合这些场景：

- 想为一个项目建立统一的本地工作流规范
- 项目里已经有多层 rules/workflows/skills，但缺一个总控入口
- 希望把 `status / audit / implement / fix / review / sync-docs / git` 串成一条标准流程
- 希望逐步沉淀技能，而不是每次都靠对话重复解释流程

## 当前结构

仓库里的 skill 本体放在 [local-workflow](./local-workflow/) 目录下，包含：

- `SKILL.md`
- `references/authority-resolution.md`
- `references/routing-matrix.md`
- `references/validation-gates.md`
- `references/execution-phases.md`
- `references/git-and-handoff.md`
- `references/skill-evolution.md`

## 设计原则

- 主 `SKILL.md` 保持精简，只放角色、路由、闸门和 references 导航
- 细节下沉到 `references/`
- 优先使用项目内已有的本地 skill，而不是重复发明
- 默认只做 `suggest` 级别的 skill evolution，不冲动自动改技能
- 不把单项目的瞬时状态硬编码成全局规则

## 推荐落地方式

当前仓库内容更适合作为：

1. 项目内原型
2. 前向测试样本
3. 后续提炼成全局 skill 的基础版本

如果你要在自己的仓库里使用，推荐先把 `local-workflow/` 放进项目内的技能目录，跑几轮真实任务，再决定是否全局化。

## 后续建议

- 做一次真实 forward-test
- 根据测试结果收敛 authority resolution 和 routing 细节
- 稳定后再推广到全局 `~/.codex/skills`
