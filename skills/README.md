# 能力库 · Skill Library

框架执行阶段（工作流 Phase 4/5）委托的具体技能。由 `../framework/core/03-routing.md` 的二级路由按领域选用。

> 这一层是框架的"双手"。大脑（何时恢复状态、如何路由、何时验证交付）在 `../framework/`。

## 规模与结构

**439 个技能 · 24 个领域大类**，由四个来源合并去重并剔除项目定制项而成：

| 来源 | 含义 | 去重优先级 |
|---|---|---|
| `ours` | 本仓库沉淀的通用工作流与可复用技能 | 最高（同能力时保留） |
| `codex` | `~/.codex/skills`（含 `~/.claude/skills` 全部） | 次之 |
| `community` | 许可清晰的第三方开源 skill 库导入 | 再次 |
| `cskills` | C_Skills 收费技能库（逆向为主） | 最后 |

目录采用**双层**结构：`<领域大类>/<来源>/<skill-slug>/SKILL.md`。同一能力在多源出现时按上表优先级保留一个赢家；**根名不同的近义变体**（如 `python-dev` 与 `java-jvm-development`）作为不同技能保留。合并对照表见 `_merge-manifest.csv`。

> **Coffee/Coff0xc 授权导入**：18 个 `coff0xc-*` 技能已在保留本仓库规范化 slug 的前提下更新到 `Coff0xc/coffee-skill` 授权版本；来源、许可与映射记录见 `../tools/skill-merge/provenance/coffee-skill/`。

> **Community 开源导入**：首批 30 个业务/商业/财务/产品/项目管理/研究运营技能来自 MIT 许可的 `alirezarezvani/claude-skills`，导入记录见 `../tools/skill-merge/provenance/claude-skills-community/`。

> **`-2` 后缀**：少数同域同源里有两个同主题但内容不同的技能（合并自不同作者），后到的取 `<名>-2`（如 `python-dev` / `python-dev-2`）。两者都保留，路由时按 `description` 择一。

> 容器型技能（`workflow-orchestration/codex/orchestration`、`quality-delivery/codex/tools`、`engineering-core/codex/domains`）的 `SKILL.md` 位于其子目录，整目录保留。

## 领域索引

### ai-automation — AI 与自动化（18）
> 来源：codex 11 · cskills 6 · ours 1
- **codex**：ai-agent-dev、ai-agent-rag、ai-orchestrator、mlops、playwright、playwright-e2e、playwright-interactive、prompt-engineering、rag-engineering、speech、transcribe
- **cskills**：agent-briefing、ai-engineering、ai-image-prompt、autojs-automation、llm-eval、mcp-tool-use
- **ours**：llm-guardrails

### backend-api — 后端与 API（25）
> 来源：codex 18 · cskills 4 · ours 3
- **codex**：api-data-platform、api-design、api-design-2、api-discovery、aspnet-core、backend-engineering、cms-headless、django-dev、event-driven、fastapi-dev、graphql-dev、laravel-dev、microservices、nestjs-dev、rails-dev、realtime-communication、service-mesh、spring-boot-dev
- **cskills**：api-engineering、backend-engineering、graphql-grpc-events、sdk-integration
- **ours**：background-jobs、dockerfile-best、websocket-impl

### business-operations — 业务运营（6）
> 来源：community 6
- **community**：capacity-planner、internal-comms、knowledge-ops、process-mapper、procurement-optimizer、vendor-management

### cloud-infra — 云与基础设施（17）
> 来源：codex 11 · cskills 6
- **codex**：chaos-engineering、cloudflare-deploy、disaster-recovery、docker-k8s、edge-computing、finops、monitoring-observability、netlify-deploy、render-deploy、sre-practices、vercel-deploy
- **cskills**：cloud-native、k8sops、platform-engineering、release-engineering、terraform、terraform-iac

### commercial-strategy — 商业策略（7）
> 来源：community 7
- **community**：channel-economics、commercial-forecaster、commercial-policy、deal-desk、partnerships-architect、pricing-strategist、rfp-responder

### content-authoring — 内容创作与文档（14）
> 来源：codex 12 · cskills 2
- **codex**：doc-office、jupyter-notebook、notion-knowledge-capture、notion-meeting-intelligence、notion-research-documentation、notion-spec-to-implementation、office-doc-tools、pdf、quick-translate、research-drawio-diagram、research-paper-writing、technical-writing
- **cskills**：document-authoring、presentation-authoring

