---
name: graceful-shutdown
description: "服务优雅停机实战。覆盖 SIGTERM/SIGINT 信号处理、HTTP 服务器 drain、数据库连接池关闭、message queue 消费者 drain、health check 摘流、Kubernetes preStop hook + terminationGracePeriodSeconds、in-flight 请求等待、shutdown timeout 设计、并发清理任务编排、init container 启动顺序。当用户提到 graceful shutdown、优雅停机、SIGTERM、preStop、terminationGracePeriodSeconds、drain、信号处理、connection draining、in-flight、滚动发布断流、deploy 中断请求时使用。"
---

# Graceful Shutdown Skill — 优雅停机

## 何时使用

- 部署滚动更新时用户看到 502 / 连接重置
- 排查"deploy 后丢了几条请求 / 队列消息"
- 设计长连接服务（WebSocket / SSE / gRPC streaming）的发布
- 数据库 / 缓存连接没正确关闭，连接数堆积
- Kubernetes 滚动 deploy 配 preStop / terminationGracePeriodSeconds

## 一、为什么需要优雅停机

```
[时刻 T]   K8s 收到 deploy 命令
[T+0ms]    新 Pod 创建
[T+xms]    新 Pod ready → Service endpoint 加入新 IP
[T+xms]    Service endpoint 移除旧 IP（异步！可能延迟）
[T+xms]    旧 Pod 收到 SIGTERM
[T+30s]    grace period 默认 30s 后 SIGKILL
```

**两个并发问题**：
1. **endpoint 摘流延迟**：旧 Pod 收到 SIGTERM 但 LB 还在发流量进来 → 502 / 连接重置
2. **in-flight 请求**：旧 Pod 处理中的请求还没完成就被 kill → 数据不一致 / 客户端 retry

## 二、停机六步标准流程

```
1. 收到 SIGTERM
2. 标记 health check 为 unhealthy → LB / Service 摘流
3. 等若干秒（让 LB / DNS / kube-proxy 真正生效）
4. 关闭 HTTP listener（不接新连接）
5. 等待所有 in-flight 请求完成（带 timeout）
6. 关闭依赖（DB pool / Redis / message queue / OTel exporter flush）
7. 进程退出
```

## 三、Go 标准实现

```go
func main() {
    srv := &http.Server{Addr: ":8080", Handler: router}
    go srv.ListenAndServe()

    // 1. 等信号
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGTERM, syscall.SIGINT)
    <-quit
    log.Info("shutdown signal received")

    // 2. 标记 unhealthy（让 LB 摘流）
    healthState.Store(false)
    time.Sleep(5 * time.Second)   // 等 LB 摘流（K8s readiness 周期 + 误差）

    // 3-4-5. 关闭 HTTP（带超时；server.Shutdown 等 in-flight 完成）
    ctx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        log.Error("forced shutdown", "err", err)
    }

    // 6. 关依赖
    db.Close()
    redis.Close()
    tracerProvider.Shutdown(context.Background())   // flush spans
    log.Info("shutdown complete")
}
```

## 四、Node.js (Express / Fastify)

```javascript
const server = app.listen(8080)
let shuttingDown = false

// healthcheck 路由
app.get('/healthz', (req, res) => {
  res.status(shuttingDown ? 503 : 200).json({ ok: !shuttingDown })
})

async function shutdown() {
  if (shuttingDown) return
  shuttingDown = true
  console.log('SIGTERM received, shutting down')

  // 1. 等 LB 摘流
  await sleep(5000)

  // 2. 关 listener
  await new Promise<void>((resolve) => {
    server.close((err) => err ? console.error(err) : resolve())
    // server.close 等所有 keep-alive 连接关闭
    // 强制关 keep-alive：server.closeIdleConnections()  (Node 18+)
    server.closeIdleConnections?.()
  })

  // 3. 等 in-flight（自家计数器或外部 inflight 中间件）
  await waitForInflightToFinish(20_000)

  // 4. 关依赖
  await db.end()
  await redis.quit()
  await otelSdk.shutdown()

  process.exit(0)
}

process.on('SIGTERM', shutdown)
process.on('SIGINT', shutdown)
```

`server.close()` 默认**等 keep-alive 连接自然关闭**（可能很久）。Node 18+ 的 `closeIdleConnections()` / `closeAllConnections()` 强制关。

## 五、Python (FastAPI / Starlette)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    db = await asyncpg.create_pool(...)
    yield
    # shutdown
    await db.close()
    await redis.close()

app = FastAPI(lifespan=lifespan)

# uvicorn 自带 SIGTERM → graceful；通过 timeout-graceful-shutdown 配置
# uvicorn main:app --timeout-graceful-shutdown 30
```

uvicorn / hypercorn 已内置 graceful 支持：收到 SIGTERM → stop accept → 等 in-flight → exit。

## 六、Kubernetes 集成（关键）

### Pod spec

```yaml
spec:
  terminationGracePeriodSeconds: 60        # 总时长（默认 30）
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh","-c","sleep 10"]   # 给 endpoint 摘流时间
    readinessProbe:
      httpGet: { path: /healthz, port: 8080 }
      periodSeconds: 5
      failureThreshold: 1
