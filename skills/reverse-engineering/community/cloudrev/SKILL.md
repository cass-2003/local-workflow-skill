---
name: cloud-client-reverse-engineering
description: 云客户端、Agent 与边缘组件逆向。AWS SSM Agent / Azure Hybrid / GCP Ops Agent / 阿里云 / 监控 SDK / Cloudflare/Fastly/Akamai 边缘 / Tailscale/Zerotier/WireGuard / Sentry/DataDog/NewRelic Agent。还原 Go binary / .NET single-file / 静态链接 Rust，识别上行通道（HTTPS/gRPC/MQTT/QUIC）、配置/凭据存储、远程命令通道。
---

# 云客户端 / Agent 逆向

## 适用场景

- 主机上跑着一个不知名的 Agent，要回答："是哪家产品？通哪个云？走什么协议？发什么数据回去？凭据怎么存？能否远程下命令？"
- 自审 SaaS / 监控 / RUM / APM Agent 的数据收集面（合规 / 数据出境 / 隐私）。
- 边缘组件审计：CDN worker / Lambda@Edge / Cloudflare Workers / 私网 mesh（Tailscale/Zerotier）。
- Go / Rust / .NET 静态链接二进制反编译（云 Agent 主流栈）。

## 不适用

- OCI 镜像层 / 镜像扫描 → `containerrev`。
- IoT 端侧 SDK → `iotrev`。
- 通用 Linux/Windows/Mac 二进制 → 平台技能 + `binrev`。

## 主流 Agent 速识

| Agent | 二进制名 / 服务名 | 默认监听 / 上行 |
| --- | --- | --- |
| **AWS SSM Agent** | `amazon-ssm-agent` (Go) | 443 → `ssm.<region>.amazonaws.com`，常驻长连接 |
| **AWS CloudWatch Agent** | `amazon-cloudwatch-agent` (Go) | 443 → `monitoring.<region>.amazonaws.com` |
| **Azure Linux Agent (waagent)** | `waagent` (Python) | HTTP → `168.63.129.16` (IMDS) |
| **Azure Monitor Agent (AMA)** | `mdsd / azuremonitoragent` | 443 → `*.monitor.azure.com` |
| **GCP Ops Agent** | `google-cloud-ops-agent` (Go + Fluent Bit) | 443 → `logging.googleapis.com` |
| **GCP Guest Agent** | `google_guest_agent` (Go) | gRPC over 443 → `metadata.google.internal` (169.254.169.254) |
| **阿里云 cloud-init / Aegis** | `AliYunDun / AliYunDunUpdate` | 443 / 80 → `*.aliyuncs.com` |
| **腾讯云 BHL** | `barad_agent / YDService` | 443 → `*.tencentcs.com` |
| **DataDog Agent** | `datadog-agent` (Go) | 443 → `intake.<region>.datadoghq.com` |
| **NewRelic Agent** | `newrelic-infra` (Go) | 443 → `infra-api.newrelic.com` |
| **Sentry SDK** | 进程内库 | 443 → `sentry.io` (POST /api/{project}/store/) |
| **Sysdig Agent** | `sysdig-agent` | 443/6666 → `collector*.sysdigcloud.com` |
| **Crowdstrike Falcon** | `falconctl / falcon-sensor` | 443 → `*.cloudsink.net` |
| **SentinelOne** | `sentinelone-agent` | 443 → `*.sentinelone.net` |
| **Cloudflare WARP** | `warp-svc / warp-cli` | UDP 1701/2408 → `*.cloudflareclient.com` |
| **Tailscale** | `tailscaled` (Go) | UDP 41641 → `*.tailscale.com` (DERP relay) |
| **Zerotier** | `zerotier-one` (C++) | UDP 9993 → `*.zerotier.com` (planet/moon) |
| **WireGuard** | `wg-quick / wireguard-go` | UDP 51820 → 任意 |
| **Cloudflared** | `cloudflared` (Go) | TLS / QUIC → `*.cfargotunnel.com` |
| **ngrok agent** | `ngrok` (Go) | TLS → `*.ngrok.com` |
| **Fly.io agent** | `flyctl-agent` | … |
| **k3s / k3os agent** | `k3s` (Go single binary, 50+ MB) | API server 6443 + WebSocket → kine/etcd |

