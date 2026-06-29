# 领域与技能中文对照 · Domain & Skill Glossary

这份文件用于快速理解 `skills/<domain>/<source>/<skill>/` 里的英文领域名和 skill slug。完整机器索引仍以 [`README.md`](README.md) 和 [`_merge-manifest.csv`](_merge-manifest.csv) 为准；本文件是给人看的中文对照表。

## 统计口径

- 覆盖：566 个 winner skills / 58 个领域大类。
- 来源：`codex` 271 · `community` 252 · `ours` 43。
- 分级：半通用 83 · 通用 483。
- 中文名是面向检索和结构审阅的参考译名；具体触发条件、边界和执行方式以每个 `SKILL.md` 为准。

## 来源层

| 来源 | 中文含义 | 说明 |
|---|---|---|
| `ours` | 本仓沉淀 | 本仓库原创或长期维护的通用工作流与技能。 |
| `codex` | Codex/本机整理层 | Codex、Claude Code、官方插件和本机技能整理后的来源层。 |
| `community` | 第三方授权导入 | 许可清晰的第三方授权技能，含开源和已获授权来源。 |

## 领域对照

| 英文目录 | 中文名 | 数量 | 来源构成 | 一句话说明 |
|---|---|---:|---|---|
| `security-engineering` | 安全工程 | 85 | codex:83, community:2 | Web/API/云/容器/移动/IoT/区块链安全、红队、SOC、威胁建模和检测响应。 |
| `reverse-engineering` | 逆向工程 | 63 | codex:6, community:57 | 二进制、移动、固件、协议、恶意样本、内核和漏洞逆向。 |
| `cloud-infra` | 云与基础设施 | 37 | codex:31, community:6 | Docker、Kubernetes、部署平台、SRE、监控、灾备和成本治理。 |
| `mobile-crossplatform` | 移动与跨端 | 37 | codex:18, community:11, ours:8 | iOS、Android、Flutter、React Native、Expo、uniapp、Taro 和小程序工程。 |
| `frontend-ui` | 前端与 UI | 30 | codex:22, community:4, ours:4 | UI 设计、前端实现、设计系统、Figma、可访问性、性能和状态数据流。 |
| `backend-api` | 后端与 API | 29 | codex:19, community:4, ours:6 | API 设计、后端框架、认证授权、实时通信、后台任务与 SDK。 |
| `engineering-core` | 通用工程模式 | 26 | codex:6, community:1, ours:19 | 缓存、幂等、分页、限流、配置、错误处理、日志、迁移等通用工程模式。 |
| `quality-delivery` | 质量与交付 | 24 | codex:19, community:5 | 测试、QA、CI、代码审计、迁移、重构、CLI 和 Git 交付。 |
| `programming-languages` | 编程语言 | 21 | codex:12, community:9 | Python、JS/TS、Go、Rust、Java、C/C++、.NET、PHP、Ruby 等语言工程。 |
| `ai-automation` | AI 与自动化 | 18 | codex:11, community:6, ours:1 | Agent、RAG、Prompt、MLOps、自动化浏览器、语音与评估能力。 |
| `workflow-orchestration` | 工作流与编排 | 16 | codex:12, ours:4 | 项目工作流、项目启动文档、多 agent 编排、规格执行和 skill 创建。 |
| `content-authoring` | 内容创作与文档 | 14 | codex:12, community:2 | Office、PDF、Notion、技术写作、研究文档和演示产物。 |
| `payments-commerce` | 支付与电商 | 12 | codex:1, community:11 | Stripe、PayPal、微信支付、支付宝、钱包、Apple Pay 和 Google Pay。 |
| `maps-location` | 地图与位置 | 11 | community:11 | 高德、百度、腾讯、Google Maps、Mapbox、GIS 和路线规划。 |
| `research-knowledge` | 研究与知识 | 10 | codex:6, community:4 | 科研写作、搜索、Context7、法律顾问、Web fetch 和知识研究。 |
| `data-analysis` | 数据与分析 | 9 | codex:7, community:1, ours:1 | 数据工程、数据库、SQL、可视化、表格和 schema 校验。 |
| `hardware-systems` | 硬件与系统 | 8 | codex:3, community:5 | STM32、嵌入式、FPGA、驱动、UEFI 和固件。 |
| `product-growth` | 产品与增长 | 8 | codex:3, community:5 | 产品经理、产品营销、Sentry、Linear、推广写作和社媒运营。 |
| `product-management` | 产品管理 | 8 | community:8 | 产品发现、PRD、路线图、竞品拆解、实验设计和产品分析。 |
| `commercial-strategy` | 商业策略 | 7 | community:7 | 定价、渠道、合作伙伴、商业政策、RFP 和 deal desk。 |
| `business-operations` | 业务运营 | 6 | community:6 | 流程、采购、供应商、知识运营、容量规划和内部沟通。 |
| `conversion-optimization` | 转化率优化 | 6 | community:6 | 表单、注册、落地页、弹窗、付费墙和 onboarding 转化优化。 |
| `change-org-management` | 组织变革管理 | 4 | community:4 | 组织变革、文化、Chief of Staff、组织健康诊断。 |
| `executive-strategy` | 高层战略 | 4 | community:4 | 董事会材料、决策记录、情景推演和战略对齐。 |
| `markdown-publishing` | Markdown 发布 | 4 | community:4 | Markdown 文档、评审、幻灯片和设计系统文档。 |
| `project-management` | 项目管理 | 4 | community:4 | 会议分析、Scrum、团队沟通和项目管理。 |
| `seo` | SEO | 4 | community:4 | SEO、Schema、站点结构和程序化 SEO。 |
| `social-media` | 社交媒体 | 4 | community:4 | 社媒内容、社媒分析、账号增长和运营。 |
| `brand-strategy` | 品牌策略 | 3 | community:3 | 品牌指南、竞品替代定位和营销心理。 |
| `content-strategy` | 内容策略 | 3 | community:3 | 内容策略、内容生产和创作者工作流。 |
| `copywriting-editing` | 文案与编辑 | 3 | community:3 | 文案、编辑、改写、人味化和表达质量。 |
| `growth-experiments` | 增长实验 | 3 | community:3 | A/B 测试、免费工具增长和推荐计划。 |
| `medical-regulatory` | 医疗监管 | 3 | community:3 | FDA、ISO13485、MDR 等医疗监管准备。 |
| `paid-acquisition` | 付费获客 | 3 | community:3 | 广告创意、付费获客和投放策略。 |
| `quality-management` | 质量管理 | 3 | community:3 | QMS、CAPA、质量文档和质量审计。 |
| `research-ops` | 研究运营 | 3 | community:3 | 临床研究、市场研究和产品研究。 |
| `video-webinar-marketing` | 视频与 Webinar 营销 | 3 | community:3 | 视频内容、YouTube 和 Webinar 营销。 |
| `ai-governance-compliance` | AI 治理合规 | 2 | community:2 | AI 法规准备、AI 管理体系与审计。 |
| `email-marketing` | 邮件营销 | 2 | community:2 | 冷邮件和邮件序列。 |
| `email-productivity` | 邮件生产力 | 2 | community:2 | 收件箱设置、邮件分拣和个人邮件工作流。 |
| `entity-research` | 实体研究 | 2 | community:2 | 实体档案、动态追踪和研究简报。 |
| `finance` | 财务与指标 | 2 | community:2 | 财务分析和 SaaS 指标。 |
| `marketing-analytics` | 营销分析 | 2 | community:2 | 营销埋点、活动分析和归因。 |
| `personal-productivity` | 个人生产力 | 2 | community:2 | 个人捕捉、反思和轻量生产力流程。 |
| `sales-enablement` | 销售赋能 | 2 | community:2 | 销售工程、合同、提案和售前材料。 |
| `security-compliance` | 安全合规 | 2 | community:2 | SOC2、ISO27001 等安全合规准备。 |
| `answer-engine-optimization` | 答案引擎优化 | 1 | community:1 | 面向 AI 搜索 / 答案引擎的内容结构优化。 |
| `app-store-growth` | 应用商店增长 | 1 | community:1 | App Store / 应用市场上架、素材和转化优化。 |
| `compliance-programs` | 合规项目 | 1 | community:1 | 通用合规项目准备与成熟度检查。 |
| `customer-success` | 客户成功 | 1 | community:1 | 客户成功管理与客户健康维护。 |
| `grant-funding` | 基金与资助 | 1 | community:1 | 基金、资助和申请材料。 |
| `handoff-knowledge` | 交接与知识传递 | 1 | community:1 | 交接材料和知识转移。 |
| `launch-management` | 发布管理 | 1 | community:1 | 产品发布计划和 go-to-market 节奏。 |
| `learning-design` | 学习设计 | 1 | community:1 | 课程大纲、学习路径和教学设计。 |
| `literature-review` | 文献综述 | 1 | community:1 | 文献综述与研究整理。 |
| `patent-intelligence` | 专利情报 | 1 | community:1 | 专利检索、专利情报和技术布局分析。 |
| `privacy-compliance` | 隐私合规 | 1 | community:1 | GDPR、隐私审计和隐私合规准备。 |
| `revenue-operations` | 收入运营 | 1 | community:1 | 收入运营和管道管理。 |

