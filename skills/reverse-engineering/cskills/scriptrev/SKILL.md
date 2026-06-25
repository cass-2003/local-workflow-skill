---
name: script-bytecode-reverse-engineering
description: 脚本与字节码逆向。DEX / smali / .NET IL / Java JVM / Lua / LuaJIT / Python pyc / Hermes / Ruby YARV / PowerShell / VBA / JavaScript bytecode / Erlang BEAM / WebAssembly。dnSpy / ILSpy / cfr / jadx / uncompyle6 / pycdc / unluac / hbcdump 全套；混淆与反混淆模式（de4dot / Invoke-Deobfuscation / synchrony / webcrack）。配合 vmrev / mrev / docrev 用。
---

# 脚本 / 字节码逆向

## 适用场景

- 拿到 .pyc / .luac / .dex / .class / .dll (.NET) / .jsc / .ps1 / .vba / .wasm 等字节码或脚本产物，要还原源代码或语义。
- 加密 / 编译 / 混淆 后分发的"脚本类"应用：PyInstaller、py2exe、Nuitka、Electron jsc、React Native Hermes、Unity IL2CPP（与 gamerev 配）。
- 恶意样本中的 stage 脚本（PowerShell / VBA / VBE / JScript / WSH / HTA / Office Macro / OneNote VBA / .NET dropper）。
- 自家加固后的 Java/Kotlin（DexGuard / R8 / ProGuard）与 .NET（ConfuserEx / Eazfuscator / dotNetReactor / Dnguard）。

## 不适用

- 字节码所在的虚拟机本身（dispatcher / handler） → `vmrev`。
- 移动 App 整体（Android/iOS） → `mrev`。
- 文档宏样本（doc/xls/pdf/rtf） → `docrev`。
- 文件格式 / 容器 → `fmtrev`。

## 字节码总览

