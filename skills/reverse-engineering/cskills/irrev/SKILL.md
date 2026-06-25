---
name: ir-dataflow-reverse-engineering
description: IR 与数据流高级静态分析逆向。LLVM IR / Ghidra P-Code / IDA microcode / VEX (Valgrind/angr) / ESIL (radare2) / BAP IL / Triton AST / B2R2 BinIR；SSA/CFG/dominator/数据流/taint/区间分析；用 angr/qiling/manticore/Triton/miasm/KLEE/Souper 做符号执行、约束求解、混淆还原与可达性分析。
---

# IR 与数据流逆向

## 适用场景

- 反编译伪 C 看不懂 / 被混淆撕碎，想退一步用更结构化的 IR 推导。
- 想自动找路径：从 main 到漏洞 sink、从输入到密钥使用点、从配置到执行分支。
- 控制流平坦化、不透明谓词、MBA（混合布尔算术）等混淆，要做去混淆。
- 用约束求解器推一组让程序进入特定状态的输入（CTF crackme / 签名还原）。

## 不适用

- 单条指令的语义和寄存器 → `asmrev`。
- C++ vtable / EH 结构 → `abirev`。
- 自定义 VM dispatch 与 handler → `vmrev`（IR 是分析手段，VM 还原本身在 vmrev）。

## 主流 IR 速览

| IR | 来源 | 形态 | 工具入口 |
| --- | --- | --- | --- |
| **LLVM IR** | clang/lifter（mctoll、retdec） | SSA，三地址，类型化 | `opt`, `llc`, `llvm-dis`, `klee`, `souper` |
| **Ghidra P-Code** | Ghidra 装载器 | 微指令，每条机器指令 1..N 个 P-Code op | Decompiler API / Java / Python (Ghidrathon) |
| **IDA microcode (Hex-Rays)** | Hex-Rays 反编译器 | 多级（MMAT_GENERATED → MMAT_LVARS → ... → MMAT_PRECISE） | hexrays_python / Lighthouse / Tenet |
| **VEX** | Valgrind / angr | RISC 化、SSA、含侧效应（Ijk_*） | angr / pyvex |
| **ESIL** | radare2 | 后缀栈 IR，逐字符 | `aer`、`ae <expr>`、`aeim/aef` |
| **BAP IL (BIL)** | Binary Analysis Platform | 类似 LLVM IR 但更小 | OCaml / Python plugin |
| **Triton AST** | Triton SE 框架 | 抽象语法树 + 符号变量 | Python API |
| **B2R2 BinIR** | KAIST B2R2 | F# / .NET，CFG/dominator 现成 | F# / CLI |
| **REIL / VEX-x86** | Zynamics REIL（已停） | 7 op 极小 IR | BinNavi（已开源）|
| **miasm IR** | miasm | 中间表示 + 表达式简化 | Python |
| **WASM bytecode** | wabt / WAVM | 类型化栈机 | `wasm2wat` |

## LLVM IR 速记

```llvm
; 函数定义
define i32 @add(i32 %a, i32 %b) {
entry:
  %sum = add nsw i32 %a, %b          ; nsw = no signed wrap
  ret i32 %sum
}

; 控制流
define void @loop(i32 %n) {
entry:
  br label %header                   ; 无条件跳
header:
  %i = phi i32 [ 0, %entry ], [ %i.next, %body ]   ; phi 节点 = SSA 入口
  %cmp = icmp slt i32 %i, %n
  br i1 %cmp, label %body, label %exit
body:
  %i.next = add i32 %i, 1
  br label %header
exit:
  ret void
}

; 内存
%ptr = alloca i32, align 4
store i32 42, i32* %ptr
%v = load i32, i32* %ptr

; getelementptr (GEP) — 数组/结构体寻址
%a = getelementptr inbounds i32, i32* %arr, i64 5

; 调用
%r = call i32 @add(i32 1, i32 2)
%t = tail call i32 @foo()           ; 尾调

; 类型
i1 i8 i16 i32 i64                    ; 整数
half float double fp80 fp128         ; 浮点
i32* %ptr                            ; 指针
[10 x i32]                           ; 数组
{i32, i8*, i32}                      ; 结构
<4 x i32>                            ; SIMD vector
```

二进制 → LLVM IR：

```bash
# clang/llvm 自家编译
clang -O0 -emit-llvm -S foo.c -o foo.ll
clang -O0 -emit-llvm -c foo.c -o foo.bc          # bitcode
llvm-dis foo.bc -o -                              # bc → ll
opt -O2 foo.ll -S -o foo.O2.ll                    # 优化
opt -passes='print<cfg>' foo.ll -disable-output  # 打印 CFG

# 二进制 lift
retdec-decompiler --backend-keep-libs orig.elf
mctoll -d orig.elf -o orig.ll                     # x86_64 → LLVM IR (LLVM 自家)
remill / mcsema 系列                               # Trail of Bits 老牌 lifter
```