## 全量 skill 对照

> 表格按领域分组；`中文参考名` 用来帮助人工查找，不替代 skill 的 `description`。

### `ai-automation` — AI 与自动化（18）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `ai-agent-dev` | AI Agent 开发 | `codex` | 通用 |
| `ai-agent-rag` | AI Agent RAG | `codex` | 通用 |
| `ai-orchestrator` | AI 编排器 | `codex` | 通用 |
| `mlops` | MLOps | `codex` | 通用 |
| `playwright` | Playwright 自动化 | `codex` | 通用 |
| `playwright-e2e` | Playwright 端到端测试 | `codex` | 通用 |
| `playwright-interactive` | Playwright 交互式调试 | `codex` | 通用 |
| `prompt-engineering` | 提示词工程 | `codex` | 通用 |
| `rag-engineering` | RAG 工程 | `codex` | 通用 |
| `speech` | 语音处理 | `codex` | 通用 |
| `transcribe` | 语音转写 | `codex` | 通用 |
| `agent-briefing` | Agent 简报 | `community` | 通用 |
| `ai-engineering` | AI 工程 | `community` | 通用 |
| `ai-image-prompt` | AI 图像提示词 | `community` | 通用 |
| `autojs-automation` | AutoJS 自动化 | `community` | 通用 |
| `llm-eval` | LLM 评估 | `community` | 通用 |
| `mcp-tool-use` | MCP 工具使用 | `community` | 通用 |
| `llm-guardrails` | LLM 防护栏 | `ours` | 通用 |

### `ai-governance-compliance` — AI 治理合规（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `ai-act-readiness` | AI Act 准备 | `community` | 通用 |
| `aims-audit` | AI 管理体系审计 | `community` | 通用 |

### `answer-engine-optimization` — 答案引擎优化（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `aeo` | 答案引擎优化 | `community` | 通用 |

### `app-store-growth` — 应用商店增长（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `app-store-optimization` | 应用商店优化 | `community` | 通用 |

### `backend-api` — 后端与 API（29）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `api-data-platform` | API 数据平台 | `codex` | 通用 |
| `api-design` | API 设计 | `codex` | 通用 |
| `api-design-2` | API 设计（二） | `codex` | 通用 |
| `api-discovery` | API 发现 | `codex` | 通用 |
| `aspnet-core` | ASP.NET Core | `codex` | 半通用 |
| `backend-engineering` | 后端工程 | `codex` | 通用 |
| `cms-headless` | Headless CMS | `codex` | 通用 |
| `django-dev` | Django 开发 | `codex` | 通用 |
| `event-driven` | 事件驱动架构 | `codex` | 通用 |
| `fastapi-dev` | FastAPI 开发 | `codex` | 通用 |
| `graphql-dev` | GraphQL 开发 | `codex` | 通用 |
| `laravel-dev` | Laravel 开发 | `codex` | 通用 |
| `microservices` | 微服务 | `codex` | 通用 |
| `nestjs-dev` | NestJS 开发 | `codex` | 通用 |
| `rails-dev` | Rails 开发 | `codex` | 通用 |
| `realtime-communication` | 实时通信 | `codex` | 通用 |
| `service-mesh` | 服务网格 | `codex` | 通用 |
| `spring-boot-dev` | Spring Boot 开发 | `codex` | 通用 |
| `supabase-postgres-best-practices` | Supabase/Postgres 最佳实践 | `codex` | 半通用 |
| `api-engineering` | API 工程 | `community` | 通用 |
| `backend-engineering` | 后端工程 | `community` | 通用 |
| `graphql-grpc-events` | GraphQL/gRPC/事件 | `community` | 通用 |
| `sdk-integration` | SDK 集成 | `community` | 通用 |
| `api-error-observability` | API 错误与可观测性 | `ours` | 通用 |
| `auth-access-control` | 认证与访问控制 | `ours` | 通用 |
| `background-jobs` | 后台任务 | `ours` | 通用 |
| `database-transaction-consistency` | 数据库事务一致性 | `ours` | 通用 |
| `dockerfile-best` | Dockerfile 最佳实践 | `ours` | 通用 |
| `websocket-impl` | WebSocket 实现 | `ours` | 通用 |

