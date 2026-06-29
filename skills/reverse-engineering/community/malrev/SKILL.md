---
name: malware-reverse-engineering
description: 恶意样本逆向分析。静态画像（PE/ELF/Mach-O 元数据、熵、imports、YARA、capa、floss）+ 动态画像（CAPE/Cuckoo/Triage/any.run/Hybrid/Joe）+ 行为分类（dropper/loader/RAT/banker/ransomware/wiper/stealer/miner）+ C2 IOC 提取（域名/URL/JA3/JA4/UA/TLS 指纹）+ MITRE ATT&CK 映射 + YARA/Sigma/Suricata/KQL 规则编写。配合 packrev / memrev / crashrev / scriptrev / docrev 用。
---

# 恶意样本逆向

## 适用场景

- 接到一个可疑文件，30 分钟内出"是不是恶意"判断 + 一句话画像 + 关键 IOC。
- 出深度报告：行为时间线 + C2 + 持久化 + ATT&CK 映射 + 检测规则。
- 大批量分流：用 yara + capa + ssdeep 把上千样本聚成几个家族。
- 应急响应：从 EDR 告警里拿到样本路径 → 速判 + 关联同事件其他主机。

## 不适用

- 加固 / 加壳脱壳本身 → `packrev`。
- 内存快照取证 → `memrev`。
- 文档宏 / OLE / RTF / PDF → `docrev`。
- 脚本字节码（DEX/IL/Lua/pyc） → `scriptrev`。
- 平台特定 API → `winrev` / `linuxrev` / `macrev` / `mrev`。

## 起手三十秒

```bash
sample=suspicious.exe
sha256sum "$sample"
md5sum "$sample"
ssdeep -b "$sample"                                       # fuzzy hash, 找家族
tlsh "$sample"                                            # TLSH 模糊 hash
file "$sample"
trid "$sample"                                            # 概率性文件类型识别
exiftool "$sample" | head -20
stat -c '%y' "$sample"                                    # 时间戳
```

立即对照三大库：

```bash
# VirusTotal CLI (vt-cli)
vt file "$sample"
vt file "$sample" --include=last_analysis_results,reputation,popular_threat_classification

# MalwareBazaar 反查
curl -X POST -d "query=get_info&hash=$(sha256sum "$sample"|cut -d' ' -f1)" \
     https://mb-api.abuse.ch/api/v1/ | jq

# Triage / ANY.RUN 检索
# Browser: app.any.run, tria.ge
```

## 静态画像

### PE / ELF / Mach-O 元数据

```bash
# PE
pefile sample.exe                                          # python -m pefile (输出全表)
pesec sample.exe                                           # 安全特性 (ASLR/DEP/CFG/Authenticode)
sigcheck -a -i sample.exe                                  # Sysinternals: 签名 + IOC
peid sample.exe                                            # 旧但好用：壳 / 编译器识别
DIE.exe sample.exe                                         # Detect It Easy GUI/CLI
exeinfope sample.exe

# python:
python3 - <<'PY'
import pefile, hashlib
pe = pefile.PE('sample.exe')
print('TimeDateStamp:', hex(pe.FILE_HEADER.TimeDateStamp))
print('Entry:', hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint))
print('Sections:')
for s in pe.sections:
    print(f"  {s.Name.decode().strip(chr(0)):8s}  vsize={s.Misc_VirtualSize:08x}  rsize={s.SizeOfRawData:08x}  entropy={s.get_entropy():.2f}")
print('Imphash:', pe.get_imphash())
print('Exports:')
if hasattr(pe,'DIRECTORY_ENTRY_EXPORT'):
    for e in pe.DIRECTORY_ENTRY_EXPORT.symbols[:30]:
        print(f"  {e.name}")
PY

# ELF
readelf -hSld sample.so
checksec --file=sample
elfparser sample

# Mach-O
otool -hVlL sample.dylib
codesign -dvvv sample.dylib
machoview sample
```

### 熵分布（找加密/打包段）

```bash
binwalk -E sample.exe                                      # 熵曲线 (gnuplot)
ent sample.exe
python3 -c "
import math
data = open('sample.exe','rb').read()
def H(b):
    from collections import Counter
    c = Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0
print('overall:', H(data))
# 滑窗
w = 4096
for i in range(0, len(data)-w, w):
    h = H(data[i:i+w])
    if h > 7.5: print(f'{i:#x}: {h:.2f}  HIGH')
"
```

