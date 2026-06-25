---
name: firmware-reverse-engineering
description: 固件与 IoT 固件逆向。识别 raw flash dump / U-Boot uImage / SquashFS / JFFS2 / UBI / CramFS / yaffs2 / cpio rootfs；用 binwalk/unblob 解包；QEMU + Firmadyne 仿真；定位 NVRAM / web 后台 / RPC 服务；ARM/MIPS/PowerPC 嵌入式架构；Bootloader / Secure Boot / TrustZone / TEE 边界识别。配合 binrev / iotrev / hwrev 用。
---

# 固件逆向

## 适用场景

- 拿到一份路由器 / 摄像头 / NAS / 工业网关 / 智能音箱 / 充电桩 / 车机的固件镜像，要回答："里面有什么？rootfs 在哪？默认账号密码？web 后台代码哪一段？哪个二进制起 RPC 服务？"
- 设备购买后的安全自审 / 厂商兼容性研究 / SOHO 路由器漏洞挖掘。
- Bootloader / Secure Boot / TEE 边界识别（OP-TEE、QSEE、TEEGRIS、Apple SEP 之类）。
- 厂商 OTA 包格式还原 + 重打包（自家设备测试用）。

## 不适用

- ELF/PE/Mach-O 函数级深挖 → `binrev`。
- IoT 设备的网络协议字段位级 → `protrev`。
- 硬件 PCB / SoC / glitch / fault injection → `hwrev`。
- 工控 PLC / Modbus / OPC UA → `icsrev`。

## Magic 头速识

```bash
# 一键魔法头识别
file image.bin
xxd image.bin | head -16
binwalk image.bin                              # 列已知签名
unblob image.bin -o extracted/                 # 比 binwalk 现代很多，递归更稳
```

| Magic（hex） | 类型 | 提取工具 |
| --- | --- | --- |
| `27 05 19 56` | U-Boot uImage（含 64-byte 头 + payload） | `dumpimage -i image -p 0 raw.bin` |
| `d0 0d fe ed` | FIT image（Flat Image Tree，新版 U-Boot） | `dumpimage -i fit.itb -p 0 kernel.bin` |
| `73 71 73 68` (`hsqs`) | SquashFS little-endian | `unsquashfs file.sqsh`（旧版用 sasquatch） |
| `73 68 73 71` (`shsq`) | SquashFS big-endian | 同上 |
| `19 85` | JFFS2 | `jffs2dump -c image.jffs2` / mount |
| `55 42 49 23` (`UBI#`) | UBI volume | `ubireader_extract_files image.ubi` |
| `45 3d cd 28` | CramFS | `cramfsck` |
| `1f 8b` | gzip | `gunzip` |
| `42 5a 68` | bzip2 | `bunzip2` |
| `28 b5 2f fd` | zstd | `zstd -d` |
| `fd 37 7a 58 5a 00` | xz / LZMA2 | `unxz` |
| `5d 00 00` | LZMA1 | `lzma -d` |
| `04 22 4d 18` | LZ4 frame | `lz4 -d` |
| `30 37 30 37 30 31` (`070701`) | cpio newc archive | `cpio -idmv < archive.cpio` |
| `cd ab cd ab` | u-boot env | strings 即可读 |
| `ef 53 ` (1024B 偏移) | ext2/3/4 | `mount -o loop` / `e2fsck` |
| `41 4e 44 52 4f 49 44 21` (`ANDROID!`) | Android Boot Image | `unpack_bootimg`（aboot tool） |
| `4d 53 41 47` (`MSAG`) | MediaTek scatter | `mtkclient` |
| `dc dc dc dc` / `b0 0d` | Qualcomm boot | `qcsuper` 系列 |
| `83 03` 头 + LZMA | TP-Link old format | binwalk 自动识别 |
| `2e 73 6e d6` | IBM Power microcode | hpe / ibm-firmware tools |
| `54 4f 43 30 50 4f 30 30` | TOC0 (Allwinner) | `sunxi-tools`（PoC） |

## 全套工具链

| 类别 | 工具 |
| --- | --- |
| **画像 / 拆解** | `binwalk` (经典, 已不维护) / `unblob` (推荐) / `firmware-mod-kit` (老牌) |
| **SquashFS** | `unsquashfs` / `sasquatch`（patched 容错，常用于挂厂商魔改 squashfs） / `squashfs-tools-ng` |
| **UBI / NAND** | `ubireader_*` / `mtd-utils`（nandwrite/nanddump/ubinize/ubidetach） / `ubi_reader` |
| **JFFS2** | `jffs2dump` / `jefferson` |
| **U-Boot** | `dumpimage` / `mkimage` / `u-boot-tools` |
| **bootimg (Android)** | `unpack_bootimg.py` / `magiskboot` / `abootimg` |
| **仿真** | `qemu-system-{arm,aarch64,mips,mipsel,ppc}` / `firmadyne` / `firmae` (改进版) / `Renode` / `Avatar²` |
| **联机 SoC 工具** | `sunxi-tools` (Allwinner) / `mtkclient` (MediaTek) / `edl.py` (Qualcomm EDL) / `nvflash` (Tegra) / `rkdeveloptool` (Rockchip) |
| **NVRAM 读** | `strings` / 厂商专用（MTD partition） / `nvram-faker` (运行时桩) |
| **bootloader 调试** | OpenOCD / J-Link / Black Magic Probe / Glasgow / Saleae |
| **物理读 flash** | `flashrom` (SPI) / `chipprog` / `programmer-x4 SPI Hex` (硬件) / Bus Pirate / TUMPA / RT809 |