### `brand-strategy` — 品牌策略（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `brand-guidelines` | 品牌指南 | `community` | 通用 |
| `competitor-alternatives` | 竞品替代定位 | `community` | 通用 |
| `marketing-psychology` | 营销心理学 | `community` | 通用 |

### `business-operations` — 业务运营（6）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `capacity-planner` | 容量规划 | `community` | 通用 |
| `internal-comms` | 内部沟通 | `community` | 通用 |
| `knowledge-ops` | 知识运营 | `community` | 通用 |
| `process-mapper` | 流程梳理 | `community` | 通用 |
| `procurement-optimizer` | 采购优化 | `community` | 通用 |
| `vendor-management` | 供应商管理 | `community` | 通用 |

### `change-org-management` — 组织变革管理（4）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `change-management` | 变革管理 | `community` | 通用 |
| `chief-of-staff` | 幕僚长 / Chief of Staff | `community` | 通用 |
| `culture-architect` | 组织文化设计 | `community` | 通用 |
| `org-health-diagnostic` | 组织健康诊断 | `community` | 通用 |

### `cloud-infra` — 云与基础设施（37）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `chaos-engineering` | 混沌工程 | `codex` | 通用 |
| `cloudflare-deploy` | Cloudflare 部署 | `codex` | 半通用 |
| `disaster-recovery` | 灾难恢复 | `codex` | 通用 |
| `docker-k8s` | Docker/Kubernetes | `codex` | 通用 |
| `edge-computing` | 边缘计算 | `codex` | 通用 |
| `finops` | FinOps 云成本治理 | `codex` | 通用 |
| `monitoring-observability` | 监控与可观测性 | `codex` | 通用 |
| `netlify-deploy` | Netlify 部署 | `codex` | 半通用 |
| `render-background-workers` | Render background workers | `codex` | 半通用 |
| `render-blueprints` | Render blueprints | `codex` | 半通用 |
| `render-cli` | Render cli | `codex` | 半通用 |
| `render-cron-jobs` | Render cron jobs | `codex` | 半通用 |
| `render-debug` | Render debug | `codex` | 半通用 |
| `render-deploy` | Render deploy | `codex` | 半通用 |
| `render-disks` | Render disks | `codex` | 半通用 |
| `render-docker` | Render docker | `codex` | 半通用 |
| `render-domains` | Render domains | `codex` | 半通用 |
| `render-env-vars` | Render env vars | `codex` | 半通用 |
| `render-keyvalue` | Render keyvalue | `codex` | 半通用 |
| `render-mcp` | Render mcp | `codex` | 半通用 |
| `render-migrate-from-heroku` | Render migrate from heroku | `codex` | 半通用 |
| `render-monitor` | Render monitor | `codex` | 半通用 |
| `render-networking` | Render networking | `codex` | 半通用 |
| `render-postgres` | Render postgres | `codex` | 半通用 |
| `render-private-services` | Render private services | `codex` | 半通用 |
| `render-scaling` | Render scaling | `codex` | 半通用 |
| `render-static-sites` | Render static sites | `codex` | 半通用 |
| `render-web-services` | Render web services | `codex` | 半通用 |
| `render-workflows` | Render workflows | `codex` | 半通用 |
| `sre-practices` | SRE 实践 | `codex` | 通用 |
| `vercel-deploy` | Vercel 部署 | `codex` | 半通用 |
| `cloud-native` | 云原生 | `community` | 通用 |
| `k8sops` | Kubernetes 运维 | `community` | 通用 |
| `platform-engineering` | 平台工程 | `community` | 通用 |
| `release-engineering` | 发布工程 | `community` | 通用 |
| `terraform` | Terraform | `community` | 通用 |
| `terraform-iac` | Terraform IaC | `community` | 通用 |

### `commercial-strategy` — 商业策略（7）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `channel-economics` | 渠道经济模型 | `community` | 通用 |
| `commercial-forecaster` | 商业预测 | `community` | 通用 |
| `commercial-policy` | 商业政策 | `community` | 通用 |
| `deal-desk` | Deal Desk | `community` | 通用 |
| `partnerships-architect` | 合作伙伴架构 | `community` | 通用 |
| `pricing-strategist` | 定价策略 | `community` | 通用 |
| `rfp-responder` | RFP 响应 | `community` | 通用 |

### `compliance-programs` — 合规项目（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `compliance-readiness` | 合规准备 | `community` | 通用 |

### `content-authoring` — 内容创作与文档（14）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `doc-office` | Office 文档 | `codex` | 通用 |
| `jupyter-notebook` | Jupyter Notebook | `codex` | 通用 |
| `notion-knowledge-capture` | Notion knowledge capture | `codex` | 半通用 |
| `notion-meeting-intelligence` | Notion meeting intelligence | `codex` | 半通用 |
| `notion-research-documentation` | Notion research documentation | `codex` | 半通用 |
| `notion-spec-to-implementation` | Notion spec to implementation | `codex` | 半通用 |
| `office-doc-tools` | Office 文档工具 | `codex` | 通用 |
| `pdf` | PDF | `codex` | 通用 |
| `quick-translate` | 快速翻译 | `codex` | 通用 |
| `research-drawio-diagram` | 研究 Draw.io 图表 | `codex` | 通用 |
| `research-paper-writing` | 研究论文写作 | `codex` | 通用 |
| `technical-writing` | 技术写作 | `codex` | 通用 |
| `document-authoring` | 文档创作 | `community` | 通用 |
| `presentation-authoring` | 演示文稿创作 | `community` | 通用 |

### `content-strategy` — 内容策略（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `content-creator` | 内容创作者 | `community` | 通用 |
| `content-production` | 内容生产 | `community` | 通用 |
| `content-strategy` | 内容策略 | `community` | 通用 |

### `conversion-optimization` — 转化率优化（6）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `form-cro` | 表单转化优化 | `community` | 通用 |
| `onboarding-cro` | Onboarding 转化优化 | `community` | 通用 |
| `page-cro` | 页面转化优化 | `community` | 通用 |
| `paywall-upgrade-cro` | 付费墙升级转化优化 | `community` | 通用 |
| `popup-cro` | 弹窗转化优化 | `community` | 通用 |
| `signup-flow-cro` | 注册流程转化优化 | `community` | 通用 |

### `copywriting-editing` — 文案与编辑（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `content-humanizer` | 内容人味化 | `community` | 通用 |
| `copy-editing` | 文案编辑 | `community` | 通用 |
| `copywriting` | 文案写作 | `community` | 通用 |

### `customer-success` — 客户成功（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `customer-success-manager` | 客户成功经理 | `community` | 通用 |

