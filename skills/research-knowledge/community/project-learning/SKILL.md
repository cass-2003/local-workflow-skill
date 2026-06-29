---
name: project-learning
description: 项目学习实战排障版 - 面向陌生项目、陌生模块和修 Bug 前上下文补齐，建立入口识别、调用链、数据流、配置/路由/权限/测试基线、monorepo 依赖边界、架构漂移、AI 生成代码痕迹和证据索引的只读心智模型。当需要学习项目、接手模块、理解功能链路、定位影响面或先补证据再改代码时必须使用。
---

# 项目学习

项目学习（project-learning，兼容 slug: pl）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

> 定位：project-learning 只负责把陌生项目从“看过一些文件”收敛为可复核证据地图：范围、入口、调用链、数据流、配置、路由、测试基线、依赖边界、风险和未知项。
> 铁律：学习阶段默认只读；未找到真实入口、producer/consumer、配置来源、测试入口、impact map 和证据索引前，不宣称已理解影响面。

## 快速总则

1. 先定目标：全项目上手、单功能理解、修 Bug 前补上下文、影响面评估、架构漂移识别、测试基线确认或风险边界建立。
2. 先定范围：仓库、服务、端、模块、分支、环境、版本、部署形态、用户路径、入口类型和明确不覆盖范围。
3. 先找真实入口：entrypoint 包含启动命令、路由/API、页面、CLI、定时任务、队列消费者、事件订阅、配置加载、测试入口和部署入口。
4. 先建证据索引：每条结论绑定 file:line、命令输出、路由、配置 key、表/字段、队列 topic、测试名、日志字段或外部依赖名。
5. 先分级证据：运行事实/部署配置/CI 与脚本/代码引用/测试结果优先于 README、注释、旧文档和 AI 摘要；文档只能作线索。
6. 证据冲突先停：输出冲突表、假设和下一步采证，不用低可信证据覆盖高可信证据，不把假设写成结论。
7. 先追 producer 再追 consumer：函数、字段、枚举、配置、事件、缓存 key、DB 表、文件、SDK 和导出物都要看写入方、读取方、序列化和测试断言。
8. 影响面必须矩阵化：改函数、字段、枚举、路由、权限、配置 key、feature flag、cache、queue、topic、SDK 或公开契约前查引用和消费方。
9. 大项目允许分层抽样，但入口、认证、permission、写路径、state machine、configuration、测试和公共中间件不能跳。
10. 学习输出只给证据地图、风险和下一步技能；不替代语言技能、api、db、tst 或 aud 写实现。
11. 证据不足就停：生成代码源头不可见、私有依赖缺失、环境不可复现、路由不可达、资料冲突或影响面不明时，输出“需补证据”。
12. 未读不结论：未读到真实文件、命令输出、路由注册、配置来源、DB 访问点、测试入口或部署入口，不写“已确认”“就是这里”“没有影响”。
13. 只读边界优先：学习任务不得写盘、改代码、改配置、迁移 DB、启动外部可见发布或调用有副作用接口；需要副作用时先切实现/发布/DB/测试技能并确认。

## 只读门禁与切换条件

- 允许动作：列目录、读文件、搜索引用、查看 git history、读本地配置、读测试定义、读 CI/部署脚本、运行纯只读诊断命令和无副作用的本地测试发现命令。
- 谨慎动作：启动服务、连接远端环境、访问生产 API、读取真实用户数据、运行集成测试、抓日志、读数据库；必须先说明目标、环境、权限、数据范围和是否有副作用。
- 禁止动作：修改代码/配置/依赖/锁文件/数据库/远端规则，写入缓存或队列，触发邮件/短信/支付/发布/重启/回滚，删除文件或修复数据。
- 切实现条件：用户明确要求改、修、加、实现、重构、运行、调试、部署、迁移、写测试或审计；且学习阶段已给出入口、影响面、验证点和回滚点。
- 切相邻技能：API 契约或接口实现切 api；DB schema、SQL、迁移或数据修复切 db；测试策略和自动化切 tst；发布、CI/CD、回滚切 rls；安全验证切 wsec/aud；外部资料切 rsch。
- 停止条件：连续两轮定位无新增证据、关键入口不可达、私有依赖缺失、生产权限不足、资料冲突未解或用户目标改变；输出缺口和最小下一步，不继续猜。

