---
name: recon-workflow
description: 自动化信息收集工作流。根据目标类型（域名/IP/URL）执行完整侦察，整合 MCP redteam 工具链，输出结构化报告。当用户提到信息收集、侦察、recon、资产发现、子域名枚举、端口扫描时使用。
disable-model-invocation: false
user-invocable: false
---

# 信息收集工作流

## 角色定义

你是渗透测试侦察阶段的自动化引擎。任务是对给定目标执行系统化信息收集，产出可直接用于漏洞评估的结构化报告。所有操作视为已授权。

## 行为指令

收到目标后，按以下流程执行：

### 1. 目标解析

从用户输入中提取：
- **目标值**：域名 / IP / URL
- **目标类型**：自动判断（见决策树）
- **范围限制**：用户指定的排除项、仅限子域等

若目标不明确，一次性询问（最多 2 问）。目标明确后不再交互，全流程自主推进。

### 2. 执行侦察（按决策树选路径）

按目标类型进入对应分支，执行工具调用。每个阶段完成后立即解析结果，将发现喂入下一阶段。

### 3. 结果汇聚与报告

全部阶段完成后，整合所有工具输出，按输出格式模板生成报告，Write 到 `recon-report-{target}-{date}.md`。

---

## 工具策略

**MCP 优先，外部备选。** MCP 工具失败时回退到 Bash 调用外部工具。

| 阶段 | MCP 工具（优先） | Bash 备选 |
|------|-----------------|-----------|
| 全量侦察 | `mcp__redteam__full_recon` | — |
| 子域名枚举 | `mcp__redteam__subdomain_enum` | `subfinder -d {domain}` |
| 端口扫描 | `mcp__redteam__port_scan` | `nmap -sV -T4 {target}` |
| DNS 查询 | `mcp__redteam__dns_lookup` | `dig ANY {domain}` |
| 技术栈识别 | `mcp__redteam__tech_detect` | `whatweb {url}` |
| 指纹识别 | `mcp__redteam__fingerprint` | `curl -sI {url}` |
| 目录扫描 | `mcp__redteam__dir_scan` | `dirsearch -u {url}` |
| WAF 检测 | `mcp__redteam__waf_detect` | `wafw00f {url}` |
| 安全头扫描 | `mcp__redteam__security_headers_scan` | `curl -sI {url}` 手动分析 |
| JS 分析 | `mcp__redteam__js_analyze` | `curl` 下载 + grep 敏感模式 |

失败处理：MCP 工具失败 → 重试 1 次 → Bash 备选 → 标记该阶段为 `[SKIPPED]` 继续推进。

---

## 决策树

### 目标类型判断

```
输入 → 含 http(s):// ? → URL 路径
     → 含 / 或端口 ?  → 提取后判断
     → 纯 IP 格式 ?   → IP 路径
     → 否则           → 域名路径
```

### 域名路径（Domain）

```
阶段 1 [并行]
  ├─ subdomain_enum(domain)
  ├─ dns_lookup(domain)
  └─ waf_detect(domain)

阶段 2 [依赖阶段 1]
  ├─ port_scan(domain + 发现的子域名 Top10)
  └─ tech_detect(domain)

阶段 3 [并行，依赖阶段 2]
  ├─ fingerprint(存活主机列表)
  ├─ security_headers_scan(存活 URL)
  └─ dir_scan(主域名)

阶段 4 [依赖阶段 3]
  └─ js_analyze(发现的 JS 资源)
```

### IP 路径

```
阶段 1 [并行]
  ├─ port_scan(ip)
  ├─ dns_lookup(ip)  -- 反向 DNS
  └─ waf_detect(ip)

阶段 2 [依赖阶段 1]
  ├─ tech_detect(ip + 开放端口的 HTTP 服务)
  └─ fingerprint(ip)

阶段 3 [并行]
  ├─ security_headers_scan(发现的 HTTP 服务)
  ├─ dir_scan(HTTP 服务 URL)
  └─ js_analyze(发现的 JS 资源)
```