### `data-analysis` — 数据与分析（9）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `airtable-filters` | Airtable 过滤器 | `codex` | 半通用 |
| `airtable-overview` | Airtable 总览 | `codex` | 半通用 |
| `data-engineering` | 数据工程 | `codex` | 通用 |
| `data-visualization` | 数据可视化 | `codex` | 通用 |
| `database` | 数据库 | `codex` | 通用 |
| `db-design` | 数据库设计 | `codex` | 通用 |
| `sql-optimization` | SQL 优化 | `codex` | 通用 |
| `spreadsheet-analysis` | 电子表格分析 | `community` | 通用 |
| `validation-schema` | 校验 Schema | `ours` | 通用 |

### `email-marketing` — 邮件营销（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `cold-email` | 冷邮件 | `community` | 通用 |
| `email-sequence` | 邮件序列 | `community` | 通用 |

### `email-productivity` — 邮件生产力（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `inbox-setup` | 收件箱设置 | `community` | 通用 |
| `inbox-triage` | 收件箱分拣 | `community` | 通用 |

### `engineering-core` — 通用工程模式（26）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `domains` | 工程领域模式 | `codex` | 通用 |
| `perf-engineering` | 性能工程 | `codex` | 通用 |
| `shell-scripting` | Shell 脚本 | `codex` | 通用 |
| `shell-scripting-2` | Shell 脚本（二） | `codex` | 通用 |
| `software-engineering` | 软件工程 | `codex` | 通用 |
| `system-design` | 系统设计 | `codex` | 通用 |
| `ponytail` | Ponytail 工程技能 | `community` | 通用 |
| `api-versioning` | API 版本管理 | `ours` | 通用 |
| `concurrency-patterns` | 并发模式 | `ours` | 通用 |
| `datetime-timezones` | 日期时间与时区 | `ours` | 通用 |
| `dependency-injection` | 依赖注入 | `ours` | 通用 |
| `environment-config` | 环境配置 | `ours` | 通用 |
| `error-handling-patterns` | 错误处理模式 | `ours` | 通用 |
| `feature-flags` | Feature Flags | `ours` | 通用 |
| `graceful-shutdown` | 优雅停机 | `ours` | 通用 |
| `http-caching` | HTTP 缓存 | `ours` | 通用 |
| `idempotency-design` | 幂等设计 | `ours` | 通用 |
| `memory-leaks` | 内存泄漏 | `ours` | 通用 |
| `migration-zero-downtime` | 零停机迁移 | `ours` | 通用 |
| `monorepo` | Monorepo | `ours` | 通用 |
| `pagination` | 分页 | `ours` | 通用 |
| `rate-limiting-algorithms` | 限流算法 | `ours` | 通用 |
| `regex-patterns` | 正则表达式模式 | `ours` | 通用 |
| `string-encoding` | 字符串编码 | `ours` | 通用 |
| `structured-logging` | 结构化日志 | `ours` | 通用 |
| `typescript-advanced` | TypeScript 进阶 | `ours` | 通用 |

### `entity-research` — 实体研究（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `dossier` | 实体档案 | `community` | 通用 |
| `pulse` | 动态追踪 | `community` | 通用 |

### `executive-strategy` — 高层战略（4）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `board-deck-builder` | 董事会材料生成 | `community` | 通用 |
| `decision-logger` | 决策记录 | `community` | 通用 |
| `scenario-war-room` | 情景推演战情室 | `community` | 通用 |
| `strategic-alignment` | 战略对齐 | `community` | 通用 |

### `finance` — 财务与指标（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `financial-analyst` | 财务分析师 | `community` | 通用 |
| `saas-metrics-coach` | SaaS 指标教练 | `community` | 通用 |

### `frontend-ui` — 前端与 UI（30）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `UIdesign` | UI 设计 | `codex` | 通用 |
| `accessibility` | 可访问性 | `codex` | 通用 |
| `angular-dev` | Angular 开发 | `codex` | 通用 |
| `chatgpt-apps` | ChatGPT Apps | `codex` | 半通用 |
| `figma` | Figma | `codex` | 半通用 |
| `figma-code-connect-components` | Figma Code Connect 组件 | `codex` | 半通用 |
| `figma-create-design-system-rules` | Figma 创建设计系统规则 | `codex` | 半通用 |
| `figma-create-new-file` | Figma 创建新文件 | `codex` | 半通用 |
| `figma-generate-design` | Figma 生成设计 | `codex` | 半通用 |
| `figma-generate-library` | Figma 生成组件库 | `codex` | 半通用 |
| `figma-implement-design` | Figma 设计实现 | `codex` | 半通用 |
| `figma-use` | Figma 使用 | `codex` | 半通用 |
| `frontend-dev` | 前端开发 | `codex` | 通用 |
| `graphics-rendering` | 图形渲染 | `codex` | 通用 |
| `i18n-l10n` | 国际化与本地化 | `codex` | 通用 |
| `nextjs-dev` | Next.js 开发 | `codex` | 通用 |
| `screenshot` | 截图处理 | `codex` | 通用 |
| `svelte-dev` | Svelte 开发 | `codex` | 通用 |
| `ui-design` | UI 设计 | `codex` | 通用 |
| `ui-doc-output` | UI 文档输出 | `codex` | 通用 |
| `vue-dev` | Vue 开发 | `codex` | 通用 |
| `winui-app` | WinUI 应用 | `codex` | 半通用 |
| `nextdev` | Next.js 开发 | `community` | 通用 |
| `react-development` | React 开发 | `community` | 通用 |
| `screenshot-to-ui` | 截图转 UI | `community` | 通用 |
| `ui-design` | UI 设计 | `community` | 通用 |
| `css-modern-2025` | 现代 CSS 2025 | `ours` | 通用 |
| `design-system-implementation` | 设计系统落地 | `ours` | 通用 |
| `frontend-performance` | 前端性能 | `ours` | 通用 |
| `frontend-state-data-flow` | 前端状态与数据流 | `ours` | 通用 |

### `grant-funding` — 基金与资助（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `grants` | 资助申请 | `community` | 通用 |

### `growth-experiments` — 增长实验（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `ab-test-setup` | A/B 测试设置 | `community` | 通用 |
| `free-tool-strategy` | 免费工具增长策略 | `community` | 通用 |
| `referral-program` | 推荐计划 | `community` | 通用 |

### `handoff-knowledge` — 交接与知识传递（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `handoff` | 交接 | `community` | 通用 |

