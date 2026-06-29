---
name: backend-engineering
description: 后端工程实战排障版技能 - 面向后端服务入口、路由/中间件、连接池、超时/重试/熔断、事务/锁、队列、缓存、配置/密钥、容器运行、健康检查、日志/指标/trace、OpenTelemetry、Kubernetes probe、serverless/edge runtime、SBOM/供应链的实战定位、修复和交付验证。涉及后端服务、运行时、API 主链路、依赖治理、线上排障、发布回滚时必须使用。
---

# 后端工程

后端工程（backend-engineering，兼容 slug: be）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

## 快速总则

1. 先锁现场：服务名、语言/框架版本、运行时、入口命令、端口、路由挂载、中间件顺序、环境变量、镜像 tag、部署版本、区域/租户、请求样本、trace_id/request_id。
2. 先证据后结论：日志、指标、trace、错误码、堆栈、连接池状态、DB/Redis/MQ 状态、Kubernetes Event、probe 结果、最近发布/配置/依赖变更必须能复核。
3. 先画边界：入口 Handler/API → Middleware → Service/Domain → Repository/Client → DB/Cache/MQ/Task → Container/Runtime → Observability/Deploy。
4. 先识别业务不变量：核心实体、状态机、幂等键、唯一性、权限边界、金额/库存/额度/配额、时间窗口和不可逆副作用；技术修复不得绕过业务不变量。
5. 复杂度要有预算：引入缓存、队列、微服务、分布式锁、Service Mesh、serverless 前，必须说明触发条件、收益、失败模式、运维成本、回滚路径；能用模块化单体/本地事务解决时不升级架构。
6. 先查调用方和消费方：改路由、字段、错误码、配置 key、队列 topic、缓存 key、任务名、健康检查路径前后都要全量追踪生产者和消费者。
7. 后端默认有外部依赖：DB、Redis、MQ、HTTP/gRPC、对象存储、配置中心、密钥系统、身份提供方、Service Mesh、云托管限制都可能是根因。
8. 所有外部 I/O 必须有超时、取消传播、连接池上限、失败分类；重试必须有退避、抖动、上限、幂等前提和熔断/隔离。
9. 写链路默认考虑事务、锁、幂等键、唯一约束、状态机、补偿、回调重放和队列重复投递；禁止事务内做 HTTP/RPC/MQ 等不受控 I/O。
10. 容器/平台不是透明层：CPU throttling、内存 OOM、DNS、时钟、文件系统只读、信号处理、graceful shutdown、Kubernetes probe、serverless 冷启动都要纳入证据。
11. 配置和密钥默认高危：缺失应拒绝启动；Secret 不进仓库、镜像、日志、trace；轮换、缓存、权限和回滚要有方案。
12. 完成必须交付证据：改动点、影响面、验证命令/结果、未验证项、上线/回滚/监控要求；未跑不报通过，未读不报覆盖。

## 单技能工程门禁

- 后端改动必须先写清本次链路穿过哪些层：入口/DTO、中间件、Service/Domain、Repository/Client、DB、Cache、MQ/Task、Observability、Deploy；缺任一层证据时不得声称全链路完成。
- 禁止只改 Handler 或 Controller 就报完成；只改入口不改 service 不变量、repo 条件、缓存/事件/旧客户端/错误语义，默认按半成品处理。
- 禁止用前端权限、隐藏按钮、路由菜单或客户端字段当安全边界；权限、租户、owner、状态机、批量逐项验权必须在服务端落地。
- 禁止请求体直绑内部实体、ORM model 或 domain aggregate；所有外部输入必须进入 DTO/schema，再由白名单 mapper 写入服务端允许字段。
- 禁止 catch 后返回成功、吞掉错误、只打日志不断路；错误必须映射为可观测、可重试语义清晰、不会泄露内部细节的结果。
- 禁止外部依赖无超时、无取消传播、无连接池预算、无失败分类；任何 HTTP/gRPC/DB/Redis/MQ/对象存储调用都要有超时和降级或失败收口。
- 禁止非幂等重试；POST、支付、发券、发货、扣减、创建资源、投递事件、任务重放必须有幂等键、唯一约束或状态机兜底。
- 禁止事务内做外部 HTTP/RPC/MQ/对象存储/邮件/短信；事务内只做本地原子写和 outbox，事务后再投递副作用。
- 禁止 UPDATE/DELETE 不检查 affected rows；0 行、多行、租户不匹配、owner 不匹配、软删、版本冲突、幂等无变化必须分清。
- 禁止把日志、trace、metrics、错误响应、队列 payload 当安全区；token、Cookie、Secret、手机号、身份证、连接串、支付参数默认脱敏或不采集。
- 旧客户端、旧 SDK、第三方回调、异步消费者和后台任务必须作为消费方处理；新增字段、错误码、状态流转、事件 payload 不能只按新前端验证。
- 灰度、回滚、迁移兼容、监控告警和降级条件必须在交付说明里出现；只有本地冒烟或接口 200 不等于后端主链路可上线。

## 一次开发落地矩阵

- 入口层：路由、方法、鉴权、租户、body size、CORS、可信代理头、request_id、错误包装、未知字段策略和旧路径兼容。
- DTO/schema：字段 presence、默认值、null/空值、只读字段、枚举、时间/金额精度、未知字段、版本兼容和错误文案。
- Service/Domain：业务不变量、状态机、权限、幂等、并发、补偿、副作用顺序、旧数据和不可逆操作。
- Repository/Client：WHERE 条件、租户/owner/version/soft delete、RowsAffected、连接池、超时、重试、事务范围和资源释放。
- DB/Cache/MQ：迁移前后兼容、回填、唯一约束、TTL、缓存失效、outbox、消费者幂等、DLQ、重放和积压告警。
- Observability：结构化日志、trace 串联、错误率/延迟/饱和度/队列积压指标、告警阈值、敏感字段过滤和排障样本。
- Deploy：环境变量、Secret、镜像 digest、健康检查、readiness、迁移顺序、灰度指标、回滚路径和回滚后数据语义。
- 验收：至少覆盖正常、权限、边界、空值、重复提交、依赖失败、并发、旧客户端、错误响应、观测证据；不能只用一条 happy path。

