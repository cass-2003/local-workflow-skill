---
name: reverse-engineering-automation
description: 逆向自动化与批量证据流水线。Ghidra headless / IDAPython batch / Binary Ninja headless / radare2 r2pipe / angr / Triton / qiling Python pipeline；批量 yara/capa/floss/syft + 报告聚合；MISP / TheHive / Cortex / Velociraptor / OpenCTI 集成；CI/CD（GitHub Actions / GitLab CI）集成 trivy/grype/syft/cosign；CAPE/Cuckoo3/IRMA 沙箱编排；ELK/Splunk/ClickHouse 数据后端。
---

# 逆向自动化与批量证据流水线

## 适用场景

- 每天 / 每小时几百几千样本进来，要自动分流 → 自动出报告 → 自动入库。
- CI/CD 集成：每次发版自动对比上一版 + 跑 SBOM + 跑 yara/capa 检测。
- 团队级 SOAR：把单兵的逆向技能（capa/strings/yara）变成自动化 pipeline。
- 大规模历史数据回溯：一条新 YARA 规则要跑过 10TB 样本库。
- 把"逆向"从"个人手艺"变成"工程化产线"。

## 不适用

- 单个样本的人工深入分析 → 各专项技能。
- 实验室 / 沙箱 / 网络基础设施搭建本身 → `revlab`。
- 报告编写规范 → `rev-report`。

## 自动化分析框架速选

| 工具 | 语言 | 强项 |
| --- | --- | --- |
| **Ghidra Headless** | Java / Jython / Python (PyGhidra) | 反编译 + 大型项目 + 多线程 + 免费 |
| **IDAPython batch** | Python | 反编译 + Hex-Rays + 商业级 |
| **Binary Ninja headless** | Python | API 最干净 + 现代 |
| **radare2 / rizin r2pipe** | Python / Go / Node / Rust | 命令式 + 脚本最方便 |
| **angr** | Python | CFG + symbolic execution + decompilation |
| **Triton** | C++/Python | DBA / SE / 路径求解 |
| **qiling** | Python | 模拟跑 binary（含 fw / kernel） |
| **Unicorn** | C/Python/JS | 底层 CPU 模拟 |
| **capa** | Python | ATT&CK 能力枚举 |
| **YARA / YARA-X** | C/Rust | 模式匹配 |
| **floss** | Python | 字符串解码 |
| **syft / grype / trivy** | Go | SBOM / 漏洞扫描 |
| **diaphora / bindiff** | Python / C++ | 版本 diff |

## Ghidra Headless

```bash
# 基本调用
$GHIDRA_HOME/support/analyzeHeadless \
    /tmp/ghidra_proj proj_name \
    -import sample.exe \
    -postScript MyAnalysis.java \
    -scriptPath /path/to/scripts \
    -deleteProject

# 批量分析一个目录
$GHIDRA_HOME/support/analyzeHeadless \
    /tmp/proj proj1 \
    -import /samples/*.exe \
    -postScript ExtractFunctions.java \
    -recursive

# 复用已有项目（不重新分析）
$GHIDRA_HOME/support/analyzeHeadless \
    /tmp/proj proj1 \
    -process sample.exe \
    -postScript MyScript.py \
    -scriptPath ./

# Python 脚本（用 Jython 在 Ghidra 内）
# script.py
from ghidra.program.model.symbol import SymbolType
listing = currentProgram.getListing()
for func in currentProgram.getFunctionManager().getFunctions(True):
    print(func.getName(), hex(func.getEntryPoint().getOffset()))
    decompiler_results = decompile(func)
    print(decompiler_results.getDecompiledFunction().getC())
```

```python
# PyGhidra (现代 Python 接口, Ghidra 11+)
import pyghidra
pyghidra.start()
with pyghidra.open_program('sample.exe') as program:
    fm = program.getFunctionManager()
    for func in fm.getFunctions(True):
        print(func.getName(), func.getBody().getMaxAddress())

# 或 ghidriff (Ghidra diff Python lib)
pip install ghidriff
ghidriff old.exe new.exe -o diff_out/                       # 自动出 HTML 报告
```

