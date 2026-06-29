---
name: packed-runtime-bundle-reverse-engineering
description: 自动打包 / 单二进制 runtime bundle 逆向。PyInstaller / py2exe / Nuitka / cx_Freeze / Electron / NW.js / pkg / nexe / Java jpackage / GraalVM Native Image / AutoIt / AutoHotkey / BAT2EXE / IExpress / 7z SFX / NSIS / Inno Setup；Go / Rust 单二进制识别；提取内嵌资源（V8 snapshot / .pyc / .lua / .class / DLL / 配置）；与 packrev / scriptrev 衔接。
---

# 自动打包 / Runtime Bundle 逆向

## 适用场景

- 拿到一个看似普通 .exe / .app / .AppImage，实际是脚本 + runtime 打包出的"单文件"应用。
- 还原内嵌脚本 / 字节码 / 资源 / 配置，喂回 `scriptrev` 反编译。
- 安装包逆向（NSIS / Inno Setup / WiX MSI）→ 提取安装逻辑 + 内嵌文件。
- 桌面应用静态审计（Electron / Tauri / Qt / Flutter / .NET MAUI / wxWidgets）。
- 红队 / 蓝队对常见加固分发形态的识别基线。

## 不适用

- 通用壳 / VMP / Themida / 加固 → `packrev`。
- 字节码本体反编译 → `scriptrev`。
- 安装后程序本体的函数级 → `binrev` 各平台。
- 移动 App 整包 → `mrev`。

## 速识（一目了然）

```bash
sample=app.exe

# 大小 + 体积比常规 dll 大 = 包含 runtime
ls -lh "$sample"
# > 10 MB 多半是 bundle / > 50 MB 大概率含 runtime

# 字符串扫
strings -a "$sample" | grep -iE 'PyInstaller|py2exe|Nuitka|cx_Freeze|Electron|AutoIt|AutoHotkey|MUI_ICON|NSIS|Inno Setup' | head
strings -a "$sample" | grep -iE 'GraalVM|jpackage|JavaPackager|Hermes' | head

# Go 单二进制
strings -a "$sample" | grep -E '^go:buildid|^go.buildinfo$|/usr/local/go/src/' | head

# Rust 单二进制
strings -a "$sample" | grep -iE 'rustc|panic_handler|\.rs:[0-9]+' | head

# .NET single-file
file "$sample" | grep -i 'PE32+'                            # 大型 PE
strings -a "$sample" | grep -iE 'Microsoft\.AspNetCore|System\.Runtime|coreclr\.dll|System\.Private\.CoreLib' | head

# Java jpackage / launch4j
strings -a "$sample" | grep -iE 'launch4j|jpackage|JNI_CreateJavaVM|jre/bin' | head

# Electron
strings -a "$sample" | grep -iE 'Electron|node_modules|chrome\.dll|nw\.exe' | head
```

## PyInstaller