## 场景执行卡

### 1. 服务入口、路由与中间件
- 先查：启动命令、main/app factory、路由注册、base path、反向代理、网关、HTTP/2/HTTP/3、gRPC gateway、中间件顺序、静态资源/管理端口、可信代理列表。
- 必做：鉴权、租户、限流、CORS、body size、request_id、recover、错误映射放在正确层；入口只做协议转换和校验；X-Forwarded-*、Forwarded、Host、真实 IP、scheme 只能来自可信网关。
- 验证：旧路径、前缀、OPTIONS、异常体、超大 body、未登录/无权限、伪造转发头、健康检查路径。

### 2. API 主链路与服务分层
- 先查：Handler、DTO/schema、Service、Repository/Client、调用方、响应消费方、错误码兼容、版本策略、SDK/移动端旧版本、第三方集成、Webhook 客户端。
- 必做：协议字段与领域模型分离；业务错误和基础设施错误分类；生产不泄露堆栈、SQL、内部路径、依赖地址；对外字段、错误码、分页/排序、幂等语义、Webhook/SDK 行为有兼容策略；破坏性变更必须有版本、灰度、弃用窗口和消费方迁移证据。
- 验证：正常、空值、越界、字段缺省、异常响应、幂等重复请求、旧 SDK/移动端、第三方回调、Webhook 重放、错误码重试语义、分页游标、未知字段容忍。

### 2.1 字段主链路补全门禁
- 改任意请求或响应字段时，必须沿请求 DTO/schema → 校验/默认值 → mapper/assembler → Service/Domain 命令对象 → Repository/DAO → DB 列/JSON 字段/索引 → 响应 DTO/schema → 调用方消费方逐层核对，禁止只改 Handler 或只改表字段。
- 请求 DTO 必须和持久化实体分离；禁止请求体直绑实体、ORM model、DB row、内部 domain aggregate，尤其禁止让客户端提交 owner_id、tenant_id、status、deleted_at、version、created_by、role、price、balance 等服务端裁决字段。
- mapper 必须显式处理新增、重命名、废弃字段；不能靠同名反射/BeanUtils/AutoMapper 悄悄吞字段；nullable、zero value、空字符串、空数组、空对象和字段缺省要有清晰语义。
- Service 层必须承接业务不变量、权限、租户、状态机、幂等和副作用编排；Repository 只表达持久化意图，不承接外部协议字段语义。
- Repository/SQL/ORM 写入必须检查受影响对象、WHERE 条件、租户/owner 过滤、软删条件、乐观锁 version、唯一约束和事务边界；批量更新必须有影响面预览或上限。
- DB 变更必须核对列类型、默认值、NOT NULL、回填、索引、唯一约束、JSON schema、旧数据、读写双版本兼容和回滚后字段语义。
- 响应 DTO 必须显式决定是否回显新增字段、脱敏字段、计算字段、服务端默认值和过期字段；禁止把内部实体原样序列化给外部客户端。
- 验证必须覆盖：字段缺省、字段为 null、字段为空值、字段非法、未知字段、只读字段伪造、旧客户端无字段、新客户端读旧数据、DB 默认值、mapper 漏映射、响应字段兼容。

### 2.2 PUT/PATCH 三态更新门禁
- PUT 按整体替换语义处理：请求 DTO 中缺失的可写字段是否保留、清空或按默认值重建，必须由契约明确；不能把 PATCH 局部更新逻辑伪装成 PUT。
- PATCH 必须支持三态：字段缺省表示不变，字段显式 null 表示清空或按契约拒绝，字段有值表示更新；布尔 false、数字 0、空字符串、空数组不能被误判为缺省。
- PATCH DTO 必须能表达字段是否出现；语言或框架默认反序列化丢失 presence 信息时，要使用 pointer/Optional/FieldMask/JSON Patch/Merge Patch 或等价机制。
- PATCH 更新前必须读取当前对象或使用带条件的原子更新，合并后再次校验业务不变量；禁止用空值覆盖整行，也禁止绕过状态机直接改 DB 字段。
- PUT/PATCH 都必须检查 affected rows：0 行要区分不存在、无权限、租户不匹配、软删、版本冲突、条件不满足和幂等无变化；多于 1 行必须按严重缺陷处理并停止。
- 并发更新必须明确乐观锁/version、updated_at 条件、幂等键或唯一约束；响应要说明最终状态、冲突错误码和客户端重试语义。
- 验证必须覆盖：PATCH 缺省不变、PATCH null 清空/拒绝、PATCH false/0/空字符串有效、PUT 替换语义、并发冲突、affected rows 为 0、多租户条件不匹配、旧字段废弃。

### 2.3 删除链路门禁
- 删除必须先判定硬删、软删、归档、匿名化、取消关联或状态流转；选择依据要来自业务不变量、审计、恢复、合规、下游消费和回滚要求。
- 删除请求必须走鉴权、租户/owner、资源归属、状态机、幂等和依赖检查；禁止只按 id 删除，禁止跳过服务层直接 repository delete。
- 软删必须统一所有读取链路、列表计数、唯一约束、索引、搜索、缓存、导出、报表、后台任务和事件消费的过滤语义；恢复路径要校验唯一冲突和状态合法性。
- 硬删必须先核对外键、审计日志、备份恢复、对象存储、搜索索引、缓存 key、事件 outbox、下游副本和异步任务；不可逆删除要有权限门槛和审计证据。
- 删除操作必须检查 affected rows：0 行要按幂等成功、404、403 或冲突由契约明确；多行删除必须有批量权限逐项校验、上限和审计。
- 删除后必须处理过期对象：缓存 key、列表缓存、计数缓存、权限缓存、搜索索引、推荐索引、事件订阅、队列任务、定时任务、对象存储文件和 CDN/边缘缓存。
- 验证必须覆盖：重复删除、删除不存在、删除无权限、删除软删对象、删除有关联对象、删除后列表/详情/搜索/缓存不可见、事件重复投递、回滚或恢复。

