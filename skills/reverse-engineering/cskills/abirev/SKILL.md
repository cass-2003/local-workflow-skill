---
name: abi-reverse-engineering
description: ABI 与调用约定逆向。System V AMD64 / Microsoft x64 / AAPCS64 / ARM EABI / Stdcall / Cdecl / Fastcall / Thiscall 调用约定、C++ name mangling (Itanium / MSVC)、vtable 与 RTTI 布局、异常表（Itanium EH / SEH x64）、FFI 与跨语言调用、ObjC msgSend / Swift class layout。配合 binrev / asmrev / irrev 用。
---

# ABI 与调用约定逆向

## 适用场景

- 反编译伪代码里参数顺序对不上、返回类型不明、`this` 在哪一个寄存器，要回答这些。
- 看到 vtable / RTTI / typeinfo / 异常处理表，要还原类层级和虚函数调用。
- 跨语言 FFI（Rust ↔ C ↔ Swift ↔ ObjC ↔ Python ctypes）的边界，要识别参数转换和栈/寄存器布局。
- C++ / Swift / ObjC 重符号去 mangling 还原。

## 不适用

- 通用反汇编 / 寄存器使用 → `asmrev`。
- 反编译伪代码本身 → `binrev`。
- 平台 syscall ABI → `linuxrev` / `winrev` / `macrev`。
- 内核 ABI（VDSO / 系统调用号） → 平台技能。

## 调用约定速查表

| 平台 / ABI | 整数/指针参数 | 浮点参数 | 返回 | shadow space | 栈对齐 | callee-saved |
| --- | --- | --- | --- | --- | --- | --- |
| **SysV AMD64** (Linux/macOS/BSD) | rdi rsi rdx rcx r8 r9 → stack | xmm0..xmm7 → stack | rax (rdx 高 64) / xmm0 | 无 | 16 (call 前 8) | rbx rbp r12-r15 |
| **MS x64** (Windows) | rcx rdx r8 r9 → stack | xmm0..xmm3 → stack（共享槽） | rax / xmm0 | 32 字节 home | 16 | rbx rbp rdi rsi rsp r12-r15 + xmm6-xmm15 |
| **AAPCS64** (ARM64) | x0..x7 → stack | v0..v7 (HFA 例外) | x0 (x1 高) / v0..v3 | 无 | 16 | x19-x28, fp(x29), lr(x30), sp, v8-v15 (低 64) |
| **AAPCS32** (ARM32) | r0..r3 → stack | s0..s15 (vfp/hfa) | r0 (r1 高) / s0 | 无 | 8 | r4-r11, sp, lr |
| **cdecl** (x86) | 全栈，调用者清栈 | st0/st1 (x87) | eax (edx 高) / st0 | 无 | 4 (实际多对 16) | ebx esi edi ebp |
| **stdcall** (x86 WinAPI) | 全栈，被调清栈 | 同 cdecl | 同 cdecl | 无 | 4 | 同 cdecl |
| **fastcall (MSVC x86)** | ecx, edx → stack | 浮点入栈 | eax | 无 | 4 | 同 cdecl |
| **thiscall (MSVC x86)** | ecx=this, 其余栈，被调清栈 | 浮点入栈 | eax | 无 | 4 | 同 cdecl |
| **vectorcall (MSVC x86_64)** | 同 MS x64 + xmm0..5 用作 SIMD 参数 | xmm0..5 | rax / xmm0 | 32 字节 home | 16 | + xmm6-xmm15 |
| **syscall (Linux x64)** | rdi rsi rdx r10 r8 r9 (注意：rcx 被 syscall 指令覆盖) | 不用 | rax | 无 | — | r11/rcx 被破坏 |

注意 SysV vs MS x64 顺序差异是逆向最常见踩坑点：把 SysV 的 rdi 当成 MS 的 rcx 时整个签名错位。

### 大结构 / 浮点 / SIMD 返回

