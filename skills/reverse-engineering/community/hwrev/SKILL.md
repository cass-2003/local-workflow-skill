---
name: hardware-reverse-engineering
description: 硬件逆向。PCB 走线 / silkscreen 找 UART/JTAG/SWD/SPI/I2C；逻辑分析仪 + 示波器 + 多用表测信号；flash 直读（SPI NOR / NAND / eMMC）；JTAG/SWD 调试与 dump；故障注入（voltage/clock/EM glitch）；侧信道（DPA/SPA/EMA）；CAN/LIN/USB/HDMI 总线分析；芯片去封装、X-ray、激光显微。
---

# 硬件逆向

## 适用场景

- 拿到一块设备 / PCB，要回答："SoC 是什么？UART/JTAG 在哪几个 pad？SPI flash 是哪一颗？能不能直接夹取读出固件？"
- bootloader 锁死、固件加密、Secure Boot 启用 → 用硬件层介入：故障注入、glitch、cold boot attack。
- USB / CAN / I2C / SPI / 串口设备的总线协议还原。
- 智能卡 / 安全芯片 / TPM / TrustZone 的物理攻击面研究。

## 不适用

- 拿到固件镜像后的解包 / rootfs 分析 → `fwrev`。
- IoT 协议栈 / 配网 / 云通信 → `iotrev`。
- 工控 PLC / RTU 协议 → `icsrev`。

## PCB 走查清单

```text
1) 大芯片 (SoC / MCU)
   - 看丝印型号 → datasheet
   - 看封装 (BGA / QFN / QFP / TSSOP) → 决定能否手焊
   - 看周边电容 (decoupling) 与晶振 → 主频判断

2) Flash 颗粒
   - SPI NOR (8/16-pin SOIC, WSON, USON)
     型号: W25Q128 / MX25L256 / GD25Q128 / EN25 / IS25 (容量 = 名字数字 / 8)
     夹取: SOIC8 test clip + Pomona 5250 + flashrom
   - SPI NAND (8/16-pin)
     型号: GD5F / W25N / MX35
     必须用支持 SPI NAND 的工具 (flashrom 不直接支持，要 OpenOCD/proxmark/特定工具)
   - eMMC (153 / 169 BGA)
     需要拆下或飞线到 eMMC adapter (e.g. EasyJTAG)
   - UFS (新手机)
     更难，需要专用 UFS 编程器

3) 调试口
   - UART: 通常 4 pin (VCC GND TX RX) 或 3 pin (TX RX GND)，丝印 J1/J2/J3/CON1/CN1
   - JTAG: 4 pin TDI TDO TMS TCK + RST + VCC GND，常见 ARM 20-pin / 14-pin / 10-pin
   - SWD: 2 pin (SWDIO + SWCLK) + RST + VCC GND，比 JTAG 紧凑
   - 见到 4 个等距 pad 排成一行 = 大概率 UART
   - 见到 6/10/20 个 pad 矩阵 = JTAG/SWD

4) 测试点 (TP)
   - 以 TPxx / TVxx 标
   - 量产测试用，但常常映射到关键信号 (Boot mode, Reset, BOOT_SEL)

5) 跳线 / Jumper / DIP
   - 常用于切换 Boot mode / Recovery / Factory test
```

## 万用表 / 示波器 / 逻辑分析仪基础

```text
万用表 (multimeter):
  电压档: 量 VCC (3.3V / 5V / 1.8V / 12V), GND
  通断档: 找 GND 网络 (一片大铜地)，找走线连接
  二极管档: 测 LED, 寻找 ESD diode 反向

示波器 (oscilloscope):
  必备双通道 100MHz+ (Rigol DS1054Z, Siglent SDS1104X-E)
  量 UART 波形 → 知道 baudrate (一个 bit 时长 1/baud)
  量 SPI clock → 频率 = 时钟速率 (常 10-50 MHz)
  量 reset 沿 → 启动序列时序

逻辑分析仪 (logic analyzer):
  Saleae Logic Pro 8 / 16 (商业, 100 MHz+)
  Kingst LA1010 / DSLogic Plus / DSCope (国产平价)
  HP/Saleae 配 PulseView (sigrok 开源软件)
  必能解 UART / SPI / I2C / SWD / JTAG / 1-Wire / CAN / Manchester
```

