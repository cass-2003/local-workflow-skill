# 路由矩阵：意图 → 执行能力

把模糊请求稳定映射到正确的工作流路线和能力库技能，不只靠关键词硬猜。

> **消歧（重要）**：下表的路由名（`implement / fix / audit / review / status / sprint / sync-docs / evolution`）是**流程动作**，不是技能名。路由先定动作，执行阶段再按问题域选择具体领域技能（见下方二级路由）。旧的同名命令封装技能属于 runtime/project 绑定项，不进入本通用库。

## 主路由（按意图）

| 用户意图 | 常见表达 | 主路由 | 常见次路由 |
|---|---|---|---|
| status | 状态、进度、现在到哪了、当前情况 | `status` | 读四态系统 |
| audit | 审计、差距分析、基线检查、验收预检 | `audit` | `review` |
| autonomous progress | 继续推进项目、自己往下做、按计划开发、自动审计修复、推进到可用版本 | `autonomous-loop` | `planning` / `implement` / `audit` / `fix` |
| planning | 项目规划、路线图、下一步该做什么、先分析进度 | `planning` | `audit` / `status` |
| implement | 实现、开发、做功能、新增能力 | `implement` | `validation` |
| fix | 修复、repair、close findings、批量修 bug | `fix` | `review` |
| review | review、检查 diff、找风险、代码评审 | `review` | `validation` |
| docs sync | 更新文档、同步计划、归档、补记录 | `sync-docs` | `status` / `audit` |
| git delivery | commit、push、branch、PR、merge | git flow | `validation` / `sync-docs` |
| evolution | 优化流程、路径、编排规则 | `evolution` | `sync-docs` |

## 二级路由：执行能力 → 能力库（`skills/`）

`implement` / `fix` 真正动手时，按问题域委托到能力库对应领域大类。能力库为**双层结构** `skills/<领域大类>/<来源>/<skill>/`（来源 = ours｜codex｜community｜cskills，去重优先级 ours>codex>community>cskills），共 **565 个技能 / 58 大类**：

| 问题域 | 领域大类 | 数量 | 代表技能 |
|---|---|---|---|
| 通用工程模式 | `engineering-core/` | 26 | api-versioning、rate-limiting、idempotency、system-design、domains |
| 编程语言 | `programming-languages/` | 21 | python-dev、go-dev、rust-dev、java-jvm-development |
| 后端与 API | `backend-api/` | 29 | auth-access-control、api-error-observability、database-transaction-consistency、supabase-postgres-best-practices、fastapi-dev、nestjs-dev、graphql-dev |
| 前端与 UI | `frontend-ui/` | 30 | design-system-implementation、frontend-performance、frontend-state-data-flow、nextjs-dev、vue-dev、figma-*、accessibility |
| 移动与跨端 | `mobile-crossplatform/` | 37 | mobile-app-architecture、mini-program-architecture、wechat-miniprogram-engineering、Taro/uniapp、Expo 系列、Flutter、React Native、各小程序 |
| 数据与分析 | `data-analysis/` | 9 | airtable-overview、airtable-filters、data-engineering、sql-optimization、spreadsheet-analysis |
| 云与基础设施 | `cloud-infra/` | 37 | Render 系列、docker-k8s、terraform、sre-practices、各 deploy |
| AI 与自动化 | `ai-automation/` | 18 | llm-guardrails、rag-engineering、prompt-engineering、playwright |
| 业务运营 | `business-operations/` | 6 | capacity-planner、process-mapper、knowledge-ops、vendor-management |
| 商业策略 | `commercial-strategy/` | 7 | pricing-strategist、deal-desk、rfp-responder、commercial-forecaster |
| 财务与指标 | `finance/` | 2 | financial-analyst、saas-metrics-coach |
| 产品管理 | `product-management/` | 8 | product-discovery、product-analytics、experiment-designer、code-to-prd |
| 项目管理 | `project-management/` | 4 | meeting-analyzer、scrum-master、senior-pm、team-communications |
| 研究运营 | `research-ops/` | 3 | market-research、product-research、clinical-research |
| 营销增长与内容 | `seo/`、`content-strategy/`、`copywriting-editing/`、`paid-acquisition/`、`email-marketing/`、`social-media/` 等 | 39 | seo-audit、content-strategy、copywriting、paid-ads、campaign-analytics |
| 合规与质量体系 | `ai-governance-compliance/`、`privacy-compliance/`、`security-compliance/`、`medical-regulatory/`、`quality-management/` 等 | 12 | ai-act-readiness、gdpr-audit-prep、soc2-audit-prep、qms-audit-expert |
| 研究、学习与知识 | `grant-funding/`、`patent-intelligence/`、`literature-review/`、`entity-research/`、`learning-design/` | 6 | grants、patent、litreview、dossier、syllabus |
| 个人生产力与交接 | `personal-productivity/`、`email-productivity/`、`handoff-knowledge/` | 5 | capture、reflect、inbox-triage、handoff |
| 经营、销售与组织管理 | `customer-success/`、`revenue-operations/`、`sales-enablement/`、`executive-strategy/`、`change-org-management/` | 12 | customer-success-manager、revenue-operations、sales-engineer、strategic-alignment |
| 发布与格式化输出 | `markdown-publishing/`、`launch-management/`、`app-store-growth/`、`video-webinar-marketing/` | 9 | md-document、md-slides、launch-strategy、app-store-optimization |
| 逆向工程 | `reverse-engineering/` | 63 | binrev、asmrev、javarev、fwrev、malrev（cskills 全家桶） |
| 安全工程 | `security-engineering/` | 85 | full-pentest、ad-pentest、forensics、threat-hunting |
| 支付与电商 | `payments-commerce/` | 12 | stripe、paypal、alipay-pay、wechat-pay、wallet-* |
| 地图与位置 | `maps-location/` | 11 | amap-gaode、google-maps-platform、mapbox-maplibre |
| 硬件与系统 | `hardware-systems/` | 8 | embedded-firmware、fpga-asic-hdl、*-driver-development |
| 质量与交付 | `quality-delivery/` | 24 | testing、code-audit、git-workflow、tools(verify-*) |
| 内容创作与文档 | `content-authoring/` | 14 | doc-office、pdf、presentation-authoring、notion-* |
| 研究与知识 | `research-knowledge/` | 10 | research、academic-writing、search-engine、web-fetch |
| 产品与增长 | `product-growth/` | 8 | product-manager、ai-content-marketing、social-media-ops |
| 工作流与编排 | `workflow-orchestration/` | 15 | project-workflow、project-inception-docs、orchestration(多 agent)、skill-router |

