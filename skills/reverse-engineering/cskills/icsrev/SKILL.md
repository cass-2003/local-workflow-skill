---
name: ics-ot-reverse-engineering
description: 工业控制系统（ICS / OT / SCADA）逆向。PLC / DCS / RTU / HMI 设备识别、PLC 程序与符号还原（IEC 61131-3 LD/FBD/ST/IL/SFC）、工业协议解析（Modbus / DNP3 / IEC 104 / OPC UA / Profinet / EtherNet/IP / S7Comm / Fox / BACnet）、HMI/SCADA 工程文件（WinCC/RSLogix/CitectSCADA/Wonderware/Ignition）解包、隔离与跳板攻击面识别。
---

# 工控（ICS / OT / SCADA）逆向

## 适用场景

- 工厂 / 电力 / 油气 / 水务 / 制药环境的设备审计：拿到 PLC、HMI、变频器、智能仪表的二进制 / 工程文件 / 流量。
- 抓 / 还原工业协议：Modbus TCP/RTU、DNP3、IEC 60870-5-104、OPC UA、PROFINET IO、EtherNet/IP、S7Comm、Fox、BACnet。
- PLC 程序还原：从工程文件或在线 upload 拿到 LD/FBD/ST/IL/SFC，重建逻辑。
- 工控隔离架构（Purdue Model L0-L5）边界识别与跳板风险。

## 不适用

- 普通 IT 协议（HTTP/TLS/MQTT） → `protrev`。
- 通用 Linux/Windows 二进制 → `binrev` + 平台。
- IoT 智能家居 → `iotrev`。

## 设备生态

| 厂家 | 主力 PLC / DCS | 编程软件 | 协议 |
| --- | --- | --- | --- |
| **Siemens** | S7-200 / 300 / 400 / 1200 / 1500 | TIA Portal / STEP 7 | S7Comm / S7CommPlus / PROFINET / OPC UA |
| **Allen-Bradley (Rockwell)** | ControlLogix / CompactLogix / MicroLogix / SLC 500 | RSLogix 5000 / Studio 5000 | EtherNet/IP (CIP) / DH+ / DF1 |
| **Schneider Electric** | Modicon M340 / M580 / Quantum / Premium | Unity Pro / EcoStruxure Control Expert | Modbus / OPC UA / EtherNet/IP |
| **Mitsubishi** | MELSEC Q / iQ-R / FX | GX Works2 / 3 | MELSEC / SLMP / CC-Link |
| **Omron** | CJ / NJ / NX | CX-Programmer / Sysmac Studio | FINS / EtherNet/IP |
| **ABB** | AC500 / AC800M / Freelance | Automation Builder | Modbus / OPC UA / Profibus |
| **Honeywell** | Experion PKS / TPS / Safety Manager | C300 EHB / Control Builder | Fox / OPC / Modbus |
| **Yokogawa** | CENTUM VP / ProSafe-RS | CENTUM VP Engineering | Vnet/IP / Modbus |
| **Emerson** | DeltaV / Ovation / RX3i | DeltaV Explorer / PME | Foundation Fieldbus / OPC UA |
| **GE / Bachmann** | RX3i / VersaMax / Bachmann M1 | Proficy Machine Edition | SRTP / EGD / Modbus |
| **Beckhoff** | TwinCAT (软 PLC, x86) | TwinCAT 3 | ADS / EtherCAT / Modbus / OPC UA |
| **HMI 主流** | Siemens WinCC / Rockwell FactoryTalk View / Wonderware InTouch / GE iFIX / Schneider Vijeo / Inductive Ignition / 国产组态王 / 力控 / 紫金桥 | — | OPC UA / OPC DA / Modbus / 自家 |

## 工业协议速查

### Modbus

```text
Modbus TCP: 端口 502
  ADU = MBAP(7) + PDU
  MBAP: tx_id(2) + proto_id(2)=0 + length(2) + unit_id(1)
  PDU:  function_code(1) + data
功能码:
  01 Read Coils                  03 Read Holding Registers
  02 Read Discrete Inputs        04 Read Input Registers
  05 Write Single Coil           06 Write Single Register
  0F Write Multiple Coils        10 Write Multiple Registers
  17 Read/Write Multiple         16 Mask Write Register
  2B Encapsulated Interface (Modbus over TCP/MEI)
异常: 功能码高位 1，data[0] = 异常码 (01-0B)
没有内置认证, 完全明文
```