## Ghidra P-Code

```python
# Ghidra Python：对一个函数列出所有 P-Code op
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
ifc = DecompInterface()
ifc.openProgram(currentProgram)
res = ifc.decompileFunction(getFunctionAt(toAddr(0x401050)), 60, ConsoleTaskMonitor())
hf = res.getHighFunction()
for pcodeop in hf.getPcodeOps():
    print(pcodeop)
# 输出: (unique, 0x100:8) COPY (register, 0x38:8)  类似
```

P-Code op 主要类型：`COPY / LOAD / STORE / BRANCH / CBRANCH / CALL / CALLIND / RETURN / INT_ADD / INT_AND / INT_LESS / INT_EQUAL / INT_MULT / INT_DIV / FLOAT_ADD / SUBPIECE / PIECE / POPCOUNT`。

## IDA microcode (Hex-Rays)

```python
# Hex-Rays Python：抓 microcode
import ida_hexrays
ea = idc.here()
mbr = ida_hexrays.mba_ranges_t()
mbr.ranges.push_back(ida_hexrays.range_t(ea, ea + 0x100))
hf = ida_hexrays.hexrays_failure_t()
mba = ida_hexrays.gen_microcode(mbr, hf, None, ida_hexrays.DECOMP_NO_WAIT, ida_hexrays.MMAT_PRECISE)
print(mba)
```

成熟用法是看 Lighthouse、HexRaysCodeXplorer、d810（去混淆器，基于 microcode pass）。

## radare2 ESIL

```bash
# ESIL 是 r2 的后缀表达式 IR
r2 -A orig.bin
> aei                                     # 初始化 ESIL VM
> aeim                                    # 初始化栈
> aef @ main                              # 模拟跑 main
> ae 0x10,rax,+,rax,=                     # 手动跑 ESIL: rax = rax + 0x10
> aer                                     # 列寄存器
> aezs                                    # ESIL 栈状态
> pa~mov rdi                              # 反汇编后过滤
> /Re mov rdi                             # 用 ESIL 模式搜
```

## 数据流分析快查

```text
SSA 形式 (Static Single Assignment)
  每个变量只赋值一次；分支汇合处用 phi 节点
  优势: def-use 链直接显式
  
CFG (Control Flow Graph)
  节点 = basic block；边 = 跳转
  Dominator: A dom B 当且仅当从 entry 到 B 都经过 A
  Post-dominator
  Dominance frontier (插 phi 用)

数据流 (Data-flow)
  Reaching definitions:    哪个 def 能流到这个 use
  Live variables:          这个变量到哪一行还活着
  Available expressions:   这个表达式之前算过没改过
  Constant propagation:    把已知常量代入
  Range analysis:          值域 [lo, hi]
  Pointer analysis:        ptr 可能指向哪些位置
  Alias analysis:          两个 ptr 是否别名

Taint analysis
  source: getenv / argv / read / recv / fread / sock recv
  sink:   system / exec / strcpy / sprintf / open(p) / SQL exec
  prop:   只跟踪 source 变量经过的拷贝/算术/字符串处理
  工具:   triton / panda / qira / dr-taint
```

## 符号执行 / 约束求解

### angr

```python
import angr, claripy
proj = angr.Project("crackme", auto_load_libs=False)

# 让 main 拿一个 16 字节符号输入
flag = claripy.BVS("flag", 16*8)
state = proj.factory.entry_state(stdin=flag)

simgr = proj.factory.simulation_manager(state)
WIN = 0x401234
LOSE = 0x4012a0
simgr.explore(find=WIN, avoid=LOSE)

if simgr.found:
    s = simgr.found[0]
    print(s.solver.eval(flag, cast_to=bytes))
```

```python
# call_state: 不从 main 跑，直接调一个函数
state = proj.factory.call_state(0x401050, claripy.BVS("arg", 64), 8)
simgr = proj.factory.simulation_manager(state)
simgr.explore(find=lambda s: s.regs.rax.concrete and s.solver.eval(s.regs.rax) == 1)
```

### Triton

```python
from triton import *
ctx = TritonContext(ARCH.X86_64)
ctx.setMode(MODE.ALIGNED_MEMORY, True)
ctx.setMode(MODE.AST_OPTIMIZATIONS, True)

# 注入指令字节码并跑
opcodes = b"\x48\x89\xf8"        # mov rax, rdi
ins = Instruction(opcodes)
ctx.processing(ins)
print(ins.getDisassembly())
print(ctx.getSymbolicRegister(ctx.registers.rax))

# 符号化输入
arg = ctx.symbolizeRegister(ctx.registers.rdi, "arg")
# 取约束求解
ast = ctx.getAstContext()
expr = ast.equal(ctx.getSymbolicRegister(ctx.registers.rax).getAst(), ast.bv(0xdeadbeef, 64))
model = ctx.getModel(expr)
print(model)
```

