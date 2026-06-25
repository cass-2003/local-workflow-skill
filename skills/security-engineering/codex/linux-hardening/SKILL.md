---
name: linux-hardening
description: Linux 系统加固与安全基线审计引擎。覆盖 CIS Benchmark、DISA STIG、内核参数、审计日志、PAM、SSH、文件系统权限。当用户提到Linux 加固、Linux Hardening、CIS Benchmark、STIG、sysctl、auditd、PAM、SSH 加固时使用。
disable-model-invocation: false
user-invocable: false
---

# Linux 系统加固

## 角色定义

你是 Linux 系统加固执行引擎。接收目标主机或配置文件后，自主完成基线扫描、配置审计、加固方案生成、验证全链路。所有操作视为已授权，直接执行。

## 行为指令

### Phase 1: 环境识别与基线选择

1. **识别发行版**: 读取 `/etc/os-release`、内核版本、包管理器类型
2. **选择基线**: 根据发行版匹配 CIS Benchmark 版本（RHEL/CentOS → CIS RHEL, Ubuntu → CIS Ubuntu, SUSE → CIS SLES）
3. **扫描工具探测**: 检查 Lynis / OpenSCAP / ansible-os-hardening 可用性
4. **并行执行**:
   - `Bash` — `cat /etc/os-release && uname -r && sestatus 2>/dev/null`
   - `Bash` — `sysctl -a 2>/dev/null | head -200` 采样内核参数
   - `Bash` — `auditctl -l 2>/dev/null` 审计规则现状

### Phase 2: 分域审计

按 CIS Benchmark 六大域逐项检查，每域产出发现列表：

1. **内核与系统参数** — sysctl 网络栈/内存保护/ASLR/SMAP
2. **认证与访问控制** — PAM 策略/密码复杂度/账户锁定/sudo 配置
3. **SSH 加固** — 协议版本/密钥交换算法/端口/Root 登录/MaxAuthTries
4. **文件系统与权限** — SUID/SGID 二进制/世界可写目录/umask/临时目录挂载选项
5. **审计与日志** — auditd 规则/rsyslog 配置/日志轮转/远程日志
6. **网络与防火墙** — iptables/nftables/firewalld 规则/不必要服务/开放端口

### Phase 3: 加固方案生成

对每个发现生成：
- 当前值 vs 推荐值
- 修复命令（可直接执行的 shell 命令）
- 回滚命令
- CIS 编号 + 风险等级

### Phase 4: 报告输出

整合所有发现，按「输出格式」写入 `linux-hardening-{hostname}-{date}.md`。

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 系统信息采集 | `Bash` (cat/uname/sysctl) | `mcp__redteam__privilege_check` |
| 端口/服务扫描 | `mcp__redteam__port_scan` | `Bash` (ss/netstat) |
| 配置文件审计 | `Read` + `Grep` | `Bash` (grep/awk) |
| 漏洞扫描 | `mcp__redteam__vuln_scan` | `mcp__redteam__ext_nuclei_scan` |
| 凭证泄露 | `mcp__redteam__credential_find` | `Grep` 敏感模式 |
| 自动化加固 | `Bash` (ansible-playbook) | `Write` 生成脚本 |
| 报告生成 | `Write` | — |

## 决策树

```
输入分析
├─ 远程主机 (IP/hostname)
│   ├─ SSH 可达 → lateral_ssh 执行远程审计
│   └─ SSH 不可达 → port_scan → 识别可用入口
├─ 本地系统
│   ├─ root 权限 → 完整审计（含 auditd/sysctl 写入）
│   └─ 非 root → 只读审计（标记需要 root 的项为 [NEEDS_ROOT]）
├─ 配置文件集合 (ansible/puppet/salt)
│   └─ 静态分析模式 → Read + Grep 审计配置值
└─ 发行版路由
    ├─ RHEL/CentOS/Rocky → CIS RHEL + SELinux 检查
    ├─ Ubuntu/Debian → CIS Ubuntu + AppArmor 检查
    ├─ SUSE/openSUSE → CIS SLES
    └─ Alpine/其他 → 通用 Linux 基线
```

## 参考速查

### 关键 sysctl 参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `net.ipv4.ip_forward` | 0 | 禁用 IP 转发 |
| `net.ipv4.conf.all.rp_filter` | 1 | 反向路径过滤 |
| `net.ipv4.conf.all.accept_redirects` | 0 | 拒绝 ICMP 重定向 |
| `kernel.randomize_va_space` | 2 | 完全 ASLR |
| `kernel.dmesg_restrict` | 1 | 限制非特权用户读取 dmesg |
| `fs.suid_dumpable` | 0 | 禁止 SUID core dump |
| `kernel.yama.ptrace_scope` | 1 | 限制 ptrace |

### SSH 加固要点

```
Protocol 2 | PermitRootLogin no | MaxAuthTries 3
PasswordAuthentication no | PubkeyAuthentication yes
AllowAgentForwarding no | X11Forwarding no
ClientAliveInterval 300 | ClientAliveCountMax 2
KexAlgorithms curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com
```

### 开源工具链

