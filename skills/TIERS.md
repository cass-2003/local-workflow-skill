# 技能分级与近义变体（阶段 6）

> 给 434 技能打「通用 / 半通用 / 项目定制」标记，并列出可精简的近义变体簇。
> 标记只落在 `_merge-manifest.csv` 的 `tier` 列与本文件，**不写进各 SKILL.md frontmatter**（沿用「不标记直接融合」偏好）。
> 本阶段**只标记、只建议，不删除** —— 删哪些等你定夺。

## tier 分布

| 分级 | 数量 | 含义 | 代表 |
|---|---|---|---|
| 通用 | 323 | 纯工程/领域模式，跨项目可直接复用 | engineering-core、programming-languages、reverse-engineering、多数 security |
| 半通用 | 85 | 厂商/产品绑定但可跨项目复用，或需轻度去项目化 | payments(stripe…)、maps(高德…)、figma-*、notion-*、anna-*、coff0xc-*、各 deploy |
| 项目定制 | 26 | 强绑 J-SOP 或特定 runtime/产品 | ours/source-command-*、ours 的 J-SOP 技能、codex 的 audit/status/sprint 等(硬读 J-SOP 文件)、floatly-* |

分级规则见 `../tools/skill-merge/tier_tag.py`（可复跑，会刷新 `_merge-manifest.csv` 的 `tier` 列并重列变体簇）。

## 近义变体簇（18 簇 / 37 技能，可精简候选）

几乎全是 **`anna-X` 与非-anna 等价物**并存（外加 1 个 coff0xc 重复）。它们归一化根名相同、内容近似但出自不同作者/家族，合并时按「根名不同则保留」留下了双份：

| 主题 | 并存技能 |
|---|---|
| python | `python-dev` ｜ `anna-python-dev` |
| go | `go-dev` ｜ `anna-go-dev` |
| js/ts | `js-ts-dev` ｜ `anna-js-ts-dev` ｜ `typescript-development` |
| api-design | `api-design` ｜ `anna-api-design` |
| backend | `backend-engineering` ｜ `anna-backend-engineering` |
| shell | `shell-scripting` ｜ `anna-shell-scripting` |
| perf | `perf-engineering` ｜ `anna-perf-engineering` |
| test | `test-engineering` ｜ `anna-test-engineering` |
| code-audit | `code-audit` ｜ `anna-code-audit` |
| git-workflow | `git-workflow` ｜ `anna-git-workflow` |
| ui-design | `ui-design` ｜ `anna-ui-design` |
| apple | `apple-development` ｜ `anna-apple-development` |
| flutter | `flutter-development` ｜ `anna-flutter-development` |
| uniapp | `uniapp-development` ｜ `anna-uniapp-dev` |
| product-manager | `product-manager` ｜ `anna-product-manager` |
| reverse | `reverse-engineering` ｜ `anna-reverse-engineering` |
| mobile-security | `mobile-security` ｜ `anna-mobile-security` |
| blockchain-security | `blockchain-security` ｜ `coff0xc-blockchain-security` |

## 精简建议（待定，不自动执行）

1. **anna-\* 家族**：18 个 anna-* 都有非-anna 等价物。三选一policy：
   - (a) 全删 anna-*（统一用非-anna 版，库瘦 18 个）；
   - (b) 全保留 anna-*、删非-anna 版（若 anna 版质量更高）；
   - (c) 逐簇对比 `description` 与正文择优（最准、最慢）。
   建议默认 (a)，除非抽查发现 anna 版明显更好。
2. **coff0xc-blockchain-security**：与 `blockchain-security` 重叠，coff0xc 版属安全合规包，可保留或并簇。
3. 其余 396 个无近义冲突，保持现状。

> 决定 policy 后可写个 5 行脚本按 `tier`/簇批量删；删前 `git` 有快照可回滚。
