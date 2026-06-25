---
name: websocket-impl
description: "WebSocket 工程实战。覆盖握手协议、frame 类型与 OPCODE、心跳 ping/pong、客户端自动重连（exponential backoff + jitter）、消息序列化（JSON/Protobuf/MsgPack）、subprotocol 协商、压缩 permessage-deflate、横向扩展（Redis pub/sub / NATS / Kafka）、Sticky session vs Pub/Sub、断线消息补偿、背压（backpressure）、CSWSH 跨站攻击、负载均衡、Socket.IO/uWebSockets/ws/Phoenix Channels 选型。当用户提到 WebSocket、ws、wss、心跳、heartbeat、ping pong、reconnect、断线重连、Socket.IO、uWebSockets、Phoenix、SSE、permessage-deflate、CSWSH、subprotocol、横向扩展实时通信 时使用。"
---

# WebSocket Implementation Skill — WS 实战

## 何时使用

- 实现实时双向通信（聊天 / 协作 / 推送 / 在线游戏）
- 排查"客户端莫名断线"/ 重连风暴
- 设计多实例部署的消息广播
- WebSocket vs SSE vs Long Polling 选型
- 评估 Socket.IO / 原生 ws / uWebSockets

## 一、何时选 WS 何时不选

| 需求 | 推荐 |
|---|---|
| 服务端 → 客户端单向推送 | **SSE**（更简单、自动重连、HTTP/2 多路复用） |
| 双向 / 低延迟 | **WebSocket** |
| 客户端 → 服务端低频提交 | **HTTP POST**（普通 API） |
| 实时性 < 1s 即可 | **Long polling** / SSE |
| 多设备同步 | WebSocket / 推送服务（FCM / APNs） |
| 文件 / 大数据流 | **HTTP/2 streaming** 或 **WebTransport** |

WS 是"双向 + 低延迟"的工具，不是默认选项。

## 二、协议基础

### 握手（HTTP Upgrade）

```
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: chat.v1
Sec-WebSocket-Extensions: permessage-deflate

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
Sec-WebSocket-Protocol: chat.v1
```

### Frame 结构

```
OPCODE 类型：
  0x0  continuation  (分片)
  0x1  text          (UTF-8 字符串)
  0x2  binary        (任意字节)
  0x8  close
  0x9  ping
  0xA  pong
  0xB-0xF  reserved
```

最大消息体：协议无硬限，**实现限**（多数 16-64 MB）。

## 三、Node.js (`ws` 库) 服务端

```typescript
import { WebSocketServer } from 'ws'
import http from 'node:http'

const server = http.createServer()
const wss = new WebSocketServer({ noServer: true })

server.on('upgrade', (req, socket, head) => {
  // 自家鉴权（cookie / token）
  if (!authenticate(req)) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n')
    socket.destroy()
    return
  }
  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit('connection', ws, req)
  })
})

wss.on('connection', (ws, req) => {
  ws.userId = extractUserId(req)
  ws.isAlive = true

  ws.on('pong', () => { ws.isAlive = true })

  ws.on('message', (data, isBinary) => {
    const msg = isBinary ? data : data.toString()
    handleMessage(ws, msg)
  })

  ws.on('close', (code, reason) => {
    cleanup(ws)
  })
})

// 心跳：每 30s 发 ping，对方未 pong 则断开
setInterval(() => {
  for (const ws of wss.clients) {
    if (!ws.isAlive) { ws.terminate(); continue }
    ws.isAlive = false
    ws.ping()
  }
}, 30_000).unref()

server.listen(8080)
```

## 四、心跳（Heartbeat）

**为什么需要**：TCP keepalive 默认 2 小时；中间 NAT / LB 可能 60s 后断开"空闲连接"。WS 需要**应用层心跳**。

```
客户端 ─ ping ──▶ 服务端
        ◀── pong ──

或反向（服务端发 ping）
```

**典型间隔**：
- 服务端 ping 客户端：30s
- 客户端等 pong 超时：5s
- 连续 N 次没 pong → 断开重连（避免半开连接）

**应用层心跳 vs 协议层 ping/pong**：
- 协议层（OPCODE 0x9 / 0xA）：库自动处理，浏览器 JS 看不到
- 应用层（自家发 `{"type":"ping"}`）：可携带业务信息（如未读数）

## 五、客户端自动重连

```typescript
class ReconnectingWS {
  private ws: WebSocket | null = null
  private attempt = 0
  private closing = false

  constructor(private url: string, private opts: { maxDelay?: number; protocols?: string[] } = {}) {
    this.connect()
  }

  private connect() {
    this.ws = new WebSocket(this.url, this.opts.protocols)

    this.ws.onopen = () => {
      this.attempt = 0
      this.onopen?.()
    }

    this.ws.onmessage = (e) => this.onmessage?.(e)

    this.ws.onclose = (e) => {
      if (this.closing) return
      // 指数退避 + 抖动
      const base = Math.min(1000 * 2 ** this.attempt, this.opts.maxDelay ?? 30_000)
      const jitter = Math.random() * base * 0.3
      setTimeout(() => this.connect(), base + jitter)
      this.attempt++
    }

    this.ws.onerror = (e) => this.onerror?.(e)
  }

  send(data: string | ArrayBufferLike) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    } else {
      // 缓冲或丢弃 — 业务自定义
      throw new Error('WebSocket not open')
    }
  }

  close() { this.closing = true; this.ws?.close() }

  onopen?: () => void
  onmessage?: (e: MessageEvent) => void
  onerror?: (e: Event) => void
}
```

