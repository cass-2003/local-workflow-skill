# <项目名称>

> 一句话定位：<这个项目为谁解决什么问题，第一版交付什么结果。>

## 当前状态

- 阶段：<idea / docs / prototype / MVP / beta / production>
- 当前焦点：<本阶段最重要的一件事>
- 最近验证：<命令、人工验收或未验证原因>
- 仓库地基：<Git/.gitignore/AGENTS/四态/验证入口是否就绪>

## 项目地基

| 项 | 状态 | 说明 |
|---|---|---|
| Git | <已初始化/待初始化/不适用> | <若未初始化，说明原因或下一步> |
| 需求访谈 | <已完成/进行中/待启动> | <空目录或新想法先访谈；已确认内容与待确认项> |
| `.gitignore` | <已就绪/待补> | <覆盖依赖、构建产物、日志、环境变量和缓存> |
| Agent 入口 | <AGENTS.md/CLAUDE.md/待补> | <AI 协作入口和本地规则位置> |
| 四态系统 | <完整/部分/缺失> | <state/LOG、REQUIREMENTS、MEMORY、PROGRESS> |
| 文档索引 | <已就绪/待补> | <docs/INDEX.md 是否能作为阅读地图> |
| 验证命令 | <已确认/待确认> | <install/dev/test/lint/build> |
| 首次提交 | <已提交/待提交/不适用> | <地基验证后进入原子 commit 闭环；不默认 push> |

## 快速开始

```bash
<安装依赖命令>
<本地启动命令>
<测试或验证命令>
```

## 文档入口

- [文档索引](docs/INDEX.md)
- [PRD](docs/PRD.md)
- [信息架构与页面原型](docs/信息架构-页面原型.md)
- [技术架构](docs/architecture/技术架构.md)
- [开发路线图](docs/planning/开发路线图.md)

## 项目结构

```text
<按当前项目实际目录填写>
```

## 关键约束

- <约束 1>
- <约束 2>
- <非目标或边界>
- 未经确认的需求、角色、权限、数据来源和商业化方案必须标 `待确认`，不要当成已确定事实。

## 协作与记录

- Agent 入口：<AGENTS.md / CLAUDE.md / 待补>
- 状态系统：<state/LOG.md、REQUIREMENTS.md、MEMORY.md、PROGRESS.md>
- 提交策略：<完成并验证修改后进入原子 commit 闭环；多逻辑变更拆成多个 commit；不默认 push>

## 下一步

1. 若需求仍不清晰，继续需求访谈并更新 `state/REQUIREMENTS.md` 与 `state/PROGRESS.md`
2. <下一步 2>
3. <下一步 3>
