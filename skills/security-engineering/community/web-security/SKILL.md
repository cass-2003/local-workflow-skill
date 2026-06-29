---
name: web-security
description: Web Security实战排障版 - 覆盖授权范围、资产入口、威胁建模、风险评分、ASVS 映射、证据闭环、OWASP Top 10 2021/2024、OWASP API Security、认证授权、Session/Cookie、CSRF SameSite、XSS、CSP/Trusted Types、SQL/NoSQL/SSTI、SSRF 云元数据、RCE、防御性文件上传、路径穿越、反序列化、CORS、JWT、OAuth/OIDC、BOLA/IDOR、GraphQL、WebSocket、供应链、secret scanning、日志取证、修复验证。仅服务授权测试、防御、教育与 CTF；拒绝破坏、DoS、逃避检测、未授权利用和凭证窃取。
---

# Web 安全

> 定位：Web 安全（web-security，兼容 slug: wsec）把 Web/API/浏览器安全从漏洞名清单收敛成资产、入口、威胁、证据、复现、修复、回归、发布边界可复核的闭环。
> 铁律：只处理授权测试、防御、教育和 CTF；授权不清只做静态审计与防御建议。禁止批量扫描、DoS、绕过检测、持久化、凭证窃取、数据破坏、未授权利用或可直接滥用的攻击链。

## 快速总则：资产 / 入口 / 威胁 / 证据

1. 资产：先列域名、API、后台、管理端、WebView、对象存储、CDN、网关、SSO、第三方回调、环境、版本、账号角色、租户和授权边界。
2. 入口：按路由、中间件、认证守卫、GraphQL resolver、WebSocket 握手、文件处理、URL 拉取、模板渲染、SQL/NoSQL、日志、CI/CD 和发布配置追真实入口。
3. 威胁：先建 subject、tenant、object、action、data flow、trust boundary，再判断 OWASP Top 10 2021/2024、OWASP API Security、ASVS、供应链和浏览器风险。
4. 证据：每条结论绑定入口、条件、请求/响应摘要、代码/配置位置、日志/trace、影响对象、修复点和复验路径；未读不引，未跑不报。
5. 最小影响：生产默认不做高影响验证；复现样本要低权限、低数据量、可回滚、可脱敏。
6. 最小披露：Cookie、JWT、Authorization、session、client_secret、验证码、个人数据、admin key 只写类型、位置、掩码、哈希或指纹。
7. 修复闭环：证明旧路径被阻断、同类入口已查、正常业务仍可用、日志已脱敏、告警可见、灰度和回滚风险已说明。

## 单技能工程门禁

Web 安全不是扫描报告，也不是漏洞百科；凡涉及 Web 安全修复、审查或开发落地，必须先过这些工程门禁：

1. 入口门禁：列出真实入口，不只看登录页。至少覆盖前台 API、管理端、后台任务、导入导出、对象存储、回调、网关、WebSocket/GraphQL、旧版本客户端和移动 WebView。
2. 身份门禁：每个入口都要说明认证主体来自哪里，是否由服务端可信中间件生成；禁止信任客户端传入的 `X-User-Id`、`X-Role`、`tenantId`、`isAdmin` 或隐藏表单字段。
3. 授权门禁：认证通过不等于授权通过。读、写、删、导出、批量、后台任务、对象存储下载和消息订阅都必须有 subject、tenant、object、action 的服务端决策证据。
4. 资源门禁：任何资源 id、slug、订单号、文件 key、预签名 URL、channel、GraphQL node id 都视为不可信对象引用；必须验证归属、状态、租户和字段级权限。
5. 浏览器门禁：Cookie、CORS、CSRF、CSP、XSS、iframe、缓存、Service Worker、第三方脚本和 SSO 回调要作为一组验证，不能只改单个 header。
6. Token 门禁：JWT/OAuth/OIDC/session 要覆盖签名、alg、kid、iss、aud、exp、nbf、scope、tenant、撤销、刷新、登出、轮换和旧 token；只验签名不算通过。
7. 输入门禁：body、query、path、header、cookie、文件、URL、webhook、队列、模板、JSON/XML/YAML 都默认不可信；结构字段也要 allowlist，不只对值做转义。
8. 输出门禁：API 响应、HTML、富文本、下载、错误详情、日志、trace、APM、缓存和第三方上报都要验证最小披露和上下文编码。
9. 发布门禁：安全修复必须有负向测试、正向回归、日志脱敏样本、告警/监控项、灰度范围和回滚条件；只说“已修复”无效。
10. 证据门禁：工具、SAST、DAST、WAF、依赖扫描只能当线索；结论必须绑定代码/配置/请求摘要/日志/测试四类证据中的至少两类，无法验证要写原因。

## 风险评分与分级

风险等级必须由证据驱动，不凭漏洞名定级：

