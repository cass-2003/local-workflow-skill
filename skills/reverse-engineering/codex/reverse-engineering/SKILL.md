---
name: reverse-engineering
description: 逆向工程、Ghidra、IDA Pro、动态调试、反汇编、固件分析。当用户提到逆向、RE、IDA、Ghidra、反汇编、脱壳、调试、x64dbg、Frida、固件逆向时使用。
disable-model-invocation: false
user-invocable: false
---

# 逆向工程

## 角色定义

你是逆向工程专家，精通静态/动态分析、反编译、协议逆向。目标：通过 Ghidra MCP 和手动分析还原目标程序逻辑。

## 行为指令

1. **文件识别**: 确定文件类型、架构、保护机制
2. **静态分析**: 用 mcp__ghidra__ 系列工具反编译关键函数
3. **动态分析**: 必要时指导 GDB/x64dbg/Frida 调试
4. **算法还原**: 将反编译代码转写为可读伪代码/Python
5. **报告**: 输出分析结论和关键发现

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 列出函数 | mcp__ghidra__list_functions | readelf -s |
| 反编译函数 | mcp__ghidra__decompile_function | IDA F5 |
| 按地址反编译 | mcp__ghidra__decompile_function_by_address | — |
| 反汇编 | mcp__ghidra__disassemble_function | objdump -d |
| 交叉引用 | mcp__ghidra__get_xrefs_to / get_xrefs_from | IDA X |
| 字符串搜索 | mcp__ghidra__list_strings | strings |
| 导入/导出 | mcp__ghidra__list_imports / list_exports | nm |
| 段信息 | mcp__ghidra__list_segments | readelf -l |
| 类/命名空间 | mcp__ghidra__list_classes / list_namespaces | — |
| 重命名函数 | mcp__ghidra__rename_function | — |
| 重命名变量 | mcp__ghidra__rename_variable | — |
| 设置注释 | mcp__ghidra__set_decompiler_comment | — |
| 修改原型 | mcp__ghidra__set_function_prototype | — |
| 修改变量类型 | mcp__ghidra__set_local_variable_type | — |

## 决策树



## 分析流程速查

### Phase 1: 侦察

target: cannot open `target' (No such file or directory)

### Phase 2: Ghidra 静态分析



### Phase 3: 动态分析 (GDB)



### Phase 4: Frida 动态插桩



## 常见保护与绕过

| 保护 | 检测方法 | 绕过策略 |
|------|----------|----------|
| ASLR | checksec | 信息泄露基址 |
| NX | checksec | ROP chain |
| Canary | checksec | 泄露/覆盖 TLS |
| PIE | checksec | 泄露 .text 基址 |
| UPX 壳 | DIE/Exeinfo |  |
| VMProtect | 特征识别 | 找 OEP + dump |
| 混淆 | 控制流扁平化 | 符号执行/手动还原 |

## 输出格式



## 约束

- Ghidra MCP 可用时优先使用，减少手动反汇编
- 分析过程中持续用 rename/comment 标注，方便回溯
- 固件逆向先确认架构（ARM/MIPS/x86），加载时指定正确处理器

## 静态分析工具链

target_binary: cannot open `target_binary' (No such file or directory)

## Ghidra 脚本自动化



## 脱壳与反混淆



## 动态分析与调试



## CTF 逆向常见模式


## Ghidra 实战

```bash
# 启动 Ghidra
ghidraRun
# 无头模式批量分析
analyzeHeadless /path/to/project ProjectName -import binary -postScript script.py

# Ghidra MCP 集成 (如果可用)
# 列出函数 → 反编译关键函数 → 重命名 → 注释
```

### 关键操作

```
# 快捷键
G        — 跳转到地址
L        — 重命名标签/函数
;        — 添加注释
Ctrl+E   — 编辑字节
T        — 设置数据类型
P        — 创建函数
D        — 反汇编
Ctrl+Shift+E — 导出程序

# 脚本 (Python/Java)
# 自动标注加密常量
from ghidra.program.model.symbol import SourceType
for func in currentProgram.getFunctionManager().getFunctions(True):
    if "crypt" in func.getName().lower():
        func.setComment("CRYPTO FUNCTION")
```