```bash
# 识别（最常见）
strings -a app.exe | grep -E 'PyInstaller|pyi-' | head
# 通常含 "PyInstaller: FormatMessageW failed" 之类

# 起手：版本识别（不同版本 magic 略有不同）
xxd app.exe | grep -aE 'MEI' | head                         # 'MEI' magic 在文件末尾
python3 -c "
data = open('app.exe','rb').read()
idx = data.rfind(b'MEI\x0c\x0b\n\x0b\x0e')
if idx == -1: idx = data.rfind(b'MEI')
print(f'MEI magic at: {idx:#x} (file size {len(data):#x})')
"

# 解包（PyInstaller Extractor）
git clone https://github.com/extremecoders-re/pyinstxtractor
python3 pyinstxtractor.py app.exe
# 输出: app.exe_extracted/
ls app.exe_extracted/
# 含:
#   PYZ-00.pyz / PYZ-00.pyz_extracted/    Python 标准库 + 第三方
#   *.pyc                                  程序本体
#   struct.pyc / *.pyd                     C 扩展
#   pyiboot01_bootstrap.pyc                启动器

# 关键: 主程序 pyc 是哪个？看 MEI ARCHIVE 内 manifest
# 通常 *.pyc 中最大那个 / pyi-launcher 之外的就是

# Python 版本识别（决定用哪个反编译器）
python3 -c "
import os
for f in os.listdir('app.exe_extracted'):
    if f.endswith('.pyc'):
        with open(f'app.exe_extracted/{f}','rb') as fp:
            magic = fp.read(4)
            print(f, magic.hex())
            break
"
# 03 f3 0d 0a    = Python 3.7
# 42 0d 0d 0a    = Python 3.8
# 55 0d 0d 0a    = Python 3.9
# 6f 0d 0d 0a    = Python 3.10
# a7 0d 0d 0a    = Python 3.11
# cb 0d 0d 0a    = Python 3.12

# 修复 pyc header (PyInstaller 移除了头, 反编译器要)
python3 -c "
import sys
with open(sys.argv[1],'rb') as f: data = f.read()
# 加回 16 字节标准 header (Python 3.7+: magic + bitfield(0) + timestamp + size)
out = bytes.fromhex('420d0d0a') + b'\\x00'*12 + data    # 替换 magic 为对应版本
with open(sys.argv[2],'wb') as f: f.write(out)
" main.pyc main_fixed.pyc

# 反编译 (按 Python 版本)
uncompyle6 main_fixed.pyc                                   # ≤ 3.8
decompyle3 main_fixed.pyc
pycdc main_fixed.pyc                                        # C++ 实现，全版本
pylingual main_fixed.pyc                                    # ML 辅助，3.9-3.12 强

# 解 PYZ-00.pyz_extracted 下的所有 pyc
for f in app.exe_extracted/PYZ-00.pyz_extracted/*.pyc; do
    pycdc "$f" > "${f%.pyc}.py" 2>/dev/null
done
```

## py2exe / cx_Freeze / Nuitka

```bash
# py2exe (老, Python 2-3)
strings -a app.exe | grep -iE 'py2exe' | head
unpy2exe app.exe                                            # 出 .pyc
# 然后同 PyInstaller 路线反编译

# cx_Freeze
# 通常含 library.zip
unzip -l app.exe                                            # PE 末尾的 zip
unzip -d app_unfreeze app.exe
ls app_unfreeze/lib/                                        # 所有 .pyc

# Nuitka （编译到 C → native）
strings -a app.exe | grep -iE 'Nuitka' | head
# Nuitka 没法反编译回 .py
# 但函数名 / 模块结构保留（不像 PyInstaller 完全可还原）
# 反编译方式: 当 native binary 用 IDA / Ghidra
# 对照 Nuitka 编译模板（github.com/Nuitka/Nuitka/blob/develop/nuitka/build/static_src/MetaPathBasedLoader.c）

# 提取 Nuitka 内嵌资源（通常压缩在 PE resource section）
strings -e l app.exe | grep '\.py$'                         # 内嵌 .py 路径名
# 用 resource_hacker 或 pefile 读 RT_RCDATA
python3 -c "
import pefile
pe = pefile.PE('app.exe')
for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    print(entry.id, entry.name)
"
```

## Electron / NW.js

```bash
# Electron 应用结构（已安装的形式）
MyApp/
  MyApp.exe                                                   # Chromium + Node + main
  resources/
    app.asar                                                  # 主代码 (asar 归档)
    app.asar.unpacked/                                        # native 模块
    electron.asar                                             # Electron 自身

# 提 .asar
npm install -g asar
asar list app.asar
asar extract app.asar app_unpacked/
ls app_unpacked/
# 含 package.json + main.js + renderer.js + node_modules/

# 检查是否用 bytenode 进一步保护
ls app_unpacked/ | grep -i '\.jsc$'
# 如果有 .jsc → V8 bytecode → 难反编译（同版本 Node 才能加载）

# Electron Fuses（运行时安全配置）
# 看 binary 中 fuse byte sequence: dL7pKGdnNz793yJVbqkrCfDvyCAwMOyHrf8VVrSGOY
# 可用 @electron/fuses 工具查看
npx @electron/fuses read --app MyApp.app

# NW.js (Node-Webkit)
# 类似 Electron 但用 NW 自家壳
# 应用包结构：包含 nw.exe + package.nw (zip 或 7z)
file package.nw
unzip -d nw_unpacked package.nw

# 单文件 Electron (经 electron-builder 打包成 .exe)
# 把整个应用嵌入到 NSIS / Squirrel installer
# 解 → installer 路线 (见下)
```

