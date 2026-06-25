---
name: binary-diff-reverse-engineering
description: 补丁与版本差分逆向。Diaphora / BinDiff (Google/zynamics) / radiff2 / Ghidra Version Tracking / Kam1n0；函数 hash / CFG hash / 模糊 hash (ssdeep / tlsh)；Patch Tuesday 1-day 复现；跨架构 diff (ARM64 vs x64 同源)；编译器升级假阳性识别；BinExport / Binary Ninja / Cutter 配合。配合 binrev / crashrev / fuzzrev / malrev 用。
---

# 补丁与版本差分逆向

## 适用场景

- 拿到 v1（漏洞版）和 v2（补丁版）二进制，定位补丁位置 → 反推漏洞细节。
- Patch Tuesday 后 1-day 利用研究：windbg + bindiff 看 MS 月度补丁差异。
- 大型项目升级影响评估：哪些函数变了？签名一致吗？参数顺序？
- 恶意软件家族跟踪：v1.0 / v2.0 变种之间的差异 → 看作者改进了什么 / 修了什么 bug。
- 跨架构同源对照：iOS arm64 vs Android arm64 vs Windows x64 同源代码反编译结果对照。
- 闭源 SDK / 商业软件 兼容性验证：旧版 vs 新版的 ABI 是否兼容。

## 不适用

- 单个函数函数级反逆向 → `binrev`。
- 漏洞触发可达性分析 → `crashrev`。
- 找新漏洞 (fuzz) → `fuzzrev`。
- 自家协议字段层 → `protrev`。

## 工具速选

| 场景 | 首选 | 备选 |
| --- | --- | --- |
| **PE / ELF / Mach-O 函数级 diff** | Diaphora (IDA Plugin / Binary Ninja) | BinDiff (Google) |
| **轻量 CLI / 嵌入式** | radiff2 (radare2) / rizdiff (rizin) | sigkit |
| **Ghidra 原生** | Ghidra Version Tracking | binexport2 + bindiff |
| **跨架构同源** | Diaphora 跨架构模式 / Binary Ninja Sigkit | Pharos |
| **大规模函数匹配** | Kam1n0 (McAfee) / FunctionSimSearch | BinShot |
| **模糊 hash 聚类** | ssdeep / tlsh / sdhash / mrsh-v2 | imphash (PE) / authentihash |
| **PE / driver 升级 diff** | bindiff + IDA + windbg | Ghidra |
| **kernel 差异** | bindiff + 通用 vmlinux + DWARF | volatility comparing |

## Diaphora 全流程（最强）

```bash
# 装
# IDA 9+ 直接装 plugin
git clone https://github.com/joxeankoret/diaphora
# 复制到 IDA plugins 目录
# Binary Ninja 也支持: 装 binaryninja plugin

# 1) 分析旧版
# IDA 打开 v1.exe → 自动分析完成 →
# File → Script File → diaphora.py → 选 "Generate SQL database"
# 输出: v1.exe.sqlite

# 2) 分析新版
# IDA 打开 v2.exe → 自动分析完成 →
# 同上 → 输出 v2.exe.sqlite

# 3) Diff
# IDA 任一打开 → File → Script File → diaphora.py
# → 选 "Diff database against this one" → 选另一个 .sqlite
# Diaphora 会自动 match 函数 (按多种启发式)
# 输出 5 类:
#   Best matches:       100% 名字 + bytes 一样
#   Partial matches:    部分相似 (调用图 / 指令分布 / 常量)
#   Unreliable matches: 弱匹配 (按 callees / strings)
#   New functions:      v2 新增
#   Removed functions:  v1 有 v2 没了
# 双击任一 partial match → IDA 同时打开两边 + 高亮差异

# 4) CLI 批量比对（CI/CD）
python3 diaphora.py --batch v1.exe.sqlite v2.exe.sqlite \
    --output diff.sqlite --reporter html
firefox diff.html
```

```python
# 自家脚本读 Diaphora 输出
import sqlite3
conn = sqlite3.connect('diff.sqlite')
cur = conn.cursor()
cur.execute("SELECT name, name2, ratio FROM results WHERE ratio < 1.0 ORDER BY ratio DESC")
for name, name2, ratio in cur.fetchall():
    print(f"{ratio:.2f}  {name} <-> {name2}")
```

### Diaphora 启发式排序（理解输出）