1. 维度：影响数据敏感度、权限变化、租户边界、是否需登录、攻击前置条件、用户交互、可达环境、默认配置、可检测性、补救复杂度。
2. 严重：可造成跨租户/管理员级越权、敏感数据大规模暴露、认证绕过、服务端执行任意不可信逻辑、供应链制品污染；需明确授权证据和影响范围。
3. 高：可稳定访问或修改非授权对象、绕过关键业务授权、泄露高敏信息、利用默认高危配置，但范围或前置条件受限。
4. 中：需要特定角色、交互、配置或链路组合，影响局部数据、会话安全或防护纵深。
5. 低：信息暴露、缺失安全头、版本提示、弱配置等，尚无明确可利用路径或业务影响；不得夸大。
6. 证据等级：A=代码/配置/日志/请求摘要闭环；B=两类证据相互印证；C=单点证据需复核；D=仅假设，不能作为结论。
7. 输出格式：风险=严重/高/中/低/信息；证据=A/B/C/D；影响=用户/租户/数据/权限/服务；置信度=高/中/低。

## 硬禁止与低级错拦截

- 禁止只鉴登录不鉴资源；每个对象、字段、导出、批量项、订阅频道和后台任务都要做服务端授权。
- 禁止把前端隐藏按钮、路由守卫、菜单权限、disabled 控件或客户端字段过滤当安全边界。
- 禁止信任客户端 header、cookie 字段、query/body 中的 userId、tenantId、role、scope、isAdmin；可信身份只能来自服务端认证链路。
- 禁止 CORS 使用 `*` 或反射 Origin 同时允许 credentials；CORS 永远不能替代认证、授权或 CSRF。
- 禁止 JWT 只验签名；必须校验 issuer、audience、expiry、not-before、algorithm、kid allowlist、tenant/scope 和撤销/轮换策略。
- 禁止 OAuth/OIDC 回调只换 token；必须校验 state、nonce、PKCE、redirect_uri、iss、aud、azp 和开放重定向。
- 禁止文件上传只看后缀或 Content-Type；必须校验 magic number、大小、解析器、存储权限、下载鉴权、扫描转换和可执行隔离。
- 禁止 SSRF 只做字符串黑名单；必须验证解析后 IP、重定向每跳、DNS rebinding、IPv6、云 metadata、超时、响应大小和 egress allowlist。
- 禁止 SQL/NoSQL 只参数化值却拼接字段、排序、过滤、聚合、JSON path 或 operator；结构输入必须白名单映射。
- 禁止把安全修复只靠 WAF、网关规则、前端校验或单点 middleware；根因必须在业务授权、输入边界或配置源头关闭。
- 禁止日志、截图、报告、测试输出打印完整 Cookie、JWT、Authorization、session、验证码、secret、PII 或真实 admin key。
- 禁止只跑 happy path；安全修复必须跑跨租户、低权限、未登录、旧 token、批量混入、异常输入和正常业务回归。

## ASVS 映射速查

- V1 架构：威胁建模、信任边界、组件边界、数据分类、第三方依赖和安全需求可追溯。
- V2 认证：密码、MFA、Passkeys/WebAuthn、账号恢复、风险登录、暴力尝试防护和认证日志。
- V3 会话：session 生命周期、Cookie 属性、登出失效、刷新、撤销、跨设备和跨站策略。
- V4 访问控制：BOLA/IDOR、RBAC/ABAC、租户隔离、对象/字段/批量/导出/后台任务逐项授权。
- V5 输入验证：所有外部输入、类型、长度、格式、allowlist、文件、URL、JSON/XML/YAML 和模板。
- V6 密码学：密钥管理、token 签名、敏感字段保护、随机数、传输和存储边界。
- V7 错误与日志：错误详情、审计日志、脱敏、trace/APM、取证字段、保留周期和访问控制。
- V8 数据保护：PII、缓存、下载、对象存储、备份、第三方上报和最小披露。
- V9 通信：TLS、HSTS、代理头、服务间身份、webhook 回调和证书/信任链。
- V10 恶意代码：文件上传、内容转换、依赖、插件、脚本、反序列化和供应链门禁。
- V11 业务逻辑：工作流顺序、金额/库存/额度、重复提交、并发、状态机和异常分支。
- V12 文件资源：上传、下载、路径、预签名 URL、CDN 缓存、私有桶、病毒扫描和转换隔离。
- V13 API/Web Service：REST、GraphQL、WebSocket、SSE、版本兼容、限流、schema、错误和对象授权。
- V14 配置：安全头、CORS、CSP、依赖版本、调试模式、CI/CD、secret scanning、SBOM 和发布回滚。

## 场景执行卡

### 1. 资产、授权与威胁建模

