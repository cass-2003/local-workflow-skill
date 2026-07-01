# 能力库导览 · Skill Catalog

这份文件是给人看的能力地图。完整机器索引见 [`README.md`](README.md)，中英文对照见 [`DOMAIN-GLOSSARY.zh-CN.md`](DOMAIN-GLOSSARY.zh-CN.md)，合并底稿见 [`_merge-manifest.csv`](_merge-manifest.csv)，通用性分级见 [`TIERS.md`](TIERS.md)。

## 怎么使用

- **按任务说目标**：例如“我要做微信小程序登录支付闭环”“帮我审计 API 权限”“初始化一个 SaaS 项目并先问需求”。
- **让 Agent 自动路由**：工作流会根据意图和项目上下文，从下方领域里挑选合适 skill。
- **想人工查找时**：先看“按场景找”，再进入对应领域；需要完整 slug 时看 [`README.md`](README.md)。

## 按场景找

| 我想做什么 | 优先看这些领域 | 典型能力 |
|---|---|---|
| 新项目从想法起步 | `workflow-orchestration`、`product-management`、`frontend-ui`、`backend-api` | 需求访谈、项目地基、PRD、路线图、文档包、下一步工作包、目标驱动推进循环 |
| Web / 管理后台 / UI | `frontend-ui`、`content-authoring`、`quality-delivery` | 设计系统、页面实现、状态数据流、性能、可访问性、截图还原 |
| 后端 / API / 数据库 | `backend-api`、`data-analysis`、`engineering-core`、`security-engineering` | API 设计、认证授权、事务一致性、后台任务、实时通信、错误可观测性 |
| App / 小程序 / 跨端 | `mobile-crossplatform`、`payments-commerce`、`maps-location`、`product-growth` | App 架构、微信/支付宝小程序、登录支付、离线同步、推送、发布运营 |
| AI / Agent / RAG | `ai-automation`、`ai-governance-compliance`、`research-knowledge` | Agent 编排、RAG、Prompt、MLOps、LLM 评估、AI 合规 |
| 云部署 / DevOps / SRE | `cloud-infra`、`quality-delivery`、`engineering-core` | Docker/K8s、Render/Vercel/Netlify、监控、灾备、发布工程、FinOps |
| 测试 / 交付 / 重构 | `quality-delivery`、`engineering-core` | 测试工程、CI 修复、性能测试、代码审计、迁移、重构、commit 纪律 |
| 安全 / 渗透 / 合规 | `security-engineering`、`security-compliance`、`privacy-compliance`、`compliance-programs` | Web/API/云/移动安全、威胁建模、SOC、合规审计、隐私工程 |
| 逆向 / 二进制 / 固件 | `reverse-engineering`、`hardware-systems` | Android/Windows/Linux/固件/协议/恶意样本逆向、APK/JS 工具链编排、漏洞分析 |
| 产品 / 增长 / 运营 | `product-management`、`product-growth`、`growth-experiments`、`marketing-analytics` | 产品发现、路线图、A/B 实验、漏斗、SEO、增长实验 |
| 内容 / 营销 / 品牌 | `content-strategy`、`copywriting-editing`、`seo`、`social-media`、`brand-strategy` | 内容策略、文案、SEO、社媒、品牌指南、广告创意 |
| 商业 / 销售 / 收入 | `commercial-strategy`、`sales-enablement`、`revenue-operations`、`finance` | 定价、渠道、RFP、销售工程、SaaS 指标、收入运营 |
| 组织 / 项目 / 知识 | `project-management`、`business-operations`、`change-org-management`、`handoff-knowledge` | Scrum、会议分析、流程、知识运营、交接、组织健康 |
| 研究 / 学习 / 文档 | `research-knowledge`、`research-ops`、`literature-review`、`learning-design`、`markdown-publishing` | 文献综述、市场研究、课程设计、Markdown 文档/幻灯片 |

## 领域地图

### 工程开发

| 领域 | 覆盖内容 |
|---|---|
| `frontend-ui` | 前端开发、UI 设计、设计系统、Figma、可访问性、性能、状态数据流 |
| `backend-api` | API、后端框架、认证授权、数据库事务、后台任务、实时通信、SDK |
| `mobile-crossplatform` | iOS、Android、React Native、Flutter、Expo、uniapp、微信/支付宝小程序 |
| `programming-languages` | Python、JS/TS、Go、Rust、Java、C/C++、.NET、PHP、Ruby 等语言工程 |
| `engineering-core` | 通用工程模式、缓存、幂等、分页、限流、配置、错误处理、日志、迁移 |
| `data-analysis` | 数据工程、SQL、数据库设计、可视化、表格分析、校验 schema |
| `payments-commerce` | Stripe、PayPal、微信支付、支付宝、Apple Pay、Google Pay、钱包 |
| `maps-location` | 高德、百度、腾讯、Google Maps、Mapbox、Leaflet、GIS、路线规划 |
| `hardware-systems` | STM32、嵌入式、驱动、FPGA、UEFI、Linux/Windows driver |

### AI、自动化与工作流