| 字节码 | 容器 | 反编译 → 源 | 反汇编 |
| --- | --- | --- | --- |
| **.NET IL** (CLR) | .exe / .dll / .nupkg | dnSpyEx / ILSpy / ikvm / cfr | ildasm / monodis |
| **Java bytecode** (JVM) | .class / .jar / .war | cfr / fernflower / procyon / Krakatau / Jadx | javap |
| **Android DEX** | .dex / .odex / .vdex / classes\*.dex in apk | jadx / d2j (dex2jar) + cfr / bytecode-viewer | baksmali |
| **Smali** (DEX 人类可读) | .smali | jadx GUI | apktool baksmali |
| **Python pyc** | .pyc / __pycache__/*.pyc / 嵌入式 | uncompyle6 (≤3.8) / decompyle3 / pycdc / xdis | dis |
| **Lua 5.x source-less** | .lua / .luac | unluac / luadec / ChunkSpy | luac -l |
| **LuaJIT bytecode** | .luac / .luajit | LjDec / LJD / luajit-disas | luajit -b |
| **Hermes** (RN) | .bundle / .hbc | hbcdump / hermes-dec / hermes-dec-tool | hbcdump -dis |
| **Ruby YARV** | .rb compiled / .rbc / Sorbet | rb2c (有限) / Iseq disasm | RubyVM::InstructionSequence#disasm |
| **PowerShell** | .ps1 / .ps1xml / .psd1 / .psm1 / EncodedCommand | 直接读 → 反混淆 | AST 解析 |
| **VBA / VBE** | .doc/.xls 内嵌 / .vbe (encoded) | olevba / vbadeobf | oledump |
| **JS bytecode (V8 snapshot)** | .blob / pkg / nexe | bytenode → 部分 / V8 patch | d8 --print-bytecode |
| **Erlang BEAM** | .beam | erlang:disassemble / beam_disasm | beam_lib:chunks |
| **Elixir** (BEAM) | .beam | erlang:disassemble | iex(1)> :beam_disasm.file/1 |
| **WebAssembly** | .wasm / .wat | wabt / wasm-decompile / wasm2c / Ghidra | wasm-objdump |
| **JavaScript** (源) | .js / bundle.js | webcrack / synchrony / unminify / @babel | (不需要反编译) |
| **TypeScript .tsbuildinfo** | — | tsc + sourcemap |
| **Bitcode / LLVM IR** | .bc / .ll | llvm-dis / opt | — |
| **Forth / Threaded code** | — | 自家工具 | — |
| **HBC Hermes JS** | .hbc | hermes-dec | hbcdump |

## .NET IL

```bash
# dnSpyEx (社区 fork，最现代)
dnSpyEx Sample.exe                                          # GUI：反编译 + 调试 + 编辑 + 重保存

# ILSpy (CLI + GUI)
ilspycmd Sample.dll > Sample.cs                             # 反编译到 C#
ilspycmd -p Sample.dll > Project.csproj                     # 出可编译工程

# de4dot (自动反混淆 30+ 种壳)
de4dot Sample.exe                                           # 输出 Sample-cleaned.exe
de4dot -p un Sample.exe                                     # unknown 模式
de4dot --strtyp emulate Sample.exe                          # 字符串解密用模拟器

# ConfuserEx 专项
ConfuserExUnpacker Sample.exe
de4dot.cex Sample.exe                                       # ConfuserEx 增强版

# .NET single-file (Apphost bundle) 拆解
SingleFileExtractor Sample.exe                              # 提出内嵌 DLL
# 或: HostModelExtractor / SingleFileExtractorNg

# 反混淆 + 反编译流水线
de4dot Sample.exe && ilspycmd Sample-cleaned.exe > Sample.cs

# ildasm / monodis 反汇编（看 IL）
ildasm Sample.dll /out=Sample.il /text
monodis Sample.dll > Sample.il

# 编辑 IL 后重打包
ilasm Sample.il /dll /output=Sample-patched.dll

# Roslyn 解析器: dotPeek (JetBrains, 免费 GUI)
# Reflexil (dnSpy 插件): 直接改方法
```

## Java / Android DEX

```bash
# 反编译 .class / .jar
cfr Sample.jar --outputdir cfr_out                          # CFR (推荐, 现代 Java 支持最好)
java -jar fernflower.jar Sample.jar fern_out                # FernFlower (IntelliJ 内置)
java -jar procyon-decompiler.jar Sample.jar -o proc_out     # Procyon
krakatau decompile Sample.jar -out krak_out                 # Krakatau

# javap (JDK 自带反汇编)
javap -c -p -v Sample.class

# Android APK
jadx-gui Sample.apk                                         # GUI，最常用
jadx -d out Sample.apk                                      # CLI 出全部源 + smali
jadx -d out --deobf --escape-unicode Sample.apk             # 反 ProGuard 名字混淆
jadx -d out --show-bad-code Sample.apk                      # 即使有 bug 也尽量出代码

# dex2jar + cfr (老路)
d2j-dex2jar.sh classes.dex -o classes.jar
cfr classes.jar --outputdir cfr_out

# apktool (smali 层)
apktool d Sample.apk -o smali_out
ls smali_out/smali_classes*/                                # smali 源
# 改 smali → 重打包 → 签名
apktool b smali_out -o new.apk
zipalign -p 4 new.apk aligned.apk
apksigner sign --ks debug.keystore aligned.apk

# baksmali / smali (单独)
java -jar baksmali.jar dis classes.dex -o smali_out
java -jar smali.jar assemble smali_out -o classes.dex

# DexGuard / R8 / ProGuard 名字还原
# 找 .map / mapping.txt 文件 → jadx 自动应用
jadx --deobf --deobf-min 3 -d out Sample.apk
# 或手动用 retrace
retrace.sh mapping.txt stack.txt

# Java 字符串解密：常见模式
# 字段被 ProGuard 混淆为 a.b.c，但运行时通过 reflection 还原
# 跑动态 + JDWP 调试拿真实值
# JDWP: jdb 或 IntelliJ remote debug

