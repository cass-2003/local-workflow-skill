---
name: assembly-reverse-engineering
description: 汇编与指令集逆向。x86/x86_64/AArch64/ARM/Thumb/RISC-V/MIPS/PowerPC 指令语义、寻址模式、寄存器约定、栈帧与序言/收尾、SIMD、跳表 vs 间接调用、原子/内存模型、PAC/BTI/CFI 硬件加固。配合 binrev / abirev / irrev 用。
---

# 汇编与指令集逆向

## 适用场景

- 在 binrev / 调试器里看到一段反汇编，要回答："这段在做什么？哪些寄存器是参数？哪些是局部？哪是循环边界？是 switch 还是 vtable？"
- 跨架构识别：拿到 ARM64 / RISC-V / MIPS 二进制，对应 x86 习惯找位置。
- 编译器风格识别：MSVC / GCC / Clang / Rustc / Swift 的序言、对齐、padding 模式不同。
- 手写汇编 patch / shellcode 调试。

## 不适用

- 函数级 / 调用图 / 反编译伪代码 → `binrev`。
- 调用约定 / vtable / 异常表 → `abirev`。
- IR 反编译 / 数据流 → `irrev`。
- 自实现 VM 的 opcode → `vmrev`。

## x86_64

### 寄存器（System V / Microsoft 一致）

```text
通用 64-bit:  rax rbx rcx rdx rsi rdi rbp rsp r8..r15
32-bit 视图:  eax ebx ecx edx esi edi ebp esp r8d..r15d
16-bit:       ax bx cx dx si di bp sp r8w..r15w
8-bit:        al ah bl bh cl ch dl dh sil dil bpl spl r8b..r15b
段寄存器:     cs ds es fs gs ss   (gs/fs 在用户态用作 TLS / KUSER_SHARED_DATA / TEB/PEB)
SIMD:         xmm0..xmm15(SSE) ymm0..15(AVX) zmm0..31(AVX-512)
标志:         rflags  ZF SF OF CF PF AF
RIP:          指令指针；rip-relative 寻址 [rip+disp32]
```

### 指令片段速查

```nasm
; 函数序言 (System V)
push    rbp
mov     rbp, rsp
sub     rsp, 0x40            ; 0x40 字节 locals
mov     [rbp-8], rdi         ; arg1 入栈

; 函数收尾
leave                         ; mov rsp,rbp; pop rbp
ret

; 字符串/数组循环 (strlen 风格)
xor     eax, eax
.loop:
    cmp     byte [rdi+rax], 0
    je      .end
    inc     rax
    jmp     .loop

; switch 跳表 (MSVC/GCC 都常生成)
cmp     eax, 5
ja      .default
lea     rcx, [rip+jumptable]
movsxd  rax, dword [rcx+rax*4]
add     rax, rcx
jmp     rax

; vtable / 函数指针调用
mov     rax, [rdi]            ; rdi = obj; rax = obj->vtable
call    qword [rax+0x20]      ; vtable[4] (每项 8 字节)

; PIC 全局变量访问 (PIE/-fPIC)
mov     rax, [rip+global_var] ; rip-relative

; SIMD 16 字节 memcpy
movdqu  xmm0, [rsi]
movdqu  [rdi], xmm0

; 原子比较交换 (atomic CAS)
lock cmpxchg [rdi], rcx       ; if [rdi]==rax, [rdi]=rcx; else rax=[rdi]; lock 前缀总线锁

; 内存屏障
mfence                         ; full barrier
lfence                         ; load barrier (Spectre v1 缓解)
sfence                         ; store barrier
```

### 寻址模式

```text
[disp32]                          绝对（PE 32 位 / 非 PIE）
[base]                            寄存器
[base + disp]                     偏移
[base + index]                    基址 + 索引
[base + index*scale + disp]       完整 SIB（scale = 1/2/4/8）
[rip + disp32]                    RIP-relative（x86_64 PIE 默认）
fs:[disp]   gs:[disp]             段寄存器（TEB/TLS）
```

### 反汇编风格

```bash
# Intel 风（推荐）
objdump -d -M intel orig.bin
gdb> set disassembly-flavor intel
# AT&T 风（GCC 默认）：操作数顺序反过来，寄存器加 % 前缀
```

## AArch64 (ARM64)

```text
寄存器: x0..x30 (64-bit) / w0..w30 (32-bit)
        x29 = fp (frame pointer)
        x30 = lr (link register, 函数返回地址)
        sp 是单独的, 不在 x0-x30 内
        xzr / wzr = 0 寄存器
SIMD/FP: v0..v31 (NEON / SVE)
PSTATE:  N Z C V (类似 flags)
```

### 指令片段

