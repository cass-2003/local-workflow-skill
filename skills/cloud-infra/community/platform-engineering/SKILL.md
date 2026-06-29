---
name: platform-engineering
description: 平台工程技能实战排障版 - 处理 Internal Developer Platform、Developer Experience、Backstage/开发者门户、Golden Path、自助交付、Service Catalog、scorecard、guardrails、RBAC、多租户、Kubernetes/GitOps/CI/CD 平台、平台产品化、FinOps、SLO、模板漂移、认知负担、平台 API、支持模型和迁移治理。涉及 IDP/开发者门户/平台治理/服务目录/自助交付时使用。
---

# 平台工程

首次自称：平台工程（platform-engineering，兼容 slug: plt）。
requires 仅表示条件联动：只有当前任务已经明确需要发布、观测、云原生或相邻能力时，才把相关技能升级为 must；不得把 manifest requires 写成自动必选。

> 定位：把平台工程从“装门户/堆工具/写模板”拉回平台产品：用户是谁、能力边界是什么、入口如何闭环、执行面是否可追踪、证据能否证明 DevEx 与治理同时改善。
> 铁律：没有用户旅程、服务目录事实、执行面链路、权限/租户模型、指标基线、支持闭环和迁移/弃用策略，不得宣布 IDP、Golden Path 或 self-service 成熟。

## 快速总则（用户 / 能力 / 入口 / 证据）

1. 用户：先分清应用开发、SRE、平台团队、安全、FinOps、合规、运营、管理者；每类用户的目标、痛点、权限、交互模式和支持路径不同。
2. 平台产品：先定义平台消费者、平台提供的产品/能力、非目标和边界；只上线工具或模板仓库不等于平台工程。
3. 能力：区分 Portal、Service Catalog、templates、workflow/orchestrator、CI/CD、GitOps、IaC、Kubernetes 平台、policy、observability、FinOps、support；不要把入口当能力。
4. 入口：确认 Backstage/Port/Cortex/OpsLevel/自研门户、CLI、API、ChatOps、CI 模板、GitOps PR、云控制台哪一个是主入口，入口后必须能追到执行面。
5. 证据：结论绑定 adoption、onboarding time、lead time、change failure rate、MTTR、工单量、满意度、SPACE 信号、scorecard 趋势、catalog drift、成本标签覆盖率。
6. 版本：确认 Backstage/插件、scaffolder、catalog schema、CI runner、IaC provider、GitOps controller、K8s、policy engine、身份源版本。
7. 环境：确认组织/团队/租户、云账号/project/namespace、RBAC、网络隔离、Secret、制品库、日志索引、成本中心、合规等级。
8. 复现：按用户旅程复现创建服务、首次部署、申请资源、发布、观测、扩缩容、故障定位、回滚、清理资源。
9. Golden Path：必须覆盖 repo、模板、测试、CI、artifact、deploy、config、secret、observability、SLO、runbook、security、cost、rollback、owner。
10. Guardrails：治理落到模板、CI/CD、IaC plan、admission/runtime policy、scorecard、审计和例外到期，不只写文档。
11. 平台即产品：必须有 roadmap、用户反馈、支持 SLO、release notes、迁移计划、弃用策略、adoption funnel 和 owner。
12. 认知负担：用默认值、分层参数、渐进披露、错误解释、文档同源和支持入口降低复杂度，不能把云/K8s 复杂度换成门户表单复杂度。
13. 服务目录真实性：Catalog 必须能被 repo、CI、runtime、APM、云资源和 on-call 证据反查；只靠人工 yaml 或门户表单不算可信。
14. 执行面闭环：任何 self-service 按钮、模板或 API 都要能追踪到 workflow run、CI job、GitOps commit、IaC plan/apply、审计日志和最终资源状态。
15. 开发者平台门禁：平台能力进入生产默认要过 identity、RBAC、tenant、quota、environment、credential、policy、SLO、cost、audit、rollback、migration 和 support gate。
16. 真实交付：不能只证明按钮可点或模板可生成；必须证明服务能创建、部署、观测、告警、回滚、升级、删除，并能被 owner 接手运营。

## 强制落地流程

