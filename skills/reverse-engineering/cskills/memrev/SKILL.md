---
name: memory-forensics-reverse-engineering
description: 内存取证逆向。Windows/Linux/macOS/Android 内存快照采集（winpmem、LiME、avml、osxpmem、Lime）+ VM 快照（.vmem / .core / .vmrs）+ Volatility 3 / Rekall 标准插件 + 凭据提取（mimikatz 离线、creddump、impacket-secretsdump）+ 注入痕迹识别（DLL hollowing、unlinked DLL、PEB 篡改）+ 内核结构（EPROCESS/EThread/SSDT/IDT）。配合 winrev / linuxrev / macrev / malrev / crashrev 用。
---

# 内存取证

## 适用场景

- 从被攻陷主机抓 RAM dump / VM 快照，拿出运行进程列表、网络连接、注入痕迹、凭据。
- EDR 告警里只有进程名 + PID，需要从内存里还原它在做什么（已死进程也能找到痕迹）。
- 文件级取证查不到（无落地恶意软件 / fileless malware），只能从内存找。
- 服务端 / DBA 凭据从 LSASS / browser process 提取（自家应急复盘）。
- VM 快照分析：拿到一份 .vmem，复用前面所有内存取证手段。

## 不适用

- 崩溃 dump 分析（仅一个进程，不是全机内存） → `crashrev`。
- 静态二进制函数级 → `binrev`。
- 文件系统取证 (NTFS / ext4 / APFS) → 另技能（本目录暂未包含）。
- 网络流量取证 → `protrev`。

## 内存采集

### Windows

```bash
# winpmem (CrowdStrike 维护)
winpmem.exe -o mem.raw                                      # 全机内存
winpmem.exe -F mem.aff4                                     # AFF4 容器
winpmem.exe --format map -o mem.map mem.raw                 # 物理地址映射

# DumpIt (Comae，简单粗暴)
DumpIt.exe                                                  # 输出 <host>-<time>.raw

# FTK Imager (商业，GUI)
# 选 Capture Memory → 输出 .mem

# Magnet RAM Capture (Magnet Forensics 免费)
# https://www.magnetforensics.com/resources/magnet-ram-capture/

# Microsoft 自家
# - Hibernation file: C:\hiberfil.sys (休眠时内存压缩快照)
# - Pagefile: C:\pagefile.sys (虚拟内存交换)
# - Crash dump: C:\Windows\MEMORY.DMP (BSOD)
hibrec.py hiberfil.sys -o hiber.raw                         # Volatility 内含工具
```

### Linux

```bash
# LiME (Linux Memory Extractor)
git clone https://github.com/504ensicsLabs/LiME
make -C LiME/src
sudo insmod LiME/src/lime-$(uname -r).ko "path=/tmp/mem.lime format=lime"
# format: raw / padded / lime（推荐 lime，含 metadata）

# avml (Microsoft Azure 出品，单二进制，无内核模块)
sudo ./avml output.lime
sudo ./avml --compress output.lime.zst                      # zstd 压缩

# /proc/kcore (内核物理 + 部分虚拟，活机限定)
sudo dd if=/proc/kcore of=kcore.dump bs=1M count=2048

# kdump (panic 后自动落盘)
ls /var/crash/                                              # 查看历史

# pmemsave (QEMU 监控)
(qemu) pmemsave 0 0x80000000 /tmp/mem.raw

# fmem (老牌内核模块)
sudo insmod fmem.ko
sudo dd if=/dev/fmem of=mem.raw bs=1M
```

### macOS

```bash
# osxpmem (Volatility Foundation, 老版本)
sudo ./osxpmem.app/MacPmem.kext  # 加载内核扩展（需 SIP off + recovery 装）
sudo osxpmem -o mem.aff4

# MacQuisition (商业)
# Volexity Surge Collect (商业, 当前最强)
sudo SurgeCollect-Pro --collect-memory --output mem.lime

# 系统休眠：/var/vm/sleepimage
sudo cp /var/vm/sleepimage /tmp/sleep.raw                   # FileVault 时不可用

# Apple Silicon (M1/M2/M3) 限制：
# SIP + APRR + Apple Memory Protection 让内存采集非常困难
# Volexity Surge 是目前唯一商业方案；DFU 模式 + checkra1n 类越狱也是路径
```