# Frida hook 抓运行时解密的字符串
frida -U -f com.target.app -e '
Java.perform(() => {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.doFinal.overload("[B").implementation = function (data) {
        var out = this.doFinal(data);
        console.log("Cipher.doFinal -> " + Java.use("java.lang.String").$new(out));
        return out;
    };
});
'
```

## Python pyc

```bash
# 起手识别 magic（python 版本）
xxd sample.pyc | head -2
# 03 f3 0d 0a   Python 3.7
# 42 0d 0d 0a   Python 3.8
# 55 0d 0d 0a   Python 3.9
# 6f 0d 0d 0a   Python 3.10
# a7 0d 0d 0a   Python 3.11
# cb 0d 0d 0a   Python 3.12
# 完整对照: github.com/google/pytype/blob/main/pytype/pyc/magic.py

# 反编译
uncompyle6 sample.pyc                                       # ≤ 3.8 (老牌但范围窄)
decompyle3 sample.pyc                                       # 3.7-3.8 (uncompyle6 fork)
pycdc sample.pyc                                            # 3.x (C++ 实现, 全版本)
pylingual sample.pyc                                        # 新一代，ML 辅助，3.9-3.12 强
xdis-show sample.pyc                                        # 显示头 + 字节码
xdis-disasm sample.pyc                                      # 反汇编

# dis (Python 自带)
python3 -c "import dis, marshal, importlib.util
with open('sample.pyc','rb') as f:
    f.read(16)                                              # 跳过 magic + 时间戳 + size + invalid_idx
    code = marshal.load(f)
dis.dis(code)
"

# PyInstaller 打包的 .exe 解开
git clone https://github.com/extremecoders-re/pyinstxtractor
python3 pyinstxtractor.py app.exe                           # 输出 app.exe_extracted/
cd app.exe_extracted
ls *.pyc PYZ-*.pyz_extracted/                               # 一堆 .pyc

# py2exe / cx_Freeze
unpy2exe sample.exe                                         # py2exe 专用
# cx_Freeze 出 library.zip，unzip 后是 .pyc

# Nuitka (编译到 C → native)
# 没办法反编译回 .py
# 只能反汇编 native binary (binrev) + 对照 Nuitka 模式识别
strings sample.exe | grep -i 'Nuitka'
# Nuitka 的函数名仍保留 + 模块结构清晰，比 PyInstaller 难逆

# pyminifier / pyobfuscate 反混淆
# - base64 / zlib / marshal 解码（自家解开）
# - exec("...") / eval("...") 多层包装 → 逐层 print 解
```

## Lua

```bash
# Lua 5.1/5.2/5.3/5.4 各代差异大，必须先确定版本
xxd sample.luac | head -1                                   # 'Lua\x53' 等 magic + 版本字节
file sample.luac

# 反编译
unluac sample.luac                                          # Lua 5.1 (最稳)
luadec sample.luac                                          # Lua 5.1 / 5.2
ldec sample.luac
luac-decompiler sample.luac
ChunkSpy.lua sample.luac --brief                            # 反汇编 + 部分反编译

# 反汇编（原生）
luac -l -p sample.luac                                      # 列字节码

# LuaJIT bytecode (不是标准 Lua)
luajit -bg -o out.lua sample.luac                           # 生成 readable disasm
LjDec sample.luac                                           # 反编译尝试
LJD sample.luac

# Cocos2d-xLua 加密
# 厂家常在 luac 头部 XOR 8 字节，先去 XOR 再喂工具
python3 -c "
data = open('sample.luac','rb').read()
key = b'XOR_KEY'                                            # 在引擎源码里找
out = bytes(b ^ key[i%len(key)] for i,b in enumerate(data))
open('decoded.luac','wb').write(out)
"

# WeChat 小游戏 Lua: signLuaC + 自家魔术头
# 飞行棋 / 棋牌类常 Lua 加密
```

## Hermes (React Native 新引擎)

```bash
# RN App 解包后, 找 .hbc 或 main.jsbundle (Hermes 模式时含 'Hermes' magic)
xxd index.android.bundle | head -1                          # 'c6 1f bc 03' 为 Hermes magic

# hbcdump (Facebook 官方)
hbcdump -mode=disassembly index.hbc > index.hasm

# hermes-dec (社区反编译)
git clone https://github.com/P1sec/hermes-dec
hermes-dec index.hbc -o decompiled.js