## IDAPython batch

```bash
# 命令行启动 IDA + 跑脚本 + 退出
ida -A -B \
    -S"my_script.py" \
    -L"/tmp/ida.log" \
    sample.exe

# -A   autonomous (不弹对话框)
# -B   batch (分析完保存 .idb 退出)
# -S   script
# -L   log

# 9.0+ 用 idat
idat -A -B -S"my_script.py" sample.exe

# 跑完 .idb 已生成，可继续
idat -A -S"another.py" sample.idb
```

```python
# my_script.py
import idaapi, idautils, idc, ida_hexrays
ida_hexrays.init_hexrays_plugin()

# 列所有函数
result = {}
for ea in idautils.Functions():
    name = idc.get_func_name(ea)
    size = idc.get_func_attr(ea, idc.FUNCATTR_END) - ea
    
    # 反编译
    func = ida_funcs.get_func(ea)
    if func:
        cfunc = ida_hexrays.decompile(ea)
        if cfunc:
            result[name] = {
                'ea': hex(ea),
                'size': size,
                'pseudo': str(cfunc),
            }

import json
with open('/tmp/funcs.json', 'w') as f:
    json.dump(result, f, indent=2)

idc.qexit(0)
```

## Binary Ninja headless

```python
import binaryninja as bn

with bn.load('sample.exe') as bv:
    bv.update_analysis_and_wait()
    
    for func in bv.functions:
        # 反编译到伪 C
        print(func.name, hex(func.start))
        for block in func.high_level_il:
            for il in block:
                print(f"  {il}")
        
        # 调用图
        print("  callees:", [c.name for c in func.callees])
        print("  callers:", [c.name for c in func.callers])
    
    # 字符串
    for s in bv.strings:
        print(s.value)
    
    # 跨引用
    for ref in bv.get_code_refs(0x401000):
        print(hex(ref.address))
```

## radare2 / rizin r2pipe

```python
import r2pipe
r2 = r2pipe.open('sample.exe', flags=['-2'])                # -2 关错误输出
r2.cmd('aaa')                                               # 全分析
funcs = r2.cmdj('aflj')                                     # 函数列表 JSON
for f in funcs:
    print(f['name'], hex(f['offset']), f['size'])
    # 反汇编
    disasm = r2.cmdj(f'pdfj @ {f["offset"]}')
    for op in disasm['ops']:
        print(f"  {hex(op['offset'])}  {op.get('opcode','?')}")
    # Pseudo C (rizin 自带)
    pdc = r2.cmd(f'pdc @ {f["offset"]}')
    print(pdc)
r2.quit()

# rizin 同 API（rzpipe）
import rzpipe
rz = rzpipe.open('sample.exe')
rz.cmd('aaaa')
```

## angr + Triton + qiling

```python
# angr CFG + 符号执行
import angr
proj = angr.Project('sample.exe', auto_load_libs=False)
cfg = proj.analyses.CFGFast()
print(f"functions: {len(cfg.kb.functions)}")

# 找目标地址
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
simgr.explore(find=0x401234, avoid=[0x401500])
if simgr.found:
    print(simgr.found[0].posix.dumps(0))                    # 解出的输入

# Triton DBA
from triton import TritonContext, ARCH, MemoryAccess, CPUSIZE, Instruction
ctx = TritonContext(ARCH.X86_64)
inst = Instruction(b'\x48\x89\xc1', 'mov rcx, rax')
ctx.processing(inst)
print(inst)

# qiling 模拟跑 binary
from qiling import Qiling
ql = Qiling(['sample.exe'], 'win_rootfs/')
def hook(ql, addr, size):
    print(f"exec {addr:#x}")
ql.hook_code(hook)
ql.run()
```

## 批量画像流水线（capa + yara + floss + syft + strings）