```bash
# 工具
nmap --script modbus-discover -p 502 192.168.1.0/24
mbpoll -1 -m tcp -a 1 -r 1 -c 10 192.168.1.10              # 读 holding registers
modpoll -m tcp -a 1 -r 1 -c 10 -t 4:int 192.168.1.10
python3 -m pymodbus.console tcp --host 192.168.1.10 --port 502
> client.read_holding_registers address=0 count=10 unit=1

# scapy
from scapy.all import *
from scapy.contrib.modbus import *
pkt = IP(dst='192.168.1.10')/TCP(dport=502)/ModbusADURequest()/ModbusPDU03ReadHoldingRegistersRequest(startAddr=0, quantity=10)
sr1(pkt)
```

### S7Comm / S7CommPlus（Siemens）

```text
S7Comm:
  端口 102 (ISO-TSAP / RFC1006), 旧协议 (S7-300/400)
  COTP(连接) → S7Comm(操作)
  function: read/write var, list blocks, upload/download blocks, run/stop CPU
  无内置加密, 但 S7-1200/1500 有 Anti-Replay 计数

S7CommPlus:
  S7-1200 (FW 4+) / S7-1500 默认
  端口 102, 但 PDU 上加了 TLS 风格的握手 + 序列号
  反逆向更严, Wireshark 解析有限
```

```bash
# 工具
plcscan 192.168.1.10                                       # 端口 + 设备识别
snap7 (libnodave 的现代继任者)
python3 -c '
import snap7
client = snap7.client.Client()
client.connect("192.168.1.10", 0, 2)
print(client.get_cpu_info())
print(client.get_cpu_state())
data = client.db_read(1, 0, 32)                            # 读 DB1 偏移 0 长 32
print(data.hex())
'

# Wireshark 解 S7Comm: 内置 dissector
# nmap S7Comm 脚本: nmap --script s7-info -p 102 192.168.1.10
```

### EtherNet/IP (CIP) — Allen-Bradley / Rockwell

```text
端口 44818 (TCP) + 2222 (UDP, IO 实时)
封装协议 + CIP (Common Industrial Protocol)
服务: ListIdentity (出厂识别), ListServices, GetAttributeAll, ReadTag, WriteTag, ForwardOpen
EtherNet/IP 在 IO 实时层用 UDP 多播 (Implicit Messaging)
管理: TCP (Explicit Messaging)
```

```bash
nmap --script enip-info -p 44818 192.168.1.0/24
python3 -m pylogix
```

### DNP3

```text
电力行业标准 (北美), 端口 20000 (TCP/UDP)
分层: Application → Pseudo-Transport → Data Link
功能: Read, Write, Operate (CROB control), Direct operate, Freeze, Cold restart
有 DNP3 Secure Authentication v5 (SAv5) 选项, 但启用率极低
```

### IEC 60870-5-104

```text
电力行业标准 (欧洲/亚洲), 端口 2404
APCI(6) + ASDU
帧类型: I-format (data), S-format (sup), U-format (control: STARTDT/STOPDT/TESTFR)
功能: Single command (C_SC_NA_1, type 45), Setpoint (50/51/52), General Interrogation (100)
```

```bash
# 工具: 60870IEC4Python / iec104-python / Wireshark 自带
python3 -c '
from c104 import Client
c = Client()
station = c.add_station(...)
'
```

### OPC UA (现代标准)

```text
端口 4840 (二进制) / 4843 (HTTPS)
带证书认证 + AES 加密 (可选, 也可不开)
浏览模型: Server → Namespaces → Nodes (Object/Variable/Method)
```

```bash
# 工具
uaexpert (商业, 但有免费版): GUI 浏览
python-opcua / asyncua (Python 客户端)
opcua-client-gui

python3 -c '
from opcua import Client
c = Client("opc.tcp://192.168.1.10:4840")
c.connect()
root = c.get_root_node()
print(root.get_children())
'
```

### PROFINET (Siemens)

```text
PROFINET RT (Real-Time): 以太网帧 EtherType 0x8892, 不带 IP
PROFINET DCP: Discovery and Configuration Protocol, 也是 0x8892
PROFINET IRT: Isochronous, 严格时序

抓: tcpdump ether proto 0x8892
解: Wireshark 自带
扫: profinet-explorer / profinet-discover (DCP 多播)
```

### BACnet（楼宇自控）

```text
端口 47808 (UDP), BVLC 头 + APDU
读 / 写 / 订阅对象
工具: yabe (Yet Another BACnet Explorer) / bacpypes / Wireshark
```

## PLC 工程文件解包