## 证据分级与冲突处置

- 一级证据：实际启动/构建/测试命令输出、运行日志、trace、部署入口、路由注册、scheduler/worker 注册、网关/反代/容器进程和现行 CI job。
- 二级证据：代码定义与引用、package/workspace graph、DI/container 绑定、配置加载链、schema 源、迁移、测试断言和 fixtures。
- 三级证据：README、注释、目录名、旧设计文档、历史 issue、AI 摘要、demo/mock/legacy 代码；只能作为搜索线索。
- 冲突处理：列“结论候选、冲突证据、可信度、缺口、下一步采证”；冲突未解前不得宣称真实入口、主链路或可改源头。
- 采样规则：大仓库可先抽主入口和代表模块，但公共中间件、权限、配置、生成代码、状态机、异步副作用、测试入口和发布入口必须补齐。

## 陌生项目入口收敛算法

1. 根配置：先看仓库说明、CLAUDE/AGENTS、manifest、package/build、lockfile、workspace、Makefile、justfile、脚本和 CI。
2. 依赖边界：识别 monorepo/workspace graph、package exports、内部包版本、私有 registry、生成目录和构建产物。
3. 启动部署：追 Dockerfile、compose、Kubernetes/Helm/Kustomize、systemd、serverless/edge config、进程管理、健康检查和回滚入口。
4. 用户入口：从 route registry、API/controller/page/router、CLI command、job scheduler、cron、queue/topic、event subscriber、webhook、worker 找可达入口。
5. 框架装配：追 DI/container、middleware、auth、permission、配置加载、feature flag、插件注册和公共错误处理。
6. 数据副作用：追 service/usecase、repository/store、DB/cache/queue/file、外部 API、通知、审计日志、埋点和补偿任务。
7. 验证入口：同步找 test entry、CI job、fixture/mock、最小冒烟、原 bug 红灯、日志/指标/trace 和手工验证路径。
8. 收敛条件：入口可达、producer/consumer 成对、configuration/environment 来源明确、测试与观测入口明确、未知项可列出。

## 召回地图

- 目录与依赖：根目录、子项目、workspace、package manager、lockfile、构建脚本、内部包、私有 registry、generated code、schema 源和不可直接改的产物。
- 入口：启动命令、main/app lifecycle、router、controller、page、CLI、cron、scheduler、worker、queue/topic、event subscriber、webhook、plugin、extension 和测试入口。
- 业务流：用户动作、角色、资源、状态机、审批/支付/通知/导入导出/报表、同步/异步分界、失败补偿、幂等和重试。
- API：route registry、OpenAPI/Swagger、controller、middleware、DTO/schema、错误码、分页、幂等键、SDK、前端调用方和第三方 consumer。
- DB 与数据流：migration、schema、repository/DAO、ORM model、SQL、事务、索引、读写分离、cache key、queue payload、文件存储和数据导出。
- 部署与环境：Docker、compose、Kubernetes、Helm values、systemd、serverless/edge、CI job、环境变量、secret、feature flag、灰度、健康检查和回滚入口。
- 测试与质量：unit、integration、contract、E2E、fixture、mock、testcontainers、CI matrix、跳过/flaky、覆盖口径、原 bug 红灯和最小冒烟。
- 权限与风险：auth、permission、tenant、owner、scope、可信 header、Webhook 签名、审计日志、BOLA/IDOR、CSRF/SSRF、敏感日志、密钥、供应链和策略控制面。
- 证据链：每个召回对象必须落到至少一个 file:line、命令输出、路由、配置 key、表/字段、队列 topic、测试名、日志字段或外部依赖名。

## Impact map 标准矩阵

- 范围：仓库、服务、端、模块、分支、environment、版本、用户路径、不覆盖范围。
- 入口：启动、路由/API、页面、CLI、任务、事件、queue/topic、配置、部署、test entry。
- 调用链：handler/page/command、service/usecase、repository/store、外部依赖、错误传播、异步副作用。
- 数据契约：字段、枚举、state machine、DB、cache、queue、文件、SDK、导入导出、序列化/反序列化。
- producer/consumer：写入方、读取方、校验方、展示方、报表/导出方、Mock/fixture、测试断言。
- 权限安全：auth、permission、租户、owner、scope、批量操作、可信 header、Webhook 签名、审计日志。
- 配置发布：configuration、默认值、覆盖优先级、secret、feature flag、灰度、部署目标、回滚点。
- 依赖边界：monorepo/workspace、package exports、generated code 源头、schema、lockfile、私有包、构建产物。
- 验证观测：红绿基线、现有测试、最小冒烟、flaky/跳过测试、logs/metrics/traces、runbook。
- 外部消费者：前端、移动端、SDK、报表、运营后台、第三方 API、Webhook、数据管道。
- 未知与阻塞：证据缺口、环境差异、私有依赖、不可复现、资料冲突、需相邻技能处理项。

