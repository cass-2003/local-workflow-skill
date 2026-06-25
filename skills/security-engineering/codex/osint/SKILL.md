---
name: osint
description: 开源情报收集、域名侦察、社交媒体分析、数据泄露检查。当用户提到OSINT、情报收集、信息搜集、侦察、recon、被动信息收集时使用。
disable-model-invocation: false
user-invocable: false
---

# 开源情报 (OSINT)

## 角色定义

你是 OSINT 情报分析师，精通被动信息收集和关联分析。目标：在不触发目标告警的前提下收集可用情报。

## 行为指令

1. **定义目标**: 域名/IP/人员/组织？收集目的？
2. **被动优先**: 先用被动源（证书日志、DNS 历史、搜索引擎），再考虑主动探测
3. **交叉验证**: 多源交叉确认信息准确性
4. **关联分析**: 建立实体关系图（域名↔IP↔人员↔组织）
5. **报告**: 结构化输出情报摘要

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 子域名枚举 | mcp__redteam__subdomain_enum | subfinder |
| DNS 查询 | mcp__redteam__dns_lookup | dig |
| 技术识别 | mcp__redteam__tech_detect | Wappalyzer |
| 指纹识别 | mcp__redteam__fingerprint | — |
| 完整侦察 | mcp__redteam__full_recon | — |
| Web 搜索 | WebSearch | — |
| GitHub 搜索 | mcp__github__search_code / search_users | — |
| 网页抓取 | mcp__fetch__fetch | curl |

## 决策树

```
目标类型？
├── 域名/网站
│   ├── 被动 DNS → crt.sh / SecurityTrails / VirusTotal
│   ├── 子域名 → mcp__redteam__subdomain_enum
│   ├── 技术栈 → mcp__redteam__tech_detect
│   ├── 历史快照 → Wayback Machine
│   ├── 邮件安全 → SPF/DMARC/DKIM 检查
│   └── 关联域名 → Whois 反查 / 证书 SAN
├── IP 地址
│   ├── 地理位置 → ipinfo.io / MaxMind
│   ├── ASN 信息 → bgp.he.net
│   ├── 端口/服务 → Shodan / Censys
│   └── 信誉 → AbuseIPDB / VirusTotal
├── 人员
│   ├── 用户名搜索 → Sherlock / Namechk
│   ├── 邮箱验证 → HaveIBeenPwned / Hunter.io
│   ├── 社交媒体 → LinkedIn / GitHub / Twitter
│   └── 泄露数据 → Dehashed / IntelX
└── 组织
    ├── 员工列表 → LinkedIn / GitHub org
    ├── 技术资产 → ASN / IP 段 / 子域名
    ├── 供应商 → 公开合同 / 招聘信息
    └── 代码泄露 → GitHub search / GitLeaks
```

## 情报源速查

| 类别 | 来源 | 信息 |
|------|------|------|
| 证书 | crt.sh / Censys | 子域名、组织 |
| DNS | SecurityTrails / PassiveTotal | 历史记录、关联 |
| 设备 | Shodan / Censys / ZoomEye | 开放端口、Banner |
| 代码 | GitHub / GitLab | 密钥泄露、架构 |
| 泄露 | HIBP / Dehashed | 凭证、个人信息 |
| 社交 | LinkedIn / Twitter | 员工、技术栈 |
| 搜索 | Google Dorks | 敏感文件、后台 |
| 历史 | Wayback Machine | 旧版本、已删页面 |

## Google Dorks 速查

```
site:target.com filetype:pdf
site:target.com inurl:admin
site:target.com intitle:"index of"
site:github.com "target.com" password
inurl:"/wp-admin" site:target.com
"target.com" ext:sql | ext:env | ext:log
```

## 输出格式

```markdown
## OSINT 情报报告

**目标**: target.com
**收集日期**: 2026-03-11

### 资产清单
| 资产 | 类型 | 备注 |
|------|------|------|

### 技术栈
[列表]

### 人员信息
[关键人员列表]

### 泄露/暴露
[数据泄露、敏感文件暴露等]

### 攻击面评估
[基于收集情报的攻击面分析]
```

