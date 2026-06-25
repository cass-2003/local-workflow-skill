# Git And Handoff

## Purpose

定义工作成果在进入 commit、push、PR 或 handoff 之前的最小交付闸门。

## Invoke Conditions

当任务涉及以下动作时，进入 Git / 交付阶段：

- commit
- branch
- push
- PR
- merge
- handoff

## Pre-Delivery Checks

- 检查实际 diff，而不是只凭记忆描述改动。
- 确认验证范围和改动范围匹配。
- 确认 docs / state sync 已考虑。
- 确认没有隐式执行破坏性 Git 动作。

## Honest Delivery States

只给当前证据支持得起的交付结论：

- not ready for delivery
- ready for commit
- ready for branch or PR flow
- ready for handoff without Git action

## Handoff Summary

handoff 应简洁包含：

- 改了什么
- 验证了什么
- 还有哪些不确定或未验证
- 下一步最有价值的动作是什么