### `hardware-systems` — 硬件与系统（8）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `STM32外设驱动开发` | STM32 外设驱动开发 | `codex` | 通用 |
| `STM32嵌入式核心开发` | STM32 嵌入式核心开发 | `codex` | 通用 |
| `STM32进阶开发` | STM32 进阶开发 | `codex` | 通用 |
| `embedded-firmware` | 嵌入式固件 | `community` | 通用 |
| `fpga-asic-hdl` | FPGA/ASIC/HDL | `community` | 通用 |
| `linux-driver-development` | Linux 驱动开发 | `community` | 通用 |
| `uefi-development` | UEFI 开发 | `community` | 通用 |
| `windows-driver-development` | Windows 驱动开发 | `community` | 通用 |

### `launch-management` — 发布管理（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `launch-strategy` | 发布策略 | `community` | 通用 |

### `learning-design` — 学习设计（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `syllabus` | 课程大纲 | `community` | 通用 |

### `literature-review` — 文献综述（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `litreview` | 文献综述 | `community` | 通用 |

### `maps-location` — 地图与位置（11）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `amap-gaode` | 高德地图 | `community` | 半通用 |
| `baidu-map` | 百度地图 | `community` | 半通用 |
| `esri-arcgis` | Esri ArcGIS | `community` | 半通用 |
| `google-maps-platform` | Google Maps Platform | `community` | 半通用 |
| `huawei-map-kit` | 华为 Map Kit | `community` | 半通用 |
| `leaflet-openlayers` | Leaflet/OpenLayers | `community` | 半通用 |
| `map-gis-core` | 地图/GIS 核心 | `community` | 半通用 |
| `mapbox-maplibre` | Mapbox/MapLibre | `community` | 半通用 |
| `openstreetmap-routing` | OpenStreetMap 路线规划 | `community` | 半通用 |
| `tencent-map` | 腾讯地图 | `community` | 半通用 |
| `tianditu-map` | 天地图 | `community` | 半通用 |

### `markdown-publishing` — Markdown 发布（4）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `design-system` | 设计系统 | `community` | 通用 |
| `md-document` | Markdown 文档 | `community` | 通用 |
| `md-review` | Markdown 评审 | `community` | 通用 |
| `md-slides` | Markdown 幻灯片 | `community` | 通用 |

### `marketing-analytics` — 营销分析（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `analytics-tracking` | 分析埋点 | `community` | 通用 |
| `campaign-analytics` | 活动分析 | `community` | 通用 |

### `medical-regulatory` — 医疗监管（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `fda-qsr-audit-prep` | FDA QSR 审计准备 | `community` | 通用 |
| `iso13485-audit-prep` | ISO13485 审计准备 | `community` | 通用 |
| `mdr-745-specialist` | MDR 745 专家 | `community` | 通用 |

### `mobile-crossplatform` — 移动与跨端（37）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `apple-development` | Apple 开发 | `codex` | 通用 |
| `building-native-ui` | 构建原生 UI | `codex` | 半通用 |
| `codex-expo-run-actions` | Codex Expo 运行操作 | `codex` | 半通用 |
| `expo-api-routes` | Expo API Routes | `codex` | 半通用 |
| `expo-cicd-workflows` | Expo CI/CD 工作流 | `codex` | 半通用 |
| `expo-deployment` | Expo 部署 | `codex` | 半通用 |
| `expo-dev-client` | Expo Dev Client | `codex` | 半通用 |
| `expo-module` | Expo Module | `codex` | 半通用 |
| `expo-tailwind-setup` | Expo Tailwind 设置 | `codex` | 半通用 |
| `flutter-dart-dev` | Flutter/Dart 开发 | `codex` | 通用 |
| `flutter-development` | Flutter 开发 | `codex` | 通用 |
| `kotlin-android-dev` | Kotlin Android 开发 | `codex` | 通用 |
| `native-data-fetching` | 原生数据获取 | `codex` | 半通用 |
| `react-native-dev` | React Native 开发 | `codex` | 通用 |
| `swift-ios-dev` | Swift iOS 开发 | `codex` | 通用 |
| `uniapp-dev` | uni-app 开发 | `codex` | 通用 |
| `upgrading-expo` | Expo 升级 | `codex` | 半通用 |
| `use-dom` | use-dom | `codex` | 半通用 |
| `alipay-miniprogram` | 支付宝小程序 | `community` | 半通用 |
| `android-development` | Android 开发 | `community` | 通用 |
| `apple-development` | Apple 开发 | `community` | 通用 |
| `douyin-miniprogram` | 抖音小程序 | `community` | 半通用 |
| `electron-development` | Electron 开发 | `community` | 通用 |
| `flutter-development` | Flutter 开发 | `community` | 通用 |
| `harmonyos-arkts` | HarmonyOS ArkTS | `community` | 半通用 |
| `harmonyos-arkui` | HarmonyOS ArkUI | `community` | 半通用 |
| `tauri-development` | Tauri 开发 | `community` | 通用 |
| `uniapp-development` | uni-app 开发 | `community` | 通用 |
| `wechat-miniprogram` | 微信小程序 | `community` | 半通用 |
| `mini-program-architecture` | 小程序架构 | `ours` | 通用 |
| `mini-program-login-payment` | 小程序登录支付 | `ours` | 通用 |
| `mobile-app-architecture` | 移动 App 架构 | `ours` | 通用 |
| `mobile-app-release-ops` | 移动 App 发布运营 | `ours` | 通用 |
| `mobile-offline-sync` | 移动端离线同步 | `ours` | 通用 |
| `mobile-push-notifications` | 移动端推送通知 | `ours` | 通用 |
| `taro-uniapp-crossplatform` | Taro/uni-app 跨端 | `ours` | 通用 |
| `wechat-miniprogram-engineering` | 微信小程序工程 | `ours` | 通用 |

### `paid-acquisition` — 付费获客（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `ad-creative` | 广告创意 | `community` | 通用 |
| `marketing-demand-acquisition` | 营销获客 | `community` | 通用 |
| `paid-ads` | 付费广告 | `community` | 通用 |

### `patent-intelligence` — 专利情报（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `patent` | 专利情报 | `community` | 通用 |

### `payments-commerce` — 支付与电商（12）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `payment-fintech` | 支付与金融科技 | `codex` | 半通用 |
| `adyen` | Adyen | `community` | 半通用 |
| `alipay-pay` | 支付宝支付 | `community` | 半通用 |
| `apple-pay` | Apple Pay | `community` | 半通用 |
| `checkout-com` | Checkout.com | `community` | 半通用 |
| `google-pay` | Google Pay | `community` | 半通用 |
| `paypal` | PayPal | `community` | 半通用 |
| `square` | Square | `community` | 半通用 |
| `stripe` | Stripe | `community` | 半通用 |
| `wallet-engineering` | 钱包工程 | `community` | 半通用 |
| `wallet-pass` | 钱包 Pass | `community` | 半通用 |
| `wechat-pay` | 微信支付 | `community` | 半通用 |

