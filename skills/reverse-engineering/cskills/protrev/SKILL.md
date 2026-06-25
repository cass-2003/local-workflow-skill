---
name: protocol-reverse-engineering
description: 私有 / 自家网络协议逆向。抓 pcap / mitm / Frida hook send-recv，识别 framing（length-prefix / TLV / chunked / delimiter）、字段类型（counter / timestamp / length / flags / checksum）、状态机；TLS 1.2/1.3 / DTLS / QUIC / HTTP/2/3 / gRPC / MQTT / CoAP / AMQP / RESP / Memcached；JA3/JA4 指纹；scapy / mitmproxy / Wireshark Lua dissector / 自家重放与 fuzz。
---

# 私有协议逆向

## 适用场景

- 抓到一份 pcap / 自家二进制流，要回答："这是什么协议？字段分布？状态机？有无加密 / 签名 / 重放保护？"
- 厂商自家协议（IoT、游戏、桌面客户端、SDK 上报）的字段位级还原。
- 协议加密层识别：TLS / DTLS / QUIC / 自家 XOR/RC4/AES + 序列号。
- 协议 fuzz：boofuzz / AFLNet / Mutiny harness 编写。
- 重放 / 重组 / 中间人：在合规复测场景下做端到端流量改写。

## 不适用

- 文件格式（不在网络流中） → `fmtrev`。
- 物理层（CAN / 蓝牙 / Wi-Fi / Zigbee） → `iotrev` / `hwrev`。
- 应用层完整 App → 各平台技能。
- Web/HTTP 后端 → `webrev`。

## 起手抓包栈

```bash
# 通用抓包
tcpdump -i any -nn -s0 -w out.pcap host 192.168.1.10
tcpdump -i any -nn -s0 -w out.pcap port 12345
tshark -i any -f 'host 192.168.1.10' -w out.pcap

# Linux 透明代理（强）
# 流量重定向到 mitmproxy
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -m owner ! --uid-owner $(id -u proxy) -j REDIRECT --to-port 8080
sudo mitmproxy --mode transparent --listen-port 8080

# Linux 不透明 (SOCKS / HTTP)
mitmproxy --mode regular --listen-port 8080

# macOS PF
echo 'rdr pass on en0 inet proto tcp from any to any port 443 -> 127.0.0.1 port 8080' | sudo pfctl -f -
sudo pfctl -e

# Windows: WireGuard / Proxifier / Charles / Fiddler
# 系统代理 + 信任 mitmproxy CA

# 已注入 TLS：mitmproxy 自动颁证；客户端要信任 mitmproxy CA
mitmproxy --listen-port 8080 --ssl-insecure

# Frida hook 应用层 send/recv（绕过 TLS 完全）
frida -U -f com.target.app -l hook_socket.js
```

```js
// hook_socket.js  — 应用层抓明文
['SSL_write', 'SSL_read', 'BIO_write', 'BIO_read'].forEach(fn => {
    var addr = Module.findExportByName('libssl.so', fn) ||
               Module.findExportByName('libboringssl.so', fn);
    if (!addr) return;
    Interceptor.attach(addr, {
        onEnter: function (args) {
            this.buf = args[1];
            this.len = args[2].toInt32();
        },
        onLeave: function (retval) {
            if (retval.toInt32() > 0) {
                var bytes = Memory.readByteArray(this.buf, Math.min(retval.toInt32(), 256));
                console.log(fn, hexdump(bytes, { offset: 0, length: bytes.byteLength, ansi: true }));
            }
        }
    });
});

// Java OkHttp / Android HttpURLConnection
Java.perform(function () {
    var URL = Java.use('java.net.URL');
    URL.openConnection.implementation = function () {
        console.log('URL.openConnection ' + this.toString());
        return this.openConnection.call(this);
    };
});

// iOS NSURLSession
var dataTask = ObjC.classes.NSURLSessionDataTask;
// ... hook 同理
```

## TLS 识别与脱壳

```text
TLS 1.2 握手:
  ClientHello → ServerHello → Certificate → ServerHelloDone
  → ClientKeyExchange + ChangeCipherSpec + Finished
  → ServerChangeCipherSpec + Finished
  之后是 application data (TLS Record)

TLS 1.3 握手 (RFC 8446, 现代主流):
  ClientHello → ServerHello + EncryptedExtensions + Certificate + CertificateVerify + Finished
  → Finished
  之后 application data
  关键变化: 加密提前到 ServerHello 后

DTLS = TLS over UDP, 多了重传与 epoch
QUIC = UDP-based, 集成 TLS 1.3 + HTTP/2-3 + 0-RTT, RFC 9000+
```