**生产推荐**：用现成库 `reconnecting-websocket` / `partysocket` / `socket.io-client`。

## 六、消息协议设计

```typescript
// 永远把消息包成 envelope 而不是裸 string
type ServerMessage =
  | { type: 'pong'; ts: number }
  | { type: 'event'; event: string; data: any }
  | { type: 'error'; code: string; message: string }
  | { type: 'ack'; id: string }

type ClientMessage =
  | { type: 'ping'; ts: number }
  | { type: 'subscribe'; channel: string }
  | { type: 'unsubscribe'; channel: string }
  | { type: 'publish'; channel: string; data: any; id?: string }

// 序列化选择
JSON          // 简单 / 调试友好 / 文本帧
MessagePack   // 50% 体积 / 二进制
Protobuf      // schema-driven / SDK 自动生成
CBOR          // 类似 MsgPack
FlatBuffers   // 零拷贝读
```

**ID + ack 模式**：客户端发 `{ id: 'req-1', ... }`，服务端返 `{ type: 'ack', id: 'req-1' }`。便于 RPC 风格 + 重发幂等。

## 七、断线消息补偿

WS 断开期间错过的消息怎么办？

### 方案 1：last-seen 序号

```
服务端给每条消息带 seq 单调递增
客户端记最后收到的 seq
重连后发送 { type: 'resume', last_seq: 12345 }
服务端从存储补发 seq > 12345 的消息（保留窗口内）
```

### 方案 2：消息流（Kafka / Redis Streams）

每个用户对应一个流 / consumer group，offset 由客户端确认。

### 方案 3：状态全量重新同步

简单粗暴：重连后客户端请求"当前状态" — 适合状态量小（< 1MB）的场景。

## 八、横向扩展（多实例）

单 Node 进程 WS 连接数上限：通常 10K-100K（看消息量）。超过要分实例。

### 问题：用户 A 在 server1，用户 B 在 server2，A 发消息 B 怎么收到？

### 方案 1：Sticky session + 无跨实例广播

按 user_id hash 路由到同一实例。同实例内通信 → 简单。但有两个限制：
- 一个 user 多设备时，只能落同一实例（设备相互通信容易；与他人通信仍需广播）
- 实例间负载不均

### 方案 2：Pub/Sub backbone（推荐）

```
        ┌── server1 ──┐
client ─┤             ├── Redis Pub/Sub / NATS / Kafka
        └── server2 ──┘
```

每个 server 订阅 `channel:room-123`，收到 publish 就转发给本地连接的订阅者。

```typescript
// 简化伪码
redis.subscribe('msg', (msg) => {
  const { channel, data } = JSON.parse(msg)
  for (const ws of localSubscribersByChannel.get(channel) ?? [])
    ws.send(data)
})

// 发消息
function broadcast(channel: string, data: any) {
  redis.publish('msg', JSON.stringify({ channel, data }))
}
```

**库**：
- Socket.IO Redis Adapter
- NATS（高性能，K8s friendly）
- Pusher / Ably / Pubnub（托管）

### 方案 3：Mesh / Phoenix Channels

Erlang/Elixir 的 Phoenix Channels 节点间用 pg2 进程广播 — 内置分布式无需 Redis。

## 九、压缩（permessage-deflate）

```typescript
new WebSocketServer({
  perMessageDeflate: {
    zlibDeflateOptions: { level: 6 },
    threshold: 1024,           // 仅大于 1KB 的消息压缩
    concurrencyLimit: 10,
  },
})
```

**注意**：压缩有 CPU 开销，对小消息得不偿失。**生产建议根据消息特征调 threshold 或关闭**。

## 十、背压（Backpressure）

服务端发送速度 > 客户端接收速度 → buffer 膨胀 → OOM。

```typescript
ws.on('message', (data) => {
  // 慢客户端：检查 bufferedAmount
  if (ws.bufferedAmount > 1024 * 1024 * 10) {   // 10MB
    ws.close(1009, 'message too big')   // 或主动节流
    return
  }
  ws.send(data)
})
```

```typescript
// uWebSockets.js 原生支持 backpressure
const ok = ws.send(data)
if (!ok) {
  // buffer 满，等 drain
  ws.cork(() => { /* 暂停业务推送 */ })
}
```

## 十一、安全

### CSWSH（Cross-Site WebSocket Hijacking）

WS 握手是 HTTP，自动带 cookie。攻击者站点的 JS 可发起 WS 连接到你的服务端，cookie 被自动带上 → 用户身份被劫持。

