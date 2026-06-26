# Codex 全局安装说明

> 目标：把「四态工作流框架」挂到**机器级 Codex 默认入口**，让没有项目本地 workflow 的仓库也能先按同一套骨架工作。

## 适用范围

适用于：

- 你想让 Codex 在任意仓库里都先按四态工作流思考
- 仓库本地还没有自己的 `AGENTS.md`
- 你希望保留机器级兜底，但仍允许项目本地规则覆盖

不适用于：

- 直接替代项目本地 `AGENTS.md`
- 把机器级工作流写成高优先级硬约束，覆盖项目内已有流程

## 安装原则

机器级入口只做两件事：

1. 声明默认工作方式：scan → state restore → intent → authority → route → execute → validate → sync → deliver → evolve
2. 指向这套框架的真实核心位置

不要在机器级入口里复制 `framework/core/*` 细则，也不要把项目特有规则抬升为全局规则。

默认自动行为建议：

- 若仓库没有本地四态系统，先初始化最小骨架
- 完成单一逻辑改动且验证通过后，允许默认 auto-commit
- 不要默认 auto-push / auto-merge / auto-PR

## 推荐机器级入口

文件位置：

- `C:\Users\Administrator\.codex\AGENTS.md`

建议结构：

1. 保留现有全局说明（如服务器 inventory）
2. 追加一节“Global Workflow Default”
3. 明确写出“项目本地 `AGENTS.md` / repo rules 优先于本全局入口”

## 推荐核心路径

当前工作区内这套框架核心实际位于：

`J:\07-Codex与AI工具\05-工作区与技能\skills-workspace\local-skills-workspace\framework\core\`

若将来迁移仓库位置，只需更新机器级 `AGENTS.md` 中的路径指针。

## 验证标准

机器级安装完成后，至少确认：

- 全局 `AGENTS.md` 仍保留旧说明且无冲突
- 新仓库没有本地 workflow 时，Codex 能看到四态工作流默认入口
- 新仓库缺少四态系统时，Codex 会先补最小骨架，再继续开发
- 单一逻辑改动在验证通过后，会进入 ready for commit / 自动提交路径
- 有本地 `AGENTS.md` 的仓库里，项目本地入口优先

## 风险提示

- 这是**全局兜底入口**，不是项目内唯一真相
- 真正流程细节仍只在 `framework/core/*`
- 如果路径迁移，机器级入口会失效，需要一起更新