```bash
# JA3 / JA4 客户端指纹
# 抓 ClientHello → 计算指纹哈希
# Wireshark: tls.handshake.ja3 (近版本内置)
# CLI:
ja3 -i pcap input.pcap
ja4 input.pcap                                              # FoxIO/ja4

# 自家计算
# JA3: SSLVersion,Cipher,SSLExtension,EllipticCurve,EllipticCurvePointFormat
# MD5 hash
# JA4: 改进版，引入 ALPN + extensions order

# SSLKEYLOGFILE: 标准的握手 key dump 方式（浏览器自带）
export SSLKEYLOGFILE=/tmp/sslkeys.log
chromium                                                    # 浏览器自动写
firefox

# Wireshark 加载
# Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename = /tmp/sslkeys.log
# 然后解密

# 应用层强制 keylog (Frida)
frida -U -f com.target.app -l keylog.js
```

```js
// keylog.js — 把 boringssl 的 master secret dump 出来
var SSL_CTX_set_keylog_callback = Module.findExportByName(null, 'SSL_CTX_set_keylog_callback');
// 或者直接 hook SSL_log_secret
// 详见: github.com/sensepost/objection / github.com/maoabc/sslparams
```

## 应用层 framing 速识

```text
A) Length-prefix
   [length(N)][payload]
   N = 1/2/4/8 bytes, big/little endian
   length 含 / 不含 自身 / 总长 - 头 长

B) Delimiter
   payload + 分隔符 (\r\n / \0 / 自定义)
   常见: HTTP / SMTP / IRC / Redis RESP

C) TLV
   [type][length][value] 链
   常见: BGP / DICOM / DNS RR / OPC UA

D) Chunked
   多个 [chunk_size + payload] 组，0 长结束
   HTTP/1.1 chunked transfer / WebSocket frames

E) Fixed
   定长包，靠 opcode 区分类型

F) Tagged + varint
   protobuf 类，每字段独立 tag + len + value
   gRPC / Cap'n Proto / Thrift compact

G) Frame + bit field
   IEEE 802.x / IP / TCP / UDP
   按位定义，需要按位解
```

判定方法：

```bash
# 抓一些样本，看每包前 2-8 字节
tcpdump -i any -nn -X -A 'host 1.2.3.4 and port 12345' | head -50
# 或 wireshark Follow TCP Stream → Show data as Hex Dump

# 自动猜：检查前 4 字节是否 = (该包大小 - 头长)
python3 - <<'PY'
import struct
from scapy.all import rdpcap, TCP, Raw
pkts = rdpcap('out.pcap')
streams = {}
for p in pkts:
    if not p.haslayer(TCP): continue
    if not p.haslayer(Raw): continue
    key = (p[0][1].src, p[TCP].sport, p[0][1].dst, p[TCP].dport)
    streams.setdefault(key, b'').__iadd__(b'')              # 不会修改 dict, 用列表
# 简化：逐包看
for p in pkts:
    if not p.haslayer(Raw): continue
    raw = bytes(p[Raw])
    if len(raw) < 8: continue
    le = struct.unpack('<I', raw[:4])[0]
    be = struct.unpack('>I', raw[:4])[0]
    print(f"pkt {len(raw):5d}B  first_u32_LE={le:#10x}  BE={be:#10x}", end='')
    if le + 4 == len(raw) or le == len(raw):
        print(' <- LE length match')
    elif be + 4 == len(raw) or be == len(raw):
        print(' <- BE length match')
    else:
        print()
PY
```

## 字段类型推断

