# AGENTS.md · 四态工作流（样板项目 Codex 入口）

> 这是 dogfood 样板项目的 Codex 适配入口。流程规范的**单一真相**在框架中立核心，本文件只负责被触发并指路。

## 工作方式（10 阶段）

接到任务时按固定顺序推进：

```text
scan → state restore → intent → authority → route → execute → validate → sync → deliver → evolve
```

- 任何实质性工作前，先从 `state/` 下的**四态系统**（LOG / REQUIREMENTS / MEMORY / PROGRESS）恢复项目状态。
- 若未来迁移到没有 `state/` 的新项目，先初始化最小四态骨架，再继续实现。
- 完成必须有与范围匹配的验证证据（本项目：`py -3 -m pytest -q tests/`），不靠口头声明。
- 变更后把成果分类回写四态系统。
- 若验证通过且改动属于单一逻辑变更，默认创建原子 commit。

## 规范指针（单一真相在中立核心）

本样板在框架仓库内，核心相对路径如下（若把样板复制出去单独跑，按实际位置改前缀）：

| 需要什么 | 读这里 |
|---|---|
| 工作流 10 阶段细节 | `../../core/01-workflow.md` |
| 四态系统发现/读写 | `../../core/02-state-systems.md` |
| 意图→能力库路由 | `../../core/03-routing.md` |
| 验证/文档/交付闸门 | `../../core/05-validation.md` |

## 本次 dogfood 任务

落地 `REQ-002`：实现 `src/tasks.py` 的 `filter_by_status(status)`，让 `tests/test_tasks.py::test_filter_by_status` 由红转绿，并把成果回写四态系统。