## UART 工作流（最常见的入口）

```bash
# 1) 用万用表找 GND
# 2) 通电，量每个候选 pad 对 GND 的电压
#    - VCC: 稳定 3.3 / 1.8 / 5
#    - TX: 上电瞬间有跳动 (设备发启动 log) 后 idle 高
#    - RX: idle 高 (上拉)，无跳动
#    - GND: 0
# 3) 用逻辑分析仪 / 示波器抓 TX 波形测 baudrate
sigrok-cli -d fx2lafw -O srzip --time 5s -o uart.sr
pulseview                                                  # 装 UART decoder, 看出 baud=115200

# 4) 用 USB-TTL 串口 (CP2102 / FTDI / CH340) 接到 TX/RX
# 跳线方向: 设备 TX → 串口 RX, 设备 RX → 串口 TX, GND ↔ GND, VCC 别接 (除非确定)
sudo apt install minicom screen picocom
picocom -b 115200 /dev/ttyUSB0
screen /dev/ttyUSB0 115200
minicom -D /dev/ttyUSB0 -b 115200

# 拿到 shell 后 (常见: 上电时按某键打断 U-Boot 进入 prompt)
=> printenv                                                # U-Boot 环境
=> setenv bootargs 'console=ttyS0,115200 init=/bin/sh'
=> bootm 0x80000000                                        # 引导带 init=/bin/sh

# Linux shell 拿到后导固件
cat /proc/mtd
dd if=/dev/mtd0 of=/tmp/mtd0.bin bs=1024
# 通过 tftp / ymodem 传出
```

## SPI Flash 直读

```bash
# 硬件: CH341A (廉价, 5 USD), 或 Pomona 5250 + flashrom + Bus Pirate / Buspirate / Raspberry Pi 自带 GPIO

# CH341A + flashrom (USB programmer)
flashrom -p ch341a_spi -r dump.bin                          # 读
flashrom -p ch341a_spi -V -r dump.bin                       # 详细模式
flashrom -p ch341a_spi -c W25Q128.V -r dump.bin             # 强制芯片型号
flashrom -p ch341a_spi -w new.bin                           # 写
flashrom -p ch341a_spi -E                                   # 擦
flashrom -p ch341a_spi --layout layout.txt -i bootloader -r boot.bin   # 按区域

# Bus Pirate
flashrom -p buspirate_spi:dev=/dev/ttyUSB0,spispeed=2M -r dump.bin

# Raspberry Pi (GPIO 直接驱动 SPI)
flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=4000 -r dump.bin

# 在线读 (in-circuit, 不拆): 须断电或保持 SoC 在 reset，否则 SoC 与编程器抢 SPI 总线
# 离线读: 拆下来夹 / 用 SOIC8 转接座
```

读完做完整性校验：

```bash
sha256sum dump.bin
file dump.bin                                              # 应为"data"，因为是 raw flash dump
binwalk dump.bin                                           # 找 U-Boot / SquashFS / kernel
```

## NAND / eMMC / UFS

```text
SPI NAND:
  比 NOR 大、便宜，但需要 ECC + bad block 管理
  flashrom 不直接支持; 用 OpenOCD / proxmark3 / SP127 / 厂商工具
  软件 ECC / 硬件 ECC 取决于 SoC; 抓的 raw dump 要去 OOB + 用 ECC 校正

eMMC (5.x, 153/169 BGA):
  在板上 in-system: 用 SDIO/eMMC adapter 飞线到 SD 接口
  专业: EasyJTAG / Riff / Z3X eMMC + UFI box
  也可: 拆 + 直接放 eMMC reader (e.g. SD 转 eMMC adapter 或专用编程器)

UFS (手机新一代):
  更难，需要专用 UFS programmer (e.g. Medusa Pro II)
  接口 = 高速 串行差分对，焊接 BGA 153 ball 难度大

flash dump 拿到后:
  raw NAND: 先去 ECC + OOB → 再 binwalk
  eMMC raw block: 通常带 GPT / MBR 分区表，按 partition split 后单独分析
```