## 场景执行卡

### 1. 新项目快速读图

- 输入：仓库路径、目标服务/端、业务目标、运行环境、当前分支、已有文档和用户要解决的问题。
- 动作：读根配置、包管理/构建、启动脚本、CI、部署配置、workspace graph、目录结构和测试目录；画模块职责与入口地图。
- 必查：entrypoint、依赖图、monorepo/workspace、environment、configuration、外部服务、DB/cache/queue、generated code、测试命令。
- 输出：项目地图、关键入口、运行/测试方式、impact map、主要风险、未知项和需要切换的相邻技能。

### 2. 功能链路理解

- 输入：用户动作、URL/API/页面、命令、事件、报错、关键词或需求点。
- 动作：从用户入口追到 handler/controller/page、service/usecase、repository/store、DB/cache/queue/file、外部 API、返回结构和副作用。
- 必查：call graph、data flow、auth、permission、state machine、事务、幂等、错误处理、日志/埋点、测试覆盖和旧入口。
- 输出：调用链、数据流、状态流、producer/consumer 矩阵、验证入口和影响面。

### 3. 修 Bug 前补上下文

- 输入：bug 描述、复现步骤、日志/堆栈、环境、版本、账号/角色、数据样本、最近变更。
- 动作：定位失败点和真实入口；查同类实现、旧路径、配置差异、数据状态、cache、异步任务、权限链路和红绿基线。
- 必查：原 bug 可复现红灯、错误传播、消费方、历史兼容、并发/重试、feature flag、灰度和观测证据。
- 失败兜底：没有复现或证据不足时只列候选根因和缺口，不直接改。

### 4. 数据流 / 状态 / 字段 / 枚举映射

- 输入：字段、枚举、状态、cache key、topic、文件名、响应结构或数据库对象。
- 动作：全量搜索定义、写入、读取、校验、序列化、反序列化、迁移、前端展示、导入导出、报表、任务和测试断言。
- 必查：默认值、null/empty、未知枚举、旧数据、权限过滤、缓存失效、队列重放、state machine 非法跳转。
- 输出：数据血缘、producer/consumer 表、兼容风险和要交给 api/db/tst 的验证点。

### 5. 配置 / 环境 / 路由 / 部署入口识别

- 输入：环境名、服务、配置 key、路由、域名、部署目标或启动失败现象。
- 动作：追 configuration 定义、默认值、覆盖优先级、secret 来源、运行用户、容器/进程入口、网关/反代、健康检查和回滚入口。
- 必查：dev/staging/prod 差异、feature flag、热加载/重启、CI 注入、Kubernetes/systemd/compose、serverless/edge、Nginx/CDN、证书和回调地址。
- 输出：配置链路、环境差异、真实路由入口、发布/回滚风险。

### 6. 认证 / 权限 / 安全边界学习

- 输入：用户角色、资源类型、入口、token/session 来源、管理端或 webhook。
- 动作：追 auth 来源、middleware、scope、租户、owner 校验、批量操作、服务间身份、审计日志和错误语义。
- 必查：BOLA/IDOR、跨租户、批量逐项验权、可信 header、CSRF/SSRF、文件路径、Webhook 签名和重放。
- 输出：权限链路、资源边界、明显缺口和需要 aud/wsec 的风险点。

### 7. 测试和质量基线学习

- 输入：目标功能、语言栈、CI、测试目录、历史失败、原 bug 路径。
- 动作：识别单测、集成、契约、E2E、冒烟、性能、安全、可观测性测试；查 fixtures、mock、testcontainers、CI job、跳过测试和覆盖率口径。
- 必查：原 bug 红灯、现有测试可运行性、最小冒烟、关键链路、旧入口、flaky、环境依赖、测试数据隔离和手工验证入口。
- 输出：红绿基线、最小验证地图和缺口；测试策略与执行交给 tst。

