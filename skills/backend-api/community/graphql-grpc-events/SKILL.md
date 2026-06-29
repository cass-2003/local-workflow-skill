---
name: graphql-grpc-events
description: GraphQL/gRPC/事件契约实战排障版 - 专管 GraphQL schema/resolver/N+1/DataLoader/persisted queries/federation/@defer/@stream，gRPC proto3/buf breaking/grpc-web/deadline/cancellation/status codes，以及 Kafka/Pulsar/NATS/schema registry/outbox/idempotency/DLQ/consumer lag/OpenTelemetry 的契约兼容、真实失败模式和发布回滚证据。
---

# GraphQL/gRPC/事件接口

GraphQL/gRPC/事件接口（graphql-grpc-events，兼容 slug: gge）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

定位：本技能只处理 GraphQL、gRPC、事件流的“协议契约与跨消费者兼容”。目标不是通用 API 模板，而是把 schema/proto/topic 从能跑收敛为可 diff、可回放、可观测、可回滚、可审计。

## 快速总则：契约定制：协议/版本、schema/proto/topic、兼容策略、证据

1. 协议先定制：GraphQL 看 schema、resolver、operation、query plan；gRPC 看 proto3、service、method、stream、metadata、status codes；事件看 topic/subject/key/schema/consumer group。
2. 版本先锁定：记录 GraphQL server/client/federation gateway、protoc/runtime/gencode、buf、grpc-web proxy、Kafka/Pulsar/NATS/broker、schema registry、OpenTelemetry semantic convention 版本。
3. schema/proto/topic 是契约：字段可空性、input/argument、enum、protobuf tag、oneof、topic 分区键、routing key、subject、retention、DLQ、replay 规则都要写入契约，不当实现细节。
4. 兼容策略默认保守：删字段、收紧 nullability、新增 required input、改默认值、改 enum 语义、复用 tag、改 status code、改 topic key、改事件含义、改顺序边界默认 breaking change。
5. 消费者先于实现：前端、App、BFF、SDK、批任务、BI、旧 consumer group、第三方未查清，不得判兼容。
6. 证据闭环：结论绑定 schema diff、proto/buf breaking、registry compatibility、operation 回放、golden sample、consumer-driven contract、trace/log/metric、consumer lag、DLQ 和灰度回滚证据。
7. 性能需场景证据：GraphQL N+1、DataLoader、federation fan-out、gRPC streaming 背压、consumer lag、DLQ 风暴必须用负载、trace 和失败样本验证。
8. 安全默认逐层验：introspection、persisted queries、query batching、alias/fragment、字段级授权、gRPC metadata、topic key、CloudEvents attributes、headers、日志、DLQ 禁止泄露 PII/secret。
9. 发布必须可回退：deprecation、双写/双读、schema/proto/topic 门禁、消费者灰度、DLQ 回灌、replay 开关、回滚点齐全才收口。
10. 治理按风险分级：breaking/high-risk 强制完整消费者矩阵、豁免到期和回滚计划；safe change 也要有最小回放和消费者证据。
11. 分页/游标先成契约：GraphQL connection、gRPC page_token、事件 replay cursor/offset 都要定义稳定排序、过滤条件绑定、过期策略、重复/缺页处理和权限边界。
12. 验收必须真实闭环：压测、旧样本回放、consumer-driven contract、灰度指标、DLQ/replay 演练、回滚或补偿证据缺一项时，不把“已上线”写成“已验收”。

## 强制门禁：先分类，再改契约

- Breaking：删除或重命名字段/method/topic/event type；收紧 GraphQL nullability；给已发布 operation 增 required input；复用 protobuf tag/name；改 enum 语义；改 gRPC status/retry/idempotency；改 partition key、ordering、retention、DLQ 或 replay 副作用。必须有消费者矩阵、迁移窗口、灰度、回滚/roll-forward 和豁免到期。
- High-risk compatible：新增 GraphQL nullable 字段但 resolver 可能 N+1；新增 proto optional 字段但跨语言 presence 未验证；新增事件字段但 registry subject/consumer 未全覆盖；新增 stream、subscription、gateway 转换、DataLoader 缓存、自动 retry、consumer concurrency。必须补负载、旧样本、trace、registry/buf 和真实消费者证据。
- Safe candidate：纯新增可选字段、reserved 后保留旧字段、仅新增新 event type/topic、仅新增观测标签。仍需最小 schema/proto/registry diff、golden sample 和一个旧消费者回放。
- 禁止把“编译通过、单测通过、producer 发出、gateway composition 通过、registry compatible 通过”单独当兼容结论；它们只是证据片段。
- 任何结论必须写明：谁生产、谁消费、旧版本保留多久、如何发现旧消费者、异常时先回滚哪一层。
- 写入前必须有契约门禁记录：diff 类型、消费者矩阵、鉴权/隐私影响、错误码或错误详情、分页/流式语义、幂等/补偿策略、压测范围、发布后验收指标和 owner。

## 低级错拦截清单

