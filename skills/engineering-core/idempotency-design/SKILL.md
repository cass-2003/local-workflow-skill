---
name: idempotency-design
description: "幂等性设计实战。覆盖 idempotency key 模式、at-least-once vs exactly-once 神话、HTTP 方法幂等性、重试安全、去重窗口、幂等性 token 存储（Redis/DB）、消息队列消费幂等、支付/订单/库存等高风险场景、Stripe API 标杆设计。当用户提到 idempotency、idempotent、幂等、重试安全、idempotency key、at-least-once、exactly-once、消息去重、订单防重、支付幂等时使用。"
---

# Idempotency Design Skill — 幂等性设计

## 何时使用

- 设计写操作 API（创建订单 / 扣款 / 发短信 / 转账）
- 客户端 retry 但不知道服务端是否成功
- 消息队列消费者（at-least-once 投递）
- Webhook 接收方（请求方可能重发）
- 调试"用户被扣了两次款"

## 一、定义

> **幂等**：执行 N 次（N≥1）的效果与执行 1 次相同。

不是"无副作用"，是"副作用合并"：
- `DELETE /users/123` 第一次删除，第二次返 404 / 204 但状态一致 → 幂等 ✅
- `POST /payments` 第一次扣 $10，第二次又扣 $10 → 不幂等 ❌

## 二、HTTP 方法幂等性（规范）

| 方法 | 幂等？ | 安全？ |
|---|---|---|
| GET / HEAD | ✅ | ✅（无副作用） |
| OPTIONS | ✅ | ✅ |
| PUT | ✅（替换） | ❌ |
| DELETE | ✅ | ❌ |
| POST | ❌（默认）| ❌ |
| PATCH | ❌（默认）| ❌ |

**关键**：HTTP 方法的幂等性是**契约**而不是自动保证。`PUT /users/123` 实现里如果每次 +1 计数器，就不幂等了——是实现错误。

## 三、为什么 exactly-once 是个神话

**真相**：在分布式系统中，**at-most-once** + **at-least-once** 才存在；**exactly-once** 是端到端**业务**层面的幻觉。

实现路径：

```
at-least-once 投递 + 消费端幂等 = 业务上的 exactly-once
```

**关键设计原则**：永远假设上游会重发，**消费端必须幂等**。

## 四、Idempotency Key 标准模式（Stripe 标杆）

### 客户端

```http
POST /v1/charges
Idempotency-Key: 8e3a5f4c-2b3d-4f1e-9c8a-1d2e3f4a5b6c
Content-Type: application/json

{ "amount": 1000, "currency": "USD", "customer": "cus_xxx" }
```

客户端为**每个唯一业务请求**生成一个 key（UUID v4）。重试同一个请求复用同一个 key。

### 服务端逻辑

```
1. 收到请求，提取 Idempotency-Key
2. 查 idempotency 表 (key, request_hash, response, status, expires_at)
3. 找到 key:
   a. 状态 = COMPLETED → 直接返回缓存的响应
   b. 状态 = IN_PROGRESS → 返回 409 Conflict 或等待
   c. request_hash 不匹配 → 返回 422（同 key 不同 body 是错误）
4. 没找到 key:
   a. INSERT (key, request_hash, status=IN_PROGRESS) 用主键约束防并发
   b. 执行业务
   c. UPDATE 表 (response, status=COMPLETED)
   d. 返回响应
5. 失败时:
   a. 留 key 给客户端重试（24h TTL 后 GC）
   b. 或 DELETE key 让重试当新请求
```

### 数据库 schema

```sql
CREATE TABLE idempotency_records (
  key            TEXT PRIMARY KEY,
  user_id        BIGINT NOT NULL,             -- 配合 user 隔离
  request_method TEXT NOT NULL,
  request_path   TEXT NOT NULL,
  request_hash   TEXT NOT NULL,               -- SHA256(body) 防同 key 不同请求
  status         TEXT NOT NULL,               -- 'in_progress' | 'completed'
  response_code  INT,
  response_body  JSONB,
  created_at     TIMESTAMPTZ DEFAULT now(),
  expires_at     TIMESTAMPTZ NOT NULL          -- 24h 后清理
);

CREATE INDEX idx_idempotency_expires ON idempotency_records(expires_at);
```

### 并发控制（关键）

两个并发请求同 key 同时到达：

**方案 A：Insert-or-fail**

```sql
INSERT INTO idempotency_records (key, status, ...)
VALUES (?, 'in_progress', ...)
-- 主键冲突 → 第二个请求拿不到锁
```

第二个请求：select 看到状态 in_progress → 返回 409 让客户端等待。

**方案 B：Redis SETNX**

```redis
SETNX idem:{key} "in_progress" EX 60
```

返回 1 才能继续；返回 0 说明并发请求已在处理。

## 五、message queue 消费幂等

### Kafka / RabbitMQ / SQS 都是 at-least-once

```
producer  ─publish─▶  broker  ─deliver─▶  consumer
                                          │
                                       process
                                          │
                                         ack
                                          │
                          (ack 丢了 → broker 重投 → 重复消费)
```

### 消费者去重模式

```python
def consume(message):
    msg_id = message.id   # broker 提供的唯一 ID

    # 1. 用 Redis SETNX 做去重窗口（5min 内重复不处理）
    if not redis.set(f"processed:{msg_id}", "1", nx=True, ex=300):
        log.info(f"duplicate message {msg_id}, skipped")
        return ack()

    # 2. 业务处理 + DB 事务
    with db.transaction():
        # 业务逻辑
        # 把 msg_id 写入业务表的 dedup 列
        db.exec("INSERT INTO orders (msg_id, ...) ON CONFLICT (msg_id) DO NOTHING ...")

    ack()
```