### `personal-productivity` — 个人生产力（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `capture` | 个人捕捉 | `community` | 通用 |
| `reflect` | 反思复盘 | `community` | 通用 |

### `privacy-compliance` — 隐私合规（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `gdpr-audit-prep` | GDPR 审计准备 | `community` | 通用 |

### `product-growth` — 产品与增长（8）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `linear` | Linear | `codex` | 半通用 |
| `product-manager` | 产品经理 | `codex` | 通用 |
| `sentry` | Sentry | `codex` | 半通用 |
| `ai-content-marketing` | AI 内容营销 | `community` | 通用 |
| `product-manager` | 产品经理 | `community` | 通用 |
| `product-marketing` | 产品营销 | `community` | 通用 |
| `project-promo-writer` | 项目推广文案 | `community` | 通用 |
| `social-media-ops` | 社媒运营 | `community` | 通用 |

### `product-management` — 产品管理（8）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `code-to-prd` | 代码转 PRD | `community` | 通用 |
| `competitive-teardown` | 竞品拆解 | `community` | 通用 |
| `experiment-designer` | 实验设计 | `community` | 通用 |
| `product-analytics` | 产品分析 | `community` | 通用 |
| `product-discovery` | 产品发现 | `community` | 通用 |
| `product-strategist` | 产品策略 | `community` | 通用 |
| `research-summarizer` | 研究总结 | `community` | 通用 |
| `roadmap-communicator` | 路线图沟通 | `community` | 通用 |

### `programming-languages` — 编程语言（21）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `c-cpp-dev` | C/C++ 开发 | `codex` | 通用 |
| `csharp-dotnet-dev` | C#/.NET 开发 | `codex` | 通用 |
| `go-dev` | Go 开发 | `codex` | 通用 |
| `go-dev-2` | Go 开发（二） | `codex` | 通用 |
| `java-dev` | Java 开发 | `codex` | 通用 |
| `js-ts-dev` | JavaScript/TypeScript 开发 | `codex` | 通用 |
| `js-ts-dev-2` | JavaScript/TypeScript 开发（二） | `codex` | 通用 |
| `php-dev` | PHP 开发 | `codex` | 通用 |
| `python-dev` | Python 开发 | `codex` | 通用 |
| `python-dev-2` | Python 开发（二） | `codex` | 通用 |
| `ruby-dev` | Ruby 开发 | `codex` | 通用 |
| `rust-dev` | Rust 开发 | `codex` | 通用 |
| `cpp-development` | C++ 开发 | `community` | 通用 |
| `dotnet-development` | .NET 开发 | `community` | 通用 |
| `elixir-erlang-development` | Elixir/Erlang 开发 | `community` | 通用 |
| `java-jvm-development` | Java/JVM 开发 | `community` | 通用 |
| `kotlin-development` | Kotlin 开发 | `community` | 通用 |
| `lua-openresty-development` | Lua/OpenResty 开发 | `community` | 通用 |
| `r-development` | R 开发 | `community` | 通用 |
| `scala-development` | Scala 开发 | `community` | 通用 |
| `typescript-development` | TypeScript 开发 | `community` | 通用 |

### `project-management` — 项目管理（4）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `meeting-analyzer` | 会议分析 | `community` | 通用 |
| `scrum-master` | Scrum Master | `community` | 通用 |
| `senior-pm` | 高级项目经理 | `community` | 通用 |
| `team-communications` | 团队沟通 | `community` | 通用 |

### `quality-delivery` — 质量与交付（24）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `cli-creator` | CLI 创建器 | `codex` | 通用 |
| `code-audit` | 代码审计 | `codex` | 通用 |
| `code-audit-2` | 代码审计（二） | `codex` | 通用 |
| `code-migration` | 代码迁移 | `codex` | 通用 |
| `code-simplifier` | 代码简化 | `codex` | 通用 |
| `commit` | 提交规范 | `codex` | 通用 |
| `devex-tooling` | 开发者体验工具 | `codex` | 通用 |
| `gh-address-comments` | GitHub 评论处理 | `codex` | 通用 |
| `gh-fix-ci` | GitHub CI 修复 | `codex` | 通用 |
| `git-workflow` | Git 工作流 | `codex` | 通用 |
| `git-workflow-2` | Git 工作流（二） | `codex` | 通用 |
| `low-code` | 低代码 | `codex` | 通用 |
| `performance-testing` | 性能测试 | `codex` | 通用 |
| `qa` | QA | `codex` | 通用 |
| `refactor` | 重构 | `codex` | 通用 |
| `test-engineering` | 测试工程 | `codex` | 通用 |
| `testing` | 测试 | `codex` | 通用 |
| `tools` | 工具集合 | `codex` | 通用 |
| `yeet` | 快速试验工具 | `codex` | 通用 |
| `browser-automation` | 浏览器自动化 | `community` | 通用 |
| `harmonyos-build-quality` | HarmonyOS 构建质量 | `community` | 通用 |
| `observability` | 可观测性 | `community` | 通用 |
| `perf-engineering` | 性能工程 | `community` | 通用 |
| `test-engineering` | 测试工程 | `community` | 通用 |

### `quality-management` — 质量管理（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `capa-officer` | CAPA 负责人 | `community` | 通用 |
| `qms-audit-expert` | QMS 审计专家 | `community` | 通用 |
| `quality-documentation-manager` | 质量文档经理 | `community` | 通用 |

### `research-knowledge` — 研究与知识（10）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `context7` | Context7 | `codex` | 通用 |
| `game-dev` | 游戏开发 | `codex` | 通用 |
| `research-scientific-research` | 科学研究 | `codex` | 通用 |
| `search-engine` | 搜索引擎 | `codex` | 通用 |
| `web-fetch` | 网页抓取 | `codex` | 通用 |
| `web3-dapp` | Web3 DApp | `codex` | 通用 |
| `academic-writing` | 学术写作 | `community` | 通用 |
| `legal-counsel` | 法律顾问 | `community` | 通用 |
| `project-learning` | 项目学习 | `community` | 通用 |
| `research` | 研究 | `community` | 通用 |

### `research-ops` — 研究运营（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `clinical-research` | 临床研究 | `community` | 通用 |
| `market-research` | 市场研究 | `community` | 通用 |
| `product-research` | 产品研究 | `community` | 通用 |

### `revenue-operations` — 收入运营（1）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `revenue-operations` | 收入运营 | `community` | 通用 |