### Android

```bash
# LiME on Android（需 root + kernel 编译）
adb push lime.ko /sdcard/
adb shell su -c "insmod /sdcard/lime.ko 'path=/sdcard/mem.lime format=lime'"
adb pull /sdcard/mem.lime

# 直接读 /dev/kmem 或 /proc/kcore（多数 ROM 已禁用）

# AVML for Android (zlocker 移植)
# 现实里：vendor ROM 限制内核模块 + selinux + 验证启动 → 大多数厂机无法直接抓
# 折中：抓 hiber-like 数据 / app heap dump
adb shell am dumpheap -n <pid> /sdcard/app.hprof
adb pull /sdcard/app.hprof
```

### VM 快照（无需 agent）

```text
VMware:                .vmem          (运行) / .vmss + .vmem (suspend)
VMware ESXi:           .vmem          + .vmsn (snapshot)
VirtualBox:            .sav           (suspend) / 内存在 .vbox + .vdi
Hyper-V:               .vmrs + .bin   (saved state)
KVM/QEMU:              virsh dump --memory-only <dom> mem.raw
                       virsh save <dom> state.save        (含内存 + 状态)
Xen:                   xl save / xenctx
Parallels:             .mem 在 .pvm 包内
AWS EC2:               aws ec2 create-instance --user-data → 触发 dump（间接）

直接喂 Volatility:
volatility -f win10.vmem --profile=Win10x64_19041 pslist
vol3 -f win10.vmem windows.pslist
```

## Volatility 3 标准工作流

```bash
# 装 vol3
pipx install volatility3
# 或
git clone https://github.com/volatilityfoundation/volatility3
pip install -r requirements.txt

# 0) 起手识别
vol3 -f mem.raw windows.info                                # Windows 版本 + 内核基址
vol3 -f mem.raw linux.banner                                # Linux 内核版本
vol3 -f mem.raw mac.kernel_module                           # macOS

# Linux/macOS 需先生成符号包 (ISF JSON)
# Linux: 用 dwarf2json
dwarf2json linux --elf /usr/lib/debug/.../vmlinux > /opt/vol3/symbols/linux/ubuntu-22.04.json
# macOS: 用社区 ISF 包
git clone https://github.com/volatilityfoundation/volatility3-symbols
```

### Windows 核心插件

```bash
# 进程
vol3 -f mem.raw windows.pslist                              # _EPROCESS 链表
vol3 -f mem.raw windows.psscan                              # 物理扫描（含 unlinked / 已退出）
vol3 -f mem.raw windows.pstree                              # 父子树
vol3 -f mem.raw windows.cmdline                             # 命令行
vol3 -f mem.raw windows.envars                              # 环境变量
vol3 -f mem.raw windows.handles --pid 1234
vol3 -f mem.raw windows.privs                               # 进程特权
vol3 -f mem.raw windows.getsids                             # 用户 SID

# 模块 / DLL
vol3 -f mem.raw windows.dlllist --pid 1234
vol3 -f mem.raw windows.ldrmodules --pid 1234               # 三链对比（InLoadOrder/InMemoryOrder/InInitializationOrder），unlinked = 注入
vol3 -f mem.raw windows.modules                             # 内核模块
vol3 -f mem.raw windows.modscan                             # 物理扫描
vol3 -f mem.raw windows.driverirp                           # 内核驱动 IRP 表
vol3 -f mem.raw windows.driverscan
vol3 -f mem.raw windows.ssdt                                # System Service Descriptor Table

# 网络
vol3 -f mem.raw windows.netscan                             # TCP/UDP 连接 + 监听
vol3 -f mem.raw windows.netstat
vol3 -f mem.raw windows.dnscache                            # DNS 缓存

# 注入检测
vol3 -f mem.raw windows.malfind                             # 可疑可执行内存区域（VAD + PE 头扫描）
vol3 -f mem.raw windows.hollowfind                          # 进程空洞化
vol3 -f mem.raw windows.threads                             # 线程列表
vol3 -f mem.raw windows.callbacks                           # 内核回调（rootkit 标志）
vol3 -f mem.raw windows.svcscan                             # 服务（rootkit 常 hide）

# 内存提取
vol3 -f mem.raw windows.dumpfiles --pid 1234                # dump 进程文件映射
vol3 -f mem.raw windows.memmap --pid 1234 --dump            # dump 整个进程虚拟内存
vol3 -f mem.raw windows.vadinfo --pid 1234                  # VAD 树
vol3 -f mem.raw windows.vadwalk --pid 1234

# 注册表
vol3 -f mem.raw windows.registry.hivelist
vol3 -f mem.raw windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"
vol3 -f mem.raw windows.registry.userassist                  # UserAssist 启动历史

# 凭据
vol3 -f mem.raw windows.hashdump                             # SAM SAM hashes (LM/NTLM)
vol3 -f mem.raw windows.lsadump                              # LSA secrets
vol3 -f mem.raw windows.cachedump                            # MS Cache hash (Domain cached creds)
```

