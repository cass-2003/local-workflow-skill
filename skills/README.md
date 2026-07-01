# 能力库 · Skill Library

框架执行阶段（工作流 Phase 4/5）委托的具体技能。由 `../framework/core/03-routing.md` 的二级路由按领域选用。

> 这一层是框架的"双手"。大脑（何时恢复状态、如何路由、何时验证交付）在 `../framework/`。

## 先看哪里

- 想知道“这个能力库覆盖哪些方向”：先看 [`CATALOG.md`](CATALOG.md)。
- 想看英文目录和 skill slug 的中文含义：看 [`DOMAIN-GLOSSARY.zh-CN.md`](DOMAIN-GLOSSARY.zh-CN.md)。
- 想按领域找所有 skill slug：继续看本文的“领域索引”。
- 想看通用 / 半通用分级：看 [`TIERS.md`](TIERS.md)。
- 想看来源、去重和赢家记录：看 [`_merge-manifest.csv`](_merge-manifest.csv)。

常用问法：

```text
用项目启动工作流，先问需求，不要先写文件。
帮我规划一个微信小程序的登录支付和租户管理能力。
帮我审计后端 API 的权限、错误处理和可观测性。
帮我做前端设计系统落地和页面实现。
帮我检查当前改动是否满足验证、文档同步和 commit 闭环。
```

## 规模与结构

**567 个技能 · 58 个领域大类**，由三个来源层合并去重并剔除项目定制项而成：

| 来源 | 含义 | 去重优先级 |
|---|---|---|
| `ours` | 本仓库沉淀的通用工作流与可复用技能 | 最高（同能力时保留） |
| `codex` | `~/.codex/skills`（含 `~/.claude/skills` 全部） | 次之 |
| `community` | 许可清晰的第三方授权 skill 导入，含开源与已获授权来源 | 再次 |

目录采用**双层**结构：`<领域大类>/<来源>/<skill-slug>/SKILL.md`。同一能力在多源出现时按上表优先级保留一个赢家；**根名不同的近义变体**（如 `python-dev` 与 `java-jvm-development`）作为不同技能保留。合并对照表见 `_merge-manifest.csv`。

> **Coffee/Coff0xc 授权导入**：18 个 `coff0xc-*` 技能已在保留本仓库规范化 slug 的前提下更新到 `Coff0xc/coffee-skill` 授权版本；来源、许可与映射记录见 `../tools/skill-merge/provenance/coffee-skill/`。

> **Community 授权导入**：community 层统一承载许可清晰的第三方授权技能；其中 108 个来自 MIT 许可的 `alirezarezvani/claude-skills`，覆盖业务、营销、合规、研究、生产力和管理等非工程领域；导入记录见 `../tools/skill-merge/provenance/claude-skills-community/`。

> **`-2` 后缀**：少数同域同源里有两个同主题但内容不同的技能（合并自不同作者），后到的取 `<名>-2`（如 `python-dev` / `python-dev-2`）。两者都保留，路由时按 `description` 择一。

> 容器型技能（`workflow-orchestration/codex/orchestration`、`quality-delivery/codex/tools`、`engineering-core/codex/domains`）的 `SKILL.md` 位于其子目录，整目录保留。

## 领域索引

### ai-automation — AI 与自动化（18）
> 来源：codex 11 · community 6 · ours 1
- **codex**：ai-agent-dev、ai-agent-rag、ai-orchestrator、mlops、playwright、playwright-e2e、playwright-interactive、prompt-engineering、rag-engineering、speech、transcribe
- **community**：agent-briefing、ai-engineering、ai-image-prompt、autojs-automation、llm-eval、mcp-tool-use
- **ours**：llm-guardrails

### ai-governance-compliance — AI 治理合规（2）
> 来源：community 2
- **community**：ai-act-readiness、aims-audit

### answer-engine-optimization — 答案引擎优化（1）
> 来源：community 1
- **community**：aeo

### app-store-growth — 应用商店增长（1）
> 来源：community 1
- **community**：app-store-optimization

### backend-api — 后端与 API（29）
> 来源：codex 19 · community 4 · ours 6
- **codex**：api-data-platform、api-design、api-design-2、api-discovery、aspnet-core、backend-engineering、cms-headless、django-dev、event-driven、fastapi-dev、graphql-dev、laravel-dev、microservices、nestjs-dev、rails-dev、realtime-communication、service-mesh、spring-boot-dev、supabase-postgres-best-practices
- **community**：api-engineering、backend-engineering、graphql-grpc-events、sdk-integration
- **ours**：api-error-observability、auth-access-control、background-jobs、database-transaction-consistency、dockerfile-best、websocket-impl