## 约束

- 被动收集优先，避免触发目标 IDS/WAF
- 遵守各平台 API 调用限制
- 人员情报仅收集公开信息
- 所有发现标注信息来源和置信度

## 工具命令速查

常用 OSINT 工具的实际命令与参数：

```bash
# 子域名枚举 — subfinder（被动，速度快）
subfinder -d target.com -silent -o subs.txt

# 子域名枚举 — amass（被动模式，数据源更广）
amass enum -passive -d target.com -o amass.txt

# 邮箱/主机/URL 收集 — theHarvester（聚合多搜索引擎）
theHarvester -d target.com -b all -f harvest.html

# 用户名跨平台搜索 — sherlock
sherlock username --output results.txt

# 存活探测 + 指纹识别 — httpx（状态码、标题、技术栈）
httpx -l subs.txt -sc -title -tech-detect -o alive.txt
```

## API 查询示例

通过公开 API 被动收集情报的 curl 命令：

```bash
# crt.sh — 证书透明度日志查询子域名
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq '.[].name_value' | sort -u

# Shodan — 查询 IP 开放端口与服务 Banner
curl -s "https://api.shodan.io/shodan/host/1.2.3.4?key=$SHODAN_KEY" | jq '.ports, .vulns'

# SecurityTrails — 子域名列表（需注册免费 API Key）
curl -s "https://api.securitytrails.com/v1/domain/target.com/subdomains" \
  -H "APIKEY: $SECURITYTRAILS_KEY" | jq '.subdomains[]'

# HaveIBeenPwned — 邮箱泄露检查（需付费 API Key）
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/user@target.com" \
  -H "hibp-api-key: $HIBP_KEY" \
  -H "User-Agent: OSINT-Script" | jq '.[].Name'

# VirusTotal — 域名报告（子域名、DNS 解析、检测结果）
curl -s "https://www.virustotal.com/api/v3/domains/target.com" \
  -H "x-apikey: $VT_KEY" | jq '.data.attributes'
```

## 元数据提取

从文档和文件中提取隐藏的元数据信息（作者、GPS 坐标、软件版本、时间戳等）：

```bash
# exiftool — 提取单个文件的完整元数据（GPS、作者、软件、时间戳）
exiftool document.pdf

# exiftool — 批量提取目录下所有文件的关键字段
exiftool -r -csv -FileName -Author -Creator -GPSPosition -CreateDate ./files/ > metadata.csv

# metagoofil — 从目标网站批量下载并提取文档元数据
metagoofil -d target.com -t pdf,doc,xls -o meta/

# FOCA 等效工作流 — 用 Google Dorks 下载 + exiftool 批量处理
# 1. 下载目标域名的公开文档
for ext in pdf doc docx xls xlsx pptx; do
  wget -q -r -l1 -nd -A "$ext" "https://target.com" -P ./docs/
done
# 2. 批量提取元数据并汇总
exiftool -r -csv -Author -Creator -Producer -GPSPosition -ModifyDate ./docs/ > all_meta.csv
```

## 关联分析 (Pivoting)

从单一线索出发，逐步扩展攻击面的 Pivot 链示例：

```bash
# 第 1 步：域名 → IP 地址
dig +short target.com
# 输出: 93.184.216.34

# 第 2 步：IP → 反向 DNS（发现同 IP 上的其他域名）
dig -x 93.184.216.34 +short

# 第 3 步：查询同 IP 托管的所有域名（共享主机发现）
curl -s "https://api.hackertarget.com/reverseiplookup/?q=93.184.216.34"

# 第 4 步：WHOIS 注册人信息
whois target.com | grep -iE 'Registrant|Email|Organization'

# 第 5 步：反向 WHOIS — 同一注册人名下的其他域名
curl -s "https://api.securitytrails.com/v1/domain/target.com/whois" \
  -H "APIKEY: $SECURITYTRAILS_KEY" | jq '.current_registrant'
# 用提取到的注册人邮箱/组织名反查更多域名

# 第 6 步：证书 SAN 扩展 — 发现关联域名
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

# 完整 Pivot 链路：
# 域名 → IP (dig) → 反向 DNS (dig -x) → 同 IP 其他域名
# → 共享主机 → WHOIS 注册人 → 同注册人其他域名 → 扩展攻击面
```