- GraphQL：先查 operation registry/client awareness/field usage，再动 schema；resolver 变更先看列表规模、调用放大、授权上下文和缓存 key；mutation 先定义幂等键、错误结构和 missing/null/empty。
- gRPC：先查 proto tag/name/reserved、生成代码语言矩阵、deadline、cancellation、retry、status details、grpc-web/mesh/LB，再改 service/method/message。
- 事件：先查 topic/subject/key、consumer group、registry subject、compatibility level、outbox/CDC、offset commit、DLQ、replay 和 retention，再改 event schema 或消费逻辑。
- 转换层：先查 GraphQL/gRPC/REST/event 的错误、分页、metadata/header、trace、streaming 降级和 retry 映射，再加网关或订阅桥。
- 发布：任何协议契约变更都要有 diff、旧样本回放、灰度指标、rollback/roll-forward、DLQ/replay 止血开关和 owner。

## 场景执行卡

### 1. GraphQL schema / resolver / mutation
- 输入：schema SDL、operationName、query/mutation/subscription、消费者版本、字段敏感性、nullable、enum、auth、cache、deprecation 窗口。
- 动作：公共 schema 按业务契约建模；新增字段优先可选；删除/改名/改类型/收紧 nullability 走 deprecation；mutation 写幂等键、权限和错误结构。
- 验证：schema diff、旧 operation 回放、未知 enum、null/缺失、字段级授权、错误 path、缓存 key、旧客户端兼容。

### 2. GraphQL input / client cache / operation registry
- 输入：operation registry/APQ、客户端名称版本、变量样本、input object、argument 默认值、fragment、normalized cache key、CDN/HTTP cache、上传/订阅能力。
- 动作：新增 input/argument 默认可选；禁止给已发布 operation 增 required input；partial update 区分 missing/null/empty；缓存 key、entity id、fragment owner 和 persisted operation 变更写入契约。
- 验证：旧 operation+旧变量回放、Apollo/Relay cache 读写、APQ/operation registry 命中、GET/POST/CSRF、multipart upload、subscription 重连和授权续期。

### 3. GraphQL pagination / cursor / partial response
- 输入：connection/edge/node、cursor 生成规则、排序字段、过滤条件、权限上下文、page size 上限、totalCount 语义、旧客户端分页样本。
- 动作：cursor 必须不暴露敏感明文且绑定排序/过滤/租户；禁止用不稳定 offset 当跨页契约；增删数据时定义重复、跳页、空页、过期 cursor 和反向分页行为。
- 验证：同过滤多页回放、并发插入/删除、权限变化、cursor 过期、first/after 与 last/before、totalCount 成本、旧客户端缓存合并和部分响应兼容。

### 4. GraphQL N+1 / DataLoader / persisted queries / security
- 输入：resolver 树、列表规模、下游调用数、loader key、租户/权限上下文、query cost、persisted query 清单、batch/alias/fragment/upload 风险。
- 动作：resolver 只编排；列表关联用 DataLoader/batcher；loader 实例请求级，key 含租户、权限、过滤和版本；生产优先 persisted queries + complexity/depth/rate limit；persisted query 不能替代对象/字段级授权。
- 验证：1/10/100 项调用不线性爆炸；trace 有 operationName、field path、resolver latency、batch size、cache hit；非法 batching、alias、fragment cycle、深度查询、上传超限和跨租户访问被阻断。

### 5. GraphQL federation / @defer / @stream / subscription
- 输入：subgraph schema、composition 结果、entity key、owner、query plan、defer/stream 支持矩阵、subscription broker、重连策略。
- 动作：federation 变更先跑 composition；entity key 和 resolver owner 不漂移；@defer/@stream 标明客户端降级；subscription 定义顺序、重放、权限、心跳和鉴权续期。
- 验证：gateway/subgraph 版本矩阵、query plan fan-out、部分响应兼容、断线重连、旧客户端不识别增量响应、subscription 乱序/重复/漏消息、鉴权续期失败、跨 subgraph 授权。

### 6. gRPC proto3 / buf breaking / grpc-web
- 输入：proto package、service/method、message、field tag、oneof、optional、JSON mapping、buf.yaml、跨语言生成代码、grpc-web 网关。
- 动作：tag 发布即冻结；删除字段 reserved name/tag；enum 0 用 UNKNOWN/UNSPECIFIED；presence 用 optional/oneof 明确；CI 接 buf breaking；grpc-web 单独验证 header/trailer/stream 限制。
- 验证：新旧生产者/消费者互读、未知字段、默认值、未知 enum、序列化 golden sample、buf breaking 输出、浏览器代理错误映射。

### 7. gRPC connection / error details / API evolution
- 输入：channel/keepalive、LB/name resolver、mesh/xDS、max message、compression、FieldMask、google.rpc.Status details、pagination/LRO、幂等声明、method 生命周期。
- 动作：method 删除/改名默认 breaking；更新语义优先 FieldMask；错误用 canonical status + typed details；连接参数、keepalive、max age、flow control、retry/hedging 按 method 白名单配置。
- 验证：跨语言 error details 解析、旧 method 兼容、mesh/LB 超时、HTTP/2 flow control、最大消息、压缩、分页 page_token 稳定性、LRO 轮询/取消、重试只作用于幂等方法。