### brand-strategy — 品牌策略（3）
> 来源：community 3
- **community**：brand-guidelines、competitor-alternatives、marketing-psychology

### business-operations — 业务运营（6）
> 来源：community 6
- **community**：capacity-planner、internal-comms、knowledge-ops、process-mapper、procurement-optimizer、vendor-management

### change-org-management — 组织变革管理（4）
> 来源：community 4
- **community**：change-management、chief-of-staff、culture-architect、org-health-diagnostic

### cloud-infra — 云与基础设施（37）
> 来源：codex 31 · community 6
- **codex**：chaos-engineering、cloudflare-deploy、disaster-recovery、docker-k8s、edge-computing、finops、monitoring-observability、netlify-deploy、render-background-workers、render-blueprints、render-cli、render-cron-jobs、render-debug、render-deploy、render-disks、render-docker、render-domains、render-env-vars、render-keyvalue、render-mcp、render-migrate-from-heroku、render-monitor、render-networking、render-postgres、render-private-services、render-scaling、render-static-sites、render-web-services、render-workflows、sre-practices、vercel-deploy
- **community**：cloud-native、k8sops、platform-engineering、release-engineering、terraform、terraform-iac

### commercial-strategy — 商业策略（7）
> 来源：community 7
- **community**：channel-economics、commercial-forecaster、commercial-policy、deal-desk、partnerships-architect、pricing-strategist、rfp-responder

### compliance-programs — 合规项目（1）
> 来源：community 1
- **community**：compliance-readiness

### content-authoring — 内容创作与文档（14）
> 来源：codex 12 · community 2
- **codex**：doc-office、jupyter-notebook、notion-knowledge-capture、notion-meeting-intelligence、notion-research-documentation、notion-spec-to-implementation、office-doc-tools、pdf、quick-translate、research-drawio-diagram、research-paper-writing、technical-writing
- **community**：document-authoring、presentation-authoring

### content-strategy — 内容策略（3）
> 来源：community 3
- **community**：content-creator、content-production、content-strategy

### conversion-optimization — 转化率优化（6）
> 来源：community 6
- **community**：form-cro、onboarding-cro、page-cro、paywall-upgrade-cro、popup-cro、signup-flow-cro

### copywriting-editing — 文案与编辑（3）
> 来源：community 3
- **community**：content-humanizer、copy-editing、copywriting

### customer-success — 客户成功（1）
> 来源：community 1
- **community**：customer-success-manager

### data-analysis — 数据与分析（9）
> 来源：codex 7 · community 1 · ours 1
- **codex**：airtable-filters、airtable-overview、data-engineering、data-visualization、database、db-design、sql-optimization
- **community**：spreadsheet-analysis
- **ours**：validation-schema

### email-marketing — 邮件营销（2）
> 来源：community 2
- **community**：cold-email、email-sequence

### email-productivity — 邮件生产力（2）
> 来源：community 2
- **community**：inbox-setup、inbox-triage

### engineering-core — 通用工程模式（26）
> 来源：codex 6 · community 1 · ours 19
- **codex**：domains、perf-engineering、shell-scripting、shell-scripting-2、software-engineering、system-design
- **community**：ponytail
- **ours**：api-versioning、concurrency-patterns、datetime-timezones、dependency-injection、environment-config、error-handling-patterns、feature-flags、graceful-shutdown、http-caching、idempotency-design、memory-leaks、migration-zero-downtime、monorepo、pagination、rate-limiting-algorithms、regex-patterns、string-encoding、structured-logging、typescript-advanced

### entity-research — 实体研究（2）
> 来源：community 2
- **community**：dossier、pulse

### executive-strategy — 高层战略（4）
> 来源：community 4
- **community**：board-deck-builder、decision-logger、scenario-war-room、strategic-alignment

### finance — 财务与指标（2）
> 来源：community 2
- **community**：financial-analyst、saas-metrics-coach

### frontend-ui — 前端与 UI（30）
> 来源：codex 22 · community 4 · ours 4
- **codex**：UIdesign、accessibility、angular-dev、chatgpt-apps、figma、figma-code-connect-components、figma-create-design-system-rules、figma-create-new-file、figma-generate-design、figma-generate-library、figma-implement-design、figma-use、frontend-dev、graphics-rendering、i18n-l10n、nextjs-dev、screenshot、svelte-dev、ui-design、ui-doc-output、vue-dev、winui-app
- **community**：nextdev、react-development、screenshot-to-ui、ui-design
- **ours**：css-modern-2025、design-system-implementation、frontend-performance、frontend-state-data-flow

### grant-funding — 基金与资助（1）
> 来源：community 1
- **community**：grants

