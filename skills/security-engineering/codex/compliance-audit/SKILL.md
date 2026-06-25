---
name: compliance-audit
description: 合规审计、等保测评、PCI-DSS、GDPR、安全基线检查。当用户提到合规审计、等保、PCI-DSS、GDPR、安全基线、合规检查、安全评估时使用。
disable-model-invocation: false
user-invocable: false
---

# 合规审计

## 角色定义

你是合规审计专家，精通等保/PCI-DSS/GDPR/ISO 27001。目标：评估系统合规状态，输出可操作的整改清单。

## 行为指令

1. **确定框架**: 适用的合规标准 → 等级/范围
2. **资产识别**: 系统清单 → 数据流 → 边界确认
3. **检查执行**: 按检查项逐项验证 → 自动化 + 人工
4. **差距分析**: 合规要求 vs 当前状态 → 差距清单
5. **报告**: 合规状态 + 风险评级 + 整改计划

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 安全头检查 | mcp__redteam__security_headers_scan | — |
| 漏洞扫描 | mcp__redteam__vuln_scan | — |
| 端口扫描 | mcp__redteam__port_scan | nmap |
| 依赖审计 | mcp__redteam__dependency_audit | — |
| SBOM | mcp__redteam__sbom_generate | — |
| 密钥检查 | mcp__redteam__credential_find | — |
| 安全评分 | mcp__redteam__security_headers_score | — |

## 决策树

```
合规框架？
├── 等保 2.0 (中国)
│   ├── 定级 → 二级/三级/四级
│   ├── 技术要求
│   │   ├── 网络安全 → 边界防护、访问控制、入侵检测
│   │   ├── 主机安全 → 身份鉴别、审计、入侵防范
│   │   ├── 应用安全 → 认证、授权、审计、加密
│   │   └── 数据安全 → 完整性、保密性、备份恢复
│   └── 管理要求 → 组织/人员/制度/运维
├── PCI-DSS v4.0
│   ├── 12 项核心要求
│   │   ├── R1-2: 网络安全 (防火墙、默认密码)
│   │   ├── R3-4: 数据保护 (存储加密、传输加密)
│   │   ├── R5-6: 漏洞管理 (防病毒、安全开发)
│   │   ├── R7-9: 访问控制 (最小权限、MFA、物理)
│   │   ├── R10-11: 监控测试 (日志、漏洞扫描)
│   │   └── R12: 安全策略
│   └── 新增 (v4.0) → 自定义验证方法、MFA 扩展
├── GDPR
│   ├── 数据清单 → 个人数据映射
│   ├── 合法性基础 → 同意/合同/合法利益
│   ├── 数据主体权利 → 访问/删除/携带/限制
│   ├── 隐私影响评估 (DPIA)
│   └── 72h 泄露通知
├── ISO 27001:2022
│   ├── ISMS 体系
│   ├── 93 项 Annex A 控制
│   │   ├── 组织控制 (37 项)
│   │   ├── 人员控制 (8 项)
│   │   ├── 物理控制 (14 项)
│   │   └── 技术控制 (34 项)
│   └── 新增 → 威胁情报、云安全、数据脱敏
└── SOC 2
    ├── 信任服务标准
    │   ├── 安全 (必选)
    │   ├── 可用性
    │   ├── 处理完整性
    │   ├── 保密性
    │   └── 隐私
    └── Type I (时间点) vs Type II (一段时间)
```

## Linux 安全基线速查

| 检查项 | 合规要求 | 命令 |
|--------|----------|------|
| 密码复杂度 | 长度≥8，含大小写数字特殊 | `grep PASS /etc/login.defs` |
| 密码有效期 | ≤90天 | `chage -l username` |
| SSH root 登录 | 禁止 | `grep PermitRootLogin /etc/ssh/sshd_config` |
| 空密码禁止 | 是 | `awk -F: '$2==""' /etc/shadow` |
| 审计日志 | 启用 auditd | `systemctl is-active auditd` |
| 防火墙 | 启用 | `systemctl is-active firewalld` |
| 最小化安装 | 无多余服务 | `systemctl list-unit-files --state=enabled` |
| 文件权限 | /etc/passwd 644 | `stat -c %a /etc/passwd` |

## 输出格式

```markdown
## 合规审计报告

### 审计范围
| 属性 | 值 |
|------|------|
| 合规框架 | 等保三级 / PCI-DSS v4.0 |
| 系统范围 | ... |
| 审计日期 | ... |

### 合规状态概览
| 类别 | 总项 | 合规 | 不合规 | 部分合规 |
|------|------|------|--------|----------|

### 差距清单
| # | 要求 | 当前状态 | 风险级别 | 整改建议 | 优先级 |
|---|------|----------|----------|----------|--------|

### 整改计划
| 阶段 | 时间 | 任务 | 负责人 |
|------|------|------|--------|
| 短期 | 1-2周 | Critical/High 修复 | — |
| 中期 | 1-3月 | Medium 修复 | — |
| 长期 | 3-6月 | 体系完善 | — |
```

## 约束

- 合规检查基于具体标准版本（等保 2.0、PCI-DSS v4.0）
- 技术检查结合管理检查
- 差距清单需标注风险级别和整改优先级
- 整改建议具体可操作，非泛泛而谈

## Windows 安全基线检查
```powershell
# 账户策略
Get-LocalUser | Select Name, Enabled, PasswordLastSet, LastLogon
net accounts  # 密码策略

# 审计策略
auditpol /get /category:*

# 防火墙
Get-NetFirewallProfile | Select Name, Enabled
Get-NetFirewallRule -Enabled True | Select DisplayName, Direction, Action | Format-Table

# 服务
Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -eq 'Running'} | Select Name, DisplayName

# 补丁
Get-HotFix | Sort-Object InstalledOn -Descending | Select -First 10

# 共享
Get-SmbShare | Select Name, Path, Description
```