熵基准：
- < 6.0 文本 / 普通代码
- 6.0–7.0 已优化的代码
- 7.0–7.5 压缩 / 编译后的二进制
- 7.5–7.9 加密 / 打包 / 高熵段
- 7.9–8.0 强加密随机数据

### YARA / capa / floss / stringstats

```bash
# YARA 扫已知规则集
yara -r ~/yara-rules sample.exe
yara -r ~/florianroth-signature-base/yara sample.exe
yara-x scan sample.exe --negate                            # YARA-X 新引擎，更快

# capa: 行为能力枚举 (MITRE 出品)
capa sample.exe
capa sample.exe -v                                         # 含命中规则
capa sample.exe -j > capa.json
capa -r ~/capa-rules sample.exe

# floss: 提取被混淆/编码的字符串
floss sample.exe
floss --no-static-strings sample.exe                       # 只看 stack/decoded/tight
floss --format json sample.exe > floss.json

# stringsifter: ML 排序，把 8000 条 strings 按"有意义度"排前 100
strings sample.exe | rank_strings | head -100

# 通用 strings 滤
strings -a -el sample.exe | grep -iE 'http(s)?://|\\\\\\\\|cmd\.exe|powershell|rundll32|regsvr32|schtasks' | sort -u
strings -a -el sample.exe | grep -ioE '[a-z0-9-]+\.[a-z]{2,}\b' | sort -u | head -50
strings -a -el sample.exe | grep -ioE '\b[0-9]{1,3}(\.[0-9]{1,3}){3}\b' | sort -u
```

### 签名 / 时间 / 编译器

```bash
# Authenticode
signtool verify /pa /v sample.exe                           # Windows SDK
sigcheck -a -i -h -hv sample.exe                            # 含吊销检查
osslsigncode verify sample.exe                              # Linux 端

# 时间戳：编译时间 + 链接时间 + 签名时间 + 资源时间
python3 - <<'PY'
import pefile, datetime
pe = pefile.PE('sample.exe')
ts = pe.FILE_HEADER.TimeDateStamp
print('PE TimeDateStamp:', datetime.datetime.fromtimestamp(ts, datetime.timezone.utc))
PY

# 编译器 / 工具链
DIE.exe sample.exe                                          # 显示 compiler/linker/lang
strings sample.exe | grep -iE 'GCC:|Rustc|Go build|Visual Studio' | head
go version sample.exe                                        # Go binary 时直接拿模块清单

# Rich header (Microsoft toolchain fingerprint)
python3 -c "import pefile; pe=pefile.PE('sample.exe'); print(pe.RICH_HEADER.clear_data)"
# Rich header 经常被恶意作者复制粘贴 → 可作族归并指纹
```

## 动态画像

### 沙箱

| 平台 | 形态 | 优点 |
| --- | --- | --- |
| **CAPE Sandbox** | 自部署，Cuckoo3 fork | 自定义最强，含 unpacker |
| **Cuckoo3** | 自部署 | 经典，老牌 |
| **DRAKVUF** | Xen + VMI agentless | 完全无 agent，反沙箱探测低 |
| **ANY.RUN** | SaaS, 交互式 | 实时浏览、人工触发 |
| **Triage (tria.ge)** | SaaS Recorded Future | 行为分类 + 家族识别强 |
| **Joe Sandbox** | 商业 | 报告最细 |
| **VMRay** | 商业 | agentless monitor, 反沙箱低 |
| **Hybrid Analysis** | SaaS | 老牌免费 |
| **Intezer Analyze** | SaaS | 代码基因比对 |

### 自家观察栈（Windows）

```text
进程 / 注册表 / 文件 / 网络 全维度:
  Sysmon (Olaf Hartong / SwiftOnSecurity config)
    EID 1  ProcessCreate
    EID 3  NetworkConnect
    EID 7  ImageLoad
    EID 8  CreateRemoteThread
    EID 10 ProcessAccess
    EID 11 FileCreate
    EID 12-14 Registry
    EID 22 DNSQuery
    EID 25 ProcessTampering
  ProcMon (Sysinternals) - 全实时
  Process Hacker / System Informer
  Wireshark + 自家 CA 解 TLS
  Fakenet-NG / INetSim - 假网络
  RegShot - 注册表前后 diff
  Capa-Explorer + Ghidra 配合
```