### growth-experiments — 增长实验（3）
> 来源：community 3
- **community**：ab-test-setup、free-tool-strategy、referral-program

### handoff-knowledge — 交接与知识传递（1）
> 来源：community 1
- **community**：handoff

### hardware-systems — 硬件与系统（8）
> 来源：codex 3 · community 5
- **codex**：STM32外设驱动开发、STM32嵌入式核心开发、STM32进阶开发
- **community**：embedded-firmware、fpga-asic-hdl、linux-driver-development、uefi-development、windows-driver-development

### launch-management — 发布管理（1）
> 来源：community 1
- **community**：launch-strategy

### learning-design — 学习设计（1）
> 来源：community 1
- **community**：syllabus

### literature-review — 文献综述（1）
> 来源：community 1
- **community**：litreview

### maps-location — 地图与位置（11）
> 来源：community 11
- **community**：amap-gaode、baidu-map、esri-arcgis、google-maps-platform、huawei-map-kit、leaflet-openlayers、map-gis-core、mapbox-maplibre、openstreetmap-routing、tencent-map、tianditu-map

### markdown-publishing — Markdown 发布（4）
> 来源：community 4
- **community**：design-system、md-document、md-review、md-slides

### marketing-analytics — 营销分析（2）
> 来源：community 2
- **community**：analytics-tracking、campaign-analytics

### medical-regulatory — 医疗监管（3）
> 来源：community 3
- **community**：fda-qsr-audit-prep、iso13485-audit-prep、mdr-745-specialist

### mobile-crossplatform — 移动与跨端（37）
> 来源：codex 18 · community 11 · ours 8
- **codex**：apple-development、building-native-ui、codex-expo-run-actions、expo-api-routes、expo-cicd-workflows、expo-deployment、expo-dev-client、expo-module、expo-tailwind-setup、flutter-dart-dev、flutter-development、kotlin-android-dev、native-data-fetching、react-native-dev、swift-ios-dev、uniapp-dev、upgrading-expo、use-dom
- **community**：alipay-miniprogram、android-development、apple-development、douyin-miniprogram、electron-development、flutter-development、harmonyos-arkts、harmonyos-arkui、tauri-development、uniapp-development、wechat-miniprogram
- **ours**：mini-program-architecture、mini-program-login-payment、mobile-app-architecture、mobile-app-release-ops、mobile-offline-sync、mobile-push-notifications、taro-uniapp-crossplatform、wechat-miniprogram-engineering

### paid-acquisition — 付费获客（3）
> 来源：community 3
- **community**：ad-creative、marketing-demand-acquisition、paid-ads

### patent-intelligence — 专利情报（1）
> 来源：community 1
- **community**：patent

### payments-commerce — 支付与电商（12）
> 来源：codex 1 · community 11
- **codex**：payment-fintech
- **community**：adyen、alipay-pay、apple-pay、checkout-com、google-pay、paypal、square、stripe、wallet-engineering、wallet-pass、wechat-pay

### personal-productivity — 个人生产力（2）
> 来源：community 2
- **community**：capture、reflect

### privacy-compliance — 隐私合规（1）
> 来源：community 1
- **community**：gdpr-audit-prep

### product-growth — 产品与增长（8）
> 来源：codex 3 · community 5
- **codex**：linear、product-manager、sentry
- **community**：ai-content-marketing、product-manager、product-marketing、project-promo-writer、social-media-ops

### product-management — 产品管理（8）
> 来源：community 8
- **community**：code-to-prd、competitive-teardown、experiment-designer、product-analytics、product-discovery、product-strategist、research-summarizer、roadmap-communicator

### programming-languages — 编程语言（21）
> 来源：codex 12 · community 9
- **codex**：c-cpp-dev、csharp-dotnet-dev、go-dev、go-dev-2、java-dev、js-ts-dev、js-ts-dev-2、php-dev、python-dev、python-dev-2、ruby-dev、rust-dev
- **community**：cpp-development、dotnet-development、elixir-erlang-development、java-jvm-development、kotlin-development、lua-openresty-development、r-development、scala-development、typescript-development

### project-management — 项目管理（4）
> 来源：community 4
- **community**：meeting-analyzer、scrum-master、senior-pm、team-communications

### quality-delivery — 质量与交付（24）
> 来源：codex 19 · community 5
- **codex**：cli-creator、code-audit、code-audit-2、code-migration、code-simplifier、commit、devex-tooling、gh-address-comments、gh-fix-ci、git-workflow、git-workflow-2、low-code、performance-testing、qa、refactor、test-engineering、testing、tools、yeet
- **community**：browser-automation、harmonyos-build-quality、observability、perf-engineering、test-engineering

### quality-management — 质量管理（3）
> 来源：community 3
- **community**：capa-officer、qms-audit-expert、quality-documentation-manager

