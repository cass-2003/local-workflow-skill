---
name: "source-command-sync-docs"
description: "同步更新项目文档。触发词：更新文档、sync docs、归档。"
---

# source-command-sync-docs

Use this skill when the user asks to run the migrated source command `sync-docs`.

## Command Template

## 文档同步

当用户运行 `/sync-docs` 时，按实际改动同步文档：
1. `docs/_update-log.md`
2. `docs/SPRINT-PLAN.md`
3. 相关审计文档
4. 如文档结构变化，再更新 `docs/README.md` / `docs/audit/INDEX.md` / 归档计划

### 规则
- 先看 `git diff --stat HEAD` 再判断该改哪些文档；Git 命令默认在项目根目录 `J:\J-SOP 伴随式自动化助手` 执行
- 不要盲目移动或归档文件，先核对引用关系
- 若最新审计或交付口径已变化，文档必须优先反映真实状态
- 以 `docs/客户整改需求清单-2026-04-30.md` 为客户需求权威来源
