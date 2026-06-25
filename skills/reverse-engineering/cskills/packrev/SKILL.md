---
name: packer-protector-reverse-engineering
description: 加壳 / 加固识别与脱壳。UPX / MPRESS / ASPack / Themida / VMProtect / Enigma / PECompact / Armadillo / Obsidium / WinLicense + 移动端 360 / 梆梆 / 爱加密 / 腾讯乐固 / Bangcle / Promon / DexGuard。识别壳类型、找 OEP、dump 内存、重建 IAT；FART / FRIDA-DEXDump / blackdex / unidbg 脱 dex；frida-ios-dump / bagbak 脱 FairPlay。配合 binrev / vmrev / malrev / mrev 用。
---

# 壳与加固识别 / 脱壳

## 适用场景

- 拿到一份 PE / ELF / Mach-O / APK / IPA，函数全是垃圾或入口跳到一段乱码 → 先识别壳，再脱掉，再 binrev / malrev。
- 厂内分发的加固产物审计：加固后熵增多少、anti-* 检测点位置、能否绕过反调试。
- 红队自家工具加壳后验证检测面是否暴露（mirror review）。

## 不适用

- 脱完后的函数级分析 → `binrev`。
- VMP / Themida 内部 VM 还原（虚拟化保护核心代码） → `vmrev`。
- iOS 完整 IPA dump / Frida hook → `mrev`。
- 文档 / 脚本类样本 → `docrev` / `scriptrev`。

## 壳类型速识

```bash
# 一键识别（按强度排序，优先级从上到下）
DIE.exe sample.exe                                          # Detect It Easy，最准
exeinfope sample.exe
PEiD.exe sample.exe                                         # 老但还能用
detect-it-easy sample.exe                                   # CLI 版

# Linux
diec sample.exe                                             # 同 DIE 但命令行
yara -r ~/yara-rules/packers sample.exe
nauz-file-detector / nfd sample.exe                         # 同 PEiD 思路

# 看 section 名 + 熵 + 入口位置
python3 - <<'PY'
import pefile, math
from collections import Counter
def H(b):
    if not b: return 0
    c = Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
pe = pefile.PE('sample.exe')
ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
for s in pe.sections:
    nm = s.Name.decode(errors='ignore').strip(chr(0))
    in_ep = '*EP*' if s.VirtualAddress <= ep < s.VirtualAddress + s.Misc_VirtualSize else ''
    print(f"{nm:10s} rva={s.VirtualAddress:08x} vsz={s.Misc_VirtualSize:08x} rsz={s.SizeOfRawData:08x} H={H(s.get_data()):.2f} {in_ep}")
PY
```

### 常见壳的 section 指纹

| 壳 | 典型 section 名 | 备注 |
| --- | --- | --- |
| **UPX** | `UPX0` `UPX1` `UPX2` | 公开规则，`upx -d` 直接脱 |
| **MPRESS** | `.MPRESS1` `.MPRESS2` | 开源，DIE 自动识别 |
| **ASPack** | `.aspack` `.adata` | 老牌 |
| **PECompact** | `.pec1` `.pec2` | 商业老壳 |
| **FSG** | `FSG!` | 早期 |
| **Themida** | `.themida` `.boomerang` / 无规律 | 强保护，含 anti-* + VM |
| **VMProtect** | `.vmp0` `.vmp1` `.vmp2` | 强 VM 保护 |
| **Enigma** | `.enigma1` `.enigma2` `.data1` | 商业 |
| **Armadillo** | `.text1` `.data1` `.adata` | 双进程 / nanomite |
| **Obsidium** | 无规律 + 高熵 | |
| **Sentinel HASP / SafeNet** | 加密 dongle 类 | 含 HASP runtime |
| **WinLicense** | `.themida` + license 段 | Themida 家族 |
| **Confuser / ConfuserEx** | .NET：MD5 化方法名 + 资源内嵌 | de4dot 直接反 |
| **Eazfuscator.NET** | .NET 控制流平坦化 | de4dot |
| **dotNetReactor** | .NET，含 strong-name 验证 + 资源加密 | de4dot |
| **Dnguard HVM** | .NET，方法存在外置 mod | 国产，需自家工具 |
| **Pelock** | 多变种 | |
| **VMProtect 3.x** | `.vmp0` 段消失（伪装），用 entropy 找 | |
| **MoleBox** | 多文件打包成单 exe | |

### 移动端加固速识