```text
SysV AMD64:
- 结构 ≤ 16B 且全 INTEGER 或全 SSE → 寄存器组合返回 (rax+rdx / xmm0+xmm1)
- 结构 > 16B → 隐藏第一个参数（指针，由 caller 在栈分配）
  caller: lea rdi, [rsp+...] ; call f          # rax = rdi
  callee: 把结果写到 [rdi]，返回 rdi

MS x64:
- 结构 8/16/32/64 bit → rax 直接
- 其他 → 隐藏第一个参数（同上）

AAPCS64:
- ≤ 16B → x0/x1 返回
- HFA (Homogeneous Floating-point Aggregate) ≤ 4 个相同类型浮点 → v0..v3
- 其他 → x8 是隐藏返回指针寄存器（不是参数寄存器之一）

可变参数 (...)
- SysV: rax = 浮点参数个数（vararg printf 必须，定参时也写）
- MS x64: vararg 总把浮点同时放 xmm 和 整数寄存器
- AAPCS64: 全部 vararg 走栈（macOS / iOS Apple 修订），其余 Linux/AAPCS 仍走寄存器
```

### 浮点 / SIMD ABI 细节

```text
SysV AMD64: xmm0..xmm7 接浮点；x87 ST(0) 用于 long double（80-bit）
MS x64: xmm0..xmm3 与整数寄存器共享 4 个槽位（call 时按声明顺序）
ARM64 AAPCS: v0..v7 浮点；HFA 与 HVA (vector aggregate) 各 8 个槽
```

## C++ Itanium ABI（GCC/Clang/macOS/iOS/Linux/Android）

### Name mangling 速查

```text
_Z<length><name><params>           不在命名空间的全局函数
_ZN<ns><cls><method>...E           带命名空间/类的成员
_ZSt                                std::
_ZNK                                const 成员
_ZNV                                volatile
模板:  _Z3fooIiEvT_                 foo<int>(int)
返回类型: 仅 const 之类前缀, 不在普通 mangle
ctor: _ZN3FooC1Ev = Foo::Foo()      C1 = complete, C2 = base, C3 = allocating
dtor: _ZN3FooD0Ev = ...             D0 = deleting, D1 = complete, D2 = base
operator: nw=new na=new[] dl=delete cl=()  ix=[]  ad=&  pl=+ mi=-

工具:
c++filt _ZN3foo3barEi              # _ZN3foo3barEi → foo::bar(int)
echo "_Z3fooIiEvT_" | c++filt
swift-demangle _$s4Test1AC1xACSi_tcfc

运行时实时:
abi::__cxa_demangle(name, NULL, NULL, &status);
```

### vtable 布局

```text
对象首 8 字节 = vptr (指向 vtable 中"地址点")

vtable 实际起点（地址点之前）:
  [-2 * sizeof(void*)] : offset_to_top  (强制转换上溯偏移)
  [-1 * sizeof(void*)] : RTTI 指针 (typeinfo for ClassName)
地址点:
  [+0]  : 第一个 virtual 方法 IMP
  [+8]  : 第二个
  [+16] : ...

多继承时每个父类对应一份子 vtable，对象内多个 vptr。
虚继承额外有 virtual base offset 表 (vtt) 用于 ctor。
```

```text
class Base { virtual void f(); virtual void g(); };
class Derived : public Base { void g() override; void h(); };

vtable for Derived:
   [0]  offset_to_top (0)
   [8]  typeinfo for Derived
   [16] Base::f
   [24] Derived::g    ← 覆盖
   [32] Derived::h    ← 新增 (但实际上 h 不是 virtual 时不出现)
```

调用：

```nasm
; obj->virtual_method()
mov     rax, [rdi]         ; vptr
call    qword [rax+0x10]   ; vtable[2]
```

### RTTI 速查

```text
typeinfo 节点（_ZTI* 符号）：
  [0]  vptr → __cxxabiv1::__class_type_info::vtable (或 __si_class_type_info, __vmi_class_type_info)
  [8]  类型字符串指针 (_ZTS* 符号)，是 mangled 字符串
  [16] base classes 数据 (vmi 才有，多继承)

dynamic_cast 检查走 typeinfo 链；多继承 / 虚继承时进入 vmi_class_type_info 走完整 hierarchy 表。

逆向 vtable 的入口:
  pseudo C: *(_QWORD *)(*(_QWORD *)obj + 0x10)(obj, arg)
  IDA 自动识别后会改写成 obj->vfn0xN(arg)
```