### Linux 核心插件

```bash
vol3 -f mem.lime linux.pslist                               # task_struct 链
vol3 -f mem.lime linux.psscan                               # 物理扫描
vol3 -f mem.lime linux.pstree
vol3 -f mem.lime linux.psaux                                # ps aux 风格
vol3 -f mem.lime linux.bash                                 # bash 历史（从内存里抠）
vol3 -f mem.lime linux.lsmod                                # 内核模块
vol3 -f mem.lime linux.check_modules                        # 隐藏模块
vol3 -f mem.lime linux.check_syscall                        # syscall 表完整性
vol3 -f mem.lime linux.check_idt                            # IDT 完整性
vol3 -f mem.lime linux.tty_check
vol3 -f mem.lime linux.elfs --pid 1234                      # 内存中的 ELF
vol3 -f mem.lime linux.proc.Maps --pid 1234                 # /proc/pid/maps 视图
vol3 -f mem.lime linux.malfind                              # 可疑映射
vol3 -f mem.lime linux.sockstat                             # socket
vol3 -f mem.lime linux.iomem                                # /proc/iomem
```

### macOS 核心插件

```bash
vol3 -f mac.lime mac.pslist
vol3 -f mac.lime mac.psaux
vol3 -f mac.lime mac.lsmod                                  # 内核扩展 (kext)
vol3 -f mac.lime mac.kauth_listeners                        # 内核回调
vol3 -f mac.lime mac.malfind
vol3 -f mac.lime mac.netstat
vol3 -f mac.lime mac.dmesg
```

## 凭据提取

```bash
# 离线 mimikatz：把 lsass 内存 dump 出来，再到隔离机跑
# 方法 1：先在主机用 Task Manager 或 procdump 抓 lsass.dmp
procdump.exe -ma lsass.exe lsass.dmp                        # Sysinternals
# 方法 2：vol3 dump 整个 lsass 进程
vol3 -f mem.raw windows.memmap --pid $(vol3 -f mem.raw windows.pslist | grep lsass | awk '{print $3}') --dump

# 拿到 lsass.dmp 后用 mimikatz 离线模式
mimikatz # sekurlsa::minidump lsass.dmp
mimikatz # sekurlsa::logonpasswords full

# 或用 pypykatz (Python 纯实现，无需 mimikatz)
pip install pypykatz
pypykatz lsa minidump lsass.dmp
pypykatz lsa minidump lsass.dmp -k /tmp/keys -o /tmp/creds.txt

# vol3 直接出 hash
vol3 -f mem.raw windows.hashdump > hashes.txt               # LM:NTLM
vol3 -f mem.raw windows.lsadump > lsa.txt                   # LSA secrets
vol3 -f mem.raw windows.cachedump > mscache.txt             # MS Cache (DCC2)

# 破解
hashcat -m 1000 hashes.txt rockyou.txt                      # NTLM
hashcat -m 2100 mscache.txt rockyou.txt                     # DCC2
john --format=NT hashes.txt
john --format=mscash2 mscache.txt

# Active Directory: ntds.dit 离线
impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL    # 离线全部 hash
impacket-secretsdump 'DOMAIN/user:pass@dc.ip'               # 在线

# Linux: shadow / faillog 内存抠
vol3 -f mem.lime linux.envars --pid 1                       # PAM 时常透露
strings mem.lime | grep -E '^\$6\$|^\$y\$' | sort -u        # shadow hash 残留

# 浏览器 cookie / token / 表单
vol3 -f mem.raw windows.dumpfiles --pid <chrome> --regex 'Login Data|Cookies'
# 离线解 Chrome encrypted_value (DPAPI)
hashcat -m 16800 chrome.hash wordlist                       # 间接路径

# SSH agent / GPG agent / 1Password / Keychain 残留
strings -el mem.raw | grep -iE 'sshv2|ssh-rsa|BEGIN OPENSSH|BEGIN RSA|API_KEY|access_token|Bearer ' | sort -u | head
```

