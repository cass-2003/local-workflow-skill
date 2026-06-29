---
name: iot-reverse-engineering
description: IoT 全链路逆向：device + 通信 (BLE/Zigbee/Z-Wave/LoRa/Thread/Matter/Wi-Fi) + 云 (MQTT/CoAP/HTTP/WebSocket/厂商 IoT 平台) + App 桥（BLE GATT、Wi-Fi 配网、AP 模式）。识别协议栈、抓 broker 流量、从 App 反推命令字、用 nRF Sniffer / Ubertooth / Zigbee2MQTT 抓低功耗协议。配合 fwrev / mrev / protrev / cryptrev 用。
---

# IoT 全链路逆向

## 适用场景

- 智能门锁 / 摄像头 / 灯泡 / 体重秤 / 充电桩 / 智能音箱 等的端到端逆向：设备本身 + 配套 App + 云服务三段一起看。
- 抓 BLE / Zigbee / Z-Wave / LoRa / Thread / Matter 这些低功耗 / 自组网协议。
- 厂商 IoT 平台命令通道：阿里云 Link / 米家 / 涂鸦 / 华为 HiLink / AWS IoT / Azure IoT / Google Cloud IoT 的 MQTT topic 与 payload 还原。
- 自家设备的远程管理协议、OTA 通道、配网协议（SmartConfig / AirKiss / EZ Mode / SoftAP）还原。

## 不适用

- 固件镜像本身的解包 / rootfs 分析 → `fwrev`。
- 移动 App 反编译 / hook → `mrev`。
- 协议字段位级 / 状态机 → `protrev`。
- 物理 PCB / SoC / 故障注入 → `hwrev`。

## 通信栈速查

| 协议 | 频段 / 介质 | 用途 | 抓包硬件 / 软件 |
| --- | --- | --- | --- |
| **Wi-Fi 2.4/5/6** | 2.4/5/6 GHz | 主干 | airodump-ng / wireshark + monitor mode / Pineapple |
| **BLE 4.x/5.x** | 2.4 GHz | 单点 / Mesh | Nordic nRF52840 + nRF Sniffer / Ubertooth / Sniffle (TI CC1352R) / Ellisys Bluetooth |
| **Zigbee 3.0** | 2.4 GHz (802.15.4) | 智能家居 | TI CC2531 + Z2M / Sonoff Zigbee Dongle / Ubiqua Sniffer / Whsniff |
| **Z-Wave** | 868/908/916 MHz | 智能家居（北美/欧洲） | Aeotec Z-Stick + zwave2mqtt / RaZberry / Z-Wave Sniffer |
| **Thread** | 2.4 GHz (802.15.4 IPv6) | Matter 底层 | Nordic nRF / Silabs EFR32 + ot-sniffer / Pyspinel |
| **Matter (CSA)** | 之上跑 Wi-Fi/Thread/Ethernet | 标准化智能家居 | chip-tool / chip-cert / matter-test |
| **LoRa / LoRaWAN** | 433/868/915 MHz | 远距离低功耗 | Heltec LoRa32 / SX127x 模块 / LoRaWAN packet forwarder |
| **Sigfox / NB-IoT / LTE-M** | 蜂窝 | 远距离 | SDR (HackRF/USRP/LimeSDR) + GR-LTE / GR-Sigfox |
| **433 MHz 无线遥控** | ISM 433 | 老款门铃/家电遥控 | RTL-SDR + rtl_433 / Universal Radio Hacker (URH) / Flipper Zero |
| **Sub-GHz 自定义** | 315/433/868/915 | 各种私有 | HackRF + GNU Radio + GQRX / SDR# |
| **NFC** | 13.56 MHz | 门禁卡 / 移动支付 | PN532 / Proxmark3 / Chameleon Mini / ACR122U |
| **RFID 125 kHz** | 125 kHz | 老门禁卡 EM4100/HID | Proxmark3 / RFIDler / Flipper Zero |
| **CAN bus** | 50k - 1Mbps | 车辆 / 工业 | CANtact / SocketCAN + Linux / PCAN-USB |
| **OBD-II** | CAN at 11/29-bit | 车辆诊断 | OBDLink / can-utils |

