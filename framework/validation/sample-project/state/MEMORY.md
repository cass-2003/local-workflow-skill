# 项目记忆 · Project Memory

## 架构与系统地图

- `src/tasks.py`：核心，模块级全局 `_TASKS` 列表 + `_NEXT_ID` 自增计数。
- `tests/test_tasks.py`：pytest，每个用例前 `setup_function` 清空全局状态。

## 关键决策

### D-001 · 用模块级全局存任务，不引入类

- **决定**：任务存模块级 `_TASKS`，函数式 API。
- **为什么**：本期是最小库，类会过度设计；非目标里已排除持久化与并发。
- **影响**：测试需在每个用例前 reset 全局；后续若要多实例再重构为类。
- **时间**：2026-06-24

## 已知坑

- `gotcha` 测试必须 `setup_function` 清空 `_TASKS`/`_NEXT_ID`，否则用例间互相污染。
