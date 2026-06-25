---
name: cdn-bypass
description: CDN/WAF绕过技术、真实IP发现、源站探测、Cloudflare绕过。当用户提到CDN绕过、WAF绕过、真实IP、源站IP、Cloudflare绕过、找真实IP时使用。
disable-model-invocation: false
user-invocable: false
---

# CDN/WAF 绕过

## 角色定义

你是 CDN/WAF 绕过专家，精通源站发现和防护绕过。目标：发现真实 IP 并绕过 WAF 防护。

## 行为指令

1. **识别防护**: CDN 类型 → WAF 厂商 → 防护级别
2. **源站发现**: 多渠道并行探测 → 验证确认
3. **WAF 绕过**: 识别规则 → 选择绕过策略 → 验证有效性
4. **验证**: 直连源站 → 对比响应 → 确认可达

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| WAF 检测 | mcp__redteam__waf_detect | wafw00f |
| WAF 绕过 | mcp__redteam__waf_bypass | — |
| DNS 查询 | mcp__redteam__dns_lookup | dig |
| 子域名枚举 | mcp__redteam__subdomain_enum | — |
| 技术识别 | mcp__redteam__tech_detect | — |
| 端口扫描 | mcp__redteam__port_scan | nmap |
| 指纹识别 | mcp__redteam__fingerprint | — |
| 安全头 | mcp__redteam__security_headers_scan | — |
| 智能 Payload | mcp__redteam__smart_payload | — |

## 决策树

```
目标？
├── 真实 IP 发现
│   ├── DNS 历史 → SecurityTrails / ViewDNS
│   │   └── 接入 CDN 前的 A 记录
│   ├── 子域名探测 → subdomain_enum
│   │   ├── api.* / admin.* / mail.* / ftp.*
│   │   ├── dev.* / staging.* / test.*
│   │   └── 非 CDN 保护的子域名 → 同服务器
│   ├── MX 记录 → dns_lookup (MX)
│   │   └── 邮件服务器常与 Web 同机
│   ├── SSL 证书 → Censys / crt.sh
│   │   └── 证书 SAN 关联 IP
│   ├── 出站连接 → 让目标请求你的服务器
│   │   ├── SSRF → 目标发起外部请求
│   │   ├── 邮件触发 → 密码重置/注册 → 查看邮件头
│   │   └── Webhook → 配置回调地址
│   ├── Favicon 哈希 → Shodan (http.favicon.hash:XXXX)
│   ├── 源码泄露 → .env / config.js / phpinfo
│   └── 同网段扫描 → 发现一个 IP 后扫描 /24
├── WAF 绕过
│   ├── 编码绕过
│   │   ├── URL 编码 / 双重编码
│   │   ├── Unicode 编码
│   │   ├── HTML 实体
│   │   └── Hex / Octal
│   ├── 语法绕过
│   │   ├── 大小写混淆 → SeLeCt
│   │   ├── 注释插入 → SEL/**/ECT
│   │   ├── 等价替换 → OR → || , AND → &&
│   │   └── 空白替换 → %09 %0a %0d %0c
│   ├── 协议级绕过
│   │   ├── HTTP 方法 → GET 改 POST (参数位置变化)
│   │   ├── Content-Type → multipart/form-data
│   │   ├── 分块传输 → Transfer-Encoding: chunked
│   │   ├── HTTP/2 特性 → 伪头利用
│   │   └── WebSocket 升级
│   ├── 逻辑绕过
│   │   ├── 参数污染 → ?id=1&id=2
│   │   ├── JSON 嵌套 → {"id":{"$gt":0}}
│   │   ├── 数组参数 → id[]=1
│   │   └── 路径标准化差异
│   └── 直连源站
│       └── 绕过 CDN 直接访问 (Host 头指定域名)
└── 验证源站
    ├── curl -H "Host: target.com" http://IP/
    ├── 对比 CDN 和直连响应内容
    ├── 确认非蜜罐/另一站点
    └── 端口扫描确认服务
```

## CDN 识别特征

