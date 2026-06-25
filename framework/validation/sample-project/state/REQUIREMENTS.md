# 项目需求 · Project Requirements

## 当前目标

一个极简任务清单库，提供增、改状态、查、按状态过滤四种能力。

## 需求清单

| ID | 需求 | 验收标准 | 状态 | 关联进度 |
|----|------|----------|------|----------|
| REQ-001 | 增/标记完成/列出任务 | add/mark_done/list 三函数，对应测试通过 | done | - |
| REQ-002 | 按状态过滤任务 | `filter_by_status(status)` 返回该状态全部任务，test_filter_by_status 通过 | open | PROGRESS#进行中 |

## 约束与非目标

- 约束：纯标准库，无外部依赖。
- 非目标：持久化、并发、CLI 入口（本期不做）。