```text
计数器:    单调递增，按时间或包顺序递增 1
时间戳:    epoch (32 bit unix sec) / 64 bit (ms / us / 100ns) / NTP (seconds since 1900)
           Apple Mach absolute time (mach_absolute_time, ns)
            Windows FILETIME (100ns since 1601)
长度:      值在 [0, packet_size - 头] 范围
偏移:      值 < packet_size, 指向 packet 内某结构
ID/UUID:   随机 / 自递增 / 厂家 OUI 前缀
版本:      固定的小数 (0x01, 0x02, ...)
flags:     单字节 / 位掩码
opcode:    小整数集合 {0x01, 0x02, ...}, 决定后续 payload 结构
端口:      网络字节序的 u16 (常见 80/443/22/...)
IPv4:      4 字节
IPv6:      16 字节
hash:      固定长度 + 高熵 (16=MD5, 20=SHA1, 28=SHA224, 32=SHA256, 48=SHA384, 64=SHA512)
HMAC:      同 hash, 但前后跟可变 payload
nonce/IV:  随机字节, 跟密文一起出现
public key: ECDSA P-256 = 64+1=0x04|x|y, 65 字节
             RSA 2048 modulus = 256 字节
             X25519 = 32 字节
密文:      高熵 (~8.0), 长度 = 明文 + AEAD tag (16 字节)
ASCII:     可读字节 0x20-0x7e
UTF-8:     多字节 (0xc0-0xf7 起始)
```

```python
# 自动给字节打类型 tag
import math, struct
from collections import Counter

def entropy(b):
    if not b: return 0
    c = Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def is_printable(b):
    return all(0x20 <= x < 0x7f or x in (9,10,13) for x in b)

def is_likely_timestamp(v):
    return 1_500_000_000 < v < 2_000_000_000                # 2017-2033 epoch

def classify(buf):
    n = len(buf)
    h = entropy(buf)
    if n == 4 or n == 8:
        v_le = int.from_bytes(buf, 'little')
        v_be = int.from_bytes(buf, 'big')
        if is_likely_timestamp(v_le): return f"timestamp LE {v_le}"
        if is_likely_timestamp(v_be): return f"timestamp BE {v_be}"
    if h > 7.5: return f"high entropy ({h:.2f}, likely encrypted/hash)"
    if is_printable(buf): return f"ASCII text"
    return f"unknown ({h:.2f})"
```

## Wireshark dissector (Lua)

```lua
-- my_protocol.lua, 放 ~/.config/wireshark/plugins/
local p = Proto("MyProto", "My Custom Protocol")

local f_magic   = ProtoField.uint32("myproto.magic", "Magic", base.HEX)
local f_version = ProtoField.uint16("myproto.version", "Version")
local f_flags   = ProtoField.uint16("myproto.flags", "Flags", base.HEX)
local f_length  = ProtoField.uint32("myproto.length", "Payload Length")
local f_opcode  = ProtoField.uint8 ("myproto.opcode", "Opcode")
local f_payload = ProtoField.bytes ("myproto.payload", "Payload")

p.fields = { f_magic, f_version, f_flags, f_length, f_opcode, f_payload }

function p.dissector(buf, pinfo, tree)
    if buf:len() < 13 then return end
    pinfo.cols.protocol = "MyProto"
    local t = tree:add(p, buf(0, buf:len()))
    t:add(f_magic,   buf(0, 4))
    t:add(f_version, buf(4, 2))
    t:add(f_flags,   buf(6, 2))
    local len = buf(8, 4):le_uint()
    t:add_le(f_length, buf(8, 4))
    t:add(f_opcode,  buf(12, 1))
    t:add(f_payload, buf(13, len))
end

DissectorTable.get("tcp.port"):add(12345, p)
```

加载后 Wireshark 直接显示自家协议字段。

## scapy custom layer

```python
from scapy.all import Packet, BitField, ShortField, IntField, FieldLenField, StrLenField, bind_layers, TCP

class MyProto(Packet):
    name = "MyProto"
    fields_desc = [
        IntField("magic", 0x4D594D59),
        ShortField("version", 1),
        ShortField("flags", 0),
        FieldLenField("length", None, length_of="payload"),
        BitField("opcode", 0, 8),
        StrLenField("payload", "", length_from=lambda p: p.length),
    ]

bind_layers(TCP, MyProto, dport=12345)
bind_layers(TCP, MyProto, sport=12345)

# 构造发送
from scapy.all import IP, TCP, sr1
pkt = IP(dst='1.2.3.4')/TCP(dport=12345)/MyProto(opcode=0x42, payload=b"hello")
sr1(pkt)

# 解析 pcap
from scapy.all import rdpcap
pkts = rdpcap('out.pcap')
for p in pkts:
    if MyProto in p:
        print(p[MyProto].show())
```

## 标准协议速查

### HTTP/1.x

```text
请求:
  METHOD path HTTP/1.x\r\n
  Header: value\r\n
  Header: value\r\n
  \r\n
  body (可选, 长度看 Content-Length 或 Transfer-Encoding: chunked)

响应:
  HTTP/1.x STATUS REASON\r\n
  Header: value\r\n
  \r\n
  body
```