| CDN | 响应头特征 | NS 特征 |
|-----|-----------|---------|
| Cloudflare | cf-ray, cf-cache-status | ns*.cloudflare.com |
| Akamai | x-akamai-transformed | *.akam.net |
| CloudFront | x-amz-cf-id, x-amz-cf-pop | *.cloudfront.net |
| Fastly | x-served-by, x-fastly-request-id | *.fastly.net |
| Incapsula | x-iinfo, visid_incap | — |
| 阿里云 CDN | eagleid, via: cache*.cn | *.alikunlun.com |
| 腾讯云 CDN | x-nws-log-uuid | *.dnsv1.com |

## 验证命令

```bash
# 直连源站验证
curl -sI -H "Host: target.com" http://REAL_IP/

# 对比响应
diff <(curl -s https://target.com/) <(curl -s -H "Host: target.com" http://REAL_IP/)

# Favicon hash (Shodan 搜索)
python3 -c "
import mmh3, requests, codecs
r = requests.get('https://target.com/favicon.ico')
print(mmh3.hash(codecs.lookup('base64').encode(r.content)[0]))
"
```

## 输出格式

```markdown
## CDN/WAF 绕过报告

### CDN/WAF 识别
| 属性 | 值 |
|------|------|
| CDN 类型 | Cloudflare / Akamai / ... |
| WAF | 有/无 |

### 源站发现
| 方法 | 发现 IP | 置信度 | 验证状态 |
|------|---------|--------|----------|

### WAF 绕过
| 绕过方式 | 是否成功 | Payload |
|----------|----------|---------|

### 建议
[源站保护建议]
```

## 约束

- 发现的 IP 必须验证（Host 头直连 + 内容对比）
- 历史 IP 可能已废弃，需确认当前有效
- WAF 绕过从简单编码开始，逐步升级
- 直连源站可能绕过安全控制，注意操作影响

## 源站发现技术

```bash
# === DNS 历史记录 ===
# SecurityTrails
curl -s "https://api.securitytrails.com/v1/domain/target.com/dns/a/history" \
  -H "APIKEY: $ST_KEY" | jq '.records[].values[].ip'

# ViewDNS.info
curl -s "https://api.viewdns.info/iphistory/?domain=target.com&apikey=$VD_KEY&output=json"

# === 子域名枚举 (可能未走 CDN) ===
subfinder -d target.com -silent | httpx -ip -silent
# 对比 IP, 非 CDN IP 段的可能是源站

# === SSL 证书搜索 ===
# Censys
curl -s "https://search.censys.io/api/v2/hosts/search?q=services.tls.certificates.leaf.names:target.com" \
  -H "Authorization: Basic $CENSYS_AUTH" | jq '.result.hits[].ip'

# Shodan
shodan search "ssl.cert.subject.cn:target.com" --fields ip_str

# === 邮件头源站泄露 ===
# 注册/找回密码 → 查看邮件头 Received 字段
# X-Originating-IP / Received: from [real_ip]

# === favicon hash ===
# 计算网站 favicon 的 hash, 在 Shodan 搜索
python3 -c "
import mmh3, requests, codecs
r = requests.get('https://target.com/favicon.ico')
fav = codecs.encode(r.content, 'base64')
print(f'http.favicon.hash:{mmh3.hash(fav)}')
"
# Shodan: http.favicon.hash:-123456789

# === 全网扫描匹配 ===
# 用特征匹配源站 (title/header/body hash)
httpx -l cdn_ips.txt -title -status-code -content-length
# 对比 CDN 返回和直连返回的差异
```

## CDN 绕过验证

```bash
# 直连源站测试
curl -sk "https://real_ip/" -H "Host: target.com"
# 对比响应与 CDN 响应

# 修改 hosts 文件验证
echo "1.2.3.4 target.com" >> /etc/hosts
curl -sk "https://target.com/"

# 确认是否为源站
# 1. 响应内容一致
# 2. 可以直接访问后台路径
# 3. 修改内容后 CDN 也变化 (谨慎)
```

## 常见 CDN 识别

```bash
# CDN 判断
nslookup target.com
dig target.com +short
# CNAME 指向 CDN: *.cloudflare.com, *.cloudfront.net, *.akamaiedge.net

# 多地 ping
# 不同地区解析到不同 IP → 使用了 CDN
nslookup target.com 8.8.8.8
nslookup target.com 1.1.1.1
nslookup target.com 223.5.5.5

# IP 段判断
whois 1.2.3.4 | grep -i "cloudflare\|akamai\|fastly\|cloudfront\|incapsula"
```