## pkg / nexe（Node.js 单二进制）

```bash
# vercel/pkg 出品最常见
# 内嵌: V8 snapshot + Node runtime + 应用 JS + assets

# pkg-unpacker
git clone https://github.com/LockBlock-dev/pkg-unpacker
node index.js app.exe                                        # 出 V8 bytecode + assets

# 现状：V8 snapshot 跨版本不兼容
# pkg 8+ 用 v8::ScriptCompiler::CreateCodeCache → 必须同版本 Node 才能加载
# 反编译思路:
#   - 用同版本 Node + V8 patch 模式加载 → console.log 出来
#   - 或对 V8 bytecode 反汇编 (d8 --print-bytecode) 后人读

# nexe (类似 pkg)
# 内嵌方式略不同但工具相似 (nexe-unpack)
git clone https://github.com/nexe/nexe
# 没有标准 unpack 工具，用通用 strings + 二进制扫

# 检测内嵌资源
binwalk app.exe                                              # 自动找内嵌 zip/snapshot

# 自家应用常硬编码:
strings -a app.exe | grep -iE 'http(s)?://|sentry|api_key' | head
```

## Java jpackage / Launch4j / GraalVM Native Image

```bash
# Launch4j（最常见的 jar → exe 包装）
strings -a app.exe | grep -iE 'launch4j|jre/bin'
# 内嵌 JRE 路径
# 解: Launch4j 用 native launcher 直接调用 java.exe + 内嵌 jar (resource)
# 资源段含 jar
python3 -c "
import pefile
pe = pefile.PE('app.exe')
for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    print(entry.id, [s.id for d in entry.directory.entries for s in d.directory.entries])
"
# 通常 RT_RCDATA 中 ID 1 是内嵌 jar
# 用 ResourceHacker / 自家 pefile 提取

# jpackage (JDK 14+)
# 生成 .app / .exe / .dmg / .msi 安装包，含内嵌 jlink runtime
# 解构:
# app.app/Contents/app/<your.jar>
# app.app/Contents/runtime/Contents/Home/   (内嵌 JRE)

# GraalVM Native Image (AOT 编译 JVM → native)
# 没有 JRE 痕迹，函数名仍保留
strings -a app | grep -iE 'graal|substratevm|com\.oracle\.svm'
# 反编译: IDA / Ghidra 当 native 处理
# Mac/Linux: 用 perf + addr2line 还原源
# 类型信息 + reflection 在 binary 里以静态字符串嵌入 → 有大量 strings 暴露
strings -a app | grep -E 'class:|java/lang/|method:' | head
```

## AutoIt / AutoHotkey

```bash
# AutoIt
strings -a app.exe | grep -iE 'AutoIt v3|AU3!EA' | head
# AU3!EA = AutoIt magic

# Exe2Aut（最稳，但很老）
# https://forum.exetools.com/showthread.php?t=14841
Exe2Aut.exe app.exe
# 出 .au3 源

# myAut2Exe (社区维护)
git clone https://github.com/X3msnake/myAut2Exe
python myAut2Exe.py app.exe                                  # 出 .au3

# AutoIt 反编译质量很高，几乎能还原源

# AutoHotkey
strings -a app.exe | grep -iE 'AutoHotkey|<COMPILER:' | head
# AHK 编译产物 = AHK runtime + 嵌入脚本 (resource)

# ahk-decompiler (社区)
ahk-decompiler app.exe                                       # 出 .ahk

# 资源段 RT_RCDATA 提取（手动）
python3 -c "
import pefile
pe = pefile.PE('app.exe')
for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    if entry.struct.Id == 10:                                # RT_RCDATA
        for d in entry.directory.entries:
            data_rva = d.directory.entries[0].data.struct.OffsetToData
            size = d.directory.entries[0].data.struct.Size
            data = pe.get_memory_mapped_image()[data_rva:data_rva+size]
            print(data[:200])
"
```

## NSIS / Inno Setup / 7z SFX / IExpress