- 输入：授权书、资产清单、账号角色、时间窗口、环境、禁止项、流量上限、数据脱敏要求、第三方边界。
- 动作：画出用户/租户/服务/第三方/云资源之间的信任边界，标出公网、内网、管理端、回调、上传、导出、对象存储、CI/CD 入口。
- 验证：授权缺口、生产影响、第三方数据、速率限制、测试账号隔离、审计日志留痕。
- 证据：资产编号、入口列表、角色矩阵、版本/平台/框架/运行环境差异、未覆盖范围。
- 风险映射：ASVS V1、V4、V7、V14；重点看边界遗漏和授权不清。

### 2. 认证、授权、会话与租户隔离

- 输入：登录方式、MFA、Passkeys/WebAuthn、RBAC/ABAC、Session、Cookie、JWT、OAuth/OIDC、旧客户端、管理员入口。
- 动作：核认证状态、对象归属、tenant、role、scope、服务间身份、token 生命周期、撤销、刷新、登出失效、权限缓存。
- 验证：未登录、低权限、跨租户、角色切换、批量混入、旧 token、可信 header 清洗、Cookie SameSite/Secure/HttpOnly/Domain/Path。
- 证据：subject、tenant、object、action、decision、token claim 摘要、Cookie 属性、审计日志脱敏结果。
- 风险映射：ASVS V2、V3、V4、V6、V7；对象级授权缺失通常高于认证体验问题。

### 3. OWASP Top 10 2021/2024 与 API Security 基线

- 用 OWASP Top 10 2021、OWASP API Security、ASVS 和 OWASP 2024 相关专题做检查框架，不把标准名当结论。
- Broken Access Control：BOLA、IDOR、越权、管理接口、导出下载、批量接口、GraphQL resolver 和对象存储下载逐项验权。
- Injection：SQL、NoSQL、命令、SSTI/模板、LDAP、路径穿越、表达式注入；字段名、排序、过滤、聚合必须 allowlist。
- Security Misconfiguration：CORS、CSP、安全头、调试模式、默认账号、错误详情、云存储公开、依赖版本、网关头信任边界。
- Software and Data Integrity Failures：依赖、构建插件、CI/CD、SBOM、签名、provenance、AI 生成代码和 secret scanning 联动 dso。

### 4. CSRF、XSS、CSP、Trusted Types 与浏览器边界

- CSRF：所有自动携带 Cookie 的状态变更接口校验 Origin/Referer 与 CSRF token；CSRF SameSite 只是纵深防御。
- XSS：区分 Stored、Reflected、DOM、Markdown/富文本、模板注入；按 HTML、属性、URL、JS、CSS 上下文编码。
- CSP：先 Report-Only 收证据，再阻断；nonce/hash 优先，限制 strict-dynamic 风险，避免 unsafe-inline 和宽泛通配。
- Trusted Types：现代前端对 DOM XSS 高风险 sink 设策略，验证第三方 SDK、A/B、客服、支付脚本兼容。
- 安全头：HSTS、X-Content-Type-Options、Referrer-Policy、Permissions-Policy、frame-ancestors、敏感响应 Cache-Control。
- 风险映射：ASVS V3、V5、V8、V14；浏览器问题需说明用户交互、会话条件和业务影响。

### 5. CORS、跨站 Cookie、SSO 与 OAuth/OIDC

- CORS：精确 Origin allowlist；禁止反射任意 Origin，禁止 credentials 搭配星号；CORS 不是授权。
- Cookie：核 SameSite=None 必须 Secure，第三方 Cookie 变化、CHIPS、Storage Partitioning、Safari ITP 对 SSO、嵌入页和 CSRF 的影响。
- OAuth/OIDC：校验 redirect_uri 精确匹配、state、nonce、PKCE、iss、aud、azp、jti、token 绑定、回调域名和开放重定向。
- JWT/JWK：固定 algorithms，校验 iss/aud/exp/nbf/iat/tenant/scope，kid allowlist，限制 JKU/X5U，JWKS 缓存和轮换有证据。
- 风险映射：ASVS V2、V3、V4、V6、V9、V14；SSO 修复必须覆盖旧客户端和回滚方案。

### 6. SSRF、URL 拉取、云元数据与 egress

- 入口：URL 预览、webhook、PDF/HTML 渲染、图片代理、导入、OAuth metadata、SSO discovery、存储同步、爬虫。
- 动作：校验 scheme、规范化 URL、解析后 IP、每跳重定向、DNS rebinding、IPv6、混淆 IP、URL parser 差异、超时、大小、响应类型。
- 防护：阻断云 metadata、内网网段和 link-local；配 egress allowlist、代理隔离、IMDSv2/云厂商 metadata 防护和告警。
- 证据：最终连接目标、DNS 解析链、重定向链、拦截日志、云环境差异、正常业务 allowlist。
- 风险映射：ASVS V5、V8、V9、V14；仅给防御验证摘要，不给可复用探测链。

### 7. 注入、SSTI、RCE、文件上传与反序列化