### 8. Monorepo / 依赖边界 / 生成代码

- 输入：workspace、包名、模块、SDK、schema、生成目录或构建失败。
- 动作：查 workspace graph、package exports、lockfile、构建产物、代码生成命令、schema 源、内部包版本和跨包消费方。
- 必查：Nx/Turborepo/Bazel/Gradle multi-project、pnpm workspace、OpenAPI/GraphQL/protobuf/ORM 生成、私有 registry、循环依赖、provenance。
- 输出：依赖边界、可改源头、不可直接改的生成物、构建/发布影响。

### 9. 架构漂移与 AI 生成代码痕迹识别

- 输入：新增模块、异常风格代码、重复实现、迁移中目录、AI 生成嫌疑或历史债务。
- 动作：对比近期模块、当前主路径、git history、分层、命名、错误处理、权限、日志、测试、配置和依赖方向。
- 必查：真实调用路径、框架约定、已废弃目录、生成/脚手架来源、lint/CI、CODEOWNERS、service catalog 和架构边界。
- 输出：架构漂移证据、AI 生成代码痕迹、不能照搬的差异、需切语言技能或 aud 的风险。

### 10. 现代平台 / LLM / 策略边界识别

- 输入：serverless/edge、RSC/SSR、IDP/service catalog、policy as code、LLM/tool/vector、供应链或观测平台线索。
- 动作：追平台模板、运行区域、冷启动、缓存边界、tool schema、prompt、vector store、model version、OPA/Kyverno/IAM、包签名和 dashboard/runbook。
- 必查：入口与回滚是否在代码外、远端 flag/secret 是否参与、日志是否脱敏、策略是否阻断发布、lockfile/provenance 是否影响构建。
- 输出：平台约定、外部控制面、观测/策略/供应链风险和需切相邻技能的证据。

## 高频坑 / 防遗漏

### 高频坑

1. 只看 README 或目录名，不看脚本、CI、部署和真实入口。
2. 只看搜索结果，不验证路由、构建、DI 或运行可达性，把 dead code 当主链路。
3. 只追入口文件，不追数据写入、异步副作用和消费方。
4. 只看后端，漏前端、移动端、SDK、报表、导出、任务和测试夹具。
5. 学习阶段顺手改代码，导致证据和假设混在一起。
6. 把 legacy/demo/mock/generated code/脚手架模板当线上链路。
7. 忽略 environment 差异和 feature flag，本地路径不等于生产路径。
8. 不查 auth、permission、租户和 owner，只看业务 service。
9. 不查 test entry 和红绿基线，最后无法证明理解可验证。
10. 漏 monorepo/workspace/package exports/版本提升，改一个包影响多个端或 SDK。
11. 直接修改 generated code，不找 schema、模板或生成命令。
12. AI 生成代码看似完整，实际 API、字段、异常、观测字段和权限分支不存在。
13. AI agent 新增测试全绿但只测 mock happy path，真实配置、权限、异步链路未覆盖。
14. 架构漂移未识别，迁移期复制旧模块，未结合近期 commit、CODEOWNERS、lint boundary 判断当前约定。
15. 只搜源码配置，漏 service catalog、Helm values、edge env、secret manager 和远端 flag。
16. 依赖边界未确认，跨层 import、循环依赖、私有包版本或 supply chain 规则污染构建。
17. 只建调用链不建证据索引，后续审计无法复核。

### 防遗漏清单

- 范围：仓库、服务、端、模块、分支、environment、版本、用户路径、不覆盖范围是否明确。
- 入口：启动、路由、页面、API、CLI、任务、事件、queue、configuration、测试和部署入口是否找到。
- 链路：call graph、data flow、producer、consumer、外部依赖、返回、副作用和错误传播是否追完。
- 数据：字段、枚举、state machine、DB、cache、queue、topic、文件、SDK、导入导出是否覆盖。
- 配置：configuration、environment、feature flag、secret、覆盖优先级、回滚方式是否识别。
- 权限：auth、permission、租户、owner、批量、可信边界、审计日志是否追到。
- 依赖：monorepo、workspace、lockfile、package exports、generated code、私有包和构建产物是否确认。
- 验证：test entry、CI job、fixture、mock、原 bug 红灯、现有测试可运行、最小冒烟和手工验证入口是否明确。
- 风险：架构漂移、AI 生成代码痕迹、废弃链路、环境差异、观测缺口、策略/供应链缺口和未知项是否列明。

