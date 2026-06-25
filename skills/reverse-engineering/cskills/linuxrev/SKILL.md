---
name: linux-elf-reverse-engineering
description: Linux ELF 运行生态逆向。dyld/glibc/musl 加载链、syscall/vDSO/ptrace 接口、procfs/sysfs/netlink 取证、LD_PRELOAD 与 ptrace 注入面、systemd/cron/xdg 持久化点、AppArmor/SELinux/seccomp/capabilities 隔离面、glibc 内部数据结构、tcache/jemalloc 堆布局、eBPF 监控；ELF 结构本身在 binrev。
---

# Linux ELF 运行生态逆向

## 适用场景

- 在 Linux 上跑的二进制，要回答："它启动后做了什么 syscall？谁在 fork？哪里在 mmap？哪个文件描述符通到哪里？怎么持久化？"
- Linux 平台样本的注入面 / 监控面 / 持久化面识别（LD_PRELOAD / ptrace / inotify / eBPF / systemd / cron / autostart）。
- 内存样本（`/proc/<pid>/maps` + core dump + LiME）的运行时画像。
- 容器内部 ELF 与宿主隔离边界（namespaces / cgroups / seccomp）的辨识。

## 不适用

- ELF 头 / 段 / 函数 / 调用图本身 → `binrev`。
- 内存取证 / coredump 解析 → `memrev` / `crashrev`。
- 内核驱动 / kmod 内部 → 平台 + `irrev`。
- 嵌入式 / 不带常规 glibc 的 BusyBox/Buildroot 镜像 → `fwrev`。

## ELF 加载链速记

```text
execve("./prog", argv, envp)
  └─ kernel 解析 ELF header
       ├─ 静态: 直接跳 e_entry
       └─ 动态: 装载 PT_INTERP（默认 /lib64/ld-linux-x86-64.so.2 / /lib/ld-musl-x86_64.so.1）
            └─ ld 接管 → 解析 PT_DYNAMIC
                  ├─ DT_NEEDED 列表 → dlopen 顺序加载 libc / libpthread / ...
                  ├─ 写 GOT/PLT 重定位（DT_RELA/RELR/JMPREL）
                  ├─ 跑 DT_INIT_ARRAY、DT_PREINIT_ARRAY、DT_INIT
                  └─ 跳 e_entry → _start (CRT) → __libc_start_main → main()
```

环境影响加载行为的环境变量：

```bash
LD_PRELOAD=/path/lib.so ./prog          # setuid 二进制忽略；非 setuid 强制加载
LD_LIBRARY_PATH=...                      # 找 .so 路径
LD_BIND_NOW=1                            # 立即绑定，禁用 lazy
LD_DEBUG=files,bindings,libs,statistics  # 详细加载日志（调试 ld 用）
LD_AUDIT=lib.so                          # 加载审计接口（rtld-audit(7)）
LD_TRACE_LOADED_OBJECTS=1                # 等价 ldd
```

setuid / setgid / capabilities / hardened 二进制屏蔽 LD_PRELOAD 与 LD_LIBRARY_PATH。

## procfs / sysfs / 进程视角

```bash
# 进程画像
PID=$(pgrep -nf prog)
ls -al /proc/$PID/                          # cwd, exe, root, fd/
cat /proc/$PID/status                       # uid/gid/cap/seccomp/state
cat /proc/$PID/maps | column -t             # 内存映射（含库基址、堆、栈、vdso、vvar）
cat /proc/$PID/smaps                        # 每段 RSS/PSS/Pss/Anon/Locked
ls -al /proc/$PID/fd/ | head                # 打开的文件 / socket / eventfd / inotify
cat /proc/$PID/cmdline | tr '\0' ' '
cat /proc/$PID/environ | tr '\0' '\n'
cat /proc/$PID/limits                       # ulimit 视图
cat /proc/$PID/syscall                      # 当前在第几号 syscall
cat /proc/$PID/wchan                        # 内核里阻塞在哪个函数
cat /proc/$PID/stack                        # 内核栈
cat /proc/$PID/sched
cat /proc/$PID/cgroup                       # 容器边界关键
cat /proc/$PID/ns/{pid,net,mnt,uts,ipc,user,cgroup} | xargs ls -la

# 网络 socket → fd
ss -tnp | grep $PID
ss -xnp | grep $PID                         # unix domain socket
lsof -p $PID -nP

# 内核模块 / 驱动
lsmod
cat /proc/modules
cat /proc/kallsyms | grep -i target_func    # 需 root 且 kptr_restrict=0

# 系统调用编号映射
cat /sys/kernel/debug/tracing/events/syscalls/sys_enter_*/format | head
```