### 3. 架构、领域边界和复杂度预算
- 先查：业务不变量、状态机、聚合/模块边界、读写路径、同步/异步边界、团队拥有者、发布频率、SLO、数据归属和历史耦合。
- 必做：优先保持简单可验证；拆服务/加队列/加缓存/加锁必须有明确瓶颈、故障隔离或交付边界；跨边界只共享契约，不共享数据库内部实现。
- 验证：核心不变量、非法状态、跨模块调用、旧数据、降级路径、回滚后兼容、单体/服务拆分前后的观测和告警。

### 4. 认证授权、租户和资源归属
- 先查：JWT/OIDC/session、issuer/audience、JWK 轮换、token claim、角色、租户、资源 owner、批量操作、后台任务身份。
- 必做：服务端强制鉴权和逐资源授权；只鉴登录不等于授权；批量操作逐项校验；后台任务和系统账号也要有租户/权限边界；401/403/404 语义兼顾安全和契约。
- 验证：过期 token、旧 token、角色切换、跨租户、IDOR/BOLA、批量混入、Webhook 回放。

### 5. 配置、密钥、运行时差异和平台差异
- 先查：env、配置文件、配置中心、Secret Manager、Kubernetes Secret/ConfigMap、Docker env、CI/CD 注入、默认值、启动顺序。
- 必做：关键配置缺失拒绝启动；密钥按最小权限和轮换窗口管理；本地默认值不得进入生产；配置变更绑定发布和回滚。
- 验证：dev/staging/prod 差异、缺配置启动、Secret 轮换、配置漂移、旧容器滚动期间双版本兼容。

### 6. DB、事务、锁和一致性
- 先查：事务边界、隔离级别、索引、唯一约束、外键/软删、状态机、旧数据、慢查询、锁等待、连接池。
- 必做：事务只包本地原子写；先落库再投递事件；金额用整数或 Decimal；幂等键和唯一约束兜底；锁有超时和释放路径。
- 验证：重复提交、并发扣减、死锁、锁超时、非法状态跳转、回滚失败、迁移前后兼容。

### 7. Redis/缓存
- 先查：缓存模式、key 设计、TTL、序列化、标签基数、热点 key、穿透/击穿/雪崩、失效策略、权限边界。
- 必做：Cache-Aside 明确一致性窗口；TTL 抖动；互斥回源；负缓存；缓存 key 带租户/版本；故障时有降级或限流。
- 验证：hit/miss、Redis 故障、热点并发、过期风暴、旧 schema 反序列化、跨租户串数据。

### 8. MQ、队列、事件、后台任务和批处理
- 先查：topic/queue、消费组、投递语义、ACK 时机、DLQ、重试间隔、顺序键、任务调度、多实例、幂等键、批处理分页/游标、长任务资源预算。
- 必做：消费者幂等；成功持久化后 ACK；失败分类进入重试或 DLQ；任务有锁、超时、告警、graceful shutdown；批处理/长任务有游标、断点续跑、租户公平性、限速、进度、取消、资源隔离和重入保护；补偿脚本必须 dry-run、限量、审计和回滚。
- 验证：重复投递、乱序、积压、消费者重启、锁竞争、任务超时、DLQ 重放、部署期间信号终止、百万级分页、任务中断续跑、重复执行、取消、限速、单租户热点、脚本 dry-run 与真实执行差异。

### 9. 容器、Kubernetes、serverless、edge runtime、多区域和时间语义
- 先查：镜像基础层、入口脚本、UID/GID、只读文件系统、资源限制、probe、HPA、PodDisruptionBudget、云函数限制、edge runtime API 限制、AZ/区域、RPO/RTO、故障切换、时区/DST、clock skew、全局 ID、DNS/证书、云托管维护窗口。
- 必做：非 root、最小权限、SIGTERM 优雅停机、startup/readiness/liveness 分离；冷启动和连接复用；edge/serverless 不依赖本地持久文件或长连接假设；时间、ID、调度和灾备语义要写入验证计划。
- 验证：滚动更新、冷启动、OOMKilled、CPU throttling、探针误杀、DNS/证书、只读 FS、并发实例放大连接数、单 AZ 故障、跨区延迟、时钟漂移、定时任务重复/跳过、灾备切换、恢复后幂等重放。

### 10. 日志、指标、trace 和健康检查
- 先查：结构化日志字段、request_id/trace_id、OpenTelemetry SDK/Collector、采样、metrics 标签、告警、dashboard、探针路径。
- 必做：日志脱敏；trace 串联入口、DB、Cache、MQ、外部 HTTP/gRPC；metrics 覆盖 QPS、延迟、错误率、饱和度、积压；liveness 不查慢依赖，readiness 查关键就绪。
- 验证：异常请求可按 trace 定位、指标能触发告警、标签基数可控、Collector 故障不阻断主链路、probe 结果符合流量接入预期。

### 11. 数据生命周期、隐私和审计
- 先查：PII/敏感字段、保留期限、删除/匿名化、导出、备份、审计日志、加密、访问角色、数据跨境/多租户边界。
- 必做：最小化采集；敏感字段加密或脱敏；删除和导出可追踪；审计日志防篡改且不记录 Secret；备份恢复要验证。
- 验证：用户删除、租户隔离、审计查询、备份恢复、密钥轮换、日志/trace/metrics 不含敏感明文。

### 12. 发布、回滚、性能、容量成本和供应链
- 先查：构建产物、lockfile、镜像 digest、SBOM、签名、CVE、迁移顺序、灰度策略、回滚兼容、profile/metrics baseline、容量上限、云/第三方配额、对象存储增长、队列积压、DB/Redis/MQ 费用、日志/trace 采样成本、限流合同。
- 必做：迁移向前兼容；发布前冒烟不替代主链路验收；回滚不丢数据且明确回滚后新字段/新事件/新任务语义；依赖升级看 breaking changes、许可证、CVE、供应链攻击；性能优化先拿 profile 证据；容量、成本和配额必须有监控或降级边界。
- 验证：构建可复现、CVE 命中版本、SBOM 生成、灰度指标、回滚演练、慢路径 profile、容量和连接池预算、配额告警、成本基线、压测外推、存储生命周期、第三方 429/限额耗尽、回滚后旧版本读取新数据。