### Itanium 异常处理（DWARF / .eh_frame / .gcc_except_table）

```text
.eh_frame    : DWARF CFI（每个函数的栈展开信息）
.eh_frame_hdr : .eh_frame 的索引 + sorted FDE 列表
.gcc_except_table : LSDA（异常 landing pad 信息）+ try/catch 类型表

运行时:
__cxa_throw → _Unwind_RaiseException → 走 FDE 找 LSDA → 决定哪个 catch
__cxa_begin_catch → __cxa_end_catch
```

`readelf -wf binary` 看 .eh_frame；`llvm-dwarfdump --eh-frame` 更易读。

## MSVC ABI（Windows）

### Name mangling

```text
?      函数前缀
?function@@YA(args)X
@@YA   = function (calling convention)
@@QEAA = const member; @@SA = static; @@CA = virtual
@      命名空间分隔
Z      参数列表结束

工具:
undname.exe ?foo@@YAHHH@Z         # 把 mangled 还原成可读
dumpbin /symbols xxx.obj
```

### vtable 布局

类似 Itanium，但每项前不存 offset_to_top；多继承 thunk 在 vtable 项里直接是 thunk 函数：

```text
[+0] thunk: this 调整 + jmp 真函数
```

`dumpbin /headers /imports` 不显示 vtable；用 IDA Pro `Class Informer` 插件或 `Ghidra ClassyGhidra` 还原。

### SEH (Structured Exception Handling) x64

```text
.pdata 节: RUNTIME_FUNCTION 数组（每函数一项），含 BeginAddress / EndAddress / UnwindInfoAddress
.xdata 节: UNWIND_INFO + UNWIND_CODE 数组 + ExceptionHandler + ExceptionData

x86 (32 位 SEH 用 fs:[0] 链表) → 已改为 SAFESEH/SEHOP 缓解
x64 → 全部走 .pdata/.xdata，无 fs:[0] 链
```

## ObjC ABI

```text
所有方法调用 → objc_msgSend(receiver, selector, ...args)
  rdi = receiver (self)        // SysV
  rsi = selector (_cmd)
  rdx, rcx, r8, r9, stack = 真实参数

selector 在 __TEXT.__objc_methname 是字符串；Class 在 __DATA.__objc_classlist 数组
方法表 entry: { selector_ptr, types_string, IMP_ptr }

ObjC 反编译器（IDA / Hopper / Ghidra）会自动重写为:
  [self stringWithFormat:@"%d", x]
  原汇编是: lea rdi, self ; lea rsi, "stringWithFormat:" ; call _objc_msgSend

变体:
  objc_msgSend       普通
  objc_msgSendSuper  super 调用
  objc_msgSend_stret 大结构返回（隐藏返回指针 rdi，self 移到 rsi）
  objc_msgSend_fpret long double 返回
```

## Swift ABI（Apple Silicon / Darwin）

```text
class layout:
  [0]   isa pointer (兼容 ObjC 桥接)
  [8]   refcount + flags
  [16]+  fields

value witness table (VWT) 描述非 trivial 类型的 init/deinit/copy/move
type metadata + protocol witness table

mangling:
_$s<...>          # Swift 5+ stable ABI
_$ss5UInt8V        UInt8 类型
swift-demangle 还原:
  echo '_$s4Test1AC1xACSi_tcfc' | swift-demangle
  → Test.A.init(x: Swift.Int) -> Test.A
```

Swift 调用约定与 SysV 接近，但有自己的 `swiftcall` calling convention（`@convention(swift)`），多了 self / error 寄存器：x20 是 self 寄存器（ARM64），x21 是 error 寄存器。

## Rust ABI

Rust 默认 `extern "Rust"`，不稳定（编译器内部）。FFI 边界用 `extern "C"`：

```text
#[repr(C)] struct Foo { ... }     # 强制 C 布局，否则字段顺序由编译器决定
extern "C" fn foo(x: i32) -> i32  # SysV / MS x64 标准 C ABI
extern "system" fn bar()          # Windows 上 = stdcall (x86) / fastcall (x64)；其他平台 = "C"

panic/unwind 通过 Itanium EH 表（Linux/macOS）或 SEH（Windows）；二进制带 .eh_frame / .pdata。
no_std 二进制可能用 panic = "abort" → 没有 EH 表。
```

