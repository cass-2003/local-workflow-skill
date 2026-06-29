---
name: dynamic-debugging-reverse-engineering
description: 动态调试与运行时观察。gdb (+pwndbg/gef/peda) / lldb / WinDbg / x64dbg / Frida / IDA debugger / Ghidra debugger 实战；高级追踪 strace/ltrace/DTrace/bpftrace/Pin/DynamoRIO/TTD；条件断点 / 硬件断点 / 内存断点 / 脚本驱动；远程调试 gdbserver/OpenOCD/WinDbg kd；反反调试 ScyllaHide/TitanHide；进程注入 + 多线程 / 多进程 / 内核调试。
---

# 动态调试与运行时观察

## 适用场景

- 程序逻辑在静态分析里看不清（混淆 / 间接调用 / VM）→ attach 跑起来看实际行为。
- 找特定函数的调用栈、参数、返回值；改寄存器 / 改内存 / 跳分支测假设。
- hook 某个 API 抓所有调用；写脚本批量取参数 / 改返回值。
- 远程调试嵌入式 / 内核 / 驱动 / 容器内进程。
- 实时观察恶意软件 / 加固应用的运行时解密、网络请求、注入动作。

## 不适用

- 崩溃 dump 离线分析 → `crashrev`。
- 整机内存快照取证 → `memrev`。
- 静态函数级反编译 → `binrev`。
- 找 crash 输入 → `fuzzrev`。

## 调试器选型

| 场景 | 首选 | 备选 |
| --- | --- | --- |
| **Linux 用户态 x86/x64/ARM/RISC-V** | `gdb` + pwndbg / gef | lldb / radare2 + r2dbg |
| **Linux 内核** | `crash` (kdump) / kgdb (qemu) | drgn / lkd |
| **Windows 用户态** | `x64dbg` (GUI 反逆向) / `WinDbg Preview` | OllyDbg (老 32 位) |
| **Windows 内核 / 驱动** | `WinDbg kd` over Network / COM / USB | LiveKD |
| **macOS / iOS** | `lldb` | Hopper debugger / debugserver remote |
| **Android native** | `gdb` + gdbserver + ndk-stack | `lldb-server` + Android Studio |
| **Android Java/Kotlin** | `jadx-gui` + JDB / Android Studio Debugger | jeb-pro |
| **跨平台 hook** | `Frida` (CLI + Python + REPL) | DynamoRIO / Pin |
| **嵌入式 ARM/RISC-V via SWD/JTAG** | OpenOCD + gdb / Black Magic Probe | J-Link GDB Server / Segger Ozone |
| **VM 联机调试** | gdb + qemu `-s -S` + vmlinux | VirtualKD (Windows kernel) |
| **HTTP/JS** | Chrome DevTools / Firefox DevTools | webrev 章节 |
| **.NET / IL** | dnSpyEx | ILSpy + debugger / Rider |
| **Java JVM** | jdb / jdwp + jadx | IntelliJ debug |
| **Python** | pdb / pudb / debugpy + VSCode | PyCharm |
| **Node.js** | node --inspect-brk + Chrome DevTools | ndb |
| **eBPF** | bpftool + bpftrace | bcc tools |

## gdb / pwndbg / gef 实战

