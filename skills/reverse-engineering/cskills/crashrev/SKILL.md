---
name: crash-exploitability-reverse-engineering
description: 崩溃 / 漏洞可达性逆向。Windows minidump / Linux core / Mach-O core / WER / ASAN/UBSAN/TSan/MSan log / KASAN 内核 panic 分析。崩溃分类（read AV / write AV / SEH / stack overflow / heap corruption / UAF / type confusion / OOB / format string / race）+ root cause 追因 + 可利用性评估（!exploitable、控制流劫持可能、ASLR/DEP/CFG/CET/Shadow stack 状态）。配合 binrev / fuzzrev / memrev / debugrev 用。
---

# 崩溃与可达性逆向

## 适用场景

- 拿到一个 crash dump / core / WER / sanitizer log，回答："是什么崩了？哪一行代码 / 哪个对象出错？复现路径？可利用吗？写得了 exp 吗？"
- Fuzzer 产出几百个 crash，分类 + 去重 + 排可利用性优先级。
- 用户上传崩溃日志，跟踪 root cause 决定打补丁还是 workaround。
- 已知 CVE，反推它的崩溃形态作为 detection signature。

## 不适用

- 找崩溃本身（输入构造） → `fuzzrev`。
- 利用链构造 / shellcode 编写 → 不在本技能范畴。
- 取证级内存快照分析（恶意行为而非崩溃） → `memrev`。
- 静态函数逆向 → `binrev`。

## 崩溃容器速识

| 容器 | 来源 | 大小 | 工具 |
| --- | --- | --- | --- |
| **Windows minidump** (`.dmp`) | WER / `MiniDumpWriteDump()` / Task Mgr | KB-MB（仅栈 + 模块 + 部分堆） | WinDbg / WinDbgX / dotnet-dump |
| **Windows full dump** | `.dump /ma` / SetUnhandledExceptionFilter | GB（完整地址空间） | WinDbg / IDA debugger |
| **Linux core** | `ulimit -c unlimited` / `kernel.core_pattern` | MB-GB | gdb / lldb / pwndbg / coredumpctl |
| **Mach-O core** | `gcore <pid>` / 系统崩溃报告 (.ips) | MB-GB | lldb / Apple CrashSymbolicator |
| **WER report** | C:\ProgramData\Microsoft\Windows\WER\\ | KB-MB | werfault / dump 提取 |
| **Android tombstone** | /data/tombstones/ + logcat | KB | ndk-stack / addr2line / atos |
| **iOS .ips** | 设备 → 设置 → 隐私 → 分析 | KB | symbolicatecrash / atos |
| **Sanitizer log** | ASAN/UBSAN/TSan/MSan 写 stderr | KB | 直接读 + addr2line |
| **kernel oops** | dmesg / /var/log/kern.log | KB | decode_stacktrace.sh + System.map |
| **eBPF crash** | dmesg + verifier log | KB | bpf-trace |

```bash
file unknown.dmp                                            # "Mini DuMP crash report data"
xxd unknown.dmp | head -2                                   # 'MDMP' (PMDM 反字节序)
xxd unknown.core | head -2                                  # ELF 头
unzip -l report.zip                                         # iOS .ips zip 包
```

## Windows minidump (WinDbg)

```bat
windbg -z crash.dmp

:: 自动分析（必跑）
!analyze -v

:: 异常 + 栈 + 寄存器
.exr -1                                                     :: 当前异常记录
.lastevent
kb 50                                                       :: 栈帧 (前 50)
kP                                                          :: 含参数名 (带 PDB)
~* k 30                                                     :: 所有线程栈
r                                                           :: 寄存器
.frame /r N                                                 :: 切到第 N 帧 + 寄存器

:: 模块 + 符号
lm vm                                                       :: 含版本
.symfix+ c:\symbols
.reload /f
!sym noisy                                                  :: 看符号解析过程

:: 堆 / 句柄
!heap -p -a <addr>                                          :: 该地址属于谁的堆块
!handle 0 f                                                 :: 句柄表
!htrace                                                     :: 句柄历史 (需 gflags)
!gflag                                                      :: 当前 gflag

:: 可利用性插件（Microsoft 已经弃但仍能装）
!load winext\msec.dll
!exploitable -v
:: 输出 EXPLOITABLE / PROBABLY_EXPLOITABLE / UNKNOWN / PROBABLY_NOT_EXPLOITABLE / NOT_EXPLOITABLE

:: 现代替代：BugId (MS 出品)
.. powershell:
.. python3 -m bugid -- crash.dmp

:: 对象 / 链表 / RTTI
dt <type> <addr>
dx -r1 ((MyApp!MyClass*)<addr>)
!list -t LIST_ENTRY.Flink -e -x "dt MyApp!Foo" <head>

:: 反汇编
u <addr> L20
ub <addr> L10                                               :: 反向反汇编
.frame 3 ; ub @rip L20

:: 内存
dd <addr> L40
db <addr> L80                                               :: byte
dpa <addr> L20                                              :: 指针 + ASCII
dps <addr> L20                                              :: 指针 + symbol
s -a <range> "AAAA"                                         :: 字符串搜
s -d <range> 0x41414141                                     :: dword 搜
```