```bash
#!/bin/bash
# pipeline.sh - 单样本 ~ 5-10 秒
sample=$1
out=$(mktemp -d)

sha=$(sha256sum "$sample" | cut -d' ' -f1)

# 1) 基本元数据
file "$sample" > $out/file.txt
exiftool -j "$sample" > $out/exif.json

# 2) YARA
yara-x scan -r ~/yara-rules "$sample" -o "$out/yara.json"

# 3) capa
capa "$sample" -j > $out/capa.json

# 4) floss (字符串解码)
floss --format json "$sample" > $out/floss.json 2>/dev/null

# 5) strings (raw)
strings -a -el "$sample" | sort -u > $out/strings.txt

# 6) SBOM
syft "$sample" -o cyclonedx-json > $out/sbom.json 2>/dev/null

# 7) PE / ELF / Mach-O 元数据
python3 -c "
import json, sys
try:
    import pefile
    pe = pefile.PE('$sample')
    meta = {
        'imphash': pe.get_imphash(),
        'timestamp': hex(pe.FILE_HEADER.TimeDateStamp),
        'sections': [{'name': s.Name.decode(errors='ignore').strip('\\x00'),
                       'entropy': s.get_entropy()} for s in pe.sections],
    }
    print(json.dumps(meta))
except: pass
" > $out/pe.json

# 8) ssdeep / tlsh
ssdeep -b "$sample" > $out/ssdeep.txt
tlsh "$sample" > $out/tlsh.txt 2>/dev/null

# 9) 聚合
python3 - <<PY > /var/samples/$sha.json
import json, os
out = '$out'
result = {'sha256': '$sha'}
for f in ('file.txt','exif.json','yara.json','capa.json','floss.json','sbom.json','pe.json','ssdeep.txt','tlsh.txt'):
    p = os.path.join(out, f)
    if os.path.exists(p):
        try:
            if f.endswith('.json'):
                result[f.rsplit('.',1)[0]] = json.load(open(p))
            else:
                result[f.rsplit('.',1)[0]] = open(p).read().strip()
        except: pass
print(json.dumps(result, indent=2))
PY

rm -rf $out
echo "DONE: /var/samples/$sha.json"
```

## 并行批量分析

```bash
# GNU parallel
ls /samples/*.bin | parallel -j 16 ./pipeline.sh {}

# xargs
ls /samples/*.bin | xargs -P 16 -n 1 ./pipeline.sh

# Python + concurrent.futures
python3 - <<'PY'
import concurrent.futures
import subprocess, glob

def analyze(path):
    return subprocess.run(['./pipeline.sh', path], capture_output=True)

with concurrent.futures.ProcessPoolExecutor(max_workers=16) as ex:
    list(ex.map(analyze, glob.glob('/samples/*.bin')))
PY

# Kafka / RabbitMQ 队列 (生产环境)
# 上游写入 sha256 → Kafka topic
# Worker 池消费 → 分析 → 写下游 topic
```

## 沙箱编排（CAPE / Cuckoo3 / IRMA）

```bash
# CAPE Sandbox REST API
# 装: github.com/kevoreilly/CAPEv2

# 提交样本
curl -X POST 'http://cape:8000/apiv2/tasks/create/file/' \
     -H 'Authorization: Token <api_token>' \
     -F "file=@sample.exe" \
     -F "package=exe" \
     -F "timeout=120" \
     -F "machine=win10"

# 拿任务 ID
# {"task_id": 123}

# 查状态
curl 'http://cape:8000/apiv2/tasks/status/123/' -H 'Authorization: Token <t>'

# 拿报告
curl 'http://cape:8000/apiv2/tasks/get/report/123/' -H 'Authorization: Token <t>' > report.json

# 拿提取的 stage2 / unpacked PE
curl 'http://cape:8000/apiv2/tasks/get/dropped/123/' -H 'Authorization: Token <t>' > dropped.zip

# Cuckoo3 类似（github.com/cuckoosandbox/cuckoo3）

# IRMA (Quarkslab)
curl http://irma:9000/api/v1.1/scans -d '{...}'
```

## MISP / TheHive / Cortex 集成