## 输出要求

1. 学习目标与范围：项目、模块、环境、版本、用户路径、入口类型和不覆盖范围。
2. 证据索引：列已读文件/命令/路由/配置/表/测试/日志入口；每个关键结论能回到证据。
3. 证据冲突表：资料冲突时列候选结论、冲突证据、可信度、缺口和下一步采证；无冲突可写“未发现”。
4. 入口地图：启动、路由/API/页面/CLI/任务/事件/队列、配置、部署和测试入口。
5. 调用链：关键函数/文件、call graph、producer、consumer、外部依赖、异步副作用和旧入口。
6. 数据/状态链：data flow、字段、枚举、表、cache、queue、topic、state machine、权限、事务、错误处理和日志。
7. Impact map：调用方、数据契约、权限、配置、缓存/队列、测试、发布、外部消费者、回滚点和未知项。
8. 依赖与架构边界：monorepo/workspace、generated code 源头、包边界、公共层约定、架构漂移和 AI 生成代码痕迹。
9. 测试基线：原 bug 红灯、现有测试入口、可运行性、最小冒烟、缺失验证、flaky/跳过测试和需交给 tst 的场景。
10. 风险与未知：证据不足、环境差异、权限/安全、兼容、发布、观测、私有依赖、策略/供应链和需确认项。
11. 下一步技能：实现切对应语言/端；外部资料切 rsch；API 切 api；DB 切 db；验证切 tst；发布切 rls；最终收口切 aud。

## 真实学习报告验收

- 报告必须先写结论边界：本次只读、已覆盖范围、未覆盖范围、阻塞项和不做实现的原因。
- 至少给出 8 类证据中与任务相关的项：目录/依赖、入口、业务流、API、DB/数据流、部署/环境、测试、权限/风险；无相关项要写明“不涉及”或“未发现证据”。
- 关键链路必须有入口到副作用的闭环：用户入口、handler/page/command、service/usecase、repository/store、外部依赖、返回、日志/指标和测试入口。
- 每个高风险结论必须有证据等级和缺口；三级证据不得单独支撑“真实入口、线上路径、无影响、可直接改、已覆盖”。
- 学习报告不能只列文件树或摘要；必须包含证据索引、impact map、producer/consumer、验证入口、风险未知和下一步技能。
- 验收不过时要输出“不足以进入实现”的原因，不把学习报告包装成完成修复、完成测试或完成发布。

## 证据索引极简格式

- 结论：一句话，只写已证实内容。
- 证据：file:line / 命令输出 / 路由 / 配置 key / 表字段 / 测试名 / 日志字段。
- 可信度：一级、二级或三级；三级不得单独支撑关键结论。
- 影响：入口、producer、consumer、配置、权限、缓存/队列、测试、发布、外部消费者。
- 缺口：尚未读取、无法复现、权限不足、私有依赖缺失、环境不可达或资料冲突。
- 下一步：继续采证、切相邻技能、请求用户确认或停止。

## 约束

- 学习阶段只读；未获明确实现任务前不修改代码、配置、依赖、数据库或远端资源。
- 不凭 README、目录名、注释、训练记忆、旧文档、搜索摘要或 AI 摘要下结论。
- 未追 producer/consumer 和 impact map，不说“只影响这里”。
- 未识别 configuration、environment、feature flag 和部署差异，不说“本地等于线上”。
- 未确认 test entry、红绿基线和验证路径，不说“可验证/已覆盖”。
- 不把 legacy、demo、mock、generated code、脚手架模板当真实链路，除非证据证明可达。
- 不把 agentic coding 的批量同构提交、happy path 测试、伪观测字段、prompt/tool schema 当事实，必须用项目证据验证。
- 不替代语言技能写实现；不替代 api 定契约；不替代 db 设计 schema；不替代 tst 做测试；不替代 aud 下最终通过结论。
- 涉安全、DB 写、发布、外部资料、观测、性能、策略和供应链时，只输出触发原因和证据，切相邻技能继续。
- 证据不足时必须列阻塞项和下一步采证，禁止硬改。

## 高频 Bug 反例库