### 自家观察栈（Linux）

```bash
# 主流观察
strace -f -e trace=network,file,process -o trace.log ./sample
ltrace -f -o ltrace.log ./sample
sysdig -p '%proc.name %evt.type %evt.args' proc.pid=$pid
falco -c falco.yaml
# eBPF
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("%s\n", str(args->filename)); }'
tracee --output json --filter event=execve,connect

# 网络
tcpdump -i any -nn -s0 -w sample.pcap
mitmproxy --mode transparent --listen-port 8080
fakenet-ng                                                  # 假 DNS+HTTP+SMTP+IRC
```

### 自家观察栈（macOS）

```bash
fs_usage -w -f filesys                                      # 文件 syscall
dtruss ./sample                                             # DTrace 系
sudo dtrace -n 'proc:::exec-success /pid == $pid/ { trace(execname); }'
log stream --predicate 'process == "sample"'                # unified log
opensnoop / execsnoop / dtruss (DTrace.org)
```

## 行为家族分类

```text
Dropper:        启动后扔下一/多个 stage 文件，自删
                典型: WriteFile + ShellExecute + DeleteFile

Downloader:     抓 stage2 from C2，磁盘或内存执行
                典型: WinHTTP/WinINet/URLDownloadToFile + CreateProcess

Loader:         壳层，解密内嵌或拉网络的 payload，注入到合法进程
                典型: VirtualAllocEx + WriteProcessMemory + CreateRemoteThread / NtMapViewOfSection

RAT (Remote Access Trojan):
                长连/心跳 C2，远控命令 (shell/file/screen/keylog/cam)
                典型家族: AsyncRAT / Remcos / NjRAT / Quasar / DarkComet / Cobalt Strike beacon

Banker:         hook 浏览器 + 表单注入 + Webinject + 2FA bypass
                典型家族: Emotet / Trickbot / IcedID / Qakbot / Dridex / Ursnif

InfoStealer:    一次性扫凭据 / cookie / 钱包 / 文档，回传，自毁
                典型家族: RedLine / Raccoon / Vidar / LummaC2 / Stealc / MetaStealer

Ransomware:     枚举文件，加密 (常 ChaCha20/AES + RSA 包裹 key)，留 ransom note
                典型家族: LockBit / BlackCat (ALPHV) / Royal / Akira / Play / Medusa

Wiper:          不要钱，直接破坏 (覆盖文件 / 改 MBR / 改 BCD)
                典型家族: HermeticWiper / WhisperGate / CaddyWiper

Cryptominer:    挂 XMRig 等矿机，吃 CPU/GPU
                关键字: stratum+tcp:// / cryptonight / monero / pool

Worm:           自传播 (SMB / WMI / DCOM / SSH / 漏洞)
                典型: WannaCry (EternalBlue) / Sality / 自家蠕虫

Rootkit:        内核态隐藏 (driver SSDT/IRP hook / DKOM)
                典型: WinNT/Rovnix / Necurs

Backdoor:       后门端口 / 反弹 shell / cron 自启
                典型: Linux/Mirai / Linux/Mozi / Linux/XorDDoS

LOLBin Abuse:   不带 binary，全靠系统自带工具 (mshta/rundll32/certutil/bitsadmin/wmic/powershell)
                典型: Living-Off-The-Land Binaries and Scripts (LOLBAS project)
```

## C2 IOC 提取

