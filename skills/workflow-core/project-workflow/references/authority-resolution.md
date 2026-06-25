# Authority Resolution

## Objective

在开始路由或执行之前，先判断当前仓库里哪些层分别承担以下职责：

1. 硬约束
2. 命令语义
3. 执行细节
4. 项目真相
5. 全局兜底

不要试图找一个“唯一真相文件”替代所有层。

## Candidate Source Families

优先按本地性从高到低检查：

1. 仓库根指令文件
   - `AGENTS.md`
   - `CLAUDE.md`
   - `README*`
   - 其他明确面向 agent 的根说明
2. 项目本地规则层
   - `.codex/rules/*`
   - 其他本地 rules 目录
3. 项目本地 workflow 包装层
   - `.codex/workflows/*`
   - `.claude/commands/*`
   - 其他 workflow wrapper 目录
4. 项目本地执行 skill 层
   - `.codex/skills/*`
   - `.agents/skills/*`
   - 其他项目本地 skills 目录
5. 镜像或插件副本
   - `.agents/plugins/*`
   - 其他复制或镜像目录
6. 项目真相文档
   - `docs/*`
   - `specs/*`
   - `runbooks/*`
   - 其他状态、基线、计划、研究、架构文档
7. 机器全局 skill
   - `~/.codex/skills`
   - `~/.agents/skills`

## Resolution Rules

- 本地优先，最后才看全局。
- 按职责分层解析，不要让一个来源覆盖全部角色。
- 有更本地、更有效的来源时，不要让镜像或全局版本反客为主。
- 文档和代码发生冲突时，优先相信“更新、更本地、且可验证”的那一层。

## Role Mapping

| 角色 | 优先来源 |
|---|---|
| host instructions | 根目录 instruction files |
| hard constraints | 项目本地 rules |
| command semantics | 项目本地 workflows / commands |
| execution detail | 项目本地 skills |
| project truth | 当前文档 + 当前代码 |
| generic fallback | 机器全局 skills |

## Drift Signals

出现以下情况时，应判为漂移或迁移残留：

- 引用了已经不存在的路径族
- 使用了明显过时的文档名或目录名
- 镜像内容和本地主源明显不一致
- wrapper 描述的命令和真实仓库布局不匹配
- 更本地的来源已经给出不同且更可信的约束

## Output Template

```md
## Authority Resolution

- Rules source:
- Workflow source:
- Execution skills source:
- Truth docs source:
- Global fallback source:
- Drift detected:
- Notes:
```
