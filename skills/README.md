# 能力库 · Skill Library

框架执行阶段（工作流 Phase 4/5）委托的具体技能。由 `../framework/core/03-routing.md` 的二级路由按领域选用。

> 这一层是框架的"双手"。大脑（何时恢复状态、如何路由、何时验证交付）在 `../framework/`。

## 规模与结构

**434 个技能 · 19 个领域大类**，由三个来源合并去重而成：

| 来源 | 含义 | 去重优先级 |
|---|---|---|
| `ours` | 本仓库从 J-SOP 抽取/沉淀 | 最高（同能力时保留） |
| `codex` | `~/.codex/skills`（含 `~/.claude/skills` 全部） | 次之 |
| `cskills` | C_Skills 收费技能库（163 个，逆向为主） | 再次 |

目录采用**双层**结构：`<领域大类>/<来源>/<skill-slug>/SKILL.md`。同一能力在多源出现时按上表优先级保留一个赢家；**根名不同的近义变体**（如 `python-dev` 与 `java-jvm-development`）作为不同技能保留。合并对照表见 `_merge-manifest.csv`。

> 容器型技能（`workflow-orchestration/codex/orchestration`、`quality-delivery/codex/tools`、`engineering-core/codex/domains`）的 `SKILL.md` 位于其子目录，整目录保留。

## 领域索引

### ai-automation — AI 与自动化（17）
> 来源：codex 11 · cskills 6
- **codex**：ai-agent-dev、ai-orchestrator、coff0xc-ai-agent-rag、mlops、playwright、playwright-e2e、playwright-interactive、prompt-engineering、rag-engineering、speech、transcribe
- **cskills**：agent-briefing、ai-engineering、ai-image-prompt、autojs-automation、llm-eval、mcp-tool-use

### backend-api — 后端与 API（26）
> 来源：ours 4 · codex 18 · cskills 4
- **ours**：background-jobs、dockerfile-best、echo-go-server、websocket-impl
- **codex**：anna-api-design、anna-backend-engineering、api-design、api-discovery、aspnet-core、cms-headless、coff0xc-api-data-platform、django-dev、event-driven、fastapi-dev、graphql-dev、laravel-dev、microservices、nestjs-dev、rails-dev、realtime-communication、service-mesh、spring-boot-dev
- **cskills**：api-engineering、backend-engineering、graphql-grpc-events、sdk-integration

### cloud-infra — 云与基础设施（17）
> 来源：codex 11 · cskills 6
- **codex**：chaos-engineering、cloudflare-deploy、disaster-recovery、docker-k8s、edge-computing、finops、monitoring-observability、netlify-deploy、render-deploy、sre-practices、vercel-deploy
- **cskills**：cloud-native、k8sops、platform-engineering、release-engineering、terraform、terraform-iac

### content-authoring — 内容创作与文档（14）
> 来源：codex 12 · cskills 2
- **codex**：coff0xc-office-doc-tools、coff0xc-research-drawio-diagram、doc-office、jupyter-notebook、notion-knowledge-capture、notion-meeting-intelligence、notion-research-documentation、notion-spec-to-implementation、pdf、quick-translate、research-paper-writing、technical-writing
- **cskills**：document-authoring、presentation-authoring

### data-analysis — 数据与分析（9）
> 来源：ours 3 · codex 5 · cskills 1
- **ours**：sync-bidirectional、validation-pipeline、validation-schema
- **codex**：anna-db-design、data-engineering、data-visualization、database、sql-optimization
- **cskills**：spreadsheet-analysis

### engineering-core — 通用工程模式（26）
> 来源：ours 19 · codex 6 · cskills 1
- **ours**：api-versioning、concurrency-patterns、datetime-timezones、dependency-injection、environment-config、error-handling-patterns、feature-flags、graceful-shutdown、http-caching、idempotency-design、memory-leaks、migration-zero-downtime、monorepo、pagination、rate-limiting-algorithms、regex-patterns、string-encoding、structured-logging、typescript-advanced
- **codex**：anna-perf-engineering、anna-shell-scripting、coff0xc-software-engineering、domains、shell-scripting、system-design
- **cskills**：ponytail