> 能力库随筛选会变化，权威以 `skills/` 实际目录与 `skills/README.md` 索引为准；合并对照表见 `skills/_merge-manifest.csv`。新增大类时回这里补一行。

**大类内如何选具体技能**：上表只定到"大类"。进了大类后（如 `programming-languages/` 21 个），用各技能 `SKILL.md` 的 `description`（frontmatter）做终选——挑触发语义最贴合当前任务的那个。两条捷径：
- **trivial 改动**（如加一个小函数、改一行）可**不委托**，直接内联完成（呼应 `01-workflow.md` 的轻量任务裁剪）。
- 大类内多个近义技能都像候选时，优先 `ours` > `codex` > `community` > `cskills`（与去重优先级一致），或并列时取 `description` 命中更精确者。

## 消歧规则

- "检查最近改动有没有问题"通常是 `review`，不是 `audit`。
- "关闭审计缺口"通常是 `fix`，不是 `audit`。
- "按需求做功能"通常是 `implement`，不是 `review`。
- "继续推进项目"通常先走 `autonomous-loop`；如果没有路线图，先进入 `planning`，再选择第一轮可验证工作包。
- "先分析接下来该做什么"通常是 `planning`，不是直接 `implement`。
- "更新计划或记录"通常是 `sync-docs`，不是 `status`。
- "为什么这套流程开始混乱"通常先走 `evolution`，而不是直接编码。

## 范围覆盖

范围可以覆盖关键词判断：

- 仓库级基线比对 → `audit`
- 单个 diff 检查 → `review`
- 只看状态不改内容 → `status`
- 持续推进多个工作包 → `autonomous-loop`
- 项目启动或方向不清 → `planning`
- 代码 + 文档 + 验证一起做 → `implement` 或 `fix`
- 只做交付打包 → git flow

## 路由输出模板

```md
## Routing Decision

- User intent:
- Primary route:
- Secondary route:
- Skill library target:   <能力库类别 / 具体技能 / none>
- Scope:
- Domain escalation:
- Fallback used:
- Notes:
```
