---
name: rate-limiting-algorithms
description: "限流算法实战。覆盖 Fixed Window / Sliding Window Log / Sliding Window Counter / Token Bucket / Leaky Bucket / GCRA 六种算法对比、单机内存实现、Redis 分布式限流（INCR / sorted set / Lua script）、Nginx limit_req 模块、Envoy / API gateway 限流、429 与 Retry-After 头、客户端退避、按 IP / user / API key 限流维度、限流与配额、突发流量处理、限流绕过攻击。当用户提到 rate limit、限流、token bucket、leaky bucket、sliding window、Redis 限流、429、Retry-After、Nginx limit_req、API quota、防爬虫、突发流量 时使用。"
---

# Rate Limiting Algorithms Skill — 限流算法

## 何时使用

- 公开 API 防滥用 / 防爬虫 / 防 DDoS
- 第三方服务调用（自家被动限流避免成本爆炸）
- 设计 API quota / billing 体系
- 选择 Nginx / Redis / 应用层限流的组合
- 排查"客户感觉被误伤"

## 一、六种核心算法

### 1. Fixed Window（固定窗口）

```
[ 0:00 - 0:59 ] 计数 100 次
[ 1:00 - 1:59 ] 计数清零，重新计 100 次
```

```python
# Redis 实现
key = f"ratelimit:{user_id}:{minute}"
count = redis.incr(key)
if count == 1: redis.expire(key, 60)
if count > 100: reject()
```

**优点**：简单 / 内存少
**缺点**：**边界突发**：0:59 用 100 次 + 1:00 立刻又 100 次 = 1 秒内 200 次，可能压垮下游

### 2. Sliding Window Log（滑动窗口日志）

```python
# 每次请求记 timestamp 到 sorted set
redis.zadd(key, {req_id: now})
redis.zremrangebyscore(key, 0, now - 60)   # 清 60s 前
count = redis.zcard(key)
if count > 100: reject()
```

**优点**：精确，无边界突发
**缺点**：内存大（每请求一条记录）

### 3. Sliding Window Counter（滑动窗口计数）

近似算法，工业首选：

```
当前窗口 [now-60, now]
= 当前分钟 已计数 × (已过秒数 / 60) + 上一分钟计数 × (剩余比例)

例：当前 1:30，已计 50；上一分钟（0:00-0:59）计 80
counter = 50 + 80 × (60-30)/60 = 50 + 40 = 90
```

```lua
-- Redis Lua（原子）
local current = redis.call('GET', KEYS[1]) or 0
local previous = redis.call('GET', KEYS[2]) or 0
local elapsed = tonumber(ARGV[1])   -- 当前窗口已过秒数
local rate = tonumber(current) + tonumber(previous) * (60 - elapsed) / 60
if rate >= tonumber(ARGV[2]) then return 0 end
redis.call('INCR', KEYS[1])
redis.call('EXPIRE', KEYS[1], 120)
return 1
```

**优点**：精度近 SW Log + 内存仅两个计数器
**缺点**：近似算法，假设窗口内请求均匀分布

### 4. Token Bucket（令牌桶）

```
桶容量 100 个 token
每秒补充 10 个（最大 100）
每个请求消耗 1 个 token
桶空时拒绝
```

```python
def allow(now):
    elapsed = now - last_refill
    tokens = min(capacity, tokens + elapsed * refill_rate)
    last_refill = now
    if tokens >= 1:
        tokens -= 1
        return True
    return False
```

**优点**：
- 允许**突发**（桶满时可一次发 100 个）
- 长期速率稳定
- AWS / GCP / Stripe 等大厂常用

**缺点**：实现稍复杂（需要存 tokens + last_refill）

### 5. Leaky Bucket（漏桶）

```
桶容量 100，固定速率 10/秒"漏出"
请求加入桶（满则拒绝）
```

```python
def allow(now):
    leaked = (now - last_check) * leak_rate
    bucket = max(0, bucket - leaked)
    last_check = now
    if bucket + 1 <= capacity:
        bucket += 1
        return True
    return False
```

**优点**：输出**严格匀速**（防下游 burst）
**缺点**：不允许突发

`Token Bucket` vs `Leaky Bucket`：
- TB 控制**输入速率均值**，允许突发
- LB 控制**输出速率严格**，平滑突发

## 二、GCRA（Generic Cell Rate Algorithm，电信级）

最优雅的实现 — 单 timestamp 替代 token 计数：