```bash
# 起步
gdb ./binary
gdb -p $(pgrep target)                                      # attach 运行中
gdb ./binary core                                           # 调 core
gdb --args ./binary arg1 arg2                               # 带参数
gdb -ex 'set follow-fork-mode child' -ex run ./binary       # fork 时跟子进程

# pwndbg 一行装 (强烈推荐)
git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh

# gef 一行装
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# 关键命令
(gdb) start                                                 # 在 main 处停
(gdb) starti                                                # 在 _start 处停（最早）
(gdb) b *0x401234                                           # 地址断点
(gdb) b foo                                                 # 符号断点
(gdb) b foo if x == 0x42                                    # 条件断点
(gdb) rb ^prefix_                                           # 正则名匹配
(gdb) watch *0x600040                                       # 写断点
(gdb) rwatch *0x600040                                      # 读断点
(gdb) awatch *0x600040                                      # 读写断点
(gdb) catch syscall execve                                  # syscall 断点
(gdb) catch signal SIGSEGV
(gdb) commands 1                                            # 给断点 1 绑命令
> silent
> print/x $rdi
> bt 5
> cont
> end

# 单步
(gdb) si                                                    # step inst
(gdb) ni                                                    # next inst
(gdb) s                                                     # step (source)
(gdb) n                                                     # next (source)
(gdb) finish                                                # 跑到当前函数 ret
(gdb) until *0x401300                                       # 跑到指定地址（同帧）
(gdb) advance foo                                           # 跑到 foo

# 反汇编
(gdb) disas foo
(gdb) disas /m foo                                          # 混合源码
(gdb) disas /r foo                                          # 含字节码
(gdb) x/40i $rip
(gdb) layout asm                                            # TUI 反汇编面板
(gdb) layout regs

# 寄存器
(gdb) info reg
(gdb) p/x $rax
(gdb) set $rax = 0x1                                        # 改寄存器

# 内存
(gdb) x/40gx $rsp                                           # 64-bit hex
(gdb) x/40bx $rsp                                           # byte
(gdb) x/s 0x402000                                          # C string
(gdb) x/40i $rip                                            # instruction
(gdb) find /b 0x400000, 0x500000, 0xde, 0xad, 0xbe, 0xef    # 内存搜
(gdb) set *(int*)0x600040 = 0x41414141                      # 改内存
(gdb) dump binary memory out.bin 0x400000 0x500000          # dump 一段

# pwndbg 增强
pwndbg> context                                             # 一屏全信息
pwndbg> heap                                                # tcache/fastbin/unsorted/...
pwndbg> bins
pwndbg> vis_heap_chunks
pwndbg> telescope $rsp 40                                   # 栈带符号
pwndbg> nearpc 20
pwndbg> got                                                 # GOT 表 + libc 函数
pwndbg> plt
pwndbg> vmmap                                               # 内存映射
pwndbg> checksec
pwndbg> aslr off                                            # 临时关 ASLR
pwndbg> tls                                                 # Thread-local
pwndbg> canary                                              # 找 stack canary
pwndbg> p2p 0x...                                           # ptr-to-ptr 链
pwndbg> search "secret"                                     # 全内存搜字符串

# 脚本驱动 (Python API)
(gdb) python
> import gdb
> class MyBP(gdb.Breakpoint):
>     def stop(self):
>         arg0 = gdb.parse_and_eval("$rdi")
>         print(f"called with rdi={int(arg0):#x}")
>         return False  # 不停下，仅记录
> MyBP("foo")
> end

# 一条命令记录 N 次调用
(gdb) b foo
(gdb) commands
> silent
> printf "rdi=%#lx rsi=%#lx\n", $rdi, $rsi
> cont
> end
```

## lldb 速查（macOS / iOS / FreeBSD / 部分 Linux）

```bash
lldb ./binary
(lldb) process attach --pid 1234
(lldb) target create binary --core core

# 断点
(lldb) b foo                                                # 符号
(lldb) b -a 0x100002345                                     # 地址
(lldb) b -n foo -c 'x == 0'                                 # 条件
(lldb) br set -y main.c:42                                  # 文件:行号

# 单步
(lldb) si / ni / s / n / finish

# 反汇编
(lldb) di -n foo                                            # 函数
(lldb) di -p -c 20                                          # 当前 RIP 前后

# 寄存器 / 内存
(lldb) reg read
(lldb) p/x $rax
(lldb) memory read --size 8 --format x --count 40 $rsp
(lldb) memory write -i input.bin 0x100002000

# Python 脚本驱动
(lldb) script
>>> import lldb
>>> def my_cmd(debugger, command, result, internal):
...     debugger.HandleCommand("bt 5")
>>> __lldb_init_module = lambda d, _: d.HandleCommand('command script add -f my_cmd mc')

# 远程 (debugserver)
# 设备: debugserver *:1234 -a "MyApp"
(lldb) process connect connect://192.168.1.100:1234
```