```

**关键时序**：

```
T+0:  K8s decide to terminate Pod
T+0:  Pod marked Terminating → endpoint 异步移除（kube-proxy 各节点收到事件可能延迟）
T+0:  preStop hook 开始执行
T+10s: preStop sleep 完毕（此时 endpoint 应已被各 LB 完全摘除）
T+10s: SIGTERM 发给 PID 1
T+10s ~ T+60s: 应用 graceful shutdown
T+60s: SIGKILL 强制
```

**preStop sleep 是工程上最可靠的摘流等待**（K8s endpoint propagation 是 best-effort 异步）。

### readiness vs liveness

| Probe | 失败时 |
|---|---|
| **liveness** | Pod 重启 |
| **readiness** | Pod 从 Service endpoint 移除（不重启）|
| **startup** | 启动期保护，成功后切到 liveness |

**优雅停机标志放 readiness**，不是 liveness（不要重启自己！）。

### terminationGracePeriodSeconds 取值

```
preStop.sleep + app.shutdown_timeout < terminationGracePeriodSeconds
比如 10 + 25 = 35 < 60
```

否则 SIGKILL 提前砍死，与不优雅一样。

## 七、长连接处理

### WebSocket / SSE

收到 SIGTERM 后：
1. 拒绝新连接（HTTP upgrade 返 503）
2. 给所有现有连接发 `close` frame，code 1001 (going away)，让客户端 reconnect 别处
3. 等连接自然关闭或 timeout 强关

```javascript
io.engine.on('connection', (socket) => {
  socket.send({ type: 'server-shutdown', retryAfter: 1 })
  setTimeout(() => socket.close(), 1000)
})
```

### gRPC streaming

```go
// 发送 GOAWAY 让客户端 reconnect
grpcSrv.GracefulStop()    // 等 in-flight RPC 完成，新 RPC 拒绝
```

## 八、Worker / Queue 消费者

```go
// SIGTERM → 停止取新消息，等当前 batch 处理完
func consumer(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            log.Info("consumer stopping, no new messages")
            return
        default:
            msg, err := queue.Receive(ctx, 5*time.Second)
            if err != nil { continue }
            process(msg)
            msg.Ack()    // 处理完才 ack
        }
    }
}

// main:
ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGTERM)
defer cancel()

go consumer(ctx)
<-ctx.Done()
// 给消费者一段时间完成最后一条消息
time.Sleep(10 * time.Second)
```

**关键**：消费完才 ACK，未 ACK 消息 broker 会重投（at-least-once + 消费幂等）。

## 九、数据库连接池

```go
// Go database/sql
db.SetConnMaxLifetime(30 * time.Minute)
defer db.Close()    // 关闭所有空闲连接，等 in-use 连接归还

// pgx pool
pool.Close()        // 等所有 acquired conn 释放（无 timeout，可能挂！）
// 推荐自家加超时：
done := make(chan struct{})
go func() { pool.Close(); close(done) }()
select {
case <-done:
case <-time.After(10*time.Second): log.Warn("pool close timeout")
}
```

## 十、Observability flush

```go
// OpenTelemetry SDK 必须 flush，否则最后一批 spans / metrics 丢失
shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
tracerProvider.Shutdown(shutdownCtx)
meterProvider.Shutdown(shutdownCtx)
```

日志通常 stdout 由 sidecar 采集，不需要 flush。如果用 batch sender（Datadog / Sentry），同样需要 flush。

## 十一、常见 Bug

| 现象 | 原因 |
|---|---|
| Deploy 后 502 / connection reset | endpoint 没摘流前就关 listener — 加 preStop sleep |
| `server.close()` 永不返回 | keep-alive 连接 — 用 closeIdleConnections() |
| 容器 SIGKILL | shutdown 时长 > terminationGracePeriodSeconds |
| 信号没收到 | PID 1 是 shell（如 `sh -c "node app"`）会吞信号 — 用 tini / dumb-init 或直接 ENTRYPOINT exec |
| 数据库连接没关 | defer db.Close() 在 main 里，main 没正常退出 — 用 signal.Notify + 显式 close |
| 队列消息重复处理 | shutdown 中已处理但没 ack 的消息被重投 — 业务侧幂等（见 idempotency-design skill） |
| OTel spans 丢失 | 没 flush — 加 tracerProvider.Shutdown |

## 十二、Dockerfile 信号传递

```dockerfile
# ❌ shell form：sh 是 PID 1，吞 SIGTERM
CMD node app.js

# ✅ exec form：node 是 PID 1，直接收信号
CMD ["node", "app.js"]

# 或用 tini 处理僵尸进程 + 信号
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "app.js"]
```

## 十三、Don'ts

- ❌ shutdown 用 `os.Exit(0)` 跳过 defer
- ❌ 不区分 SIGTERM 和 SIGINT 行为（应一致）
- ❌ shutdown 超时时间硬编码（应依赖 K8s grace period）
- ❌ readiness 失败重启进程（用 liveness）
- ❌ 收到 SIGTERM 立刻关 listener（应先摘流再关）
- ❌ pool.Close() 不带超时（可能阻塞到 SIGKILL）
- ❌ 长连接收到 SIGTERM 不通知客户端（让客户端不知道 reconnect）
- ❌ 队列消费先 ack 再处理（崩了消息丢）
- ❌ Dockerfile 用 shell form CMD（PID 1 吞信号）
- ❌ 处理 SIGKILL（不可能 — 不可捕获，只能预防）

## 十四、参考资料

- Kubernetes Pod Lifecycle：https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- "Kubernetes Termination Lifecycle"（学习路径必看）：https://learnk8s.io/graceful-shutdown
- Go `http.Server.Shutdown` doc：https://pkg.go.dev/net/http#Server.Shutdown
- Node.js process signals：https://nodejs.org/api/process.html#signal-events
- "12-Factor App #9: Disposability"：https://12factor.net/disposability
- AWS / GCP load balancer connection draining docs