# 看 Hermes 版本
hbcdump -mode=hbcVersion index.hbc

# RN 普通模式（非 Hermes）= 直接是 JS bundle → 用 webrev 路线
```

## Ruby

```bash
# 编译 Ruby (Sorbet/.rb → .rbc) 较少见，绝大多数 .rb 是源
# YARV 字节码（运行时）
ruby -e 'puts RubyVM::InstructionSequence.compile(File.read("a.rb")).disasm'

# 反编译尝试
gem install ruby_parser sexp_processor
gem install ruby2ruby
ruby -r ruby2ruby -e 'puts Ruby2Ruby.new.process(RubyParser.new.parse(File.read("a.rb")))'

# 编译型 (Rubinius, mruby) 二进制
# mruby bytecode (.mrb)
mrbc -e a.rb                                                # 编译
mruby -b a.mrb                                              # 跑
# 反编译: 没有现成成熟工具
```

## PowerShell

```powershell
# 混淆 PowerShell 常见手法 + 反混淆

# 1) Base64 encoded command
powershell.exe -enc <BASE64>
# 解:
[System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String("<BASE64>"))

# 2) Compress + base64
$bytes = [System.Convert]::FromBase64String("...")
$ms = New-Object IO.MemoryStream(,$bytes)
$ds = New-Object IO.Compression.DeflateStream($ms, [IO.Compression.CompressionMode]::Decompress)
$sr = New-Object IO.StreamReader($ds)
$sr.ReadToEnd()

# 3) Invoke-Obfuscation 反混淆
# https://github.com/danielbohannon/Invoke-Obfuscation 反向工具:
# - PSDecode (psdecode.psm1)
PowerShell.exe -ExecutionPolicy Bypass -File PSDecode.ps1 sample.ps1
# - Revoke-Obfuscation (检测/打分混淆程度)

# 4) AST 解析（Microsoft 推荐）
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    "sample.ps1", [ref]$null, [ref]$null)
$ast.FindAll({$args[0].GetType().Name -eq "InvokeMemberExpressionAst"}, $true)

# 5) AMSI bypass 识别（关键字）
'AmsiUtils' 'amsiInitFailed' 'AmsiScanBuffer' 'patch' 'unhook'

# 6) PowerShell ScriptBlock Logging 看历史
Event ID 4104 (Microsoft-Windows-PowerShell/Operational)
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational';Id=4104}

# 7) IEX (Invoke-Expression) 链
# 嵌套 IEX 多层 → 用 PSDecode 自动解层
```

## VBA / VBE / Office Macro

```bash
# oletools (Decalage 出品，最全)
pip install oletools

# VBA 源
olevba sample.doc                                           # 反混淆字符串 + 自动启发式
olevba --decode sample.doc                                  # 解 Hex/Base64/Dridex
olevba --reveal sample.doc                                  # 显示函数调用图
olevba --analysis sample.doc

# OLE 对象 dump
oledump.py sample.doc                                       # 列流
oledump.py sample.doc -s 8 -d                               # dump stream 8

# OLE map
olemap sample.doc

# OOXML (docx/xlsx) → unzip + vbaProject.bin
unzip -d unpacked sample.docx
oledump.py unpacked/word/vbaProject.bin

# VBE (encoded VBS) 解码
git clone https://github.com/bontchev/decode-vbe
python3 decode_vbe.py sample.vbe > sample.vbs

# VBA Stomping 识别（源代码与 p-code 不一致 = 极可疑）
olevba --no-deobf --analysis sample.doc | grep -i 'stomp'

# Excel 4.0 (XLM) macro
xlmdeobfuscator sample.xls
oletools-xlm sample.xls
# Excel 4.0 不是 VBA，是老式 XLM macro，2020-2022 大量样本回潮

# 反编译 VBA p-code（即使源被擦除）
pcodedmp sample.doc                                         # github.com/bontchev/pcodedmp
```

## JavaScript bytecode（V8 snapshot / pkg / nexe）

```bash
# pkg / nexe 把 Node.js 应用编译成单 binary（含 V8 snapshot + Node runtime）