## syscall 追踪

```bash
# 全部 syscall + 时间戳
strace -ff -tt -T -y -yy -s 256 -o tr.log -- ./prog arg1
# -y/-yy 把 fd 显示成路径/socket，调试 IO 极有用
# -e trace=network,file,desc 缩小范围
# -e inject=openat:retval=-1                                # 故意注错值
# -e fault=openat:error=EACCES                              # 故意失败一次

# 库函数
ltrace -f -tt -e '*' -o lt.log -- ./prog
ltrace -e '@libcrypto.so.3' -- ./prog                       # 只看 OpenSSL

# 高精度 + tracepoint
perf trace -p $PID --duration 1
bpftrace -e 'tracepoint:syscalls:sys_enter_openat /comm == "prog"/ { printf("%s\n", str(args->filename)); }'

# eBPF 通用
bcc tools: opensnoop, execsnoop, tcpconnect, biolatency, ...
```

## ptrace 注入面（识别）

```c
// 典型 linux 进程注入序列：
ptrace(PTRACE_ATTACH, pid, 0, 0);
waitpid(pid, &st, 0);
ptrace(PTRACE_GETREGS, pid, 0, &regs);
// 在远程进程 mmap 一段可执行内存 → 写入 shellcode → 改 RIP → 单步
ptrace(PTRACE_POKEDATA, pid, addr, val);
ptrace(PTRACE_SETREGS, pid, 0, &regs);
ptrace(PTRACE_CONT, pid, 0, 0);

// 无 ptrace 路径（CAP_SYS_PTRACE / process_vm_writev）：
process_vm_writev(pid, local_iov, 1, remote_iov, 1, 0);
```

防注入开关：

```bash
sysctl kernel.yama.ptrace_scope            # 0 任意 / 1 仅父进程 / 2 仅 CAP_SYS_PTRACE / 3 完全禁
sysctl kernel.dmesg_restrict
sysctl kernel.kptr_restrict
prctl(PR_SET_DUMPABLE, 0)                  # 进程自己关闭 ptrace 跟踪
```

`PR_SET_NO_NEW_PRIVS` + seccomp 是常见自我隔离。

## gdb 工作流

```bash
# 启动
gdb --args ./prog -opt val
gdb -p $(pgrep prog)                                          # attach

# 推荐插件三选一
# pwndbg: github.com/pwndbg/pwndbg
# gef:    github.com/hugsy/gef
# peda:   github.com/longld/peda

# 常用命令
starti                                                       # 停在第一条用户态指令
catch syscall openat
catch load                                                   # dlopen 时停
b *0x401050
b main if argc > 2
commands
  silent
  bt 5
  printf "rax=%p rdi=%p rsi=%s\n", $rax, $rdi, (char*)$rsi
  c
end

# 内存查看
x/64xb $rsp
vmmap                                                        # pwndbg
context                                                      # pwndbg
heap chunks                                                  # pwndbg
checksec
print *(struct mystruct*)0x602010
```

非交互 batch：

```bash
gdb -batch -ex 'starti' -ex 'catch syscall' -ex 'continue' \
    -ex 'bt 10' -ex 'info registers' --args ./prog
```

## 持久化面识别（这是看，不是搭）