## App ↔ 设备通信常见模式

```text
1) 直连模式（局域网）
   App → MQTT broker (WiFi router 或设备本身) → Device
   App → HTTP/HTTPS (设备 web 后台 / API)
   App → BLE GATT 直连 (设备作 peripheral)

2) 云中继模式（最常见）
   Device ⇄ TLS+MQTT/Custom ⇄ Cloud broker ⇄ TLS+MQTT/Custom ⇄ App
   命令: app → cloud → device
   状态: device → cloud → app
   端到端"E2E"加密少见，绝大多数厂商在 cloud 透传

3) 混合模式
   局域网时直连，公网时走云
   配网/绑定阶段 BLE，工作阶段 Wi-Fi+MQTT

4) Matter 模式（新趋势）
   设备出厂带证书 + DAC（Device Attestation Cert），
   配网走 BLE → 上 Wi-Fi/Thread → 加入 Matter fabric → mDNS+IPv6
```

## 关键抓包 / hook 命令

### Wi-Fi

```bash
# Linux monitor mode
sudo ip link set wlan0 down
sudo iw wlan0 set type monitor
sudo ip link set wlan0 up
sudo iw wlan0 set channel 6                                # IoT 设备多在 1/6/11
sudo airodump-ng wlan0
sudo wireshark -k -i wlan0

# 加密 Wi-Fi 抓包后解密
# Wireshark: 编辑 → 偏好 → 协议 → IEEE 802.11 → Decryption keys
# 加 wpa-pwd:<psk>:<ssid>，必须抓到 4-way handshake 才能解 unicast
```

### BLE

```bash
# 自家有 BLE 适配器（macOS/Linux）：扫描 + GATT 浏览
hcitool lescan
gatttool -b AA:BB:CC:DD:EE:FF -I
> connect
> primary                                                  # 主服务列表
> characteristics                                          # 特征列表
> char-read-uuid 2a00                                      # 读 Device Name
> char-write-req 0x000c 12345678                           # 写命令

# bluetoothctl（更现代）
bluetoothctl
> scan on
> connect AA:BB:CC:DD:EE:FF
> menu gatt
> list-attributes
> read 0x000c
> write "0x12 0x34"

# 真正抓 BLE 报文（绑定 / 配对 / 数据）：必须用专用 sniffer
# nRF Sniffer for Bluetooth LE (Nordic 官方)
# 1) 烧 nRF52840 dongle 或 dev kit 烧 sniffer 固件
# 2) 装 Wireshark + nRF Sniffer 插件
# 3) 选目标设备 → 自动捕获

# Linux btmon（HCI 层，本机 host ↔ controller，不是 air）
sudo btmon -w /tmp/bt.btsnoop

# Android: 设置 → 开发者 → "启用 Bluetooth HCI 探测日志"
adb pull /sdcard/btsnoop_hci.log
wireshark btsnoop_hci.log

# iOS: PacketLogger.app（XCode Additional Tools 内）
```

### Zigbee

```bash
# CC2531 + zigbee2mqtt + zigbee-herdsman 是最便宜的进入方案
# 抓包: ubertooth-rx / zboss_sniffer / kismet zigbee plugin
sudo zb-sniffer -d /dev/ttyACM0 -c 11 -w zigbee.pcap

# Whsniff (CC2531/CC2538 通用)
whsniff -c 11 > zigbee.pcap

# Wireshark 解密：编辑 → 偏好 → 协议 → ZigBee → Pre-configured keys
# 加入 well-known TC link key: 5A:69:67:42:65:65:41:6C:6C:69:61:6E:63:65:30:39 ("ZigBeeAlliance09")
```

### Z-Wave

```bash
# Aeotec Z-Stick 7 + zwavejs2mqtt
# 或 RaZberry / Z-Wave.Me Sniffer
# 抓 Z-Wave: 需要 Sigma Designs 官方 sniffer (Zniffer) 或 OpenZniffer 改装
```

### LoRa / Sub-GHz