## 后端工程核心模式速查（独家）

事务与一致性：

- **transactional outbox pattern**：DB 写业务表 + 写 outbox 表在同事务；后台 worker 读 outbox 发 broker；防止 DB 提交但消息丢失。
- **inbox pattern**：消费侧用 inbox 表 + message_id unique 约束去重；at-least-once → effectively-once。
- **idempotent consumer**：消息处理必须用 dedupe key（message_id/business id）写 DB unique；不能假设 broker 不重投。
- **saga**：跨服务长事务用补偿；orchestration（中央 coordinator state machine）vs choreography（事件链）；每步补偿要可重试 + 幂等。
- **event sourcing + CQRS**：写 append-only event log + 物化 read view；event 是不可变 + 有 version；snapshot 减少 replay 开销；CQRS 让读写各自优化。
- **two-phase commit (2PC)** 几乎都避免：性能差 + coordinator 单点；用 saga + outbox 替代。
- 分布式 ACID 不存在：CAP/PACELC + BASE；强一致性走单 leader（Raft/Paxos）；最终一致性 + 业务可容忍。

缓存：

- **cache-aside (lazy loading)**：读时 miss 再查 DB + 回写；最常见；要处理 stale write（先 invalidate cache 再写 DB 防止 race）。
- **read-through**：cache 层主动从 DB 加载（Caffeine / Redis with module）；应用代码不感知 DB。
- **write-through / write-back**：写时同步 / 异步写 DB；write-back 更快但 crash 丢数据。
- **cache stampede**（thundering herd）：热 key 过期时大量并发请求同时 miss + 查 DB 打爆；解决：mutex / single-flight（一个 fetch 其他等）/ probabilistic early expiration / 永不过期 + 后台刷新。
- **TTL jitter**：所有同类 key 设同样 TTL 会同时过期；加 random jitter（±10%）分散。
- **cache invalidation** 两难（Phil Karlton：CS 两件最难事之一）：write-after-cache vs cache-after-write 都有 race；用 versioned key 或 event-driven invalidation。
- **negative cache**：缓存 "not found" 防穿透；TTL 短（5-30s）。
- **bloom filter**：先查 bloom 再查 cache，0 false negative 防穿透；接受 false positive。

并发与限流：

- **distributed lock**：单 Redis 用 `SET NX EX`；多 Redis 用 **Redlock 算法**（仍有争议，仅作 advisory lock）；强一致用 etcd/Consul/ZooKeeper（基于 Raft）。
- **leader election**：多实例选主跑 cron/scheduler；etcd lease / ZooKeeper ephemeral node / Redis SET NX + heartbeat。
- **rate limit 算法**：fixed window（边界冲击）、sliding window（精确）、**token bucket**（允许突发）、**leaky bucket**（平滑输出）；分布式用 Redis script (Lua) 或 Envoy ratelimit。
- **circuit breaker**（resilience4j / Polly / sentinel）：3 态 closed/open/half-open；失败率/慢调用比例触发 open；half-open 试探恢复；防 cascading failure。
- **bulkhead**：隔离资源池（thread pool / connection pool）防一个 slow 依赖拖垮整个服务。
- **backpressure**：消费速度 < 生产时反向施压；Reactive Streams / TCP window / bounded channel；防 OOM。
- **connection pool**：DB / HTTP / Redis 都有上限；过大耗光下游、过小造成 wait；按下游能力 + 实例数算（HikariCP / PgBouncer / database-pool-sizing rules）。

队列与消息：

- **at-least-once 是默认**：所有 broker (Kafka/RabbitMQ/SQS/NATS) 都不保证 exactly-once；消费侧必须幂等设计。
- **ordering** 通常只在 partition / queue 内保证；跨 partition 无序；ordering-critical 走单 partition + 牺牲并行。
- **DLQ + retry policy**：N 次重试失败进 DLQ + 监控 + 重放工具；区分 transient（重试）和 poison（DLQ）。
- **priority queue**：紧急消息优先（Sidekiq 多 queue + worker，RabbitMQ priority queue 受限于 prefetch）。
- **fan-out / fan-in**：一对多发布（pub/sub）、多对一聚合（worker 写 result store + coordinator 收集）。
- **scheduled job vs cron**：cron 跑在固定时间（leader-elected 防多实例同时跑）；scheduled job 是延迟队列（Sidekiq scheduled set / SQS delay / Quartz scheduler）。

配置 / 12-factor / 部署：

- **12-factor app**：env config / 无状态进程 / 端口绑定 / 并发进程模型 / 快速启动+优雅停机 / dev-prod parity / 日志 stream / 一次性 admin 进程。
- **config from env**：app 启动时校验 env schema（fail-fast）；不要 fallback 默认值掩盖缺配；密钥从 secret manager 注入。
- **graceful shutdown**：SIGTERM 后停止接新请求 + drain 进行中 + close DB/queue + 退出 zero；K8s preStop hook + terminationGracePeriodSeconds。
- **health check** 分层：**liveness**（进程活着）/ **readiness**（能服务流量）/ **startup**（启动期 grace）；K8s 三个 probe 各自语义；liveness 失败 K8s 重启 pod。
- **rolling deploy / blue-green / canary**：rolling 是 K8s 默认；blue-green 双环境切换；canary 按比例放流量 + observability 自动 promote/rollback。

可观测：

- **三大支柱**：metrics（Prometheus）、logs（structured JSON + Loki/ELK）、traces（Jaeger/Tempo）；**OpenTelemetry** 是统一 SDK + protocol。
- **structured logging**：key=value / JSON 字段；包含 trace_id / request_id / user_id / tenant_id；不打 token/PII。
- **RED metrics**：Rate（QPS）、Errors（错误率）、Duration（latency p50/p95/p99）；服务级 SLO。
- **USE metrics**：Utilization、Saturation、Errors；资源级（CPU/memory/disk）。
- **distributed tracing**：每请求 trace_id + 跨服务 traceparent header（W3C TraceContext）；span 标 service.name + db.statement + http.status。
- **error budget** + **SLO/SLI**：用户体验承诺；超 burn rate 阈值告警；季度 SLO 不达回滚释放节奏。