```text
// 函数序言（AAPCS64）
stp     x29, x30, [sp, #-0x20]!     // 同时压入 fp + lr
mov     x29, sp
sub     sp, sp, #0x20

// 函数收尾
ldp     x29, x30, [sp], #0x20
ret

// Apple Silicon 带 PAC（ARM64e）
pacibsp                              // 用 sp 上下文给 lr 签名
stp     x29, x30, [sp, #-0x10]!
mov     x29, sp
...
ldp     x29, x30, [sp], #0x10
retab                                // 验证签名后 ret

// 加载常量（RISC 风：常量必须分两步）
adrp    x0, _str@PAGE                // 取 PC-relative 4KB 页基址
add     x0, x0, _str@PAGEOFF         // 加上页内偏移
ldr     x1, [x0]                     // 解引用

// 32 位 immediate 装入
mov     w0, #0x1234
movk    w0, #0xabcd, lsl #16

// 字符串比较（无 strcmp，自己写）
loop:
    ldrb    w8, [x0], #1
    ldrb    w9, [x1], #1
    cmp     w8, w9
    b.ne    diff
    cbnz    w8, loop

// switch 跳表
adrp    x10, jt@PAGE
add     x10, x10, jt@PAGEOFF
ldr     w11, [x10, w0, uxtw #2]      // 取 32-bit 偏移
add     x10, x10, w11, sxtw           // 32 位有符号扩展加回
br      x10                            // PAC 时用 braa
```

### 条件 + 计算合并指令

```text
csel    x0, x1, x2, eq              // x0 = (Z) ? x1 : x2
csinc   x0, x1, x2, ne              // x0 = (!Z) ? x1 : x2+1
cinc    x0, x1, eq                  // x0 = (Z) ? x1+1 : x1
ccmp    x0, x1, #0, eq              // 条件比较
fmla    v0.4s, v1.4s, v2.4s         // SIMD: v0 += v1 * v2
```

### Thumb-2 (ARM 32-bit)

```text
push    {r4-r7, lr}                 // 序言
add     r7, sp, #0x10
sub     sp, sp, #0x40
...
add     sp, sp, #0x40
pop     {r4-r7, pc}                 // pop pc = ret

// 立即数装入（PC-relative）
ldr     r0, [pc, #0x14]             // 编译器把常量放在函数末尾
```

T 位（CPSR.T）= 1 时是 Thumb，CPSR.T = 0 是 ARM；BX/BLX 的目标地址低位 = T 位（指令必然 2/4 字节对齐）。

## RISC-V (RV64GC)

```text
寄存器: x0=zero, x1=ra(返回), x2=sp, x3=gp, x4=tp,
        x5-x7=t0-t2, x8=fp/s0, x9=s1, x10-x11=a0-a1(参数+返回),
        x12-x17=a2-a7(参数), x18-x27=s2-s11, x28-x31=t3-t6
ABI 名: zero ra sp gp tp t0..t2 s0/fp s1 a0..a7 s2..s11 t3..t6

指令长度: 4 字节（GC 扩展含 2 字节 C 压缩）
```

```asm
# 函数序言
addi    sp, sp, -32
sd      ra, 24(sp)
sd      s0, 16(sp)
addi    s0, sp, 32
...
ld      ra, 24(sp)
ld      s0, 16(sp)
addi    sp, sp, 32
ret                          # 别名 jalr x0, ra, 0

# 立即装入
li      a0, 0x1234           # 伪指令; 展开成 lui + addiw

# 比较 + 分支
beq    a0, a1, .eq           # ==
bnez   a0, .nz               # != 0
blt    a0, a1, .lt
bgeu   a0, a1, .geu          # 无符号 >=
```

## MIPS / PowerPC（嵌入式 / 旧路由器固件常见）

MIPS 关键：

```text
$0=zero $sp=29 $gp=28 $fp=30 $ra=31
$a0-$a3 (4-7) 参数；$v0-$v1 (2-3) 返回
延迟槽 (delay slot)：jr/j/branch 后面的一条总是先执行
gp-relative 数据访问 ($gp 指向 .got)
```

PowerPC 关键：

```text
r0=有时 0 / 有时变量；r1=sp；r2=TOC base (BE) / thread (LE)
LR=Link Register; CTR=Count Register
mtctr / bctr  = 间接跳转
crN  共 8 个 4-bit 条件域
```

固件逆向遇到这两个的概率不低，留意大端 / 小端：

```bash
file orig.bin
# 输出含 "MIPS, MIPS32, version 1, MSB" → 大端 MIPS
# "PowerPC or cisco 4500, version 1 (SYSV), statically linked, ..." → PPC
```

## 跳表 vs 间接调用 vs vtable 分辨

```text
1) 跳表 (switch) — 通常 lea/adrp 取本地常量地址 + 索引读 + 加回 + jmp/br
   特点: 表项是局部静态数据 (.rodata)，索引 0..N 连续

2) 间接调用 (函数指针) — 取一个全局/局部变量的值再 call
   call qword [rip+func_ptr]
   blr  x16
   特点: 目标地址来源是变量，可被外部修改

3) vtable 调用 — 先解引用对象第一个字段（vtable 指针），再读偏移
   mov rax, [rdi]              ; obj->vptr
   call qword [rax + 0x20]     ; vtable[4]
   特点: 双重解引用；偏移是 vtable 槽号 × ptr_size
```