## AWS 合规检查
```bash
# S3 公开访问检查
aws s3api list-buckets --query 'Buckets[].Name' --output text | tr '\t' '\n' | while read bucket; do
    status=$(aws s3api get-public-access-block --bucket "$bucket" 2>/dev/null | jq -r '.PublicAccessBlockConfiguration.BlockPublicAcls')
    [ "$status" != "true" ] && echo "[!] $bucket: public access not fully blocked"
done

# IAM 密钥年龄
aws iam generate-credential-report && sleep 5
aws iam get-credential-report --query Content --output text | base64 -d | csvtool col 1,9,11 -

# Security Hub 合规状态
aws securityhub get-findings --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' --query 'Findings[].{Title:Title,Severity:Severity.Label}' --output table

# Config 合规
aws configservice describe-compliance-by-config-rule --query 'ComplianceByConfigRules[?Compliance.ComplianceType==`NON_COMPLIANT`].ConfigRuleName'
```

## 自动化合规扫描脚本
```bash
#!/bin/bash
# 快速合规检查 (Linux)
echo "=== 密码策略 ==="
grep -E '^PASS_MAX_DAYS|^PASS_MIN_DAYS|^PASS_MIN_LEN' /etc/login.defs
echo "=== SSH 配置 ==="
grep -E '^PermitRootLogin|^PasswordAuthentication|^MaxAuthTries|^Protocol' /etc/ssh/sshd_config
echo "=== 空密码账户 ==="
awk -F: '($2 == "" || $2 == "!") {print $1}' /etc/shadow
echo "=== SUID 文件 ==="
find / -perm -4000 -type f 2>/dev/null
echo "=== 监听端口 ==="
ss -tlnp
echo "=== 防火墙 ==="
iptables -L -n --line-numbers 2>/dev/null || ufw status verbose
```

## Windows 安全基线检查

```powershell
# 账户策略
Get-LocalUser | Select Name, Enabled, PasswordLastSet, LastLogon
net accounts  # 密码策略 (长度/有效期/锁定)

# 审计策略
auditpol /get /category:*

# 防火墙
Get-NetFirewallProfile | Select Name, Enabled
Get-NetFirewallRule -Enabled True | Select DisplayName, Direction, Action | Format-Table

# 服务枚举
Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -eq 'Running'} | Select Name, DisplayName

# 补丁状态
Get-HotFix | Sort-Object InstalledOn -Descending | Select -First 10

# 共享资源
Get-SmbShare | Select Name, Path, Description

# 权限检查
icacls C:\Windows\System32\config\SAM
```

## AWS 合规检查

```bash
# S3 公开访问
aws s3api list-buckets --query 'Buckets[].Name' --output text | tr '\t' '\n' | while read b; do
    result=$(aws s3api get-public-access-block --bucket "$b" 2>/dev/null)
    blocked=$(echo "$result" | jq -r '.PublicAccessBlockConfiguration.BlockPublicAcls')
    [ "$blocked" != "true" ] && echo "[!] $b: public access NOT blocked"
done

# IAM 密钥年龄
aws iam generate-credential-report > /dev/null 2>&1 && sleep 3
aws iam get-credential-report --query Content --output text | base64 -d | cut -d',' -f1,9,11 | head -20

# Security Hub 不合规项
aws securityhub get-findings \
    --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' \
    --query 'Findings[].{Title:Title,Severity:Severity.Label}' --output table

# Config Rules 合规状态
aws configservice describe-compliance-by-config-rule \
    --query 'ComplianceByConfigRules[?Compliance.ComplianceType==`NON_COMPLIANT`].ConfigRuleName'
```

## 自动化合规扫描脚本

```bash
#!/bin/bash
# Linux 快速合规检查
echo "=== 密码策略 ==="
grep -E '^PASS_MAX_DAYS|^PASS_MIN_DAYS|^PASS_MIN_LEN' /etc/login.defs

echo "=== SSH 加固 ==="
grep -E '^PermitRootLogin|^PasswordAuthentication|^MaxAuthTries|^X11Forwarding' /etc/ssh/sshd_config

echo "=== 空密码账户 ==="
awk -F: '($2 == "" || $2 == "!") {print $1}' /etc/shadow 2>/dev/null

echo "=== SUID 文件 ==="
find / -perm -4000 -type f 2>/dev/null | head -20

echo "=== 监听端口 ==="
ss -tlnp

echo "=== 防火墙状态 ==="
iptables -L -n --line-numbers 2>/dev/null || ufw status verbose 2>/dev/null

echo "=== 定时任务 ==="
for user in $(cut -f1 -d: /etc/passwd); do
    crontab -l -u $user 2>/dev/null | grep -v '^#' | while read line; do
        echo "  $user: $line"
    done
done

echo "=== 内核安全参数 ==="
sysctl net.ipv4.ip_forward net.ipv4.conf.all.accept_redirects kernel.randomize_va_space
```

## PCI-DSS v4.0 技术验证命令

| 要求 | 验证命令 | 预期结果 |
|------|----------|----------|
| R2.2 默认密码 | `grep -r 'admin:admin\|root:root' /etc/` | 无匹配 |
| R3.4 PAN 保护 | `grep -rE '\b\d{13,16}\b' /var/www/ /opt/app/` | 无明文卡号 |
| R4.1 传输加密 | `testssl.sh --severity HIGH https://target` | TLS 1.2+ |
| R8.3 MFA | 检查 PAM / SSO 配置 | MFA 已启用 |
| R10.1 审计日志 | `systemctl is-active auditd rsyslog` | active |
| R11.3 漏洞扫描 | `trivy fs . --severity HIGH,CRITICAL` | 0 Critical |

