---
name: "source-command-review"
description: "代码变更审查。对最近的 git diff 做质量 + 安全 + 一致性审查。触发词：review、审查、检查代码、看下改动。"
---

# source-command-review

Use this skill when the user asks to run the migrated source command `review`.

## Command Template

## J-SOP 代码审查

### 上下文恢复
1. `git diff --stat HEAD` 查看变更范围
2. Extension 编译：`cd "/j/J-SOP 伴随式自动化助手/j-sop-extension" && npx tsc --noEmit`
3. 如 diff 涉及 `j-sop-license-server`，追加：`cd "/j/J-SOP 伴随式自动化助手/j-sop-license-server" && go build ./...`
4. 不要在仓库根目录直接执行 `go build ./...`；仓库根不是 Go module

### 审查重点
1. 逻辑错误与错误行为
2. 未覆盖的边界条件
3. `null` / `undefined` 风险
4. 并发或竞态问题
5. 安全漏洞
6. 资源泄漏或清理不完整
7. API / 消息契约不一致
8. 缓存与状态正确性
9. 违反既有代码模式或约定

### 规则
- 优先并行做只读探索
- 不报告低置信、纯猜测问题
- 如果相关，可把高置信既有问题与本次 diff 分开列出