### TTD (Time-Travel Debugging) 反向追因

```text
拿到 .run 文件 (TTD trace):
  windbg crash.run
  !tt 0n0                                                   ← 跳到 trace 起点
  g                                                         ← 正向跑
  g-                                                        ← 反向跑
  bp /w "memory write at this addr"                         ← 反向找写者
  ba w4 <addr>                                              ← 反向 hbp 找谁改了某 dword

定位 UAF / heap corruption 的标准动作:
  1. !tt 99 → 跳到崩溃点
  2. 找到崩坏对象 obj_ptr
  3. ba r1 obj_ptr+0x18 → 反向跑找最后写入者
  4. !tt prev → 一路反到 free 调用栈 → 真凶

数据流命令:
  dx @$cursession.TTD.Calls("kernel32!HeapFree")           ← 列所有 HeapFree
  dx @$cursession.TTD.Memory(<addr>, <addr+8>, "w")       ← 该地址所有写
```

## Linux core (gdb / pwndbg)

```bash
# 启用 core
ulimit -c unlimited
echo "core.%e.%p" | sudo tee /proc/sys/kernel/core_pattern

# 或用 systemd-coredump
coredumpctl list
coredumpctl info <pid>
coredumpctl debug <pid>                                     # 直接进 gdb

# gdb 分析
gdb /path/to/binary /path/to/core
(gdb) bt full                                               # 完整栈 + 局部变量
(gdb) info threads
(gdb) thread apply all bt                                   # 所有线程栈
(gdb) info registers
(gdb) p /x $rip
(gdb) x/40i $rip-30                                         # 周边反汇编
(gdb) x/40gx $rsp                                           # 栈内容
(gdb) info proc mappings                                    # 进程地址空间
(gdb) info shared                                           # 共享库

# pwndbg 增强（强烈推荐）
echo "source /usr/share/pwndbg/gdbinit.py" >> ~/.gdbinit
gdb /path/to/binary /path/to/core
pwndbg> context                                             # 寄存器 + 栈 + 反汇编 + 历史一屏
pwndbg> heap                                                # 整个 glibc 堆视图
pwndbg> bins                                                # tcache/fastbin/unsorted/small/large
pwndbg> vmmap                                               # 内存映射
pwndbg> nearpc 20                                           # 附近指令
pwndbg> telescope $rsp 30                                   # 栈追踪
pwndbg> got                                                 # GOT 表
pwndbg> checksec                                            # PIE/NX/Relro/Canary/Fortify

# gef 也很强（pwndbg 替代）
pip install gef
echo "source /path/to/gef.py" >> ~/.gdbinit

# 符号外置
gdb -ex 'set debug-file-directory /usr/lib/debug' binary core
debuginfod                                                  # 联网拉调试符号
DEBUGINFOD_URLS="https://debuginfod.fedoraproject.org/" gdb
```

## macOS / iOS

```bash
# macOS
lldb /path/to/binary -c /cores/core.<pid>
(lldb) bt all
(lldb) thread list
(lldb) frame select 0
(lldb) register read
(lldb) memory read --size 8 --format x --count 40 $rsp
(lldb) image list                                           # 模块列表
(lldb) image lookup --address 0x100002345
(lldb) disassemble -p -c 30                                 # 反汇编当前帧

# iOS .ips 符号化
mkdir crash && cd crash
symbolicatecrash report.ips MyApp.dSYM > symbolicated.crash
atos -o MyApp.app/MyApp -arch arm64 -l 0x102100000 0x102104a30
# 或：xcrun atos -arch arm64e -o MyApp -l 0x100000000 0x100123abc

# crash report → symbolicate
# 自动化（spotify/symbolicator）
symbolicator symbolicate --crash report.ips --symbol-source ./symbols
```

## Android tombstone / NDK