- SQL/NoSQL：值用 bind；动态表名、字段、排序、LIKE、IN、分页、聚合和 JSON 查询用 allowlist；过滤 $、.、操作符和类型混淆。
- SSTI/RCE：模板、表达式、插件、脚本、文件解析器、命令执行和反序列化 gadget 只给防御审计、低影响复现摘要和修复验证。
- 文件上传：file upload 必须校验扩展名、MIME、magic number、大小、尺寸、页数、压缩层级、重命名、私有桶、预签名 URL、下载鉴权、病毒扫描、内容转换。
- 路径穿越：规范化后校验根目录，阻断 ../、编码、软链、zip slip、对象存储 key 穿越。
- 反序列化：禁不可信对象反序列化；JSON/XML/YAML 关闭危险类型、XXE、任意 class；DTO allowlist 防 mass assignment。
- 风险映射：ASVS V5、V10、V11、V12；避免输出可直接滥用 payload 或攻击链。

### 8. GraphQL、WebSocket、SSE 与长连接

- GraphQL：入口认证不等于字段授权；resolver 按对象和字段验权，限制 depth、complexity、alias、batch、introspection、error detail 和 DataLoader 泄露。
- WebSocket：握手认证、Origin 校验、token 续期/撤销、频道订阅授权、租户隔离、消息 schema、重放、心跳、断线恢复和背压。
- SSE/streaming：鉴权、断线重连、last-event-id、缓存、敏感片段、日志脱敏和前端错误处理。
- 证据：握手摘要、订阅主题、subject/tenant/channel、消息类型、拒绝日志、限流和正常路径。
- 风险映射：ASVS V4、V5、V7、V13；长连接必须验证持续授权和撤销生效。

### 9. 日志取证、依赖供应链与发布验证

- 日志取证：Authorization、Cookie、Set-Cookie、JWT、password、验证码、PII、client_secret、API key 禁止明文落盘或进入 APM/trace/prompt。
- 证据保全：记录 request_id、trace_id、时间窗、环境、版本、账号角色、脱敏样本、保留周期和访问权限。
- 依赖/框架：按版本、启用模块、配置、运行环境、CVE/GHSA、补丁行为和可利用条件判定；不凭标题判命中。
- 供应链：SAST、DAST、SCA、SBOM、secret scanning、容器镜像、IaC、CI 权限和制品 provenance 交 dso 落门禁。
- 发布/回滚：评估安全头、CORS、Cookie、OAuth、JWT、网关、中间件、CDN、WAF、灰度、告警和回滚兼容。
- 风险映射：ASVS V7、V8、V10、V14；supply chain 结论必须绑定制品和调用条件。

### 10. 漏洞复现与修复验证

- 复现：只在授权范围内执行，优先最小、低影响、可回滚样本；生产环境默认不做破坏性验证。
- 旧证据：记录版本、环境、账号角色、入口、参数、响应摘要、日志和影响面。
- 修复：最小改动阻断根因，覆盖同类入口，不借安全修复做无关重构。
- 验证：原路径负向失败、正常路径成功、相邻路径失败、权限矩阵通过、日志脱敏、告警可见、发布回滚说明完整。
- 风险映射：ASVS 全域；修复后风险需从“已阻断/残余/待验证”三类说明。

## 修复验证模板

每个安全修复必须按以下模板收口，缺项写“未验证+原因”：

1. 问题摘要：资产、入口、角色、环境、版本、风险等级、证据等级、ASVS/OWASP 映射。
2. 根因：认证/授权/输入验证/输出编码/配置/供应链/日志/发布流程中的具体缺口。
3. 影响面：用户、租户、对象、字段、接口、后台任务、缓存、移动端/WebView、第三方回调、历史数据。
4. 修复点：代码/配置/流程位置、策略、兼容性、灰度、回滚、残余风险。
5. 负向验证：旧路径被拒绝；跨租户、低权限、批量混入、相邻对象、旧 token 或异常输入按预期失败。
6. 正向验证：合法用户、合法对象、正常业务流、旧客户端兼容、告警无误报。
7. 证据：请求/响应摘要、日志/trace、审计记录、测试命令摘要、截图或报告均脱敏。
8. 发布：监控项、告警阈值、灰度范围、回滚触发条件、责任人和复查时间。

## 负向验证矩阵

安全修复没有负向证据，不算完成：