### HTTP/2

```text
二进制 frame:
  [length(3)][type(1)][flags(1)][stream_id(4)][payload]
  type: 0x00 DATA / 0x01 HEADERS / 0x03 RST_STREAM / 0x04 SETTINGS / 0x06 PING ...
  HEADERS 用 HPACK 压缩
```

### HTTP/3 (over QUIC)

```text
基于 QUIC UDP, 用 QPACK 替 HPACK
单连接多 stream，无 head-of-line blocking
```

### gRPC

```text
HTTP/2 + protobuf
路径: /<service>/<method>
header: grpc-status, grpc-message, content-type=application/grpc
body: 1 byte (compression flag) + 4 bytes (length) + protobuf message
```

```bash
grpcurl -plaintext server:50051 list                        # 列服务（需 reflection）
grpcurl -plaintext server:50051 list mypkg.MyService
grpcurl -plaintext -d '{"x":1}' server:50051 mypkg.MyService/Method

# 无 reflection 时
grpcurl -proto my.proto -plaintext -d '{...}' server:50051 mypkg.MyService/Method

# bloomrpc / kreya GUI
```

### MQTT

```text
端口 1883 (明文) / 8883 (TLS)
固定头 (1+长度可变 varlen) + 可变头 + 载荷
控制类型 (high 4 bit of byte 0):
  0x10 CONNECT     0x20 CONNACK
  0x30 PUBLISH     0x40 PUBACK    0x50 PUBREC   0x60 PUBREL  0x70 PUBCOMP
  0x80 SUBSCRIBE   0x90 SUBACK
  0xa0 UNSUBSCRIBE 0xb0 UNSUBACK
  0xc0 PINGREQ     0xd0 PINGRESP
  0xe0 DISCONNECT
  0xf0 AUTH        (MQTT 5)
```

```bash
mosquitto_sub -h broker -t '#' -v                           # 监听所有 topic
mosquitto_pub -h broker -t test -m hello
mqtt-explorer                                               # GUI
```

### CoAP (RFC 7252)

```text
端口 5683 (UDP) / 5684 (DTLS)
4 字节固定头 + Token + Options + Payload
Type: CON / NON / ACK / RST
Code: 0.01 GET / 0.02 POST / 0.03 PUT / 0.04 DELETE / 2.xx success / 4.xx client err / 5.xx server err
```

```bash
coap-client -m get coap://server/sensor
aiocoap-client coap://server/sensor
libcoap / californium / go-coap
```

### AMQP / RabbitMQ

```text
0-9-1 (主流) / 1.0 (OASIS)
端口 5672 / 5671 (TLS)
帧: METHOD / HEADER / BODY / HEARTBEAT
Wireshark 自带 dissector
```

### Redis RESP

```text
端口 6379, 文本协议
+OK\r\n           Simple String
-Error msg\r\n    Error
:1234\r\n         Integer
$5\r\nhello\r\n   Bulk String
*2\r\n+OK\r\n+a\r\n  Array

```

```bash
redis-cli -h 127.0.0.1 -p 6379
redis-cli --raw GET key
# 协议: nc 1.2.3.4 6379 → 直接发文本
```

### Memcached

```text
端口 11211
两种协议:
  ASCII text (老): "get key\r\n" / "VALUE key 0 5\r\nhello\r\nEND\r\n"
  Binary (新): 24 字节头 + extras + key + value
```

### SMB / DCE-RPC

```text
SMB1 (老, 已弃) / SMB2 / SMB3
端口 445 (TCP)
DCE-RPC over named pipes
Wireshark 自带, NSE script: smb-os-discovery
```

### DNS / mDNS / SSDP

```text
DNS: UDP 53, TCP 53 (大响应)
mDNS: UDP 5353 多播
SSDP: UDP 1900 多播 (UPnP)
LLMNR: UDP 5355
NetBIOS-NS: UDP 137

Wireshark + nbtscan / responder / mdns-recon
```

### DHCP / BOOTP

```text
UDP 67/68
固定头 + options (TLV)
```

## 状态机还原