```bash
adb pull /data/tombstones/tombstone_00 tombstone.txt
adb logcat -d "*:F" > native_crash.log

# 自动符号化栈
ndk-stack -sym ./obj/local/arm64-v8a -dump tombstone.txt

# 手动
addr2line -C -f -e libfoo.so 0x000123ab
arm-linux-androideabi-addr2line -C -f -e libfoo.so 0x123ab

# iOS-like atos for Android
echo "0x000123ab" | ndk-stack -sym ./symbols/
```

## 崩溃分类

| 类型 | 信号 / 异常码 | 标志 | 可利用性 |
| --- | --- | --- | --- |
| **Null deref read** | SIGSEGV / 0xC0000005 read at 0x0 | rip 正常 | DoS only（多数）|
| **Null deref write** | SIGSEGV / 0xC0000005 write at 0x0 | rip 正常 | 可能 → 偏移可控时高 |
| **OOB read** | SIGSEGV / fault at heap+large | 通常 ASAN heap-buffer-overflow READ | 信息泄露 |
| **OOB write** | SIGSEGV / heap-buffer-overflow WRITE | 高 | 控制流劫持候选 |
| **Stack buffer overflow** | canary fail / SEGV at ret | __stack_chk_fail | NX 时受限，否则 RCE |
| **Heap overflow (linear)** | malloc_consolidate corrupt | tcache / unsorted bin error | 高（chunk meta） |
| **UAF (use-after-free)** | SIGSEGV at vtable 调用 / 读已 free 块 | ASAN heap-use-after-free | 高（type confusion） |
| **Double-free** | malloc 报错 / abort() | corrupted top chunk | 中-高 |
| **Type confusion** | bad vtable / 调到错误虚函数 | dtype mismatch | 高（C++ / JIT） |
| **Integer overflow** → buf | 之后是 OOB write | int * size 检查不严 | 高 |
| **Format string** | SIGSEGV at puts / printf 内 | %n / %s 任意写读 | RCE / leak |
| **Uninitialized read** | 行为不可重复 | MSan 报 use-of-uninit | 信息泄露 |
| **Race condition** | 时序敏感 / 不易重现 | TSan 报 data-race | TOCTOU / privesc |
| **SEH overflow (Windows)** | exception_record 链断 | EH chain → ret | XP 时代经典，CFG 缓解 |
| **Stack exhaustion** | recursion 太深 | 栈底 vs 栈顶 | DoS |
| **Divide-by-zero** | SIGFPE | int 0 | DoS only |
| **Illegal instruction** | SIGILL | 错位指令 / ROP 调坏地址 | 中 |
| **Bus error** | SIGBUS | 未对齐 / mmap 截断 | 平台相关 |

## Sanitizer log 解读

```text
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x614000000044
WRITE of size 4 at 0x614000000044 thread T0
    #0 0x4ab1c2 in foo /src/a.c:42
    #1 0x4abd33 in main /src/main.c:15

0x614000000044 is located 4 bytes to the right of 64-byte region [0x614000000000,0x614000000040)
allocated by thread T0 here:
    #0 0x498abc in __interceptor_malloc
    #1 0x4ab0a3 in foo /src/a.c:38

SUMMARY: AddressSanitizer: heap-buffer-overflow /src/a.c:42 in foo
```

解读要点：
- `heap-buffer-overflow` / `heap-use-after-free` / `stack-buffer-overflow` / `global-buffer-overflow` / `use-of-uninit` / `double-free`
- `READ` vs `WRITE` → 影响 exploitability
- 偏移：`X bytes to the right/left of N-byte region`，配合源码看是否可控
- allocated by thread → 谁分配；freed by thread → 谁释放
- 数字 thread T0 = 主线程

```bash
# 编译时开 ASAN
clang -fsanitize=address -g -O1 -fno-omit-frame-pointer src.c -o app
./app                                                        # 出错自动报详细信息

# 联合 ASAN + UBSAN + LSAN
clang -fsanitize=address,undefined,leak src.c

# 全套 sanitizer
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:halt_on_error=1 ./app
UBSAN_OPTIONS=print_stacktrace=1 ./app
TSAN_OPTIONS=halt_on_error=1 ./app
MSAN_OPTIONS=poison_in_dtor=1 ./app

# 大型项目用 SyzkalleR + KASAN（内核）
# KASAN 报告样式：
# BUG: KASAN: use-after-free in fn+0xab/0xff [module]
# Read of size 8 at addr ffff... by task ...
```

## 可利用性评估