## 二进制识别套路

```bash
# 第一步：file + strings + 大小特征
file myagent
ls -lh myagent           # Go binary 通常 5-50 MB；C 写的 100KB-3MB；Rust 5-15 MB；.NET single-file 30-200 MB
sha256sum myagent

# Go binary 标志（最常见）
strings myagent | grep -E '^go\.buildid|^buildinfo$|/usr/local/go/src/'
strings myagent | grep -E 'github\.com/.+|gitlab\.com/.+|golang\.org/x/' | head -30
strings myagent | grep -oE 'go[0-9]+\.[0-9]+\.[0-9]+' | sort -u   # Go 版本

# 用 GoReSym 提取 Go 符号 + Buildinfo（Mandiant 出品）
goresym -m myagent
goresym -d -p "main.run" -t myagent

# 或 Go 自带：runtime.buildVersion
go version myagent                                # 简单粗暴
strings myagent | grep -A1 'Go buildinf'

# Rust binary 标志
strings myagent | grep -E '_$LT$|panic_handler|core::panic|alloc::raw_vec'
strings myagent | grep -E 'rustc-[0-9]'
# 反混淆 mangled 名
echo '_RNvCs1SCq3Oyq4w_3foo3bar' | rustfilt

# .NET single-file
file myagent | grep -i 'PE32+ executable'
xxd myagent | head -5   # 起始 MZ
# .NET single-file 内嵌 .NET runtime + 应用 dll，bundle marker
strings myagent | grep -E 'Microsoft\.AspNetCore|System\.Runtime|coreclr\.dll|System\.Private\.CoreLib'
# 工具: ILSpy / dnSpyEx 直接打开新版可识别 single-file bundle
# 或 dotnet bundle extractor: github.com/Loneman/SingleFileExtractor

# Node.js single binary (pkg / node-pkg / nexe)
strings myagent | grep -E 'node\.js v[0-9]+|pkg/dictionary'
# 工具: pkg-unpacker / pkg2bin → 拿到内嵌的 V8 snapshot
```

## Go binary 反编译

```bash
# Ghidra 11+ 内置 Go support，自动识别 string table + interface table
analyzeHeadless ./projdir proj1 -import myagent \
    -postScript GoStringTransform.java \
    -postScript GoTypeRecovery.java

# IDA Pro 9+ 自带 Go loader (golang_loader)
# 旧版需要插件: idagolanghelper / golang_loader_assist

# 第三方专门工具
goreversal myagent                     # gore (Go reverse) 的 CLI
GolangBuildInfo myagent

# 看依赖
go version -m myagent                  # 列出依赖模块版本（非常有价值）
# 输出例:
#   path    main
#   mod     main    (devel)
#   dep     github.com/gorilla/mux  v1.8.0  h1:...
#   dep     google.golang.org/grpc  v1.50.0 h1:...
```

Go binary 反编译要点：
- **goroutine** = `runtime.newproc` 创建，`go` 关键字编译成调用 newproc
- **interface 调用** = (*itab + data) 双指针；调用走 itab 中 fun 数组
- **defer / panic / recover** = 编译器塞 `runtime.deferproc` / `runtime.gopanic` / `runtime.gorecover`
- **string** = `(ptr, len)` 结构；slice = `(ptr, len, cap)`
- **map** = `runtime.hmap` 哈希表
- **GC roots** 标记函数前序 stackmap

## 配置 / 凭据 / 状态文件位置