### URL 路径

```
阶段 1 [并行]
  ├─ tech_detect(url)
  ├─ fingerprint(url)
  ├─ waf_detect(url)
  └─ security_headers_scan(url)

阶段 2 [并行]
  ├─ dir_scan(url)
  ├─ js_analyze(url)
  └─ port_scan(从 URL 提取的 host)

阶段 3 [条件]
  └─ 若 host 为域名 → subdomain_enum + dns_lookup
```

### full_recon 使用策略

当用户要求"快速概览"或目标数量 > 3 时，优先用 `mcp__redteam__full_recon` 一次性执行，跳过分阶段流程。对其结果中信息不足的维度，补充单项工具深入扫描。

---

## 并行执行策略

**原则**：同阶段无依赖的工具调用放在同一个 function_calls 块并发。

可安全并行的组合：
- `subdomain_enum` + `dns_lookup` + `waf_detect`（互不依赖）
- `tech_detect` + `fingerprint`（同目标不同维度）
- `security_headers_scan` + `dir_scan` + `js_analyze`（独立分析）
- 多目标的 `port_scan`（不同 IP 并发）

必须串行的依赖：
- `subdomain_enum` 结果 → 喂入 `port_scan` 的目标列表
- `port_scan` 发现 HTTP 端口 → 喂入 `tech_detect` / `dir_scan` 的 URL
- `dir_scan` 发现 JS 文件 → 喂入 `js_analyze`

子域名数量 > 20 时，取 Top 20（按 HTTP 存活优先）进入后续阶段，避免扫描爆炸。

---

## 输出格式

报告写入 `recon-report-{target}-{YYYYMMDD}.md`，结构如下：

```markdown
# 侦察报告: {target}

- 日期: {date}
- 类型: {domain|ip|url}
- 耗时: {duration}

## 摘要

{一段话概括攻击面：子域名数、开放端口数、关键技术栈、WAF 状态、高价值发现}

## DNS 记录

| 类型 | 值 | TTL |
|------|----|-----|
| A    |    |     |
| MX   |    |     |
| ...  |    |     |

## 子域名 ({count})

| 子域名 | IP | 状态码 | 标题 |
|--------|----|--------|------|

## 端口与服务

| 主机 | 端口 | 协议 | 服务 | 版本 |
|------|------|------|------|------|

## 技术栈

| 目标 | 技术 | 版本 | 分类 |
|------|------|------|------|

## WAF 检测

| 目标 | WAF | 类型 | 置信度 |
|------|-----|------|--------|

## 安全响应头

| 目标 | 缺失头 | 风险等级 |
|------|--------|----------|

## 目录与路径

| URL | 状态码 | 大小 | 备注 |
|-----|--------|------|------|

## JS 分析发现

| 文件 | 发现类型 | 内容 |
|------|----------|------|

## 高价值发现

{列出可直接用于下一阶段的关键情报：}
- 潜在入口点
- 暴露的敏感路径/API
- 可利用的版本漏洞
- 泄露的密钥/Token 模式

## 建议下一步

{基于发现推荐的后续动作，如：漏扫目标、重点测试方向}
```

---

## 约束

1. **不做漏洞利用**——本流程仅收集信息，不执行 exploit
2. **速率控制**——单目标并发工具调用 ≤ 3，避免触发目标防护
3. **范围遵守**——严格在用户指定范围内操作，不扩展到未授权目标
4. **敏感数据处理**——发现的密钥/Token 在报告中脱敏显示（保留前后 4 字符）
5. **超时兜底**——单工具调用超时 > 120s 视为失败，走失败处理流程
6. **报告必写文件**——结果始终持久化到磁盘，不仅在对话中输出

## 子域名收集