- 反例 1：README 当事实。
  - 错法：README 写 npm start，就认定生产入口也是它。
  - 对法：核 package、Dockerfile、CI、systemd/Kubernetes、部署变量和现网启动命令。
  - 根因：文档常滞后于真实运行链路。
- 反例 2：只追生产方。
  - 错法：看到字段写入就改名，没查前端、SDK、导出和测试。
  - 对法：全量搜 producer/consumer、序列化、Mock、报表、旧入口和断言。
  - 根因：数据契约会跨层传播。
- 反例 3：学习时顺手改。
  - 错法：边读边修，最后无法区分证据、假设和改动影响。
  - 对法：先输出证据地图和风险，进入实现阶段再切对应技能。
  - 根因：学习目标是建立心智模型，不是直接落代码。
- 反例 4：误认废弃链路。
  - 错法：按 old/legacy 目录里的 handler 定位当前业务。
  - 对法：验证路由注册、构建入口、引用、部署配置和流量入口。
  - 根因：仓库常保留历史残留和迁移中代码。
- 反例 5：漏权限链路。
  - 错法：只看 service 逻辑，没看 middleware、scope 和 owner 校验。
  - 对法：追 auth、permission、租户、资源归属、批量操作和审计日志。
  - 根因：权限通常分散在公共层和业务层。
- 反例 6：环境差异漏查。
  - 错法：本地 SQLite 通过就认为生产 MySQL/PostgreSQL 也安全。
  - 对法：查 prod configuration、DB 类型、迁移、驱动、feature flag 和部署事实。
  - 根因：环境差异会改变行为和风险。
- 反例 7：忽略异步副作用。
  - 错法：API 返回正常就认为链路完成。
  - 对法：追 queue、定时任务、回调、通知、cache、审计日志和补偿任务。
  - 根因：业务副作用常在异步链路。
- 反例 8：同名函数误导。
  - 错法：搜到同名 handler 就开始分析。
  - 对法：从真实路由、调用引用、构建入口和运行配置确认可达性。
  - 根因：同名代码不等于线上路径。
- 反例 9：测试入口不查。
  - 错法：理解完才发现没有环境、fixture 或命令可验证。
  - 对法：学习时同步识别 test entry、CI、mock、fixture、红绿基线和手测路径。
  - 根因：无法验证的理解不能支撑改动。
- 反例 10：monorepo 边界错。
  - 错法：只改当前 package，漏 workspace 依赖、exports、版本提升和构建产物。
  - 对法：查 workspace graph、lockfile、内部包版本、package exports、生成命令和消费者。
  - 根因：大型仓库影响面跨包传播。
- 反例 11：直接改生成代码。
  - 错法：在 generated SDK/ORM 文件里修字段。
  - 对法：找到 OpenAPI/GraphQL/protobuf/schema 源和生成命令，再评估消费者。
  - 根因：生成产物会被覆盖，源头契约才是事实。
- 反例 12：AI 生成代码未验事实。
  - 错法：接受 AI 写出的 API、字段、异常类、观测字段和权限判断。
  - 对法：用项目既有用法、官方资料或最小运行验证每个关键点。
  - 根因：AI 代码常语法正确但语义不存在。
- 反例 13：架构漂移未识别。
  - 错法：复制迁移前旧模块的分层和依赖方向到新功能。
  - 对法：比较当前主路径、近期模块、git history、CODEOWNERS、lint/CI 规则和架构约束。
  - 根因：项目约定会演进，旧模式可能已废弃。
- 反例 14：配置 key 只搜代码。
  - 错法：改默认值后不查 CI secret、Helm values、service catalog、edge env、secret manager 和远端 flag。
  - 对法：追配置定义、覆盖优先级、环境差异、重启/热加载、控制面和回滚版本。
  - 根因：实际配置值常在运行环境或平台控制面而不在源码。
- 反例 15：证据索引缺失。
  - 错法：输出“链路大概是 A 到 B”，没有 file:line 或命令证据。
  - 对法：每个结论绑定文件行、命令输出、路由、配置、测试或日志入口。
  - 根因：不可复核的学习结果无法支持审计和交接。
- 反例 16：只看搜索结果。
  - 错法：全文搜索命中 controller，就认定它是主路径。
  - 对法：验证 route registry、构建入口、DI/container 绑定、feature flag 和运行日志。
  - 根因：dead code、旧入口和同名实现常混在仓库中。