# pkg-unpacker (vercel/pkg)
git clone https://github.com/LockBlock-dev/pkg-unpacker
node index.js app.exe                                       # 提出 V8 bytecode + assets

# pkg2bin: 拆出 V8 snapshot
# 现状：V8 snapshot 跨版本不兼容，多数情况需要 V8 同版本 d8 加载

# bytenode (Node.js 字节码模式)
node -e 'require("bytenode").compileFile({filename:"a.js",compileAsModule:true})'
# 生成 a.jsc, 内含 V8 内部 bytecode
# bytenode 自家没有反编译工具，社区有 bytenode-decode (功能有限)

# Electron .asar
asar extract app.asar app_unpacked/
# app_unpacked/ 通常是普通 JS（除非进一步用 bytenode 编译）

# nexe（少见）
# 类似 pkg，先 unpack 出 V8 snapshot

# V8 bytecode 反汇编（限定同版本 V8）
d8 --print-bytecode --print-bytecode-filter=funcname sample.js

# 反编译 JS bundle / minify → 见 webrev
```

## Erlang BEAM / Elixir

```bash
# 反汇编
erl -noshell -eval 'beam_disasm:file("sample.beam"), init:stop().'
erl -noshell -eval 'io:format("~p~n",[beam_lib:chunks("sample.beam",[abstract_code])]), init:stop().'
# 如果 abstract_code 还保留 → 几乎能还原源码
# 多数生产 BEAM 都被 strip 掉了 abstract_code

# Elixir
mix decompile sample.beam                                   # 社区工具
elixir-decompile sample.beam

# Erlang AST 还原
erl -noshell -eval '
    {ok,{_,[{abstract_code,{_,AC}}]}} = beam_lib:chunks("sample.beam",[abstract_code]),
    io:format("~s~n",[erl_prettypr:format(erl_syntax:form_list(AC))]),
    init:stop().'
```

## WebAssembly

```bash
# WABT (官方工具集)
wasm-objdump -x sample.wasm                                 # PE-like dump
wasm-objdump -d sample.wasm                                 # 反汇编
wasm2wat sample.wasm -o sample.wat                          # 转人类可读 .wat
wat2wasm sample.wat -o sample.wasm                          # 反向

# 反编译到 C
wasm-decompile sample.wasm -o sample.dcmp                   # 类 C 输出（WABT 自带）
wasm2c sample.wasm -o sample.c                              # 真正能编译的 C

# Ghidra 11+ 自带 WebAssembly Loader（直接拖 .wasm 进去）

# Twiggy: 大小分析
twiggy top sample.wasm                                      # 哪个函数最大
twiggy dominators sample.wasm
twiggy paths sample.wasm

# wasm-tools (Bytecode Alliance)
wasm-tools dump sample.wasm
wasm-tools strip sample.wasm
wasm-tools demangle sample.wasm                             # Rust 名字解 mangle

# Component model (新)
wasm-tools component wit sample.wasm                        # 出 WIT (WebAssembly Interface Type) 接口
```

## JavaScript（源级反混淆）

```bash
# webcrack（推荐, 综合反 webpack + obfuscator.io + javascript-obfuscator）
npm install -g webcrack
webcrack input.js -o output/

# synchrony (javascript-obfuscator 专项)
npm install -g deobfuscator
deobfuscator input.js

# de4js (GUI Web 工具)
# https://lelinhtinh.github.io/de4js/

# AST 自家管线 (Babel)
npm install @babel/parser @babel/traverse @babel/generator @babel/types
node -e "
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generator = require('@babel/generator').default;
const fs = require('fs');

const src = fs.readFileSync('input.js','utf8');
const ast = parser.parse(src);
traverse(ast, {
    StringLiteral(path) {
        // 自定义解码逻辑
    }
});
console.log(generator(ast).code);
"

# JStillery / JSDetox / 旧式 packer 解包
```

## 自家解释器 / 自家 VM 字节码

如果上面工具都不认 → 该字节码是自家 VM：

```text
1) 确认它是字节码（不是机器码）：
   - 大段 data 段 entropy 中等（5-7）
   - 没有 ELF/PE/Mach-O 头
   - 二进制里看到 dispatcher 函数（大 switch / 函数指针表）

