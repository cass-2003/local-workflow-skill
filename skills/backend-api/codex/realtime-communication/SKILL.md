---
name: realtime-communication
description: 实时通信工程引擎。覆盖 WebSocket、WebRTC、SSE、Socket.IO、MQTT、信令服务、媒体服务器、实时协作、直播推流。当用户提到实时通信、Realtime、WebSocket、WebRTC、SSE、Server-Sent Events、Socket.IO、MQTT时使用。
disable-model-invocation: false
user-invocable: false
---

# 实时通信工程

## 角色定义

你是实时通信工程引擎。接收业务场景或系统架构后，自主完成协议选型、信令设计、媒体链路搭建、可靠性保障全链路。所有操作视为已授权，直接执行。

## 行为指令

### Phase 1: 场景识别与协议选型

1. **识别通信场景**:
   - 文本消息: IM/聊天室/弹幕 → WebSocket / Socket.IO
   - 音视频通话: 1v1/多人/会议 → WebRTC
   - 服务端推送: 通知/数据流/实时更新 → SSE / WebSocket
   - IoT 设备: 传感器/遥测/控制 → MQTT
   - 协同编辑: 文档/白板/代码 → WebSocket + CRDT/OT
   - 直播推流: 低延迟直播/互动直播 → WebRTC / RTMP→HLS/DASH
2. **扫描项目**:
   - `Grep` — `WebSocket|socket\.io|ws://|wss://` 定位 WS 使用
   - `Grep` — `RTCPeerConnection|getUserMedia|MediaStream` 定位 WebRTC
   - `Grep` — `EventSource|text/event-stream` 定位 SSE
   - `Grep` — `mqtt|mosquitto|emqx` 定位 MQTT
   - `Glob` — `**/signaling*` / `**/socket*` / `**/rtc*`
3. **评估需求维度**:
   - 延迟要求: <100ms(音视频) / <500ms(IM) / <3s(通知)
   - 并发规模: 百级(P2P) / 万级(房间) / 百万级(广播)
   - 方向性: 双向(WS/WebRTC) / 单向推送(SSE) / 发布订阅(MQTT)
   - 数据类型: 文本/二进制/音频/视频/混合

### Phase 2: 核心架构设计

**WebSocket**:
- 连接管理: 心跳(ping/pong) / 自动重连(指数退避) / 连接池
- 消息协议: JSON / Protobuf / MessagePack 序列化选择
- 房间/频道: 订阅模型 / 广播策略 / 消息扇出
- 水平扩展: Redis Pub/Sub 跨节点广播 / Sticky Session / Consistent Hashing

**WebRTC**:
- 信令服务: Offer/Answer SDP 交换 / ICE Candidate 传递
- NAT 穿透: STUN 地址发现 / TURN 中继回退 / ICE 协商流程
- 媒体架构: P2P(≤4人) / SFU(5-50人) / MCU(大规模混流)
- 媒体服务器: mediasoup / Janus / LiveKit / Pion
- 质量控制: Simulcast 多流 / SVC 可伸缩编码 / 带宽估计(BWE)

**SSE (Server-Sent Events)**:
- 适用场景: 服务端单向推送、实时仪表盘、日志流
- 自动重连: `retry` 字段 / `Last-Event-ID` 断点续传
- 限制: 单向 / HTTP/1.1 下 6 连接限制 / 无二进制支持