## JTAG / SWD

```bash
# OpenOCD（开源最强）
openocd -f interface/jlink.cfg -f target/stm32f4x.cfg
# 或自己写配置:
openocd -f /tmp/myboard.cfg
# 进 telnet
telnet 127.0.0.1 4444
> halt
> reg
> mdw 0x08000000 16
> dump_image flash.bin 0x08000000 0x100000
> flash erase_address 0x08000000 0x10000
> flash write_image new.bin 0x08000000

# Black Magic Probe (BMP)
gdb -ex 'target extended-remote /dev/ttyACM0' -ex 'monitor swdp_scan' \
    -ex 'attach 1' -ex 'monitor erase_mass' fw.elf

# JTAGulator: 自动找 TDI/TDO/TMS/TCK
# 接 JTAGulator 24 channel 到候选 pad 阵列, 它会枚举找 JTAG 拓扑

# Glasgow (适合 SPI/I2C/JTAG/UART 一机多能, 开源硬件)
glasgow run jtag-pinout
glasgow run jtag-svf -- read.svf

# SAM-BA (Atmel/Microchip 原厂自带 ROM bootloader 协议)
sam-ba -p serial:/dev/ttyACM0 -d at91sam9x60 -a sdmmc::read:0:0:1024:dump.bin
```

## 故障注入 (Glitch)

```text
原理: 在 SoC 关键运算周期，注入电源毛刺 / 时钟毛刺，让某条指令"跳过"或"失败"
       常用于绕过签名校验、绕开 PIN 校验、把 0 比成非 0

电源毛刺 (Voltage Fault Injection, VFI):
  把 VCC 在纳秒级拉低/拉高，让 CPU 当前周期出错
  硬件: ChipShouter (商业) / ChipWhisperer (开源, NewAE) / MEAVR-Glitcher / PicoEMP

时钟毛刺 (Clock Glitch):
  在外部时钟输入注入额外脉冲，CPU 来不及完成指令
  仅当 SoC 用外部时钟时有效（很多现代 SoC 用内部 PLL，要换 EM/voltage）

EM 故障注入 (EMFI):
  用磁场探针在 die 表面快速变化
  ChipShouter / NewAE EMFI Transient Probe

Laser Fault Injection:
  实验室级，去封装后激光打在 die 特定位置
  极少在攻击实操，多在芯片厂自家测试 / 学术研究

ChipWhisperer 入门工作流:
  1) 准备目标 (Atmega328 / STM32 / Cortex-M0 / RISC-V)
  2) 写 victim firmware: 含 PIN 校验或签名校验
  3) 录"洁净"trace + "胜利"trace, 找触发点
  4) 在 ChipWhisperer Capture 软件里 sweep glitch_offset / glitch_width
  5) 找到能让校验"成功"的窗口 → 自动重放
```

## 侧信道分析 (Side-Channel Analysis)

```text
SPA (Simple Power Analysis):
  量 VCC 上电流瞬时变化, 直接看 RSA / DES / AES 的轮次时间差
  乘法 vs 平方 在 RSA 里耗时不同, 可推 secret bits

DPA (Differential Power Analysis):
  采集大量 trace + 不同输入, 统计分析 (Hamming weight / distance) 找 key
  需要: 高精度示波器 (1 GS/s+) + 数千组 trace + 信号处理

EMA (EM Side Channel):
  类似 DPA, 但用 EM 探头量 die 附近磁场, 不需要接电源
  非接触, 适合 secure element / smartcard

CPA (Correlation Power Analysis):
  DPA 的现代版本, 用 Pearson correlation
  ChipWhisperer 自带 CPA template 攻击, 标准 AES 一键过

工具:
  ChipWhisperer (NewAE 开源 + Pro 版)
  Riscure Inspector (商业)
  PicoScope + Python + scared / lascar (开源 SCA 库)
  Jasmin (formal proofs against SCA)
```