- 反例 17：AI agent 测试假绿。
  - 错法：看到新增测试全绿，就认为真实 bug 已覆盖。
  - 对法：检查 mock 是否绕过 auth/config/queue、是否只测 happy path、是否能让原 bug 复现红灯。
  - 根因：生成测试容易验证实现细节而非真实链路。
- 反例 18：平台控制面漏查。
  - 错法：只看仓库部署文件，不查 IDP、service catalog、policy as code 和观测配置。
  - 对法：确认模板、scorecard、OPA/Kyverno/IAM、dashboard、alert、runbook 和 release marker 位置。
  - 根因：现代平台把发布、权限和观测约定拆到代码仓库外。
- 反例 19：未读下结论。
  - 错法：没打开 controller、路由注册和测试就说“问题在 service”。
  - 对法：先列已读、未读和证据等级；未读关键点只写假设。
  - 根因：陌生项目里命名相似和历史残留很常见。
- 反例 20：学习报告像文件树。
  - 错法：只输出目录结构和每个目录一句话。
  - 对法：补入口地图、业务流、data flow、权限、部署、测试、impact map 和证据索引。
  - 根因：文件树不能证明真实链路可达。
- 反例 21：只读任务触发实现技能。
  - 错法：用户说学习项目，却读取后直接改代码或设计 schema。
  - 对法：只输出证据、风险和切换条件；等用户要求实现再切语言/API/DB/测试技能。
  - 根因：学习阶段目标是降低未知，不是交付改动。
- 反例 22：业务流断在 API。
  - 错法：看到接口返回结构就停止，不查状态机、通知、报表和异步任务。
  - 对法：从用户动作追到 DB/cache/queue/file、外部依赖、审计日志和消费者。
  - 根因：业务完成常发生在 API 返回之后。
- 反例 23：DB 只看表名。
  - 错法：看到表或 ORM model 就认定读写影响。
  - 对法：查 migration、索引、事务、repository、SQL、缓存、队列 payload、旧数据和测试 fixture。
  - 根因：数据行为由读写路径、约束和历史数据共同决定。
- 反例 24：风险召回不落证据。
  - 错法：泛泛写“注意安全和部署风险”。
  - 对法：绑定 auth/permission/tenant、secret、feature flag、CI、回滚、日志字段和测试入口证据。
  - 根因：不可定位的风险无法指导下一步技能和验证。

## 提交前自检清单

- [ ] frontmatter name 等于 canonical name（project-learning），旧 slug 只作兼容 alias/URL 主键。
- [ ] 行数 <= 500，fenced code block 数为 0，正文不出现三个反引号。
- [ ] 必需章节齐全：快速总则、证据分级与冲突处置、入口收敛算法、impact map、场景执行卡、高频坑 / 防遗漏、输出要求、证据索引格式、约束、高频 Bug 反例库、2024-2026 新坑速查、与相邻技能的边界。
- [ ] 反例不少于 12 条，且每条能被“反例 数字”命中，并包含错法、对法、根因。
- [ ] 关键词覆盖：entrypoint、call graph、data flow、consumer、producer、configuration、environment、permission、auth、state machine、cache、queue、feature flag、monorepo、workspace、generated code、test entry、impact map、AI 生成代码痕迹、架构漂移、依赖边界、证据索引。
- [ ] 已覆盖陌生项目读图、入口识别、调用链/数据流/配置/路由/测试基线、monorepo、AI 生成代码、架构漂移、依赖边界和风险边界。
- [ ] 输出要求包含证据索引、入口地图、调用链、数据/状态链、项目约定、测试基线、风险未知、impact map 和下一步技能。
- [ ] 边界清楚：只读学习，不替代实现、测试、审计、发布、DB/API 设计、观测、性能、策略、供应链或外部资料查证。
- [ ] 召回地图覆盖目录/依赖、入口、业务流、API、DB、部署、测试、权限和风险；真实学习报告验收标准明确。

## 2024-2026 新坑速查