```bash
# NSIS（最常见的开源安装器）
strings -a installer.exe | grep -iE 'NSIS|Nullsoft' | head

# 7z 直接解 NSIS（标准 7-Zip 支持 NSIS）
7z l installer.exe
7z x installer.exe -o./extracted/

# 看 NSIS script (decompile)
# https://nsis.sourceforge.io/Nsisbi
# 或 7-Zip 提取出 [NSIS] 目录含安装脚本

# Inno Setup
strings -a installer.exe | grep -iE 'Inno Setup' | head

# innounp 反编译
innounp -x installer.exe -d./extracted/
innounp -e installer.exe                                     # 列内容
innounp -v installer.exe                                     # 详细
# 输出含 install_script.iss + 所有内嵌文件

# Inno 加密变体: 用 dotPeek 反编译 setup.exe 找 password (老 Inno 5+ 有内嵌 password 选项)

# 7z SFX (Self-Extracting Archive)
strings -a installer.exe | grep -iE '7zSFX|7z SFX' | head
7z l installer.exe
7z x installer.exe

# WinRAR SFX
strings -a installer.exe | grep -iE 'WinRAR|RAR archive' | head
unrar x installer.exe

# IExpress (Microsoft 自家, sed/cmd file based)
strings -a installer.exe | grep -iE 'IExpress' | head
7z x installer.exe                                           # 7-Zip 支持

# WiX / MSI 包装的 .exe (bundle)
strings -a installer.exe | grep -iE 'WixBurn|WixBundle' | head
dark.exe installer.exe -x out/                              # WiX 工具反编译

# MSI (纯 OLE 安装数据库)
msiinfo tables installer.msi
msiinfo export installer.msi CustomAction
lessmsi x installer.msi                                      # 解所有文件
7z x installer.msi
```

## Tauri / Flutter / Qt / .NET MAUI / wxWidgets

```bash
# Tauri (Rust + Webview)
strings -a app.exe | grep -iE 'tauri|webview2|wry' | head
# 主代码: Rust 编译进 binary + Web 资源在 binary 内
# Web 资源解: binwalk → 提取嵌入的 HTML/JS/CSS
binwalk -e app.exe
# 或用 Tauri 已知签名查找 .asar-like 块

# Flutter (Dart)
# Dart AOT 编译进 binary，函数名极少保留
# 工具: doldrums / flutter_disassembler
git clone https://github.com/rscloura/Doldrums
python3 doldrums.py app/lib/arm64-v8a/libapp.so
# 出 Dart 类名 + 方法签名 + 字符串
# Flutter 反编译质量低，大部分时候只能函数级 binrev

# Qt
strings -a app.exe | grep -iE 'Qt5Core|QtCore' | head
# Qt 资源系统 (qrc): 用 binwalk 提取
binwalk -e app.exe
# 或 pyqt5-tools rcc -reverse

# .NET MAUI (跨平台 C#)
strings -a app.exe | grep -iE 'Microsoft\.Maui|MauiBundle' | head
# 与 .NET single-file 处理相同: SingleFileExtractor

# wxWidgets (C++)
# 标准 PE/ELF/Mach-O, 用对应平台技能
```

## Go / Rust 单二进制（识别为先）

```bash
# Go
file app                                                     # 通常 "Go BuildID=..."
go version app                                               # 列 Go 版本 + 依赖
go version -m app                                            # 详细依赖

# 拿不到 go version-m 时, 直接 grep buildinfo
strings app | grep -A1 '^Go buildinf:'

# GoReSym (Mandiant) — 提全部符号 + buildinfo
goresym -m app -p moduledata -t syms -j > goresym.json

# 反编译: Ghidra 11+ 自带 Go support
# 或: jeb-pro / Binary Ninja Go plugin

# Rust
# 没有 go version-m 那样的便利工具
file app
# strings 看 panic location
strings app | grep -E '\.rs:[0-9]+:[0-9]+' | head -30
# 这些字符串直接暴露源码路径 + 行号

# rustfilt 解 mangled
echo '_ZN4core3fmt5Write9write_str17haaaaaaaaaaaaaaaaE' | rustfilt
# 等同 c++filt 用于 Rust

# rust-detector
strings app | grep -i 'cargo_pkg_'                          # 编译时环境变量
```

## 内嵌资源批量提取