## 高频坑 / 防遗漏

- 改入口：查启动脚本、容器 CMD/ENTRYPOINT、进程管理、端口、路由前缀、网关、probe、反向代理转发头。
- 改中间件：查顺序、短路条件、异常处理、body 读取次数、流式响应、CORS、鉴权和限流互相影响。
- 改 API/SDK：查旧客户端、第三方回调、错误码重试语义、未知字段容忍、版本/弃用窗口和消费方迁移证据。
- 改字段：查请求 DTO、mapper、Service 命令对象、Repository 写入、DB 列/索引、响应 DTO、缓存对象、事件 payload、搜索索引、旧客户端和后台任务。
- 改领域逻辑：查业务不变量、状态机、聚合边界、不可逆副作用、旧数据和非法状态转移。
- 改 PUT/PATCH：查字段 presence、null/缺省/空值三态、整体替换和局部更新边界、乐观锁、affected rows、幂等无变化和冲突错误码。
- 改删除：查软删/硬删/归档/匿名化语义、关联对象、唯一约束、读取过滤、缓存和索引过期、事件重复投递、恢复路径和审计。
- 改配置：查默认值、环境变量名、配置中心、Secret 注入、镜像变量、部署模板、回滚版本和配置漂移。
- 改连接池：查每实例连接数、HPA 最大副本、serverless 并发、数据库 max_connections、空闲回收、DNS/TLS keepalive。
- 改超时/重试：查调用方总预算、幂等性、退避抖动、熔断恢复、任务重试和队列重试是否叠加。
- 改事务/锁：查外部 I/O、隔离级别、死锁顺序、唯一约束、锁超时、补偿任务和状态机终态。
- 改缓存：查租户维度、TTL 抖动、热点 key、负缓存、旧 schema、删除/更新顺序和缓存预热。
- 改队列/任务：查 ACK、DLQ、消费组、顺序键、重复消息、积压告警、重放脚本、消费者版本兼容、游标、断点续跑、dry-run、限量和审计。
- 改健康检查：查 startup/readiness/liveness 分工、超时时间、慢依赖、管理端口、网关健康路径和滚动更新行为。
- 改观测：查 trace_id 贯穿、日志脱敏、metrics 标签基数、采样率、Collector 出口、告警阈值和 dashboard。
- 改数据隐私：查保留/删除/导出、审计日志、备份恢复、加密、访问角色、跨租户和日志/trace/metrics 明文风险。
- 改部署：查镜像 digest、资源 requests/limits、PDB、HPA、Secret、SBOM、签名、CVE、灰度和回滚。
- 改多区域/时间：查 AZ/区域、RPO/RTO、故障切换、时区/DST、clock skew、全局 ID、定时任务重复/跳过。
- 改容量/成本：查 DB/Redis/MQ/对象存储/第三方 API 配额、速率限制、日志/trace 成本、队列积压和告警。
- 改性能：先确定 baseline、profile、慢查询、连接池、锁等待、GC、CPU throttling；禁凭感觉调并发。

## 输出要求

1. 场景卡：命中的后端主场景和相邻场景。
2. 现场证据：运行时、平台差异、入口、路由/中间件、配置/密钥来源、依赖版本、复现样本、日志/指标/trace、DB/Redis/MQ/K8s 证据；缺失必须列明。
3. 影响层级：Handler、Middleware、Service、Domain、Repository、Client、DB、Cache、MQ、Task、Container、Deploy、Observability。
4. 风险点：鉴权授权、租户隔离、业务不变量、幂等、事务一致性、锁、并发、超时、重试、熔断、配置传播、连接池预算、消费方兼容、数据生命周期、灾备/时间语义、容量/成本、回滚、安全/供应链。
5. 验证方案：必须区分单元、集成、契约、迁移、并发、故障注入、回放/补偿、部署/回滚、观测告警；覆盖正常、边界、异常、权限、依赖失败；标明已验证/未验证和命令产出；只跑冒烟不得声称主链路已验证。
6. 交付证据：改动文件行号、配置/脚本/路由/迁移/监控改动、测试或构建输出、未覆盖原因、上线前检查项。
7. 联动技能：API 契约、DB、Web 安全、可观测性/SRE、发布、性能、云原生、DevSecOps、测试、审计是否已读取；未读取不能声称遵守。

## 约束

- 本技能只处理后端工程现场事实、链路排障和交付验证；不替代 api 的契约设计、db 的表/迁移设计、wsec 的专项安全审计。
- 未读入口、配置、依赖、调用方、消费方、部署和观测证据，不得下“已完成/已验证/可上线”结论。
- 证据不足先不改；连续两次修复无效必须停下复盘运行时、入口、配置、依赖和复现假设。
- 禁止为“架构更高级”无证据引入微服务、缓存、队列、service mesh、serverless、复杂中间件或全局重构。
- 外部输入默认不可信；鉴权、资源归属、租户隔离、批量逐项验权必须在服务端完成。
- 外部依赖必须有超时、取消传播、失败分类和隔离；重试必须受幂等、预算、退避、熔断约束。
- 事务内禁止外部 HTTP/RPC/MQ；跨资源一致性用 outbox、补偿、幂等和可观测重放，不用长事务幻想。
- 生产错误、日志、metrics、trace 不得泄露 Secret、token、Cookie、PII、SQL、内部路径和供应商凭据。
- 发布前必须有健康检查、监控告警、灰度/回滚、迁移兼容、配置/密钥和依赖故障预案。
- 数据保留、删除、导出、审计、备份恢复、加密、跨租户/跨境边界缺证据时必须标“需验证”，不得假设已合规。
- 涉测试/回归按 tst 收口；任何代码改动完成前按 aud 收口。

## 高频 Bug 反例库

