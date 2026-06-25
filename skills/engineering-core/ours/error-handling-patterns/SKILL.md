---
name: error-handling-patterns
description: "错误处理跨语言模式。覆盖 Result/Either 模式、panic vs throw vs error code、错误链 wrap/unwrap、RFC 7807 Problem Details、用户态 vs 系统态错误、retry/circuit breaker、structured errors、不要日志即吞噬、stack trace 保留、错误恢复策略。当用户提到错误处理、error handling、Result、Either、panic、throw、错误链、wrap error、RFC 7807、Problem Details、retry、circuit breaker、错误码 时使用。"
---

# Error Handling Patterns Skill — 错误处理跨语言

## 何时使用

- 设计公共库 / SDK 的错误 API
- 调试"日志写了但堆栈没了"/ "错误吞了没人知道"
- 跨服务调用错误传递（HTTP / gRPC）
- 决定何时 throw / 何时返回 error / 何时 panic
- 重试 / 熔断 / 降级策略

## 一、错误的两个维度

| 维度 | 取值 |
|---|---|
| **方向** | 上游传来 / 自家产生 / 下游返回 |
| **可恢复性** | 可重试（瞬时） / 不可重试（永久） / 灾难（停服） |

```
              | 可重试        | 不可重试       | 灾难
--------------|---------------|----------------|----------
用户输入错    | -             | 400/422 显示   | -
认证失败      | -             | 401 引导登录   | -
权限不足      | -             | 403 提示       | -
不存在        | -             | 404 提示       | -
冲突          | (有时可)      | 409 让用户改   | -
限流          | 重试退避      | -              | -
依赖超时      | 重试 1-2 次   | 降级           | -
依赖 5xx      | 重试退避      | 降级           | -
DB 死锁       | 立即重试      | -              | -
DB 连不上     | 重试退避      | -              | 启动失败 panic
代码 bug      | -             | 500 + 告警     | -
OOM           | -             | -              | crash + restart
```

## 二、四大流派

### 1. **Exception**（Java / C# / Python / Ruby / JS）

```javascript
try {
  const user = await db.findUser(id)
  if (!user) throw new NotFoundError('user', id)
  return user
} catch (e) {
  if (e instanceof NotFoundError) return null
  throw e   // rethrow 未知错误
}
```

**优点**：调用栈自动展开 / 不污染正常路径
**缺点**：函数签名隐藏失败可能 / 容易吞噬 / 性能（构造 stack）

### 2. **Error Value**（Go）

```go
user, err := db.FindUser(id)
if err != nil {
    if errors.Is(err, sql.ErrNoRows) { return nil, nil }
    return nil, fmt.Errorf("db.FindUser: %w", err)   // wrap
}
return user, nil
```

**优点**：错误是显式返回值 / 不会忘记处理
**缺点**：样板代码多 / 容易 `if err != nil { return err }` 丢失上下文

### 3. **Result/Either**（Rust / Haskell / Scala / 现代 TS）

```rust
fn find_user(id: u64) -> Result<User, FindError> {
    db.find_user(id).map_err(FindError::DbError)
}

match find_user(123) {
    Ok(user) => println!("{}", user.name),
    Err(FindError::DbError(e)) => log::error!("db: {}", e),
    Err(FindError::NotFound) => println!("not found"),
}
```

```typescript
// TS / fp-ts / neverthrow
import { Result, ok, err } from 'neverthrow'

function findUser(id: number): Result<User, FindError> {
  return db.findUser(id).match(
    user => user ? ok(user) : err({ kind: 'not_found' }),
    e => err({ kind: 'db_error', cause: e })
  )
}
```

**优点**：类型层强制处理 / 可组合（`map` / `andThen` / `?`）
**缺点**：语言不原生支持时样板更多

### 4. **Algebraic Effects / Monadic**（OCaml / Koka / Effect-TS）

最理想但最学习成本高。Effect-TS 在 TS 生态崛起：

```typescript
import { Effect } from 'effect'
const program = db.findUser(id).pipe(
  Effect.flatMap(user => log.info(`found ${user.name}`)),
  Effect.catchTag('NotFound', () => Effect.succeed(null)),
  Effect.retry({ times: 3, schedule: Schedule.exponential('100 millis') }),
)
```

