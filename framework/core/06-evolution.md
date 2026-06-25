# 演进机制（保守沉淀）

把重复出现的流程经验转成长期可复用的框架改进，而不是每次重新解释。**默认保守**：先观察，不急着改。

## 默认生命周期

```text
observe → cluster → suggest → approve → apply → verify
```

默认停在 `suggest`，不要直接跳到 `apply`。

## 观察触发信号

- 引用路径失效
- 找到了更好的本地权威源
- 同一类路由判断反复出现
- 同一类验证缺口反复出现
- 镜像 / 适配副本与中立核心出现漂移
- 同一段人工说明重复出现

## 建议阈值

满足任一即可形成建议：

- 一个强结构信号 + 一次确认
- 三次以上重复出现的同类模式

## 应用规则

同时满足才进入实际修改：

- 变更是低风险、结构性的
- 已获得明确批准

优先更新**中立核心主源**，不要先改适配副本。

## 模板

观察记录：

```md
## Observation

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
## Evolution Suggestion

- Target:                <core / state-systems / skills / adapters>
- Type: `add` / `replace` / `deprecate` / `move-to-reference`
- Reason:
- Evidence:
  - task/session:
  - files inspected:
  - repeated pattern:
- Suggested change:
- Risk if not updated:
```