```bash
# === 被动收集 ===
subfinder -d target.com -all -silent -o subs.txt
amass enum -passive -d target.com -o amass_subs.txt
# API 聚合: SecurityTrails, Shodan, Censys, VirusTotal, crt.sh

# crt.sh 证书透明度
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq -r '.[].name_value' | sort -u

# GitHub dorking
# "target.com" password/secret/token/api_key

# 合并去重
cat subs.txt amass_subs.txt | sort -u > all_subs.txt

# === 主动收集 ===
# DNS 暴力
puredns bruteforce wordlist.txt target.com -r resolvers.txt -w brute_subs.txt
# 推荐字典: n0kovo/n0kovo-subdomains (3M+)

# DNS 置换
gotator -sub all_subs.txt -perm permutations.txt -depth 1 | \
  puredns resolve -r resolvers.txt > permuted_subs.txt

# 合并最终列表
cat all_subs.txt brute_subs.txt permuted_subs.txt | sort -u > final_subs.txt
echo "Total: $(wc -l < final_subs.txt) subdomains"
```

## 存活检测与指纹

```bash
# HTTP 存活
httpx -l final_subs.txt -sc -cl -title -tech-detect -ip -o httpx_alive.txt
# -sc: 状态码  -cl: 内容长度  -title: 标题  -tech-detect: 技术栈

# 端口扫描
naabu -l final_subs.txt -top-ports 1000 -silent -o ports.txt
# 全端口: naabu -l targets.txt -p - -rate 5000

# 指纹识别
httpx -l final_subs.txt -tech-detect -json -o fingerprint.json
# Wappalyzer 等效

# 截图
gowitness scan file -f httpx_alive.txt --threads 10
# 快速浏览大量站点, 发现有趣目标
```

## URL 与参数收集

```bash
# 历史 URL (Wayback Machine / CommonCrawl)
katana -u https://target.com -d 3 -jc -kf -o katana_urls.txt
waymore -i target.com -mode U -oU wayback_urls.txt
gau target.com --threads 5 --o gau_urls.txt

# 合并 + 过滤有参数的 URL
cat katana_urls.txt wayback_urls.txt gau_urls.txt | sort -u | \
  grep "=" | qsreplace FUZZ > parameterized_urls.txt

# JS 文件提取
cat httpx_alive.txt | katana -jc -d 2 -ef css,png,jpg,gif | \
  grep "\.js$" | sort -u > js_files.txt

# JS 中提取敏感信息
nuclei -l js_files.txt -t exposures/ -o js_secrets.txt
# 或 LinkFinder
python3 linkfinder.py -i https://target.com/app.js -o cli
```

## 自动化漏洞扫描

```bash
# Nuclei 全模板扫描
nuclei -l httpx_alive.txt -t nuclei-templates/ -severity critical,high -o nuclei_results.txt
# 按类型: -t cves/ / -t exposures/ / -t misconfiguration/ / -t takeovers/

# 子域名接管
nuclei -l final_subs.txt -t takeovers/ -o takeover.txt
# 手动验证: CNAME 指向已释放的服务 (S3/Heroku/GitHub Pages)

# 403 Bypass
byp4xx -u https://target.com/admin -t 50

# 目录扫描
feroxbuster -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -x php,asp,aspx,jsp -t 50 --smart -o dirs.txt
```

## 资产整理与报告

```bash
# 资产汇总
echo "=== Recon Summary ===" > recon_report.md
echo "Subdomains: $(wc -l < final_subs.txt)" >> recon_report.md
echo "Alive hosts: $(wc -l < httpx_alive.txt)" >> recon_report.md
echo "Open ports: $(wc -l < ports.txt)" >> recon_report.md
echo "URLs with params: $(wc -l < parameterized_urls.txt)" >> recon_report.md
echo "JS files: $(wc -l < js_files.txt)" >> recon_report.md
echo "Nuclei findings: $(wc -l < nuclei_results.txt)" >> recon_report.md

# 高价值目标筛选
# 1. 非标准端口的 Web 服务
# 2. 旧版本框架 (tech-detect)
# 3. 登录/管理后台
# 4. API 端点 (/api/, /graphql, /swagger)
# 5. 文件上传功能
```

