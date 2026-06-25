---
name: sync-docs
description: "同步更新项目文档。触发词：更新文档、sync docs、归档。"
---

## 文档同步

1. `git diff --stat HEAD` 统计变更
2. 更新 `docs/_update-log.md` 追加记录
3. 更新 `docs/SPRINT-PLAN.md` 已完成项
4. 更新 `docs/audit/AUDIT-SUMMARY.md`（如有审计/修复）
5. 超过一周的旧报告移入 `docs/archive/`