## 编译器指纹小抄

```text
GCC:
- 偏好 leave/ret 收尾
- -O2 默认大量 cmov、SIMD
- 字符串放 .rodata.str1.x
- frame pointer omit by default (-fomit-frame-pointer)

Clang:
- 类似 GCC，但更多 movabs；vector 化更激进
- LLVM 名: __cxx_global_var_init / __clang_call_terminate
- ASan 痕: __asan_init / __asan_shadow / .asan_globals

MSVC:
- 偏好 /GS (security cookie): mov rax, [rip+__security_cookie]; xor rax, rsp
- catch 用 __CxxFrameHandler / __C_specific_handler
- 异常: SEH (.pdata / .xdata)
- TLS callback 直接用
- /Os 大量 push/pop 减小 size

Rust:
- core::panicking::panic_bounds_check / panic_fmt
- _$LT$ ... _$GT$ name mangling (Itanium 兼容形式)
- 大量 inline 拒绝 + 单态化产生海量函数
- panic_handler 入口
- alloc::raw_vec / Vec 痕

Swift:
- _$s 前缀，复杂 mangling，用 swift-demangle 还原
- ObjC bridge: $sSo... 前缀
- _swift_release / _swift_retain
- swiftshims / Array._endMutation 等

Go:
- runtime.morestack_noctxt 在每个函数序言（栈检查）
- mod 为 main 的二进制保留全部符号 (无 strip 默认)
- runtime.gopanic / runtime.goexit 标记
- TLS via fs:0xfffffffffffffff8

Nim:
- nimZeroMem / nimGCunref 痕
```

## SIMD 速查（识别加密 / 编解码）

```text
SSE/SSE2 (xmm)   16B
AVX/AVX2 (ymm)   32B
AVX-512 (zmm)    64B
ARM NEON (v0..v31) 16B
ARM SVE          可变长

常见模式:
- 块加密轮: pshufb / aesenc / aesenclast / aesdec / aesdeclast (AES-NI)
- ChaCha20: vpaddd + vpxor + vpslld/vpsrld 旋转
- SHA: sha256rnds2 / sha256msg1 / sha256msg2
- memcpy 大块: rep movsb (已 ERMS 化) 或 vmovdqu/ymm
- strlen: pcmpistri / pcmpeqb + pmovmskb
- crc32: crc32 r/m
- 矩阵乘 / DSP: vfmadd / vmulps / vfma
```

## 反汇编验证小技巧

```bash
# 单条指令 16 进制 → 汇编（手写 patch 验证）
echo -n '4831c0' | xxd -r -p | objdump -D -m i386:x86-64 -b binary -M intel /dev/stdin
# 输出: xor rax, rax

# capstone 一行
python3 -c '
from capstone import *
md = Cs(CS_ARCH_X86, CS_MODE_64)
for i in md.disasm(b"\x48\x31\xc0\xc3", 0x1000):
    print("%x %s %s" % (i.address, i.mnemonic, i.op_str))
'

# keystone 反向（汇编 → 字节码）
python3 -c '
from keystone import *
ks = Ks(KS_ARCH_X86, KS_MODE_64)
b, _ = ks.asm(b"xor rax, rax; ret")
print(bytes(b).hex())
'
```

## 实战入口

- **AssemblyLanguageTutorial / x86 cheat sheet (Sandpile.org)** — x86 完整指令集与微架构。
- **Intel SDM / AMD APM** — 官方权威。
- **ARM ARM (ARM Architecture Reference Manual)** — AArch64 指令完整定义。
- **RISC-V Unprivileged ISA Spec** — RV64 指令。
- **CrackMes.one** — 各架构 crackme，纯指令训练。
- **pwn.college Reverse Engineering / Assembly** — 系统化课程。
- **Compiler Explorer (godbolt.org)** — 写 C 看每个编译器输出，反向训练利器。

## 自检（拿到一段反汇编 5 分钟内回答）

1. 哪个架构？哪个 ABI？哪个端序？哪个编译器风格？
2. 这是函数序言还是收尾还是中间？栈帧大小？
3. 哪些寄存器是参数？哪些是返回？
4. 是循环、跳表、vtable 还是 函数指针调用？
5. 是否有 PAC/BTI/CFG 等加固痕？
6. 用 capstone / objdump 重新反汇编，结果与原一致？

## 相邻技能

- `binrev` — ELF/PE/Mach-O 结构 + 反编译伪 C。
- `abirev` — calling convention、name mangling、vtable / RTTI / EH。
- `irrev` — 反编译器中间表示与数据流（LLVM IR / Ghidra P-Code / VEX / ESIL）。
- `vmrev` — 自定义 VM dispatch + handler。
- `linuxrev` / `winrev` / `macrev` — 各平台 syscall stub 与系统结构寻址。
- `crashrev` / `memrev` / `debugrev` — 在调试器里读寄存器/栈/内存。
- `cryptrev` — SIMD 加密内核识别。
- `fwrev` — MIPS / PowerPC / ARM 嵌入式固件常用架构。