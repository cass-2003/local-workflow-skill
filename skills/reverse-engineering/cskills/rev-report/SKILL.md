---
name: reverse-engineering-report
description: 逆向报告与交付收口。报告骨架（摘要 / 范围 / 样本身份 / 方法 / 关键发现 / 证据索引 / 影响 / 限制 / 复现）+ IOC 输出（YARA / Sigma / Suricata / Snort / KQL / Splunk SPL / OpenIOC / STIX 2.1 / MISP）+ ATT&CK 映射 + 时间线 + 复现脚本 + Pandoc / drawio / mermaid 渲染 + 客户交付。配合所有 *rev 技能用。
---

# 逆向报告与交付

## 适用场景

- 完成 1 个或多个样本 / 漏洞 / 事件的分析，要把结论组织成可交付的报告。
- 客户 / 上级 / 同事需要不同详细程度的内容（执行摘要 vs 技术细节 vs 复现指令）。
- 报告需要可机读：YARA / Sigma / STIX2 / MISP event 直接喂进检测系统。
- 长期归档：报告要可复现（含数字证据 + 命令链 + 工具版本）。
- 团队内的"知识库"沉淀：每份报告变成下次开局的起点。

## 不适用

- 样本本身的分析 → 各专项技能。
- 实验室基础设施 → `revlab`。
- 自动化分析流水线 → `revauto`。

## 报告骨架（通用模板）

```markdown
# 报告标题 — 一句话概括样本 / 事件
**ID:** 2026-04-15-mal-xxx
**Author:** 分析师
**Date:** 2026-04-15
**Classification:** TLP:AMBER
**Version:** 1.0

## 执行摘要 (Executive Summary)
1-2 段，决策者读完即可。
- 这是什么？(family / 类别)
- 影响范围？
- 优先级 / 严重等级？
- 推荐动作 (3 条 bullet)？

## 范围 (Scope)
- 收到的 N 个样本 SHA256
- 分析时段
- 不在本报告范围的：（明确边界）

## 样本身份 (Sample Identification)
| Field | Value |
|---|---|
| SHA256 | abc... |
| MD5 | ... |
| Size | 123 KB |
| Type | PE32 executable (DLL) |
| Imphash | ... |
| TLSH | ... |
| Compile time | 2024-XX-XX |
| Compiler | MSVC 19.34 |
| Signed | No / Yes (subject: ...) |
| First seen (VT) | 2024-XX-XX |
| Family | (推断) |

## 方法 (Methodology)
- 静态: IDA Pro 9.0 / Ghidra 11.1 / capa 6.x / floss 2.x / pestudio
- 动态: CAPE Sandbox / Wireshark / Sysmon (config v77)
- 环境: Windows 11 23H2 / Ubuntu 24.04 / macOS 15.x
- 工具版本固定（reproducibility）

## 关键发现 (Key Findings)
1. **功能 / 类别** — 一句话 + 证据指针 (§3.1)
2. **C2 通道** — 域名 / 协议 / 端口 (§3.2)
3. **持久化** — 注册表键 / 计划任务 (§3.3)
4. **横向移动** — SMB / WMI / Schedule (§3.4)
5. ……

## 技术细节 (Technical Details)
### 3.1 加载流程
[反汇编截图 / 伪代码 / call graph]
**证据:** offset 0x401234 in sample.exe, decompile excerpt

### 3.2 C2 协议
[wireshark 截图 + 字段表]
**证据:** pcap chunk #45, packet 123

### 3.3 持久化
**证据:** registry key, scheduled task, …

### 3.4 ATT&CK 映射
| Tactic | Technique | ID | Evidence |
|---|---|---|---|
| Execution | Command and Scripting Interpreter: PowerShell | T1059.001 | §3.1 |
| Persistence | Registry Run Keys | T1547.001 | §3.3 |
| Defense Evasion | Obfuscated Files | T1027 | §3.5 |
| C2 | Application Layer Protocol: Web Protocols | T1071.001 | §3.2 |
…

## 影响 (Impact)
- 受影响系统 / 用户范围
- 危害等级 (CVSS / DREAD / 自家标准)
- 业务影响

## IOC 表 (Indicators of Compromise)
### Hashes
- abc... (SHA256, dropper)
- def... (SHA256, stage2)

### Network
- bad-c2.example[.]com
- 1.2.3.4 (port 443)
- URL: https://bad-c2.example.com/api/v1/checkin

### Files
- C:\ProgramData\loader.dll
- /tmp/.cache/loader

### Registry / Scheduled Tasks
- HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Updater
- \Microsoft\Windows\Custom\UpdateTask

### YARA
（见附录 A）

### Sigma
（见附录 B）

## 限制 (Limitations)
- 加密的 C2 内容未解（仅看到流量大小 + 时序）
- 部分 stage2 拉取地址条件触发，未走到
- 反沙箱机制使 X 分钟内未触发完整链

## 复现 (Reproduction)
```bash
# 在 FLARE-VM 24.04 中：
sha256=abcd…
wget https://lab/samples/$sha256 -O sample.exe
# 隔离 VM, 设 sinkhole
inetsim &
# 启动样本
./sample.exe
# 预期：
#   - HTTP POST to bad-c2.example.com:443/api/v1/checkin
#   - registry persistence
#   - cmd.exe 子进程被 spawn
```

## 时间线 (Timeline)
- 2026-04-15 09:00 UTC — 样本首次收到
- 2026-04-15 09:05 UTC — 静态分析开始
- 2026-04-15 10:30 UTC — 沙箱跑完
- 2026-04-15 13:00 UTC — IOC 写完
- 2026-04-15 15:00 UTC — 报告草稿
- 2026-04-15 17:00 UTC — 同行评审
- 2026-04-15 18:00 UTC — 发布

## 附录 A: YARA 规则
…

## 附录 B: Sigma 规则
…

## 附录 C: 工具版本
- IDA Pro 9.0 build 240520
- Ghidra 11.1.0
- capa 6.1
- ...

## 附录 D: 参考资料
- [1] Vendor advisory
- [2] CVE-2024-XXXXX
- [3] 类似家族报告 ...
```