### data-analysis — 数据与分析（7）
> 来源：codex 5 · cskills 1 · ours 1
- **codex**：data-engineering、data-visualization、database、db-design、sql-optimization
- **cskills**：spreadsheet-analysis
- **ours**：validation-schema

### engineering-core — 通用工程模式（26）
> 来源：codex 6 · cskills 1 · ours 19
- **codex**：domains、perf-engineering、shell-scripting、shell-scripting-2、software-engineering、system-design
- **cskills**：ponytail
- **ours**：api-versioning、concurrency-patterns、datetime-timezones、dependency-injection、environment-config、error-handling-patterns、feature-flags、graceful-shutdown、http-caching、idempotency-design、memory-leaks、migration-zero-downtime、monorepo、pagination、rate-limiting-algorithms、regex-patterns、string-encoding、structured-logging、typescript-advanced

### finance — 财务与指标（2）
> 来源：community 2
- **community**：financial-analyst、saas-metrics-coach

### frontend-ui — 前端与 UI（27）
> 来源：codex 22 · cskills 4 · ours 1
- **codex**：UIdesign、accessibility、angular-dev、chatgpt-apps、figma、figma-code-connect-components、figma-create-design-system-rules、figma-create-new-file、figma-generate-design、figma-generate-library、figma-implement-design、figma-use、frontend-dev、graphics-rendering、i18n-l10n、nextjs-dev、screenshot、svelte-dev、ui-design、ui-doc-output、vue-dev、winui-app
- **cskills**：nextdev、react-development、screenshot-to-ui、ui-design
- **ours**：css-modern-2025

### hardware-systems — 硬件与系统（8）
> 来源：codex 3 · cskills 5
- **codex**：STM32外设驱动开发、STM32嵌入式核心开发、STM32进阶开发
- **cskills**：embedded-firmware、fpga-asic-hdl、linux-driver-development、uefi-development、windows-driver-development

### maps-location — 地图与位置（11）
> 来源：cskills 11
- **cskills**：amap-gaode、baidu-map、esri-arcgis、google-maps-platform、huawei-map-kit、leaflet-openlayers、map-gis-core、mapbox-maplibre、openstreetmap-routing、tencent-map、tianditu-map

### mobile-crossplatform — 移动与跨端（18）
> 来源：codex 7 · cskills 11
- **codex**：apple-development、flutter-dart-dev、flutter-development、kotlin-android-dev、react-native-dev、swift-ios-dev、uniapp-dev
- **cskills**：alipay-miniprogram、android-development、apple-development、douyin-miniprogram、electron-development、flutter-development、harmonyos-arkts、harmonyos-arkui、tauri-development、uniapp-development、wechat-miniprogram

### payments-commerce — 支付与电商（12）
> 来源：codex 1 · cskills 11
- **codex**：payment-fintech
- **cskills**：adyen、alipay-pay、apple-pay、checkout-com、google-pay、paypal、square、stripe、wallet-engineering、wallet-pass、wechat-pay

### product-growth — 产品与增长（8）
> 来源：codex 3 · cskills 5
- **codex**：linear、product-manager、sentry
- **cskills**：ai-content-marketing、product-manager、product-marketing、project-promo-writer、social-media-ops

### product-management — 产品管理（8）
> 来源：community 8
- **community**：code-to-prd、competitive-teardown、experiment-designer、product-analytics、product-discovery、product-strategist、research-summarizer、roadmap-communicator

### programming-languages — 编程语言（21）
> 来源：codex 12 · cskills 9
- **codex**：c-cpp-dev、csharp-dotnet-dev、go-dev、go-dev-2、java-dev、js-ts-dev、js-ts-dev-2、php-dev、python-dev、python-dev-2、ruby-dev、rust-dev
- **cskills**：cpp-development、dotnet-development、elixir-erlang-development、java-jvm-development、kotlin-development、lua-openresty-development、r-development、scala-development、typescript-development

### project-management — 项目管理（4）
> 来源：community 4
- **community**：meeting-analyzer、scrum-master、senior-pm、team-communications

