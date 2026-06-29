# 技能分级与变体（阶段 6）

> 给 565 技能打「通用 / 半通用」标记；项目定制项不进入开源通用库。
> 标记只落在 `_merge-manifest.csv` 的 `tier` 列与本文件，**不写进各 SKILL.md frontmatter**（沿用「不标记直接融合」偏好）。

## tier 分布

| 分级 | 数量 | 含义 | 代表 |
|---|---|---|---|
| 通用 | 482 | 纯工程/领域模式，跨项目可直接复用 | engineering-core、frontend-ui、backend-api、mobile-crossplatform、programming-languages、reverse-engineering、多数 security、business-operations、product-management、project-inception-docs |
| 半通用 | 83 | 厂商/产品绑定但可跨项目复用，或需轻度去项目化 | payments(stripe…)、maps(高德…)、figma-*、notion-*、Render、Expo、Airtable、各 deploy |
| 项目定制 | 0 | 强绑单一项目、产品、旧命令封装或私有上下文的技能不进入本仓库 | 已移除 source-command-*、具体项目 UI/扩展、运行时命令封装、迁移/宠物样本 |

分级规则见 `../tools/skill-merge/tier_tag.py`。

## anna-/coff0xc- 前缀已去除

原来有 18 个 `anna-*` + 18 个 `coff0xc-*` 前缀技能。经逐对内容对比（词汇 Jaccard 0.03–0.39），确认它们与库内同名技能**并非重复**——内容、篇幅、风格都不同（anna 系多为精简触发式规范，部分第三方授权导入版更偏实战排障，篇幅常差数倍）。因此**全部保留、仅去前缀**：

- **26 个直接去前缀**：去掉后无路径冲突（含 7 个同名但位于不同来源层、靠双层结构天然分开的技能）。
- **10 个真撞名**（同 `<域>/codex/` 下已有同名）取 `-2` 后缀：`api-design-2`、`shell-scripting-2`、`go-dev-2`、`js-ts-dev-2`、`python-dev-2`、`code-audit-2`、`git-workflow-2`、`reverse-engineering-2`、`mobile-security-2`、`blockchain-security-2`。

## community 授权导入

`community` 来源层统一承载许可清晰的第三方授权技能，含开源与已获授权来源；其中 108 个 MIT 许可技能补齐业务、营销、合规、研究、生产力、管理和发布等领域。导入原则：

- 只收通用或可跨项目复用的技能。
- 不收 router/index、项目包装、私有上下文或偏角色扮演的 executive persona。
- 统一 frontmatter 为 `name` / `description`，许可与来源放在 provenance 目录。

来源记录：`../tools/skill-merge/provenance/claude-skills-community/`。

## OpenAI plugins 官方技能导入

从 OpenAI 官方 `openai/plugins` 仓库筛选导入 34 个许可证明确的 plugin skills，补强 Render、Expo、Airtable 与 Supabase/Postgres 场景。导入原则：

- 只导入 skill 或插件目录明确 MIT 许可的内容。
- 不导入根仓库未声明许可、许可不明确或过度垂直的插件技能。
- 统一放入 `codex` 来源层；保留 bundled `references/`、`scripts/`、`assets/`，但 `SKILL.md` frontmatter 归一化为 `name` / `description`。
- 已存在的 `render-deploy` 不重复导入。

来源记录：`../tools/skill-merge/provenance/openai-plugins/`。

## App 与小程序通用技能补强

本仓库新增 8 个 `mobile-crossplatform/ours` 技能，补齐真实 App / 小程序项目常见地基能力：App 架构、离线同步、推送、发布运营、小程序架构、微信小程序工程、登录支付闭环、Taro/uniapp 跨端适配。

完成 App / 小程序补强后，技能总数现为 **565**。