2) 找 dispatcher → 找 handler → 编 opcode 表
   → 进 vmrev 技能（自家 VM 还原）

3) 常见自家字节码：
   - 商业应用反爬 / DRM
   - 游戏脚本（自家 Lua-like）
   - 黑产马 stage payload 自定义编码
   - 一些 .net / java 加固后期的 IL/Java 重新映射
```

## 混淆 / 加密反制

```text
通用步骤:
  1) 提 strings → 看是否是 base64 / hex / xor 链
  2) 找 entry main → 看是否只 eval/exec 一段 → 解一层
  3) 重复 1-2 直到出明文
  4) 字符串数组 + 索引 obfuscation：找到数组 → 替换索引为字符串
  5) 控制流平坦化：用 IR-level 工具（angr/d810/Tigress unflattener）
  6) Dead code 注入：用 dataflow analysis 删
  7) MBA (Mixed Boolean-Arithmetic)：simba 简化器

工具:
  Python obfuscator (PyArmor, hyperion, layhey)
    PyArmor 多版本 → 用 pyarmor-unpacker / pydecipher
  JS obfuscator.io: webcrack 直接处理
  .NET ConfuserEx: de4dot
  Java ProGuard/R8: jadx --deobf + mapping.txt 还原
  Android DexGuard / DashO: 没有公开反混淆器，手动 + Frida hook

字符串/常量解密的通用脚本套路:
  - 找解密函数 (常 static + 小循环 + XOR/RC4/AES)
  - hook 解密函数，记 (输入, 输出) 表
  - 全局替换所有引用为解密结果
```

## 实战入口

- **Flare-On**：Mandiant 年度逆向 CTF，**几乎每年有一题是字节码/脚本类**。
- **MalwareBazaar PowerShell / VBA / OLE 标签**：海量真实样本。
- **CyberChef**：在线一站式编码 / 加密 / 混淆识别（recipe 链）。
- **The Office Macro Adventure (Decalage)**：oletools 作者教程。
- **0xdf htb writeups / IppSec YouTube**：CTF 风格但工具讲得透。
- **Mandiant FLARE / Microsoft Threat Intelligence / SentinelLabs / Securelist**：脚本类样本深度报告。
- **dnSpyEx / ILSpy / jadx GitHub Issues**：实战问题答案库。
- **awesome-deobfuscation / awesome-reversing GitHub list**。

## 自检（拿到字节码 30 分钟内回答）

1. 字节码类型 + 版本（.NET 4.8 / Python 3.10 / Lua 5.3 / Hermes 88）？
2. 是否被混淆？哪种工具混的（识别签名）？
3. 反编译能否直接成功？需要先 de4dot / 自家脱壳？
4. 是否含 native loader（加固型）？需要进 mrev / packrev 配合？
5. 字符串解密 / 索引数组 / 控制流平坦化 哪种混淆模式？
6. 出现的高危 API：网络 / 注册表 / 文件 / 反射 / 远程加载？
7. 是否有 multi-stage（一层解一层）？需要几层才能见到明文？

## 相邻技能

- `vmrev` — 自家 VM 字节码（非标准）→ dispatcher / handler 还原。
- `mrev` — Android/iOS 整 App（与 DEX/IL2CPP 衔接）。
- `webrev` — JavaScript 源级反混淆 / Webpack 反打包。
- `docrev` — Office 文档 / OLE / RTF 投递层。
- `malrev` — 脚本类恶意样本上下游联动。
- `packrev` — .NET 加壳 (ConfuserEx) / Python 加壳 (PyArmor)。
- `cryptrev` — 字节码内嵌的字符串解密算法识别。
- `binrev` — Nuitka / Cython / Unity IL2CPP 编译到 native 的对照。
- `gamerev` — Unity Mono / IL2CPP / Unreal Blueprint / Cocos Lua 等游戏脚本字节码。
- `revauto` — 反混淆 / 反编译自动化流水线。