## WinDbg / x64dbg

### WinDbg Preview（推荐新版）

```text
:: 起步
windbg -p $(pgrep target.exe)
windbg -z crash.dmp
windbg -kd -k com:port=COM1,baud=115200                     :: 内核调试

:: 符号
.symfix+ c:\symbols
.reload /f
!sym noisy

:: 基本
g                                                            :: go
gu                                                           :: go up (finish)
p                                                            :: step over
t                                                            :: step into
pt                                                           :: 到下一个 ret
ph                                                           :: 到下一个 branch
.restart
.detach

:: 断点
bp kernel32!CreateFileW                                      :: 软断
bm kernel32!CreateFile*                                      :: 模式匹配
ba w4 0x12345678                                             :: 写硬断 (4 字节)
ba r1 0x12345678                                             :: 读硬断
bp /1 0x401234 ".printf \"hit\\n\"; g"                       :: 命中一次后自删
bl                                                           :: list
bd 0                                                          :: disable
bc *                                                          :: clear all

:: 数据
dq 0x7ffe0000 L10                                            :: qword
dps esp L40                                                  :: pointer + symbol
da addr                                                      :: ASCII
du addr                                                      :: UNICODE
.printf "%x = %ma\n", @rax, @rax

:: 反汇编
u rip L20
ub rip L10

:: 栈 / 寄存器
k 30
kP                                                            :: 含参数
~* k                                                          :: 所有线程
.frame /r 3
r
r rax = 0x0

:: WinDbg JavaScript (新式脚本)
.scriptload c:\scripts\my.js
dx Debugger.Sessions[0].Processes[0x1234].Threads.Where(t => t.Id == 0x42)
dx -r1 ((nt!_EPROCESS*)@$proc)
```

### x64dbg（GUI 反逆向首选）

```text
快捷键:
  F2  软断
  F4  Run to selection
  F7  Step into
  F8  Step over
  F9  Run
  Ctrl-F9  Execute till return
  Ctrl-F  搜字符串
  Ctrl-G  Go to expression
  *  设硬件断点 (Set HW BP)

Memory map (Alt-M):
  右键 → Find references
  右键 → Dump in dump

Symbols (Ctrl-Alt-S): 列出所有模块 + 符号
References (Ctrl-R): 字符串 / 调用 / 立即数引用

ScyllaHide 插件: 反反调试一站式
  Profile = Themida / VMP / Default
  自动隐藏 PEB/NtGlobalFlag/NtQuery* 等检测点

Scylla 插件: dump + IAT rebuild (脱壳必备)

Conditional Logging (右键断点 → Edit):
  Break Condition: rdi == 0x42
  Log Text: "rdi={rdi} rsi={rsi:s}"
  Command Text: "msg \"hit foo\""
```

## Frida（跨平台 hook 王者）

```bash
# 装
pip install frida-tools

# 列设备
frida-ls-devices
frida-ps -U                                                 # USB Android/iOS
frida-ps -R                                                 # Remote (frida-server)
frida-ps -a                                                 # 仅 application 进程

# spawn vs attach
frida -U -f com.target.app -l hook.js                       # spawn 模式（更早 hook）
frida -U -p 1234 -l hook.js                                 # attach
frida -H 192.168.1.10:27042 -p 1234 -l hook.js              # 远程

# 一行注入
frida -U com.target.app -e 'Java.perform(() => { console.log(Java.use("java.util.Date").$new()); })'

# REPL 交互
frida -U com.target.app
[Pixel::com.target.app]-> Java.use("android.os.Build").MODEL.value
[Pixel::com.target.app]-> Process.enumerateModules()
[Pixel::com.target.app]-> Module.getExportByName("libc.so", "open").readByteArray(16)
```