### 8. gRPC deadline / cancellation / status codes / streaming
- 输入：SLO、客户端 deadline、服务端 cancellation、retry/hedging、stream 类型、背压、心跳、恢复点、LB/mesh HTTP/2 行为。
- 动作：每个调用设置 deadline；服务端尊重 context cancellation；业务错误映射 canonical status codes；streaming 定义半关闭、sequence/offset、去重窗口、限速、最大消息和最终 trailers。
- 验证：INVALID_ARGUMENT、NOT_FOUND、PERMISSION_DENIED、UNAUTHENTICATED、FAILED_PRECONDITION、RESOURCE_EXHAUSTED、DEADLINE_EXCEEDED、CANCELLED、断线重连、慢消费者、重复消息、恢复点和最终状态。

### 9. Kafka / Pulsar / NATS 事件建模
- 输入：事件事实/命令、topic/subject/stream、partition/routing/ordering key、consumer group/subscription、retention、ack、redelivery、ordering 范围。
- 动作：事件名表达已发生事实；key 选择业务顺序维度；不同消费者隔离 group/subscription；Kafka/Pulsar/NATS 的顺序、ack、retention、compaction 写进契约。
- 验证：同 key 顺序、跨分区无全局顺序、partition skew、rebalance、ack deadline、redelivery、consumer lag、DLQ、重放。

### 10. schema registry / AsyncAPI / CloudEvents
- 输入：Avro/Protobuf/JSON Schema、subject 命名、compatibility level、event type/version、envelope version、payload schema version、CloudEvents source/type/id/subject/dataschema、AsyncAPI channel。
- 动作：跨团队事件必须接 schema registry；默认 backward compatibility；subject strategy、event type/version、envelope/payload 版本写入契约；schema 演进先扩展后迁移再收缩；结构兼容不等于语义兼容，语义变化新增 event type/topic/version。
- 验证：registry compatibility、旧 schema 互读、示例消息、subject 兼容矩阵、AsyncAPI 与真实 topic 一致、CloudEvents 信封和 data schema 同时校验。

### 11. Event versioning / compacted topics / consumer backpressure
- 输入：event type/version、envelope version、payload schema version、subject strategy、tombstone/delete 语义、compaction、offset commit、consumer concurrency、pause/resume、poison pill。
- 动作：语义变化新增 event type/version；envelope 与 payload 分别版本化；compacted topic 明确 key 唯一性和 tombstone retention；offset 在副作用成功后提交；毒丸消息隔离并限速回灌。
- 验证：subject 兼容矩阵、旧消费者互读、tombstone/replay、rebalance 中断、pause/resume 回压、重复提交、poison pill 不阻断分区。

### 12. outbox / CDC / idempotency / DLQ / replay
- 输入：事务边界、event_id、business_id+version、outbox 表、CDC offset、retry backoff、DLQ 分类、回灌和 replay 副作用策略。
- 动作：DB 变更与事件发布用 outbox/事务性方案；消费者按 event_id 或业务版本幂等；retry 区分临时/永久错误；DLQ 可诊断、可限速回灌；外部副作用必须有幂等键、撤销、对账或人工补偿路径。
- 验证：事务回滚、发送失败、重复发送、消费者崩溃、乱序、CDC 快照重复、tombstone、schema 变更、历史 replay、副作用隔离、补偿脚本 dry-run 和回灌限速。

### 13. Cross-protocol gateway / transcoding
- 输入：GraphQL-to-gRPC、REST-to-gRPC、grpc-gateway、event-to-subscription、Envoy/mesh 规则、header/metadata、错误映射、trace propagation、streaming 降级。
- 动作：转换层必须声明字段/状态码/错误详情/header-metadata 映射；分页、streaming、partial response、retry 语义不得静默降级；trace/context 贯穿网关和下游。
- 验证：端到端 golden sample、错误映射快照、metadata/header 白名单、超时/取消传播、streaming 降级、跨协议 trace 串联。

### 14. OpenTelemetry / 契约观测
- 输入：trace_id、span_id、operationName、service/method、topic/partition/offset/group、schema version、error/status、lag、DLQ 指标。
- 动作：GraphQL/gRPC/Event 统一 trace propagation；指标按协议维度拆；日志只存脱敏摘要；dashboard 覆盖端到端延迟和消费者完成率。
- 验证：跨协议 trace 串联、resolver span、grpc status、consumer lag、DLQ rate、replay 标记、schema version 标签、告警与 runbook。

### 15. 契约测试 / 压测 / 发布回滚 / 治理资产
- 输入：消费者清单、旧样本、错误样本、CI、registry、测试 broker、灰度策略、回滚和废弃窗口、owner、审查人、豁免。
- 动作：schema/proto/topic diff、consumer-driven contract、golden sample、compatibility matrix、failure injection、load/replay test；压测覆盖 P95/P99、慢消费者、突增流量、DLQ 风暴、broker rebalance、网关限流和回压；所有豁免需到期时间、影响消费者、回滚计划和补验证据。
- 验证：CI job、命令输出、报告、trace/span、dashboard、灰度比例、回滚开关、DLQ 回灌演练、消费者使用率、压测基线对比和豁免到期检查。

### 16. 生产发布 / 回滚 / 事故止血 / 真实验收
- 输入：发布版本、commit、schema/proto/topic diff、消费者矩阵、灰度比例、feature flag、registry/buf/CI 输出、dashboard、DLQ/replay 开关、上一版本契约快照。
- 动作：先发布向后兼容服务和消费者，再灰度新契约；breaking 变更走 expand-migrate-contract；事件链路先双写/双读或 shadow consume；回滚前判断代码、schema、registry、topic、offset、缓存和副作用能否独立回退。
- 验证：发布前后 operation/error/latency、grpc status、consumer lag、DLQ rate、replay 标记、schema version、旧客户端成功率、新旧 producer/consumer 交叉矩阵、真实业务完成率；异常时输出暂停、回滚、补偿或 roll-forward 判据。

