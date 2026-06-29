---
name: binary-reverse-engineering
description: 通用二进制逆向。处理 Linux ELF / Windows PE / macOS Mach-O / 共享库 / 静态库 / object file 的结构画像、函数级深挖、调用约定还原、漏洞入口定位与 patch 验证；不展开汇编/平台运行生态/壳/恶意行为/密码细节，那些有更精确子技能。
---

# 通用二进制逆向

## 适用场景

- 拿到 ELF / PE / Mach-O / .so / .dll / .dylib / .a / .o，要做函数级反编译、调用图还原、字符串/常量交叉引用、漏洞入口定位、patch 测试。
- 已经分流自 `rev`，需要在二进制层面回答："这个函数做什么？谁调谁？输入边界在哪？patch 在哪能改最少代码改变行为？"
- 安全测试中需要从二进制中定位认证 / 解密 / 校验 / 限速 / 反调试函数，给 fuzzer 或 PoC 找入口。

## 不适用

- 指令级寄存器轮转、栈帧细节 → `asmrev`
- C++ vtable / RTTI / 异常表 / FFI ABI → `abirev`
- 平台 syscall / 加载器 / 注入面 → `linuxrev` / `winrev` / `macrev`
- 加壳样本未脱壳前的入口分析 → 先 `packrev`
- 自定义 VM / dispatch → `vmrev`

## 文件结构速识

### ELF (System V)

```bash
readelf -h orig.elf       # ELF header: 类、字节序、ABI、e_entry、e_phoff、e_shoff
readelf -l orig.elf       # Program header: 装载段、PHDR、INTERP、DYNAMIC、NOTE、GNU_STACK
readelf -S orig.elf       # Section header: .text/.rodata/.data/.bss/.plt/.got/.got.plt/.init_array/.fini_array
readelf -d orig.elf       # 动态段: NEEDED、SONAME、INIT、FINI、JMPREL、PLTGOT、RUNPATH
readelf -s orig.elf       # 符号表: STT_FUNC / STT_OBJECT、STB_GLOBAL/LOCAL/WEAK
readelf -r orig.elf       # 重定位: R_X86_64_JUMP_SLOT (PLT)、R_X86_64_GLOB_DAT、R_X86_64_RELATIVE
readelf -p .comment orig.elf   # 编译器/版本指纹
checksec --file=orig.elf       # PIE / RELRO / Canary / NX / FORTIFY
```

入口判定：动态可执行从 `_start` → `__libc_start_main` → `main`；动态库无 main，看 `.init_array` / `.fini_array` / `DT_INIT`。

### PE (Windows)

```bash
rabin2 -I -i -E -z -H orig.exe          # 头/导入/导出/段/字符串/header dump
pe-parse orig.exe
sigcheck -h orig.exe                    # 数字签名 + Authenticode 哈希
dumpbin /headers /imports /exports /relocations orig.exe   # MSVC 工具
peid orig.exe                           # 编译器/壳指纹
floss orig.exe                          # 解码混淆字符串
```

入口：`AddressOfEntryPoint`（OptionalHeader）→ `mainCRTStartup` → `main`；DLL 看 `DllMain` / 导出函数表 / `EXPORT` 节。
关键节：`.text` `.rdata` `.data` `.idata` (IAT) `.edata` `.rsrc` `.reloc` `.tls`（TLS callback 在执行 main 前跑）。

### Mach-O

```bash
otool -hl orig                          # mach_header + load commands
otool -L orig                           # 依赖 dylib + LC_LOAD_DYLIB
otool -tV -arch x86_64 orig             # 反汇编
nm -m orig                              # 符号 + 来源（external/undefined/__TEXT/__DATA）
codesign -dvvv orig                     # 签名细节、entitlements
jtool2 -d objc orig                     # ObjC 类/方法表
plutil -convert xml1 -o - Info.plist
```

入口：LC_MAIN → `_main`；老格式 LC_UNIXTHREAD。Universal binary：`lipo -info`、`lipo -thin x86_64 fat.bin -output thin.bin`。

## 反编译批量入口

```bash
# Ghidra Headless（CI 友好）
analyzeHeadless ./projdir proj1 -import orig.bin \
    -postScript ListAllFunctions.java \
    -postScript ExportPseudoC.java \
    -scriptPath ./scripts

# radare2
r2 -A -q -c 'aaa; afl; pdf @main; iz~http; axt sym.imp.strcmp' orig.bin

# IDA Pro batch
idat64 -A -B -Sscript.idc orig.bin                    # 生成 .i64 + .asm
idat64 -A -Sexport_pseudo.py orig.bin                 # 调用 IDAPython 导出 pseudo C

# Binary Ninja headless
binaryninja --headless -p analyze.py orig.bin
```

### IDAPython 例：导出所有函数 pseudo-C

```python
# export_pseudo.py（IDA Pro，运行: ida -A -Sexport_pseudo.py target.bin）
import idaapi, idautils, idc, ida_hexrays
ida_hexrays.init_hexrays_plugin()
out = open(idc.ARGV[1] if len(idc.ARGV) > 1 else "pseudo.c", "w", encoding="utf-8")
for ea in idautils.Functions():
    name = idc.get_func_name(ea)
    cfunc = ida_hexrays.decompile(ea)
    if cfunc:
        out.write(f"// {hex(ea)} {name}\n{str(cfunc)}\n\n")
out.close()
idc.qexit(0)
```