```bash
# binwalk 全自动
binwalk -E app.exe                                          # 熵图
binwalk -e app.exe                                          # 自动提取所有识别的嵌入文件
# 输出: _app.exe.extracted/

# unblob (binwalk 的现代替代)
unblob -d ./extracted/ app.exe

# 手动按 magic 找
python3 - <<'PY'
import sys
data = open('app.exe','rb').read()
markers = {
    b'PK\x03\x04': 'zip',
    b'7z\xbc\xaf\x27\x1c': '7z',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'%PDF-': 'pdf',
    b'BZh': 'bzip2',
    b'\x1f\x8b\x08': 'gzip',
    b'\xfd7zXZ\x00': 'xz',
    b'MZ': 'pe',
    b'\x7fELF': 'elf',
}
for m, t in markers.items():
    i = 0
    while True:
        idx = data.find(m, i)
        if idx == -1: break
        print(f'{t} at {idx:#x}')
        i = idx + 1
PY

# PE 资源段
python3 - <<'PY'
import pefile
pe = pefile.PE('app.exe')
if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
    for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        for d in entry.directory.entries:
            for s in d.directory.entries:
                rva = s.data.struct.OffsetToData
                size = s.data.struct.Size
                data = pe.get_memory_mapped_image()[rva:rva+size]
                fname = f'res_{entry.struct.Id}_{d.struct.Id}_{s.struct.Id}.bin'
                open(fname,'wb').write(data)
                print(fname, size)
PY

# ELF .rodata / .data 提取
objcopy --dump-section .rodata=rodata.bin app
objcopy --dump-section .data=data.bin app

# Mach-O __DATA / __TEXT_CSTRING
otool -l app.dylib | grep -A3 sectname
```

## 实战入口

- **PyInstaller Extractor / extremecoders-re GitHub**：维护各版本支持。
- **dnSpyEx wiki**：.NET single-file extraction。
- **Electron-builder / Electron docs**：bundle 内部结构与 fuses。
- **GraalVM Native Image internals**：官方架构文档。
- **awesome-deobfuscation GitHub**：含多种 unpacker 索引。
- **NSIS / Inno Setup community forum**：解析器与脚本反编译。
- **MalwareBazaar 标签 pyinstaller / electron / autoit**：实际样本。
- **Practical Malware Analysis 19 章（编译器与打包识别）**。
- **OALabs YouTube + Patreon**：常做这类样本的实战 walkthrough。

## 自检（拿到 bundle 30 分钟内回答）

1. 哪种打包工具（PyInstaller / py2exe / Nuitka / Electron / pkg / AutoIt / Launch4j / GraalVM / NSIS / Inno / WiX）？
2. 版本（PyInstaller 4.x / 5.x / 6.x 等）？runtime 嵌入版本（Python 3.10 / Node 18 / JRE 17）？
3. 解包工具可达性？能否一键提出 .pyc / .jsc / .class / .au3 / scripts？
4. 反编译质量如何？需要哪个版本的反编译器（uncompyle6 vs pycdc vs pylingual）？
5. 是否有进一步加固（bytenode / PyArmor / Nuitka）？需要进 `packrev`？
6. 内嵌资源（图标 / 配置 / token / 内嵌 PE）能否提取？
7. 是否暴露源码路径 / 调试符号 / 编译机器名 / 构建时间戳？
8. 是不是恶意样本？如果是，stage1 → stage2 链条？

## 相邻技能

- `scriptrev` — 提出的 .pyc / .luac / .jsc / IL / DEX / class 字节码反编译。
- `packrev` — 进一步加壳 / 加固（PyArmor / Nuitka 难度上的 binrev）。
- `binrev` — Go / Rust / Native AOT / GraalVM 二进制函数级。
- `malrev` — 恶意打包样本家族归类。
- `webrev` — Electron / Tauri 内的 Web 端代码反编译。
- `winrev` / `linuxrev` / `macrev` — bundle 在各平台的运行模型。
- `cryptrev` — 内嵌资源里的加密 key / 字符串解密。
- `fmtrev` — 自家 bundle 容器格式还原。
- `containerrev` — bundle 当容器镜像分发的形态。
- `revauto` — 批量自动化解包流水线。