1. 先定平台产品：目标用户、要卖给内部团队的能力、非目标、成功指标、支持边界和 owner。
2. 再读事实：服务目录、仓库、CI/CD、GitOps、IaC、runtime、权限、工单、事故、成本和绕行路径。
3. 再画旅程：从创建服务到上线、观测、故障、扩容、回滚、升级、删除，每一步标入口、等待、失败点和证据。
4. 再定控制面：Portal/CLI/API 只做入口，真实状态以 workflow/GitOps/IaC/runtime 的单一事实源为准。
5. 再定权限链：identity、team、tenant、role、approval、runner token、cloud IAM、K8s RBAC、Secret、artifact、logs 必须一致。
6. 再定 guardrails：allow/warn/block/exception、例外 owner、到期、审计、自动修复和用户可理解解释。
7. 再定验证：端到端走一条 Golden Path，故意触发权限不足、配额不足、policy fail、runner fail、GitOps fail 和 rollback。
8. 再定门禁：生产准入、环境保护、凭证轮换、模板版本、配额、成本预算、SLO、审计、回滚、迁移和弃用必须有可执行 owner。
9. 最后定运营：adoption funnel、支持 SLO、office hour、release notes、迁移批次、弃用公告、回滚和复盘节奏。

## 场景执行卡

### 1. 平台现状评估与路线图
- 适用：从零建设 IDP、平台没人用、工具碎片化、交付慢、治理靠人工。
- 输入：用户访谈、工单、DORA/SPACE、onboarding 时间、服务创建步骤、发布频率、MTTR、owner/成本标签缺失率。
- 动作：画能力地图：Portal、catalog、templates、CI/CD、GitOps、IaC、K8s/cloud runtime、Secret、observability、安全、FinOps、文档、支持。
- 证据：top 3 摩擦点、北极星指标、MVP 范围、90 天路线图、迁移批次、风险与依赖。
- 兜底：没有访谈/指标基线时，只能给调研计划和假设，不能给工具采购结论。

### 2. IDP 分层架构
- 适用：设计 Internal Developer Platform、平台编排器、门户与执行面集成。
- 动作：分清体验层 Portal/Backstage、控制层 workflow、执行层 CI/CD/GitOps/IaC/cloud API、治理层 policy/scorecard/audit、数据层 catalog/metadata/events。
- 验证：状态单一事实源、幂等、重试、回滚、审计、最小权限、correlation id、失败可定位。
- 开发者平台门禁：每个 capability 要有 owner、API/CLI/UI 契约、权限矩阵、环境矩阵、quota、SLO、成本模型、审计事件、回滚路径和弃用策略。
- 自助边界：IDP 可以封装复杂度，但不能隐藏执行主体、审批原因、策略结果、资源状态、费用归属和失败补偿。
- 高频坑：Portal 直接用平台管理员权限调云 API，绕过策略、审计、GitOps 和回滚。

### 3. Developer Experience 诊断
- 适用：开发者抱怨平台难用、认知负担高、支持工单多、团队绕平台。
- 动作：拆 onboarding、inner loop、review、deploy、observe、operate、incident、cleanup；结合指标和访谈。
- 证据：首次服务创建/部署时间、文档查找时间、失败率、错误可理解度、满意度、支持响应时间。
- 认知负担：按 Team Topologies 交互模式看 X-as-a-Service、facilitating、collaboration 是否清晰，避免平台团队变隐形审批队列。
- 高频坑：只数按钮和自动化步骤，不看排障、文档、错误提示、等待时间和支持质量。

### 4. Golden Path / paved road 设计
- 适用：服务创建、API、批处理、前端、数据管道、模型服务、基础设施申请。
- 动作：定义适用边界、参数 schema、默认安全、测试、CI/CD 模板、Secret、观测、SLO、runbook、scorecard、成本、回滚、升级策略。
- 验证：端到端走通、生成物可测试、可升级、可注册 catalog、可回滚、可受控逃逸。
- 黄金路径验收：repo 生成后必须自动带 owner、tier、template_version、SLO、runbook、成本标签、环境配置、凭证引用、告警路由、回滚命令和迁移说明。
- 生产准入：至少验证 build、test、scan、SBOM、artifact signing、deploy、config diff、secret reference、health check、smoke、observe、rollback 和 cleanup。
- 逃生口：Golden Path 要有默认路径、例外路径、采纳指标和弃用策略；禁止变成不可逃逸的 Golden Cage。
- 高频坑：只生成 repo，不生成运行时、观测、告警、runbook、生产准入和迁移路径。

