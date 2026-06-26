# 阶段 5 · Dogfood 端到端验证（Claude Code 侧）

> 日期：2026-06-26 ｜ 执行：以 Agent 身份照 `core/01-workflow.md` 十阶段，对一个最小样板项目真实跑一遍。
> 结论：**框架端到端可跑通**，产出真实成果（代码 + 通过的测试 + 回写的四态系统）。发现 3 处可改进点，已就地小修 2 处。

## 测试设置

- 样板项目：极简 Python 任务清单库（`src/tasks.py` + pytest）。
- 四态系统**故意放在 `state/` 子目录**（而非根），以检验"不强制固定位置"的发现能力。
- 任务：落地 `REQ-002`（`filter_by_status`），其测试基线**预先失败**（2 passed / 1 failed）。

## 十阶段实跑记录

| 阶段 | 结果 | 备注 |
|---|---|---|
| 0 scan | ✅ | 识别出 src/tests/state 与四态文件 |
| 1 state restore | ✅ | 四态文件在 `state/` 子目录仍被按名发现；恢复出"REQ-002 进行中、D-001 全局态设计" |
| 2 intent | ✅ | implement |
| 3 authority | ✅ | 项目无本地 rules；真相=四态+代码；执行=能力库；兜底=全局 |
| 4 route | ⚠️ | intent→`implement`；二级路由停在"大类"，未给到具体技能（见发现 2） |
| 5 execute | ✅ | 先读后改，最小新增 `filter_by_status` |
| 6 validate | ✅ | V2 级：`pytest` → 3 passed |
| 7 sync | ✅ | LOG 加条目、REQUIREMENTS REQ-002→done、PROGRESS 归档；MEMORY 无新决策正确跳过 |
| 8 deliver | ✅ | 样板非 git 仓 → "ready for handoff without Git action"（框架已覆盖该情形） |
| 9 evolve | ✅ | 产出本报告 + 下列改进 |

## 发现

### 发现 1 ·（已修）路由名与技能名撞名
intent 路由名 `implement / fix / audit / review / status / sprint / sync-docs` 曾与能力库里的旧同名命令封装技能撞名，Phase 4 时"路由到 implement"容易被误解为"委托给叫 implement 的技能"。
→ 已在 `core/03-routing.md` 加消歧说明：路由名是**流程动作**，不是技能名；旧同名命令封装属于 runtime/project 绑定项，不进入通用能力库。

### 发现 2 ·（已修）二级路由止于大类，缺"大类内选具体技能"
`core/03-routing` 的二级路由把问题域映射到**大类**（如 programming-languages，21 个技能），但没给"21 选 1"的判据。trivial 改动我按"轻量任务可跳过委托"内联完成，但非平凡任务存在选择空窗。
→ 已在 `core/03-routing.md` 补一节：大类内用各技能 `description`（frontmatter）做终选；trivial 改动可不委托直接内联。

### 发现 3 ·（仅记录）四态发现对子目录依赖"文件名够标准"
模板默认根级 `LOG.md` 等；样板放 `state/` 仍被发现，因文件名是字面标准名。若项目用非标准名又放深目录，关键词发现可能漏。
→ 已在 `core/02-state-systems.md` 的发现线索里补常见承载目录（`state/`、`docs/`、`.agent-os/`）。

## 待办（用户侧，本环境替代不了）
- Codex 侧同样跑一遍：把 `framework/adapters/codex/AGENTS.md` 装进同款样板，在真实 Codex 里走一遍，核对四态读写与 CC 侧一致。