1. 认证：未登录、过期 session、旧 refresh token、撤销 token、错 issuer/audience、错 tenant/scope 都应失败。
2. 授权：低权限、跨租户、跨 owner、字段越权、批量混入、导出下载、后台任务、对象存储 URL 和订阅频道都应失败。
3. CSRF/CORS/Cookie：跨站状态变更、异常 Origin、缺 token、SameSite=None 无 Secure、credentials + 宽 Origin 都应失败或被拦截。
4. XSS/CSP：富文本、Markdown、URL scheme、属性上下文、DOM sink、第三方脚本兼容和 CSP Report-Only/Enforce 都要有样本。
5. SSRF/URL：内网、metadata、重定向、IPv6、DNS rebinding、超时、大响应、非 HTTP scheme 和正常 allowlist 都要测。
6. 上传/下载：伪造 MIME、错 magic number、超大文件、压缩炸弹、路径穿越、zip slip、私有文件下载和预签名过期都要测。
7. 注入：SQL/NoSQL 的值、字段、排序、过滤、聚合、操作符、JSON path 都要有拒绝或白名单证据。
8. 日志：访问日志、异常日志、网关日志、APM/trace、审计日志和测试输出都要确认脱敏，不只查业务 logger。
9. 回归：合法用户合法对象、旧客户端、灰度用户、缓存/CDN、回滚后状态和监控告警都要保留正向证据。

## 高频坑 / 防遗漏

### 高频坑

1. 只有登录校验，没有对象级授权，导致 BOLA/IDOR。
2. 只在前端隐藏按钮，后端接口仍可越权调用。
3. CORS allowlist 用后缀匹配，恶意相似域混入。
4. Cookie 改 SameSite=None 后漏 Secure 或漏 CSRF。
5. JWT 只验签名，不验 iss、aud、exp、nbf、tenant、kid allowlist。
6. OAuth/OIDC redirect_uri 使用通配，state/nonce/PKCE 缺失。
7. SSRF 只拦字符串 localhost，不校验解析后 IP、重定向链和云 metadata。
8. 文件上传只看扩展名，不看 MIME、magic number、存储权限和下载鉴权。
9. SQL ORM 仍拼接 order by、where 片段或 raw query。
10. GraphQL 只在入口验登录，resolver 和字段级对象未验权。
11. WebSocket 连接后不再校验订阅频道、租户和 token 撤销。
12. CSP 一上来阻断生产，第三方 SDK、支付、SSO 直接故障。
13. 日志记录完整 Cookie/JWT/Authorization，修复报告又泄露样本。
14. 依赖漏洞不核版本、启用模块和配置，误判命中或漏判。
15. 修复只改新入口，旧 API、后台任务、导出下载、移动端 WebView 未验证。

### 防遗漏清单

- 授权：是否有明确书面范围、账号角色、时间窗口、禁止项、脱敏和流量限制？
- 资产：域名、API、后台、GraphQL、WebSocket、对象存储、CDN、网关、回调、预发/生产是否列全？
- 数据：subject、tenant、object、action、scope、owner、缓存 key、channel 是否进入证据链？
- 输入：request body、query、header、cookie、文件、URL、webhook、队列消息、模板、第三方回调是否按不可信处理？
- 输出：浏览器上下文、API 响应、下载、日志、trace、APM、错误详情、缓存、第三方上报是否脱敏和授权？
- 版本：浏览器、Node/Java/PHP/Python/Ruby/.NET、框架、网关、CDN、WAF、容器镜像、云平台差异是否说明？
- 验证：漏洞复现、修复验证、正向回归、负向权限、日志脱敏、告警、发布或回滚风险是否都有证据？

## 输出要求

安全任务输出保持极简但可复核：

1. 结论：存在/不存在/部分覆盖/无法验证，附风险等级、证据等级和 ASVS/OWASP 映射。
2. 授权与范围：资产、环境、账号角色、允许动作、禁止项、未覆盖项。
3. 入口与证据：路径/接口/参数/代码或配置位置/请求响应摘要/日志或 trace；敏感值必须脱敏。
4. 威胁与影响：用户、租户、数据、权限、可利用条件、版本/平台/框架/运行环境差异。
5. 修复：最小代码/配置/流程改法，说明兼容、灰度、回滚和残余风险。
6. 测试：原漏洞复现、修复验证、正向/负向/边界/权限矩阵、已跑命令和结果；未跑写原因。
7. 取证：request_id、trace_id、时间窗、日志位置、保留周期、访问控制、脱敏方式。
8. 边界：需联动 api、dso、prot、rev、obs、tst、aud 时写触发原因。

## 约束

- 只服务授权测试、防御、教育与 CTF；未知授权范围不做主动扫描、爆破、fuzz、绕过、防护规避或高影响操作。
- 不提供批量扫描脚本、隐蔽绕过、持久化、凭证窃取、数据破坏、DoS、可直接复用的攻击链或未授权利用步骤。
- 不把工具扫描结果直接当结论；必须结合版本、配置、代码、路径、权限、可利用条件和日志证据。
- 不把安全头缺失夸大成高危；不把认证通过等同授权通过；不把 CORS 当授权；不把测试通过包装成可上线。
- 不输出完整 token、Cookie、JWT、session、secret、验证码、个人敏感数据或 admin key；截图、日志、请求摘要必须脱敏。
- 涉 API 契约找 api；涉供应链/CI/secret scanning 找 dso；涉抓包/协议证据找 prot；涉二进制/客户端混合容器证据找 rev；涉日志/告警/incident 找 obs；涉回归矩阵找 tst；最终改动由 aud 收口。