```
Theoretical Arrival Time (TAT)
period T = 1/rate
burst tolerance τ = burst × T

allow(now):
  if now > tat:    tat = now             # 桶空
  new_tat = tat + T
  if new_tat - now > τ: reject()
  tat = new_tat
  return True
```

**Cloudflare / Stripe / GitHub 用法**。Redis 模块 `redis-cell` 原生提供 `CL.THROTTLE`。

## 三、单机内存（最快，无网络开销）

```typescript
// 单机 token bucket
class TokenBucket {
  private tokens: number
  private lastRefill: number
  constructor(private capacity: number, private refillPerSec: number) {
    this.tokens = capacity
    this.lastRefill = Date.now()
  }
  tryConsume(n = 1): boolean {
    const now = Date.now()
    const elapsed = (now - this.lastRefill) / 1000
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.refillPerSec)
    this.lastRefill = now
    if (this.tokens >= n) { this.tokens -= n; return true }
    return false
  }
}
```

**库**：
- Node: `bottleneck` / `p-throttle` / `limiter`
- Go: `golang.org/x/time/rate` (token bucket)
- Python: `aiolimiter` / `ratelimit`
- Java: Guava `RateLimiter` / Resilience4j RateLimiter

**适用**：单实例 / 边车进程级限流。多实例失效（每实例独立计数）。

## 四、Redis 分布式限流（多实例）

### 简单 INCR 方案（fixed window）

```python
# 每分钟 100 次
key = f"rl:{user_id}:{int(now/60)}"
n = redis.incr(key)
if n == 1: redis.expire(key, 60)
return n <= 100
```

**陷阱**：`INCR` 后 `EXPIRE` 中间 crash 会留下永不过期的 key。改用 Lua 原子：

```lua
local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return n
```

### Sorted Set 方案（sliding window log）

```lua
-- KEYS[1] = key, ARGV[1] = window_ms, ARGV[2] = max, ARGV[3] = now_ms, ARGV[4] = req_id
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[3] - ARGV[1])
local n = redis.call('ZCARD', KEYS[1])
if n >= tonumber(ARGV[2]) then return 0 end
redis.call('ZADD', KEYS[1], ARGV[3], ARGV[4])
redis.call('PEXPIRE', KEYS[1], ARGV[1])
return 1
```

### redis-cell（GCRA 模块）

```
CL.THROTTLE user:123 15 30 60 1
       max_burst    rate    quantity
返回：[allowed?, total_limit, remaining, retry_after_sec, reset_after_sec]
```

最简单，**强烈推荐**。

## 五、HTTP 响应规范

### 响应头（每次响应都带）

```
RateLimit-Limit:     100               (规范: RFC IETF draft)
RateLimit-Remaining: 17
RateLimit-Reset:     30                (秒)
```

或老格式（GitHub / Twitter）：

```
X-RateLimit-Limit:     100
X-RateLimit-Remaining: 17
X-RateLimit-Reset:     1715000060      (Unix ts)
```

### 限流响应（429）

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 30                        ← 秒（也支持 HTTP-date）
RateLimit-Reset: 30

{
  "type": "/errors/rate-limited",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded for endpoint /api/users",
  "retry_after": 30
}
```

`Retry-After` 是**标准头**，客户端 SDK 应自动遵守。

## 六、客户端退避

```typescript
async function callWithBackoff(fn, opts) {
  let attempt = 0
  while (true) {
    const resp = await fn()
    if (resp.status !== 429) return resp
    if (++attempt > opts.maxAttempts) throw new RateLimitError()

    const retryAfter = parseRetryAfter(resp.headers.get('Retry-After'))
        ?? Math.min(60_000, 1000 * 2 ** attempt)         // exponential fallback
    const jitter = Math.random() * retryAfter * 0.3       // 30% jitter
    await sleep(retryAfter * 1000 + jitter)
  }
}
```

**关键**：用服务端 `Retry-After`，加 jitter 防 thundering herd。

## 七、Nginx 限流

```nginx
http {
  # 共享内存区
  limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
  limit_req_zone $http_authorization  zone=user:10m rate=100r/m;

  server {
    location /api/ {
      limit_req zone=api burst=20 nodelay;
      limit_req zone=user burst=10;
      proxy_pass http://backend;
    }
  }
}
```

**`burst`**：允许的突发量（漏桶容量）
**`nodelay`**：超额立即 503，不延迟
**`delay=N`**：超过 N 才 503，前面排队延迟

返回 503 默认（可改 `limit_req_status 429`）。

## 八、API Gateway 限流（Envoy / Kong / AWS API Gateway）

| 网关 | 限流支持 |
|---|---|
| **Envoy** | Local rate limit / Global rate limit (gRPC service) / Quota service |
| **Kong** | rate-limiting plugin (local / cluster / Redis) |
| **AWS API Gateway** | Usage plans + API keys + throttle / burst settings |
| **Cloudflare** | Rate Limiting Rules (edge layer，最强) |
| **Fastly** | VCL 自定义 |

**层次化限流**（推荐）：
- 边缘（CDN / Cloudflare）：粗粒度按 IP，挡爬虫 / DDoS
- API Gateway：按 API key
- 应用层：按 user / endpoint 细粒度

## 九、限流维度

```
按什么 key 限流？
- IP (anonymous)              → 防爬虫，但 IPv4 NAT 集体误伤
- user_id (authenticated)     → 公平
- API key                     → 商业 API 必备
- endpoint × user_id          → 防关键 endpoint 滥用
- IP × endpoint               → 多维组合
- tenant_id (multi-tenant)    → 防一个租户拖垮其他
```

**多桶并行**：

```
每个请求：
  if !allow(per_ip_bucket):       reject
  if !allow(per_user_bucket):     reject
  if !allow(per_endpoint_bucket): reject
  if !allow(global_bucket):       reject
