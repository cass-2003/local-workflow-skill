# Skill Evolution

## Purpose

把重复出现的流程经验转成更长期可复用的 skill 改进，而不是每次都重新解释。

## Default Lifecycle

默认走这条链路：

1. `observe`
2. `cluster`
3. `suggest`
4. `approve`
5. `apply`
6. `verify`

默认停在 `suggest`，不要直接跳到 `apply`。

## Observation Triggers

出现这些信号时，应该考虑记录观察：

- 引用路径失效
- 找到了更好的本地权威源
- 同一类路由判断反复出现
- 同一类验证缺口反复出现
- 镜像 skill 和主 skill 出现漂移
- 同一段人工说明重复出现

## Suggestion Threshold

默认满足以下任一条件时，可以形成建议：

- 一个强结构信号，加一次确认
- 三次以上重复出现的同类模式

## Apply Rules

只有同时满足以下条件才进入实际修改：

- 变更是低风险、结构性的
- 已获得明确批准

优先更新主来源，不要先改镜像。

## Templates

观察记录：

```md
## Skill Observation

- Signal:
- Where found:
- Affected source family:
- Repeat count:
- Immediate risk:
- Candidate target:
- Notes:
```

演进建议：

```md
## Skill Evolution Suggestion

- Target:
- Type: `add` / `replace` / `deprecate` / `move-to-reference`
- Reason:
- Evidence:
  - task/session:
  - files inspected:
  - repeated pattern:
- Suggested change:
- Risk if not updated:
```