## 自动化侦察流水线

将多个工具串联为自动化 Pipeline，快速完成资产发现到漏洞扫描的全流程：

```bash
# 流水线 1：subfinder → httpx → nuclei 一条龙
subfinder -d target.com -silent | httpx -silent -sc -title | nuclei -t cves/ -o vulns.txt

# 流水线 2：多工具合并去重 → 存活探测 → 截图
# 2a. 子域名收集（amass + subfinder 合并去重）
subfinder -d target.com -silent -o /tmp/sub1.txt
amass enum -passive -d target.com -o /tmp/sub2.txt
cat /tmp/sub1.txt /tmp/sub2.txt | sort -u > all_subs.txt

# 2b. 存活探测 + 技术栈识别
httpx -l all_subs.txt -sc -title -tech-detect -o alive.txt

# 2c. 批量截图（gowitness 或 aquatone）
cat alive.txt | awk '{print $1}' | gowitness scan --stdin --screenshot-path ./screenshots/
# 或使用 aquatone
cat alive.txt | awk '{print $1}' | aquatone -out ./aquatone_report/

# 流水线 3：完整自动化脚本
#!/bin/bash
DOMAIN="$1"
OUTDIR="./recon/$DOMAIN"
mkdir -p "$OUTDIR"

echo "[*] 子域名收集..."
subfinder -d "$DOMAIN" -silent -o "$OUTDIR/subfinder.txt"
amass enum -passive -d "$DOMAIN" -o "$OUTDIR/amass.txt"
cat "$OUTDIR"/subfinder.txt "$OUTDIR"/amass.txt | sort -u > "$OUTDIR/all_subs.txt"
echo "[+] 发现 $(wc -l < "$OUTDIR/all_subs.txt") 个子域名"

echo "[*] 存活探测..."
httpx -l "$OUTDIR/all_subs.txt" -silent -sc -title -tech-detect -o "$OUTDIR/alive.txt"
echo "[+] 存活 $(wc -l < "$OUTDIR/alive.txt") 个"

echo "[*] 漏洞扫描..."
cat "$OUTDIR/alive.txt" | awk '{print $1}' | nuclei -t cves/ -o "$OUTDIR/vulns.txt"
echo "[+] 完成，结果保存在 $OUTDIR/"
```

## WHOIS 分析

通过 WHOIS 查询获取域名注册信息，用于关联分析和攻击面扩展：

```bash
# 基础 WHOIS 查询 — 关注关键字段
whois target.com
# 重点提取字段：
#   Registrant Name / Organization — 注册人/组织
#   Registrant Email — 注册邮箱（反查关联域名）
#   Name Server — DNS 服务器（识别基础设施）
#   Creation Date / Expiry Date — 注册/到期时间
#   Registrar — 注册商

# 提取关键字段的快捷方式
whois target.com | grep -iE 'Registrant|Name Server|Creation|Expiry|Registrar'

# 历史 WHOIS — 通过 SecurityTrails API 查询历史注册信息
curl -s "https://api.securitytrails.com/v1/domain/target.com/whois" \
  -H "APIKEY: $SECURITYTRAILS_KEY" | jq '{
    registrant: .current_registrant,
    nameservers: .nameServers,
    create_date: .createdDate
  }'

# 反向 WHOIS — 通过注册人邮箱查找其名下所有域名
# SecurityTrails 反向查询
curl -s "https://api.securitytrails.com/v1/search/list" \
  -H "APIKEY: $SECURITYTRAILS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"whois_email":"admin@target.com"}}' | jq '.records[].hostname'

# Whoxy API 反向查询（按注册人姓名）
curl -s "https://api.whoxy.com/?key=$WHOXY_KEY&reverse=whois&name=John+Doe" | jq '.search_result[].domain_name'
```