### `reverse-engineering` — 逆向工程（63）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `android-reversing` | Android 逆向 | `codex` | 通用 |
| `binary-exploit` | 二进制漏洞利用 | `codex` | 通用 |
| `dotnet-reversing` | .NET 逆向 | `codex` | 通用 |
| `reverse-analysis` | 逆向分析 | `codex` | 通用 |
| `reverse-engineering` | 逆向工程 | `codex` | 通用 |
| `reverse-engineering-2` | 逆向工程（二） | `codex` | 通用 |
| `abirev` | ABI逆向 | `community` | 通用 |
| `asmrev` | 汇编逆向 | `community` | 通用 |
| `autorev` | 自动化逆向 | `community` | 通用 |
| `binrev` | 二进制逆向 | `community` | 通用 |
| `bootrev` | 启动链逆向 | `community` | 通用 |
| `carrev` | 车载安全逆向 | `community` | 通用 |
| `cloudrev` | 云客户端逆向 | `community` | 通用 |
| `containerrev` | 容器逆向 | `community` | 通用 |
| `contractrev` | 智能合约逆向 | `community` | 通用 |
| `crashrev` | 崩溃逆向 | `community` | 通用 |
| `cryptrev` | 密码学逆向 | `community` | 通用 |
| `debugrev` | 调试逆向 | `community` | 通用 |
| `diffrev` | 二进制 Diff逆向 | `community` | 通用 |
| `diskrev` | 磁盘/文件系统逆向 | `community` | 通用 |
| `docrev` | 文档格式逆向 | `community` | 通用 |
| `dotnetrev` | .NET逆向 | `community` | 通用 |
| `drmrev` | DRM逆向 | `community` | 通用 |
| `ebpfrev` | eBPF逆向 | `community` | 通用 |
| `edrrev` | EDR逆向 | `community` | 通用 |
| `fmtrev` | 文件格式逆向 | `community` | 通用 |
| `fuzzrev` | 模糊测试辅助逆向 | `community` | 通用 |
| `fwrev` | 固件逆向 | `community` | 通用 |
| `gamerev` | 游戏逆向 | `community` | 通用 |
| `gorev` | Go 二进制逆向 | `community` | 通用 |
| `hvrev` | Hypervisor逆向 | `community` | 通用 |
| `hwrev` | 硬件逆向 | `community` | 通用 |
| `icsrev` | 工控 ICS逆向 | `community` | 通用 |
| `iotrev` | IoT逆向 | `community` | 通用 |
| `irrev` | 事件响应逆向 | `community` | 通用 |
| `javarev` | Java逆向 | `community` | 通用 |
| `kernrev` | 内核逆向 | `community` | 通用 |
| `linuxrev` | Linux逆向 | `community` | 通用 |
| `macrev` | macOS逆向 | `community` | 通用 |
| `malrev` | 恶意样本逆向 | `community` | 通用 |
| `memrev` | 内存逆向 | `community` | 通用 |
| `mitirev` | MITRE 映射逆向 | `community` | 通用 |
| `mlrev` | 机器学习模型逆向 | `community` | 通用 |
| `mobile-reverse-engineering` | 移动逆向工程 | `community` | 通用 |
| `opsecrev` | OPSEC逆向 | `community` | 通用 |
| `packrev` | 壳/打包器逆向 | `community` | 通用 |
| `protrev` | 协议逆向 | `community` | 通用 |
| `rev-report` | 逆向报告 | `community` | 通用 |
| `revauto` | revauto | `community` | 通用 |
| `revlab` | revlab | `community` | 通用 |
| `rktrev` | Rootkit逆向 | `community` | 通用 |
| `rustrev` | Rust 二进制逆向 | `community` | 通用 |
| `scriptrev` | 脚本逆向 | `community` | 通用 |
| `sdkrev` | SDK逆向 | `community` | 通用 |
| `sigrev` | 签名/规则逆向 | `community` | 通用 |
| `supplyrev` | 供应链逆向 | `community` | 通用 |
| `swiftrev` | Swift逆向 | `community` | 通用 |
| `ttdrev` | 时间旅行调试逆向 | `community` | 通用 |
| `vmrev` | 虚拟机逆向 | `community` | 通用 |
| `vulnrev` | 漏洞逆向 | `community` | 通用 |
| `wasmrev` | WebAssembly逆向 | `community` | 通用 |
| `webrev` | Web 客户端逆向 | `community` | 通用 |
| `winrev` | Windows逆向 | `community` | 通用 |

### `sales-enablement` — 销售赋能（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `contract-and-proposal-writer` | 合同与提案写作 | `community` | 通用 |
| `sales-engineer` | 销售工程师 | `community` | 通用 |

### `security-compliance` — 安全合规（2）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `iso27001-audit-prep` | ISO27001 审计准备 | `community` | 通用 |
| `soc2-audit-prep` | SOC2 审计准备 | `community` | 通用 |