- 反例 1：配置默认值掩盖生产缺失
  - 错法：生产缺 DB_URL、SECRET_KEY、OIDC_ISSUER 时自动使用本地默认值启动。
  - 对法：关键配置启动期校验，生产缺失直接失败；默认值只允许本地并在日志标识。
  - 根因：把开发便利当生产容错，运行时配置来源和环境边界未被证据化。
- 反例 2：服务入口和实际容器命令不一致
  - 错法：只改本地 npm start 或 main 函数，线上 Docker ENTRYPOINT 仍跑旧 worker 或旧端口。
  - 对法：同时核对 Procfile、Dockerfile、K8s command/args、进程列表、端口和启动日志。
  - 根因：未确认真实运行入口，把源码入口误认为生产入口。
- 反例 3：中间件顺序导致鉴权绕过
  - 错法：路由先挂公开组，再挂 auth middleware，部分管理接口未经过鉴权。
  - 对法：按路由树核对中间件顺序，对敏感路由加服务端资源归属检查和测试。
  - 根因：只看单个 Handler，没验证路由注册、分组和短路逻辑。
- 反例 4：连接池按单实例估算
  - 错法：每个 Pod 配 100 个 DB 连接，HPA 到 30 副本后打满数据库 max_connections。
  - 对法：按副本上限、serverless 并发、后台任务和迁移脚本统一计算连接预算。
  - 根因：忽略平台扩缩容和多进程模型，连接池缺少全局容量约束。
- 反例 5：重试无退避和幂等前提
  - 错法：下游 5xx 立即循环重试 POST 创建订单，造成重复写和故障放大。
  - 对法：只对幂等操作或带幂等键请求重试，设置指数退避、抖动、上限、熔断和总预算。
  - 根因：把重试当可靠性万能药，未区分错误类型、幂等性和调用链 SLO。
- 反例 6：事务内调用外部服务
  - 错法：DB 事务未提交时调用支付、HTTP、MQ，超时后锁长时间占用且外部副作用不可回滚。
  - 对法：事务内只写本地状态和 outbox，提交后异步投递，失败由补偿和幂等重放处理。
  - 根因：混淆本地 ACID 和分布式副作用，事务边界设计错误。
- 反例 7：队列消费 ACK 过早
  - 错法：收到消息立即 ACK，再写 DB，写失败后消息丢失且无 DLQ。
  - 对法：业务持久化成功后 ACK；失败按可重试/不可重试分类进入重试或 DLQ；消费者幂等。
  - 根因：未理解消息投递语义和失败窗口，缺少重放证据。
- 反例 8：缓存 key 缺租户和版本
  - 错法：用 user:{id} 缓存资料，多租户或 schema 升级后串数据/反序列化失败。
  - 对法：key 包含租户、业务版本和必要权限维度，旧 schema 兼容或批量失效。
  - 根因：缓存被当作透明加速层，忽略权限边界和数据演进。
- 反例 9：Kubernetes liveness 查慢依赖
  - 错法：liveness 每次查询 DB/外部 HTTP，依赖抖动时 kubelet 反复杀 Pod。
  - 对法：liveness 只证明进程可恢复，readiness/startup 用短超时检查关键就绪。
  - 根因：混淆存活、启动和接流量语义，probe 设计未结合滚动更新。
- 反例 10：日志和 trace 泄露密钥
  - 错法：把 Authorization、Cookie、手机号、支付参数、连接串完整写入日志和 span attribute。
  - 对法：字段白名单、脱敏、采样控制、敏感 attribute 过滤和日志平台访问控制。
  - 根因：观测数据被当成内部安全区，未按生产数据治理处理。
- 反例 11：OpenTelemetry Collector 故障阻断主链路
  - 错法：同步导出 trace，Collector 慢或不可用时请求延迟暴涨。
  - 对法：异步批量导出、超时和丢弃策略，Collector 故障只降级观测不阻断业务。
  - 根因：把观测依赖放进请求关键路径，缺少 backpressure 和失败预算。
- 反例 12：serverless/edge runtime 依赖本地状态
  - 错法：在 /tmp 或进程内缓存保存会话、锁或队列 offset，实例回收后状态丢失。
  - 对法：状态放外部持久服务；冷启动、并发实例和 edge runtime API 限制单独验证。
  - 根因：沿用长驻容器假设，忽略无状态和运行时 API 差异。
- 反例 13：供应链只看直接依赖版本
  - 错法：升级框架后不检查传递依赖、镜像基础层、构建插件、许可证和签名。
  - 对法：生成 SBOM，扫描 CVE，核对 lockfile、镜像 digest、签名/SLSA provenance 和 breaking changes。
  - 根因：把依赖治理局限在 package.json/go.mod，忽略构建链和镜像层。
- 反例 14：批处理补偿脚本无保护
  - 错法：线上一次性全量修数据，无 dry-run、无限量、无审计、无断点，失败后无法判断影响面。
  - 对法：先 SELECT/预览影响面，分批限量执行，记录审计和游标，支持暂停、回滚或幂等重跑。
  - 根因：把后台修复当一次性手工操作，缺少任务治理和运维可重复性。
- 反例 15：新增字段只改请求体和表
  - 错法：Controller 接收了新字段，DB 也加了列，但 mapper、Service 命令对象、Repository 更新列表、响应 DTO、缓存对象、事件 payload 和索引文档都没补。
  - 对法：按请求 DTO → mapper → Service → Repository → DB → 响应 DTO → 缓存/事件/索引/消费方逐层对账，并补旧数据、旧客户端和默认值验证。
  - 根因：把字段当局部变量，没把字段生命周期当跨层契约。
- 反例 16：请求体直绑实体导致越权写字段
  - 错法：把 JSON 请求直接 bind 到 ORM entity，客户端能提交 tenant_id、owner_id、status、deleted_at、role 或 balance 覆盖服务端裁决字段。
  - 对法：外部请求只进入请求 DTO，服务端从认证上下文和业务规则填充裁决字段，mapper 白名单映射可写字段。
  - 根因：混淆外部协议模型和内部持久化模型，缺少字段级写权限。