```

任一桶不够 → 429。

## 十、Quota vs Rate Limit

| | Rate Limit | Quota |
|---|---|---|
| 时间窗 | 秒 / 分钟 | 天 / 月 |
| 目的 | 保护下游 / 防突发 | 计费 / 公平分配 |
| 超出 | 429 + Retry-After | 402 Payment Required / 429 |
| 重置 | 滑动 / 桶补 | 月初 / 计费周期 |

公开 API（Stripe / OpenAI）通常组合：每秒限流 + 每月配额。

## 十一、突发流量（实际场景）

```
正常: 100 req/s
活动开始: 5000 req/s 持续 5 分钟
```

**应对**：
1. **预估 + 提前调高**（缓存 warm + 实例扩容）
2. **token bucket** 允许短时突发（桶大）
3. **降级优先级**：业务关键路径不限，次要路径限严
4. **队列削峰**：限流后请求入队（Kafka / SQS）异步处理 — 仅限**异步可接受**业务（订单 / 通知）
5. **CDN 缓存**：相同请求 GET 走边缘，源站只见少量

## 十二、Don'ts

- ❌ 仅按 IP 限流（NAT / VPN 误伤；攻击者轮换 IP 绕过）
- ❌ 忘记返回 429 改返 500 — 客户端无法识别
- ❌ 无 Retry-After 头 — 客户端只能盲猜
- ❌ 单机内存限流但多实例部署（每实例独立配额，实际 ×N）
- ❌ Redis 限流不用 Lua 原子（INCR + EXPIRE race condition）
- ❌ 限流粒度太粗（一个 endpoint 限 1000/s 但内含登录 + 列表 + 下单）
- ❌ 用 sleep 实现客户端限流而不是退避 — 阻塞调用栈
- ❌ admin / 内部调用走同一限流桶 — 误伤运维
- ❌ 限流计数 key 用明文 user 邮箱 — PII；用 hash 或 ID
- ❌ 不监控 429 比例 — 突增时反应慢
- ❌ 把 `Retry-After: 60` 当死规则 client 多次同时苏醒 → thundering herd（必加 jitter）
- ❌ 用限流当鉴权（"匿名 1/s，认证 100/s"作为唯一保护）— 限流是防滥用不是访问控制

## 十三、监控指标

```
- requests_total{status, endpoint, user_tier}
- requests_throttled_total{reason}      ← 429 计数
- bucket_remaining{key}                  ← 各桶余量分布
- retry_after_seconds (histogram)        ← 客户端等待时长
```

报警：
- 429 比例 > 1% 持续 5 min → 调高配额或扩容
- 单 user_id 触发 429 > 100 次 / 分钟 → 滥用嫌疑

## 十四、参考资料

- "Rate limiting Stripe APIs"：https://stripe.com/blog/rate-limiters
- Cloudflare Rate Limiting：https://developers.cloudflare.com/waf/rate-limiting-rules/
- "An alternative approach to rate limiting"（GCRA / Cloudflare blog）
- Redis Patterns - Rate Limiter：https://redis.io/learn/develop/node/nodecrashcourse/ratelimiting
- redis-cell（GCRA 模块）：https://github.com/brandur/redis-cell
- IETF RateLimit header draft：https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/
- Nginx ngx_http_limit_req_module 文档
- "System Design Interview" Chapter 4（Alex Xu）