## 三、错误链（wrap / unwrap）

**绝不**这样：

```go
// ❌ 丢失底层信息
if _, err := db.Query(...); err != nil {
    return errors.New("query failed")
}

// ❌ 字符串拼接破坏类型
if _, err := db.Query(...); err != nil {
    return fmt.Errorf("query failed: " + err.Error())
}
```

**应该**：

```go
// ✅ Go 1.13+ %w wrap
if _, err := db.Query(...); err != nil {
    return fmt.Errorf("findUser %d: %w", id, err)
}

// 上层判断
if errors.Is(err, sql.ErrNoRows)        { ... }   // sentinel
if errors.As(err, &dnsErr)              { ... }   // typed
```

```typescript
// ✅ JS 2022+ Error cause
throw new ApiError('failed to fetch user', { cause: e })

// 检查
if (e instanceof ApiError && e.cause instanceof NetworkError) ...
```

```python
# ✅ Python from 关键字
try:
    db.query(...)
except DBError as e:
    raise UserError('failed to find user') from e
```

## 四、RFC 7807 Problem Details（HTTP 错误格式）

```http
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "type": "https://example.com/errors/validation",
  "title": "Validation failed",
  "status": 400,
  "detail": "Email is required",
  "instance": "/users/create",
  "errors": [
    { "field": "email", "code": "required" },
    { "field": "age", "code": "min", "min": 18 }
  ]
}
```

**字段**：
- `type`：URI 标识错误类型（可选但推荐）
- `title`：人读简述
- `status`：HTTP 状态码（与响应一致）
- `detail`：本次具体错误说明
- `instance`：本次错误的 URI（请求路径 / trace ID）
- 自定义扩展字段（如 `errors`）

跨语言库：
- Spring：`spring-boot-starter-validation` 自动产
- ASP.NET：`ProblemDetails` 内置
- Node：`http-errors` + 自家中间件
- Python：`fastapi` HTTPException + 自定义 handler

## 五、错误分类（用 typed errors 而非 string）

```typescript
// ✅ Discriminated union
type AppError =
  | { kind: 'validation'; field: string; message: string }
  | { kind: 'not_found'; resource: string; id: string }
  | { kind: 'unauthorized' }
  | { kind: 'forbidden'; reason: string }
  | { kind: 'conflict'; current: unknown }
  | { kind: 'rate_limited'; retryAfter: number }
  | { kind: 'upstream_error'; service: string; cause: unknown }
  | { kind: 'internal'; cause: unknown }

// HTTP 映射
function toHttp(e: AppError): { status: number; body: ProblemDetails } {
  switch (e.kind) {
    case 'validation': return { status: 400, body: {...} }
    case 'not_found':  return { status: 404, body: {...} }
    case 'unauthorized': return { status: 401, body: {...} }
    case 'forbidden':  return { status: 403, body: {...} }
    case 'conflict':   return { status: 409, body: {...} }
    case 'rate_limited': return { status: 429, body: {...} }
    case 'upstream_error': return { status: 502, body: {...} }
    case 'internal':   return { status: 500, body: {...} }
  }
}
```

## 六、retry / 退避 / 熔断

### 指数退避 + 抖动

```typescript
async function retry<T>(
  fn: () => Promise<T>,
  opts: { maxAttempts: number; baseMs: number; maxMs: number }
): Promise<T> {
  let lastErr: unknown
  for (let i = 0; i < opts.maxAttempts; i++) {
    try { return await fn() }
    catch (e) {
      lastErr = e
      if (!isRetryable(e)) throw e
      const delay = Math.min(opts.maxMs, opts.baseMs * 2 ** i)
      const jitter = Math.random() * delay        // full jitter
      await new Promise(r => setTimeout(r, jitter))
    }
  }
  throw lastErr
}

function isRetryable(e: unknown): boolean {
  if (e instanceof NetworkError) return true
  if (e instanceof TimeoutError) return true
  if (e instanceof Response5xxError) return true
  if (e instanceof RateLimitedError) return true
  return false
}
```

**关键**：
- **抖动**避免 thundering herd（所有客户端同时重试）
- **可重试性判断**：4xx 一般不重试（除 408/425/429）；5xx 通常重试
- **请求幂等**：非幂等请求需 idempotency key（见 idempotency-design skill）