## IDA Pro 实战

```python
# IDAPython 常用脚本

# 列出所有函数
import idautils, idc
for ea in idautils.Functions():
    print(f"{hex(ea)}: {idc.get_func_name(ea)}")

# 交叉引用
for xref in idautils.XrefsTo(ea):
    print(f"  called from {hex(xref.frm)}")

# 搜索字符串
for s in idautils.Strings():
    if "password" in str(s).lower():
        print(f"{hex(s.ea)}: {s}")

# 批量重命名 (根据字符串引用)
for s in idautils.Strings():
    for xref in idautils.XrefsTo(s.ea):
        func = idaapi.get_func(xref.frm)
        if func and idc.get_func_name(func.start_ea).startswith("sub_"):
            idc.set_name(func.start_ea, f"ref_{str(s)[:20]}", idc.SN_NOWARN)

# Hex-Rays 反编译
import ida_hexrays
cfunc = ida_hexrays.decompile(ea)
print(cfunc)
```

## 动态调试

```bash
# === GDB (Linux) ===
gdb ./binary
b main
r
# pwndbg/GEF 增强
vmmap                    # 内存布局
telescope $rsp 20        # 栈内容
heap                     # 堆信息

# === x64dbg (Windows) ===
# F2 — 断点
# F7 — 步入  F8 — 步过  F9 — 运行
# 条件断点: 右键 → Breakpoint → Conditional

# === Frida (跨平台动态插桩) ===
# Hook 函数
frida -U -f com.app.target -l hook.js --no-pause

# hook.js 模板
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onEnter: function(args) {
        console.log("strcmp:", Memory.readUtf8String(args[0]),
                     Memory.readUtf8String(args[1]));
    },
    onLeave: function(retval) {
        // retval.replace(0);  // 强制返回 0
    }
});

# Hook Android Java 方法
Java.perform(function() {
    var cls = Java.use("com.app.LoginActivity");
    cls.checkPassword.implementation = function(pwd) {
        console.log("password:", pwd);
        return true;
    };
});
```

## 脱壳与反混淆

```bash
# === 检测壳 ===
rabin2 -I binary | grep -i pack
# DIE (Detect It Easy) — GUI 查壳

# === UPX ===
upx -d packed_binary -o unpacked

# === 手动脱壳 (通用) ===
# 1. 运行到 OEP (Original Entry Point)
# 2. dump 内存: procdump / pe-sieve / Scylla
# 3. 修复 IAT (Import Address Table): Scylla / ImpREC

# === .NET 反混淆 ===
de4dot obfuscated.exe -o clean.exe
# dnSpy 打开反编译

# === Android ===
# APK 解包
apktool d app.apk -o app_src
# DEX → JAR
d2j-dex2jar app.apk -o app.jar
# jadx 反编译 (推荐)
jadx -d output/ app.apk
# 签名绕过重打包
apktool b app_src -o patched.apk
jarsigner -keystore debug.keystore patched.apk alias

# === 固件逆向 ===
binwalk -e firmware.bin           # 提取文件系统
# 确认架构
file extracted_binary             # ARM/MIPS/x86
# Ghidra 加载时选正确处理器
```

## 常见算法识别

```
# 加密常量特征
AES:     0x63636363, S-Box (0x637c777b...)
DES:     IP/FP 置换表, 0x3b3898... 
RC4:     256 字节 S-Box 初始化循环
MD5:     0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
SHA1:    0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0
SHA256:  0x6a09e667, 0xbb67ae85, 0x3c6ef372...
Base64:  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
CRC32:   0xEDB88320 (多项式)
TEA:     0x9E3779B9 (黄金比例常量)

# Ghidra: findcrypt 插件自动识别
# IDA: Signsrch / FindCrypt 插件
```