## 注入痕迹识别

```text
1) DLL Injection (LoadLibrary)
   - CreateRemoteThread → LoadLibrary
   - 痕迹: 目标进程多出一个 DLL，名字不在常规 image list
   vol3 windows.dlllist | sort | uniq → 比对未注入基线

2) Reflective DLL Loading (Stephen Fewer)
   - 内存中存在 PE 头但 windows.ldrmodules 三链不一致（unlinked）
   vol3 windows.ldrmodules --pid X
   # 三列 inload/inmem/ininit 不全部 True 的就是嫌疑

3) Process Hollowing
   - 创建合法进程（SUSPEND）→ unmap 主映像 → 写入恶意 PE → ResumeThread
   - 痕迹: PEB.ImageBaseAddress 指向 PE 但 VAD 该区域不是 IMAGE 类型
   vol3 windows.hollowfind
   vol3 windows.malfind

4) Process Doppelgänging / Process Herpaderping / Mockingjay
   - 利用 NTFS transaction / Section 创建技巧绕过 EDR
   - 痕迹: VAD 类型与 FILE_OBJECT 不一致
   vol3 windows.dumpfiles --pid X + 比对磁盘 PE

5) APC Injection (NtQueueApcThread)
   - 痕迹: 线程 ApcStateIndex 异常 / 不熟悉的 user APC
   vol3 windows.threads

6) AtomBombing / SetWindowsHookEx / Manual Map
   - 痕迹各异，统一靠 malfind 扫高熵 RWX

7) Linux:
   - LD_PRELOAD → 看 /proc/<pid>/maps 多出 .so
   - ptrace 注入 → vol3 linux.malfind 可疑 anonymous mmap
   - process_vm_writev / dlopen via remote → strings 找 dlopen 字符串

8) macOS:
   - DYLD_INSERT_LIBRARIES → vol3 mac.dyld_lsm
   - task_for_pid + mach_vm_write → 抓不到 launchctl 痕迹
   - injected dylib 不出现在 _dyld_image_count() 的合法列表里
```

## 大文件字符串 + YARA + bulk_extractor

```bash
# strings 暴力扫
strings -el -n 8 mem.raw | grep -iE 'http(s)?://|cmd\.exe|powershell|/etc/shadow' | sort -u > urls.txt

# bulk_extractor: 一键扫所有特征 (邮件 / URL / IPv4 / 信用卡 / domain / pcap)
bulk_extractor -o bulk_out mem.raw
ls bulk_out/                                                # email.txt url.txt domain.txt ip.txt pcap.pcap aes_keys.txt
# 它会自动提 AES key, RSA key, 邮件地址, URL, 域名

# YARA 跑内存
yara -r ~/yara-rules mem.raw
yara -r ~/yara-rules mem.raw --print-strings --print-meta

# 大于 4GB dump 时 yara 慢，可用 yara-x
yara-x scan -r rule.yar mem.raw

# 已知壳 / RAT 配置提取器
1768.py mem.raw                                             # 扫所有 CS beacon config

# AES key 扫描（aeskeyfind / interrogate / volatility aeskeyfind 插件）
aeskeyfind mem.raw
rsakeyfind mem.raw
```

## 内核结构速查

