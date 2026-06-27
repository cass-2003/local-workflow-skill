# 技能分级与变体（阶段 6）

> 给 439 技能打「通用 / 半通用」标记；项目定制项不进入开源通用库。
> 标记只落在 `_merge-manifest.csv` 的 `tier` 列与本文件，**不写进各 SKILL.md frontmatter**（沿用「不标记直接融合」偏好）。

## tier 分布

| 分级 | 数量 | 含义 | 代表 |
|---|---|---|---|
| 通用 | 390 | 纯工程/领域模式，跨项目可直接复用 | engineering-core、programming-languages、reverse-engineering、多数 security、business-operations、product-management、project-inception-docs |
| 半通用 | 49 | 厂商/产品绑定但可跨项目复用，或需轻度去项目化 | payments(stripe…)、maps(高德…)、figma-*、notion-*、各 deploy |
| 项目定制 | 0 | 强绑单一项目、产品、旧命令封装或私有上下文的技能不进入本仓库 | 已移除 source-command-*、具体项目 UI/扩展、运行时命令封装、迁移/宠物样本 |

分级规则见 `../tools/skill-merge/tier_tag.py`。

## anna-/coff0xc- 前缀已去除

原来有 18 个 `anna-*` + 18 个 `coff0xc-*` 前缀技能。经逐对内容对比（词汇 Jaccard 0.03–0.39），确认它们与库内同名技能**并非重复**——内容、篇幅、风格都不同（anna 系多为精简触发式规范，部分同名版是 cskills 的"实战排障版"，篇幅常差数倍）。因此**全部保留、仅去前缀**：

- **26 个直接去前缀**：去掉后无路径冲突（含 7 个"同名但在 `cskills` 源文件夹、靠双层结构天然分开"的）。
- **10 个真撞名**（同 `<域>/codex/` 下已有同名）取 `-2` 后缀：`api-design-2`、`shell-scripting-2`、`go-dev-2`、`js-ts-dev-2`、`python-dev-2`、`code-audit-2`、`git-workflow-2`、`reverse-engineering-2`、`mobile-security-2`、`blockchain-security-2`。

## community 开源导入

首批 `community` 来源导入 30 个 MIT 许可技能，补齐业务运营、商业策略、财务指标、产品管理、项目管理和研究运营领域。导入原则：

- 只收通用或可跨项目复用的技能。
- 不收 router/index、项目包装、私有上下文或偏角色扮演的 executive persona。
- 统一 frontmatter 为 `name` / `description`，许可与来源放在 provenance 目录。

来源记录：`../tools/skill-merge/provenance/claude-skills-community/`。

完成首批 community 扩容后，技能总数现为 **439**。