```text
完全相同 (1.00):
  same_name + same_bytes      (符号名字 + 字节完全一致)

高置信:
  same_address + same_bytes
  same_pseudocode             (Hex-Rays 反编译输出相同)
  same_assembly_normalized    (规整化汇编后相同)

中等置信:
  callgraph_similarity > 0.85
  cfg_similarity > 0.8
  mnemonics_distribution      (指令统计相近)
  same_constants              (字符串常量相同)

弱置信:
  same_callees                (调用相同子函数集)
  same_strings                (使用相同字符串)
  same_imports                (调用相同 import)

新 / 删:
  new in v2 / removed from v1

调参:
  Diaphora 设置 → 调整 threshold / 启用更多启发式
```

## BinDiff（Google/zynamics 经典）

```bash
# 装
# Linux: 下载 .deb https://www.zynamics.com/bindiff.html
sudo apt install ./BinDiff-7.deb

# 流程
# 1) IDA 分析每个二进制 → File → Produce file → Binary Export (.BinExport)
# 或: ida -A -B -OBinExportAutoAction:BinExportBinary -OBinExportModule:auto v1.exe
# 2) BinDiff CLI:
bindiff v1.BinExport v2.BinExport -output_dir=out

# 3) GUI
bindiff_gui
# File → New Diff → 选两个 .BinExport
# 出函数对比表 + similarity 评分

# 4) IDA Plugin (BinDiff for IDA)
# 在 IDA 里直接对照打开 v1 + v2，high-light 函数差异

# similarity: 0.0 - 1.0
# confidence: 0.0 - 1.0
# bindiff 同时显示两个指标
```

## radiff2 / rizdiff（CLI 轻量）

```bash
# radiff2 (radare2)
radiff2 -A v1.exe v2.exe                                     # 函数级
radiff2 -AC v1.exe v2.exe                                    # 同时考虑 callgraph
radiff2 -O v1.exe v2.exe                                     # 全二进制级
radiff2 -d v1.exe v2.exe                                     # 反汇编模式对比
radiff2 -g main v1.exe v2.exe | xdot -                       # 单函数 callgraph diff
radiff2 -t 70 v1.exe v2.exe                                  # 相似度阈值

# rizdiff (rizin fork)
rizdiff -AC v1.exe v2.exe

# 输出格式示例:
# 0x00401234 80% 0x00501234     (中等匹配)
# 0x00401500 100% 0x00501500    (完全匹配)
# 0x00401800 NEW                 (v2 新增)
```

## Ghidra Version Tracking

```text
Ghidra 自带 Version Tracking (VT) tool, 不需第三方插件

启动:
  Ghidra → Tool → Version Tracking
  
工作流:
  1) 在 Project Manager 把 v1 + v2 都 import
  2) New Session → 选 source (v1) + destination (v2)
  3) Add Correlators:
     - Exact Match (function bytes / instruction bytes / mnemonics)
     - Reference Correlator (相同地址引用)
     - Symbol Name (导出符号同名)
     - Data Match
  4) Accept matches (高置信自动接受 + 低置信人工确认)
  5) 接受后 → v2 自动应用 v1 的符号名 / 注释 / 数据类型
  6) 剩余未匹配 = 新函数或删除函数 = 重点关注

CLI 自动化:
  analyzeHeadless ./proj proj -postScript VTAutoApply.java -import v2.exe
```

## CFG / Function hashing

```python
# 自家做函数指纹
# IDA 脚本
import idautils, idaapi
def func_hash(ea):
    fn = idaapi.get_func(ea)
    if not fn: return None
    # 提取 normalized mnemonics
    mnems = []
    for head in idautils.Heads(fn.start_ea, fn.end_ea):
        if idaapi.is_code(idaapi.get_full_flags(head)):
            mnems.append(idc.print_insn_mnem(head))
    return hash(tuple(mnems))

hashes = {}
for f in idautils.Functions():
    h = func_hash(f)
    hashes[h] = hashes.get(h, []) + [idc.get_func_name(f)]

# 跨二进制比对
# v1.hashes / v2.hashes → 找相同 hash 不同名 = 重命名 函数
```

```bash
# 现成模糊 hash 函数级
sigkit                                                      # Vector35 出品，Binary Ninja 插件
function-simhash                                            # Google
FunctionSimSearch                                           # Google

# 整二进制级
ssdeep -b sample1 sample2                                   # 经典模糊哈希
tlsh sample1 sample2                                        # Trend Micro 模糊哈希
sdhash sample1 sample2
```

## Patch Tuesday 1-day 复现工作流