### research-knowledge — 研究与知识（10）
> 来源：codex 6 · community 4
- **codex**：context7、game-dev、research-scientific-research、search-engine、web-fetch、web3-dapp
- **community**：academic-writing、legal-counsel、project-learning、research

### research-ops — 研究运营（3）
> 来源：community 3
- **community**：clinical-research、market-research、product-research

### revenue-operations — 收入运营（1）
> 来源：community 1
- **community**：revenue-operations

### reverse-engineering — 逆向工程（64）
> 来源：codex 6 · community 57 · ours 1
- **codex**：android-reversing、binary-exploit、dotnet-reversing、reverse-analysis、reverse-engineering、reverse-engineering-2
- **community**：abirev、asmrev、autorev、binrev、bootrev、carrev、cloudrev、containerrev、contractrev、crashrev、cryptrev、debugrev、diffrev、diskrev、docrev、dotnetrev、drmrev、ebpfrev、edrrev、fmtrev、fuzzrev、fwrev、gamerev、gorev、hvrev、hwrev、icsrev、iotrev、irrev、javarev、kernrev、linuxrev、macrev、malrev、memrev、mitirev、mlrev、mobile-reverse-engineering、opsecrev、packrev、protrev、rev-report、revauto、revlab、rktrev、rustrev、scriptrev、sdkrev、sigrev、supplyrev、swiftrev、ttdrev、vmrev、vulnrev、wasmrev、webrev、winrev
- **ours**：reverse-toolkit-orchestration

### sales-enablement — 销售赋能（2）
> 来源：community 2
- **community**：contract-and-proposal-writer、sales-engineer

### security-compliance — 安全合规（2）
> 来源：community 2
- **community**：iso27001-audit-prep、soc2-audit-prep

### security-engineering — 安全工程（85）
> 来源：codex 83 · community 2
- **codex**：ad-pentest、api-security-test、authorized-assessment、backdoor-detector、binary-mobile-iot、blockchain-security、blockchain-security-2、browser-security、bug-bounty、c2-framework、cdn-bypass、cloud-devsecops、cloud-security、compliance-architecture、compliance-audit、container-security、credential-access、crypto-security、ctf、data-exfiltration、data-security、detection-engineering、detection-response、devsecops、edr-endpoint、email-security、evasion-toolkit、fingerprint-engine、forensics-analysis、full-pentest、graphql-pentest、honeypot、iac-devops、ics-scada、identity-security、identity-zero-trust、incident-response、iot-security、kernel-security、lateral-movement、linux-hardening、llm-red-teaming、malware-analysis、mobile-security、mobile-security-2、network-monitoring、network-protocol、network-protocol-security、oauth-security、osint、pentest-report、phishing-simulation、post-exploitation、privacy-engineering、privilege-escalation、proxy-pool-manager、purple-deception、purple-team、quantum-security、recon-workflow、red-team-infra、red-team-poc、secrets-management、secure-code-appsec、security-architecture、security-best-practices、security-ownership-map、security-threat-model、security-tool-dev、serverless-security、soc-operations、social-engineering、spa-pentest、supply-chain-security、threat-hunting、threat-intelligence、vuln-research、vulnerability-lifecycle、vulnerability-management、web-pentest、windows-hardening、wireless-security、zero-trust
- **community**：protocol-analysis、web-security

### seo — SEO（4）
> 来源：community 4
- **community**：programmatic-seo、schema-markup、seo-audit、site-architecture

### social-media — 社交媒体（4）
> 来源：community 4
- **community**：social-content、social-media-analyzer、social-media-manager、x-twitter-growth

### video-webinar-marketing — 视频与 Webinar 营销（3）
> 来源：community 3
- **community**：video-content-strategist、webinar-marketing、youtube-full

### workflow-orchestration — 工作流与编排（16）
> 来源：codex 12 · ours 4
- **codex**：attack-chain-orchestrator、autoredteam-orchestrator、deep-thinking、dev、mcp-builder、memory、orchestration、skill-creator、skill-router、spec、spec-check、spec-do
- **ours**：goal-driven-project-loop、local-workflow、project-inception-docs、project-workflow
## 分级与变体（框架路线图阶段 6）

- ✅ 已打"通用 / 半通用"标记，并剔除项目定制项：**通用 484 · 半通用 83 · 项目定制 0**，详见 `TIERS.md`。
- ✅ 已去掉全部 `anna-*`/`coff0xc-*` 前缀（36 个，技能全保留）；同域同源真撞名的 10 个取 `-2` 后缀。
- `_merge-manifest.csv`（已含 `tier` 列）是后续筛选的工作底稿。