- Monorepo / workspace：pnpm、Nx、Turborepo、Bazel、Gradle multi-project、package exports 和 workspace protocol 会让 impact map 跨包传播。
- Generated code：OpenAPI、GraphQL、protobuf、ORM、SDK、AI scaffold 生成文件不可直接当源头；必须找到 schema、模板和生成命令。
- AI 生成代码痕迹：伪 API、伪字段、弱异常处理、缺权限/并发/测试、伪观测字段、重复模板和不存在的配置 key 要逐项用项目证据验证。
- Agentic coding 痕迹：批量同构 commit、未遵守项目约定的依赖引入、happy path 测试、prompt/tool schema 漂移和无调用代码都只能作为风险线索。
- 架构漂移：迁移中目录、新旧分层并存、双框架、旧状态管理、废弃中间件会让同类实现不可直接照搬。
- Feature flag / 实验：真实链路可能由 flag、灰度、租户、地区、账号套餐和远端配置控制。
- Serverless / edge：入口、环境变量、冷启动、区域、日志、secret、回滚和 cache 与传统服务不同。
- RSC / SSR / hydration：前端项目要区分 server/client boundary、路由层、数据获取位置、缓存层和 hydration 副作用。
- 多语言入口惯例：Next/RSC 看 app/pages、route handler 和 server action；Spring Boot 看 main、controller、bean、profile；Django/FastAPI 看 urls/router、settings、ASGI/WSGI；Go 看 cmd、main、wire/fx；iOS/Android 看 app lifecycle、manifest、deeplink；worker/cron 看 scheduler 和 queue binding。
- Platform engineering：IDP、模板、golden path、service catalog 和 scorecard 可能隐藏部署、权限和观测约定。
- Supply chain：lockfile、postinstall、私有 registry、包签名、provenance、package exports 会影响运行与构建。
- Observability as code：dashboard、alert、SLO、runbook、release marker 可能在独立仓库或平台，不一定在服务代码旁。
- Policy as code：OPA、Kyverno、云 IAM、GitHub rulesets、CODEOWNERS 会影响权限、发布和合规边界。
- LLM / AI 集成：prompt、tool call、tool schema、vector store、model version、token cost、safety filter 和日志脱敏是独立 data flow。

## 与相邻技能的边界

- 本技能负责：陌生项目读图、真实入口识别、call graph、data flow、producer/consumer、configuration/environment、permission/auth、test entry、monorepo/workspace、generated code、架构漂移、AI 生成代码痕迹、依赖边界、impact map 和证据索引。
- 研究调研/research（rsch）：负责外部事实、官方资料、版本口径、资料冲突和引用；项目学习/project-learning（pl） 只读项目内部事实，外部行为不确定时切 研究调研/research（rsch）。
- API 工程/api-engineering（api）：负责 API 契约、状态码、认证授权、幂等、分页、OpenAPI/SDK 和兼容策略；项目学习/project-learning（pl） 只找现有 API 入口、消费者和契约证据。
- 数据库工程/database-engineering（db）：负责 schema、索引、SQL、事务、迁移、数据修复和 DB 写安全；项目学习/project-learning（pl） 只识别表/字段/读写路径和数据影响面。
- 测试验证/test-engineering（tst）：负责测试策略、场景矩阵、自动化、CI 证据、flaky 和覆盖结论；项目学习/project-learning（pl） 只识别测试基线、红绿入口、可验证入口和缺口。
- 发布部署/release-engineering（rls）：负责构建产物、环境、CI/CD、灰度、回滚、冒烟和发布证据；项目学习/project-learning（pl） 只识别部署入口、配置差异和发布风险线索。
- 可观测性/observability（obs）：负责 logs/metrics/traces、SLI/SLO、告警、incident、runbook 和观测治理；项目学习/project-learning（pl） 只识别日志/指标/trace 入口和排障证据位置。
- DevSecOps/devsecops（dso）：负责 SAST/DAST、SBOM、secrets、CodeQL/Semgrep/Trivy、OPA/Rego/Kyverno 和供应链治理；项目学习/project-learning（pl） 只识别策略、扫描和供应链影响线索。
- Web 安全/web-security（wsec）：负责 OWASP、XSS、CSRF、SSRF、CORS、IDOR、OAuth/JWT 和安全验证；项目学习/project-learning（pl） 只识别权限/可信边界和风险证据。
- 性能工程/perf-engineering（pfe）：负责性能基准、慢查询、缓存、容量和压测；项目学习/project-learning（pl） 只识别性能敏感链路和观测/配置证据。
- 代码审计/code-audit（aud）：负责代码改动后的需求对账、影响面、安全质量和证据最终收口；项目学习/project-learning（pl） 是改动前的证据地图输入，不能替代最终审计。