```bash
# Linux
ls -la /etc/<agent>/                 # 主配置
ls -la /var/lib/<agent>/             # 状态 + 缓存
ls -la /var/log/<agent>/             # 日志
ls -la ~/.config/<agent>/            # 用户级
ls -la /run/<agent>/                 # PID + socket

# Windows
ls 'C:\ProgramData\<vendor>\<agent>\'
ls 'C:\Program Files\<vendor>\<agent>\'
ls 'C:\Users\<user>\AppData\Roaming\<vendor>\'
reg query 'HKLM\SOFTWARE\<vendor>'

# macOS
ls /Library/Application\ Support/<vendor>/
ls /usr/local/<agent>/
ls ~/Library/Application\ Support/<vendor>/
launchctl list | grep -i <agent>

# 常见凭据存放点
- AWS Agent: /var/lib/amazon/ssm/registration  +  /etc/amazon/ssm/...
- DataDog:   /etc/datadog-agent/datadog.yaml (api_key)
- Sentry:    在应用代码里硬编码 DSN (https://<key>@sentry.io/<project>)
- Cloudflared: ~/.cloudflared/cert.pem  +  config.yml
- Tailscale:  /var/lib/tailscale/tailscaled.state (json, 含 NodeKey)
- Zerotier:   /var/lib/zerotier-one/identity.secret
- WireGuard:  /etc/wireguard/*.conf  (PrivateKey)

# 提取（自家 host 上，授权审计）
cat /etc/datadog-agent/datadog.yaml | grep -i api_key
sudo cat /var/lib/tailscale/tailscaled.state | jq
```

## 抓 Agent 上行流量

```bash
# 1) 基线：netstat / ss 看端到端连接
ss -tnp | grep -i agent
lsof -p $(pgrep -f agent) -nP -i

# 2) 抓包（先把 HTTPS 解开：CA 投放 + SSLKEYLOGFILE / mitmproxy 透明代理）
# Linux: 把 /etc/ssl/certs 里塞自家 CA，让 Agent 信任
sudo cp my-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# 用 mitmproxy 透明拦
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -m owner ! --uid-owner root -j REDIRECT --to-port 8080
mitmproxy --mode transparent --listen-port 8080 --ssl-insecure

# Go 程序常因 go-tls 默认信任 system CA 而被拦; 但有些 Agent 内嵌 CA 池 → 必须 patch binary 或 hook (Frida)

# 3) Frida 拦 Go binary 的 TLS（无符号难拦，用 BoringSSL 内部函数 ssl_verify_peer_cert）
frida -p $(pgrep agent) -l hook.js
```

```js
// hook.js: 关 Go 程序的 cert 验证（仅自家测试机）
const sslVerify = Module.findExportByName(null, 'crypto/tls.(*Conn).clientHandshake');
// Go 不导出符号，需要先 GoReSym 找地址再 Module.getBaseAddress(...)+offset
```

## gRPC / Protobuf 还原

```bash
# Agent 大量走 gRPC，service 定义在二进制里
# 1) protobuf 字段提取
strings myagent | grep -oE '\.proto\b|\bRpc\b|.*\.Service$' | head -20

# 2) 找 service 表 (Go: grpc.ServiceDesc 全局)
grep -aoE '[a-z]+\.[A-Za-z]+/[A-Za-z]+' myagent | sort -u | head -30
# 输出常含: cloudprovider.MetricsService/Push  之类

# 3) 反序列化抓到的 protobuf
protoc --decode_raw < captured.bin
# 知道 .proto 后用 -I -decode 精确解
protoc --decode=foo.bar.MyMsg ./myagent.proto < captured.bin

# 4) 工具
- grpc-tools / grpcurl                        # gRPC 客户端，反射 list/describe
- bloomrpc / kreya                             # GUI
- protobuf-inspector                           # 推测字段类型
- pbtk (protobuf toolkit)                      # 从二进制提 protobuf 描述
```

## 边缘组件 / mesh 速识