### Ghidra script 例：导出调用图

```java
// ExportCallGraph.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
public class ExportCallGraph extends GhidraScript {
    public void run() throws Exception {
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            for (Function callee : f.getCalledFunctions(monitor)) {
                println(f.getName() + " -> " + callee.getName());
            }
        }
    }
}
```

## 函数级工作流

### 1. 锁定关键函数

按字符串 / API / 常量交叉引用倒推：

```bash
# 找到字符串 "auth_failed" 的引用者
strings -t x orig.bin | grep -i auth_failed
# 0x8e2a4 auth_failed: invalid token
r2 -q -c 'iz~auth_failed; axt @ 0x8e2a4' orig.bin

# 找到所有调用 strcmp 的地方
r2 -q -c 'aaa; axt sym.imp.strcmp' orig.bin
objdump -d orig.bin | grep -B2 'call.*strcmp@plt'

# 找特定常量（魔法数）的引用者
r2 -q -c '/x deadbeef; axt @ <addr>' orig.bin
```

### 2. 函数边界 + CFG

```bash
# r2: 分析 + 函数列表 + 反汇编 + CFG
r2 -A -c 'afl ~auth' orig.bin
r2 -A -c 'agf @ sym.check_password' orig.bin > cfg.dot
dot -Tpng cfg.dot -o cfg.png

# 反汇编单函数
objdump -d --disassemble=check_password orig.bin
gdb -batch -ex 'disas check_password' orig.bin
```

### 3. 调用约定与参数

x86_64 SysV：rdi rsi rdx rcx r8 r9 → stack；返回 rax。
x86_64 MS：rcx rdx r8 r9 → stack；shadow space 32 字节；返回 rax。
ARM64 AAPCS：x0..x7 → stack；返回 x0；x29=fp、x30=lr。

```python
# IDAPython 修正函数签名（发现传 5 个参数被识别成 3 个）
import ida_typeinf, idc
ea = idc.get_name_ea_simple("check_password")
tinfo = ida_typeinf.tinfo_t()
ida_typeinf.parse_decl(tinfo, None, "int check_password(const char *user, const char *pw, int salt, int *out, int flags)", 0)
ida_typeinf.apply_tinfo(ea, tinfo, ida_typeinf.TINFO_DEFINITE)
```

### 4. 数据交叉引用

PLT/GOT 调用本质：`call sym@plt` → PLT stub → 第一次走 `_dl_runtime_resolve` 填 GOT，之后直接跳 GOT。
全局变量：`mov rax, [rip+0x???]` 形式（PIE）或绝对地址（非 PIE）。
找写入：`r2 -c 'axw @ <addr>'`，`gdb watch *0xdeadbeef`。

### 5. 关键漏洞入口模式

```text
# 栈缓冲溢出候选
   strcpy / strcat / sprintf / gets / scanf("%s") / read 到栈数组

# 整数溢出 -> 堆
   malloc(size * count); memcpy(dst, src, size * count);   # size*count overflow
   alloca(user_size);

# Format string
   printf(user_input); fprintf(fp, user_input); syslog(LOG_INFO, user_input);

# UAF / Double-free
   free(p); ... ; *p = ...;   # 仍持引用
   free(p); free(p);

# 命令注入
   system(buf); popen(buf); execl("/bin/sh", "sh", "-c", buf);

# 路径穿越
   open(buf); fopen(buf); CreateFileW(buf);  # 未做 ../ 过滤
```

`grep` 这些原型在导入表的命中是粗筛，必须再人工跟一段反编译确认输入可达。

### 6. patch 测试

```bash
# 单字节 patch（NOP 一个跳转）
printf '\x90\x90' | dd of=work/orig.bin bs=1 seek=$((0x1234)) conv=notrunc

# r2 写
r2 -w -q -c 'wx 9090 @ 0x1234' work/orig.bin

# 重算 PE checksum（NT_HEADER OptionalHeader.CheckSum）
pe-parse --update-checksum work/orig.bin

# 重签 Mach-O（自签名足够给 Gatekeeper 跑测试）
codesign --force --sign - work/orig.bin

# ELF 删除 .note.gnu.build-id 让两份对比时不被指纹差异干扰
objcopy --remove-section=.note.gnu.build-id work/orig.bin
```

## 调用图 / 数据流自动化

### angr 找路径

```python
# reach_sink.py：从 main 到目标地址的可达路径
import angr, claripy
proj = angr.Project("orig.bin", auto_load_libs=False)
state = proj.factory.entry_state()
simgr = proj.factory.simulation_manager(state)
TARGET = 0x401234
simgr.explore(find=TARGET)
if simgr.found:
    print(simgr.found[0].posix.dumps(0))   # 触发输入
```

### qiling 在沙箱里跑函数