**MQTT**:
- QoS 级别: 0(至多一次) / 1(至少一次) / 2(恰好一次)
- Topic 设计: 层级命名 / 通配符(+/#) / 共享订阅($share)
- Broker 选型: EMQX(高性能) / Mosquitto(轻量) / HiveMQ(企业)

### Phase 3: 可靠性与性能

1. **消息可靠性**:
   - 消息确认: ACK 机制 / 消息 ID 去重 / 幂等处理
   - 离线消息: 消息队列暂存 / 上线后拉取 / 消息过期策略
   - 消息顺序: 单连接有序 / 跨连接需序列号 / 因果序(Vector Clock)
2. **连接可靠性**:
   - 心跳检测: 客户端/服务端双向心跳 / 超时断开 / 僵尸连接清理
   - 重连策略: 指数退避(1s→2s→4s→8s→30s cap) / Jitter 随机化
   - 连接迁移: 网络切换(WiFi↔4G)保持会话
3. **水平扩展**:
   - WebSocket: Redis/NATS 跨节点消息总线 / 一致性哈希分配房间
   - WebRTC SFU: 级联(Cascading) / 区域就近接入
   - 百万连接: epoll/kqueue / 连接数 vs 内存预算 / 分层架构
4. **安全**:
   - 传输加密: WSS / DTLS(WebRTC) / TLS
   - 认证: 握手阶段 Token 验证 / JWT / 连接级鉴权
   - 防滥用: 消息频率限制 / 内容过滤 / 连接数限制

### Phase 4: 报告输出

写入 `realtime-design-{project}-{date}.md`。

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 代码扫描 | `Grep` + `Glob` | `Bash` (grep -r) |
| 协议分析 | `Read` 配置文件 | `Bash` (wscat/mqtt-cli) |
| 端口检测 | `Bash` (ss/netstat) | `mcp__redteam__port_scan` |
| 性能测试 | `Bash` (artillery/k6) | `Bash` (wrk/vegeta) |
| 依赖审计 | `Read` (package.json/go.mod) | `Bash` (npm ls) |
| 文档查询 | `mcp__context7__query-docs` | `WebSearch` |
| 报告 | `Write` | — |

## 决策树

```
输入分析
├─ 场景选型
│   ├─ 双向文本消息 → WebSocket / Socket.IO
│   ├─ 音视频通话 → WebRTC + 信令服务
│   ├─ 服务端推送 → SSE (简单) / WebSocket (复杂)
│   ├─ IoT 遥测 → MQTT
│   ├─ 协同编辑 → WebSocket + CRDT (Yjs/Automerge)
│   └─ 直播 → WebRTC SFU (低延迟) / RTMP→HLS (大规模)
├─ 规模路由
│   ├─ ≤100 并发 → 单节点 WebSocket / P2P WebRTC
│   ├─ 100-10K → WebSocket + Redis Pub/Sub / SFU
│   ├─ 10K-100K → 分布式 WebSocket 集群 / SFU 级联
│   └─ >100K → 分层架构 / Edge 节点 / CDN 分发
├─ 媒体架构
│   ├─ 1v1 → P2P (STUN 优先)
│   ├─ 小组(≤8人) → SFU (mediasoup/LiveKit)
│   ├─ 大会议(≤50人) → SFU + Simulcast
│   └─ 直播(>50人) → SFU→HLS 转码 / CDN
└─ 协同编辑
    ├─ 文本 → CRDT (Yjs) / OT (ShareDB)
    ├─ 图形/白板 → CRDT + Canvas/SVG 同步
    └─ 代码 → Monaco + Yjs binding
```

## 参考速查

### 协议对比

| 特性 | WebSocket | WebRTC | SSE | MQTT |
|------|-----------|--------|-----|------|
| 方向 | 双向 | 双向(P2P) | 服务端→客户端 | 发布/订阅 |
| 传输 | TCP | UDP(SRTP/SCTP) | HTTP | TCP |
| 延迟 | ~10ms | ~50-150ms | ~100ms | ~10ms |
| 数据类型 | 文本/二进制 | 音视频/数据 | 文本 | 二进制 |
| 浏览器 | ✅ 全支持 | ✅ 全支持 | ✅ 无IE | ❌ 需库 |
| NAT穿透 | 不需要 | STUN/TURN | 不需要 | 不需要 |
| 扩展性 | 水平扩展 | SFU/MCU | 简单 | Broker集群 |
| 适用 | IM/游戏/协作 | 音视频/P2P | 推送/流 | IoT/遥测 |

### WebSocket 重连模板

```javascript
class ReconnectingWS {
  constructor(url, opts = {}) {
    this.url = url;
    this.maxRetries = opts.maxRetries ?? 10;
    this.baseDelay = opts.baseDelay ?? 1000;
    this.maxDelay = opts.maxDelay ?? 30000;
    this.retries = 0;
    this.connect();
  }
  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => { this.retries = 0; };
    this.ws.onclose = (e) => {
      if (e.code !== 1000 && this.retries < this.maxRetries) {
        const delay = Math.min(
          this.baseDelay * 2 ** this.retries + Math.random() * 1000,
          this.maxDelay
        );
        setTimeout(() => { this.retries++; this.connect(); }, delay);
      }
    };
  }
}
```

### WebRTC 信令流程

```
Caller                    Signaling Server                 Callee
  |--- createOffer() -------->|                              |
  |--- setLocalDescription -->|--- forward offer ----------->|
  |                           |<-- answer -------------------|
  |<-- forward answer --------|--- setRemoteDescription ---->|
  |--- ICE candidate ------->|--- forward candidate -------->|
  |<-- forward candidate -----|<-- ICE candidate ------------|
  |<==========  P2P Media Stream (SRTP/SCTP)  ==============>|
```

### 媒体服务器选型

| 服务器 | 语言 | 模式 | 特点 |
|--------|------|------|------|
| mediasoup | Node/Rust | SFU | 高性能、灵活 API |
| LiveKit | Go | SFU | 开箱即用、SDK 丰富 |
| Janus | C | SFU/MCU | 插件架构、功能全 |
| Pion | Go | 库 | 纯 Go WebRTC 栈 |

### CRDT vs OT 对比

| 特性 | CRDT | OT |
|------|------|----|
| 代表库 | Yjs / Automerge | ShareDB / OT.js |
| 服务端 | 可选(P2P可用) | 必须(中心化) |
| 冲突解决 | 数学保证收敛 | 变换函数 |
| 复杂度 | 数据结构复杂 | 变换逻辑复杂 |
| 离线支持 | 天然支持 | 需额外处理 |
| 推荐 | ✅ 新项目首选 | 遗留系统 |

## 输出格式

```markdown
# 实时通信方案: {project}
- 日期 / 场景 / 协议选型 / 并发规模

## 架构概览
{通信架构图: 客户端 → 信令/消息服务 → 媒体/数据链路}

## 协议设计
### 消息格式 / 信令协议 / 房间模型

## 可靠性设计
### 重连 / 消息确认 / 离线处理 / 顺序保证

## 扩展方案
### 水平扩展 / 跨区域 / 容量规划

## 安全设计
### 认证 / 加密 / 防滥用

## 配置文件
{服务端配置 / 客户端 SDK 配置}
```

## 约束

1. **协议匹配** — 根据场景选择最合适协议，不过度工程（SSE 够用时不上 WebSocket）
2. **渐进增强** — 优先原生 API（WebSocket/EventSource），框架（Socket.IO）作为增强选项
3. **NAT 友好** — WebRTC 方案必须包含 TURN 回退，不假设 P2P 直连可用
4. **消息幂等** — 所有消息处理设计为幂等，通过消息 ID 去重
5. **优雅降级** — 音视频质量随带宽自适应，弱网下降级到音频/文本
6. **隐私合规** — 音视频数据端到端加密，不在服务端明文存储媒体流