```bash
# RTL-SDR + rtl_433（最便宜）
rtl_433 -G                                                 # 试所有解码器
rtl_433 -f 433.92M -s 250k -A                              # 自动模式分析

# GR-LoRa (GNU Radio)
gr-lora_sdr / gr-lora

# Universal Radio Hacker (URH)
urh                                                         # GUI，最适合还原私有协议
```

### NFC / RFID

```bash
# Proxmark3 (最强工具)
proxmark3 /dev/ttyACM0
> hf search                                                 # 探测高频卡
> hf mf info                                                # MIFARE Classic
> hf mf chk *1 ? d default_keys.dic                         # 默认 key 字典攻击
> hf mf nested 1 0 A FFFFFFFFFFFF                           # nested attack
> hf mf dump                                                # 全 dump
> hf 14a sim t 1 u 11223344                                 # 模拟卡

# libnfc (PN532 廉价方案)
nfc-list
nfc-mfclassic r a u dump.mfd                                # 读 MIFARE Classic
mfoc -O dump.mfd                                            # MIFARE Offline Cracker
```

## 厂商 IoT 平台速识

### MQTT 通用模式

```text
Device → MQTT Broker
  Topic 例:
    /sys/<productKey>/<deviceName>/thing/event/property/post     (阿里云 Link)
    $iothub/twin/PATCH/properties/desired/                        (Azure IoT Hub)
    $aws/things/<thingName>/shadow/update/accepted               (AWS IoT)
    /home/<homeId>/device/<deviceId>/event                        (米家 / 自家)
  Payload: 多数 JSON, 也有 protobuf / cbor / 自家 binary

抓: mosquitto_sub -h broker -t '#' -v
    或 mqtt-explorer / MQTT.fx GUI
TLS 抓: mitmproxy --listen-port 8883 --mode reverse:mqtts://broker:8883
        或 sslsplit + 把设备 CA 替换成自家
```

### 阿里云 Link Kit

```text
Topic 命名: /sys/<PK>/<DN>/thing/...
  /thing/event/property/post           设备上报属性
  /thing/service/property/set          云下发设置
  /thing/service/<id>                  自家服务调用
Payload: JSON, 含 id / version / params / method
设备认证: 三元组 (ProductKey, DeviceName, DeviceSecret) + HMAC-SHA1 mqtt 用户名密码
SDK: Link Kit (C/Java/Python) / open-iot-sdk
逆向: 在固件里 strings | grep ProductKey/DeviceName/DeviceSecret
```

### 米家 / Yeelight

```text
本地协议: UDP 54321 端口（米家协议）
  Header: \x21\x31\x00\x20<token><device_id><stamp> + AES-128-CBC payload
  token: 设备绑定时分发，存储在 ~/.config/miio/...
工具:
  python-miio (`miiocli` CLI)
  Home Assistant xiaomi_miio integration
逆向:
  抓 UDP → 解出 header → 用 token 解 AES → JSON 命令
```

### 涂鸦 IoT (Tuya)

```text
设备本地协议: TCP 6668 (旧) / 类 MQTT
版本: 3.1 / 3.3 / 3.4 / 3.5 (不同加密形态)
工具: tuyapi (Node.js) / tinytuya (Python) / homebridge-tuya
取 localKey: 抓配网过程 / 绕路 https://iot.tuya.com 控制台 / smarthack tools
```

### Matter / CHIP

```bash
# 官方测试工具
chip-tool pairing ble-wifi 0x1234 <ssid> <psk> <pin> <discriminator>
chip-tool onoff toggle 0x1234 1
chip-tool descriptor read parts-list 0x1234 0
# 抓: bluetoothctl + nRF Sniffer 抓 BLE commissioning 阶段
# 工作期: 抓 IPv6 + mDNS（_matter._tcp）
```

## 配网协议识别