### 5. Backstage / Developer Portal
- 适用：开发者门户、Service Catalog、Software Templates、TechDocs、插件集成。
- 动作：确认 auth、permission framework、catalog provider、entity model、scaffolder actions、TechDocs 存储、插件维护状态。
- 验证：catalog-info owner/system/lifecycle/type/API/resource/dependency 完整，scaffolder 权限可审计，TechDocs 与 repo 同源。
- 平台 API：核心能力应有受控 API/CLI 或 workflow 接口，门户只是入口；避免业务关键路径绑定单一 UI 插件。
- 真实性：抽样 5-10 个服务，用 repo、runtime、APM、cloud resource、on-call、incident、cost tag 反查 catalog 字段。
- 权限：Backstage permission、scaffolder action、backend plugin、token、runner 和云 IAM 要做同一用户的越权验证。
- 高频坑：把 Backstage 当万能 workflow 引擎，在模板里塞长时间高权限且不可回滚的动作。

### 6. Service Catalog 治理
- 适用：owner 不清、依赖不明、资产重复、故障找不到人、scorecard 不可信。
- 动作：定义 entity 标准：owner、system、component、API、resource、dependency、lifecycle、tier、SLO、on-call、repo、runtime、data classification。
- 验证：从 repo、CI、K8s/APM、云资源自动同步；owner 必填；orphan entity 和 drift 检测。
- 数据质量：catalog 是数据产品；要有同步源、冲突处理、owner 确认、误报处理和漂移趋势。
- 高频坑：人工注册目录后无人 reconcile，三个月后与真实环境漂移。

### 7. Self-service 工作流
- 适用：自助创建服务、环境、数据库、队列、域名、发布版本、preview env。
- 动作：按风险定义 allow/warn/block/exception；设计状态、幂等、日志、重试、回滚、审批、通知、TTL、清理、成本标签。
- 验证：低风险自动完成，中风险策略校验，高风险审批；每一步有审计、失败恢复和用户可理解错误。
- 生命周期：创建、更新、删除、延期、过期回收、权限变更和失败补偿都要可见可审计。
- 审批边界：审批只用于高风险、跨租户、生产、成本超额或合规例外；常规路径应靠策略和配额自动化，不把平台变成工单前端。
- 证据链：输出 request id、actor、tenant、policy result、approval id、execution id、resource id、rollback id 和 audit event。
- 环境/凭证：自助流程必须区分 dev/staging/prod、preview/prod quota、secret scope、runner identity、cloud IAM、K8s service account、凭证轮换和撤销路径。
- 高频坑：只做创建，不做更新、删除、过期回收、成本归属和失败补偿。

### 8. Templates 与 CI/CD 模板治理
- 适用：服务模板、CI/CD 模板、IaC 模块、运行时配置、组织基线升级。
- 动作：锁语言/框架版本、参数 schema、默认测试/lint/SCA/SBOM、Dockerfile、健康检查、OpenTelemetry、readiness、runbook。
- 验证：模板版本化、自动测试、生成后验证、批量升级、弃用计划、catalog 自动注册、漂移检测。
- 漂移治理：记录模板版本、生成时间、继承基线、豁免项；用 scorecard 或批量 PR 追踪旧版本服务升级。
- 版本门禁：模板、CI reusable workflow、IaC module、base image、OTel SDK、policy bundle、runtime chart 都要有版本、兼容矩阵、升级路径和撤回策略。
- AI 生成：LLM 生成脚手架必须有锁文件、测试、SBOM、扫描、owner 和生成后验证，禁止批量制造供应链风险。
- 高频坑：模板生成即遗留，无法批量升级安全、可观测、CI/CD 和依赖基线。

### 9. Scorecard 与质量门禁
- 适用：生产准入、服务健康度、治理推动、持续改进。
- 动作：按 tier 定 ownership、SLO、漏洞、依赖 freshness、runtime support、backup、runbook、成本标签、incident readiness。
- 验证：数据源自动采集，红项有修复路径，例外有 owner/到期日，趋势能追踪。
- 赋能：scorecard 要提供自动修复入口、批量 PR、文档、owner 和例外流程；禁止只排名。
- 高频坑：scorecard 只排名羞辱团队，不提供修复指引、例外机制和自动修复入口。