```python
# qiling_call.py
from qiling import Qiling
ql = Qiling(["./orig.bin"], rootfs="./rootfs", verbose=4)
ql.os.exec_arbitrary(0x401050, 0x401120)   # 任意从 0x401050 跑到 0x401120
```

### 符号执行 + 约束

```python
# 解 license：让 magic_check 函数返回 1
import angr, claripy
proj = angr.Project("orig.bin")
key = claripy.BVS("key", 16*8)
state = proj.factory.call_state(0x401050, key, len(key)//8)
simgr = proj.factory.simulation_manager(state)
simgr.explore(find=lambda s: s.regs.rax.concrete and s.solver.eval(s.regs.rax) == 1)
print(simgr.found[0].solver.eval(key, cast_to=bytes))
```

## 跨平台对照表

| 概念 | ELF | PE | Mach-O |
| --- | --- | --- | --- |
| 头 | ELF header (Ehdr) | DOS+NT (IMAGE_NT_HEADERS) | mach_header(_64) |
| 段/节 | Program/Section header | Sections (.text/.rdata/.idata) | LC_SEGMENT + sections |
| 入口 | e_entry | OptionalHeader.AddressOfEntryPoint | LC_MAIN entryoff |
| 动态符号 | .dynsym + .dynstr + DT_NEEDED | IAT + ILT + Import Directory | LC_DYLD_INFO + LC_LOAD_DYLIB |
| 导入跳板 | .plt / .plt.got | IAT (jmp [iat_addr]) | __TEXT.__stubs / __DATA.__la_symbol_ptr |
| 全局变量 | .data / .bss + GOT (RIP-relative) | .data + RVA + base reloc | __DATA.__data |
| TLS | .tdata + DT_TLS + GS/FS | .tls + TLS callback (在 main 前) | __DATA.__thread_data |
| 重定位 | .rela.dyn / .rela.plt | .reloc | LC_DYLD_INFO bind/lazy_bind |
| 元数据指令 | .init_array / .fini_array / .ctors | TLS callback / .CRT$XCU | LC_FUNCTION_STARTS / module_init_func |
| 调试 | DWARF (.debug_*) | PDB (外置) | dSYM bundle (DWARF) |
| 校验 | build-id | OptionalHeader.CheckSum | LC_CODE_SIGNATURE |

## 反汇编输出阅读小抄

### 函数序言

```text
# x86_64 SysV
push rbp
mov rbp, rsp
sub rsp, 0x40            ; 0x40 字节本地变量
mov [rbp-8], rdi         ; arg1 入栈

# x86_64 MS-x64
mov [rsp+0x10], rdx      ; arg2 home space
sub rsp, 0x28            ; shadow space 32 + locals
```

### 字符串/数组循环

```text
# strlen 风格
movzx eax, byte ptr [rdi]
test al, al
je   .end
add  rdi, 1
jmp  .loop
```

### 间接调用 = vtable 或函数指针

```text
mov rax, [rdi]           ; obj->vtable
call qword ptr [rax+0x20]  ; vtable[4]
```

vtable 的具体定位与 RTTI/异常表展开：交给 `abirev`。

### switch / 跳表

```text
cmp eax, 5
ja  .default
lea rcx, [rip+jumptable]
movsxd rax, dword ptr [rcx+rax*4]
add rax, rcx
jmp rax
```

跳表起始地址是 `lea rcx, [rip+...]`，表项是相对偏移。

## 实战入口

- crackmes.one — 全语言 crackme 训练库。
- Flare-On 历年 — PE/.NET/JS 综合赛。
- ROPEmporium — 6 道经典 ROP 关卡。
- pwn.college Reverse Engineering 模块 — 系统化课程 + 题库。
- 看雪「逆向工程核心原理」配套样本。
- LiveOverflow / OALabs / RE 文章 — 长视频带做题。

## 自检（拿到二进制 30 分钟内回答）

1. ELF/PE/Mach-O？架构、位数？编译器与版本指纹？
2. 是否 PIE / 是否 stripped / 是否签名 / 是否 fortify / 是否 RELRO？
3. 入口点地址？main 在哪？init/fini/TLS callback 有几个？
4. 关键导入：是否有 strcmp/strcpy/system/exec/CryptoAPI/network API？
5. 字符串里有没有 URL、路径、错误信息、版本号、内嵌 base64/hex blob？
6. 选一个可疑函数，画出 CFG 和参数类型；写一段触发输入。

## 相邻技能

- `asmrev` — 单条指令、寄存器、栈帧、calling convention 细节。
- `abirev` — C++ vtable/RTTI/异常表、FFI、name mangling。
- `linuxrev` / `winrev` / `macrev` — 平台 loader、syscall、注入面。
- `irrev` — 中间表示（LLVM IR、Ghidra P-Code、VEX、ESIL）数据流分析。
- `crashrev` / `memrev` / `debugrev` — 动态调试、内存证据、崩溃分析。
- `packrev` — 加壳样本先脱壳再回 binrev。
- `cryptrev` — 当函数实现的是加密算法时，用 cryptrev 识别再回 binrev 看实现。
- `vmrev` — dispatch loop + handler table 模式。
- `fuzzrev` — 拿 binrev 找出的入口给 fuzzer。