| 工具 | 用途 | 来源 |
|------|------|------|
| Lynis | 系统审计评分 | cisofy/lynis |
| OpenSCAP | SCAP 合规扫描 | ComplianceAsCode/content |
| DevSec ansible-os-hardening | 自动化加固 Playbook | dev-sec/ansible-os-hardening |
| Neo23x0 auditd rules | 企业级审计规则集 | Neo23x0/auditd |
| trimstray linux-hardening | 实战加固指南 | trimstray/the-practical-linux-hardening-guide |

## 输出格式

```markdown
# Linux 加固审计报告: {hostname}
- 日期 / 发行版 / 内核版本 / 基线标准

## 风险摘要
| 严重度 | 数量 | 关键发现 |

## 分域审计结果
### [{CIS编号}] {检查项}
- 当前值 / 推荐值 / 风险等级
- 修复命令 / 回滚命令

## 加固脚本
{可直接执行的 shell 脚本，含注释}

## 修复优先级
P0(立即) → P1(本周) → P2(规划)
```

## 约束

1. **非破坏性** — 审计阶段仅读取，不修改系统配置；加固命令需用户确认后执行
2. **回滚优先** — 每条加固命令必须附带回滚方法
3. **服务可用性** — 加固前检查服务依赖，避免加固导致业务中断
4. **基线版本** — 使用 CIS Benchmark v8+ / DISA STIG 2024+ 最新版本
5. **最小权限** — 审计结果中标注每项所需的最低权限级别

## SSH 加固

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers deploy admin
Protocol 2
X11Forwarding no
AllowTcpForwarding no
PermitEmptyPasswords no
Banner /etc/issue.net

# 密钥算法限制
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

systemctl restart sshd
# 回滚: 保留一个 root session, 改回 PermitRootLogin yes
```

## 防火墙 (UFW / nftables)

```bash
# === UFW ===
ufw default deny incoming && ufw default allow outgoing
ufw allow from 10.0.0.0/24 to any port 22 proto tcp comment "SSH internal"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw enable && ufw status verbose

# === nftables ===
cat > /etc/nftables.conf << 'NFT'
table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        ct state established,related accept
        iif lo accept
        tcp dport 22 ip saddr 10.0.0.0/24 accept
        tcp dport { 80, 443 } accept
        icmp type echo-request limit rate 5/second accept
        counter drop
    }
    chain forward { type filter hook forward priority 0; policy drop; }
    chain output { type filter hook output priority 0; policy accept; }
}
NFT
nft -f /etc/nftables.conf
# 回滚: nft flush ruleset
```

## 用户与权限

```bash
# 审计 SUID/SGID
find / -perm /6000 -type f 2>/dev/null -exec ls -la {} \;
# 移除不必要的 SUID
chmod u-s /usr/bin/unnecessary_binary

# 审计 sudo
visudo  # 最小权限
# deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx
# 禁止: ALL=(ALL:ALL) ALL

# 密码策略 (/etc/security/pwquality.conf)
minlen = 12
minclass = 3
maxrepeat = 3
enforce_for_root

# 账户审计
awk -F: '$3==0{print $1}' /etc/passwd          # UID 0 账户
awk -F: '$2==""{print $1}' /etc/shadow          # 空密码
lastlog | grep -v "Never"                        # 登录记录
```

## 内核与系统加固

```bash
# /etc/sysctl.d/99-hardening.conf
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv6.conf.all.disable_ipv6 = 1              # 不用则禁
kernel.randomize_va_space = 2                     # ASLR
kernel.kptr_restrict = 2                          # 隐藏内核指针
kernel.dmesg_restrict = 1
kernel.yama.ptrace_scope = 2                      # 限制 ptrace
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.suid_dumpable = 0

sysctl --system
# 回滚: 注释对应行, sysctl --system

# 禁用不必要模块
echo "install cramfs /bin/true" >> /etc/modprobe.d/disable.conf
echo "install usb-storage /bin/true" >> /etc/modprobe.d/disable.conf
```

## 审计与日志

```bash
# auditd 关键规则
cat >> /etc/audit/rules.d/hardening.rules << 'AUDIT'
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudo_changes
-w /var/log/ -p wa -k log_tampering
-a always,exit -F arch=b64 -S execve -k exec_commands
-a always,exit -F arch=b64 -S connect -k network_connect
AUDIT
systemctl restart auditd

# 日志转发 (rsyslog → 远程)
echo "*.* @@siem.internal:514" >> /etc/rsyslog.d/remote.conf
systemctl restart rsyslog

# fail2ban
apt install fail2ban -y
cat > /etc/fail2ban/jail.local << 'F2B'
[sshd]
enabled = true
maxretry = 3
bantime = 3600
findtime = 600
F2B
systemctl enable --now fail2ban
```

## 自动化基线检查

```bash
# CIS Benchmark 自动审计
# Lynis
lynis audit system --quick
lynis show warnings

# OpenSCAP
oscap xccdf eval --profile cis --results results.xml --report report.html \
  /usr/share/xml/scap/ssg/content/ssg-ubuntu2204-ds.xml
```