### 10. Guardrails 与合规内建
- 适用：安全、合规、成本和审计要求平台化。
- 动作：把策略放进 templates、CI、IaC plan、admission control、runtime policy、scorecard；区分 allow/warn/block/exception。
- 验证：审计证据、例外流程、修复链接、自动修复、告警路由、例外到期清理。
- 策略即代码：最小权限、密钥治理、供应链基线、审计留痕、配额/隔离和成本归属默认内建。
- 高频坑：平台为了自助绕过安全，最后又退回人工审批和线下例外。

### 11. Multi-tenant / RBAC 平台治理
- 适用：多团队共享门户、K8s、云账号、runner、日志、制品库、FinOps 数据。
- 动作：设计 identity、RBAC/ABAC、namespace/account/project、quota、network、secret、runner、artifact、observability data、cost、audit 隔离。
- 验证：越权测试、noisy neighbor、配额、成本归属、日志可见性、应急隔离、break-glass 审计。
- 权限链：Portal 权限、API、runner token、K8s RoleBinding、云 IAM、Secret、日志索引和制品发布权限必须一致。
- 租户模型：先明确 team、product、environment、account/project、namespace、repo、cost center 和 data classification 的映射，禁止临时拼权限。
- 执行身份：区分人、服务账号、runner、workflow、GitOps controller 和 break-glass；每类身份都有最小权限、轮换、审计和吊销路径。
- 配额模型：按 tenant/environment/resource type 定 CPU、内存、存储、runner minutes、日志量、egress、预算和例外上限；配额不足要返回可申请路径。
- 审计模型：越权、提权、审批、break-glass、凭证轮换、跨租户访问、quota exception 和 policy override 都必须有不可抵赖日志。
- 高频坑：只做 UI 权限，底层 token、runner、Secret、日志索引和制品发布权限共享。

### 12. 平台运营与采用率
- 适用：平台建成但没人用、旧路绕行、迁移阻力大、认知负担上升。
- 动作：建立 adoption funnel、office hour、champion、迁移工具、release notes、弃用期限、支持 SLO、反馈闭环。
- 验证：采用率、失败率、支持工单下降、满意度、旧路收口、成本趋势、异常绕行原因。
- 产品化：平台要有 roadmap、需求入口、支持模型、版本发布、兼容策略、弃用公告和升级迁移节奏。
- 高频坑：用强制门禁替代产品运营，导致团队复制旧脚本绕平台。

### 13. 平台 SLO / 运营可靠性
- 适用：门户、CI 模板、workflow、GitOps、catalog、runner 成为关键路径。
- 动作：定义平台 SLI/SLO、错误预算、告警、事件响应、降级路径、容量和变更窗口。
- 验证：平台故障能关联受影响团队/服务，支持工单有响应目标，核心自助路径有成功率和延迟指标。
- 高频坑：平台成为全组织关键依赖后，没有 SLO、容量计划、降级和事故流程。

### 14. FinOps / 成本内建
- 适用：preview env、DB、队列、日志、runner、云资源自助创建后成本失控。
- 动作：默认写入 owner、purpose、cost center、TTL、quota、budget alert；把成本反馈嵌入申请、续期、销毁和 scorecard。
- 验证：标签覆盖率、闲置资源回收率、预算告警命中、团队成本趋势和例外到期清理。
- 高频坑：只展示账单，不把成本治理嵌入资源生命周期。

### 15. 证据闭环与审计日志
- 适用：平台改动已上线但无法证明谁触发、执行到哪、资源是否真实创建、失败原因是什么。
- 动作：统一 request id/correlation id；串起 portal、API、workflow、CI、IaC、GitOps、cloud/K8s、observability、ticket 和 audit。
- 验证：随机抽一条成功和一条失败流程，从用户请求追到资源状态、日志、成本标签、告警和回滚入口。
- 高频坑：只有门户操作日志，没有执行面日志、策略结果、资源 id 和失败分类。