```bash
# 1) 字符串里的 URL/IP/域名
strings -a -el sample.exe | grep -ioE 'https?://[a-z0-9.\-/?=_&%]+' | sort -u > c2_urls.txt
strings -a -el sample.exe | grep -ioE '[a-z0-9-]+\.(com|net|org|io|cn|ru|top|xyz|cc|tk|ml|ga|cf|gq)' | sort -u
strings -a -el sample.exe | grep -ioE '\b[0-9]{1,3}(\.[0-9]{1,3}){3}\b' | grep -vE '^(0\.|10\.|127\.|169\.254|172\.(1[6-9]|2[0-9]|3[0-1])|192\.168|22[4-9]|23[0-9])' | sort -u

# 2) DGA (Domain Generation Algorithm) 检测
# DGA 域名特征：长 / 高熵 / 无意义字符 / 多 TLD 轮换
# 工具：DGArchive / dga_predict (ML 分类)
python3 -m dga_predict suspicious-domain.com

# 3) Cobalt Strike beacon 配置提取
1768.py sample.exe                                          # Didier Stevens
cs-extractor sample.bin
cobaltstrike-config-parser sample.exe

# 4) 已知 RAT 配置提取器集合
malware_config_parser sample.exe                            # github.com/jeFF0Falltrades/rat_king_parser

# 5) JA3 / JA4 client TLS 指纹
# 抓 PCAP → ja4 工具
ja4 sample.pcap                                             # github.com/FoxIO-LLC/ja4

# 6) DNS / 网络
dnstwist target-domain.com                                  # 查 typosquat 域名群

# 7) 上传 IOC 到团队 MISP / OpenCTI
misp-cli event create --info "$(date +%F) $sample" --analysis 1 --threat-level 1
```

## 持久化检测面识别

```text
Windows:
  Run / RunOnce / 注册表 (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
  Scheduled Tasks (\Microsoft\Windows\<dir>\<task>)
  Services (sc.exe / services.msc / svchost group)
  WMI Event Subscription (__EventFilter / __EventConsumer)
  AppInit_DLLs / Image File Execution Options (IFEO)
  COM Hijacking (HKCU\Software\Classes\CLSID\{...}\InProcServer32)
  PowerShell Profile / Module Logging bypass
  BITS Job (bitsadmin /transfer)
  ASEPs（Autoruns 自动检 200+ 位置）

Linux:
  systemd unit (/etc/systemd/system /usr/lib/systemd/system)
  cron / cron.d / crontab -u root
  ~/.bashrc / ~/.profile / /etc/profile.d
  /etc/init.d (sysv) / rc.local
  LD_PRELOAD (/etc/ld.so.preload)
  /etc/passwd 新增 UID 0 帐号
  SSH authorized_keys
  /etc/sudoers
  kernel module autoload

macOS:
  LaunchDaemons (/Library/LaunchDaemons)
  LaunchAgents (/Library/LaunchAgents, ~/Library/LaunchAgents)
  Login Items (LSSharedFileList)
  Cron / at
  Login/Logout Hooks
  Periodic / emond
  Configuration Profiles (MDM)
```

工具：

```bash
# Windows
autorunsc.exe -accepteula -a * -h -s -c > autoruns.csv      # Sysinternals 全 ASEP
# Linux
chkrootkit
rkhunter --check
linpeas.sh
unhide
# macOS
KnockKnock.app                                              # objective-see
BlockBlock.app                                              # 实时弹窗
KextViewr.app                                               # 内核扩展审计
LuLu.app                                                    # 出站防火墙
```

## ATT&CK 映射

```text
拿到样本行为后，把每个动作映射到 MITRE ATT&CK technique ID：

Reconnaissance       (TA0043)
Resource Development (TA0042)
Initial Access       (TA0001)   T1566 Phishing  T1190 Exploit Public-Facing App
Execution            (TA0002)   T1059 Command and Scripting  T1106 Native API  T1053 Scheduled Task
Persistence          (TA0003)   T1547 Boot/Logon Autostart  T1543 Create/Modify Service
Privilege Escalation (TA0004)   T1068 Exploitation  T1134 Token Manipulation
Defense Evasion      (TA0005)   T1055 Process Injection  T1027 Obfuscated Files
Credential Access    (TA0006)   T1003 OS Credential Dumping  T1555 Browser Data
Discovery            (TA0007)   T1057 Process Discovery  T1083 File Discovery
Lateral Movement     (TA0008)   T1021 Remote Services  T1570 Lateral Tool Transfer
Collection           (TA0009)   T1056 Input Capture  T1113 Screen Capture
C2                   (TA0011)   T1071 App Layer Protocol  T1572 Tunneling  T1090 Proxy
Exfiltration         (TA0010)   T1041 Exfil over C2  T1567 Exfil over Web
Impact               (TA0040)   T1486 Encrypt for Impact (Ransomware)  T1485 Disk Wipe

工具:
  ATT&CK Navigator                  https://mitre-attack.github.io/attack-navigator/
  pyattck (Python)
  attackcti (Python)
  Mordor / Atomic Red Team          每个 technique 一条复现脚本
  Sigma2Attack                       Sigma 规则自动映射
```