### frontend-ui — 前端与 UI（35）
> 来源：ours 7 · codex 24 · cskills 4
- **ours**：anti-detection、chrome-mv3-ext、css-modern-2025、dom-scraping、i18n-trio、panel-ui、preact-popup
- **codex**：UIdesign、accessibility、angular-dev、anna-ui-design、chatgpt-apps、coff0xc-ui-doc-output、figma、figma-code-connect-components、figma-create-design-system-rules、figma-create-new-file、figma-generate-design、figma-generate-library、figma-implement-design、figma-use、floatly-design-implementation、floatly-ui-style、frontend-dev、graphics-rendering、i18n-l10n、nextjs-dev、screenshot、svelte-dev、vue-dev、winui-app
- **cskills**：nextdev、react-development、screenshot-to-ui、ui-design

### hardware-systems — 硬件与系统（8）
> 来源：codex 3 · cskills 5
- **codex**：STM32外设驱动开发、STM32嵌入式核心开发、STM32进阶开发
- **cskills**：embedded-firmware、fpga-asic-hdl、linux-driver-development、uefi-development、windows-driver-development

### maps-location — 地图与位置（11）
> 来源：cskills 11
- **cskills**：amap-gaode、baidu-map、esri-arcgis、google-maps-platform、huawei-map-kit、leaflet-openlayers、map-gis-core、mapbox-maplibre、openstreetmap-routing、tencent-map、tianditu-map

### misc — 杂项（1）
> 来源：codex 1
- **codex**：hatch-pet

### mobile-crossplatform — 移动与跨端（18）
> 来源：codex 7 · cskills 11
- **codex**：anna-apple-development、anna-flutter-development、anna-uniapp-dev、flutter-dart-dev、kotlin-android-dev、react-native-dev、swift-ios-dev
- **cskills**：alipay-miniprogram、android-development、apple-development、douyin-miniprogram、electron-development、flutter-development、harmonyos-arkts、harmonyos-arkui、tauri-development、uniapp-development、wechat-miniprogram

### payments-commerce — 支付与电商（12）
> 来源：codex 1 · cskills 11
- **codex**：payment-fintech
- **cskills**：adyen、alipay-pay、apple-pay、checkout-com、google-pay、paypal、square、stripe、wallet-engineering、wallet-pass、wechat-pay

### product-growth — 产品与增长（8）
> 来源：codex 3 · cskills 5
- **codex**：anna-product-manager、linear、sentry
- **cskills**：ai-content-marketing、product-manager、product-marketing、project-promo-writer、social-media-ops

### programming-languages — 编程语言（21）
> 来源：codex 12 · cskills 9
- **codex**：anna-go-dev、anna-js-ts-dev、anna-python-dev、c-cpp-dev、csharp-dotnet-dev、go-dev、java-dev、js-ts-dev、php-dev、python-dev、ruby-dev、rust-dev
- **cskills**：cpp-development、dotnet-development、elixir-erlang-development、java-jvm-development、kotlin-development、lua-openresty-development、r-development、scala-development、typescript-development

### quality-delivery — 质量与交付（24）
> 来源：codex 19 · cskills 5
- **codex**：anna-code-audit、anna-git-workflow、anna-test-engineering、cli-creator、code-audit、code-migration、code-simplifier、commit、devex-tooling、gh-address-comments、gh-fix-ci、git-workflow、low-code、performance-testing、qa、refactor、testing、tools、yeet
- **cskills**：browser-automation、harmonyos-build-quality、observability、perf-engineering、test-engineering