## GraphQL / gRPC / Event 契约陷阱速查（独家）

GraphQL 深度坑：

- **N+1 必用 DataLoader**：resolver 单独取每条记录会触发 N+1；用 DataLoader.load(key) 自动按 batch + cache（per-request scope，不跨请求）；嵌套 resolver 也要走 DataLoader。
- **Apollo Federation v2 / Hive Schema Registry**：subgraph 各自 schema + `@key`/`@external`/`@requires`/`@provides` 标识；composition 在 gateway 编译期完成；breaking change 必须经 schema check（apollo-cli/Buf）。
- **persisted query**（automatic / manual）：客户端发 query hash 替代完整 query 文本；防止恶意大 query；CDN 缓存；版本上线前提交 hash 列表。
- **directive vs schema versioning**：`@deprecated(reason:"...")` 标记字段；不要给 schema 整体版本，按字段演进；新增字段是 nullable + 不破坏旧客户端。
- **fragment / @defer / @stream**（GraphQL spec 2024）：fragment 拆字段集；`@defer` 让慢字段异步返；`@stream` 让列表分批；客户端要支持 multipart response。
- **subscription**：默认 WebSocket（graphql-ws protocol）；服务端要管理订阅生命周期、auth、ping/pong；Server-Sent Events (SSE) 作 fallback。
- **cursor-based pagination (Relay)**：`{ edges { node, cursor }, pageInfo { hasNextPage, endCursor } }`；不要用 offset；cursor 是 opaque base64 string。
- **complexity / depth limit**：防恶意 query，`graphql-query-complexity`/`apollo-server-plugin-query-complexity` 计算 cost；rate limit 按 complexity。

gRPC 深度坑：

- **proto field number 永久不变**：字段编号是 wire format key；删字段要 `reserved 5;` + `reserved "old_name";` 防 reuse；改 type 也是 breaking；Buf breaking change detector CI 必跑。
- **proto2 vs proto3**：proto3 默认值不区分"未设置"和"零值"（解决：用 `optional` 关键字 proto3.15+ 或 wrapper types `google.protobuf.StringValue`）。
- **四种 RPC 模式**：unary、server streaming、client streaming、bidi streaming；流式 RPC deadline 仍生效但每条消息无单独超时；流式 handler 要处理 client cancel。
- **deadline / timeout**：客户端设 deadline 通过 metadata 传播；服务端 `context.Context` / `ServerCallContext` 检查；上游 deadline 减去网络 RTT 给下游；不设默认无限等。
- **status code** 不是 HTTP：gRPC 用 `google.rpc.Code`（OK/CANCELLED/INVALID_ARGUMENT/NOT_FOUND/...）；通过 `status.WithDetails` 携带结构化错误（`google.rpc.ErrorInfo`/`BadRequest`/`PreconditionFailure`）。
- **interceptor**：服务端/客户端 unary + stream interceptor；按 chain 顺序执行；用于 auth、logging、metrics、retry。
- **metadata** 是 key-value header（小写 key）：binary 值后缀 `-bin`；不要塞大数据（move 到 message body）。
- **gRPC-Web** vs **Connect**：gRPC-Web 是浏览器子集（无 client streaming）；Connect protocol（Buf 出品）取代 gRPC-Web，HTTP/1.1 + JSON/Protobuf，更通用。
- **Buf** + **buf.gen.yaml**：proto plugin 管理 + lint + breaking + format；替代 protoc + 手写脚本；Buf Schema Registry 是 hosted proto repo。

事件驱动深度坑：

- **at-most-once / at-least-once / exactly-once**：Kafka transaction + idempotent producer 可达 effectively-once；消费侧仍要幂等设计（用 message_id + DB unique）；不存在真正分布式 exactly-once。
- **transactional outbox pattern**：DB 写业务表 + 写 outbox 表在同事务；后台 worker 读 outbox 发 broker；防止 DB 提交但消息丢失。
- **idempotent producer**（Kafka 0.11+）：`enable.idempotence=true` + producer ID + sequence number；防止 retry 重复消息；ordering 保证 per-partition。
- **partition / consumer group**：Kafka partition 是并发单位；同 group 内一个 partition 给一个 consumer；rebalance 时消息可能重复消费（处理需幂等）。
- **schema registry** + **Avro / Protobuf / JSON Schema**：producer 注册 schema 拿 ID + message 头存 ID + consumer 按 ID 取 schema；Confluent Schema Registry + Apicurio 双主流；compat mode（BACKWARD/FORWARD/FULL/NONE）。
- **dead letter queue (DLQ)**：消息处理失败 N 次进 DLQ；监控 DLQ 大小 + 重放工具；区分 transient（重试）vs poison message（DLQ）。
- **event sourcing + CQRS**：写 append-only event log，读用物化 view；event 是 immutable + version；snapshot 减少 replay 开销；CQRS 分离读写模型。
- **saga**：长事务跨服务用补偿模式；orchestration（中央协调）vs choreography（事件驱动）；每步补偿要幂等。
- **CloudEvents** 标准（CNCF）：`specversion`/`type`/`source`/`id`/`time`/`data` 统一信封；broker-agnostic event 互操作。
- **AsyncAPI** 是事件 schema 描述（类似 OpenAPI）；codegen 客户端 + portal；2.6 / 3.0 持续演进。
- broker 对比：**Kafka**（log + partition）、**Pulsar**（topic + 分层存储）、**RabbitMQ**（exchange + routing）、**NATS JetStream**（轻量 + stream）；选型按吞吐 / ordering / retention / 运维难度。