```text
Cloudflare Workers / Lambda@Edge / Fastly Compute@Edge:
  实际是 V8 isolate / WASM 沙箱跑用户代码
  访问限制大, 无 fs 无 network 默认
  逆向时拿 wrangler tail 抓日志, 或 dump bundle 后 webrev

Tailscale:
  控制平面: HTTP 长连接 → coordination server (登录端)
  数据平面: WireGuard UDP P2P (NAT 穿透 + DERP relay 兜底)
  状态文件 tailscaled.state 含 NodeKey (private), 一旦泄漏可冒充节点
  逆向: Go binary, github.com/tailscale/tailscale 完全开源, 直接对照源码

Zerotier:
  控制平面: planet/moon root 节点
  数据平面: P2P / TURN-like; 自家加密
  identity.secret 含 25 字节 Curve25519 私钥
  开源, 看源 + 反编译

WireGuard:
  内核模块 (wireguard.ko) 或用户态 (wireguard-go)
  PrivateKey 在 /etc/wireguard/*.conf, 读到就能解流量
  协议简单: Noise IK handshake + ChaCha20-Poly1305 packet

ngrok / Cloudflared / frp / rathole:
  内网穿透，长连接拉通公网
  通常: TLS over 443 / QUIC / 自家 binary protocol
  抓: 拿 token + endpoint → 用 ngrok-cli 自己起 tunnel 复现
```

## 监控 / RUM / APM SDK 数据收集面

```text
Sentry:
  POST /api/{project}/store/  with X-Sentry-Auth header
  payload = JSON: {event_id, exception, stacktrace, request, user, ...}
  默认 PII: 用户名、IP、cookies、source code 上下文 5 行

DataDog:
  POST 到 intake.datadoghq.com
  metrics / logs / traces / RUM 多种端点
  api_key 在 header 或 query
  RUM SDK 收集: URL, click, network, errors, viewport, session

NewRelic:
  RPM Agent 上报 (browser/mobile/infra)
  类似 DataDog, 多通道

PostHog / Mixpanel / Amplitude:
  POST /capture (PostHog) /track (Mixpanel)
  事件 JSON, 含 distinct_id + properties

合规审计要点:
  - 是否带 IP / Email / phone / cookie 这些 PII
  - 是否带源码片段（Sentry 默认带）
  - 数据出境（境外 SaaS）是否有合规说明
  - 是否能配置 sample rate / scrubbing / before_send hook
```

## 实战入口

- **Mandiant blog** — Cloud Agent 逆向典型 writeup（FLARE）。
- **AWS Security Workshops / Azure Security Lab / GCP Cloud Security Sandbox**。
- **Cloudreach / Hacking The Cloud (hackingthe.cloud)** — 云攻防资料库。
- **flAWS / flAWS2 / pwnedlabs.io** — 云 CTF 靶场。
- **公开样本: Crowdstrike / SentinelOne / Sysdig 报告附件** — 常含 IOC + Agent 二进制特征。
- **DEFCON Cloud Village / SANS Cloud Track**。

## 自检（拿到一个 Agent 30 分钟内回答）

1. 二进制类型（Go / Rust / .NET / Python frozen / Node pkg / C 静态）？
2. 厂家 + 版本？开源还是闭源？
3. 配置文件 / 凭据 / 状态文件路径？提取得到的 token 是什么形态？
4. 上行域名 / IP / 端口 / 协议（HTTPS / gRPC / WebSocket / QUIC / UDP 自家）？
5. 是否能远程下命令（双向通道）？是 SSE / WebSocket / gRPC stream / MQTT？
6. 数据收集面（PII / 凭据 / 文件 / 流量）？是否本地缓冲 + 离线上传？
7. 启动方式（systemd / launchd / Service / cron / 嵌入 init）？是否被 fail-open 设计？

## 相邻技能

- `binrev` / `linuxrev` / `winrev` / `macrev` — 平台底层与函数级。
- `containerrev` — 镜像内 Sidecar / DaemonSet / init container 形态。
- `cryptrev` — Agent 与云之间的 TLS / 自家加密 / pin 校验。
- `protrev` — 上行协议字段位级（自家 binary / gRPC / MQTT）。
- `webrev` — 浏览器 RUM / 监控 SDK / Service Worker。
- `mrev` — 移动端监控 SDK 形态。
- `iotrev` — 边缘 IoT 容器 + Agent。
- `sdkrev` — 闭源云 SDK / 预编译 .a/.so/.dylib。
- `fwrev` — 边缘设备固件中嵌入的云 Agent。