## 证据条目格式（每个发现必须）

```text
每个"关键发现"对应一个证据块：

**Evidence E-001**
- Type: function / string / network / registry / file
- Location: sample.exe @ 0x401234  (or pcap #45 / dump.bin @ 0x1000)
- Tool: IDA Pro 9.0
- Command: `idat -A -B sample.exe`
- Excerpt:
    [反汇编 / hex / 截图]
- Hash of excerpt: sha256 of the relevant region

证据归档:
  evidence/
    E-001-disasm.txt
    E-001-disasm.png
    E-002-netflow.json
    E-003-regdump.txt
    sha256sums.txt
```

## IOC 多格式输出

### YARA

```yara
rule Family_XYZ_Variant_2026 {
    meta:
        author = "team"
        date = "2026-04-15"
        report = "2026-04-15-mal-xxx"
        sha256 = "abc..."
        family = "XYZ"
        score = 95
        tlp = "amber"
    strings:
        $magic = { 4D 5A } // PE
        $s1 = "Custom/1.0 (Windows NT 10.0; x64)" ascii
        $s2 = "/api/v1/checkin" ascii
        $s3 = "::cfg::" wide
        $op1 = { 6A 40 68 00 30 00 00 } // PUSH 40h, PUSH 3000h (VirtualAlloc flag)
    condition:
        $magic at 0
        and filesize < 5MB
        and 2 of ($s*)
        and $op1
}
```

### Sigma

```yaml
title: XYZ Loader CreateRemoteThread into LSASS
id: 12345678-1234-1234-1234-123456789012
status: experimental
description: Detect process injection pattern from family XYZ (report 2026-04-15-mal-xxx)
references:
    - https://example.com/reports/2026-04-15-mal-xxx
author: team
date: 2026/04/15
logsource:
    product: windows
    service: sysmon
detection:
    selection:
        EventID: 8
        TargetImage|endswith: '\lsass.exe'
        SourceImage|endswith:
            - '\rundll32.exe'
            - '\regsvr32.exe'
            - '\mshta.exe'
    condition: selection
falsepositives:
    - Legitimate AV process scanning lsass
level: high
tags:
    - attack.defense_evasion
    - attack.privilege_escalation
    - attack.t1055
    - attack.t1003
```