```text
Android (APK)：
  360 加固 (Jiagu)：libjiagu.so / libjiagu_64.so / classes.dex 极小
  梆梆 (Bangcle)：libsecexe.so / libsecmain.so / bangcleplugin/
  爱加密 (iJiami)：libexec.so / libexecmain.so
  腾讯乐固 (Tencent Legu)：libshellx-*.so / libshella-*.so / libshellx-super.*.so
  阿里聚安全：libmobisec.so / libmobisecy.so
  网易易盾：libnesec.so
  Promon SHIELD：libpromon.so（金融常用）
  DexGuard：方法名 / 字符串高度混淆 + 反射调用
  ProGuard / R8：开源混淆器，可读 .map / .mapping
  AppSealing：libcovault.so
  Verimatrix XTD：libxtd.so

iOS (IPA)：
  FairPlay：原厂加密 (App Store 下载的全部)，需越狱设备 frida-ios-dump
  iXGuard / iEncryptor：商业加固
  Promon SHIELD iOS：libpromon.dylib
  通常 + Bitcode 上传 + objc 名称混淆
  Themis / Themida iOS：少见
```

```bash
# Android 识别一键
apktool d sample.apk -o out
ls out/lib/*/
file out/lib/arm64-v8a/*.so | head
# 若 classes.dex 才几 KB + lib/ 下有奇怪 .so → 八成被加固
unzip -l sample.apk | awk '$4 ~ /\.dex$/ { print }'
```

## 通用脱壳工作流（用户态 PE）

```text
1. 在受控 VM 里跑样本 → 拿到内存映像
2. 找 OEP (Original Entry Point) → 程序真正的代码起点
3. dump 整个进程内存到磁盘
4. 重建 IAT (Import Address Table)
5. 修复 PE 头 + section + 重建 reloc（或关 ASLR）
6. 重 IDA / Ghidra 加载脱完的 dump
```

### 找 OEP 的常用法

```text
A) ESP 法（最经典）
   起点 EP 通常 push 一堆 reg 到栈保存
   hwbp on ESP 当前值 → 壳出栈恢复时触发 → 几条 ret 后到 OEP

B) 内存断点法
   在 .text 段下 memory access bp
   壳解压代码 → 跳到解压后的 .text 触发 → OEP

C) call/jmp 跨段法
   壳代码通常在 .upx1 / .vmp 段
   设条件断点：if EIP in .text 段 → 命中即 OEP

D) API 法
   壳结束时常 call 真实程序的 GetCommandLineA / GetVersion / GetModuleHandle
   user32!ExitProcess 倒推几层
   bp GetCommandLineA / bp GetModuleHandleA + 看返回栈

E) TLS Callback 法
   有些壳在 TLS callback 先解 → bp on TLS callback

F) 异常法
   壳常 SetUnhandledExceptionFilter + 故意 INT3
   PageGuard / 单步异常处理也常见
   x64dbg 设"忽略所有异常 → 给程序处理" 跑过去
```

### x64dbg + ScyllaHide + Scylla 脱壳

```text
0. 装好 x64dbg 64bit 版 + ScyllaHide 插件 + Scylla 插件
1. 打开 sample.exe → x64dbg 直接 attach 或 load
2. Options → Preferences → Events → 取消 "TLS Callbacks" "System Breakpoints"
   只留 "Entry Breakpoint"
3. ScyllaHide → profile = VMProtect (强反调试) 或 Default
4. F9 跑到 EP → 用上述 A/B/C/D 法找 OEP
5. 到 OEP 后 → Plugins → Scylla
   Attach to active process → Module = sample.exe
   IAT Autosearch → Get Imports → 验证是否完整
   修复 invalid 项（手动 RVA 标 Cut / 重新解析）
   Dump (使用 PE Header)
   Fix Dump → 选择 dumped.exe + IAT 信息 → fixed.exe
6. fixed.exe 用 IDA 重新加载 → 正常分析
```

### 命令式工具（半自动）

```bash
# UPX 标准壳，直接脱
upx -d packed.exe -o unpacked.exe

# UPX 损坏 / 改头的变种
python3 -c "
import lief
p = lief.parse('packed.exe')
for s in p.sections:
    s.name = s.name.replace('foo','UPX')      # 还原段名让 upx 认
p.write('rebuilt.exe')
"
upx -d rebuilt.exe

# unipacker：通用 unpacker (Python + unicorn)
unipacker sample.exe -d ./dumps/

# Universal Unpacker (Ghidra plugin)
analyzeHeadless ./proj proj1 -import sample.exe \
    -postScript GenericUnpacker.java

# qiling 模拟跑出 OEP
python3 - <<'PY'
from qiling import Qiling
ql = Qiling(['sample.exe'], rootfs='./win_rootfs')
def hook(ql, addr, size):
    if 0x401000 <= addr < 0x500000 and addr != ql.entry_point:
        print(f"OEP candidate: {addr:#x}")
        ql.save(snapshot='oep.snap')
        ql.stop()
ql.hook_code(hook)
ql.run()
PY
```

## VMProtect / Themida 战术