## 工作流

### 1. 魔法头扫描 + 递归解包

```bash
# 起手三连
file image.bin
xxd image.bin | head -32
binwalk image.bin

# 现代选择 unblob：递归 + 哈希 + 报告
unblob -d extracted/ image.bin
# 输出: extracted/image.bin_extract/<offset>-<type>/...

# 老路 binwalk: -e 提取 + -M 递归
binwalk -eM image.bin
# 提取目录: _image.bin.extracted/

# 厂商魔改 squashfs（很常见，标准 unsquashfs 报错）
sasquatch -d squashfs-out my.squashfs

# UBI 镜像
ubireader_list_files image.ubi
ubireader_extract_files -o ubifs-out image.ubi

# 单分区
dd if=image.bin of=part1.bin bs=1 skip=$((0x80000)) count=$((0x100000))
```

### 2. 基本画像

```bash
# rootfs 出来后，画像
cd extracted/.../squashfs-root
file bin/busybox bin/sh sbin/init
file lib/libc.so.0           # libc → 知道 toolchain 与 libc 类型 (uClibc/musl/glibc)

# 架构 + 字节序
file usr/sbin/httpd
# 输出例: ELF 32-bit MSB executable, MIPS, MIPS-I version 1 (SYSV)

# CPU info（启动配置中常见）
grep -RhoE 'CONFIG_[A-Z0-9_]+' etc/ | sort -u | head
cat etc/config/cpu_speed   # OpenWrt / 各家变种

# 默认账号密码
cat etc/passwd etc/shadow etc/group
strings -a etc/init.d/* | grep -iE '(pass|admin|root)'
grep -RnE '"(admin|password|root|123)"' usr/

# 启动脚本
ls etc/init.d/
ls etc/rc.d/
cat etc/inittab
ls etc/network/
```

### 3. Web 后台 / RPC 服务定位

```bash
# 大多数路由器 / IoT 都是 web 配置
find . -path '*/www/*' -o -path '*/htdocs/*' -o -path '*/cgi-bin/*' | head
# httpd 的二进制
file usr/sbin/httpd usr/sbin/lighttpd usr/sbin/nginx
# 一般是自家的，含管理面板逻辑
strings usr/sbin/httpd | grep -E '(POST|GET|cgi|admin|login|password)' | head -50

# 常见 URL 路由表关键词
strings usr/sbin/httpd | grep -E 'tplink|netgear|asus|huawei' 
strings usr/sbin/httpd | grep -E '/(api|cgi-bin|goform|hndUnblock|HNAP|webdav)/'

# RPC / 守护进程
ls usr/sbin/ | head
strings usr/sbin/upnpd | head
strings usr/sbin/miniupnpd | head
strings usr/sbin/dropbear  # SSH
```

把找到的 httpd 二进制丢回 `binrev` 做函数级分析（路由表反汇编、命令注入入口、stack/heap overflow 入口）。

### 4. NVRAM / 配置注入

```bash
# 多数厂商把配置写在 MTD 分区，二进制启动时调用 nvram_get / nvram_set
strings usr/sbin/httpd | grep -E '^(wlan|wan|lan|admin|http|ssh|telnet)_'

# 仿真时常见技巧：用 nvram-faker LD_PRELOAD 提供假值
LD_PRELOAD=./nvram-faker.so ./usr/sbin/httpd
```

### 5. 仿真启动

```bash
# 简单：单二进制 chroot 跑（仅静态链接 / glibc 兼容时）
sudo chroot extracted/squashfs-root /bin/sh

# QEMU user-mode（按架构）
sudo cp /usr/bin/qemu-mips-static squashfs-root/usr/bin/
sudo chroot squashfs-root /usr/bin/qemu-mips-static /bin/sh
sudo chroot squashfs-root /usr/bin/qemu-mips-static /usr/sbin/httpd -f /etc/httpd.conf

# QEMU system 模式（完整内核 + rootfs）：用 firmadyne / firmae
git clone https://github.com/pr0v3rbs/FirmAE; cd FirmAE
./run.sh -d MyDevice ../image.bin
# 自动: 抓 root fs → 准备 NVRAM 桩 → 选内核 → 启动 → 保留 web shell

# Renode 跑特定 SoC（无标准 Linux 时也行）
renode renode-resc-script.resc

# Avatar² 把仿真 + 实物联机调试
import avatar2
avatar = Avatar(arch=ARM, output_directory='/tmp/avatar')
target = avatar.add_target(JLinkTarget, name='dut', ...)
target.init()
```