```js
// hook.js — 通用模板
Java.perform(function () {
    // Java method hook (Android)
    var Http = Java.use("okhttp3.Request$Builder");
    var url = Http.url.overload("java.lang.String");
    url.implementation = function (u) {
        console.log("[okhttp] " + u);
        return url.call(this, u);
    };
});

// Native function hook (任意平台)
var open = Module.getExportByName("libc.so", "open");
Interceptor.attach(open, {
    onEnter: function (args) {
        this.path = args[0].readUtf8String();
        console.log("[open] " + this.path);
    },
    onLeave: function (retval) {
        if (this.path.indexOf("/data/data") === 0) {
            console.log("  -> " + retval);
        }
    }
});

// 改返回值
Interceptor.replace(open, new NativeCallback(function (path, flags) {
    return -1;                                              // 让 open 永远失败
}, 'int', ['pointer', 'int']));

// 反 SSL pinning（标准模板，多家库）
// frida-tools 自带 objection wrapper:
//   objection -g com.target.app explore
//   android sslpinning disable

// 读 / 写任意地址
var p = ptr("0x7ffd1234");
console.log(p.readByteArray(64));
p.writeU32(0x41414141);

// 枚举模块
Process.enumerateModules().forEach(m => console.log(m.name, m.base, m.size));

// 找 RWX 段
Process.enumerateRanges('rwx').forEach(r => console.log(r.base, r.size));

// hook 所有 jmp/call into ranges
Stalker.follow(Process.getCurrentThreadId(), {
    events: { call: true },
    onReceive: function (events) {
        var calls = Stalker.parse(events);
        console.log(calls.length);
    }
});
```

```bash
# Frida 工具集
frida-trace -U -i 'open*' com.target.app                    # 自动生成 hook 模板
frida-trace -U -j 'okhttp3.OkHttpClient!*' com.target.app   # Java 类全方法 trace
frida-trace -U -m '-[NSURLSession dataTaskWithRequest:*]' MyApp   # ObjC
frida-discover -U com.target.app                            # 寻找适合 hook 的函数

# objection（Frida 上面的 CLI 工具，零脚本）
objection -g com.target.app explore
android hooking list classes
android hooking watch class okhttp3.OkHttpClient
android sslpinning disable
ios sslpinning disable
android root simulate
android root disable                                        # 反 root 检测
ios jailbreak disable
memory dump all output.bin
```

## 高级追踪

### Linux

```bash
# strace - syscall
strace -f -e trace=open,openat,connect,execve -o trace.log ./app
strace -p $(pgrep app) -f -tt -s 200 -e network             # attach + 时间戳 + 长字符串
strace -f -c ./app                                          # 统计每种 syscall 次数

# ltrace - libc / 用户态函数
ltrace -f -o lt.log ./app
ltrace -e 'malloc*+free*' ./app
ltrace -p <pid>

# perf
perf record -F 99 -p $(pgrep app) -g -- sleep 10
perf report
perf top -p <pid>
perf trace -p <pid>                                         # strace-like
perf stat -e 'cache-misses,branch-misses' ./app

# bpftrace（一行式 eBPF）
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("%s\n", str(args->filename)); }'
bpftrace -e 'uprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc { @sz[arg0] = count(); }'
bpftrace -e 'uretprobe:/usr/bin/myapp:foo { printf("ret=%lx\n", retval); }'
bpftrace -e 'kprobe:vfs_read { @[comm] = count(); }'        # 每个进程 vfs_read 次数

# bcc tools
sudo opensnoop-bpfcc -p <pid>
sudo execsnoop-bpfcc
sudo tcpconnect-bpfcc
sudo bpftrace /usr/share/bpftrace/tools/biosnoop.bt

# Pin (Intel PIN 二进制插桩)
pin -t MyTool.so -- ./app
# 自家 PIN tool 写 C++ 注入到每条指令 / 函数 / syscall

# DynamoRIO（开源 PIN 替代）
drrun -t drcov -- ./app                                     # 收集 coverage（喂 AFL）
drrun -t drltrace -- ./app                                  # ltrace 风格

# Valgrind 系
valgrind --tool=memcheck ./app                              # 内存错误
valgrind --tool=cachegrind ./app                            # 缓存模拟
valgrind --tool=callgrind ./app                             # 函数调用图
valgrind --tool=helgrind ./app                              # 线程问题
```