## 高频坑 / 防遗漏

- GraphQL schema 不是 DB/ORM 镜像；resolver 调用数要按列表放大验证；DataLoader 必须请求级、租户级、权限级隔离。
- GraphQL input/argument 也是契约；给旧 operation 新增 required input、改变默认值、混淆 missing/null/empty 都可能 breaking。
- normalized cache、Apollo/Relay fragment、APQ、CDN/HTTP cache、operation registry、client awareness 变化要纳入兼容证据。
- persisted queries 不等于授权；federation composition 通过不等于字段 owner、entity key、query plan 性能正确。
- @defer/@stream 和 subscription 会改变响应时序，旧客户端、网关、缓存和监控必须单独验。
- GraphQL 安全门禁不只 introspection：alias 批量、fragment cycle、batching、深度/复杂度、字段级授权、对象级租户隔离、GET CSRF、上传大小、subscription 鉴权续期必须有测试。
- gRPC proto3 默认值、presence、oneof、JSON mapping、gencode/runtime 版本差异会制造静默兼容问题。
- buf breaking 只能防部分结构破坏，不能证明业务语义、状态码、deadline 和重试策略正确。
- grpc-web 受浏览器、代理、trailers、streaming 能力限制，不等同原生 gRPC。
- gRPC channel、keepalive、LB/name resolver、mesh/xDS、HTTP/2 flow control、max message、compression 是运行时契约，不是纯配置。
- method 删除/改名、错误 details、FieldMask、pagination、LRO、resource name 改动要按消费者矩阵验证。
- Kafka/Pulsar/NATS 的 topic/subject、key、partition、subscription、ack、retention、compaction 是契约，不是运维细节。
- outbox、CDC、replay 默认重复、乱序、延迟和副作用重放；idempotency 不是可选项。
- offset commit 时机、pause/resume、consumer concurrency、poison pill 隔离决定是否会重复副作用或阻塞分区。
- schema registry 不验证业务语义；CloudEvents 只管信封；AsyncAPI 不是运行时契约测试。
- producer 成功不代表业务成功；必须看 consumer lag、DLQ、端到端 trace 和业务状态。
- 转换层会吞语义：GraphQL/gRPC/REST/event 互转时必须明示错误、metadata/header、分页、streaming、retry 和 trace 映射。
- 事件与协议字段按 public/internal/confidential/restricted 分级；restricted 禁入 key/header/metadata/CloudEvents subject/log/DLQ；replay、测试 broker、第三方 consumer 必须脱敏并继承 retention、删除和审计要求。
- 发布后只能证明“新版本已被请求/消费/观测到”才算生效；只看 deploy success、Pod Ready、topic 有消息或 schema 已注册不够。
- 回滚不一定能撤销事件副作用；扣款、通知、外部 webhook、缓存失效、offset 提交、DLQ 回灌必须有补偿或幂等止血方案。

## 输出要求

1. 契约对象：GraphQL schema/resolver/operation/input、gRPC proto/service/message/method、Kafka/Pulsar/NATS topic/subject、CloudEvents type、schema registry subject、跨协议映射。
2. 版本环境：GraphQL/gateway/client、operation registry/APQ、protoc/runtime/buf/grpc-web、broker/registry/client、OpenTelemetry 版本和环境差异。
3. 入口复现：请求或消息样本、旧版本样本、失败条件、operationName/service/method/topic/group、变量/input、最小复现范围。
4. 兼容结论：兼容、breaking change、高风险兼容或需验证，并列 schema/proto/buf/registry/消费者证据。
5. 影响面：生产者、消费者、SDK、缓存、网关、broker、registry、监控、测试、发布、回滚、DLQ/replay、第三方和跨境消费者。
6. 风险点：N+1、DataLoader、persisted queries、federation、@defer/@stream、deadline/cancellation、status codes、connection/LB、ordering key、idempotency、consumer lag、隐私生命周期。
7. 测试证据：contract test、golden sample、新旧矩阵、failure injection、load/replay test、缓存/注册表/转换层快照、CI job 和命令结果。
8. 观测证据：OpenTelemetry trace/span、resolver latency、grpc status、topic/partition/offset/group、lag、DLQ、dashboard、告警。
9. 发布方案：灰度、双写/双读、deprecation、迁移窗口、schema/proto/topic 门禁、回滚点、DLQ 回灌策略、豁免到期。
10. 发布后证据：版本、schema/proto/registry subject、topic offset、consumer group、灰度比例、旧消费者成功率、错误率/延迟/lag/DLQ 前后对比。
11. 缺口：未查消费者、未跑 CI、未拿 registry、未验证旧版本、未覆盖安全/发布/隐私/转换层时显式标“无法验证”。