```text
拿到多个 session 抓包，标方向 (C→S / S→C)，按时序对照

例:
  C → S [CONNECT magic=0x4D ver=1 id=...]
  S → C [CONNACK status=ok session=...]
  C → S [AUTH token=...]
  S → C [AUTH_OK]
  C → S [HEARTBEAT seq=1]
  S → C [HEARTBEAT_ACK seq=1]
  C → S [REQUEST opcode=read key=foo]
  S → C [RESPONSE opcode=read value=...]

状态图:
  INIT  --CONNECT-->  WAITING_CONNACK
  WAITING_CONNACK  --CONNACK ok-->  AUTHENTICATING
  AUTHENTICATING  --AUTH_OK-->  ESTABLISHED
  ESTABLISHED  --HEARTBEAT/REQ/RESP-->  ESTABLISHED
  ESTABLISHED  --DISCONNECT-->  CLOSED

工具:
  - 手动画 + Graphviz
  - Netzob (Python, 协议推断)：自动从 pcap 推 inference + state machine
  - PRISMA / SPRITE / Polyglot：学术 protocol-inference 工具
  - mitmproxy 自家脚本累计统计
```

## 重放 / 重组 / fuzz

```bash
# tcpreplay：原样回放 pcap
tcpreplay -i eth0 out.pcap
tcpreplay-edit --srcip=192.168.1.1:10.0.0.1 -i eth0 out.pcap

# tcpliveplay：实时重放 + 自动重传
tcpliveplay eth0 out.pcap 1.2.3.4 192.168.1.1

# mitmproxy 修改 + 转发
mitmdump -s mod.py
# mod.py
def request(flow):
    if flow.request.host == 'api.example.com':
        flow.request.headers['X-Custom'] = 'patched'
        if b'key' in flow.request.content:
            flow.request.content = flow.request.content.replace(b'old', b'new')

# scapy 重放 + 改字段
from scapy.all import *
pkts = rdpcap('out.pcap')
for p in pkts:
    if Raw in p:
        p[Raw].load = p[Raw].load.replace(b'foo', b'bar')
    sendp(p, iface='eth0')

# 协议 fuzz (与 fuzzrev 重叠)
boofuzz / AFLNet / Mutiny / fuzzowski
```

## 实战入口

- **Wireshark 官方文档 + Wireshark wiki**：上千 dissector 源码可学习。
- **CCSDS / IETF RFCs**：标准协议第一手资料。
- **Real World Network Reverse Engineering (Practical Packet Analysis 第 4 版)**。
- **awesome-pentest-protocols** / **awesome-iot-hacks** GitHub list。
- **CTF (DEFCON / RealWorldCTF) 网络题**：常含自家协议。
- **Project Zero / SecuriTeam blog**：自家协议中找漏洞。
- **黑哥 (RailgunX) / 看雪协议逆向教程**。
- **MQTT.org / CoAP technology / gRPC docs**：标准协议 spec。

## 自检（拿到协议样本 30 分钟内回答）

1. 传输层：TCP / UDP / SCTP / QUIC？端口？
2. 是否走 TLS？JA3/JA4 指纹？能否解密（mitm/keylog/frida）？
3. framing 类型（length-prefix / TLV / chunked / delim / fixed / tagged）？
4. opcode / 命令字集合？每种 opcode 后续 payload 结构？
5. 字段：counter / timestamp / length / flags / hash / signature？
6. 状态机：握手 → 认证 → 数据传输 → 心跳 → 断开 各阶段消息？
7. 重放保护？sequence number / nonce / timestamp 校验？
8. 能否写出 Wireshark Lua dissector + scapy custom layer + boofuzz harness？

## 相邻技能

- `fmtrev` — 静态文件格式，与协议相通的字段技巧。
- `cryptrev` — TLS / 自家加密 / HMAC / 签名机制识别。
- `iotrev` — IoT 端到端协议（含物理层与上层应用）。
- `mrev` — 移动端协议（Frida hook 应用层 send/recv）。
- `webrev` — HTTP/HTTPS/WS/HTTP2/HTTP3 + Browser DevTools。
- `cloudrev` — Agent ↔ 云的私有 gRPC/MQTT/HTTP 通道。
- `gamerev` — 游戏自家协议（常 UDP binary + 加密 + 序列号）。
- `icsrev` — Modbus / DNP3 / IEC104 / OPC UA / S7Comm。
- `binrev` — 协议解析器本身的函数级。
- `fuzzrev` — boofuzz / AFLNet 协议 fuzz harness。
- `revauto` — 协议自动化解析 / 取证流水线。