Rust 在符号表里大量出现：`core::`, `alloc::`, `std::`, `_$LT$`, `_$GT$`, monomorphized 函数有具体类型（`Vec$LT$u8$GT$::push`）。

## FFI 跨语言

```text
C ↔ C++:        extern "C" 包裹；name 不 mangle；ABI = C
C ↔ Swift:      @_silgen_name("foo") 显式给 C 名；@convention(c)
C ↔ ObjC:       直接互通，ObjC 是 C 超集
C ↔ Rust:       extern "C" 双向；#[repr(C)] 结构
C ↔ Python:     ctypes / cffi / PyO3 (Rust)
JNI (Java↔C):   函数签名 Java_<pkg>_<class>_<method>，前两参数 (JNIEnv*, jobject/jclass)，后参数按 Java 类型映射 jint/jlong/jstring/jbyteArray
```

## 反汇编里识别 ABI 的小技巧

```text
1) 函数收尾看 ret 类型:
   ret           cdecl / SysV / 大多数
   ret 0xN       stdcall / thiscall / fastcall (x86) — 被调清栈
   leave; ret    带帧指针的 SysV
   pacibsp...retab  ARM64e PAC

2) 参数寄存器使用模式:
   rdi 先用 → SysV
   rcx 先用 + sub rsp,0x28+ → MS x64 (shadow space)
   x0 先用 + stp x29,x30 → AAPCS64

3) 是否成员函数:
   函数序言后第一时间 mov rbx, rdi → SysV 成员（this 是 rdi）
   mov rbx, rcx → MS x64 成员（this 是 rcx）
   x86 mov esi, ecx → MSVC thiscall (this 是 ecx)

4) 返回大结构:
   函数刚开始 mov [rdi], 某值 + ret → 隐藏返回指针在 rdi（SysV）
   或 mov rax, rcx ; ret → 把 rcx (隐藏返回指针) 直接返回（MS x64 大结构）
   ARM64 函数序言用 x8 写返回 → 大结构隐藏指针在 x8

5) 异常处理:
   .eh_frame / .gcc_except_table 多 → Itanium / GCC/Clang
   .pdata / .xdata 多 → MSVC SEH x64
   __cxa_throw / __cxa_begin_catch → Itanium C++
   __CxxThrowException / __CxxFrameHandler3 → MSVC C++
```

## 实战入口

- **Itanium C++ ABI 文档** — `https://itanium-cxx-abi.github.io/cxx-abi/abi.html`，权威。
- **System V AMD64 ABI 文档** — `https://gitlab.com/x86-psABIs/x86-64-ABI`。
- **Microsoft x64 calling convention** — MSDN `x64-calling-convention`。
- **AAPCS64 / Procedure Call Standard for the Arm 64-bit Architecture** — ARM 官方。
- **Compiler Explorer (godbolt.org)** — 把 C++ 源码喂进去看不同编译器的 ABI 对应。
- **swift-demangle / c++filt / undname / rustfilt** — 必装。

## 自检（看到一段反编译 5 分钟内回答）

1. 哪个 ABI？SysV / MS x64 / AAPCS64？
2. 哪些寄存器是参数？是否成员函数（this 在哪）？
3. 返回类型是大结构还是寄存器？是否隐藏返回指针？
4. 是否 vararg？
5. 看到的间接调用是 vtable 还是函数指针？
6. 异常处理走 Itanium 还是 SEH？

## 相邻技能

- `asmrev` — 指令本身的语义。
- `binrev` — 反编译伪代码与函数布局。
- `irrev` — 反编译器中间表示如何重建参数 / 返回 / vtable。
- `linuxrev` / `winrev` / `macrev` — 各平台 syscall ABI 与 EH/SEH 节区。
- `cryptrev` — 库 API 调用的 ABI 边界（SysV / MS x64 / JNI）。
- `mrev` — JNI Android / Swift on iOS 的 ABI 桥接。
- `vmrev` — 自实现 VM 自家的"调用约定"。
- `scriptrev` — JNI / .NET P/Invoke / Python ctypes / Lua C API。