```text
SmartConfig (TI/Espressif):
  手机端用 multicast 包，把 SSID/PSK 编码进 IP/端口/长度
  设备在 monitor mode 嗅探，按预设规则解码

AirKiss (微信):
  类似 SmartConfig，编码方式公开
  GitHub: noisyz/airkiss

EZ Mode / EZ-Click (Tuya):
  类 SmartConfig 变体

SoftAP / AP Mode:
  设备临时变 AP（SSID 含设备 ID）
  手机连进去 → HTTP POST /config 发 SSID/PSK
  最简单也最直观，抓包看 plaintext 即可

ESP-Touch v2 / 蓝牙配网 (BLE provisioning):
  通过 BLE 直接传 SSID/PSK
  Espressif 自家 esp-idf 的 wifi_provisioning 组件

Matter Provisioning:
  蓝牙 → SPAKE2+ 鉴权（PIN + discriminator）→ 上 Wi-Fi/Thread
```

## OTA / 固件升级抓取

```bash
# 中间人抓 OTA 包
mitmproxy --mode transparent --listen-port 8080 -s save_ota.py

# save_ota.py：把含 .bin/.fw/.dfu/.zip 的响应保存
from mitmproxy import http
def response(flow: http.HTTPFlow):
    ct = flow.response.headers.get('content-type','')
    if any(s in flow.request.path for s in ['/ota','/firmware','/fw','/upgrade']) or \
       any(ct.startswith(t) for t in ['application/octet-stream','application/zip']):
        path = '/tmp/ota/' + flow.request.path.split('/')[-1]
        open(path, 'wb').write(flow.response.content)

# 或不用 mitmproxy，直接 wireshark + decode-as → 把 HTTP 流重组成文件
# wireshark: File → Export Objects → HTTP

# 厂商 OTA 服务器域名：在固件 strings 里 grep
strings rootfs/usr/sbin/* | grep -E 'http(s)?://.*\.(com|cn|io)' | sort -u
```

## 实战入口

- **OWASP IoTGoat / DamnVulnerableIoT** — 系统化训练。
- **Pwn2Own SOHO Smashup / Pwn2Own Toronto** — 历年 IoT 真实漏洞 writeup。
- **DEFCON IoT Village / IoT Village Capture the Signal**。
- **Black Hat IoT Track / SSTIC IoT papers**。
- **Hak5 Lab + WiFi Pineapple + Bash Bunny + Flipper Zero** — 实物训练硬件。
- **MQTT.box / Insomniac.io / Practical IoT Hacking 书 (No Starch Press)**。

## 自检（拿到一个 IoT 设备 30 分钟内回答）

1. SoC 型号？（Espressif ESP32 / Realtek RTL8710 / Mediatek MT7681 / Beken BK7231 / Nordic nRF52）
2. 通信栈（Wi-Fi only / Wi-Fi+BLE / Zigbee / Thread / Matter / LoRa）？
3. 走哪个云平台（自家 / 阿里 / 涂鸦 / 米家 / 华为 / AWS / Azure）？
4. 配网模式（SmartConfig / AirKiss / SoftAP / BLE provisioning / Matter）？
5. App 与设备主要通过哪条通道？是否走本地 LAN 直连还是必须走云？
6. OTA 服务器域名 + URL 路径 + 是否 TLS + 是否签名？
7. 默认凭据 / 三元组 / 局部 token / 私钥在固件里能否找到？

## 相邻技能

- `fwrev` — 设备固件镜像本身的解包与 rootfs 分析。
- `hwrev` — UART/JTAG/SPI flash 物理直读，eFuse / TEE 边界。
- `mrev` — 配套 App 的反编译 + Frida hook 抓本地协议 / token。
- `protrev` — 协议字段位级、状态机、重放风险。
- `cryptrev` — 设备 ↔ 云的认证（HMAC-SHA1/SHA256、ECDSA、ECDH、SPAKE2+）。
- `cloudrev` — 厂商 IoT 平台 broker / 控制台 / SDK 二进制。
- `linuxrev` — 嵌入式 Linux IoT 设备的运行生态。
- `binrev` — 设备主程序函数级深挖。
- `containerrev` — IoT 边缘容器化趋势（K3s / KubeEdge / Balena）。
- `icsrev` — 工业级 IoT（IIoT）与 SCADA 边界。