```bash
# 转换到具体 SIEM
sigma convert -t splunk rule.yml > rule.spl
sigma convert -t elastic rule.yml > rule_lucene.txt
sigma convert -t microsoft365defender rule.yml > rule.kql
sigma convert -t qradar rule.yml
sigma convert -t powershell rule.yml                          # 给本地 PoSH 跑
```

### Suricata / Snort

```text
alert dns $HOME_NET any -> any any (msg:"XYZ DNS lookup to known C2";
    dns_query; content:"bad-c2.example.com"; depth:50;
    classtype:trojan-activity; sid:1000001; rev:1;
    reference:url,example.com/reports/2026-04-15-mal-xxx;)

alert http $HOME_NET any -> $EXTERNAL_NET any
   (msg:"XYZ Custom UA";
    flow:established,to_server; http.user_agent;
    content:"Custom/1.0"; http.method; content:"POST"; http.uri;
    content:"/api/v1/checkin";
    classtype:trojan-activity; sid:1000002; rev:1;)
```

### KQL (Microsoft Sentinel / Defender)

```kql
// Detection: XYZ loader injection
let report_id = "2026-04-15-mal-xxx";
DeviceProcessEvents
| where Timestamp > ago(30d)
| where InitiatingProcessFileName in~ ("rundll32.exe", "regsvr32.exe", "mshta.exe")
| join kind=inner (
    DeviceImageLoadEvents
    | where FileName =~ "lsass.exe"
) on $left.DeviceId == $right.DeviceId and $left.InitiatingProcessId == $right.InitiatingProcessId
| project Timestamp, DeviceName, InitiatingProcessFileName, FolderPath, ProcessCommandLine, report_id
| order by Timestamp desc
```

### Splunk SPL

```text
index=windows EventCode=8 (TargetImage="*lsass.exe")
| eval source_proc=replace(SourceImage,"^.*\\\\","")
| search source_proc IN (rundll32.exe, regsvr32.exe, mshta.exe)
| stats count by ComputerName, source_proc, TargetImage
```

### STIX 2.1 (machine-readable IOC)

```json
{
  "type": "bundle",
  "id": "bundle--abc123",
  "objects": [
    {
      "type": "indicator",
      "spec_version": "2.1",
      "id": "indicator--abc1...",
      "created": "2026-04-15T09:00:00Z",
      "modified": "2026-04-15T18:00:00Z",
      "name": "XYZ Loader C2 Domain",
      "indicator_types": ["malicious-activity"],
      "pattern": "[domain-name:value = 'bad-c2.example.com']",
      "pattern_type": "stix",
      "valid_from": "2026-04-15T09:00:00Z",
      "labels": ["malicious-activity"]
    },
    {
      "type": "malware",
      "spec_version": "2.1",
      "id": "malware--xyz...",
      "name": "XYZ Loader",
      "malware_types": ["downloader", "trojan"],
      "is_family": true
    },
    {
      "type": "relationship",
      "spec_version": "2.1",
      "id": "relationship--rel1...",
      "relationship_type": "indicates",
      "source_ref": "indicator--abc1...",
      "target_ref": "malware--xyz..."
    }
  ]
}
```

### MISP Event

```python
from pymisp import PyMISP, MISPEvent, MISPAttribute, MISPObject

misp = PyMISP('https://misp.example.com', 'API_KEY', ssl=False)

ev = MISPEvent()
ev.info = "XYZ Loader 2026-04-15 — Analysis Report 2026-04-15-mal-xxx"
ev.distribution = 1     # community
ev.threat_level_id = 2  # medium
ev.analysis = 2         # completed
ev.add_tag('tlp:amber')
ev.add_tag('mitre-attack-pattern="Process Injection - T1055"')

# 加单个 attribute
ev.add_attribute('sha256', 'abc...', comment='Sample dropper')
ev.add_attribute('domain', 'bad-c2.example.com', comment='C2')
ev.add_attribute('url', 'https://bad-c2.example.com/api/v1/checkin')
ev.add_attribute('ip-dst', '1.2.3.4')
ev.add_attribute('yara', open('xyz.yar').read(), comment='Detection rule')

# 用 object 模型（更结构化）
file_obj = MISPObject('file')
file_obj.add_attribute('filename', 'loader.dll')
file_obj.add_attribute('sha256', 'abc...')
file_obj.add_attribute('size-in-bytes', 12345)
ev.add_object(file_obj)

misp.add_event(ev)
```

