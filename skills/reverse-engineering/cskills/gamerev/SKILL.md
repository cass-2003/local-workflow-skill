---
name: game-client-reverse-engineering
description: 游戏客户端与资源逆向防御分析。Unity (Mono / IL2CPP) / Unreal Engine (UE4/5) / Cocos / Godot / 自家引擎；asset bundle / pak / pck 解包；反外挂识别（EAC / BattlEye / Vanguard / TenProtect / NP / Themida 系）；游戏协议与加密；CheatEngine / Frida / 内存补丁 / 网络包还原。
---

# 游戏客户端逆向

## 适用场景

- 游戏厂商：自家做反外挂研究、外挂样本分析、协议加固审计、签名校验加固。
- 测试团队：审计自家 SDK / Anti-Cheat 集成质量、bug 追根（资源没解出来 / 协议丢字段）。
- 蓝队：识别和分析野外外挂样本，提供检测规则。
- 资源还原：合法商业兼容工具（如 mod 工具链）需要解资源格式。

## 不适用

- 服务器端游戏后端 → `binrev` / `linuxrev` / `cloudrev`。
- 移动端游戏（除引擎部分） → `mrev` 主导，本技能配合。
- 网络协议字段位级 → `protrev`。
- 加密算法识别本身 → `cryptrev`。

## 引擎速识

| 引擎 | 入口标志 | 资源 | 脚本 |
| --- | --- | --- | --- |
| **Unity Mono** | `MonoBleedingEdge/` 目录 + `Managed/Assembly-CSharp.dll` + `mono-2.0-bdwgc.dll` | `*.assets` / `*.bundle` / `globalgamemanagers` | C# 编译成 Mono .NET DLL |
| **Unity IL2CPP** | `il2cpp_data/` + `libil2cpp.so` (Android) 或 `GameAssembly.dll` (Win) + `global-metadata.dat` | 同上 | C# 编译成 C++ 再编 native |
| **Unreal Engine 4/5** | `Engine/Binaries/Win64/...exe` + `*.pak` 资源 + `*.uproject` | `.pak` (UE pak) / `.utoc + .ucas` (IoStore, UE 4.27+) | Blueprint (字节码) + C++ |
| **Cocos2d-x C++** | `libcocos2d.so` / `libgame.so` | `.csb` 场景 / `.plist` 动画 / 普通图片音频 | 可选 Lua / JavaScript |
| **Cocos Creator** | `assets/` 目录 + `main.bin` (jsc) | `.bin` 资源包 + `.json` 描述 | JavaScript / TypeScript（编译为 jsc 或 bytecode） |
| **Godot** | 单二进制 + `*.pck` | `.pck` (PackedScene) | GDScript（字节码 .gdc）/ C# |
| **Source / Source 2** | `bin/launcher.dll` + `*.vpk` | `.vpk` Valve Pack | 不同 |
| **id Tech** | 自家 | `.pk3` (zip 改名) | 不同 |
| **CryEngine / Lumberyard** | 自家 | `.pak` + `.cdf` | Lua 自家 |
| **自家引擎（米哈游 / 网易 / 腾讯）** | 看二进制 strings + 工程命名 | 千差万别 | 通常 Lua / Python / 自家 VM |

## 资源解包工具链

### Unity

```bash
# AssetStudio (Mono GUI, 最常用)
# https://github.com/Perfare/AssetStudio
AssetStudio.exe                                   # 拖入 *.assets / *.bundle / *.unity3d

# UABEA (Unity Assets Bundle Extractor Avalonia, 跨平台 GUI)
UABEA.exe

# CLI: AssetStudioCLI / UnityPy
pip install UnityPy
python -c "
import UnityPy
env = UnityPy.load('sharedassets0.assets')
for obj in env.objects:
    if obj.type.name == 'Texture2D':
        data = obj.read()
        data.image.save(f'/tmp/{data.name}.png')
"

# IL2CPP 反编译（Unity 现代默认）
# Il2CppDumper (最常用)
# https://github.com/Perfare/Il2CppDumper
Il2CppDumper.exe libil2cpp.so global-metadata.dat dumped/
# 输出：
# - DummyDll/Assembly-CSharp.dll  → 用 dnSpy / dotPeek 反编译
# - script.json                   → 给 IDA / Ghidra 恢复符号
# - il2cpp.h                      → C 头文件

# IDA + Il2CppDumper.py / il2cpp_header_parser.py 自动还原符号

# Mono Unity（老版本）
dnSpyEx Assembly-CSharp.dll                       # 直接反编译，无任何障碍
ILSpy Assembly-CSharp.dll
```

### Unreal Engine