**关键**：去重 + 业务在**同一事务**或者去重在前（业务前 SETNX）+ ack 在后。

### 顺序保证

`Kafka` 同 partition 顺序；`SQS FIFO queue` MessageGroupId 同组顺序；其他无序。

## 六、不同业务的幂等策略

### 1. 订单创建（最经典）

**方案**：业务侧 idempotency key（Stripe 模式）+ DB 唯一索引

```sql
CREATE UNIQUE INDEX uniq_order_idem ON orders(user_id, idempotency_key);
```

INSERT 失败时返回已有订单。

### 2. 转账 / 扣款

**方案**：transaction_id 唯一 + 流水表

```sql
-- 流水表（永远 INSERT，绝不 UPDATE）
CREATE TABLE ledger_entries (
    id SERIAL PRIMARY KEY,
    transaction_id UUID UNIQUE NOT NULL,    -- 客户端提供，重试同值
    account_id BIGINT,
    delta_cents BIGINT,
    created_at TIMESTAMPTZ
);
```

重试 INSERT 同 transaction_id 直接冲突 → 安全。

### 3. 发短信 / 邮件

**方案**：短期去重表（10min 窗口）

```sql
CREATE TABLE notification_dedupe (
    dedupe_key TEXT PRIMARY KEY,    -- e.g. SHA(user + template + payload)
    created_at TIMESTAMPTZ DEFAULT now()
);
```

INSERT 冲突 → 跳过。配合 `WHERE created_at > now() - interval '10 minutes'` 的清理任务。

### 4. 库存扣减

**方案**：版本号 / 乐观锁

```sql
UPDATE inventory
SET qty = qty - 1, version = version + 1
WHERE sku = 'X' AND qty >= 1 AND version = ?
-- 影响行数 0 → 重试或返回失败
```

或者：用唯一约束记录"该订单是否扣过"

```sql
CREATE TABLE inventory_deductions (
    order_id BIGINT,
    sku TEXT,
    qty INT,
    PRIMARY KEY (order_id, sku)
);
```

### 5. Webhook 接收

**方案**：依赖发件方提供 event_id + 自家去重表

```python
# Stripe webhook
event_id = request.json['id']   # evt_xxx
if db.exists(f"webhook_event:{event_id}"):
    return 200   # 已处理
db.insert("webhook_event", id=event_id)
process(event)
```

## 七、key 来源与寿命

### 客户端生成（推荐）

UUID v4 / v7 (含时间戳)。客户端在**业务操作开始时**生成，整个重试周期复用。

```javascript
// 用户点击"创建订单"按钮
const idempotencyKey = crypto.randomUUID()
// 重试时复用该 key
async function submit() {
  return retry(() => api.createOrder({ ...formData, idempotencyKey }))
}
```

**陷阱**：用户刷新页面后再点击 → 新 key → 可能重复创建。
解决：把 key 存 sessionStorage 关联表单状态。

### 服务端衍生

请求体哈希：

```
key = SHA256(user_id + endpoint + JSON(sorted(body)))
```

**风险**：用户故意修改一个字段就绕过去重。仅做防御性兜底，不替代客户端 key。

### TTL

- **24 小时**（Stripe 默认）：覆盖大多数 retry 场景
- **7 天**：保守选项
- **永久**（仅订单 ID 这种）：用业务唯一约束而非通用 idempotency 表

## 八、Don'ts

- ❌ 用 timestamp 做 idempotency key（毫秒级冲突）
- ❌ 用 user_id 做 key（同用户不同操作互相吞了）
- ❌ key 全局唯一但不 scope user → 别人偷你 key 用
- ❌ 同 key 不同 body 静默处理 → 必须返回 422 提醒客户端 bug
- ❌ 在内存 map 里存 key → 重启丢、多实例不一致
- ❌ 不限 key 长度 → 数据库 KEY 列被超长字符串撑爆
- ❌ idempotency 表不限 TTL → 无限增长
- ❌ 用 retry 库但请求未带 idempotency key → 不安全的重试
- ❌ 把 idempotency 当一致性保证 → 它只是去重，不解决分布式事务
- ❌ 幂等保证用 read-modify-write（不加锁）→ race condition

## 九、API 设计建议

```http
# 幂等接口必须接受 Idempotency-Key 头
POST /api/v1/orders
Idempotency-Key: <uuid>
Content-Type: application/json

# 缺失时拒绝
HTTP/1.1 400 Bad Request
{
  "type": "/errors/missing-idempotency-key",
  "title": "Idempotency-Key header required for this endpoint"
}

# 同 key 不同请求体
HTTP/1.1 422 Unprocessable Entity
{
  "type": "/errors/idempotency-key-conflict",
  "title": "Idempotency-Key reused with different request body"
}

# 处理中
HTTP/1.1 409 Conflict
Retry-After: 1
{
  "type": "/errors/idempotency-key-in-progress",
  "title": "Original request still processing"
}
```

## 十、监控与运维

- **指标**：duplicate_request_count / idempotency_table_size / replay_response_count
- **报警**：表大小异常增长（TTL 清理任务挂了）
- **审计**：每次复用 idempotency key 应该记日志（潜在客户端 bug 信号）

## 十一、参考资料

- Stripe API Idempotency：https://stripe.com/docs/api/idempotent_requests
- "Idempotency in HTTP Methods"：RFC 9110 §9.2.2
- AWS API Gateway Idempotency: docs
- "Designing Data-Intensive Applications"（Kleppmann 第 8、11 章 — 一致性与共识）
- "Implementing exactly-once semantics in Kafka": confluent.io blog
- BraveCobra "Idempotency-Key" 草案：https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