| 领域 | 覆盖内容 |
|---|---|
| `workflow-orchestration` | 项目工作流、目标驱动推进循环、项目启动文档、规格执行、多 agent 编排、skill 创建 |
| `ai-automation` | Agent 开发、RAG、Prompt、Playwright、MLOps、语音、MCP、LLM guardrails |
| `ai-governance-compliance` | AI Act、AI 管理体系、AI 审计 |
| `research-knowledge` | Web fetch/search、Context7、科研写作、法律顾问、知识研究 |

### 云、质量与交付

| 领域 | 覆盖内容 |
|---|---|
| `cloud-infra` | Docker、Kubernetes、Render、Vercel、Netlify、Cloudflare、Terraform、SRE |
| `quality-delivery` | 测试工程、QA、CI 修复、CLI 工具、代码审计、迁移、重构、Git workflow |
| `security-engineering` | 渗透测试、云安全、移动安全、SOC、检测响应、红队、零信任、隐私工程 |
| `security-compliance` | SOC2、ISO27001 等安全合规准备 |
| `privacy-compliance` | GDPR、隐私审计 |
| `compliance-programs` | 合规项目准备 |

### 安全与逆向

| 领域 | 覆盖内容 |
|---|---|
| `reverse-engineering` | 二进制、Android、固件、协议、恶意样本、崩溃、内存、内核、WebAssembly、授权 APK/JS 工具链编排 |
| `security-engineering` | Web/API/云/容器/移动/IoT/区块链安全、安全架构、威胁建模 |
| `medical-regulatory` | FDA QSR、ISO13485、MDR 医疗监管 |
| `quality-management` | QMS、CAPA、质量文档 |

### 产品、增长与运营

| 领域 | 覆盖内容 |
|---|---|
| `product-management` | 产品发现、竞品拆解、PRD、路线图、实验设计、产品分析 |
| `product-growth` | 产品经理、产品营销、Sentry、Linear、推广写作、社媒运营 |
| `growth-experiments` | A/B 测试、免费工具增长、推荐计划 |
| `marketing-analytics` | 营销埋点、活动分析 |
| `conversion-optimization` | 表单、登录、付费墙、弹窗、落地页转化优化 |
| `app-store-growth` | ASO 应用商店增长 |
| `seo` / `answer-engine-optimization` | SEO、Schema、站点结构、AEO |

### 内容、品牌与市场

| 领域 | 覆盖内容 |
|---|---|
| `content-authoring` | Office、PDF、Notion、技术写作、研究文档、绘图、演示 |
| `content-strategy` | 内容策略、内容生产、内容创作者 |
| `copywriting-editing` | 文案、编辑、内容人味化 |
| `social-media` | 社媒内容、社媒分析、X/Twitter 增长 |
| `video-webinar-marketing` | 视频内容、YouTube、Webinar |
| `brand-strategy` | 品牌指南、竞品替代、营销心理 |
| `paid-acquisition` / `email-marketing` | 广告创意、付费获客、冷邮件、邮件序列 |

### 商业、销售与组织

| 领域 | 覆盖内容 |
|---|---|
| `commercial-strategy` | 定价、渠道、商业政策、合作伙伴、Deal Desk |
| `sales-enablement` | 销售工程、合同与提案 |
| `revenue-operations` | 收入运营 |
| `finance` | 财务分析、SaaS 指标 |
| `business-operations` | 采购、供应商、流程、知识运营、容量规划 |
| `project-management` | Scrum、会议分析、团队沟通、高级 PM |
| `change-org-management` | 组织变革、文化、Chief of Staff、组织健康 |
| `customer-success` | 客户成功 |

### 研究、学习与知识生产

| 领域 | 覆盖内容 |
|---|---|
| `research-ops` | 临床研究、市场研究、产品研究 |
| `literature-review` | 文献综述 |
| `learning-design` | 课程大纲与学习设计 |
| `markdown-publishing` | Markdown 文档、评审、幻灯片、设计系统文档 |
| `entity-research` | 实体档案、动态追踪 |
| `patent-intelligence` | 专利情报 |
| `grant-funding` | 基金与资助 |
| `personal-productivity` / `email-productivity` / `handoff-knowledge` | 捕捉、反思、收件箱、交接 |

## 常用触发说法

```text
使用项目启动工作流，先问需求，不要先写文件。
帮我把这个想法变成 PRD、架构和下一步工作包。
你继续推进这个项目：先定一个小目标，验证、自审、修复、同步状态并 commit。
帮我审计这个 API 的权限、错误处理和可观测性。
用移动端/小程序工程能力规划微信小程序登录支付闭环。
帮我做前端页面实现和设计系统落地。
帮我做后端 API、数据库事务和认证授权设计。
帮我检查当前改动是否满足验证、文档同步和 commit 闭环。
```

## 读完整索引

- 完整领域与 skill slug：[`skills/README.md`](README.md)
- 领域与 skill 中文对照：[`DOMAIN-GLOSSARY.zh-CN.md`](DOMAIN-GLOSSARY.zh-CN.md)
- 通用 / 半通用分级：[`skills/TIERS.md`](TIERS.md)
- 工作流路由矩阵：[`../framework/core/03-routing.md`](../framework/core/03-routing.md)
- 合并来源与去重结果：[`_merge-manifest.csv`](_merge-manifest.csv)