### 16. 开发者平台门禁与真实交付验收
- 适用：平台能力、Golden Path、模板、自助流程、权限模型或迁移批次准备对开发者开放。
- 门禁：identity/RBAC、tenant isolation、quota/budget、environment protection、credential scope、policy result、SLO、audit、rollback、support owner、migration plan 全部有证据。
- 验收：用普通开发者身份从空白服务走到生产候选版本，再走一次失败和回滚；记录 request id、repo、artifact、deployment、catalog entity、alert、runbook 和 cost tag。
- 回滚：能力回滚、模板回滚、服务回滚、权限回滚、迁移回退和旧路临时恢复要分别定义触发条件、执行人、时间窗和验证点。
- 迁移：每批次明确 owner、目标版本、旧路依赖、兼容期、批量 PR/脚本、沟通渠道、例外到期、成功指标和停止条件。
- 真实交付：验收报告必须包含可复现入口、执行记录、资源状态、审计日志、SLO/成本影响、用户接手说明和未关闭风险。
- 高频坑：只用平台团队管理员账号演示 happy path，没有普通用户、失败路径、生产门禁、回滚和迁移证据。

### 17. 迁移、弃用与旧路收口
- 适用：从旧脚本、手工流程、老 CI 模板、旧 runtime 或旧门户迁移到平台。
- 动作：分服务 tier 和团队批次；提供兼容期、迁移工具、批量 PR、试点团队、回滚窗口、例外清单和弃用公告。
- 验证：旧路调用量下降、迁移成功率、失败原因、支持工单、回滚次数、未迁移 owner 和例外到期。
- 高频坑：只发通知关旧路，没有工具、支持、指标和回滚，导致团队复制脚本绕开平台。

## 高频坑 / 防遗漏

- 做 IDP：同步查 Portal、orchestrator、CI/CD、GitOps、IaC、runtime、policy、catalog、observability、FinOps、support。
- 做 Golden Path：同步查 repo、template、pipeline、deploy、secret、config、SLO、runbook、scorecard、rollback、升级。
- 做 Backstage：同步查 auth、permission、catalog provider、entity schema、scaffolder action、TechDocs、插件维护。
- 做 Catalog：同步查 owner、system、lifecycle、tier、dependency、SLO、on-call、runtime、data classification、drift。
- 做 Self-service：同步查 RBAC、审批、策略、幂等、状态、日志、回滚、通知、TTL、清理、成本标签。
- 做 CI/CD 模板：同步查 runner 权限、缓存、制品签名、SBOM、环境保护、回滚、模板版本漂移。
- 做 Scorecard：同步查数据源、自动采集、tier 差异、修复链接、例外、趋势、误报处理。
- 做 Multi-tenant：同步查 identity、quota、network、secret、runner、artifact、observability、cost、audit。
- 做平台运营：同步查 adoption、满意度、支持 SLO、roadmap、迁移工具、弃用策略、认知负担。
- 做平台 API：同步查 authn/authz、审计、幂等、限流、错误分类、版本兼容和 UI/CLI/API 一致性。
- 做迁移治理：同步查旧路依赖、兼容期、批量迁移工具、弃用公告、回滚路径和例外清单。
- 做证据闭环：同步查 request id、actor、tenant、policy、workflow、resource、audit、rollback、ticket。
- 做审批边界：同步查风险分级、自动策略、审批 owner、SLA、例外到期、审计和绕行指标。

## 输出要求

平台工程任务输出必须包含：
1. 平台目标：要解决的 Developer Experience、交付、治理、合规、成本或可靠性问题。
2. 用户与能力：目标用户、平台产品、能力边界、入口、执行面和不负责事项。
3. 版本/环境：Portal/Backstage、CI/CD、GitOps、IaC、runtime、policy、catalog schema、身份和租户模型。
4. 入口与复现：用户旅程、触发入口、失败步骤、错误提示、correlation id、工单/指标证据。
5. 现状证据：服务目录、工具链、交付链路、治理缺口、指标基线、成本/owner 覆盖。
6. 推荐方案：IDP 分层架构、Golden Path、Service Catalog、templates、self-service、guardrails、scorecard。
7. Multi-tenant：身份、RBAC、隔离、配额、成本、审计和应急隔离。
8. 度量：adoption、onboarding time、lead time、change failure rate、MTTR、工单量、满意度、DORA/SPACE、scorecard 趋势。
9. 落地计划：MVP、90 天路线图、迁移批次、风险、依赖、回滚、弃用和支持模型。
10. 未确认点：组织权限、云账号、合规要求、运行时版本、owner、平台 SLO、支持模型。
11. 证据闭环：request/correlation id、执行记录、审计日志、资源状态、策略结果、例外到期和回滚证据。