### 熔断器（circuit breaker）

```
CLOSED  ──失败次数 ≥ 阈值──▶  OPEN
                                │
                       cooldown │ 计时
                                ▼
                          HALF_OPEN
                          │       │
                       成功     失败
                          │       │
                       CLOSED   OPEN
```

**库**：
- Java：Resilience4j（替代 Hystrix）
- Go：sony/gobreaker、 resilience4go
- Node：opossum
- Python：pybreaker

## 七、不要做的（最常见反模式）

```javascript
// ❌ 1. 吞掉异常
try { doX() } catch (e) {}

// ❌ 2. 日志即吞噬
try { doX() } catch (e) { console.log(e) }   // 调用方以为成功了

// ❌ 3. 通用 Error 类型
throw new Error('failed')   // 上层无法分类处理

// ❌ 4. 用 string 做错误码
if (e.message === 'not found') ...   // 国际化 / 改文案就崩

// ❌ 5. 包了一层就丢栈
try { doX() } catch (e) { throw new Error('wrap') }   // 原栈丢失
// ✅
try { doX() } catch (e) { throw new Error('wrap', { cause: e }) }

// ❌ 6. await 但不 catch
const data = await fetch(...)   // 异常冒泡到顶，难以定位
// ✅ 在合适层级 try-catch

// ❌ 7. 业务错也用 panic / throw
if (user.age < 18) panic("too young")    // 改用 return error
// panic 用于"程序员错误"（不可能到达的状态），不是业务

// ❌ 8. catch 后继续用半状态
try { user = await fetchUser() } catch {}
console.log(user.name)   // user undefined

// ❌ 9. 多次 retry 却不退避 / 不限次
while (!ok) { ok = await tryX() }   // 雪崩源
```

## 八、何时 panic / 何时 error

```go
// ✅ panic（不可能到达 / 程序员错误）
if config == nil { panic("config not initialized — bug") }

// ✅ error（业务可能失败）
user, err := db.FindUser(id)
```

判断：

> 这个错误是**调用方可能希望恢复**的吗？
> - 是 → return error / Result
> - 否（说明代码有 bug）→ panic / assert

`Cannot read properties of null` 在生产是 bug，在开发阶段越早 panic 越好。

## 九、HTTP 错误响应规范

```typescript
// 中间件统一兜底
app.use((err, req, res, next) => {
  if (err instanceof AppError) {
    const { status, body } = toHttp(err)
    res.status(status).type('application/problem+json').json(body)
  } else {
    // 未知错误
    logger.error({ err, traceId: req.id }, 'unexpected error')
    res.status(500).json({
      type: '/errors/internal',
      title: 'Internal Server Error',
      status: 500,
      instance: req.id,    // trace id 让客户支持 / 报告
    })
  }
})
```

**永远不**把内部错误细节（SQL / 文件路径 / 堆栈）回显给客户端。仅给 `traceId`，让用户报告时关联日志。

## 十、Don'ts 速查

- ❌ catch 不打日志（默默吞）
- ❌ catch 不带 cause（丢栈）
- ❌ retry 不退避 / 不抖动 / 不限次
- ❌ retry 非幂等请求（重复扣款）
- ❌ 业务错误 panic / throw new Error
- ❌ 错误细节漏到客户端
- ❌ try 包整个函数（粒度过粗）
- ❌ async 函数返 Promise<unknown>（错误被吞）
- ❌ 用 boolean 表达成功失败（损失信息）
- ❌ 把 nil/undefined 当"成功无数据" + "未查"重载（用 Option / Result）

## 十一、参考资料

- "The Error Model"（Joe Duffy）：http://joeduffyblog.com/2016/02/07/the-error-model/
- "Errors are Values"（Rob Pike）：https://go.dev/blog/errors-are-values
- RFC 7807 / RFC 9457 (Problem Details for HTTP APIs)
- Resilience4j docs：https://resilience4j.readme.io/
- neverthrow（TS Result）：https://github.com/supermacro/neverthrow
- Effect（TS effect system）：https://effect.website/
- AWS Builder's Library "Timeouts, retries, and backoff with jitter"：https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