## 检测规则编写

### YARA

```yara
rule Family_LoadingPattern_v1 {
    meta:
        author = "team"
        date = "2024-04-15"
        description = "Detects custom loader from incident XYZ"
        sha256 = "abcdef..."
        score = 85
    strings:
        $imp1 = { 6A 40 68 00 30 00 00 }                    // PUSH 0x40, PUSH 0x3000 (VirtualAlloc)
        $str1 = "Mozilla/5.0 (Windows NT 10.0; x64) Custom/1.0" ascii
        $str2 = "/api/v3/checkin" ascii
        $str3 = "::config::" wide
        $api  = "VirtualAllocEx" ascii
        $api2 = "WriteProcessMemory" ascii
    condition:
        uint16(0) == 0x5A4D
        and filesize < 5MB
        and ($imp1 and $str1)
        or (3 of ($str*) and all of ($api*))
}
```

```bash
# 测试 + 跑全 corpus
yara -r rule.yar /samples/
yara --rules-dir rules/ --target sample.exe
# 性能：用 yara-x 替换老 yara
yara-x scan -r rule.yar /samples/

# 大规模扫：mquery (CERT Polska) / yara-mt
mquery search "rule_name" --limit 1000
```

### Sigma → SIEM

```yaml
title: Loader CreateRemoteThread into LSASS
id: 12345678-1234-1234-1234-123456789012
status: experimental
description: Detect process injection pattern from family XYZ
references:
    - https://...
author: team
date: 2024/04/15
logsource:
    product: windows
    service: sysmon
detection:
    selection:
        EventID: 8
        TargetImage|endswith: '\lsass.exe'
        SourceImage|endswith:
            - '\rundll32.exe'
            - '\regsvr32.exe'
    condition: selection
fields:
    - SourceImage
    - SourceProcessId
    - TargetImage
    - StartAddress
level: high
tags:
    - attack.defense_evasion
    - attack.t1055
```

```bash
# 转换到具体 SIEM
sigma convert -t splunk rule.yml
sigma convert -t elastic rule.yml
sigma convert -t microsoft365defender rule.yml             # KQL
sigma convert -t qradar rule.yml
```

### Suricata / Snort

```text
alert dns $HOME_NET any -> any any (msg:"DNS lookup to known C2 domain"; \
    dns_query; content:"badc2.example.com"; depth:50; \
    classtype:trojan-activity; sid:1000001; rev:1;)

alert http $HOME_NET any -> $EXTERNAL_NET any (msg:"Custom UA from family X"; \
    flow:established,to_server; http.user_agent; content:"Custom/1.0"; \
    classtype:trojan-activity; sid:1000002; rev:1;)
```

### KQL (Microsoft Defender / Sentinel)

```kql
DeviceProcessEvents
| where Timestamp > ago(7d)
| where ProcessCommandLine has_any ("powershell -enc", "powershell -nop", "iex (new-object net.webclient).downloadstring")
| where InitiatingProcessFileName !in ("Code.exe", "msedge.exe")
| project Timestamp, DeviceName, ProcessCommandLine, InitiatingProcessFileName
| order by Timestamp desc
```

## 反沙箱 / 反分析特征识别

