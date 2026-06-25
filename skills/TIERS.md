# 技能分级与近义变体（阶段 6）

> 给 398 技能打「通用 / 半通用 / 项目定制」标记。
> 标记只落在 `_merge-manifest.csv` 的 `tier` 列与本文件，**不写进各 SKILL.md frontmatter**（沿用「不标记直接融合」偏好）。

## tier 分布

| 分级 | 数量 | 含义 | 代表 |
|---|---|---|---|
| 通用 | 323 | 纯工程/领域模式，跨项目可直接复用 | engineering-core、programming-languages、reverse-engineering、多数 security |
| 半通用 | 49 | 厂商/产品绑定但可跨项目复用，或需轻度去项目化 | payments(stripe…)、maps(高德…)、figma-*、notion-*、各 deploy |
| 项目定制 | 26 | 强绑 J-SOP 或特定 runtime/产品 | ours/source-command-*、ours 的 J-SOP 技能、codex 的 audit/status/sprint 等(硬读 J-SOP 文件)、floatly-* |

分级规则见 `../tools/skill-merge/tier_tag.py`（会刷新 `_merge-manifest.csv` 的 `tier` 列并重列变体簇）。

## 已做的精简

- **移除 `anna-*` 家族（18 个）**：均与非-anna 版（`python-dev`、`go-dev`、`ui-design` 等）重复，统一保留非-anna 版。
- **移除 `coff0xc-*` 家族（18 个）**：安全合规/工程打包技能，与库内细分技能重叠，整体下线。
- 合计下线 36 个，库从 434 → **398**。

## 剩余近义变体

去除上述两家族后，仅剩 1 处根名相近：

| 主题 | 并存技能 | 处理 |
|---|---|---|
| js/ts | `js-ts-dev`(codex) ｜ `typescript-development`(cskills) | 保留 —— 前者偏 JS+TS 通用、后者专精 TS 进阶，定位不同 |

其余 396 个无近义冲突。