### `security-engineering` — 安全工程（85）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `ad-pentest` | Active Directory渗透测试 | `codex` | 通用 |
| `api-security-test` | API安全test | `codex` | 通用 |
| `authorized-assessment` | 授权评估 | `codex` | 通用 |
| `backdoor-detector` | 后门检测 | `codex` | 通用 |
| `binary-mobile-iot` | 二进制移动IoT | `codex` | 通用 |
| `blockchain-security` | 区块链安全 | `codex` | 通用 |
| `blockchain-security-2` | 区块链安全2 | `codex` | 通用 |
| `browser-security` | 浏览器安全 | `codex` | 通用 |
| `bug-bounty` | bug赏金 | `codex` | 通用 |
| `c2-framework` | c2框架 | `codex` | 通用 |
| `cdn-bypass` | CDN绕过 | `codex` | 通用 |
| `cloud-devsecops` | 云devsecops | `codex` | 通用 |
| `cloud-security` | 云安全 | `codex` | 通用 |
| `compliance-architecture` | compliance架构 | `codex` | 通用 |
| `compliance-audit` | compliance审计 | `codex` | 通用 |
| `container-security` | 容器安全 | `codex` | 通用 |
| `credential-access` | 凭据access | `codex` | 通用 |
| `crypto-security` | 密码学安全 | `codex` | 通用 |
| `ctf` | ctf | `codex` | 通用 |
| `data-exfiltration` | 数据外泄 | `codex` | 通用 |
| `data-security` | 数据安全 | `codex` | 通用 |
| `detection-engineering` | 检测工程 | `codex` | 通用 |
| `detection-response` | 检测响应 | `codex` | 通用 |
| `devsecops` | devsecops | `codex` | 通用 |
| `edr-endpoint` | edr终端 | `codex` | 通用 |
| `email-security` | 邮件安全 | `codex` | 通用 |
| `evasion-toolkit` | 规避toolkit | `codex` | 通用 |
| `fingerprint-engine` | 指纹引擎 | `codex` | 通用 |
| `forensics-analysis` | 取证分析 | `codex` | 通用 |
| `full-pentest` | 完整渗透测试 | `codex` | 通用 |
| `graphql-pentest` | GraphQL渗透测试 | `codex` | 通用 |
| `honeypot` | 蜜罐 | `codex` | 通用 |
| `iac-devops` | iac / devops | `codex` | 通用 |
| `ics-scada` | ics / scada | `codex` | 通用 |
| `identity-security` | 身份安全 | `codex` | 通用 |
| `identity-zero-trust` | 身份零信任 | `codex` | 通用 |
| `incident-response` | 事件响应 | `codex` | 通用 |
| `iot-security` | IoT安全 | `codex` | 通用 |
| `kernel-security` | 内核安全 | `codex` | 通用 |
| `lateral-movement` | 横向移动 | `codex` | 通用 |
| `linux-hardening` | linux加固 | `codex` | 通用 |
| `llm-red-teaming` | llm红队teaming | `codex` | 通用 |
| `malware-analysis` | 恶意软件分析 | `codex` | 通用 |
| `mobile-security` | 移动安全 | `codex` | 通用 |
| `mobile-security-2` | 移动安全2 | `codex` | 通用 |
| `network-monitoring` | 网络monitoring | `codex` | 通用 |
| `network-protocol` | 网络协议 | `codex` | 通用 |
| `network-protocol-security` | 网络协议安全 | `codex` | 通用 |
| `oauth-security` | OAuth安全 | `codex` | 通用 |
| `osint` | OSINT | `codex` | 通用 |
| `pentest-report` | 渗透测试report | `codex` | 通用 |
| `phishing-simulation` | 钓鱼simulation | `codex` | 通用 |
| `post-exploitation` | 后渗透 | `codex` | 通用 |
| `privacy-engineering` | 隐私工程 | `codex` | 通用 |
| `privilege-escalation` | 权限提升 | `codex` | 通用 |
| `proxy-pool-manager` | 代理池manager | `codex` | 通用 |
| `purple-deception` | 紫队deception | `codex` | 通用 |
| `purple-team` | 紫队团队 | `codex` | 通用 |
| `quantum-security` | 量子安全 | `codex` | 通用 |
| `recon-workflow` | 侦察workflow | `codex` | 通用 |
| `red-team-infra` | 红队团队infra | `codex` | 通用 |
| `red-team-poc` | 红队团队poc | `codex` | 通用 |
| `secrets-management` | 密钥管理 | `codex` | 通用 |
| `secure-code-appsec` | secure / code / appsec | `codex` | 通用 |
| `security-architecture` | 安全架构 | `codex` | 通用 |
| `security-best-practices` | 安全最佳实践 | `codex` | 通用 |
| `security-ownership-map` | 安全责任地图 | `codex` | 通用 |
| `security-threat-model` | 安全威胁模型 | `codex` | 通用 |
| `security-tool-dev` | 安全工具开发 | `codex` | 通用 |
| `serverless-security` | Serverless安全 | `codex` | 通用 |
| `soc-operations` | SOCoperations | `codex` | 通用 |
| `social-engineering` | 社会工程 | `codex` | 通用 |
| `spa-pentest` | SPA渗透测试 | `codex` | 通用 |
| `supply-chain-security` | 供应链chain安全 | `codex` | 通用 |
| `threat-hunting` | 威胁狩猎 | `codex` | 通用 |
| `threat-intelligence` | 威胁情报 | `codex` | 通用 |
| `vuln-research` | 漏洞研究 | `codex` | 通用 |
| `vulnerability-lifecycle` | 漏洞lifecycle | `codex` | 通用 |
| `vulnerability-management` | 漏洞管理 | `codex` | 通用 |
| `web-pentest` | Web渗透测试 | `codex` | 通用 |
| `windows-hardening` | Windows加固 | `codex` | 通用 |
| `wireless-security` | 无线安全 | `codex` | 通用 |
| `zero-trust` | 零信任 | `codex` | 通用 |
| `protocol-analysis` | 协议分析 | `community` | 通用 |
| `web-security` | Web安全 | `community` | 通用 |

### `seo` — SEO（4）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `programmatic-seo` | 程序化 SEO | `community` | 通用 |
| `schema-markup` | Schema 标记 | `community` | 通用 |
| `seo-audit` | SEO 审计 | `community` | 通用 |
| `site-architecture` | 站点架构 | `community` | 通用 |

### `social-media` — 社交媒体（4）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `social-content` | 社媒内容 | `community` | 通用 |
| `social-media-analyzer` | 社媒分析 | `community` | 通用 |
| `social-media-manager` | 社媒经理 | `community` | 通用 |
| `x-twitter-growth` | X/Twitter 增长 | `community` | 通用 |

### `video-webinar-marketing` — 视频与 Webinar 营销（3）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `video-content-strategist` | 视频内容策略 | `community` | 通用 |
| `webinar-marketing` | Webinar 营销 | `community` | 通用 |
| `youtube-full` | YouTube 全链路 | `community` | 通用 |

### `workflow-orchestration` — 工作流与编排（16）

| skill slug | 中文参考名 | 来源 | 分级 |
|---|---|---|---|
| `attack-chain-orchestrator` | 攻击链编排器 | `codex` | 通用 |
| `autoredteam-orchestrator` | 自动红队编排器 | `codex` | 通用 |
| `deep-thinking` | 深度思考 | `codex` | 通用 |
| `dev` | 开发工作流 | `codex` | 通用 |
| `mcp-builder` | MCP 构建器 | `codex` | 通用 |
| `memory` | 记忆系统 | `codex` | 通用 |
| `orchestration` | 编排 | `codex` | 通用 |
| `skill-creator` | 技能创建器 | `codex` | 通用 |
| `skill-router` | 技能路由器 | `codex` | 通用 |
| `spec` | 规格说明 | `codex` | 通用 |
| `spec-check` | 规格检查 | `codex` | 通用 |
| `spec-do` | 规格执行 | `codex` | 通用 |
| `goal-driven-project-loop` | 目标驱动项目推进循环 | `ours` | 通用 |
| `local-workflow` | 本地工作流 | `ours` | 通用 |
| `project-inception-docs` | 项目启动文档 | `ours` | 通用 |
| `project-workflow` | 项目工作流 | `ours` | 通用 |

## 结构调整参考

- 大领域可考虑拆二级：`security-engineering`、`reverse-engineering`。
- 长尾领域可考虑按产品化视角合并：营销增长、商业运营、研究学习、合规监管。
- 结构调整时需要同步：`README.md`、`CATALOG.md`、`DOMAIN-GLOSSARY.zh-CN.md`、`_merge-manifest.csv`、`../framework/core/03-routing.md` 和四态系统。