## 约束

- 禁止把平台工程简化为安装 Backstage、门户链接集合或 CI 模板仓库。
- 禁止没有用户旅程和指标基线就规划大而全平台。
- 禁止把 Golden Path 做成不可逃逸的 Golden Cage；例外必须可见、可审计、有到期。
- 禁止 self-service 绕过安全、合规、成本、审计、回滚和清理。
- 禁止只靠文档治理；guardrails 必须进入自动化执行点。
- 禁止 templates 硬编码组织密钥、个人权限、环境 ID 或不可迁移路径。
- 禁止平台抽象吞掉底层错误；错误要追踪到 workflow、CI、IaC、GitOps、runtime、cloud API。
- 禁止 scorecard 只排名不赋能；失败项必须有 owner、修复路径和例外机制。
- 禁止多租户共享高权限凭证、未隔离 runner、敏感日志索引或制品发布权限。
- 禁止把 FinOps 只做账单展示；必须落到标签、quota、TTL、预算告警和回收。
- 禁止平台 API/CLI/UI 权限不一致；所有入口必须共享身份、审计、策略和错误模型。
- 禁止强推迁移无支持；弃用旧路前必须提供迁移工具、兼容期、回滚和例外流程。
- 禁止把审批当平台能力；没有风险分级、自动策略、SLA 和到期清理的审批只是新瓶装旧工单。
- 禁止 catalog、scorecard、owner、on-call、runbook 只写静态字段；必须有同步源、验证频率和漂移处理。
- 涉具体实现、测试和审计时，按边界联动对应技能。

## 高频 Bug 反例库

- 反例 1：Backstage = IDP
  - 错法：装门户和链接后宣布平台工程完成。
  - 对法：Portal 背后接 CI/CD、IaC、runtime、policy、observability、FinOps 和 audit。
  - 根因：把入口误认为能力，忽略执行面与治理闭环。
- 反例 2：Golden Path 只有脚手架
  - 错法：模板只生成目录、README 和示例代码。
  - 对法：覆盖构建、测试、部署、Secret、观测、SLO、runbook、scorecard 和回滚。
  - 根因：只优化创建瞬间，没有覆盖生产生命周期。
- 反例 3：Scorecard 羞辱团队
  - 错法：全公司统一排名，红项无修复链接。
  - 对法：按 tier 定规则，红项给自动修复、owner、例外流程和到期日。
  - 根因：把治理当考核，没有把平台当赋能产品。
- 反例 4：Self-service 无清理
  - 错法：自助创建 preview env/DB/队列，但没有 TTL、成本标签和销毁。
  - 对法：每个资源有 owner、purpose、cost center、TTL、审计和删除路径。
  - 根因：只设计 happy path，漏掉资源生命周期与 FinOps。
- 反例 5：多租户只做 namespace
  - 错法：namespace 分开但共享 cluster-admin token、runner、Secret、日志索引。
  - 对法：身份、RBAC、网络、Secret、runner、artifact、observability、cost 全链路隔离。
  - 根因：只看 Kubernetes 名称空间，没做端到端租户威胁模型。
- 反例 6：平台强推无采用
  - 错法：直接关停旧路要求迁移。
  - 对法：先让新路更快更稳，提供迁移工具、支持和期限，再逐步收口。
  - 根因：忽略开发者体验和认知负担，用行政命令替代产品运营。
- 反例 7：模板不可升级
  - 错法：服务生成后永远停在旧依赖、旧 CI 和旧可观测基线。
  - 对法：模板版本化，提供迁移脚本、弃用策略、批量 PR 和 scorecard 追踪。
  - 根因：把模板当一次性脚手架，没有设计模板漂移治理。