### Windows

```text
:: ProcMon (Sysinternals) - 文件/注册表/进程/网络
procmon.exe                                                  :: GUI 实时

:: ETW (Event Tracing for Windows)
wpr -start GeneralProfile
wpr -stop trace.etl
xperf -on Latency -stackwalk profile
xperf -d trace.etl

:: TTD (Time Travel Debugging) - 录制再回放
ttd.exe -out trace.run -- target.exe arg
windbg trace.run

:: API Monitor (rohitab.com) - GUI API hook
:: Detours (Microsoft) - 编程式 hook

:: WinDbg JavaScript trace
dx -r2 Debugger.Sessions[0].Processes[0x1234].Threads
```

### macOS

```bash
# dtrace (默认装 + 需要 SIP off)
sudo dtrace -n 'syscall::open*:entry { trace(execname); trace(copyinstr(arg0)); }'
sudo dtrace -n 'pid$target:::entry { @[probefunc] = count(); }' -p <pid>
sudo dtruss ./app                                           # strace-like
sudo execsnoop -t                                           # 实时 exec
sudo opensnoop -t -n app

# fs_usage / sc_usage / latency
sudo fs_usage -w -f filesys app
sudo sc_usage -e app
sudo latency -rt

# Instruments (XCode bundle)
instruments -t "Time Profiler" -D out.trace ./app
instruments -t "Allocations" -D out.trace ./app
# 现代: xctrace (xcrun xctrace record --template ...)
```

## 反反调试 / Anti-anti-debug

```text
样本检测 → 你需要绕

Windows:
  ScyllaHide (x64dbg/x32dbg/IDA 插件) - 最强用户态全套
    Profile: VMProtect / Themida / Default
    覆盖: PEB.BeingDebugged / NtGlobalFlag / HeapFlags /
          NtQueryInformationProcess(ProcessDebugPort/ObjectHandle/Flags) /
          IsDebuggerPresent / CheckRemoteDebuggerPresent /
          NtSetInformationThread(HideFromDebugger) /
          NtClose 异常陷阱 / NtCreateThread...
  TitanHide (内核驱动) - 比 ScyllaHide 更深
  Phant0m / Antianti (老版 OllyDbg)
  PE-sieve + HollowsHunter (可视化检测)

Linux:
  LD_PRELOAD libfake-ptrace.so 桩 ptrace
  /proc/<pid>/status TracerPid → kernel patch / Frida hook 改返回
  prctl(PR_SET_DUMPABLE) 检测 → ptrace_scope 改为 0
    sudo sysctl kernel.yama.ptrace_scope=0

Android:
  Frida-detection-bypass (一键脚本集合)
  objection --gadget com.target.app explore
  android root disable
  android sslpinning disable
  HyperHide / NotIsolatedHide
  fridantiroot.js (社区脚本)
  Magisk + LSPosed + RootCloak 等模块

iOS:
  iSpy / Liberty Lite / A-Bypass / Choicy
  Frida + fridantiroot equivalent
  objection ios jailbreak disable
```

```js
// fridantiroot.js 风格代码示例（Android）
Java.perform(function () {
    // Block File.exists for su / busybox / magisk paths
    var File = Java.use('java.io.File');
    File.exists.implementation = function () {
        var path = this.getAbsolutePath();
        if (/su|busybox|magisk|xposed/i.test(path)) {
            console.log('[hide] File.exists ' + path);
            return false;
        }
        return this.exists.call(this);
    };

    // Block Build.TAGS check
    var Build = Java.use('android.os.Build');
    Build.TAGS.value = 'release-keys';

    // Block Settings.Secure.getString for adb_enabled
    var Settings$Secure = Java.use('android.provider.Settings$Secure');
    var orig = Settings$Secure.getString;
    Settings$Secure.getString.implementation = function (cr, name) {
        if (name === 'adb_enabled' || name === 'development_settings_enabled') {
            return '0';
        }
        return orig.call(this, cr, name);
    };
});
```