```text
Siemens TIA Portal:
  工程文件: .ap14 / .ap15 / .ap16 (按 TIA 版本)
  内部是 SQLite + zip + 加密 blob
  工具: tia-project-extractor (社区) / 商业工具 ICSDATA / ICS Defender

  STEP 7 (旧 S7-300/400): .s7p 项目, 子目录里 OB1.AWL / FB.SCL 文件 = STL/SCL 源
  AWL → IL (Instruction List)

Rockwell Studio 5000:
  工程文件: .ACD (二进制), 同时可导出 .L5K / .L5X (XML)
  .L5X 是文本: <Tag><Routine>... 直接可读

Schneider Unity Pro:
  工程文件: .stu / .sta (压缩 + 加密)

Inductive Ignition:
  工程文件: .gwbk = zip 内含 sqlite, 直接 unzip + sqlite3 看

WinCC:
  HMI 工程: .mcp / .pcp + Tag.dwm + 各种数据库

Wonderware InTouch:
  工程目录: 多个 .dat / .idx / .bin
  每个 Window 是单独文件
```

## SCADA / HMI 解析

```bash
# WinCC 取 tag 表
strings WinCC.exe | grep -i 'OPC' | head
# WinCC.exe 是基于 .NET, 用 dnSpy / dotPeek 反编译

# RSLogix .L5X (XML 直接看)
xmllint --format MyProject.L5X | head -200
# 提取所有 routine 名称
xmllint --xpath '//Routine/@Name' MyProject.L5X

# Ignition .gwbk
unzip -d ignition_proj backup.gwbk
sqlite3 ignition_proj/db_backup_sqlite.idb '.schema'
```

## Purdue Model 速查（工控架构）

```text
Level 5: Enterprise Network        办公网, ERP / Email
Level 4: Site Business Logistics   办公 / IT 跨边界
─── DMZ (隔离层, Historian, Patch Server, AV/Update) ───
Level 3: Site Operations           工程师站, MES, Asset Mgmt
Level 2: Area Supervisory          HMI, SCADA Server
Level 1: Basic Control             PLC, RTU, IED
Level 0: Process                   传感器, Actuator, Motor

每一层之间应该有防火墙；现实里大量 L3 ↔ L2 ↔ L1 几乎全开。
跳板攻击面常在: Engineering Workstation (L3) 通过 USB / VPN 进入 → S7Comm / EtherNet/IP 直达 PLC
```

## 实战入口

- **Claroty / Dragos / Nozomi Networks blog** — 工控漏洞 / 真实事件分析。
- **ICS-CERT advisories** — `https://www.cisa.gov/news-events/ics-advisories`。
- **S4 Conference / 4SICS / DEFCON ICS Village** — 现场训练。
- **Siemens / Schneider / Rockwell 自家"安全播报"** — PLC 0day patch 公告。
- **OpenPLC + plc4x + ScadaBR** — 自搭练手平台。
- **Hack The Box / TryHackMe ICS / ICS-CTF** — 公开靶场。
- **Industrial Control Systems Joint Working Group (ICSJWG) Workshops**。
- **"Industrial Cybersecurity" by Ackerman / Wireshark for Network Security** — 系统化教材。

## 自检（拿到工控样本 30 分钟内回答）

1. 哪个厂家 / 型号 / 固件版本？编程软件版本？
2. 工程文件能否打开 / 解包 / 反编译为可读 ladder / ST？
3. 设备开了哪些 TCP/UDP 端口？运行哪些工业协议？
4. 是否启用 OPC UA + 证书 + 加密？是否启用 S7CommPlus / DNP3 SAv5？
5. PLC 在 RUN 还是 PROG 模式？是否允许远程 stop / download？
6. 工程师站 / HMI 与 PLC 之间有没有 Network 隔离？防火墙策略？
7. Historian / 数据库 / web HMI 暴露面？默认凭据？

## 相邻技能

- `fwrev` — PLC / RTU / IED 固件镜像本身的解包。
- `protrev` — Modbus / DNP3 / IEC 104 / OPC UA / S7 / EtherNet/IP 字段位级。
- `binrev` — PLC 内部 ELF/PE（多数 PLC 用 ARM/PowerPC + VxWorks/Linux）。
- `vmrev` — 部分 PLC 自家字节码（Rockwell logix 可能含 VM）。
- `cryptrev` — OPC UA / DNP3 SA / S7CommPlus 加密握手。
- `iotrev` — IIoT 边缘网关、MQTT 上云。
- `hwrev` — PLC 物理 UART/JTAG 调试与 flash 提取。
- `linuxrev` / `winrev` — HMI 平台（多 Windows）+ 工程师站。
- `scriptrev` — 工程文件中的 Lua / Python / .NET IL（如 Ignition Jython / Beckhoff TwinCAT.NET）。