## 约束

- 不把 GraphQL 当万能 BFF；强事务命令、高吞吐流、批处理不默认走 GraphQL。
- 不用“GraphQL/gRPC/Kafka 高性能”替代证据；必须看查询形态、消息大小、下游调用和消费能力。
- 不复用 protobuf tag，不把 UNKNOWN/INTERNAL 当业务错误垃圾桶，不给非幂等 gRPC 方法开自动重试。
- 不把 Kafka/Pulsar/NATS 当 RPC；需要同步结果时重评交互模型。
- 不承诺 Exactly-once 业务效果；broker 事务不覆盖外部副作用。
- 不把 schema registry、CloudEvents、AsyncAPI 当完整契约测试。
- 不让 GraphQL error、gRPC metadata、topic key、headers、CloudEvents attributes、logs、DLQ 承载敏感明文。
- 不跨相邻技能边界；DB、Web 安全、测试、SRE、后端实现、最终审计必须联动对应技能。

## 高频 Bug 反例库

- 反例 1：GraphQL schema 直接暴露 ORM。错法：把 DB 字段全量映射到公共 GraphQL schema。对法：按业务契约建模，敏感字段默认不暴露。根因：内部模型不是公共契约。
- 反例 2：GraphQL 字段直接删除。错法：服务端没引用就删字段。对法：deprecate、监控 operation/field、通知消费者、窗口后删除。根因：消费者常在客户端 query 中。
- 反例 3：GraphQL input 破坏旧客户端。错法：给已发布 mutation 新增 required input 或改变默认值。对法：新增可选 input、版本化 input object，回放旧变量。根因：变量校验先于业务逻辑失败。
- 反例 4：partial update 语义混乱。错法：把 missing、null、empty string 都当清空。对法：明确 FieldMask/patch 语义或 input 版本。根因：输入 presence 也是契约。
- 反例 5：客户端缓存炸裂。错法：改 entity id/cache key/fragment owner 未通知 Apollo/Relay 客户端。对法：把 normalized cache 和 operation registry 纳入兼容测试。根因：兼容事故常发生在客户端状态层。
- 反例 6：resolver 触发 N+1。错法：订单 100 条逐条查用户和商品。对法：DataLoader/batcher 批量加载，key 含租户和权限。根因：执行树掩盖调用放大。
- 反例 7：DataLoader 全局缓存。错法：loader 单例跨请求复用。对法：请求级实例，key 含租户/权限/过滤。根因：缓存边界错会串数据。
- 反例 8：persisted queries 当安全边界。错法：只允许白名单 query 就不做字段授权。对法：persisted queries 配合对象/字段级授权和 complexity。根因：查询白名单不等于数据授权。
- 反例 9：GraphQL batching/alias 滥用。错法：只限制 depth 不限制 alias、batch、fragment cycle。对法：复杂度、频率、批量、递归和租户边界一起测。根因：攻击形态不只深查询。
- 反例 10：federation 只看 composition 通过。错法：subgraph 字段 owner 变更后直接发。对法：查 query plan、entity key、旧 gateway 和消费者。根因：组合成功不代表运行时兼容。
- 反例 11：@defer/@stream 无降级。错法：服务端开启增量响应，旧客户端解析失败。对法：按客户端能力协商并保留非增量路径。根因：响应时序也是契约。
- 反例 12：protobuf tag 复用。错法：删除 old_status 后把 tag 7 给 new_status。对法：reserved 7 和 old_status，新字段用新 tag。根因：wire format 按编号解析，会静默误读。
- 反例 13：proto3 presence 误判。错法：把缺失和显式默认值当同一语义。对法：用 optional/oneof 或版本字段表达 presence，做跨语言样本。根因：生成代码语义受版本和语言影响。
- 反例 14：buf breaking 未进 CI。错法：本地改 proto 只跑单测。对法：CI 跑 buf breaking 与 golden sample。根因：破坏性变更常在消费者侧爆炸。
- 反例 15：grpc-web 等同原生 gRPC。错法：浏览器端照搬 bidi streaming 和 trailers 处理。对法：验证代理、header/trailer、stream 支持和错误映射。根因：Web 传输能力受限。
- 反例 16：gRPC 无 deadline/cancellation。错法：客户端无限等待，服务端不处理取消。对法：客户端设置 deadline，服务端尊重 context cancellation。根因：局部慢会扩散成资源耗尽。
- 反例 17：gRPC status codes 滥用 UNKNOWN。错法：权限、参数、未找到全返回 UNKNOWN。对法：映射 UNAUTHENTICATED、PERMISSION_DENIED、INVALID_ARGUMENT、NOT_FOUND。根因：客户端无法稳定重试和告警分组。
- 反例 18：gRPC 连接治理缺失。错法：mesh/LB/channel keepalive、max age、flow control 默认值上线。对法：按 method/SLO 验证连接生命周期、超时、压缩和最大消息。根因：连接参数会改变可用性和背压。
- 反例 19：gRPC 方法演进静默破坏。错法：改名/删除 method，或把错误 details 从结构化改成字符串。对法：保留旧 method、canonical status + typed details，跑跨语言样本。根因：调用方依赖生成代码和错误类型。
- 反例 20：streaming 当队列用。错法：无背压、无心跳、无恢复点。对法：定义 offset/sequence、keepalive、限速、重连和最终 status。根因：stream 是连接语义，不是持久队列。
- 反例 21：Kafka partition key 随机。错法：同订单事件落不同分区。对法：按业务实体选 partition key 并记录顺序边界。根因：Kafka 只保证同分区顺序。
- 反例 22：Pulsar subscription 模式误选。错法：需要按 key 有序却用 Shared。对法：按 Key_Shared/Failover 等语义选择并压测。根因：订阅模式决定并发和顺序。
- 反例 23：NATS ack/redelivery 未设计。错法：消费者超时后重复副作用。对法：设置 ack、max deliver、幂等键和 DLQ。根因：至少一次投递会重复。
- 反例 24：消费者无 idempotency。错法：rebalance 后重复扣款/发短信。对法：event_id 或 business_id+version 唯一约束，副作用可去重。根因：异步交付不保证只处理一次。
- 反例 25：offset 过早提交。错法：副作用前提交 offset，失败后消息丢失。对法：副作用成功后提交，失败可重试或进 DLQ。根因：提交点定义交付语义。
- 反例 26：poison pill 阻塞分区。错法：坏消息无限重试卡住同分区。对法：错误分类、隔离、限速、DLQ 和告警。根因：单条坏消息会拖垮有序消费。
- 反例 27：DLQ 不可回灌。错法：只把失败消息丢到死信队列。对法：记录错误分类、schema version、trace、回灌限速和副作用开关。根因：DLQ 是排障与恢复契约。
- 反例 28：schema registry subject 选错。错法：本地 schema 通过，生产 subject 兼容检查失效。对法：统一 subject 策略并在 CI 连接 registry。根因：兼容性绑定 subject。
- 反例 29：事件语义悄悄改变。错法：OrderPaid 从支付成功改为授权成功，event type 不变。对法：新增 event type/version，旧语义保留迁移窗口。根因：结构兼容不等于业务语义兼容。
- 反例 30：compacted topic tombstone 未定义。错法：删除事件没有 tombstone retention 和 replay 策略。对法：约定 key 唯一性、delete 语义、保留期和回放行为。根因：压缩主题的删除也是契约。
- 反例 31：跨协议转换吞错误。错法：gRPC PERMISSION_DENIED 经网关变成 GraphQL 200 + 普通 error，客户端重试。对法：固定错误映射和快照测试。根因：转换层会改变状态码和重试语义。
- 反例 32：metadata/header 泄露或丢失。错法：网关透传所有 header，或丢 trace/tenant。对法：白名单、脱敏、trace/context 传播测试。根因：跨协议边界是安全和观测断点。
- 反例 33：consumer lag 未告警。错法：producer 发送成功就判链路成功。对法：看 lag、DLQ、端到端延迟、业务状态和 OpenTelemetry trace。根因：异步成功发生在消费者完成后。
- 反例 34：PII 进入事件路由属性。错法：把手机号/邮箱放 topic key、CloudEvents subject、DLQ。对法：字段分级、最小化路由属性、脱敏和 retention。根因：路由和排障字段也受隐私生命周期约束。
- 反例 35：breaking 变更混在普通发布里。错法：同一发版删字段、换 topic key、开新 consumer 并清理旧逻辑。对法：拆 expand-migrate-contract，先兼容双轨，再观测旧消费者归零。根因：契约迁移不是一次性代码替换。
- 反例 36：registry 兼容但消费者崩。错法：Avro/Protobuf 结构 backward 通过就全量发。对法：补语义变更审查、旧样本回放和 consumer-driven contract。根因：结构兼容不覆盖业务含义。
- 反例 37：回滚只回服务不回契约。错法：代码回滚后 registry/topic/offset/flag 仍在新语义。对法：发布前写清每层回滚或 roll-forward 顺序。根因：协议状态分散在多处。
- 反例 38：灰度只看入口错误率。错法：GraphQL/gRPC 入口正常就晋级，异步消费者 lag 已飙升。对法：把 lag、DLQ、consumer success、业务完成率作为晋级门禁。根因：异步链路成功滞后于入口成功。
- 反例 39：AI 生成 proto/schema 未审兼容。错法：字段名更顺眼就改 tag、nullability 或 enum。对法：机器 diff、buf/registry、人工契约审查和旧样本。根因：命名优化可能是 wire/API breaking。
- 反例 40：trace 断在网关。错法：GraphQL 到 gRPC 或事件桥丢掉 traceparent/baggage。对法：header/metadata 白名单和端到端 trace 快照测试。根因：没有串联观测就无法定位跨协议故障。

