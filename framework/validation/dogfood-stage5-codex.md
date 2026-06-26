# 阶段 5 · Dogfood 端到端验证（Codex 侧）

> 日期：2026-06-26 ｜ 执行：以 Codex 入口 `AGENTS.md + agents/workflow.yaml` 为触发面，
> 在真实 `codex exec` 运行中对最小样板项目走一遍四态工作流十阶段。
> 结论：**Codex 侧已真实跑通**，可在样板里跑出与 Claude Code 侧一致的恢复/路由/验证/回写流程。

## 测试设置

- 样板项目：`framework/validation/sample-project/`
- 入口：
  - `AGENTS.md`
  - `agents/workflow.yaml`
- 四态系统位置：`state/` 子目录
- 任务：落地 `REQ-002`（实现 `filter_by_status(status)`，让 pytest 由红转绿）

## 测试方式

- 运行器：本机 `codex exec`
- 工作目录：样板项目的临时副本，保持 `AGENTS.md -> ../../core/*` 相对路径不变
- 任务提示：
  - 按四态工作流落地 `REQ-002`
  - 先扫描、恢复四态系统
  - 实现 `filter_by_status(status)`
  - 跑 pytest
  - 回写四态系统

## 入口结构检查

| 项目 | 结果 | 备注 |
|---|---|---|
| 仓库根 `AGENTS.md` 存在 | ✅ | 声明 10 阶段工作方式与核心指针 |
| `agents/workflow.yaml` 存在 | ✅ | Codex 角色描述已补齐 |
| 指向 `../../core/*` 的路径有效 | ✅ | 路径存在，可作单一真相 |
| 样板内四态文件可发现 | ✅ | `state/LOG.md` 等均存在 |

## 十阶段验证记录

| 阶段 | 结果 | 备注 |
|---|---|---|
| 0 scan | ✅ | 识别 `src/`、`tests/`、`state/`、`AGENTS.md`、`agents/workflow.yaml` |
| 1 state restore | ✅ | 从 `state/` 恢复出 `REQ-002` 为 open、`PROGRESS` 中有进行中项 |
| 2 intent | ✅ | implement |
| 3 authority | ✅ | 入口=样板 `AGENTS.md`；单一真相=`../../core/*`；项目真相=`state/* + 代码/测试` |
| 4 route | ✅ | 主路由 `implement`，二级路由到 Python 样板代码场景 |
| 5 execute | ✅ | Codex 在样板副本中补 `filter_by_status(status)` |
| 6 validate | ✅ | `py -3 -m pytest -q tests/` 复验通过（3 passed） |
| 7 sync | ✅ | `LOG / REQUIREMENTS / PROGRESS` 已真实回写；`MEMORY` 无新增决策，正确跳过 |
| 8 deliver | ✅ | 样板默认是验证夹具，可 handoff；是否 git 交付取决于宿主仓 |
| 9 evolve | ✅ | 形成本报告；确认 Codex 入口结构可推广到真实项目 |

## 与 Claude Code 侧对齐结果

- 四态恢复模型一致：都能从 `state/` 子目录恢复日志 / 需求 / 记忆 / 进度
- 主路由一致：`REQ-002` 都落到 `implement`
- 验证门槛一致：都以 `pytest` 作为 V2 证据
- 文档回写规则一致：都要求回写 `LOG / REQUIREMENTS / PROGRESS`

## 运行产物证据

- `src/tasks.py` 新增 `filter_by_status(status)`
- `state/REQUIREMENTS.md`：`REQ-002` 从 `open` → `done`
- `state/PROGRESS.md`：进行中项归档到已完成
- `state/LOG.md`：新增 2026-06-26 变更记录
- `py -3 -m pytest -q tests/`：`3 passed`

## 结论

Codex 侧此前缺的不是核心设计，而是两点：

1. 样板项目缺少 `agents/workflow.yaml`
2. 缺少真实 `codex exec` 的端到端验证记录

这两点补齐后，这套 workflow 已经从“模板已登记”推进到 **Codex 真实 dogfood 已跑通**。

## 后续建议

- 若要作为**机器级全局工作流入口**使用，再补一个全局安装说明与机器级 `AGENTS.md` 合并策略。
- 若要作为**跨项目 drop-in 包**使用，优先提供一份一键复制的安装目录建议（如 `.agent-os/framework/`）。