### quality-delivery — 质量与交付（24）
> 来源：codex 19 · cskills 5
- **codex**：cli-creator、code-audit、code-audit-2、code-migration、code-simplifier、commit、devex-tooling、gh-address-comments、gh-fix-ci、git-workflow、git-workflow-2、low-code、performance-testing、qa、refactor、test-engineering、testing、tools、yeet
- **cskills**：browser-automation、harmonyos-build-quality、observability、perf-engineering、test-engineering

### research-knowledge — 研究与知识（10）
> 来源：codex 6 · cskills 4
- **codex**：context7、game-dev、research-scientific-research、search-engine、web-fetch、web3-dapp
- **cskills**：academic-writing、legal-counsel、project-learning、research

### research-ops — 研究运营（3）
> 来源：community 3
- **community**：clinical-research、market-research、product-research

### reverse-engineering — 逆向工程（63）
> 来源：codex 6 · cskills 57
- **codex**：android-reversing、binary-exploit、dotnet-reversing、reverse-analysis、reverse-engineering、reverse-engineering-2
- **cskills**：abirev、asmrev、autorev、binrev、bootrev、carrev、cloudrev、containerrev、contractrev、crashrev、cryptrev、debugrev、diffrev、diskrev、docrev、dotnetrev、drmrev、ebpfrev、edrrev、fmtrev、fuzzrev、fwrev、gamerev、gorev、hvrev、hwrev、icsrev、iotrev、irrev、javarev、kernrev、linuxrev、macrev、malrev、memrev、mitirev、mlrev、mobile-reverse-engineering、opsecrev、packrev、protrev、rev-report、revauto、revlab、rktrev、rustrev、scriptrev、sdkrev、sigrev、supplyrev、swiftrev、ttdrev、vmrev、vulnrev、wasmrev、webrev、winrev

### security-engineering — 安全工程（85）
> 来源：codex 83 · cskills 2
- **codex**：ad-pentest、api-security-test、authorized-assessment、backdoor-detector、binary-mobile-iot、blockchain-security、blockchain-security-2、browser-security、bug-bounty、c2-framework、cdn-bypass、cloud-devsecops、cloud-security、compliance-architecture、compliance-audit、container-security、credential-access、crypto-security、ctf、data-exfiltration、data-security、detection-engineering、detection-response、devsecops、edr-endpoint、email-security、evasion-toolkit、fingerprint-engine、forensics-analysis、full-pentest、graphql-pentest、honeypot、iac-devops、ics-scada、identity-security、identity-zero-trust、incident-response、iot-security、kernel-security、lateral-movement、linux-hardening、llm-red-teaming、malware-analysis、mobile-security、mobile-security-2、network-monitoring、network-protocol、network-protocol-security、oauth-security、osint、pentest-report、phishing-simulation、post-exploitation、privacy-engineering、privilege-escalation、proxy-pool-manager、purple-deception、purple-team、quantum-security、recon-workflow、red-team-infra、red-team-poc、secrets-management、secure-code-appsec、security-architecture、security-best-practices、security-ownership-map、security-threat-model、security-tool-dev、serverless-security、soc-operations、social-engineering、spa-pentest、supply-chain-security、threat-hunting、threat-intelligence、vuln-research、vulnerability-lifecycle、vulnerability-management、web-pentest、windows-hardening、wireless-security、zero-trust
- **cskills**：protocol-analysis、web-security

### workflow-orchestration — 工作流与编排（15）
> 来源：codex 12 · ours 3
- **codex**：attack-chain-orchestrator、autoredteam-orchestrator、deep-thinking、dev、mcp-builder、memory、orchestration、skill-creator、skill-router、spec、spec-check、spec-do
- **ours**：local-workflow、project-inception-docs、project-workflow

## 分级与变体（框架路线图阶段 6）

- ✅ 已打"通用 / 半通用"标记，并剔除项目定制项：**通用 390 · 半通用 49 · 项目定制 0**，详见 `TIERS.md`。
- ✅ 已去掉全部 `anna-*`/`coff0xc-*` 前缀（36 个，技能全保留）；同域同源真撞名的 10 个取 `-2` 后缀。
- `_merge-manifest.csv`（已含 `tier` 列）是后续筛选的工作底稿。