## 提交前自检清单

- [ ] 行数 < 500，且 fenced code block = 0。
- [ ] frontmatter 含 name、description，H1 等于 manifest title（GraphQL/gRPC/事件接口）。
- [ ] 快速总则覆盖协议/版本、schema/proto/topic、兼容策略、证据。
- [ ] GraphQL schema、input、resolver、N+1、DataLoader、persisted queries、client cache、operation registry、federation、@defer/@stream 已覆盖。
- [ ] GraphQL alias/batching/fragment、GET CSRF、multipart upload、subscription auth、tenant boundary 已覆盖为契约门禁。
- [ ] gRPC proto3、buf breaking、grpc-web、deadline/cancellation、status codes、streaming、connection/LB/mesh、error details、FieldMask/API evolution 已覆盖。
- [ ] Kafka/Pulsar/NATS、schema registry、event versioning、compacted topic、outbox、idempotency、DLQ、consumer lag、pause/resume、poison pill 已覆盖。
- [ ] 跨协议转换层的状态码、错误、metadata/header、pagination、streaming 降级、trace 传播已覆盖。
- [ ] 契约测试、consumer-driven contract、golden sample、新旧消费者矩阵、失败注入有证据。
- [ ] OpenTelemetry trace/log/metric/dashboard/runbook 与协议维度一致。
- [ ] 发布、灰度、deprecation、回滚/roll-forward、DLQ 回灌、replay 风险、owner、审查人、豁免到期已说明。
- [ ] breaking/high-risk/safe 分类、上一版本契约快照、发布前后指标和回滚层级已写清。
- [ ] 隐私字段分级、数据最小化、retention、right-to-delete、replay 脱敏、第三方消费者审计已纳入契约证据。
- [ ] 与 api、db、wsec、obs、be、tst、aud 边界无重复职责。