### OpenIOC（老格式但仍支持）

```xml
<OpenIOC xmlns="http://schemas.mandiant.com/2010/ioc">
  <indicator id="abc..." operator="OR">
    <IndicatorItem condition="contains">
      <Context document="DnsEntryItem" search="DnsEntryItem/Host"/>
      <Content type="string">bad-c2.example.com</Content>
    </IndicatorItem>
    <IndicatorItem condition="is">
      <Context document="FileItem" search="FileItem/Sha256sum"/>
      <Content type="string">abc...</Content>
    </IndicatorItem>
  </indicator>
</OpenIOC>
```

## 自动化 IOC 转换

```bash
# Sigma → 多种 SIEM
sigma convert -t splunk rule.yml -o rule.spl
sigma convert -t microsoft365defender rule.yml -o rule.kql
sigma convert -t elastic rule.yml -o rule.json

# YARA → MISP
python3 -c "
import yara, json
rules = yara.compile(filepath='detection.yar')
# 提取 metadata
"

# STIX2 ↔ MISP
# MISP 自带导出 STIX2
# OpenCTI 自带导入 STIX2

# 通用工具
ioc-parser sample-report.pdf > iocs.json                    # 从 PDF 报告自动提 IOC
iocextract -t < report.txt
iocsearcher -i report.txt -t hash domain ip

# CyberChef recipe 一键转换
# https://gchq.github.io/CyberChef/

# Pandoc：报告 markdown → docx / pdf / html
pandoc report.md -o report.docx
pandoc report.md -o report.pdf --pdf-engine=xelatex
pandoc report.md -o report.html --self-contained --css=style.css
```

## 时间线生成

```bash
# Plaso / log2timeline: 超级时间线工具
log2timeline.py timeline.plaso /mnt/evidence/
psort.py -o l2tcsv timeline.plaso > timeline.csv
psort.py -o json timeline.plaso > timeline.json

# 自家时间线（python）
python3 - <<'PY'
import json
events = []
events.append({'ts': '2026-04-15T09:00:00Z', 'src': 'email', 'desc': 'Phishing email received', 'user': 'alice'})
events.append({'ts': '2026-04-15T09:01:23Z', 'src': 'sysmon', 'desc': 'WINWORD.EXE -> powershell.exe -enc ...', 'host': 'WS01', 'sysmon_id': 1})
events.append({'ts': '2026-04-15T09:01:45Z', 'src': 'firewall', 'desc': 'WS01 → 1.2.3.4:443 (HTTPS, JA3=abc...)', 'host': 'WS01'})
events.sort(key=lambda e: e['ts'])
for e in events:
    print(f"{e['ts']}  [{e['src']:10s}]  {e['desc']}")
PY

# Mermaid sequence diagram
cat > timeline.mmd <<'EOF'
sequenceDiagram
    participant U as User (Alice)
    participant E as Email
    participant W as WS01
    participant C as C2 (1.2.3.4)
    E->>U: Phishing email
    U->>W: Open attachment
    W->>W: WINWORD spawn powershell
    W->>C: POST /api/v1/checkin
    C->>W: stage2 (encrypted)
    W->>W: VirtualAllocEx + WriteProcessMemory
    W->>W: CreateRemoteThread (lsass.exe)
EOF
mmdc -i timeline.mmd -o timeline.svg
```

## 流程 / 架构图