## 高频 Bug 反例库

- 反例 1：只鉴登录不鉴对象
  - 错法：用户登录后可传任意 orderId 查看他人订单。
  - 对法：服务端校验 subject、tenant、object、action，并在批量场景逐项校验。
  - 根因：认证和授权混淆。
- 反例 2：批量接口只验第一个 ID
  - 错法：批量导出混入他人 id 仍返回数据。
  - 对法：逐项验权，失败项拒绝或剔除并记录审计日志。
  - 根因：集合输入扩大对象级授权缺口。
- 反例 3：前端权限当安全边界
  - 错法：隐藏删除按钮，但 API 无权限校验。
  - 对法：后端 policy/middleware 强制授权，前端只做体验。
  - 根因：信任客户端。
- 反例 4：CORS 反射任意 Origin
  - 错法：请求什么 Origin 就返回什么，且允许 credentials。
  - 对法：精确 allowlist，敏感接口仍做认证授权和 CSRF 防护。
  - 根因：把跨域策略当鉴权。
- 反例 5：CSRF 只靠 SameSite
  - 错法：Cookie 自动携带的转账接口无 Origin/Referer 和 token。
  - 对法：SameSite、Origin/Referer、CSRF token 组合验证。
  - 根因：把浏览器默认策略当业务授权。
- 反例 6：XSS 只用正则过滤 script
  - 错法：富文本允许 SVG、事件属性、危险 URL scheme 和 Markdown HTML。
  - 对法：成熟 sanitizer allowlist，按上下文编码，CSP 和 Trusted Types 纵深。
  - 根因：输出上下文未建模。
- 反例 7：SQL 排序字段拼接
  - 错法：where 用 bind，但 order by 直接拼 query 参数。
  - 对法：字段和方向用 allowlist 映射。
  - 根因：只关注值注入，漏结构注入。
- 反例 8：SSRF 黑名单绕过
  - 错法：仅拦固定本地地址字符串，未校验最终连接目标。
  - 对法：校验 scheme、解析后 IP、每跳重定向、DNS rebinding 和 egress allowlist。
  - 根因：把输入字符串当连接目标。
- 反例 9：上传公开可执行
  - 错法：用户可控文件名进入公开目录并可被脚本执行。
  - 对法：重命名、私有存储、不可执行域、下载鉴权、扫描转换。
  - 根因：上传、存储、访问链路割裂。
- 反例 10：JWT 算法和 kid 信任 header
  - 错法：按 token header 动态选择算法或远程密钥地址。
  - 对法：固定 algorithms、issuer、audience、kid allowlist 与 JWKS 缓存。
  - 根因：把不可信 header 当信任配置。
- 反例 11：OAuth 缺 state/nonce/PKCE
  - 错法：授权码回调只换 token，不校验会话绑定。
  - 对法：state 防 CSRF，nonce 防 ID Token 重放，公共客户端用 PKCE。
  - 根因：登录态与授权响应未绑定。
- 反例 12：GraphQL resolver 裸奔
  - 错法：query 入口验登录后，字段 resolver 返回跨租户对象。
  - 对法：resolver 按对象和字段验权，限制深度、复杂度、批量和错误详情。
  - 根因：GraphQL 一次请求包含多个资源边界。
- 反例 13：WebSocket 订阅未验权
  - 错法：连接鉴权后客户端可订阅任意 tenant channel。
  - 对法：握手、订阅、消息发送和 token 撤销都校验 subject/tenant/channel。
  - 根因：把长连接认证当成持续授权。
- 反例 14：日志脱敏只改业务日志
  - 错法：网关、异常中间件、APM、trace baggage 仍记录 Authorization 和 Cookie。
  - 对法：入口、异常、访问日志、trace、第三方上报统一脱敏并验证样本。
  - 根因：只查应用代码不查观测链路。
- 反例 15：依赖漏洞只看 CVE 标题
  - 错法：看到 CVE/GHSA 就判高危或忽略 transitive dependency。
  - 对法：核版本、启用模块、配置、调用路径、补丁行为、SCA/SBOM 证据。
  - 根因：供应链风险需要可利用条件和制品证据。
- 反例 16：可信 header 被客户端伪造
  - 错法：后端直接读取 `X-User-Id` 或 `X-Tenant-Id` 决定身份和租户。
  - 对法：网关清洗危险 header，由认证中间件写入服务端上下文，业务层只读可信上下文。
  - 根因：混淆了外部请求头和内部信任边界。