**防护**：
1. **校验 `Origin` 头**（强制白名单）
2. 不仅靠 cookie，**额外用 token**（query 参数 / 第一条消息发 JWT）
3. 用 SameSite=Strict cookie

```typescript
server.on('upgrade', (req, socket, head) => {
  const origin = req.headers.origin
  if (!ALLOWED_ORIGINS.has(origin)) {
    socket.write('HTTP/1.1 403 Forbidden\r\n\r\n')
    socket.destroy()
    return
  }
  // ...
})
```

### 拒绝服务

- 未鉴权连接超时（5s 内必须发 auth 消息否则断）
- 限连接数 / IP / user
- 限消息大小 / 消息频率（per-connection rate limit）

### TLS

`wss://` 而非 `ws://`。LB 终止 TLS 后通常用 `ws://` 内网，但避免明文走公网。

## 十二、负载均衡

```nginx
# Nginx 反向代理 WS
upstream ws_backend {
  ip_hash;             # sticky session
  server backend1:8080;
  server backend2:8080;
}

server {
  location /ws {
    proxy_pass http://ws_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;       # 长连接超时调大
    proxy_send_timeout 3600s;
  }
}
```

云 LB：
- AWS ALB：原生支持 WS（idle timeout 4000s 上限）
- Cloudflare：原生支持 + 免费
- GCP HTTPS LB：支持 + 全局
- Cloudflare Workers Durable Objects / Hibernating WS：边缘原生

## 十三、库选型

| 库 | 语言 | 特点 |
|---|---|---|
| **ws** | Node | 原生协议，最快但要自己实现高层逻辑 |
| **uWebSockets.js** | Node (C++) | 极致性能（Fastify 用其底层） |
| **Socket.IO** | Node + Browser | room / namespace / 自动 fallback / 自动重连，但**不是标准 WS**（私有协议） |
| **PartySocket** | 跨边缘 | Cloudflare Workers / Durable Objects 友好 |
| **Phoenix Channels** | Elixir | 内置 pub/sub + presence + 分布式 |
| **Tower / axum-tungstenite** | Rust | 高性能 |
| **Centrifugo** | Go server | 多协议（WS/SSE/HTTP-stream），客户端 SDK 全 |
| **Ably / Pusher / Pubnub** | SaaS | 托管，无需自建基础设施 |
| **MQTT over WS** | 任 | IoT 场景标准 |

## 十四、Socket.IO 特殊点

- **不是标准 WebSocket**（自家协议，握手 + 心跳 + room 等扩展）
- 自带 fallback：long-polling → WS upgrade
- 支持 room / namespace / acknowledgement / 自动重连
- 客户端必须用对应 socket.io-client（不能用浏览器原生 `WebSocket`）

适合：聊天 / 协作类，开箱即用。
不适合：与第三方 / 移动客户端互通（标准 WS 通用）。

## 十五、Don'ts

- ❌ 在 WS 上传 100MB 文件 — 用 HTTP / S3 multipart 更合适
- ❌ 不做心跳 — 半开连接积累
- ❌ 重连无 jitter — 服务挂时所有客户端同时苏醒（thundering herd）
- ❌ 客户端 onclose 立即 connect 无退避 — 服务挂时拒绝请求 100% CPU 风暴
- ❌ 仅靠 cookie 鉴权 WS — CSWSH 漏洞
- ❌ 不校验 Origin
- ❌ 单实例部署但流量 > 单机能力 — 设计不可扩展
- ❌ Sticky session 但 user 多设备 — 设备落不同实例不通信
- ❌ 用 WS 做单向推送 — SSE 更适合（自动重连 + HTTP/2 多路）
- ❌ JSON 消息体里塞二进制（base64）— 用 binary frame
- ❌ 不限连接数 — 一个用户开 1000 个 tab 把实例打挂
- ❌ Nginx `proxy_read_timeout` 用默认 60s — WS 长连接被断

## 十六、调试技巧

```bash
# 命令行客户端
websocat wss://example.com/ws

# Chrome DevTools → Network → WS → Messages tab 看双向流量
# Wireshark 可解析未压缩 WS frame
# Charles / mitmproxy 抓包 wss
```

```javascript
// 客户端调试
ws.addEventListener('message', e => console.log('recv:', e.data))
const _send = ws.send.bind(ws)
ws.send = d => { console.log('send:', d); _send(d) }
```

## 十七、参考资料

- RFC 6455 (WebSocket Protocol)
- MDN WebSocket API：https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
- "WebSockets vs Server-Sent Events vs Long Polling" 对比文章
- ws library docs：https://github.com/websockets/ws
- uWebSockets.js：https://github.com/uNetworking/uWebSockets.js
- Socket.IO docs：https://socket.io/docs/v4/
- Phoenix Channels：https://hexdocs.pm/phoenix/channels.html
- "Real-Time Web at Scale" 系列博客
- Cloudflare Hibernating WebSockets：https://developers.cloudflare.com/durable-objects/api/websockets/