- 反例 8：Portal 高权限直连云 API
  - 错法：用户点击按钮即用平台管理员权限创建资源，无审计和回滚。
  - 对法：通过受控 workflow、策略、最小权限、GitOps/IaC 变更和环境审批执行。
  - 根因：追求低摩擦时绕过 guardrails 和职责分离。
- 反例 9：Catalog 全靠人工维护
  - 错法：手填 owner 和依赖，运行时变化后目录失真。
  - 对法：repo、CI、APM、K8s、云资源自动 reconcile，orphan entity 自动标红。
  - 根因：没有把 catalog 当数据产品维护，缺少同步源和漂移检测。
- 反例 10：平台抽象遮蔽错误
  - 错法：用户只看到“创建失败”，不知道是 IAM、quota、policy 还是 GitOps。
  - 对法：错误带 correlation id，能追到 workflow、CI、IaC、GitOps 和 cloud API。
  - 根因：抽象层只包装成功路径，缺少可观测性和错误分类。
- 反例 11：RBAC 只做门户菜单
  - 错法：Portal 隐藏按钮，但 API、runner、K8s RoleBinding 和云 IAM 仍可越权。
  - 对法：统一身份映射，端到端权限校验，定期做越权测试和审计。
  - 根因：权限模型停在 UI 层，没有覆盖执行面凭证链。
- 反例 12：FinOps 只展示账单
  - 错法：门户展示团队成本图，但资源没有标签、quota、预算告警和回收。
  - 对法：self-service 默认写入成本标签，配 quota/TTL/预算告警，scorecard 暴露浪费项。
  - 根因：把成本治理当报表，没有嵌入资源申请和生命周期。
- 反例 13：平台没有 SLO
  - 错法：门户、runner、GitOps 成为关键路径后仍无可用性和支持目标。
  - 对法：定义平台 SLO、错误预算、告警、降级、容量和事件响应。
  - 根因：把平台当内部工具，没有按生产依赖运营。
- 反例 14：认知负担转移
  - 错法：把云控制台复杂度搬进几十个门户表单字段。
  - 对法：默认值、分层参数、渐进披露、示例和错误解释优先。
  - 根因：只做抽象封装，没有设计开发者体验。
- 反例 15：审批平台化
  - 错法：所有资源申请都进门户审批，平台团队手工点通过。
  - 对法：低风险自动化，高风险审批，例外有 owner、SLA、到期和审计。
  - 根因：把 self-service 做成工单皮肤，没有风险分级和策略执行。
- 反例 16：Owner 字段失真
  - 错法：catalog 写了 owner，但 on-call、repo 权限、成本标签和事故处理人都不同。
  - 对法：owner 与 repo、runtime、pager、cost、incident 自动 reconcile。
  - 根因：服务目录没有真实性校验，只追求字段完整。
- 反例 17：执行面不可追
  - 错法：门户显示“部署成功”，但找不到对应 CI job、GitOps commit、资源版本和审计事件。
  - 对法：全链路 correlation id，成功失败都能追到执行面和回滚入口。
  - 根因：只设计前台体验，没有设计证据闭环。
- 反例 18：旧路无限兼容
  - 错法：新平台上线后旧脚本、旧模板、旧账号长期并行。
  - 对法：分批迁移、监控旧路调用、公告弃用、提供工具和例外到期。
  - 根因：平台产品运营缺失，迁移没有 owner 和收口指标。

## 提交前自检清单

- [ ] 行数 <= 500，且无 fenced code block。
- [ ] 已覆盖用户、平台产品、能力、入口、证据。
- [ ] 已覆盖版本、环境、复现、服务目录事实和指标基线。
- [ ] 已区分 IDP、Portal、Backstage、PaaS、CI/CD、GitOps、IaC、runtime 和 cloud console。
- [ ] 已覆盖 Developer Experience、Golden Path、Service Catalog、self-service、templates、scorecard、guardrails。
- [ ] 已覆盖 RBAC、multi-tenant、Kubernetes 平台、平台产品化、FinOps、SLO、模板漂移和认知负担。
- [ ] 已覆盖 request id、执行面、审计日志、资源状态、回滚证据和本地/远端一致性。
- [ ] 已覆盖 owner、on-call、runbook、support SLO、office hour、release notes、迁移和弃用策略。
- [ ] 已列反例不少于 10 条，且每条有错法/对法/根因。
- [ ] 已说明输出要求、约束、2024-2026 新坑和相邻技能边界。
- [ ] 已标明 K8s/安全/发布/观测/后端/测试/审计需联动技能。

