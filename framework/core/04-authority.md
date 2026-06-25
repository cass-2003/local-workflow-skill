# 权威解析（多 Agent 中立版）

在路由或执行前，先判断仓库里哪些层分别承担：① 硬约束 ② 命令语义 ③ 执行细节 ④ 项目真相 ⑤ 全局兜底。不要试图找一个"唯一真相文件"替代所有层。

## 候选来源族（按本地性从高到低）

为支持多 Agent，候选来源同时覆盖各家 runtime 的本地目录约定：

1. **仓库根指令文件**
   - `AGENTS.md`（Codex 等）、`CLAUDE.md`（Claude Code）、`README*`、其他面向 agent 的根说明
2. **项目本地规则层**
   - `.codex/rules/*`、`.claude/rules/*`、`.cursor/rules/*`、`.agents/rules/*`
3. **项目本地 workflow / 命令包装层**
   - `.codex/workflows/*`、`.claude/commands/*`、其他 workflow wrapper 目录
4. **项目本地执行能力层**
   - `.codex/skills/*`、`.claude/skills/*`、`.agents/skills/*`、本仓库的 `skills/*`
5. **镜像或插件副本**
   - `.agents/plugins/*`、其他复制或镜像目录
6. **项目真相文档（四态系统）**
   - `LOG.md` / `REQUIREMENTS.md` / `MEMORY.md` / `PROGRESS.md` 及其等价物
   - `docs/*`、`specs/*`、`runbooks/*` 等状态、基线、计划、研究、架构文档
7. **机器全局能力**
   - `~/.codex/skills`、`~/.claude/skills`、`~/.agents/skills`

## 解析规则

- 本地优先，最后才看全局。
- 按职责分层解析，不让一个来源覆盖全部角色。
- 有更本地、更有效的来源时，不让镜像或全局版本反客为主。
- 文档与代码冲突时，优先相信"更新、更本地、且可验证"的那一层。

## 角色映射

| 角色 | 优先来源 |
|---|---|
| host instructions | 根目录 instruction files |
| hard constraints | 项目本地 rules |
| command semantics | 项目本地 workflows / commands |
| execution detail | 项目本地 skills（含本仓库 `skills/`） |
| project truth | 四态系统 + 当前代码 |
| generic fallback | 机器全局 skills |

## 漂移信号

出现以下情况判为漂移或迁移残留：

- 引用了已不存在的路径族
- 使用了明显过时的文档名或目录名
- 镜像内容和本地主源明显不一致
- wrapper 描述的命令和真实仓库布局不匹配
- 更本地的来源已给出不同且更可信的约束

## 输出模板

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
