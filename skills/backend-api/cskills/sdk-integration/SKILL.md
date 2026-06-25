---
name: sdk-integration
description: 第三方 SDK 集成工程技能，覆盖普通 SDK 初始化、鉴权、环境切换、升级迁移、breaking changes、回调契约、多端接入、示例验收、错误处理和发布回滚；涉及集成或升级非逆向第三方 SDK 时使用。
---

# SDK Integration

首次自称：SDK Integration（sdk-integration）。

定位：把第三方 SDK 从“示例能跑”收敛为“版本、初始化、鉴权、环境、回调、错误、隐私、升级和验收可控”。本技能处理合法公开 SDK 的工程集成，不做闭源 SDK 逆向、供应链审计或支付核心后端替代。

## 适用范围

- 普通第三方 SDK 接入：Web、Node、iOS、Android、Flutter、React Native、Unity、后端服务或多端 SDK。
- 初始化、配置、鉴权、app key/client id、环境切换、region、feature flag、回调、事件、错误码和日志。
- SDK 升级迁移、breaking changes、版本锁定、依赖冲突、示例改造、灰度发布和回滚。
- 多端一致性：同一业务在 Web/App/服务端 SDK 中的字段、状态、错误和回调契约对齐。
- SDK 官方示例验收、最小闭环 demo、mock/sandbox/live 环境分离和上线 checklist。

## 不适用范围

- 闭源 SDK 逆向、二进制供应链审计、ABI 恢复、符号分析、反编译或安全取证；转 sdkrev。
- 支付 SDK 的后端扣款、退款、回调验签、对账、状态机核心；转对应支付技能。
- 地图 SDK 的 provider 专项接入；转高德、Google Maps、Mapbox、腾讯地图等地图技能。
- 只读学习、项目上手、仅识别依赖中出现 SDK，没有集成、升级、调试、测试或发布动作。
- 未授权破解 SDK、绕过 license、盗用 key、规避风控、隐藏采集或供应链投毒。

## 铁律

1. 未确认 SDK 名称、版本、平台、官方文档、授权范围、环境、鉴权方式和业务闭环前，不开始改代码。
2. SDK key/secret/token 只按官方边界放置；server secret 不进前端、移动包、日志、截图和错误体。
3. 初始化必须幂等、可观测、可降级；重复 init、热更新、SSR、App 前后台切换和多实例都要有策略。
4. 回调契约必须稳定：事件名、payload、顺序、重试、线程/队列、错误码和生命周期要绑定业务状态机。
5. SDK 升级默认高风险；必须读 release notes、breaking changes、迁移指南、弃用项和最小版本要求。
6. 环境必须分离：dev/sandbox/staging/live 的 endpoint、key、tenant、region、webhook 和数据隔离不能混用。
7. 示例代码只能作为入口；必须改成项目错误处理、权限、隐私、日志、超时、重试和回滚风格。
8. 没有官方示例、真实最小闭环、失败场景和回滚验证，不报告 SDK 集成完成。

## 强制流程

1. 输入锁定：确认 SDK、平台、版本、业务目标、官方文档、账号/租户、环境、权限、数据流和禁止项。
2. 版本策略：锁定版本范围、包管理器、transitive dependencies、minimum OS/runtime、兼容矩阵和回滚版本。
3. 初始化设计：定义 init 时机、单例/多实例、配置来源、鉴权、重试、超时、日志、降级和重复调用行为。
4. 权限隐私：列 SDK 需要的系统权限、用户授权、数据采集、隐私披露、开关、脱敏和合规文案交接。
5. 回调契约：梳理 success/fail/cancel/progress/webhook/event listener、线程/队列、重复投递、乱序和业务状态迁移。
6. 错误模型：把 SDK error code 映射成项目稳定错误；保留 request id、trace id、SDK version 和脱敏上下文。
7. 多端对齐：同一业务字段、状态、错误和事件在 Web/App/服务端 SDK 中保持兼容。
8. 验证闭环：跑官方示例、项目最小闭环、负向、弱网、权限拒绝、环境切换、升级回滚和发布前 smoke。
9. 交付：输出版本、配置、初始化点、回调矩阵、错误映射、验证证据、风险和回滚方案。

## 场景执行卡

## 回调与密钥矩阵

- 回调契约必须列 event name、payload schema、签名/验签边界、幂等键、重放窗口、ack 语义、重试、乱序、线程/队列和业务状态迁移。
- 鉴权材料分级：publishable/client key、server secret、refresh token、license、webhook secret 分别写允许端、日志、包体、截图、错误体和 CI 规则。
- 验证证据至少包含官方示例、项目最小闭环、sandbox/live 切换、负向、弱网、权限拒绝、回滚版本和 smoke 结果。
- 多端差异要记录 Web SSR/CSR、Node、iOS、Android、Flutter/RN、Unity 的生命周期、线程、权限、包体、混淆/R8、SPM/CocoaPods/Gradle/npm 锁定。
- 参考公开 SDK 时看 release notes、migration guide、examples、CI、privacy/security policy 和 issue 中的 breaking change。