### 6. 抓 OTA / 验签

```bash
# OTA 包通常是: <header><签名><gz/squashfs/ubinize>
# 找头：用 binwalk / 自己写解析
python3 -c '
import struct, sys
with open(sys.argv[1], "rb") as f:
    hdr = f.read(0x100)
    print("magic:", hdr[:4].hex())
    print("size:", struct.unpack("<I", hdr[4:8])[0])
    ...
' ota.bin

# 厂商签名常见
# - RSA-PSS over SHA-256 (PKCS#1 v2.x)
# - ECDSA P-256
# 公钥常嵌入 bootloader 里
strings -el bootloader.bin | grep -iE 'BEGIN PUBLIC KEY|ssh-rsa|-----BEGIN'

# 厂商 root key 哈希常烧到 SoC eFuse / OTP，SoC 直接验 bootloader 签
```

### 7. Bootloader / Secure Boot 链

```text
Cold boot → SoC ROM (写死，bootrom) 
  → 验 bootloader 头部签名（公钥哈希在 eFuse）
       → bootloader (U-Boot / SBL / Aboot / TF-A)
            → 验 kernel + dtb + rootfs hash
                 → kernel 启动
                      → init / systemd / busybox init
                           → 应用层

每一层都可能有 fuse 强制锁定 (Secure Boot enabled)
通过物理调试 (UART, JTAG) 拿 bootloader shell 是常见入口
```

### 8. TEE / Secure World

```text
ARM TrustZone 把 SoC 切两半:
  Normal World: Linux / Android
  Secure World: TEE (Trusted Execution Environment)

常见 TEE:
  OP-TEE         开源参考实现
  QSEE           Qualcomm TEE
  TEEGRIS        Samsung TEE
  Trustonic Kinibi  ARM Trustonic
  Apple SEP / SEPOS  iPhone/Mac 安全协处理器（独立处理器）
  Google Titan M / M2  Pixel 安全芯片

TEE 模块 = TA (Trusted Application)，常见格式:
  OP-TEE: <UUID>.ta (ELF + 头)
  QSEE: .mbn (Qualcomm Multiboot, 含签名头 hashtable)
  TEEGRIS: .tzar
  Apple SEPOS: 独立 Mach-O 在 SEP firmware 里

逆向手段:
  - 抓 TEE 镜像（通常在 OEM image 的某个分区）
  - 解头 → 拿到内部 ELF / 类似格式
  - 反编译: Ghidra/IDA + 自定义 loader（社区有 SEPOS / OPTEE 插件）
```

## 实战入口

- **OWASP IoT Top 10 / OWASP IoT Goat 靶场** — 系统化训练。
- **Damn Vulnerable Router Firmware (DVRF)** — Praetorian 出品的练手镜像。
- **OpenWrt 源码 + 各家 fork** — 大多数 SOHO 设备从这分叉。
- **Firmware Hacking Diaries / FirmaeIoT.io / IoTPenTest 系列博客**。
- **Embedded Security CTF: microcorruption.com** — MSP430 真实嵌入式题。
- **DEFCON IoT Village / Pwn2Own SOHO** — 公开 writeup 与样本。
- **Routersploit / RouterSploit framework** — 已知漏洞 PoC 库，逆向参考。

## 自检（拿到固件 image 30 分钟内回答）

1. 厂商 / 设备型号 / 版本？整体大小？SoC 型号？
2. 文件类型识别：U-Boot uImage / 多分区 raw / OTA 加密包 / FIT image？
3. 解包后 rootfs 在哪？文件系统类型（squashfs/ubifs/jffs2/cramfs）？
4. 架构 / 字节序 / libc / busybox 版本？
5. 默认账号密码（passwd/shadow）？SSH key？默认 wifi 凭据？
6. 主要服务进程（httpd / RPC / upnpd / telnet / SSH）？
7. NVRAM / config 节区位置？厂商私有 utility 入口（如 cgi-bin/goform/...）？
8. 是否带 Secure Boot？bootloader 签名机制？是否能仿真启动？

## 相邻技能

- `binrev` / `asmrev` — rootfs 内 ELF 函数 / 指令深挖。
- `iotrev` — IoT 全链路（设备 + 协议 + 云端）联动。
- `hwrev` — UART/JTAG/SPI 物理调试与 flash 直读。
- `icsrev` — PLC / RTU 工控固件，协议层 Modbus/OPC。
- `cryptrev` — 厂商签名 / OTA 加密 / TLS 客户端实现。
- `protrev` — 厂商私有协议（OTA、配置、远程管理）。
- `containerrev` — IoT 容器化趋势：用 OCI 镜像作为 firmware 分发。
- `linuxrev` — 嵌入式 Linux 内核接口与启动序列。
- `vmrev` — TEE 中间表示 / TA opcode 自家 VM。
- `sdkrev` — IoT SDK 二进制（HiLink / Alink / IoT 平台 SDK）。