```python
# MISP: IOC 共享
from pymisp import PyMISP, MISPEvent, MISPAttribute

misp = PyMISP('https://misp.example.com', 'API_KEY', ssl=False)

ev = MISPEvent()
ev.info = f"Auto analysis of {sha256}"
ev.distribution = 1                                          # community

# 加 attribute
ev.add_attribute('sha256', sha256)
for ip in extract_c2_ips(report):
    ev.add_attribute('ip-dst', ip, comment='C2 from sandbox')
for url in extract_urls(report):
    ev.add_attribute('url', url)
for yara in matched_yara_rules:
    ev.add_attribute('yara', yara)

# 关联到 ATT&CK
for tech in mitre_techniques:
    ev.add_tag(f'mitre-attack-pattern="{tech}"')

misp.add_event(ev)

# TheHive: 事件管理
from thehive4py.api import TheHiveApi
from thehive4py.models import Case, CaseTask, CaseObservable

api = TheHiveApi('https://thehive.example.com', 'API_KEY')
case = Case(title=f"Suspicious sample {sha256[:8]}", tlp=2, severity=2)
r = api.create_case(case)
case_id = r.json()['id']

api.create_case_observable(case_id, CaseObservable(
    dataType='hash', data=sha256, message='SHA256 of sample'))

# Cortex: 自动化分析
# Cortex 可调度多个 analyzer（VirusTotal / abuse.ch / Hybrid Analysis / 自家）
# 在 TheHive 中点 "Run analyzer" → Cortex 跑 → 结果回填
```

## CI/CD 集成（GitHub Actions）

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1) 编译产物
      - run: make release
      
      # 2) SBOM
      - uses: anchore/sbom-action@v0
        with:
          path: ./build/
          format: cyclonedx-json
          output-file: sbom.json

      # 3) 漏洞扫描
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'sarif'
          output: 'trivy.sarif'
      - uses: anchore/grype-action@v3
        with:
          path: ./build/
          output-format: json
          output-file: grype.json

      # 4) Secret 扫描
      - uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}

      # 5) YARA 扫
      - run: |
          docker run --rm -v $PWD:/scan yara-x scan -r /rules /scan/build

      # 6) capa
      - run: |
          curl -L -o capa https://github.com/mandiant/capa/releases/latest/download/capa-linux
          chmod +x capa
          ./capa ./build/myapp -j > capa.json

      # 7) Diff 与上一版本
      - uses: anchore/scan-action@v3
        with:
          path: "./build/"
          fail-build: true

      # 8) 阻挡 critical
      - run: |
          jq -e '.matches | map(select(.vulnerability.severity == "Critical")) | length == 0' grype.json

      # 9) 上传报告
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy.sarif

      # 10) cosign 签名
      - run: cosign sign --key cosign.key ./build/myapp
```

```yaml
# .gitlab-ci.yml 类似
stages: [build, scan]
scan:
  stage: scan
  image: aquasec/trivy
  script:
    - trivy fs --format json -o report.json .
    - syft . -o cyclonedx-json > sbom.json
  artifacts:
    paths: [report.json, sbom.json]
```

## 数据后端 + 索引 + 检索

```bash
# 1) 写入 ElasticSearch
curl -X POST 'http://es:9200/samples/_doc' \
     -H 'Content-Type: application/json' \
     -d @analysis.json

# 2) 大规模: Kafka → Logstash → ES
# 或: Vector / FluentBit → ClickHouse