```bash
# UnrealPak (Epic 自家)
UnrealPak.exe -List target.pak -cryptokeys=keys.json
UnrealPak.exe -Extract target.pak -Output=extracted/

# UModel / UAssetGUI（社区主流）
# https://www.gildor.org/en/projects/umodel
umodel -path=Content/Paks -game=ue5.3 *.uasset    # GUI 浏览 + 导出
umodel -export -path=Content/Paks                  # 批量导

# IoStore (UE 4.27+ 新格式: .utoc + .ucas)
# UnrealPak 新版支持，UModel 也支持

# .uasset / .umap 解析（独立资源文件）
UAssetGUI.exe target.uasset
# CLI: UAssetAPI

# Blueprint 反编译
# 较难，UE 把 Blueprint 编译成 K2Node 字节码 + C++ stub
# 工具: ue4-bp-disassembler / uelogviewer (商业 BP 编辑器)

# AES key 提取（UE 默认 AES-256-ECB 加密 pak）
# 厂商在二进制里硬编码 32 字节 key
strings GameLauncher.exe | grep -aE '[0-9A-Fa-f]{64}' | head      # 找 hex 长度 64
# 或 用 IDA 找 FCoreDelegates::GetPakEncryptionKeyDelegate 的注册处
```

### Cocos Creator

```bash
# 大部分 Cocos Creator 游戏直接是 Web 形态 (HTML5)
# 资源在 assets/ 目录 + main.js (打包后)
# 用 webrev 思路: webcrack / unminify

# 编译过的 Lua/JS bytecode
# Cocos2d-xLua: .luac (LuaJIT 字节码)
luajit -bg -o decompiled.lua input.luac           # 反汇编（不是反编译）
unluac in.luac > out.lua                           # 反编译（仅 Lua 5.1）

# Cocos Creator 3.x 默认 JS bundle，类似 Webpack
```

### Godot

```bash
# Godot pck 解包
gdsdecomp                                          # 社区工具
godotpcktool --action=extract --pack=game.pck

# .gdc 字节码反编译
godot-de-compiler / gdsdecomp 都支持
```

## Anti-Cheat 速识

| AC | 厂家 | 内核驱动 | 检测面 |
| --- | --- | --- | --- |
| **Easy Anti-Cheat (EAC)** | Epic | `EasyAntiCheat.sys` (Win) | 内存扫描、模块完整性、调试器、Hook、CFG 一致性 |
| **BattlEye** | BattlEye Innovations | `BEDaisy.sys` | 类似 EAC，硬件指纹更激进 |
| **Vanguard** | Riot | `vgc.sys` + `vgk.sys`（开机就跑） | TPM / 安全启动 / Ring 0 hook，最严 |
| **TenProtect (TP)** | 腾讯 | TPHelper / TPSafe / NtoskrnlEx | 国服游戏主流 |
| **NetEase Anti-Cheat (NeAC)** | 网易 | `nac.exe` 等 | 国服 |
| **MajieCi 麻吉次 / Hyperion** | RuneScape | 客户端混淆 | JS / .NET 自家 VM |
| **Anti-Cheat Toolkit (Unity Asset Store)** | 第三方 | 用户态 | 内存读保护、时间作弊检测 |
| **Themida + VMProtect** | 通用 | 用户态 | 见 `vmrev` / `packrev` |

```bash
# 系统已装 anti-cheat 检查（Windows）
sc query | findstr /I "anti easy battle vanguard tencent"
driverquery | findstr /I "EasyAntiCheat BEDaisy vgc vgk TPSafe"

# 进程
Get-Process | Where-Object { $_.Name -match 'anti|cheat|battle|vanguard|tp|nac' }

# Linux Wine 跑 EAC：游戏看 /proc/<pid>/status TracerPid + ld.so.preload + libpthread 完整性
```

## 反作弊检测面（看，不绕）

```text
1) 模块完整性
   - 取 .text 段 hash，与首次启动时对比
   - 检测 IAT / EAT 是否被改
   - inline hook (mov reg, imm; jmp reg) 检测：扫前 16 字节是否被改

2) 内存扫描
   - 扫描已知 cheat / Frida / Cheat Engine signature
   - 检测 VirtualAllocEx (远程进程) 写过来的页

3) 调试器检测
   - IsDebuggerPresent / CheckRemoteDebuggerPresent / NtQueryInformationProcess(7)
   - 'fs:[0x30]+0x68' (NtGlobalFlag), 'fs:[0x30]+0x68' check
   - HW breakpoint (DR0-DR7) 检测
   - SetUnhandledExceptionFilter
   - vehDbgPresentCheck

4) VM 检测
   - cpuid 0x1 ECX bit 31 (hypervisor present)
   - rdtsc 时间漂移
   - VMware/VirtualBox/Parallels backdoor 端口
   - MAC 前缀 (00:0C:29 = VMware, 08:00:27 = VBox, 00:50:56 = VMware)

5) 输入异常
   - 鼠标移动太线性 / 太规律 / 没有人类抖动
   - 反应时间 < 80 ms 长期触发
   - 击杀模式异常（同一像素角度命中）

6) 服务端验证
   - 关键操作必须服务端校验，客户端只是显示
   - "客户端不要信"是基本原则
```