```text
1) 拿到 KB 编号 (KB5005565 等), 找到对应 .msu 包
   - microsoft.com/en-us/download/details.aspx
   - winbindex.m417z.com (社区维护，按文件名找历史)

2) 抽出补丁文件
   expand -F:* KB5005565.msu C:\out\
   # 出大量 cab / msp，进一步:
   expand -F:* update.cab C:\out2\
   # 含 .dll / .sys / .exe 等被替换的二进制

3) 找出"未补"版本（前一个月的 KB）
   winbindex.m417z.com → 按文件名 + Microsoft VirusTotal 查更早版本

4) Diaphora / BinDiff
   v1 = patched dll, v2 = unpatched dll
   找新增的边界检查 / 长度校验 / 异常处理 → 那就是漏洞修补点

5) 反推漏洞:
   补丁加 if (len > max) → unpatched 没有 → 即 buffer overflow
   补丁加 NULL check → 即 NULL deref
   补丁改 alloc size → integer overflow
   补丁改 token check → privilege escalation
   补丁改 type check → type confusion

6) 写 PoC
   crashrev 思路：构造让该函数走到补丁前的路径

参考:
  - msrc-microsoft.us-microsoft.com/update-guide/  (官方公告)
  - github.com/google/oss-fuzz-vulns
  - Microsoft Patch Diffing Workshop (NCC Group)
```

## 编译器升级导致的"假阳性"

```text
v1 用 GCC 9, v2 用 GCC 11 → 反汇编大幅差异，但语义不变
v1 -O1, v2 -O2 → inline / 死代码消除 / 寄存器分配变化
v1 用 MSVC 19.29, v2 用 MSVC 19.34 → CFG 字节不同但函数语义相同

识别方法:
  - 看 .rdata 中嵌入的编译器版本字符串 ("Visual Studio 16.10" 等)
  - 看 PE 头 Rich Header (Microsoft toolchain fingerprint, 含 build N)
  - 看 ELF Note 段的 GCC version
  - 看 Mach-O LC_BUILD_VERSION

应对:
  - Diaphora 的 "Same pseudo-code" 启发式比 "Same bytes" 更稳
  - normalize_assembly 选项启用 (Diaphora) / mnemonic-only 模式 (radiff2 -m)
  - 跨编译器场景重点看 callgraph + string + import 匹配
```

## 跨架构 diff

```text
ARM64 vs x86_64 同源:
  - 指令完全不同，bytes diff 无意义
  - 但函数调用图 (CFG) 类似
  - imports / strings / constants 一致
  
Diaphora 跨架构启发式:
  - same_pseudocode  (Hex-Rays 输出几乎一致)
  - same_callees
  - same_strings
  - same_constants
  - same_imports
  - callgraph_similarity (拓扑相似)

CFG hashing:
  - 把 CFG 编码成 string (BFS 顺序的节点度数序列)
  - 同源函数即使在不同架构，CFG 应该相同
  - 工具: FunctionSimSearch (Google, 跨架构最强)
```

## BinExport / 格式互换

```text
BinExport (zynamics): 二进制分析的中间格式
  - 含完整反汇编 + 符号 + 函数边界 + xrefs
  - 跨 IDA / Ghidra / Binary Ninja 互操作

工具链:
  IDA -> binexport.dll plugin       -> .BinExport
  Ghidra -> BinExport ext (Java)    -> .BinExport
  Binary Ninja -> binexport plugin  -> .BinExport
  
然后 BinDiff / 自家工具读 .BinExport
  
BinExport 协议: 
  Google protobuf, schema 公开
  github.com/google/binexport

把 .BinExport 转换成 SQL/JSON 进自家流水线
```

## ssdeep / tlsh 模糊 hash 聚类（家族跟踪）

```bash
# ssdeep
ssdeep -b sample1.exe sample2.exe sample3.exe               # 两两比相似度
ssdeep -l sample.exe > sig.txt                              # 生成 signature
ssdeep -m sig.txt unknowns/*                                # 用已有 sig 扫未知

# tlsh
tlsh sample.exe                                             # 单文件 hash
tlsh -c file1 -f file2                                      # 两两距离 (0 = 相同)
tlsh -r dir1/ -d dir2/                                      # 目录跨集合

# imphash (PE 专属，import 表的 hash)
python3 -c "import pefile; print(pefile.PE('sample.exe').get_imphash())"
# imphash 相同 = 编译时 import 一致 = 高度可能同源
# 大量 malware 家族 share imphash

# authentihash (PE Authenticode hash, 排除签名段)
python3 -c "import pefile; print(pefile.PE('sample.exe').get_authentihash())"

# Mandiant FLARE: capa 输出可作"行为指纹"
capa sample1.exe -j > sample1.json
capa sample2.exe -j > sample2.json
diff <(jq '.rules|keys' sample1.json) <(jq '.rules|keys' sample2.json)
```