## 2024-2026 新坑速查

- 2024-2026 GraphQL federation、persisted queries、@defer/@stream 更常见；坑是 query plan fan-out、只控 query 不控授权、旧客户端不支持增量响应，修法是 query plan/resolver latency 门禁、复杂度预算、字段级授权、能力协商和降级路径。
- 2024-2026 GraphQL 安全治理聚焦 introspection、alias 批量、fragment 递归、GET CSRF、multipart upload 和 subscription 续权；坑是登录后无限查或跨租户查，修法是 depth/complexity/rate limit、租户边界和上传/订阅专项测试。
- 2024-2026 Protobuf Editions 与 proto2/proto3 并存，buf breaking 成为门禁；坑是 presence、默认值、生成代码不一致或只跑结构 diff，修法是锁 protoc/runtime/gencode 矩阵、buf breaking + golden sample + 消费者矩阵。
- 2024-2026 grpc-web、移动网关、service mesh/xDS 增多；坑是 trailers、streaming、CORS、代理超时、LB/keepalive/flow control 差异，修法是真实网关链路压测和连接参数契约化。
- 2024-2026 gRPC retry/hedging 平台化；坑是非幂等方法自动重试放大副作用，修法是 method 级幂等声明、重试白名单和 typed error details。
- 2024-2026 Kafka/Pulsar/NATS 混用增加；坑是把三者顺序和 ack 语义套用，或忽略 pause/resume、offset commit、poison pill，修法是按 broker 写清契约和失败注入。
- 2024-2026 schema registry 同管 Avro/Protobuf/JSON Schema；坑是 subject 策略混乱、结构兼容掩盖语义变化，修法是统一命名、event type/version、envelope/payload 版本并进 CI。
- 2024-2026 outbox/CDC 普及；坑是快照重复、tombstone、源 schema 变更、replay 乱序，修法是 event_id、source offset、version、幂等消费和 compaction/tombstone 策略。
- 2024-2026 OpenTelemetry semantic conventions 迭代且跨协议网关增多；坑是 attribute 漂移、trace/context 中断、错误映射失真，修法是锁版本、统一命名、转换层 golden sample。
- 2024-2026 隐私审计覆盖事件流；坑是 PII 进入 topic key、metadata、CloudEvents subject、DLQ、replay 环境和第三方 consumer，修法是字段分级、最小化、脱敏、retention/删除/审计继承。
- 2024-2026 AI 生成 schema/proto 增多；坑是命名好看但兼容错误，修法是机器 diff、registry check、人工审查三件套。

## 与相邻技能的边界

- 与 API 工程/api-engineering（api）：REST/OpenAPI/HTTP 资源、URL、状态码、认证语义归 API 工程/api-engineering（api）；GraphQL schema/input、gRPC proto、事件 schema/topic 的兼容与排障归本技能。
- 与 数据库工程/database-engineering（db）：表、索引、SQL、迁移、锁、事务归 数据库工程/database-engineering（db）；outbox/CDC 事件语义、schema evolution、消费者幂等归本技能协作。
- 与 Web 安全/web-security（wsec）：漏洞验证、攻击面审计、授权测试归 Web 安全/web-security（wsec）；本技能负责把 introspection、query batching、alias/fragment、CSRF/upload/subscription、字段级权限、metadata/headers/topic key/PII 泄露写入契约。
- 与 可观测性/observability（obs）：SLO、告警、值班、容量、事故流程归 可观测性/observability（obs）；本技能定义 GraphQL/gRPC/Event 必备协议维度、trace 字段、lag/DLQ 指标。
- 与 后端工程/backend-engineering（be）：后端分层、运行时、配置、队列任务实现归 后端工程/backend-engineering（be）；本技能约束跨服务协议契约、连接治理、转换层和消费者兼容。
- 与 测试验证/test-engineering（tst）：测试体系、场景矩阵、自动化落地归 测试验证/test-engineering（tst）；本技能提供 contract/golden/replay/failure injection/cache/registry/transcoding 的验证口径。
- 与 代码审计/code-audit（aud）：最终改动对账、安全质量和证据收口归 代码审计/code-audit（aud）；本技能提供协议/事件风险清单与兼容证据。