```text
VMP / Themida 把关键函数转成自家 VM 字节码：
  原代码段 → 替换成 jmp to vm_entry
  vm_entry → 取 handler 表 + 字节码 → 走 dispatcher → 调 N 个 handler
  每个 handler 完成一条原 x86 语义片段

绕路（看，不要硬怼 VM）：
  1. 找入口函数：通常 VMP 不混淆全部函数，只混淆 license / IAT / 关键判断
     非 VM 函数照常 IDA 反编译
  2. dump 完整内存后，VM 字节码作为 "data" 出现
     把 dispatcher 拉出来，符号化执行整段 vm_entry → 还原 N 条 handler 行为
  3. 工具：
     - vmpunprotect (社区 VMP 1.x/2.x)
     - vmattack (Themida)
     - ThemidaUnmutate (Themida 2/3 部分混淆移除)
     - tigress-protect / NoVmp / VMProtect-Devirtualizer (静态去虚拟化)
     - hex-rays Class Informer + 自家脚本
  4. 动态：直接 hook handler 数组首址，记每次调度，重放出 trace → 反推原 IR
     用 Triton / angr 跑符号执行回收语义

参考资料：
  - rev.ng SymVM 论文
  - SektorCTF VMP 题解
  - LaurieWired VMP YouTube
  - Tiger Team VMProtect tutorials
```

## .NET 加壳 / 混淆

```bash
# de4dot 自动反混淆（支持 30+ 种 .NET 壳）
de4dot sample.exe                                           # 输出 sample-cleaned.exe

# 强 name / Anti-tamper 移除
de4dot -d sample.exe                                        # 仅 detect
de4dot --strtyp emulate sample.exe                          # 字符串解密用模拟器
de4dot -p un sample.exe                                     # unknown 模式
de4dot --keep-types sample.exe

# Confuser / ConfuserEx 专项
ConfuserExUnpacker sample.exe

# dnSpyEx 配合
dnSpyEx sample.exe                                          # 反编译 + 调试 + 修改 + 重保存

# .NET single-file (Apphost bundle)
SingleFileExtractor sample.exe                              # 拆出内嵌 dll
ilspycmd sample.dll > sample.cs
```

## Android 脱壳

```text
通用思路：dex 在内存里解出来 → 找时机 dump

工具按强度从上到下：
1) FART (Fupk3 修改版)
   修改 ART 运行时强制 dump 所有 class
   要 ROOT 设备 + AOSP 编译 / 现成 FART ROM
   优点：稳，几乎所有加固都过
   产物：/sdcard/fart/ 多个 dex

2) FRIDA-DEXDump
   pip install frida frida-tools + DEXDump.py
   frida -U -f com.target.app -l dexdump.js
   原理：扫内存找 dex magic ("dex\n035")，dump 出来
   局限：高强度加固 (360/腾讯) dex 切片散乱，需要重组

3) blackdex (跨 Android 版本)
   APK 形态的 hook 工具，对普通加固即可

4) HyperHide / objection
   objection -g com.target.app explore
   android hooking list classes

5) Xposed / LSPosed + DexDumper module

6) unidbg (无设备模拟 ART)
   纯 Java 模拟 Android linker + libdvm + libart
   适合脱 .so 中加密的 dex
   github.com/zhkl0228/unidbg

7) 自家 ART hook
   写 native module hook ClassLinker::DefineClass
   每次有 class 注册就 dump 它的 dex blob

主流加固对应技巧：
  360 加固 v3+：FART 优先；FRIDA-DEXDump 经常拿到不完整切片
  腾讯乐固：高版本含 anti-FART，需补丁版 ART
  梆梆 / 爱加密：FRIDA-DEXDump 多数能过
  DexGuard 类：不算加固，是混淆，dex 反编译能直接出
```

```bash
# FRIDA-DEXDump 实操
adb shell pm list packages | grep target
adb shell pm path com.target.app                            # 拿 base.apk 路径
adb pull /data/app/.../base.apk

# 启动 frida-server (root device)
adb shell su -c "/data/local/tmp/frida-server &"
frida-ps -U                                                 # 列进程确认 server ok

# DEXDump
git clone https://github.com/hluwa/FRIDA-DEXDump
cd FRIDA-DEXDump
python3 main.py -U -f com.target.app                        # spawn 模式
# 或附加到运行中
python3 main.py -U -p $(frida-ps -U|grep target|awk '{print $1}')

# 输出: ./<pkg>/<process>-<base>-<size>.dex
# 用 jadx-gui 加载
jadx-gui *.dex
```

## iOS 脱壳（FairPlay）