- 反例 17：JWT 只验签名
  - 错法：签名正确就放行，忽略 aud、iss、exp、nbf、scope、tenant 和撤销。
  - 对法：固定算法和 key 来源，完整校验 claim、时钟偏差、租户、权限、撤销和轮换。
  - 根因：把加密完整性误当业务授权。
- 反例 18：OAuth 回调缺会话绑定
  - 错法：回调收到 code 就换 token，redirect_uri 宽匹配，state/nonce/PKCE 不校验。
  - 对法：精确 redirect_uri，校验 state、nonce、PKCE、iss、aud、azp 和开放重定向。
  - 根因：授权响应没有和发起会话绑定。
- 反例 19：CORS 星号配凭证
  - 错法：为了调试把 Origin 放宽，敏感接口允许 credentials。
  - 对法：精确 Origin allowlist，分环境配置，敏感接口仍走认证、授权和 CSRF。
  - 根因：把跨域访问便利当成安全策略。
- 反例 20：上传只看后缀
  - 错法：`.jpg` 后缀即允许进入公开桶，下载不鉴权。
  - 对法：校验 MIME、magic number、尺寸、内容转换、病毒扫描、私有存储和下载授权。
  - 根因：文件从上传到访问的整条链路没有建模。
- 反例 21：NoSQL operator 注入
  - 错法：把 JSON body 直接传给查询条件，攻击者提交操作符改变语义。
  - 对法：DTO schema 固定字段和类型，禁止危险 operator，查询结构白名单生成。
  - 根因：只防 SQL 字符串，忽略结构化查询也是输入。
- 反例 22：路径穿越只替换字符串
  - 错法：简单删除 `../`，编码、软链、zip slip 或对象 key 绕过。
  - 对法：解码和规范化后校验根目录，拒绝软链逃逸，解压前逐项校验目标路径。
  - 根因：把路径文本当最终文件系统位置。
- 反例 23：SSRF 没验重定向链
  - 错法：只检查首次 URL，后续 302 跳到内网或 metadata。
  - 对法：每跳重新解析、校验 IP/网段/scheme/host，限制跳转次数和响应大小。
  - 根因：只验证输入 URL，没验证实际连接目标。
- 反例 24：CSRF 修复破坏旧客户端
  - 错法：直接全站强制 token，旧 WebView、SSO 嵌入和支付回调故障。
  - 对法：按状态变更入口分级灰度，Origin/Referer/token 组合验证并保留兼容证据。
  - 根因：缺少浏览器、客户端和第三方回调矩阵。
- 反例 25：错误详情泄露对象存在性
  - 错法：无权限返回“订单属于别人”，不存在返回 404，方便枚举。
  - 对法：按业务策略统一不可见响应，审计日志记录真实原因。
  - 根因：错误映射泄露授权决策。
- 反例 26：限流只按 IP
  - 错法：登录、验证码、导出和敏感修改只按 IP 限流，账号和租户维度缺失。
  - 对法：按账号、设备、租户、IP、接口、风险动作和失败原因组合限流和告警。
  - 根因：攻击维度和业务对象维度未对齐。
- 反例 27：日志脱敏漏测试输出
  - 错法：生产日志脱敏了，但测试快照、CI artifact、错误截图仍含 token。
  - 对法：业务日志、网关、APM、测试输出、截图和报告统一脱敏校验。
  - 根因：只把日志当运行时问题，忽略交付证据链。
- 反例 28：只测漏洞样本不测正常业务
  - 错法：旧攻击路径被拒绝后直接上线，合法导出、SSO、上传或旧客户端断掉。
  - 对法：负向阻断和正向业务回归同时通过，灰度、监控和回滚条件齐全。
  - 根因：安全修复缺少产品路径和发布验证。

## 提交前自检清单

- [ ] frontmatter name 为 canonical `web-security`，description 存在，H1 为“Web 安全”；兼容 slug 为 `wsec`，自检不得要求 name 等于短 slug。
- [ ] 行数 <= 500。
- [ ] fenced code block 数量为 0。
- [ ] 必需章节齐全：快速总则、风险评分与分级、ASVS 映射速查、场景执行卡、修复验证模板、高频坑 / 防遗漏、输出要求、约束、高频 Bug 反例库、提交前自检清单、2024-2026 新坑速查、与相邻技能的边界。
- [ ] 快速总则为 Web 安全领域定制的资产 / 入口 / 威胁 / 证据。
- [ ] 反例数量不少于 10，且编号可被 反例\s*\d+ 命中。
- [ ] 关键词无缺失：OWASP Top 10 2021、OWASP 2024、CSP、Trusted Types、OAuth、OIDC、JWT、session、CSRF SameSite、CORS、SSRF 云元数据、SSTI、模板注入、GraphQL、WebSocket、file upload、supply chain、secret scanning、日志取证。
- [ ] 已覆盖版本/平台/框架/运行环境差异、入口/复现/证据/验证路径、高频真实 bug、安全/权限/数据/兼容/发布或回滚风险。
- [ ] 未输出完整凭证、Cookie、JWT、session、secret、个人敏感数据或 admin key。
- [ ] 涉测试验证联动 tst；最终改动按 aud 口径复核。