### KLEE（LLVM IR 上的符号执行）

```bash
# 编译目标到 bitcode
clang -O0 -Xclang -disable-O0-optnone -emit-llvm -c -g target.c -o target.bc

# 跑 KLEE
klee --libc=uclibc --posix-runtime target.bc --sym-args 0 3 8

# 输出在 klee-last/，每个 .ktest 是一组触发某分支的具体输入
ktest-tool klee-last/test000001.ktest
```

### Souper（找编译器优化机会，也能找 MBA 等价）

```bash
souper -z3-path=$(which z3) target.bc
```

### Z3 直接用

```python
import z3
x, y = z3.BitVecs('x y', 32)
s = z3.Solver()
s.add(x * 0x9e3779b9 + y == 0xdeadbeef)
s.add(x ^ y == 0x12345678)
print(s.check(), s.model())
```

## 混淆还原（IR 上做）

| 混淆 | 识别特征 | 还原 |
| --- | --- | --- |
| **MBA (Mixed Boolean-Arithmetic)** | `(a & b) + (a \| b) == a + b` 等等同恒等被嵌入 | gamba / SiMBA / Z3 等价检查 |
| **Control Flow Flattening** | 大 switch 调度块；状态变量驱动 | d810 (Hex-Rays) / Tigress 反向 / OLLVM-deobf |
| **不透明谓词 (Opaque Predicates)** | 永真/永假分支误导 | SMT 求解 + 可达性裁剪 |
| **指令替换 (substitute)** | `add x,y` → 一连串异或与 + 加 | 模式匹配 + IR 简化 |
| **Bogus Control Flow** | 死代码块 | 不可达分支删除 |
| **Virtualization (VMP/Themida)** | dispatch loop + handler table | `vmrev` 主导，IR 辅助 |

## 角色分工对照

```text
反编译器（Hex-Rays / Ghidra Decompiler）
    用 microcode / P-Code 给你"伪 C"，但隐藏 IR 细节

去混淆插件（d810, AmpleHeavy, gooMBA）
    在 microcode pass 链里插自定义 pass，输出更干净的伪 C

二进制 lifter（mctoll, retdec, remill）
    把机器码升到 LLVM IR，让你跑 LLVM 工具

符号执行框架（angr, Triton, manticore）
    自带 IR + 模拟器 + Z3 求解；适合自动找路径 / 还原 key

约束求解（Z3, CVC5, Yices, MathSAT）
    底层算力，绝大多数工具都封了一层
```

## 实战入口

- **angr CTF** — `github.com/jakespringer/angr_ctf`，从入门到精通的 16 关。
- **Cyber Apocalypse / DEFCON Quals 历年用 angr 题** — Writeups 全公开。
- **Tigress C Diversifier** — Christian Collberg，混淆器学习反向。
- **OllVM 项目** — LLVM 自带混淆器；研究它的 pass 可以反推还原。
- **MBA-Solver / SiMBA 论文与仓库**。
- **B2R2 / BAP / souper / SMT competition** — 学术工具的实战练手。

## 自检（拿到混淆 / 复杂二进制 30 分钟内回答）

1. 选哪种 IR 进入？（Hex-Rays microcode / Ghidra P-Code / angr VEX / Triton）
2. 函数 CFG 是被平坦化了吗？dispatcher block 在哪？状态变量是哪个？
3. 出现的运算是 MBA 嵌入还是真有意义？
4. 输入到目标 sink 的最短路径是什么？是否能符号执行求解？
5. 是否有不透明谓词把 SE 卡住？
6. 当前结论用 IR 验证一遍能复现吗？

## 相邻技能

- `binrev` — 反编译伪 C（最常用 IR 包装层）。
- `asmrev` — 单条指令的语义。
- `abirev` — IR 还原后的参数 / 返回 / vtable / EH 类型恢复。
- `vmrev` — 自实现 VM 的 dispatcher 与 handler 用 IR 描述并还原 opcode。
- `crashrev` / `memrev` / `debugrev` — 动态符号执行与 trace 引导。
- `cryptrev` — IR 上识别加密内核常量与运算。
- `fuzzrev` — IR 引导 fuzzer（dataflow / coverage / sancov）。
- `packrev` — packer 内置 VM 用 IR 还原。
- `linuxrev` / `winrev` / `macrev` — 平台 ABI 与 syscall 边界让 IR 模拟更准确。