```bash
# 越狱设备 + Frida
# A) frida-ios-dump (最常用)
git clone https://github.com/AloneMonkey/frida-ios-dump
brew install usbmuxd libimobiledevice
pip3 install -r requirements.txt
iproxy 2222 22 &                                            # USB 转 SSH
./dump.py com.target.app                                    # 自动 dump IPA

# B) bagbak (功能更全)
npm install -g bagbak
bagbak com.target.app -o ./output

# C) Clutch (老牌, 需要 jb iOS)
ssh root@ip
Clutch -i                                                   # 列已装应用
Clutch -d com.target.app                                    # dump

# D) dumpdecrypted (最古老)
# 把 dumpdecrypted.dylib 拷到设备 → DYLD_INSERT_LIBRARIES 注入到目标进程

# 拿到 IPA 后 → 进 mrev (Frida hook / IDA 分析 Mach-O)
```

## 反 anti-* 实操

```text
样本启动就 exit / hang → 通常是 anti-debug / anti-VM 命中

绕路（按层次）：
1. PEB.BeingDebugged
   在 attach 前手动 OR EBX, 0x68
   或 ScyllaHide HideBeingDebugged 自动改

2. NtGlobalFlag (PEB + 0x68)
   ScyllaHide HideNtGlobalFlag

3. HeapFlags / ForceFlags
   ScyllaHide HideHeapFlags

4. NtQueryInformationProcess
   ProcessDebugPort (7)
   ProcessDebugObjectHandle (0x1E)
   ProcessDebugFlags (0x1F)
   ScyllaHide HideNtQuery* 三连

5. CheckRemoteDebuggerPresent / IsDebuggerPresent
   钩子返回 0
   ScyllaHide 默认开

6. Hardware breakpoints
   样本 GetThreadContext(GetCurrentThread()) 看 Dr0-Dr7
   ScyllaHide HideContextDebugBits

7. SetUnhandledExceptionFilter + 自家异常
   x64dbg → Options → Exceptions → 选自家处理那些异常码

8. rdtsc / GetTickCount + sleep 时间检测
   ScyllaHide RDTSCEmulation
   或 x64dbg + StaTimeStamp 插件

9. CPU 核数 / RAM / 磁盘大小
   VM 配置 ≥ 真实机 (4 核 / 8GB / 100GB)

10. 已知 sandbox 字符串：用户名 / 主机名 / 域名
    虚拟机里改 hostname = WIN10-SECURED 这类常见名

11. cpuid leaf 0x40000000
    QEMU 改 -cpu host,-hypervisor 或自家 cpu 模板

12. VMware backdoor port (0x5658 magic)
    VMware → 关 isolation.tools.getPtrLocation.disable=TRUE 等

13. MAC 前缀
    VirtualBox → 设置 → 网络 → MAC 改 BC:00:00:11:11:11

工具汇总：
  ScyllaHide (x64dbg/x32dbg 插件) — 用户态全套
  TitanHide (内核驱动) — 更深一层
  PhantOm (OllyDbg 时代)
  Antianti (IDA debugger)
  HyperPlay (硬件级反反调试)
```

## 实战入口

- **crackmes.one**：海量练习样本，分难度。
- **OALabs YouTube + Patreon**：脱壳实战教学最系统。
- **MalwareAnalysisForHedgehogs YouTube**：欧洲思路。
- **看雪 / 52pojie**：中文圈，国产壳脱壳教程最多。
- **Mahmood Nuxt Themida tutorials / Tiger Team writeups**：VMP/Themida 深度。
- **NoMoreRansom 解密家族列表**：勒索家族脱壳与 key 还原案例。
- **vx-underground.org**：壳样本对照学习。
- **PMA 课本（Practical Malware Analysis, No Starch Press）**：经典教材含脱壳章节。
- **MalwareUnicorn workshops**：免费练手 lab。

## 自检（拿到加壳样本 30 分钟内回答）

1. 壳 / 加固类型？版本？是公开壳还是商业壳还是自家壳？
2. section 列表 + 入口段 + 高熵段位置？
3. 含哪些 anti-debug / anti-VM / anti-sandbox 检测点？
4. OEP 候选位置？能用哪几种法找到？
5. IAT 完整还是被加密 / 延迟解析？
6. 是否含 VM 保护核心代码（需要进 `vmrev`）？
7. 脱完的 dump 在 IDA 里能否正常反编译？
8. 移动端：dex 是切片散乱还是单 dex？需要哪种脱壳方案？

## 相邻技能

- `binrev` — 脱完后的函数级分析。
- `vmrev` — VMProtect / Themida / Code Virtualizer 自家 VM 还原。
- `malrev` — 脱壳后做行为画像。
- `mrev` — Android / iOS 整 App 脱壳后逆向。
- `debugrev` — 调试器使用 + ScyllaHide 配置。
- `winrev` / `linuxrev` / `macrev` — 平台特定反调试结构（PEB / TracerPid / dyld）。
- `cryptrev` — 壳的字符串解密 / IAT 解密算法识别。
- `memrev` — 内存里运行态的 unpacked image 提取。
- `scriptrev` — .NET / Java / Lua / Python 加壳。
- `fuzzrev` — 脱完后再 fuzz。