## 内存视角（CheatEngine 风格）

```text
CheatEngine 工作流（检测面 = 反作弊关注点）:
1) 进程 attach + 扫描内存（精确值 / 范围 / 改变 / 没改 / 增加 / 减少）
2) 找到地址后 → 反查谁写它（找出关键函数）
3) 改值 / 加 lock / 加脚本 / 注入 DLL

工具:
- Cheat Engine (Win, GUI)
- ScannerHax / GameGuardian (Android)
- IDA Pro + Hex-Rays + 自家脚本
- Frida (跨平台 hook)
- Process Hacker / x64dbg

防护点:
- 关键变量加运行时编码 (XOR mask 每帧重算)
- 关键变量分散存储 (多份冗余 + 一致性校验)
- 重要逻辑放服务端
- "honey trap" 假指针 / 假变量
```

## 网络协议（游戏多自家 binary）

```text
常见游戏协议:
- HTTP/HTTPS (登录、商城、配置)
- WebSocket (实时聊天 / 房间)
- TCP 自家 binary (战斗包: 长度+opcode+payload+CRC)
- UDP 自家 binary (实时帧同步 / FPS / RTS, 加 reliable layer)
- KCP (国服 MMO 偏爱)
- gRPC / QUIC (新游戏)

抓包:
- mitmproxy + 自家 CA (HTTPS)
- Wireshark + 自家 dissector (Lua plugin)
- 内核态 NDIS / WFP filter
- Frida hook 应用层 send/recv

加密:
- 多用 AES + 服务端下发 session key
- 包内常带 sequence number 防重放
- 校验 CRC / HMAC
```

## 实战入口

- **Unknown Cheats forum (unknowncheats.me)** — 全球最大的游戏逆向社区，海量 PE / native / .NET 反编译教程。
- **GuidedHacking forum / GuidedHacking YouTube** — 系统化游戏 hack 教程。
- **OWASP MASTG mobile games 部分**。
- **看雪 / 52pojie 中文圈** — 大量国产游戏逆向 writeup。
- **MalwareBazaar 标签 game / cheat** — 已知恶意外挂样本。
- **GitHub: NoesisGames / Mod Loaders / Modding 框架** — 合法 mod 社区的逆向产物。
- **Pwn2Own / DEFCON Game Hacking Village**（少见，但有专题）。
- **AnimeGame / 米游社开源工具圈** — Unity IL2CPP 还原标杆。

## 自检（拿到游戏客户端 30 分钟内回答）

1. 引擎与版本（Unity 2021.3.x / UE 5.2 / 自家）？
2. Anti-Cheat 套件（EAC / BattlEye / Vanguard / TP / NeAC / Themida）？是否带内核驱动？
3. 资源格式（asset bundle / pak / pck / 自家）？是否加密？key 怎么获取？
4. 主逻辑在 Mono / IL2CPP / Blueprint / 自家 VM？反编译可达性如何？
5. 核心数值（HP/技能 CD/坐标）在客户端可改吗？是否有服务端权威？
6. 网络协议形式（HTTP/WS/TCP binary/UDP/KCP）？是否加密 + 序列号 + HMAC？
7. 是否检测 VM / 调试器 / Frida / 内存扫描器？检测点能否定位？

## 相邻技能

- `binrev` / `winrev` / `linuxrev` / `macrev` — 客户端二进制平台层。
- `mrev` — 移动端游戏（绝大多数手游走 Unity / Cocos / Unreal）。
- `webrev` — H5 / Cocos Creator Web / Cloud Game。
- `vmrev` — 反作弊套件常用 VMProtect / Themida 自家 VM 保护关键函数。
- `packrev` — 游戏 PE 加壳（VMP / Themida / Enigma）。
- `cryptrev` — 包加密 / 资源加密 / pak AES key 还原。
- `protrev` — 自家网络协议字段位级、状态机、重放风险。
- `scriptrev` — Lua / JS / GDScript / Blueprint 字节码深挖。
- `cloudrev` — Cloud Gaming / 串流客户端形态。
- `crashrev` / `memrev` — minidump / 玩家上传的崩溃 + 反作弊证据链。