## 2024-2026 新坑速查

- AI 模板膨胀：LLM 生成脚手架若无测试、锁文件、SBOM 和扫描，会批量制造供应链风险。
- Portal 工具泛滥：Backstage、Port、Cortex、OpsLevel、自研门户选型要回到数据模型、权限、插件维护和执行面集成。
- 平台编排器边界不清：workflow、GitOps、IaC、CI/CD 状态双写会形成漂移，必须定义单一事实源。
- Golden Path 变 Golden Cage：治理压力容易把推荐路径变强制唯一道路，需保留受控例外。
- Scorecard 数据质量：catalog drift 会误判服务健康，需自动同步、owner 确认和误报处理。
- 平台成本黑洞：preview env、DB、队列、日志索引、runner 自助创建后必须有 TTL、quota、FinOps 标签。
- 多云多租户权限漂移：云 IAM、K8s RBAC、Portal 权限、CI token 不一致会越权。
- 开发者体验局部优化：只优化创建服务，不优化 inner loop、调试、故障定位和升级，会让平台被绕开。
- 合规左移变阻塞：policy 只有 block 没解释和自动修复会制造绕平台行为。
- Backstage 插件风险：插件维护、权限模型和内部 API 变化会让关键路径脆弱，核心 action 要有测试和回滚。
- 平台 SLO 缺失：门户、CI、模板、GitOps 成为关键路径后，没有 SLO 会放大全组织停摆。
- 模板漂移放大：语言版本、CI runner、基础镜像、OTel SDK 和安全扫描基线不同步，会批量形成隐性遗留。
- 认知负担转移：平台把云/K8s 复杂度换成门户表单复杂度，需默认值、分层参数和渐进披露。
- 平台 API 缺失：只有门户 UI 没有稳定 API/CLI，自动化、审计、回放和故障恢复都会脆弱。
- 支持模型缺失：平台团队只交付能力不运营支持，工单、office hour、champion、release notes 和弃用沟通断裂。
- 审批队列复辟：自助平台若没有自动策略和低风险直通，会退化成更漂亮的人工审批系统。
- 执行证据断裂：门户、workflow、CI、GitOps、IaC、cloud/K8s 各自有状态但缺 correlation id，失败复盘会失真。
- Catalog 合规幻觉：owner、tier、SLO、runbook 字段全绿，但没有 runtime 和 on-call 反查，事故时仍找不到责任人。

## 与相邻技能的边界

- 本技能负责：平台工程方法、IDP 抽象、DevEx、Golden Path、Service Catalog、self-service、scorecard、guardrails、RBAC/multi-tenant、平台运营和度量。
- 云原生 / cloud-native（cld）：负责 Kubernetes/GitOps 控制器、集群能力、运行时 YAML/Helm/Kustomize 细节；本技能只定义平台抽象与边界。
- IaC / Terraform / terraform-iac（itf）：负责 Terraform/OpenTofu 模块、状态、plan/apply 和 provider 细节；本技能只定义自助入口、策略和生命周期。
- DevSecOps / devsecops（dso）：负责供应链、安全扫描、策略规则和漏洞治理细节；本技能只定义 guardrails 落点和例外机制。
- 可观测性 / observability（obs）：负责指标、日志、链路、告警、SLO 实现和事故流程；本技能只要求 Golden Path 默认接入和证据闭环。
- 发布部署 / release-engineering（rls）：负责发布策略、流水线、制品、回滚和上线窗口；本技能只管 CI/CD 模板体验与治理要求。
- FinOps 云成本 / finops（fop）：负责成本模型、预算、分摊和优化；本技能只确保标签、quota、TTL、成本反馈进入 self-service。
- 后端工程 / backend-engineering（be）：负责应用架构、API、代码和运行时行为；本技能只定义服务模板与平台契约。
- 测试验证 / test-engineering（tst）：负责测试矩阵、回归、质量门禁验证；平台改动涉及模板/工作流/权限时必须联动。
- 代码审计 / code-audit（aud）：负责最终审计改动影响面、风险和遗漏；远端技能更新完成前必须收口。