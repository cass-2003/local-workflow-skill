---
name: structured-logging
description: "结构化日志工程实战。覆盖 JSON 日志格式、log levels 语义、context 与 trace ID 透传、sampling 采样、PII 脱敏、log shipping 链路（Fluentd/Vector/Loki/CloudWatch）、关联 metrics 与 traces、cardinality 爆炸防护、各语言库选型（zap/zerolog/pino/structlog/slog/serilog）。当用户提到结构化日志、structured logging、JSON log、log level、trace ID、context propagation、PII 脱敏、log shipping、Loki、Fluentd、cardinality、sampling、zap、zerolog、pino、slog 时使用。"
---

# Structured Logging Skill — 结构化日志

## 何时使用

- 新项目立项（日志格式从一开始定型）
- 调试"为什么 SRE 让我加 trace ID"
- 处理"日志体积爆炸 / 检索缓慢"
- 排查跨服务调用的请求链路
- 满足合规（PII / GDPR）的日志脱敏

## 一、核心原则

1. **机器优先**：JSON 格式，键值对。人类用 `jq` / Loki / ES query 看
2. **每条日志带 context**：service / version / env / trace_id / user_id / request_id
3. **大写 level 严格语义**：DEBUG < INFO < WARN < ERROR < FATAL
4. **永不日志即吞噬**：catch 后必须含 cause 或 rethrow
5. **结构化字段稳定**：键名固定、不要混用 `userId` / `user_id` / `uid`
6. **PII 默认脱敏**：邮件 / 手机 / 身份证 / 卡号永远过滤 redactor

## 二、JSON 日志标准字段

```json
{
  "ts": "2026-05-06T07:00:00.123Z",
  "level": "info",
  "service": "checkout-api",
  "version": "v2.3.1",
  "env": "production",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "request_id": "req_abc123",
  "user_id": "u_456",
  "msg": "order created",
  "order_id": "ord_789",
  "amount_cents": 12345,
  "currency": "USD",
  "duration_ms": 87
}
```

**字段约定**：
- `ts` ISO 8601 UTC（带 Z）
- `level` 小写：`debug` / `info` / `warn` / `error` / `fatal`
- `msg` 简短描述（**不含**变量值；变量在结构化字段里）
- `trace_id` / `span_id` 遵循 W3C Trace Context（OpenTelemetry 标准）

**反模式**：

```json
// ❌ 字符串拼接
{ "msg": "user 123 created order 456 for $123.45" }

// ✅ 结构化
{ "msg": "order created", "user_id": 123, "order_id": 456, "amount_cents": 12345 }
```

理由：检索 `user_id=123` 比正则匹配 string 快几个数量级，且不受 msg 文案变化影响。

## 三、Log Level 语义（严格）

| Level | 含义 | 例子 | 生产开启？ |
|---|---|---|---|
| **DEBUG** | 开发诊断 | "entering function X with args" | ❌ |
| **INFO** | 正常事件 | "user logged in" / "order created" | ✅ |
| **WARN** | 异常但已恢复 | "retrying after 5xx" / "fallback to cache" | ✅ |
| **ERROR** | 失败需关注 | "DB query failed" / "5xx returned" | ✅（有告警） |
| **FATAL** | 进程终止 | "config invalid, shutting down" | ✅（罕见） |

**关键**：
- ERROR 应触发告警 → 慎用，不要给瞬时网络抖动打 ERROR
- INFO 日志 = 业务事件；不是函数追踪（用 trace 替代）
- DEBUG 日志生产关闭，但**保留代码**（dev / staging 启用）

## 四、Context 透传

### Go (1.21+ slog)

```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

// 带 context 的 logger（每个请求基础信息）
reqLogger := logger.With(
    "request_id", reqID,
    "user_id", userID,
    "trace_id", traceID,
)

reqLogger.Info("order created", "order_id", orderID, "amount_cents", 12345)
```

### TypeScript (pino)

```typescript
import pino from 'pino'
const logger = pino({ level: 'info' })

// 子 logger 继承字段
const reqLogger = logger.child({ request_id: req.id, user_id: req.user.id })
reqLogger.info({ order_id, amount_cents: 12345 }, 'order created')
```

### Python (structlog)

```python
import structlog
log = structlog.get_logger()

# bind context
req_log = log.bind(request_id=req.id, user_id=req.user.id)
req_log.info("order_created", order_id=order_id, amount_cents=12345)
```

### Rust (tracing)

```rust
use tracing::{info, instrument};

#[instrument(fields(user_id = %user.id))]
fn create_order(user: &User) {
    info!(order_id, amount_cents = 12345, "order created");
}
```

### 中间件设置 context（通用）

```typescript
// Express middleware
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] ?? randomUUID()
  req.log = baseLogger.child({
    request_id: req.id,
    method: req.method,
    path: req.path,
    trace_id: extractTraceId(req),
  })
  next()
})
```

## 五、Trace ID 与 OpenTelemetry 集成

W3C Trace Context 标准：

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^ ^^
             ver trace_id (32 hex)              span_id (16 hex)  flags