| 位置 | 路径 / 单元 |
| --- | --- |
| **systemd user/system** | `/etc/systemd/system/*.service`、`/lib/systemd/system/*.service`、`~/.config/systemd/user/*.service`、`systemctl list-unit-files`、`systemd-analyze critical-chain` |
| **systemd timer** | `*.timer` 单元，相对 cron 现代化 |
| **cron** | `/etc/cron.{d,daily,hourly,weekly,monthly}/`、`/etc/crontab`、`crontab -lu <user>`、`/var/spool/cron/crontabs/` |
| **at / batch** | `atq`，`/var/spool/cron/atjobs/`、`/var/spool/at/` |
| **init 老体系** | `/etc/init.d/`、`/etc/rc?.d/` |
| **profile / shell** | `~/.bashrc /.bash_profile /.profile /.zshrc`、`/etc/profile.d/*` |
| **xdg autostart（GUI）** | `/etc/xdg/autostart/*.desktop`、`~/.config/autostart/*.desktop` |
| **GNOME / KDE** | `gnome-shell --extensions-list`、`~/.config/plasma-workspace/env/`、`~/.config/plasma-workspace/shutdown/` |
| **udev rule** | `/etc/udev/rules.d/`、`/lib/udev/rules.d/` |
| **PAM** | `/etc/pam.d/`、`/lib/security/`（pam_module 注入） |
| **NSS / glibc** | `/etc/nsswitch.conf`、注入自定义 `libnss_*.so.2` |
| **dyn linker 全局** | `/etc/ld.so.preload`（极敏感、已知 rootkit 经典手法） |
| **inetd / xinetd / socket activation** | `/etc/inetd.conf`、`/etc/xinetd.d/`、systemd `*.socket` |
| **logrotate / postrotate** | `/etc/logrotate.d/`，可被串入命令 |
| **APT/DPKG hooks** | `/etc/apt/apt.conf.d/`、`/etc/dpkg/dpkg.cfg.d/` |
| **MOTD** | `/etc/update-motd.d/` 是脚本 |
| **kernel module autoload** | `/etc/modules-load.d/`、`/etc/modprobe.d/` |
| **eBPF 持久化** | `bpftool prog list`、`bpftool map list`、自动加载脚本 |

## 隔离面识别

```bash
# capabilities
cat /proc/$PID/status | grep Cap
capsh --print                                              # decode bitmask
getcap /usr/bin/ping

# seccomp
cat /proc/$PID/status | grep Seccomp                       # 0 disabled / 1 strict / 2 filter
seccomp-tools dump ./prog                                  # ruby gem，反序列化 BPF 规则
strace -e seccomp ./prog 2>&1 | head

# AppArmor
aa-status
cat /etc/apparmor.d/usr.bin.prog
ls /sys/kernel/security/apparmor/profiles

# SELinux
sestatus
ls -Z /usr/bin/prog
audit2allow -a                                              # 看拒绝日志

# namespaces
lsns -p $PID
unshare --user --pid --mount-proc bash                      # 复现用户命名空间

# cgroups (v2)
cat /proc/$PID/cgroup
ls /sys/fs/cgroup/$(cat /proc/$PID/cgroup | cut -d: -f3-)/
```

## 容器/cgroup 视角

```bash
# 是否在容器内
cat /proc/1/cgroup
[ -f /.dockerenv ] && echo "docker"
mount | grep overlay
# Kubernetes 通常 /etc/resolv.conf 含 cluster.local，env 有 KUBERNETES_SERVICE_HOST

# 镜像层
docker inspect <ctr> | jq '.[0].GraphDriver'
crane manifest --platform linux/amd64 image:tag           # OCI manifest
syft image:tag                                             # SBOM
```

镜像取证 / 解包细节走 `containerrev`。

## 内存观察

```bash
# coredump
ulimit -c unlimited; sysctl kernel.core_pattern
gcore -o ./core $PID
gdb ./prog ./core.$PID -ex 'bt full' -ex 'info threads' -ex q

# 拷整段内存（root）
dd if=/proc/$PID/mem bs=1 skip=$((0x7f0000000000)) count=$((0x1000)) of=region.bin 2>/dev/null
# 或更高效
cat /proc/$PID/maps | awk '$2~/r/' | while read l h _; do
  r=${l#*-}; b=${l%-*}
  ...
done

# 全机内存
sudo apt install linux-tools-common; perf-record ...
sudo modprobe lime "path=/tmp/mem.lime format=lime"
volatility3 -f /tmp/mem.lime linux.pslist linux.bash linux.malfind
```

