# 项目日志 · Project Log

> 日志系统：回答“最近发生了什么”。追加新条目在最上方，重要决策同步到 `MEMORY.md`。

---

## 2026-06-27

- `docs` 在 README 增加“自动产物契约”独立小节。
  - 触发：用户确认 README 需要把审计报告、状态回写和文档索引同步规则写得更明显。
  - 验证：新增小节链接 `framework/core/07-artifact-contracts.md`，并列出 audit、implement/fix、docs-sync、validation 的默认产物与同步要求。

- `change` 加硬仓库根与适配模板入口的 Artifact Contracts 规则。
  - 触发：用户指出仅有核心 `07-artifact-contracts.md` 不够，`AGENTS.md` / `CLAUDE.md` 等入口也应直接约束智能体自动产物行为。
  - 验证：检查仓库根 `AGENTS.md` / `CLAUDE.md`、Codex / Claude 适配模板和本机全局入口均包含 Artifact Contracts 段，明确审计写 `docs/audit/`、实现/修复回写 `state/LOG.md` 与 `state/PROGRESS.md`、文档变更更新索引。

- `change` 新增工作流产物契约，要求审计、验收、实现、修复、验证和文档同步留下可发现文件产物。
  - 触发：用户指出当前工作流不会像 J-SOP 样板项目一样自动审计、自动产出报告和同步日志/索引。
  - 验证：新增 `framework/core/07-artifact-contracts.md`，更新核心入口、适配模板、`project-workflow`、`project-inception-docs` 和启动模板；用临时项目烟测确认初始化会生成 `docs/audit/INDEX.md` 与 `docs/audit/TEMPLATE-GLOBAL-AUDIT.md`。

## 2026-06-26

- `change` 清理项目定制 skill，并把能力库同步为开源通用口径：409 技能、18 大类、项目定制 0。
  - 触发：用户确认本仓库要做成通用开源仓库，而不是携带个人/项目定制 skill。
  - 验证：同步 manifest、README、路由表、分级脚本、开源治理文件与四态系统，并执行一致性/敏感信息扫描。

- `change` 补齐 README 对新项目地基门禁的说明，并增强启动模板 README 的地基状态表。
  - 触发：检查发现根 README 尚未同步 Git 初始化、忽略文件、Agent 入口和首次提交规则。
  - 验证：检查 README 关键词覆盖、skill 校验、diff check 与 Git 提交闸门。

- `change` 强化项目启动地基门禁，要求新项目先补 Git、忽略文件、agent 入口、四态系统、文档索引和验证入口。
  - 触发：用户要求每个项目初始时，如果没有 Git 等基础设施就先初始化，把项目地基打好。
  - 验证：运行 skill frontmatter 校验、模板路径/关键词检查、diff 检查与 Git 提交闸门。

- `change` 按用户授权从 `Coff0xc/coffee-skill` 原位更新 18 个 Coff0xc 技能，并保存 LICENSE/NOTICE/manifest 来源记录。
  - 触发：用户希望把授权的 Coffee skill 纳入本地能力库。
  - 验证：检查 18 个目录文件数、frontmatter 名称归一化、skill quick_validate、来源记录位置和 Git diff。

- `change` 从真实项目文档集抽取标准启动文档包，并沉淀为 `project-inception-docs` 的 reference 与模板资产。
  - 触发：需要把真实项目中验证过的多文档结构转成可复用模板，支持新项目从想法自动生成文档包。
  - 验证：运行 skill frontmatter 校验、模板路径枚举、链接与占位检查。

- `change` 扩展 `project-inception-docs` 为项目启动文档包技能，并同步当时的能力库索引。
  - 触发：需要在项目起步时从想法自动生成 README、PRD、页面/信息架构、技术架构、数据模型、API、AI/Prompt 工作流、路线图、测试验收、部署运维、安全合规、迁移清单与四态系统。
  - 验证：运行 skill frontmatter 校验、一致性搜索、diff 检查与 manifest 计数检查。