## 实战例子（公开案例）

```text
CVE-2020-0796 (SMBGhost) – SMB3 压缩头部 integer overflow
  diff srv2.sys v1 vs v2 → SmbCompressionDecompress 多了边界 check
  补丁: if (SizeOfData > 0xFFFFFFFF - OffsetOrLength) return ERROR
  漏洞: 没这个 check → 整数溢出 → heap overflow

CVE-2021-31166 (HTTP.sys ULPHandleAcceptedTransport)
  diff HTTP.sys v1 vs v2 → Accept-Encoding 字段处理改写

CVE-2023-29336 (win32k!xxxClientAllocWindowClassExtraBytes)
  diff win32kfull.sys → 处理 UAF 加了 reference counting

CVE-2024-21338 (Appid driver IOCTL)
  diff appid.sys → 加了 SeAccessCheck 在 IOCTL handler 入口

每一个公开 1-day writeup 都来自 bindiff/diaphora
- Project Zero blog
- ZDI (Zero Day Initiative)
- Quarkslab blog
- Cybereason / Talos / Mandiant
```

## 自动化批量 diff 流水线

```bash
#!/bin/bash
# diff_pipeline.sh
# 对一个 vendor / 软件的每月新版自动 diff

VENDOR=$1
OLD_DIR=$2
NEW_DIR=$3

for new in $NEW_DIR/*.dll; do
    name=$(basename $new)
    old=$OLD_DIR/$name
    [ -f $old ] || continue
    
    # 拿 sha256, 不同才继续
    if [ $(sha256sum $old | cut -d' ' -f1) == $(sha256sum $new | cut -d' ' -f1) ]; then
        continue
    fi
    
    # 用 IDA 自动分析
    ida -A -B "-O Diaphora:export $old" $old &
    ida -A -B "-O Diaphora:export $new" $new &
    wait
    
    # CLI diff
    python3 diaphora.py --batch $old.sqlite $new.sqlite \
        --output diff/$name.sqlite --reporter html
    
    # 提取 partial matches
    sqlite3 diff/$name.sqlite "SELECT name, name2, ratio FROM results WHERE ratio < 1.0 AND ratio > 0.5" \
        > diff/$name.txt
done

# 生成报告 + 发邮件
python3 generate_diff_report.py diff/ > monthly_diff.html
mail -s "Patch Diff Report" team@example.com < monthly_diff.html
```

## 实战入口

- **Project Zero blog 1day series**：bindiff 实战标杆。
- **ZDI Advisory + writeup**：每个 advisory 常含 root cause + diff 思路。
- **NCC Group / Microsoft Patch Diffing Workshop**。
- **Talos blog / Mandiant blog / SecuriTeam 公告**。
- **Quarkslab / Cybereason / SentinelLabs 长文**。
- **Diaphora GitHub 文档**（作者 joxeankoret 经常更新）。
- **BinDiff 学习社区**：zynamics 老用户社群。
- **CTF reversing 题**：含 v1 v2 对比类题（FlareOn 偶有）。
- **awesome-reversing GitHub list**：含 diff 工具索引。

## 自检（拿到 v1 / v2 30 分钟内回答）

1. 两版二进制的 sha256 / 大小 / 模块版本号 / 编译器版本是否变化？
2. 用哪个工具组合（Diaphora / BinDiff / Ghidra VT / radiff2）？
3. 100% / partial / new / removed 各几个？哪几个 partial 最可疑？
4. 函数级差异落在哪：边界 check / NULL check / 类型转换 / 加密 key 变更？
5. 是否有跨架构同源对照需求？用哪种启发式（pseudocode / callgraph）？
6. 是否含未匹配新函数（v2 新加防御 / v1 残留代码）？
7. 编译器升级导致的假阳性如何过滤？
8. 自家流水线集成（CI/CD）需要哪些步骤？

## 相邻技能

- `binrev` — 函数级理解（diff 拿到位置后的深挖）。
- `crashrev` — 拿到 root cause 后构造触发输入。
- `fuzzrev` — diff 找到候选点后 fuzz 验证可达性。
- `malrev` — 家族 v1 vs v2 跟踪。
- `irrev` — Ghidra P-Code / decompiled C 跨架构对照。
- `winrev` / `linuxrev` / `macrev` — 平台补丁 KB / cumulative update 抽取。
- `cryptrev` — 加密算法 / key 变更识别。
- `vmrev` — VM handler 表 v1 vs v2 对照（VMP/Themida 升级）。
- `revauto` — 自动化批量 diff 流水线。
- `rev-report` — diff 结论组织成可交付报告。