```text
Windows _EPROCESS (Win10+ 偏移会变, 用 vol3 自动算):
  +0x000  Pcb (_KPROCESS)
  +0x180  ProcessLock (_EX_PUSH_LOCK)
  +0x440  CreateTime / ExitTime
  +0x440  UniqueProcessId
  +0x448  ActiveProcessLinks (LIST_ENTRY)        ← pslist 走这条链
  +0x4b8  Token (_EX_FAST_REF)                    ← 提权痕迹
  +0x508  ImageFilePointer (FILE_OBJECT*)
  +0x5a8  ImageFileName (16 char)
  +0x418  Peb (_PEB*)

Windows _ETHREAD: ThreadListEntry / StartAddress / Win32StartAddress / Cid

Linux task_struct (内核版本敏感, 用 dwarf2json 自动):
  pid / tgid / comm[16]
  thread_info / mm_struct (mm->mmap 链 = 内存映射)
  fs_struct (cwd / root)
  files_struct (fd 数组)
  parent / real_parent / children / sibling

SSDT / IDT / IRP MajorFunction Table:
  内核 rootkit 常 hook 这些表
  vol3 windows.ssdt + 验签每一项是否指向 ntoskrnl.exe 模块范围内
  vol3 linux.check_syscall 类似

ProcessHandleTable / HandleTableEntry:
  打开句柄信息 (token / process / file / mutant / event)
  vol3 windows.handles --object-type=Token
```

## EDR / Tetragon / Velociraptor 联动

```bash
# Velociraptor: agent-based DFIR (Rapid7 系列后续)
velociraptor --config server.config.yaml frontend &
# 客户端
velociraptor --config client.config.yaml client &
# 服务端 → Hunts → Generic.Forensic.Memory → 全网内存采集

# GRR (Google Rapid Response, 比较老)
# osquery + Fleet 远程审计（轻量替代）
osqueryi
osquery> SELECT pid, name, cmdline FROM processes WHERE on_disk = 0;   # 不在磁盘上的进程

# Falco / Tracee / Tetragon (eBPF 实时)
falco -r /etc/falco/falco_rules.yaml
tetragon --tracing-policy policy.yaml
# 实时事件可补充内存取证的"时间窗口缺失"
```

## 实战入口

- **SANS FOR508 / FOR526 / FOR518**：DFIR 系统训练。
- **The Art of Memory Forensics (Ligh, Case, Levy, Walters)**：标准教材。
- **13Cubed YouTube**：免费内存取证短视频集，含 Volatility 3 工作流。
- **HackTheBox Sherlocks / DFIR.science / dfir.training**：靶场。
- **MemLabs (CTF)**：`https://github.com/stuxnet999/MemLabs`。
- **Volatility Foundation Plugin Contest**：每年优秀插件，覆盖最新检测面。
- **Velocidex Forensics blog / Volexity blog / Mandiant blog**：真实事件 writeup。
- **Black Hat / DEF CON DFIR / SANS Summit talks**。

## 自检（拿到内存 dump 30 分钟内回答）

1. dump 格式 / 大小 / 来源主机 + 操作系统 + 内核版本？
2. 进程列表对比已知基线，有哪些不该出现？parent 链是否合理？
3. unlinked / hidden 进程（psscan vs pslist 差集）有几个？
4. 网络连接：netscan 输出中有几个对外 TCP？目标 IP 是否归属可疑 ASN？
5. 注入痕迹：ldrmodules unlinked 数量？malfind 命中段数量？hollowfind 命中？
6. 服务 / 驱动 / SSDT / IDT 完整性？是否有未签名 / 异常内核回调？
7. 凭据：能否拿到 NTLM / DCC2 / LSA / cleartext token？
8. bulk_extractor / strings 扫到的关键 URL / IP / domain / API key？

## 相邻技能

- `winrev` / `linuxrev` / `macrev` — 平台内核结构 + 进程模型。
- `malrev` — 内存里运行体的行为画像。
- `crashrev` — 崩溃 dump（单进程 vs 全机内存的差别）。
- `packrev` — 内存里的 unpacked image 还原 → 喂回静态分析。
- `binrev` — dump 出的进程 PE/ELF/Mach-O 函数级分析。
- `protrev` — 抓到的网络连接对应的协议解析。
- `cryptrev` — 内存里残留的密钥 / 证书还原。
- `cloudrev` — 云主机 EC2/VM snapshot 取证。
- `containerrev` — 容器内进程的内存视图。
- `iotrev` / `fwrev` — 嵌入式设备内存抓取（多通过 JTAG / 硬件级，难度高）。
- `debugrev` — live 主机调试器附加（与离线 dump 互补）。