```text
样本常用检测点（识别用，知道它在测什么就能反制）：

时间 / 资源:
  - Sleep > 5min before behavior
  - CheckTickCount delta between calls
  - QueryPerformanceCounter
  - rdtsc + cpuid timing
  - CPU 核数 < 2 / RAM < 2GB / 磁盘 < 60GB

用户活动:
  - GetCursorPos 多次比较移动量
  - GetForegroundWindow 标题
  - 桌面图标数 < 5
  - 鼠标点击模拟检测

VM / 沙箱产物:
  - VMware/VBox/Parallels/QEMU 注册表键
  - 硬件 MAC 前缀 (00:0C:29 VMware / 08:00:27 VBox / 00:50:56 VMware / 00:1C:14 VMware / 00:15:5D Hyper-V)
  - cpuid leaf 0x40000000 ("VMwareVMware" / "Microsoft Hv" / "KVMKVMKVM" / "XenVMMXenVMM")
  - Disk size / Drive vendor 字符串
  - 已知沙箱产物文件 (C:\agent.exe / cuckoo.dll)

进程列表:
  - vmtoolsd / vboxservice / qemu-ga / wireshark / procmon / fiddler / sysmon
  - Sandboxie 进程

域 / 主机名:
  - 主机名 = SANDBOX/MALWARE/CUCKOO/UNKNOWN-PC/USER-PC/WIN-XXXXXXX
  - 域 = WORKGROUP 且未加入企业域

反调试:
  - IsDebuggerPresent / CheckRemoteDebuggerPresent
  - PEB.BeingDebugged / NtGlobalFlag / HeapFlags
  - NtQueryInformationProcess(7=ProcessDebugPort, 0x1F=ProcessDebugObjectHandle)
  - 硬件断点检测 (Dr0-Dr7)
  - SetUnhandledExceptionFilter + 故意触发异常
  - INT3 / INT2D 扫描

工具列表见: github.com/LordNoteworthy/al-khaser
```

## 实战入口

- **MalwareBazaar / abuse.ch**：`https://bazaar.abuse.ch` — 海量样本免费下载（含家族标签）。
- **VirusTotal Enterprise / VT Intelligence**：YARA hunting + retrohunt。
- **theZoo**：经典恶意软件研究集 `https://github.com/ytisf/theZoo`。
- **Florian Roth signature-base** / **Elastic protections-artifacts** / **Yara-Rules**：开源 YARA 规则源。
- **The DFIR Report**：每周一篇完整事件链 writeup（绑定 ATT&CK + IOC）。
- **Mandiant FLARE blog / Microsoft Threat Intelligence / SentinelLabs / Trellix ARC / Kaspersky GReAT / ESET WeLiveSecurity / Trend Micro / CheckPoint Research**：APT 与商业恶意家族追踪。
- **vx-underground**：`https://vx-underground.org` — 学术 + 历史样本库。
- **FLARE-On**：Mandiant 年度逆向 CTF（含恶意主题）。
- **MalwareTech / OALabs / Casey Cammilleri / John Hammond / LaurieWired** YouTube：实战 walkthrough。
- **NSA Codebreaker Challenge / SANS Holiday Hack**。

## 自检（拿到样本 30 分钟内回答）

1. 文件类型 / 大小 / 编译时间 / 是否签名 / 签发主体？
2. 加壳 / 加固 / 高熵段位置？是否需要先 `packrev`？
3. Imphash / Rich header / TLSH / ssdeep → 与已知家族有无重合？
4. capa 告诉你哪些 ATT&CK techniques？
5. C2 候选（域名 / IP / URL / 端口 / UA / TLS 指纹）？
6. 持久化方式 + 注入目标进程 + 权限要求？
7. 类别（dropper/loader/RAT/ransomware/stealer/wiper/miner）？
8. 是否有 wormable / 自传播逻辑？
9. 是否带反沙箱 / 反调试 / VM 检测？检测点能否枚举？
10. 写得出 YARA + Sigma 两条检测规则吗？

## 相邻技能

- `binrev` / `winrev` / `linuxrev` / `macrev` — 平台与函数级深挖。
- `packrev` — 加壳样本必须先脱才能进 malrev 静态画像。
- `memrev` — 内存样本（注入到合法进程后的运行体）。
- `crashrev` — 样本本身崩溃 / OOB 反推漏洞。
- `scriptrev` — 脚本 stage（PowerShell / VBS / JS / .NET IL）。
- `docrev` — 文档投递（doc/docx/xlsx/pdf/lnk/iso/one）。
- `protrev` — C2 协议字段位级 / 自家加密通道。
- `cryptrev` — Ransomware key 流程 / C2 加密握手。
- `vmrev` — 自家 VM 保护的核心代码（VMP/Themida）。
- `cloudrev` — 走云端 C2 / 滥用合法 SaaS 的家族。