### 新 SDK 接入

- 查：官方 quickstart、API reference、平台版本、账号权限、key 类型、环境、示例项目和限制条款。
- 做：先最小闭环，再接入项目；配置集中管理；敏感 key 后端化；初始化与业务调用分层。
- 验：成功、失败、取消、重复初始化、无网络、权限拒绝、错误码、日志脱敏、回滚开关。

### SDK 升级迁移

- 查：当前版本、新版本、release notes、breaking changes、deprecated API、依赖冲突、安全修复和迁移指南。
- 做：先建兼容清单和灰度方案；替换 API 时同步测试、文档、mock、CI 和回滚版本。
- 验：旧功能回归、迁移路径、配置兼容、序列化变更、回调顺序、性能和包体影响。

### 回调与事件

- 查：事件触发时机、线程、队列、重复投递、错误码、取消语义、payload 字段和签名/验签边界。
- 做：回调只做轻处理和状态投递；业务状态机在项目层推进；重复/乱序要安全。
- 验：重复回调、乱序、取消、失败重试、App 生命周期、后台/前台、tab 切换。

### 多端集成

- 查：Web/iOS/Android/后端 SDK 字段差异、环境差异、能力差异、错误码差异和版本节奏。
- 做：抽象业务契约，不把某端 SDK 字段直接扩散到全端；缺能力时明确降级。
- 验：同一账号、同一环境、同一业务数据在多端一致，失败和回滚路径一致。

## SDK 集成核心陷阱速查（鉴权/重试/幂等/版本独家）

鉴权方式与生命周期：

- **API key**：长期凭据；最简单但泄露后只能轮换；必须只在服务端用、绝不进客户端 bundle / mobile app；不进 git、不进日志；存 secret manager (Vault/AWS Secrets Manager/GCP Secret Manager)。
- **OAuth 2.1 + PKCE**（取代 implicit flow）：移动/SPA 必须 PKCE（code_verifier + code_challenge）；refresh token 比 access token 长但仍要定期轮换；access token 默认 1h 内过期。
- **JWT** + JWKS：服务端验签用 issuer 公布的 JWKS endpoint（不要硬编码 public key）；验证 `iss`/`aud`/`exp`/`nbf`/`iat`；不接受 `alg: none`、不接受 HS256 if 期待 RS256（algorithm confusion 攻击）。
- **mTLS** / 双向证书：企业 SDK 常用；客户端证书在 TLS 握手时验证；证书过期是 PKI 头号事故源，监控 + 提前 30 天告警轮换。
- **PAT (Personal Access Token)** vs **OAuth App** vs **GitHub App**：CI 用 GitHub App（fine-grained + 短期 token）不用 PAT；轮换难度 OAuth > App > PAT。
- token 刷新竞态：多线程同时刷新 refresh token 会让一个成功一个失败（refresh token rotation）；用 mutex / single-flight 模式串行化刷新。

retry / idempotency / rate limit：

- **idempotency key**：客户端生成 UUID 放 `Idempotency-Key` header；服务端用此 key 去重（Stripe/Square/PayPal 都支持）；重试用同 key 拿同结果不重复扣款。
- 默认**不重试 POST/PATCH** 除非有 idempotency key；GET/HEAD/OPTIONS/PUT/DELETE 是 idempotent 可重试。
- **exponential backoff + jitter**：base × 2^attempt + random(0, jitter)；避免 thundering herd；上限 30s-60s；最多 3-5 次。
- **rate limit header**：`X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` / `Retry-After`；429 响应必须遵守 `Retry-After`。
- circuit breaker：连续失败超阈值打开熔断（resilience4j、Polly、tower::Service）；half-open 状态试探恢复；防止 cascading failure。
- timeout 分层：connect timeout（3-5s）、read timeout（10-30s）、total timeout；总超时 < 调用方期望响应时间。

webhook 与回调契约：

- **签名验证**：webhook payload 必须 HMAC SHA-256 签名（Stripe Signature header、GitHub X-Hub-Signature-256、Slack X-Slack-Signature）；服务端用 webhook secret 重算 + constant-time compare（`crypto.timingSafeEqual` 防 timing attack）。
- **replay 防护**：签名包含 timestamp，服务端拒绝 5 分钟外的请求；记录 event_id 去重（at-least-once delivery）。
- **at-least-once vs exactly-once**：webhook 默认 at-least-once，处理必须幂等；用 event_id 作 dedupe key 写 DB unique 约束。
- 同步响应：webhook handler 必须 < 5s 返回 2xx（多数 provider 超时阈值）；长任务入队列 + 立即 ACK；不要在 handler 内调 LLM/邮件/支付。
- **event ordering** 不保证：跨 webhook 调用是并发；同实体多事件用 version/timestamp 判最新；同步状态机用 event sourcing 或 outbox。
- 失败重试：provider 自动重试（指数退避，通常 24h-72h）；过期不送达；监控 dead letter queue。
- **callback URL / redirect URI** 安全：白名单匹配、不接受任意 URL；OAuth callback URL 必须 https + 注册到 provider。