### research-knowledge — 研究与知识（10）
> 来源：codex 6 · cskills 4
- **codex**：context7、game-dev、research-scientific-research、search-engine、web-fetch、web3-dapp
- **cskills**：academic-writing、legal-counsel、project-learning、research

### reverse-engineering — 逆向工程（63）
> 来源：codex 6 · cskills 57
- **codex**：android-reversing、anna-reverse-engineering、binary-exploit、dotnet-reversing、reverse-analysis、reverse-engineering
- **cskills**：abirev、asmrev、autorev、binrev、bootrev、carrev、cloudrev、containerrev、contractrev、crashrev、cryptrev、debugrev、diffrev、diskrev、docrev、dotnetrev、drmrev、ebpfrev、edrrev、fmtrev、fuzzrev、fwrev、gamerev、gorev、hvrev、hwrev、icsrev、iotrev、irrev、javarev、kernrev、linuxrev、macrev、malrev、memrev、mitirev、mlrev、mobile-reverse-engineering、opsecrev、packrev、protrev、rev-report、revauto、revlab、rktrev、rustrev、scriptrev、sdkrev、sigrev、supplyrev、swiftrev、ttdrev、vmrev、vulnrev、wasmrev、webrev、winrev

### security-engineering — 安全工程（85）
> 来源：codex 83 · cskills 2
- **codex**：ad-pentest、anna-mobile-security、api-security-test、backdoor-detector、blockchain-security、browser-security、bug-bounty、c2-framework、cdn-bypass、cloud-security、coff0xc-authorized-assessment、coff0xc-binary-mobile-iot、coff0xc-blockchain-security、coff0xc-cloud-devsecops、coff0xc-compliance-architecture、coff0xc-detection-response、coff0xc-identity-zero-trust、coff0xc-network-protocol-security、coff0xc-purple-deception、coff0xc-secure-code-appsec、coff0xc-vulnerability-lifecycle、compliance-audit、container-security、credential-access、crypto-security、ctf、data-exfiltration、data-security、detection-engineering、devsecops、edr-endpoint、email-security、evasion-toolkit、fingerprint-engine、forensics-analysis、full-pentest、graphql-pentest、honeypot、iac-devops、ics-scada、identity-security、incident-response、iot-security、kernel-security、lateral-movement、linux-hardening、llm-red-teaming、malware-analysis、mobile-security、network-monitoring、network-protocol、oauth-security、osint、pentest-report、phishing-simulation、post-exploitation、privacy-engineering、privilege-escalation、proxy-pool-manager、purple-team、quantum-security、recon-workflow、red-team-infra、red-team-poc、secrets-management、security-architecture、security-best-practices、security-ownership-map、security-threat-model、security-tool-dev、serverless-security、soc-operations、social-engineering、spa-pentest、supply-chain-security、threat-hunting、threat-intelligence、vuln-research、vulnerability-management、web-pentest、windows-hardening、wireless-security、zero-trust
- **cskills**：protocol-analysis、web-security

### workflow-orchestration — 工作流与编排（29）
> 来源：ours 9 · codex 20
- **ours**：local-workflow、project-workflow、source-command-audit、source-command-fix、source-command-implement、source-command-review、source-command-sprint、source-command-status、source-command-sync-docs
- **codex**：attack-chain-orchestrator、audit、autoredteam-orchestrator、coff0xc-skill-router、deep-thinking、dev、fix、implement、mcp-builder、memory、migrate-to-codex、orchestration、review、skill-creator、spec、spec-check、spec-do、sprint、status、sync-docs

## 分级与变体（框架路线图阶段 6）

- ✅ 已打"通用 / 半通用 / 项目定制"标记：**通用 323 · 半通用 85 · 项目定制 26**，详见 `TIERS.md`。
- ⏳ 近义变体 18 簇（多为 `anna-*` 与非-anna 并存）已列出，**精简 policy 待定夺**，见 `TIERS.md`。
- `_merge-manifest.csv`（已含 `tier` 列）是后续筛选的工作底稿。