# 3) ClickHouse （大规模 + 列存）
clickhouse-client --query "
CREATE TABLE samples (
    sha256 String,
    timestamp DateTime,
    imphash String,
    yara_hits Array(String),
    capa_techniques Array(String),
    c2_urls Array(String),
    family String,
    INDEX yara_idx yara_hits TYPE bloom_filter GRANULARITY 1,
    INDEX capa_idx capa_techniques TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree() ORDER BY (timestamp, sha256)
"

clickhouse-client --query "INSERT INTO samples FORMAT JSONEachRow" < analyses.ndjson

# 4) 查询: 找 7 天内所有命中某 YARA 的样本
clickhouse-client --query "
SELECT sha256, family, c2_urls FROM samples
WHERE has(yara_hits, 'CobaltStrike_Beacon') AND timestamp > now() - INTERVAL 7 DAY
"

# 5) Velociraptor: agent-based DFIR 平台 (Rapid7 出品)
# 可作 IOC hunt 平台 + 自动跑 yara 全网终端
velociraptor --config server.config.yaml frontend &
# Web GUI: 创建 hunt → 推规则到 1000+ endpoint → 收结果
```

## 简单 SOAR：自动化决策树

```python
# auto_triage.py
import json
from pymisp import PyMISP

def triage(sample_path):
    report = run_pipeline(sample_path)
    
    # 决策树
    score = 0
    if any(r in report['yara'] for r in ['Ransomware', 'Wiper']):
        score += 100
    if report['capa'].get('host-interaction/process/inject'):
        score += 50
    if report['floss'].get('decoded') and len(report['floss']['decoded']) > 100:
        score += 30
    if report['pe']['entropy'] > 7.5:
        score += 20
    
    if score >= 100:
        # 自动入库 MISP + 告警 Slack
        misp_add(report)
        slack_alert(f"HIGH RISK sample: {report['sha256']}", report)
        # 推全网 EDR hunt
        velociraptor_hunt(yara_rule=generate_yara(report))
    elif score >= 50:
        # 入 TheHive 案件队列
        thehive_create_case(report)
    else:
        # 入 ClickHouse 归档
        clickhouse_insert(report)
    
    return score
```

## 实战入口

- **Mandiant Threat Pursuit VM**：自动化流水线参考栈。
- **MalwareBazaar / abuse.ch / URLhaus / ThreatFox**：免费 IOC feed。
- **TheHive Project / Cortex / MISP**：开源 SOAR 三大件。
- **CAPE Sandbox / Cuckoo3 / IRMA / DRAKVUF**：开源沙箱。
- **Mandiant CAPA + capa-rules**：行为画像规则库。
- **Velociraptor / OSQuery / Fleet**：终端 hunt。
- **Falco / Tetragon / Tracee**：运行时观测。
- **Sigma + sigma-rules / Yara-Rules + signature-base**：开源规则源。
- **The Hive Project 文档 / MISP project docs / OpenCTI docs**。
- **SANS FOR578 Cyber Threat Intelligence**。
- **Hashicorp Vagrant / Terraform / Ansible / Packer**：IaC for lab。

## 自检（搭流水线 30 分钟前回答）

1. 数据量：每天进多少样本？规模决定架构（单机 vs 集群）。
2. 后端选型（ElasticSearch / ClickHouse / PostgreSQL + jsonb）？
3. 沙箱选型（CAPE / Cuckoo3 / VMRay 商业 / DRAKVUF agentless）？
4. SOAR 平台（TheHive / FortiSOAR / Splunk SOAR / 自家）？
5. 规则源（YARA / Sigma / Suricata / 自家）+ 更新机制（cron / Git submodule / Webhook）？
6. IOC 共享（MISP / OpenCTI / 自家上下游）？
7. CI/CD 集成接口（GitHub Actions / GitLab CI / Drone / Jenkins）？
8. 报告交付（HTML / PDF / Confluence / Slack / Email）？

## 相邻技能

- `malrev` — 单个样本画像（流水线的"原子操作"）。
- `binrev` / `linuxrev` / `winrev` / `macrev` — 平台分析。
- `fuzzrev` — 持续 fuzz 集成（OSS-Fuzz / ClusterFuzzLite）。
- `diffrev` — 版本 diff 自动化（CI/CD 中的 patch diffing）。
- `containerrev` — 镜像供应链扫描流水线。
- `cloudrev` — 云上分析平台架构。
- `revlab` — 沙箱与隔离基础设施（流水线跑在它上面）。
- `rev-report` — 报告交付规范。
- `protrev` — 抓包流量的自动化解析与入库。
- `iotrev` / `fwrev` — 固件批量扫描流水线。