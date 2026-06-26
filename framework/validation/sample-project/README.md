# Dogfood 样板项目

四态工作流框架的端到端测试夹具。**PRE 状态**：`REQ-002` 未实现，`test_filter_by_status` 待红。

```
src/tasks.py        极简任务库（缺 filter_by_status）
tests/test_tasks.py pytest（REQ-002 用例预期失败）
state/              四态系统：LOG / REQUIREMENTS / MEMORY / PROGRESS（故意放子目录，测发现能力）
AGENTS.md           Codex 适配入口（指向 ../../core）
```

## 基线

```bash
py -3 -m pytest -q tests/      # 预期 2 passed, 1 failed
```

## 怎么用它跑 dogfood

让 Agent（Claude Code 或 Codex）照框架十阶段处理一句话任务：

> 按四态工作流落地 REQ-002：先从 state/ 恢复四态系统，再实现 filter_by_status，跑 pytest 验证，最后把成果回写四态系统。

**期望结果**：实现 `filter_by_status` → `3 passed` → LOG 加条目、REQUIREMENTS REQ-002→done、PROGRESS 归档。

- **CC 侧**：已实测跑通，见 `../dogfood-stage5.md`。
- **Codex 侧**：入口结构已补齐（`AGENTS.md` + `agents/workflow.yaml`），验证记录见 `../dogfood-stage5-codex.md`。

> 跑完若想重置：`git checkout -- framework/validation/sample-project/`。