## 反调试 / 反 ptrace 检测面

```c
// 自检是否被 ptrace
ptrace(PTRACE_TRACEME, 0, 0, 0);   // 已被 trace 时返回 -1

// /proc/self/status 里 TracerPid != 0
// /proc/self/stat 字段 4 = ppid，状态 't' = tracing stop
// 检查 LD_PRELOAD env
// 检查 /proc/self/maps 有没有自家黑名单 .so（frida-agent / linjector）
// timing trap: rdtsc 前后差 + 一段无副作用代码
// signal 干扰: signal(SIGTRAP, handler) 然后故意 int3，预期 handler 命中
// ldd-style: dlsym(RTLD_DEFAULT, "ptrace") 自检 hook
```

测试时通过 LD_PRELOAD 一个 stub `ptrace` 总是返回 0，或者 `prctl(PR_SET_DUMPABLE,1)` + `echo 0 > /proc/sys/kernel/yama/ptrace_scope` 后再 attach。

## glibc / musl / heap 速查

```text
# malloc 内核
glibc:    ptmalloc2（main_arena + per-thread arena + tcache 64 bins + fastbins + smallbins + largebins + unsortedbin）
musl:     mallocng（chunk 元数据外置，硬化更强）
jemalloc: TCMalloc-style，size class + bins
mimalloc: 微软的，类似 jemalloc

# tcache 利用要点（堆题）
glibc 2.27+ 引入 tcache，每 size class 7 chunk 不做 double-free 校验（2.28- 才加）
glibc 2.32+ tcache key 校验 + safe-linking（pointer xor randomization）
glibc 2.34+ __libc_init_first 移到内联，hijack target 改变

# 关键全局
__malloc_hook  __free_hook  __realloc_hook   # glibc 2.34 起被废弃
_dl_runtime_resolve / _dl_fixup               # PLT lazy 触发
__libc_argv  __environ  __progname            # 信息泄露常用
stdin->_IO_buf_base                           # FILE 结构利用面
```

## 实战入口

- **pwn.college / pwn.college Linux Userspace** — 系统化训练：syscall、libc、ROP、kernel。
- **HackTheBox / VulnHub Linux machine** — 实操真实场景。
- **Linux Kernel CTF / kernelCTF / kCTF** — 内核题。
- **OverTheWire bandit / leviathan / krypton** — Linux shell 训练。
- **Nightmare Heap / how2heap (shellphish)** — glibc 堆训练，每个 commit 跟一个 glibc 版本。
- **MalwareBazaar Linux 标签** — Linux 恶意样本，VM 内做。

## 自检（拿到 Linux 二进制 30 分钟内回答）

1. 静态/动态？libc 依赖（glibc/musl/uclibc）？版本？
2. checksec：PIE / RELRO (full/partial) / Canary / NX / FORTIFY / RPATH？
3. setuid / setgid / capabilities？AppArmor / SELinux profile？seccomp？
4. 默认连接哪些 syscall 簇（execve / openat / connect / mmap PROT_EXEC）？
5. 启动后会写哪些路径？读哪些 env？fork 链是什么？
6. 持久化面：systemd unit / cron / `~/.bashrc` / `ld.so.preload` 有没有改？
7. 容器内还是宿主？namespace / cgroup 边界在哪？

## 相邻技能

- `binrev` — ELF 头/段/函数/调用图本身。
- `asmrev` — x86_64 / aarch64 / riscv 指令级。
- `abirev` — SysV AMD64 / AAPCS / ARM EABI、C++ vtable / RTTI / 异常表。
- `crashrev` / `memrev` / `debugrev` — coredump、内存证据、动态调试。
- `containerrev` — OCI 镜像 / overlayfs / 镜像层差异。
- `irrev` — Linux kernel CFG / eBPF prog 反汇编。
- `fwrev` — 嵌入式裁剪后的 BusyBox/Buildroot ELF。
- `malrev` — Linux 恶意样本（rootkit / cryptominer / Mirai 系）。
- `cryptrev` — OpenSSL / libsodium / GnuTLS 调用流识别。
- `protrev` — Linux 上 unix domain socket / netlink 协议。