```text
1) 控制 RIP / EIP 吗？
   崩点 rip = AAAA... or 用户可控 dword → 高可利用
   rip = 合法地址但被劫持的虚表 → 中-高

2) 缓解措施状态
   ASLR (Win: /DYNAMICBASE, Linux PIE): 影响是否需要 leak
   DEP / NX: 排除 ret-to-stack shellcode → 走 ROP
   Stack canary: stack overflow 是否 abort
   CFG (Win), CET shadow stack, IBT: 控制流验证
   SafeSEH / SEHOP: SEH 链利用难度
   GS / fortify_source: 部分 stack overflow 被检测
   Heap hardening (glibc safe-linking, mscrt LFH, Windows segment heap)

   checksec 命令快速看:
   checksec --file=./binary
   # RELRO / Stack / NX / PIE / Canary / Fortify / RWX

3) 漏洞原语类型
   任意写 (arbitrary write) → "what" + "where" 可控？大小？次数？
   任意读 (arbitrary read) → 用于 leak
   相对偏移写 → 受限程度
   悬挂指针 → 喷射 + 重分配
   info leak → 用于绕 ASLR

4) 输入到达性
   崩点是否在 attacker-reachable code path 上？
   是否需要预先认证 / 特权？
   远程触发 vs 本地触发？

5) 沙箱 / 隔离
   浏览器 renderer / sandbox escape 需求？
   容器逃逸 / namespace 突破？

6) 自动化评估工具
   !exploitable (老)
   BugId (微软新)
   exploitable (Mozilla, lldb plugin)
   AFL automated triage + exploitability scoring
   CrashWalk (BlackHat 17)
   afl-cov / fuzzbench 报告
```

## 复现 / 减小输入

```bash
# AFL++ 内置 minimizer
afl-tmin -i original_crash -o min_crash -- ./target @@
afl-cmin -i corpus_in -o corpus_out -- ./target @@           # corpus 整体精简

# honggfuzz minimizer
honggfuzz --minimize -f crash_input -- ./target ___FILE___

# 手动二分（适合大输入）
python3 - <<'PY'
import subprocess
data = open('crash.bin','rb').read()
def crashes(d):
    open('/tmp/t','wb').write(d)
    r = subprocess.run(['./target','/tmp/t'])
    return r.returncode != 0
# binary search …
PY

# 复现脚本（最终交付）
#!/bin/bash
# repro.sh
set -e
./target < crash_input
echo "exit=$?"
```

## 实战入口

- **pwn.college**：免费 binary exploitation 课程（含 crash analysis 章节）。
- **picoCTF / HackTheBox / RealWorldCTF / CSAW CTF binary 题**。
- **Project Zero blog**：Tavis Ormandy / James Forshaw 风格深度 root cause 分析。
- **Google Bug Hunters / Microsoft Security Response Center blog / Apple Security Research**。
- **CrashLab / Microsoft BugId 仓库** — 含真实样本 + 标注。
- **AddressSanitizer cheat sheet / clang sanitizer docs**。
- **WinDbg cheat sheet (DJ FBI / Andrey Kolischak)**。
- **Tavis Ormandy Twitter / @taviso, ulexec, j00ru blog**。
- **Phrack / Argp papers**：heap exploitation 理论。
- **Project Zero "In the Wild" 系列**：野外 0day root cause 复盘。

## 自检（拿到 crash 30 分钟内回答）

1. dump 类型 / 大小 / 是否带符号 / 模块版本？
2. 崩点：模块 + 偏移 + 反汇编 + 源行（如有 PDB/DWARF）？
3. 异常类型（read/write AV / SEH / ASSERT / abort()）？地址 + 大小？
4. 寄存器状态：rip 是否被劫持？哪些用户可控？
5. 栈完整性：canary 是否触发？
6. 哪个对象 / 缓冲区出错？大小？谁分配 / 谁 free（如 UAF）？
7. 缓解措施状态：ASLR / DEP / CFG / Canary / Fortify / RELRO？
8. 触发路径：输入入口在哪？需要什么前置（认证 / 配置 / 时序）？
9. 是否能 minimize 到最小复现？
10. 可利用性等级：DoS / info leak / RCE / sandbox escape？

## 相邻技能

- `binrev` — 函数级反汇编 + 数据流追因。
- `fuzzrev` — 找 crash 的上游。
- `memrev` — 大型 full dump 的取证维度。
- `debugrev` — 动态调试器 + 反复运行 / 条件断点。
- `winrev` / `linuxrev` / `macrev` — 平台 ABI + crash 容器结构。
- `irrev` — 转 IR + 符号执行回推可控变量。
- `diffrev` — 补丁 vs 未补对比，反推漏洞细节。
- `cryptrev` — 崩在加密 / hash 算法内的特殊情况。
- `vmrev` — 自家 VM 崩溃 / handler 写错。
- `malrev` — 恶意样本本身崩溃，反推它在做什么。