```bash
# Mermaid (Markdown 友好)
cat > arch.mmd <<'EOF'
flowchart TD
    A[Phishing Email] --> B[WINWORD.EXE]
    B --> C[macro.vba]
    C --> D[powershell -enc ...]
    D --> E{decode}
    E -->|stage1| F[loader.dll<br/>VirtualAlloc + CreateThread]
    F --> G[stage2 from C2]
    G --> H[Beacon @1.2.3.4]
    H -.persistence.-> I[Registry Run key]
    H -.lateral.-> J[SMB to WS02]
EOF

# drawio (复杂图)
# 在线 https://app.diagrams.net/ 或本地 desktop 版
# 导出 SVG / PNG，引用到报告

# Graphviz
cat > callgraph.dot <<'EOF'
digraph G {
    main -> init;
    init -> load_config;
    init -> connect_c2;
    connect_c2 -> http_post -> tls_negotiate;
    main -> command_loop -> handle_cmd;
    handle_cmd -> exec_shell;
    handle_cmd -> file_exfil;
}
EOF
dot -Tsvg callgraph.dot > callgraph.svg

# IDA / Ghidra 自带 call graph → 右键 export → SVG
```

## 报告写作风格

```text
1) 一段写一件事
   - 别把"发现 + 证据 + 影响 + 推荐"挤一段
   - 标题分明，可单独引用

2) 主动语态，过去时
   - "loader 在 0x401234 处调用 VirtualAllocEx 分配 RWX 内存"
   - 不要: "可能会被分配..."

3) 数字 / 路径 / hash 一定要完整
   - 不要 "abc..." (除非空间不够) → 全 hash 在脚注 / 表
   - 不要 "register key" → HKCU\Software\...

4) 不确定的标注出来
   - "推断为 XYZ 家族 (基于 imphash + 5 处字符串匹配)"
   - "未能复现 stage3 (条件触发)"

5) 不放未证实的猜测
   - "C2 在俄罗斯" → 改 "C2 IP 1.2.3.4 (ASN 12345, 注册地 RU)"

6) 截图要打码
   - 客户环境 IP / hostname / 用户名脱敏（仅在交付到外部时）

7) 同一份报告两个版本
   - Executive (1 页, 给管理层)
   - Technical (全量, 给分析师 / SOC)

8) 版本号 + 日期 + 作者 + classification 必备
   v1.0 — 初版
   v1.1 — 加 stage3 复现细节
   v2.0 — 重大修订
```

## 渲染工具链

```bash
# Markdown → Word / PDF / HTML
pandoc report.md -o report.docx \
    --reference-doc=template.docx \
    --toc \
    --number-sections

pandoc report.md -o report.pdf \
    --pdf-engine=xelatex \
    --template=template.tex \
    -V mainfont="Helvetica" \
    -V geometry:margin=2cm \
    --toc

# Markdown → HTML 自包含（邮件 / 网页发布）
pandoc report.md -o report.html \
    --self-contained \
    --css=style.css \
    --metadata title="Report XYZ"

# Mermaid 嵌入: 安装 mermaid-filter
npm install -g mermaid-filter
pandoc report.md --filter mermaid-filter -o report.pdf

# 带代码高亮
pandoc report.md -o report.pdf --highlight-style=pygments

# 出版级排版：Typst (现代 LaTeX 替代)
typst compile report.typ

# 报告模板仓库:
# - https://github.com/cdown/report-template (LaTeX)
# - https://github.com/DFIR-IRIS/iris-templates
# - Mandiant FLARE 公开报告（学习风格）

# 团队 wiki:
# Confluence / GitLab Wiki / Notion / Obsidian
# Markdown → Confluence: mark + pandoc + atlassian-cli

# 红色团队风格: drawio + dark theme PDF
```

## 客户交付

```bash
# PGP 加密
gpg --encrypt --recipient client@example.com report.zip
# 或对称加密
gpg --symmetric --cipher-algo AES256 report.zip
# 客户拿到 .gpg → gpg --decrypt 即可

# Age (现代 PGP 替代)
age --recipients-file public-keys.txt -o report.zip.age report.zip
age --decrypt -i client.key report.zip.age

# 一次性传输服务
# OneTimeSecret / PrivateBin / Hat.sh
# 自托管: cryptpad / sendix

# 团队 SOC 平台:
# DFIR-IRIS                     开源, MISP/TheHive 兼容
# Atlassian Confluence + Jira
# Splunk Mission Control

# 文档版本控制
git init reports/
git add report.md
git commit -m "Initial report XYZ"
git lfs install                                              # 大附件用 LFS
git lfs track "*.pcap" "*.zip" "*.mem"
```

## 团队评审 / 同行复核