## 远程调试

```bash
# Linux: gdbserver
# 目标
gdbserver :2345 ./target arg1
gdbserver --attach :2345 1234
# 主机
gdb ./target
(gdb) target remote 192.168.1.100:2345

# Kernel via QEMU
qemu-system-x86_64 -kernel vmlinuz -initrd initrd.img -s -S -append "nokaslr"
# 主机
gdb vmlinux
(gdb) target remote :1234

# Linux Kernel kgdb
echo ttyS0,115200 > /sys/module/kgdboc/parameters/kgdboc
echo g > /proc/sysrq-trigger
# 主机串口连接
gdb vmlinux
(gdb) target remote /dev/ttyUSB0

# Embedded ARM/RISC-V via OpenOCD
openocd -f interface/jlink.cfg -f target/stm32f4x.cfg
gdb-multiarch firmware.elf
(gdb) target extended-remote :3333
(gdb) monitor reset halt
(gdb) load
(gdb) c

# Black Magic Probe (BMP)
arm-none-eabi-gdb firmware.elf
(gdb) target extended-remote /dev/ttyACM0
(gdb) monitor swdp_scan
(gdb) attach 1
(gdb) load

# Windows kernel via Network
:: 目标 (admin):
bcdedit /debug on
bcdedit /dbgsettings net hostip:192.168.1.5 port:50000 key:1.2.3.4
:: 主机:
windbg -k net:port=50000,key=1.2.3.4
```

## 实战入口

- **pwn.college** — Pwn College 全免费课程，含调试器实战章节。
- **GuidedHacking forum / YouTube** — 游戏调试 + 内存 patch 实战。
- **Frida Codeshare** — `https://codeshare.frida.re` 现成脚本集。
- **awesome-frida / frida-snippets** — GitHub 大量样板。
- **Microsoft Debugging Tools docs** — WinDbg / TTD 官方教程。
- **OALabs YouTube** — 恶意样本调试实战。
- **MalwareTech YouTube** — 调试 + 反反调试。
- **Jonatas Adoni / 0x90 podcast / LiveOverflow YouTube** — 入门 debugging。
- **Practical Reverse Engineering (Bruce Dang, Wiley)** — 调试章节最系统。
- **The IDA Pro Book (2nd Ed, Chris Eagle, No Starch)**。
- **Linux Kernel debugging book / Bootlin / kernelnewbies.org**。

## 自检（拿到目标 30 分钟内回答）

1. 调试器选型 + attach 还是 spawn？需要远程吗？
2. 反调试检测点位（PEB / TracerPid / ptrace / IsDebugged）能否一次性中和？
3. 关键函数 / 入口点的符号能不能解出来？需要 PDB / dSYM / debuginfod 吗？
4. 怎么用条件 / 硬件 / 内存断点缩小关注范围？
5. 是否需要 Frida / Pin / DynamoRIO 这种插桩级介入？
6. 远程 / 跨设备调试链路通了吗（gdbserver / OpenOCD / kd-net）？
7. 脚本化批量观察怎么写（gdb commands / Python API / Frida JS）？

## 相邻技能

- `binrev` / `linuxrev` / `winrev` / `macrev` — 平台二进制和 ABI。
- `crashrev` — 调试器联动 crash 复现。
- `memrev` — 离线 dump（与 live 调试互补）。
- `packrev` — ScyllaHide + Scylla 流程。
- `malrev` — 调试器附加恶意样本看运行时行为。
- `fuzzrev` — 调试器联动 fuzzer 抓 crash 现场。
- `mrev` — Frida / objection / iOS debugserver 全家桶。
- `irrev` — Pin / DynamoRIO trace 转 IR 做符号执行。
- `vmrev` — 调 dispatcher 抓 handler 索引。
- `hwrev` — OpenOCD / J-Link SWD / JTAG 嵌入式联机。