- 反例 17：PATCH 缺省和 null 混淆
  - 错法：PATCH DTO 无法区分字段未传、显式 null、false、0、空字符串，导致局部更新误清空或无法清空。
  - 对法：使用能表达 presence 的 DTO，并定义三态语义；缺省不变，null 清空或拒绝，有值更新，false/0/空字符串按有效值处理。
  - 根因：沿用 create/update 共享 DTO，忽略 PATCH 的字段存在性。
- 反例 18：更新不检查 affected rows
  - 错法：UPDATE/DELETE 执行后直接返回成功，WHERE 中租户、owner、version 或 soft delete 条件不匹配时仍声称已改。
  - 对法：必须检查 affected rows，0 行区分不存在、无权限、版本冲突、条件不满足和幂等无变化，多于 1 行立即按严重缺陷处理。
  - 根因：把 SQL 执行成功当业务成功，未验证目标对象真的被修改。
- 反例 19：删除后缓存和索引仍暴露对象
  - 错法：DB 软删成功，但详情缓存、列表缓存、搜索索引、推荐索引、事件订阅、对象存储文件和 CDN 仍返回旧对象。
  - 对法：删除链路必须列出并处理过期对象，落库后通过事务 outbox 或可靠任务失效缓存、索引和下游副本，重复执行保持幂等。
  - 根因：把删除视为单表写入，忽略读取副本和异步投影。
- 反例 20：用前端权限当后端权限
  - 错法：菜单隐藏了删除按钮，后端只校验登录态，攻击者直接请求接口就能跨租户删除。
  - 对法：服务端按资源 owner、tenant、role、状态机和批量逐项权限校验，前端只做体验优化。
  - 根因：把 UI 展示误当安全边界，缺少对象级授权证据。
- 反例 21：可信 header 被任意客户端伪造
  - 错法：直接信任 X-Forwarded-For、X-User-Id、X-Tenant-Id、Host 或 scheme 做限流、审计、回调地址和租户选择。
  - 对法：只信任来自白名单网关/mesh 的转发头，身份和租户从服务端认证上下文派生。
  - 根因：混淆网关内部协议和公网请求，入口 trust boundary 未定义。
- 反例 22：catch 异常后返回成功
  - 错法：发送 MQ、写缓存或调用下游失败后 catch 只记录日志，接口仍返回成功，后续数据永久不一致。
  - 对法：按关键性决定失败、降级、补偿或 outbox 重试；对外响应必须反映真实业务状态和重试语义。
  - 根因：把“不中断用户体验”误解为吞掉失败，缺少副作用一致性设计。
- 反例 23：无超时调用拖垮线程池
  - 错法：HTTP/gRPC/Redis/对象存储客户端使用默认无限等待，下游卡住后请求线程、连接池和队列全部耗尽。
  - 对法：设置连接、读写、整体 deadline 和取消传播；隔离核心/非核心依赖并配置熔断和限流。
  - 根因：只验证正常响应，未把依赖抖动当一等失败路径。
- 反例 24：非幂等重试导致重复副作用
  - 错法：超时后自动重试创建订单、扣库存、发券、发短信或投递事件，用户收到重复资源。
  - 对法：非幂等操作必须有幂等键、唯一约束、状态机或去重表；重试前定义错误类型和总预算。
  - 根因：把网络重试当可靠性保障，未处理“请求已成功但响应丢失”的窗口。
- 反例 25：只跑冒烟就报主链路通过
  - 错法：只 curl 一个 200 或跑一次本地启动，就声称订单、队列、缓存、权限、回滚全部可用。
  - 对法：按链路矩阵补正常、异常、权限、重复提交、依赖失败、并发、旧客户端、观测和回滚证据。
  - 根因：把服务可启动当业务可交付，验证面没有覆盖真实失败模式。
- 反例 26：灰度无法判断是否该回滚
  - 错法：只按副本比例发布，没有错误率、延迟、业务成功率、队列积压、DB 锁等待和日志异常阈值。
  - 对法：发布前定义灰度指标、暂停条件、回滚命令、数据兼容和监控看板，发布后按指标推进。
  - 根因：把灰度当流量开关，缺少可判断的工程证据。
- 反例 27：任务/队列没有幂等和重放边界
  - 错法：消费者按消息到达顺序直接写状态，重启、乱序、重复投递或 DLQ 重放后覆盖新状态。
  - 对法：消费者用业务幂等键、状态机版本、去重记录和可观测重放脚本，DLQ 重放前先预览影响面。
  - 根因：只在单次消费成功路径验证，没有验证消息系统的真实投递语义。
- 反例 28：错误语义让客户端误重试
  - 错法：参数错误、无权限、库存不足、下游超时和未知异常都返回同一个成功体或 500。
  - 对法：错误分类要映射到稳定状态码/错误码/重试建议，生产响应不泄露内部细节但保留排障 ID。
  - 根因：错误处理被当成格式包装，未作为客户端协作契约设计。

## 提交前自检清单