## CAN / OBD / 车载

```bash
# 装 socketcan + can-utils
sudo modprobe can vcan
sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0

# 真实硬件: CANtact (FTDI USB-CAN) / PCAN-USB / Innomaker USB2CAN
sudo ip link set up can0 type can bitrate 500000           # 500k 是车 CAN-C 速度

# 抓 / 重放 / 注入
candump -tA -x can0
cansniffer can0
cansend can0 7DF#0201050000000000                          # OBD-II PID 0x05 = 冷却液温度
canplayer -I trace.log

# OBD-II PID 解码
ELM327 over USB → AT 命令 (cmd: ATZ; ATSP6; 0100; 010C ...)
python-OBD / pyOBD GUI

# 车厂自家协议常用: UDS (ISO 14229) on CAN/CAN-FD
# 抓 -> 看 7E0 / 7E8 等 ID, payload 第一字节 0x10/0x21/0x22/0x27 是 service ID
```

## USB / I2C / SPI 总线分析

```bash
# USB
sudo modprobe usbmon                                       # Linux 自带 USB sniff
sudo wireshark -k -i usbmon0                                # 选 USB 接口

# Wireshark 也可以解 USB HID / Mass Storage / CDC ACM / Audio class

# 老路: USB Sniffer (Beagle USB 12/480, Total Phase) 物理在线
# 廉价: USBPcap on Windows / Wireshark + USBPcap

# I2C 抓
sudo apt install i2c-tools sigrok-cli pulseview
i2cdetect -y 1                                             # Raspberry Pi I2C-1 总线扫描
i2cget / i2cset / i2cdump
# 逻辑分析仪 + sigrok i2c decoder 直接看波形 → 解出地址 + 数据

# SPI 抓 (logic analyzer + sigrok spi decoder)
# Bus Pirate 自带 SPI sniffing 模式
```

## 实战入口

- **Hardware Hacking Handbook (No Starch Press)** — 最系统的教材。
- **NewAE / ChipWhisperer** — 入门到精通的故障注入与 SCA 训练板 + tutorials。
- **wrongbaud's blog** — 大量真实硬件逆向 writeup（路由器、玩具、键盘）。
- **DEFCON Hardware Hacking Village** — 现场训练。
- **JTAG Explained / Hardware Hacker / Andrew "bunnie" Huang** — 经典文献。
- **microcorruption.com** — MSP430 嵌入式 CTF。
- **Hack The Box hardware machines / picoCTF Embedded** — 在线训练。
- **Flipper Zero + Marauder + ESP32 + RTL-SDR + HackRF + Proxmark3** — 入门套件。

## 自检（拿到一块板子 30 分钟内回答）

1. SoC / MCU 主芯片是哪颗？datasheet 里 boot 选择脚位是什么？
2. flash 是 SPI NOR / NAND / eMMC / 内置？容量？是否能离线读？
3. 候选 UART / JTAG / SWD pad 在哪？baudrate 多少？
4. 调试口是否被锁（fuse / RDP / JTAG disable bit）？
5. 启动 log 里 U-Boot / kernel cmdline 透露了什么（rootfs 分区位置、bootargs）？
6. 是否启用 Secure Boot？验证 chain 走到哪一步？

## 相邻技能

- `fwrev` — 物理读到固件后的解包与文件系统分析。
- `iotrev` — IoT 设备的协议栈、云端、App 联动。
- `icsrev` — 工控 PLC 的硬件 + 协议结合。
- `cryptrev` — DPA/CPA 抓出的 key 验证与算法识别。
- `protrev` — 抓到的 USB / CAN / SPI / I2C 协议字段位级。
- `linuxrev` / `binrev` — 抓到固件后的 ELF 分析。
- `vmrev` — 一些智能卡 / smartcard 内部跑自家 VM。
- `mrev` — 配套手机 App 桥接物理设备的协议。