```

服务 A 调服务 B：
- A 设置 outgoing header `traceparent`
- B 读取 → 自家 span 用同 trace_id + 新 span_id
- 日志库自动注入 trace_id / span_id 到每条日志

```go
// otel + slog 集成
import "go.opentelemetry.io/contrib/bridges/otelslog"
logger := otelslog.NewLogger("checkout")
// 自动从 context 注入 trace_id / span_id
logger.InfoContext(ctx, "order created")
```

效果：在 Grafana 一处看 trace，点 trace_id 跳转到 Loki 看该请求的所有日志。**强烈推荐配置**。

## 六、Sampling（采样）

高 QPS 服务全量日志会爆。采样策略：

### 1. 速率采样

```
DEBUG: 1%
INFO:  100%（业务事件不采样）
WARN:  100%
ERROR: 100%
```

### 2. Tail-based sampling（OTel collector 推荐）

收集所有 trace + 日志，到 collector 端按规则抽样：
- 含 ERROR 的 trace 100% 保留
- 慢请求（latency > 1s）100% 保留
- 其余 1%

### 3. 限流（rate limit logger）

```typescript
// pino: 每秒最多 100 条同一 msg
logger.info({ rate_limited: true, key: 'fetch-failure' }, 'fetch failed')
```

防止"同一错误每秒 1 万条"瞬间打爆 storage。

## 七、PII 脱敏

```typescript
// pino: redact 配置
const logger = pino({
  redact: {
    paths: [
      'user.email',
      'user.phone',
      '*.password',
      '*.token',
      'req.headers.authorization',
      'req.headers.cookie',
    ],
    censor: '[REDACTED]',
  },
})
```

```go
// slog: 自定义 ReplaceAttr
slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        if isSensitive(a.Key) {
            return slog.String(a.Key, "[REDACTED]")
        }
        return a
    },
})
```

**清单**：
- 邮箱 → 显示 `j***@example.com`
- 手机 → `138****1234`
- 卡号 → 仅显示后 4 位
- IP（GDPR 视情况）→ `192.168.x.x` 或全 hash
- Authorization / Cookie / Session token → 整体替换
- 敏感业务字段（薪资 / 病历） → 项目自定义清单

## 八、Cardinality 爆炸（关键陷阱）

```json
// ❌ 不要把高基数字段做 metrics tag / log index field
{ "user_id": "u_123" }   // user_id 千万级
{ "request_id": "..." }  // 每请求唯一
```

**Loki 标签 / Prometheus label / Elasticsearch keyword 字段**：高基数会让索引爆炸 / 查询慢 / 成本高。

**规则**：
- 高基数字段：写在 **JSON body**（可全文搜索 / grep / jq）
- 低基数字段（service / env / level / status_code）：作为 **label / tag**

```yaml
# Loki labels（低基数）
{ service="checkout", level="error", env="prod" }
# 业务字段在日志体里
```

## 九、各语言库选型

| 语言 | 推荐库 | 备注 |
|---|---|---|
| **Go** | log/slog (1.21+) | 标准库，零依赖 |
| **Go (高性能)** | uber-go/zap、rs/zerolog | 零分配，benchmark 之冠 |
| **Node.js** | pino | 业界 fastest |
| **Python** | structlog + stdlib logging | 业界事实标准 |
| **Java** | Logback + Logstash encoder | / SLF4J facade |
| **Rust** | tracing + tracing-subscriber | 与 OTel 集成完美 |
| **C#** | Serilog | rich sink 生态 |
| **Ruby** | semantic_logger / lograge (Rails) | |
| **PHP** | Monolog | PSR-3 标准 |

## 十、Log Shipping 链路

```
应用 stdout JSON
   ↓
[ Fluentd / Vector / Filebeat ]   ← 边车 / DaemonSet 采集
   ↓
[ Kafka / SQS ]                   ← 缓冲（可选）
   ↓
[ Loki / Elasticsearch / CloudWatch / Datadog ]   ← 存储 + 检索
   ↓
[ Grafana / Kibana ]               ← 查询 + 可视化
```

**关键**：
- 应用**只写 stdout**（12-factor 第 11 条）
- 采集 / 路由 / 存储 / 检索都是基础设施职责
- 不要应用层调云日志 SDK（耦合 / 故障导致请求阻塞）

## 十一、查询模式

```bash
# Loki LogQL
{service="checkout", level="error"} | json | user_id="u_123"

# Elasticsearch DSL
GET checkout-*/_search
{ "query": { "bool": { "must": [
  { "match": { "level": "error" }},
  { "match": { "user_id": "u_123" }}
]}}}

# CloudWatch Logs Insights
fields @timestamp, msg, user_id, error
| filter level = "error" and user_id = "u_123"
| sort @timestamp desc

# 本地 jq
cat app.log | jq 'select(.level=="error" and .user_id=="u_123")'
```

## 十二、Don'ts

- ❌ `console.log("user " + userId + " did X")` — 用结构化字段
- ❌ `printf("%v", obj)` — 序列化不可控，可能含 PII
- ❌ 日志即吞噬：`catch (e) { log.error(e) }` 不带 context — 加 stack / cause
- ❌ stdout + stderr 混合 JSON 和 plain text — 一律 JSON，stderr 留给真正的 error
- ❌ 日志里写大对象（整个 user record） — 只写 ID + 关键字段
- ❌ 多行日志（异常 stack 拆成多行）— 容器采集会拆成多条 → 用 multiline 配置或单行 JSON
- ❌ DEBUG 留在生产 — 体积 + 可能泄密
- ❌ 用日志当 metrics（计数 ERROR 行数）— 用专门的 Prometheus / OTel metrics
- ❌ 在 hot path 同步写文件 — 异步 / 缓冲
- ❌ trace_id 用 UUID v4 — 用 16 字节 hex（OTel 标准）以兼容 W3C Trace Context
- ❌ 日志带 wallclock 计时 — 跨节点漂移；用 monotonic / 服务端 ts

## 十三、参考资料

- 12-Factor App #11 (Logs)：https://12factor.net/logs
- W3C Trace Context：https://www.w3.org/TR/trace-context/
- OpenTelemetry Logs：https://opentelemetry.io/docs/specs/otel/logs/
- pino docs：https://getpino.io/
- Go slog tutorial：https://go.dev/blog/slog
- structlog docs：https://www.structlog.org/
- Honeycomb "Observability Engineering"（书 / Charity Majors）