## 2024-2026 新坑速查

- OWASP Top 10 2021 仍以 Broken Access Control、Injection、Security Misconfiguration、Software and Data Integrity Failures 为高频；OWASP 2024 相关专题更强调 API、LLM/AI 生成代码、供应链和云原生配置证据。
- Chrome 第三方 Cookie 变化、CHIPS、Storage Partitioning、Safari ITP 会影响 SSO、嵌入页、跨站 Cookie、CSRF 和埋点。
- OAuth 2.0 Security BCP/RFC 9700 强化 PKCE、精确 redirect_uri、禁止隐式流程和开放重定向，旧 SPA 方案需复核。
- OWASP API Security 中 BOLA/IDOR 仍高频；GraphQL、批量、导出、对象存储下载都要测“别人的资源”。
- Next.js/边缘中间件/网关头处理存在绕过类风险；鉴权不要只放单层 middleware，危险 header 要在网关清理。
- JWT/JWK 风险集中在 alg confusion、kid/JKU/X5U、JWKS 缓存、issuer/audience 混淆和多租户 claim。
- SSRF 新坑集中在云 metadata、IPv6、DNS rebinding、重定向、URL parser 差异、PDF/HTML 渲染器、webhook 和 SSO discovery。
- CSP 与 Trusted Types 在现代前端更重要，但第三方 SDK、A/B、支付、客服脚本会带来兼容和发布回滚风险。
- GraphQL 风险集中在 resolver 对象级授权、query depth/complexity、alias/batch、introspection、错误详情和 DataLoader 跨租户缓存。
- WebSocket/SSE 风险集中在握手 Origin、token 撤销、频道授权、重连、消息 schema、日志脱敏和长连接限流。
- 对象存储预签名 URL、CDN 缓存、Service Worker、WebView、移动端内嵌浏览器会放大会话、CORS、缓存和下载鉴权问题。
- Passkeys/WebAuthn、MFA 恢复码、设备绑定和风险登录要验证降级、重放、账号恢复和客服绕过链路。
- DevSecOps 门禁应覆盖 SAST、DAST、SCA、SBOM、secret scanning、容器镜像、IaC、CI 权限和发布制品 provenance。
- AI 生成代码常漏鉴权、输入校验、日志脱敏、错误处理、测试证据；需按真实数据流审计。

## 与相邻技能的边界

- Web 安全（web-security，slug: wsec）负责：Web/API/浏览器安全威胁建模、认证授权、会话 Cookie、CSRF、XSS、SQL/NoSQL/SSTI、SSRF、RCE、上传、路径穿越、反序列化、CORS、CSP、Trusted Types、JWT、OAuth/OIDC、BOLA/IDOR、GraphQL、WebSocket、日志取证、漏洞复现与修复验证口径。
- API 工程（api-engineering，slug: api）负责：API 契约、状态码、版本兼容、幂等、分页、限流、OpenAPI/SDK；web-security 只定义安全检查点、威胁和防护验证。
- DevSecOps（devsecops，slug: dso）负责：SAST/DAST/SCA/SBOM、secret scanning、CI/CD 门禁、签名/provenance、容器/IaC、供应链和例外治理；web-security 提供 Web 风险样本和修复验证口径。仅当当前目标是把 Web 安全发现接入 CI/CD、安全门禁、供应链治理或发布制品证据时，才条件联动 dso。
- 协议分析（protocol-analysis，slug: prot）负责：授权抓包、HTTP/2/3、TLS、WebSocket/gRPC/MQTT 协议证据、时序和兼容性；web-security 使用其协议证据判断漏洞和防护。
- 逆向工程总控（reverse-engineering，slug: rev）负责：样本、二进制、APK/IPA、混合容器、私有格式和运行时观察；web-security 只接收其客户端证据并判断 Web 攻击面。
- 可观测性工程（observability，slug: obs）负责：logs/metrics/traces、SLO、告警、incident、runbook、观测成本和多租户观测；web-security 只定义安全日志、取证、脱敏和告警需求。
- 测试验证（test-engineering，slug: tst）负责：测试策略、场景矩阵、自动化、CI 证据、回归和冒烟结论；web-security 提供风险样本、权限矩阵和验收口径。只有当前步骤实际要写测试、跑测试、做回归或用测试证据证明修复时，才条件联动 tst；不能因 `requires` 自动升级。
- 代码审计（code-audit，slug: aud）负责：最终需求对账、影响面追踪、安全/质量复盘和修复复验收口；web-security 改动或安全修复完成后必须按其口径收口。