环境与版本：

- **sandbox / staging / production** 严格隔离：不同 base URL、不同 API key、不同 webhook endpoint；测试数据不混生产。
- **SDK 版本 pin**：lockfile + semver；`^1.2.3` 允许 minor 升级风险；`~1.2.3` 只 patch；`1.2.3` 完全 pin；定期 audit + 计划升级。
- **breaking change** 监控：订阅 provider changelog / RSS / GitHub releases；deprecate 通知通常 6-12 个月窗口；旧版本支持期记到日历。
- multi-region：region-aware endpoint（`api-us.example.com` vs `api-eu.example.com`）；GDPR/数据主权要求；不要跨 region 复制 PII。
- **feature flag** 控制 SDK rollout：金丝雀 / 灰度 / 按 user/tenant 渐进；新 SDK 切换有 fallback 回旧版路径。

## 2024-2026 SDK 集成增量速查

鉴权与协议：

- **OAuth 2.1**（2024 draft）：合并 OAuth 2.0 + best practices + PKCE 强制；移除 implicit flow、ROPC（resource owner password credentials）。
- **OIDC**（OpenID Connect）持续主流：`id_token`（JWT）+ `userinfo` endpoint；社交登录、SSO。
- **Passkey / WebAuthn / FIDO2**：替代密码；浏览器/OS-level credentials；passkey provider SDK（Apple/Google/1Password/Microsoft Authenticator）。
- **DPoP**（Demonstrating Proof of Possession，RFC 9449）：access token 绑定到客户端公钥，防 token 泄露后被重用。
- **mTLS for SaaS APIs**：金融/医疗领域 + zero-trust 网络越来越常见。

API 生态：

- **Stripe / PayPal / Square** 支付 SDK：idempotency key 必须、webhook 签名、PCI-DSS 合规（不存卡号）；3DS / SCA 流程。
- **Twilio / SendGrid / Mailgun** 通信 SDK：rate limit + bouncing/suppression list 处理；webhook event 状态机。
- **Auth0 / Clerk / Supabase Auth / Firebase Auth / AWS Cognito** 身份 SDK：multi-tenancy、organization、custom claim、JIT provisioning。
- **OpenAI / Anthropic / Google Gemini** LLM SDK：streaming、function calling/tool use、token cost、rate limit + retry-after、structured output。
- **Apollo Federation / Hasura / Supabase / PostgREST** Backend-as-a-Service：自动 codegen client SDK。

工具与 CodeGen：

- **OpenAPI generator** + **openapi-typescript** + **kiota**（Microsoft）：从 OpenAPI 生成 typed client；持续同步 provider spec。
- **gRPC-Web / Connect** + **Buf Schema Registry**：proto 生成多语言 client。
- **typed webhook handler**：Hookdeck / Svix / Inngest：托管 webhook 路由 + retry + 监控。
- **Postman / Bruno / Insomnia** + **Hoppscotch**：API client + spec 验证；CI 集成 Postman runner。

合规与监控：

- **SBOM (CycloneDX/SPDX)** SDK 依赖供应链：`npm sbom` / `pip-sbom` / `syft` 生成；CI 跑 `grype`/`trivy` 扫漏洞。
- **dependency confusion**：私有 npm/pypi/maven 包名要 scoped 且优先级 > 公网；2024 仍是主流供应链攻击。
- **observability**：SDK call 加 trace context（W3C TraceContext header `traceparent`）；记录 status code + duration + error class；不记 secret/PII。
- **EU AI Act** + **GDPR**：调 AI provider 需要数据出境合规；终端用户告知；不上传 PII 训练。

## 低级错误清单

- 重复初始化、全局配置污染、SSR 中访问浏览器 API、热更新或前后台切换后 SDK 状态错乱。
- sandbox/live key 串环境、token 过期或时钟偏移未处理、错误码直接透给用户、debug 日志泄露密钥。
- 升级只改包版本，不看 lockfile、transitive dependency、minimum OS/runtime、序列化变化、回调顺序和弃用 API。
- 示例代码直接搬进项目，绕过项目权限、隐私、日志、超时、重试、错误映射和回滚开关。

## 输出要求

- 必须列 SDK 名称、版本、平台、官方文档依据、初始化点、配置项、鉴权边界、回调矩阵、错误映射和验证结果。
- 升级任务必须列 breaking changes、影响面、回滚版本和灰度策略。
- 不输出真实 key、secret、token、license、用户隐私数据或供应商敏感配置。

## 相邻技能边界

- 闭源 SDK 逆向审计走 sdkrev；sdk-integration 只处理公开、授权、工程接入。
- 支付 SDK 的资金核心走对应支付技能；本技能只协助客户端 SDK 初始化和回调接入边界。
- 地图、AI、推送、埋点等 provider 已有专项技能时，优先使用 provider 专项。