- [ ] 已确认运行时、入口命令、路由/中间件、配置/密钥来源、依赖版本和部署形态。
- [ ] 已全量追踪调用方、消费方、配置 key、缓存 key、队列 topic、任务名、健康检查路径。
- [ ] 已对新增/修改字段逐层追踪请求 DTO、校验、mapper、Service/Domain、Repository、DB、响应 DTO、缓存、事件、索引和消费方。
- [ ] 已确认 PUT/PATCH 语义：PUT 整体替换边界清晰，PATCH 能区分缺省/null/有效空值三态，false/0/空字符串不会被误判。
- [ ] 已确认写操作和删除操作检查 affected rows，并区分不存在、无权限、租户不匹配、软删、版本冲突、条件不满足、幂等无变化和异常多行。
- [ ] 已确认删除链路覆盖软删/硬删/归档/匿名化语义、关联对象、缓存/事件/索引/CDN/对象存储过期对象、恢复路径和审计证据。
- [ ] 已识别业务不变量、状态机、领域边界、数据生命周期、隐私/审计要求和旧客户端/第三方消费方兼容。
- [ ] 已覆盖鉴权授权、租户隔离、错误映射、日志脱敏和生产错误不泄露内部细节。
- [ ] 已检查连接池预算、超时、取消传播、重试退避、熔断、限流和依赖失败路径。
- [ ] 已检查事务边界、锁、幂等、唯一约束、状态机、补偿和队列重复投递。
- [ ] 已确认可信代理头、Host、scheme、真实 IP、用户/租户 header 不可被公网请求伪造。
- [ ] 已确认所有 catch/降级/补偿路径不会把失败伪装成业务成功。
- [ ] 已检查缓存一致性、TTL、热点、穿透/击穿/雪崩、租户维度和旧 schema。
- [ ] 已检查容器非 root、资源限制、graceful shutdown、Kubernetes probe、serverless/edge runtime 差异。
- [ ] 已检查多区域/灾备/时间语义、容量/成本/配额、长任务/补偿脚本的 dry-run、限量、审计和回滚。
- [ ] 已检查日志、指标、trace、OpenTelemetry、告警和健康检查是否能支撑排障。
- [ ] 已检查 SBOM、CVE、签名/来源、镜像 digest、Secret、灰度、回滚和迁移兼容。
- [ ] 已验证旧客户端、旧 SDK、第三方回调、队列消费者和后台任务对新字段/新错误/新状态的兼容。
- [ ] 已给出测试/构建/验证命令产出；未验证项已标明原因；代码改动已走 tst 和 aud。

## 2024-2026 新坑速查

- OpenTelemetry 语义约定和 SDK/Collector 版本变化会影响 span name、attribute、metrics 名称和采样；升级前后要比对 dashboard/alert 查询。
- OTLP 默认协议、压缩、批量导出和 Collector pipeline 变化可能让 trace 丢失或延迟暴涨；业务线程不得同步等待导出。
- Kubernetes 1.28-1.34 周期内 sidecar containers、probe 行为、资源指标、gateway/service mesh 集成持续演进；不要用旧模板套新集群。
- Kubernetes startupProbe/readiness/liveness 配错会在滚动更新、冷启动、慢迁移时放大故障；探针要绑定真实接流量条件。
- HTTP/3、gRPC、proxy protocol、X-Forwarded-*、Forwarded headers 在网关/CDN/mesh 后语义不同；鉴权、限流和真实 IP 不能猜。
- serverless 和 edge runtime 常限制 TCP 长连接、本地文件、后台线程、执行时长、Node/Python 标准库；连接池和缓存策略要按平台重算。
- 容器基础镜像、distroless、非 root、只读文件系统会暴露写临时目录、CA 证书、字体/时区、shell 依赖问题。
- SBOM、SLSA provenance、Sigstore/cosign、npm/pypi token 生命周期和 2FA 政策变化让构建凭据、发布权限、依赖来源成为上线门槛。
- Redis/Kafka/DB 云托管默认 TLS、ACL、连接上限、空闲回收、跨 AZ 延迟和维护窗口会改变本地压测结论。
- AI/LLM、Webhook、支付回调、第三方 SaaS 更常见长尾超时和回放；幂等、签名校验、异步补偿必须落到后端主链路。
- eBPF/continuous profiling 更普及，但 profiling 证据必须和版本、流量、CPU throttling、GC、锁等待一起解释，不能单图下结论。
- 供应链投毒和 typosquatting 更频繁；新增构建插件、GitHub Action、Docker action、下载脚本时要审来源、权限和 pin 到 digest/commit。
- 多区域/灾备常被误认为平台自动兜底；RPO/RTO、故障切换、时钟漂移、全局唯一 ID、跨区延迟和恢复后重放必须单独验证。
- 隐私合规不仅是日志脱敏；数据最小化、保留期限、删除/导出、审计、备份恢复和密钥轮换都要有工程证据。
- 云账单和第三方配额会成为可用性风险；对象存储生命周期、日志/trace 采样、队列积压、API 429 和限额耗尽要纳入告警。

## 与相邻技能的边界

- API 工程/api-engineering（api）：负责 API 契约、资源模型、状态码、版本、兼容和认证语义；后端工程/backend-engineering（be） 负责契约在路由/中间件/服务分层中的落地证据。
- 数据库工程/database-engineering（db）：负责表结构、迁移、索引、SQL、事务模型和数据一致性专项；后端工程/backend-engineering（be） 负责调用链事务边界、连接池、锁等待和运行时影响。
- Web 安全/web-security（wsec）：负责漏洞专项、攻击面、BOLA/IDOR、注入、XSS/CSRF/SSRF 等安全审计；后端工程/backend-engineering（be） 负责默认安全基线和服务端鉴权落地。
- 可观测性/observability（obs）：负责 SLO、告警、事件响应、容量和可观测平台；后端工程/backend-engineering（be） 负责代码链路日志/指标/trace/health 的埋点与排障证据。
- 发布部署/release-engineering（rls）：负责构建、部署、灰度、回滚和发布流程；后端工程/backend-engineering（be） 负责服务入口、配置、迁移兼容和运行时健康条件。
- 性能工程/perf-engineering（pfe）：负责系统性压测、profile、容量模型和性能专项；后端工程/backend-engineering（be） 负责超时、连接池、锁、缓存、队列等性能风险的工程落地。
- 云原生/cloud-native（cld）：负责 Kubernetes、容器、Service Mesh、云原生平台专项；后端工程/backend-engineering（be） 负责后端服务在这些平台上的运行时假设和健康检查证据。
- DevSecOps/devsecops（dso）：负责 CI/CD 安全、SBOM、签名、凭据和供应链治理；后端工程/backend-engineering（be） 负责依赖/镜像/密钥变更对服务运行和交付的影响。
- 测试验证/test-engineering（tst）：负责测试矩阵、自动化、回归和验证可信度；后端工程/backend-engineering（be） 提供后端风险场景和复现证据。
- 代码审计/code-audit（aud）：负责最终需求对账、影响面、安全质量和证据收口；后端工程/backend-engineering（be） 完成修改后必须交由其复盘。