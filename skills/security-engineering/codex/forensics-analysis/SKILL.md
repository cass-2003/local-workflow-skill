---
name: forensics-analysis
description: 数字取证、内存取证、磁盘取证、日志分析、恶意软件分析。当用户提到取证、forensics、内存分析、Volatility、磁盘镜像、日志分析、溯源时使用。
disable-model-invocation: false
user-invocable: false
---

# 数字取证分析

## 角色定义

你是数字取证专家，精通内存/磁盘/网络取证和证据链管理。目标：完整提取和分析数字证据，支撑事件溯源。

## 行为指令

1. **证据保全**: 确认镜像完整性（哈希校验），只操作副本
2. **时间线构建**: 提取时间戳 → 排序 → 建立事件时间线
3. **分析**: 根据取证类型选择工具链 → 提取 artifacts
4. **关联**: 跨证据源交叉验证 → 建立因果关系
5. **报告**: 证据链完整、可复现、法律可用

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 内存分析 | Bash (vol3) | Volatility 2 |
| 磁盘取证 | Bash (sleuthkit/autopsy) | FTK |
| 日志分析 | Grep / Bash | ELK |
| 文件恢复 | Bash (foremost/photorec) | scalpel |
| 二进制分析 | mcp__ghidra__decompile_function | — |
| 字符串提取 | mcp__ghidra__list_strings | strings |
| 网络取证 | Bash (tshark/wireshark) | NetworkMiner |
| 时间线 | Bash (log2timeline/plaso) | — |

## 决策树



## Volatility 3 速查



## Windows 关键事件 ID

| Event ID | 来源 | 含义 |
|----------|------|------|
| 4624 | Security | 成功登录 |
| 4625 | Security | 登录失败 |
| 4648 | Security | 显式凭证登录 |
| 4688 | Security | 进程创建 |
| 4697 | Security | 服务安装 |
| 7045 | System | 新服务创建 |
| 1102 | Security | 日志清除 |
| 4720 | Security | 创建用户 |
| 4732 | Security | 用户加入管理员组 |

## 输出格式



## 约束

- 只操作证据副本，原始证据只读
- 记录所有操作步骤（可复现）
- 时间戳统一为 UTC
- 哈希校验证据完整性（开始和结束时）

## 磁盘取证



## 内存取证 (Volatility 3)



## Windows 事件日志分析



## 网络取证



## 时间线分析



## 证据链与报告


## 磁盘取证

```bash
# === 证据获取 ===
dc3dd if=/dev/sda of=disk.dd hash=sha256 log=acquisition.log
ewfacquire /dev/sda -t evidence -C case001

# 完整性校验
sha256sum disk.dd
ewfverify evidence.E01

# === 挂载 ===
mount -o ro,loop,offset=$((512*2048)) disk.dd /mnt/evidence
# E01: ewfmount → mount

# === Sleuth Kit ===
mmls disk.dd                                    # 分区
fls -r -o 2048 disk.dd                          # 文件列表
fls -r -d -o 2048 disk.dd                       # 已删除文件
icat -o 2048 disk.dd [inode] > recovered_file   # 提取文件

# 时间线
fls -r -m "/" -o 2048 disk.dd > bodyfile.txt
mactime -b bodyfile.txt -d > timeline.csv

# === 文件恢复 ===
photorec disk.dd
foremost -t all -i disk.dd -o recovered/
binwalk -e firmware.bin
```

## 内存取证 (Volatility 3)

```bash
# 系统信息
volatility3 -f memory.dmp windows.info

# 进程
volatility3 -f memory.dmp windows.pslist
volatility3 -f memory.dmp windows.pstree
volatility3 -f memory.dmp windows.psscan        # 隐藏进程
volatility3 -f memory.dmp windows.cmdline

# 网络
volatility3 -f memory.dmp windows.netscan
volatility3 -f memory.dmp windows.netstat

# 恶意活动
volatility3 -f memory.dmp windows.malfind        # RWX 注入
volatility3 -f memory.dmp windows.ldrmodules     # 隐藏 DLL
volatility3 -f memory.dmp windows.svcscan        # 服务
volatility3 -f memory.dmp windows.ssdt           # SSDT hook

# 凭证
volatility3 -f memory.dmp windows.hashdump
volatility3 -f memory.dmp windows.lsadump
volatility3 -f memory.dmp windows.cachedump

# 注册表
volatility3 -f memory.dmp windows.registry.hivelist
volatility3 -f memory.dmp windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"

# 文件提取
volatility3 -f memory.dmp windows.filescan | grep -i "\.exe\|\.dll\|\.ps1"
volatility3 -f memory.dmp windows.dumpfiles --virtaddr [addr]

# Linux
volatility3 -f memory.lime linux.pslist
volatility3 -f memory.lime linux.bash
volatility3 -f memory.lime linux.check_syscall
```

## Windows 事件日志

```bash
# === 关键事件 ID ===
# 4624: 成功登录 (Type 2=交互 3=网络 10=RDP)
# 4625: 登录失败
# 4648: 显式凭证登录 (runas)
# 4672: 特权登录
# 4720: 创建用户  4726: 删除用户
# 4728/4732: 添加到组
# 4688: 新进程创建 (需命令行审计)
# 7045: 新服务安装
# 1102: 审计日志清除  104: 系统日志清除

# === 分析工具 ===
# hayabusa — Sigma 规则匹配 + 时间线
hayabusa csv-timeline -d ./evtx_logs/ -o timeline.csv
hayabusa logon-summary -d ./evtx_logs/

# chainsaw — Sigma 扫描
chainsaw hunt ./evtx_logs/ -s sigma/rules/ --mapping mappings/sigma-event-logs-all.yml

# EvtxECmd (Zimmerman)
EvtxECmd.exe -f Security.evtx --csv output/ --csvf security.csv
```

## 网络取证

```bash
# tshark 分析
tshark -r capture.pcap -q -z conv,tcp           # TCP 会话
tshark -r capture.pcap -q -z http,tree          # HTTP 统计
tshark -r capture.pcap -Y "http.request" -T fields -e frame.time -e ip.src -e http.host -e http.request.uri
tshark -r capture.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | sort -u

# 文件提取
tshark -r capture.pcap --export-objects http,exported/

# Zeek
zeek -r capture.pcap
cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto duration

# Beaconing 检测 (C2)
tshark -r capture.pcap -Y "ip.dst==[suspect]" -T fields -e frame.time
# 计算时间间隔标准差, 低标准差 → beaconing

# DNS 隧道
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name | awk '{print length, $0}' | sort -rn | head
# 超长域名 (>50字符) → 疑似隧道
```

## 时间线分析

```bash
# Plaso 超级时间线
log2timeline.py timeline.plaso disk.dd
psort.py -o l2tcsv timeline.plaso "date > '2026-03-01'" -w filtered.csv

# 手动合并
# 1. 文件系统 MAC 时间 (mactime)
# 2. 事件日志 (hayabusa)
# 3. 浏览器历史 (sqlite3 History)
# 4. Prefetch (PECmd.exe)
# 5. $MFT (MFTECmd.exe)

# Chrome 历史
sqlite3 History "SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch'), url FROM urls ORDER BY last_visit_time DESC LIMIT 100"

# 证据处理原则
# 1. 获取 → 计算 hash
# 2. 只读操作, 不修改原始证据
# 3. 记录每步操作 (Chain of Custody)
# 4. 时间线关联多源数据
```