```text
报告交付前必须：
1) 内部同行复核 (peer review)
   - 至少 1 个独立分析师跑一遍证据
   - 重点检查：hash 一致 / 命令可复现 / IOC 不假阳性
2) Devil's advocate
   - 问 "我怎么证伪这个结论？"
   - 列出所有"不确定" / "限制"
3) 引用 + 参考
   - 类似家族报告 / CVE / 公开 writeup
4) Sanity check
   - 时间线一致 (timezone 标 UTC)
   - IOC 转格式后仍正确
   - 截图 / 反汇编 readable

模板 PR review checklist (GitLab MR / GitHub PR):
- [ ] 执行摘要 1-2 段
- [ ] 范围明确
- [ ] 样本身份完整
- [ ] 关键发现 ≥ 3 条 + 证据指针
- [ ] ATT&CK 映射完整
- [ ] IOC 多格式 (YARA + Sigma + STIX2)
- [ ] 时间线
- [ ] 复现脚本可跑
- [ ] 限制 / 不确定项列出
- [ ] 参考资料
- [ ] 工具版本
- [ ] 评审人签字
```

## 公开报告参考样本

```text
学习同行报告的"风格 + 深度 + 排版":

Mandiant FLARE blog:
  https://www.mandiant.com/resources/blog
  - 排版精良, 反汇编截图丰富, ATT&CK 标准
  - 适合学"企业级"报告

The DFIR Report:
  https://thedfirreport.com
  - 真实事件 + 完整 IOC + 命令链
  - 适合学"事件复盘"

Microsoft Threat Intelligence:
  https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence
  - 与 KQL / Defender 联动

SentinelLABS:
  https://www.sentinelone.com/labs/

Talos:
  https://blog.talosintelligence.com

Securelist (Kaspersky GReAT):
  https://securelist.com
  - APT 跟踪 + 长期家族画像

ESET WeLiveSecurity:
  https://www.welivesecurity.com

CheckPoint Research:
  https://research.checkpoint.com

CrowdStrike OverWatch:
  https://www.crowdstrike.com/blog
```

## 实战入口

- **Mandiant FLARE / The DFIR Report / SentinelLABS**：风格标杆。
- **SANS FOR578 (Cyber Threat Intelligence)**：报告方法论。
- **STIX 2.1 + MITRE ATT&CK Navigator + TAXII**：机读格式。
- **Sigma project / Yara-Rules / signature-base**：开源规则源。
- **Pandoc / Typst / drawio / mermaid**：渲染工具链。
- **DFIR-IRIS / TheHive / MISP / OpenCTI**：开源 SOC 平台。
- **NIST SP 800-86 Forensic Guide / RFC 3227 Evidence**：基础规范。
- **awesome-incident-response / awesome-cti GitHub list**。
- **Confluence / Notion / GitLab Wiki 团队模板**。

## 自检（开始写报告前 30 分钟回答）

1. 谁是读者（管理层 / SOC / 客户 / 公开发布）？分多少版本？
2. 分类 / TLP 等级？是否需要脱敏？
3. 关键发现是几条？每条对应几条证据？
4. ATT&CK 映射完整吗？覆盖哪些 tactic？
5. IOC 格式覆盖（YARA / Sigma / STIX2 / Splunk / KQL）？
6. 时间线 + 流程图 + 调用图 用什么工具画？
7. 复现脚本能否在干净 VM 上跑通？
8. 同行复核安排了吗？谁来？
9. 渲染：Markdown → 什么交付格式？
10. 交付方式：PGP / OneTimeSecret / 邮件 / Confluence？

## 相邻技能

- 所有 *rev 技能 — 本技能是上游 / 收口。
- `malrev` / `crashrev` / `memrev` — 给本技能提供原始素材。
- `revauto` — 自动化生成 IOC 与初步报告骨架。
- `revlab` — 报告 reproduction 跑在实验室。
- `diffrev` — 补丁差异类报告。
- `protrev` — 协议字段级证据组织。
- `fmtrev` — 文件格式分析类报告。
- `iotrev` / `fwrev` / `hwrev` / `icsrev` — 设备 / 工控类报告对客户的呈现。
- `cloudrev` — 云上事件报告（含 IAM / API audit log 时间线）。
- `mrev` — 移动 App 审计交付报告。