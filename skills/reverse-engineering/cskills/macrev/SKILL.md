---
name: macos-macho-reverse-engineering
description: macOS / Mach-O 运行生态逆向。dyld4 加载链、dyld_shared_cache 拆解、launchd/XPC/Mach IPC、entitlements、codesign/notarization/Gatekeeper/AMFI/SIP、TCC、Apple Silicon ARM64e PAC、Endpoint Security framework、ObjC/Swift runtime metadata、persistence 面（LaunchAgents/LaunchDaemons/kexts/Login Items）、lldb/dtrace/Instruments 工作流。
---

# macOS / Mach-O 运行生态逆向

## 适用场景

- macOS 上的 Mach-O / .app / .dylib / .framework / .kext / .dext，要回答其 dyld 加载链、entitlements、签名、Mach IPC、注入面与持久化。
- Apple Silicon (M1/M2/M3) 与 Intel 二进制差异，PAC / Pointer Authentication / BTI 的影响。
- 拆解 `dyld_shared_cache`（系统库都不是单独 .dylib 文件了）。
- ObjC/Swift 类元数据还原、协议表、selector 字符串到方法地址映射。
- 调试器：lldb 与 dtrace + Instruments。

## 不适用

- Mach-O 头 / 节区 / 函数 / 反编译 → `binrev`。
- iOS 应用（IPA） → `mrev`。
- 通用 ARM64 指令级 → `asmrev`。
- C++ vtable / RTTI / Swift class layout → `abirev`。

## Mach-O 加载链

```text
exec(2) → kernel
  ├─ 检查签名（AMFI: AppleMobileFileIntegrity，桌面也有，影响 page validation）
  ├─ 选择架构（fat binary → cpusubtype 匹配）
  └─ 装载 dyld（/usr/lib/dyld，Apple 自家动态链接器）
       └─ dyld4 main:
            ├─ 解析 LC_LOAD_DYLIB → 装载依赖（多数命中 dyld_shared_cache）
            ├─ 处理 LC_DYLD_INFO_ONLY: rebase / bind / weak_bind / lazy_bind / export_trie
            ├─ 跑 LC_LOAD_DYLINKER 指定的 dyld 自身的 ___start
            ├─ Mod-init: __DATA.__mod_init_func / module_init_func 列表
            ├─ ObjC: realize 类 + 注册 selector
            ├─ Swift: register protocol conformance
            └─ 跳 LC_MAIN entryoff → main()
```

环境变量：

```bash
DYLD_PRINT_LIBRARIES=1  # 列出加载的 dylib（hardened runtime 屏蔽，下面同）
DYLD_PRINT_BINDINGS=1
DYLD_PRINT_SEGMENTS=1
DYLD_PRINT_INITIALIZERS=1
DYLD_PRINT_APIS=1
DYLD_INSERT_LIBRARIES=/path/lib.dylib  # 仅未签名 / 未带 hardened runtime / 无 restricted entitlement
DYLD_FORCE_FLAT_NAMESPACE=1
DYLD_LIBRARY_PATH=...
```

绝大多数现代 macOS 应用都签名 + hardened runtime，DYLD_* 会被忽略。要测注入必须重签或关 SIP。

## 工具链

```bash
# 文件 / 头
file Target
otool -hl Target               # mach_header + load_commands
otool -Iv Target               # 重定位
otool -L Target                # LC_LOAD_DYLIB
otool -tV Target               # 反汇编 __TEXT,__text
otool -s __TEXT __cstring -V Target
nm -m Target                   # 符号 + 来源
size -m Target                 # 段/节大小
codesign -dvvv Target          # 签名细节
codesign --display --entitlements - Target
spctl -a -vv -t execute Target.app   # Gatekeeper 评估
xattr -lr Target.app           # 含 com.apple.quarantine
strings -e l Target

# 现代工具
ktool dump --symbols Target
ktool dump --headers Target
ktool dump --objc Target           # 等价 class-dump
ktool decrypt Target               # iOS 解密（FairPlay）
class-dump -H Target -o headers/
jtool2 -d objc Target
RotorVibe / MachOView                 # GUI 浏览
Hopper Disassembler                   # macOS 原生反编译
Binary Ninja / Ghidra / IDA Pro       # 跨平台
```

## dyld_shared_cache 拆解

macOS 11+ 系统库不再单独存在文件系统，全部塞进 `dyld_shared_cache_*`：

```bash
# 路径
ls /System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/   # Apple Silicon
ls /System/Library/dyld/                                         # Intel

# 拆出来
dyld_shared_cache_extract_dylibs dyld_shared_cache_arm64e ./extracted_dylibs
# 或 jtool2: jtool2 -e libsystem_c.dylib dyld_shared_cache_arm64e
# Apple 也开源了 dyld：github.com/apple-oss-distributions/dyld

# IDA Pro 9+ / Ghidra 11+ 自带 dyld_shared_cache loader，可以直接拖整个 cache 文件
# Hopper 也支持
```

## launchd / XPC / Mach IPC

```bash
# 服务列表（用户/系统域）
launchctl list                                            # 全部
launchctl list | head
launchctl print user/$UID
launchctl print system
launchctl print gui/$UID/com.apple.Finder

# plist 配置
ls ~/Library/LaunchAgents/                                # 用户
ls /Library/LaunchAgents/                                 # 全用户
ls /Library/LaunchDaemons/                                # 系统启动
ls /System/Library/LaunchAgents/                          # 系统自带（SIP 保护）
ls /System/Library/LaunchDaemons/

# plist 内容
plutil -p ~/Library/LaunchAgents/com.example.helper.plist

# XPC 服务列表
launchctl print-disabled gui/$UID
launchctl bootstraps -all

# Mach 端口
sudo lsmp -all -p $(pgrep -nf TargetApp)                  # 列进程的所有 mach port + 对端
heap $(pgrep -nf TargetApp)                                # ObjC heap 视图
sample TargetApp 5                                         # 抓 5 秒栈
spindump 30 -file dump.txt                                # 全机栈
```

XPC 通信：

```c
// XPC connection
xpc_connection_t conn = xpc_connection_create_mach_service("com.example.helper", NULL, XPC_CONNECTION_MACH_SERVICE_PRIVILEGED);
xpc_connection_set_event_handler(conn, ^(xpc_object_t event){...});
xpc_connection_resume(conn);
// 谁能连：服务方在 plist + 自校验 audit_token + entitlements
```

XPC 客户端伪造常见漏洞：未校验 audit_token，仅看 entitlement 名 → root 升权（Apple 历年 0day 多个走这条）。

## 调试 / 追踪

### lldb

```bash
lldb -- ./Target arg1
# 必备命令
target create Target
br set -n main
br set -F "_objc_msgSend"
br set -r "^Crypto::"             # 正则
br modify --command "po $arg1; po $arg2; c" 1
expression -- (int)getpid()
po (NSString*)$x0                 # ObjC 对象
register read
memory read --size 8 --format x --count 16 0x10000c000
image list
image lookup -a 0x10000c000        # 地址 → 符号 + 文件偏移
image lookup -n NSURLSession.dataTaskWithRequest
process attach --pid <pid>
process attach --name Target --waitfor
disassemble -n decryptKey -b
```

### dtrace（System Integrity Protection 限制下）

```bash
sudo dtrace -n 'syscall::open*:entry /execname == "Target"/ { printf("%s", copyinstr(arg0)); }'
sudo dtrace -n 'objc$target:NSURLRequest:-URL:return /pid == $target/ { ustack(); }' -p $(pgrep -nf Target)
sudo dtrace -ln 'objc*:NSString::*'                    # 列出所有 NSString 入口

# Instruments (GUI)：System Trace / Time Profiler / File Activity / Network / Allocations
xcrun xctrace record --template 'System Trace' --target-pid $(pgrep -nf Target) --time-limit 5s --output trace.trace
```

### Endpoint Security framework

第三方 EDR 都基于 ES framework：

```bash
# ESF 事件类型（节选）
ES_EVENT_TYPE_AUTH_EXEC / NOTIFY_EXEC
ES_EVENT_TYPE_AUTH_OPEN / NOTIFY_OPEN
ES_EVENT_TYPE_NOTIFY_FORK / EXIT
ES_EVENT_TYPE_NOTIFY_MMAP
ES_EVENT_TYPE_NOTIFY_MOUNT / UNMOUNT
ES_EVENT_TYPE_NOTIFY_SETEXTATTR
ES_EVENT_TYPE_AUTH_KEXTLOAD
# 日志
sudo log stream --predicate 'subsystem == "com.apple.endpointsecurity"'
```

测试用：写自家 `system_extension` + `EndpointSecurity.entitlement`，观察事件流。

## 注入面（识别）

| 手法 | 路径 / API | 限制 |
| --- | --- | --- |
| **DYLD_INSERT_LIBRARIES** | env var | hardened runtime / setuid / restricted entitlement 屏蔽 |
| **task_for_pid + mach_vm_write + thread_create_running** | Mach API | 需 `com.apple.security.cs.debugger` entitlement 或 `task_for_pid-allow` |
| **ROPInjector / Frida-Gadget** | static patch + 重签 | 修改后二进制必须重签 |
| **`__TEXT` patch + 重签** | 直接改 binary，re-sign | 适合本机测试 |
| **Insertable bundle**（旧版 SIMBL / mySIMBL） | App 加载未签名 plugin | macOS 现代版基本失效 |
| **AppleScript / OSAScript** | 利用 NSAppleScript / AEDescriptor | 有 TCC 弹窗 |
| **PAC bypass on M1+** | 利用 PAC 实现细节绕 | 学术 / Apple SEAR 持续修补 |

```bash
# 重签注入工作流（自家 / 测试）
otool -L Target.app/Contents/MacOS/Target
install_name_tool -change @rpath/old.dylib /tmp/inject.dylib Target.app/Contents/MacOS/Target
codesign --force --deep --sign - Target.app
xattr -dr com.apple.quarantine Target.app
spctl --add --label "test" Target.app
```

## 持久化面

```text
LaunchAgents（用户级）
  ~/Library/LaunchAgents/*.plist
  /Library/LaunchAgents/*.plist                      # 全用户
LaunchDaemons（root，启动时）
  /Library/LaunchDaemons/*.plist
LoginItems
  ~/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm
  System Settings → General → Login Items
Cron（弃用但仍可用）
  crontab -l ; /var/at/tabs/<user>
At
  /var/at/jobs/
Periodic
  /etc/periodic/{daily,weekly,monthly}/
emond
  /etc/emond.d/rules/                                # macOS 12 起弃用
Configuration Profile (.mobileconfig)
  /Library/Managed Preferences/
Login/Logout hooks（弃用但有些样本仍用）
  com.apple.loginwindow LoginHook / LogoutHook
Authorization plug-ins
  /Library/Security/SecurityAgentPlugins/
QuickLook plug-ins
  ~/Library/QuickLook/*.qlgenerator
Dock 持久化
  defaults write com.apple.dock persistent-apps -array-add ...
Spotlight importer
  ~/Library/Spotlight/*.mdimporter
Cron 替代：launchd `StartInterval` / `StartCalendarInterval`
Kext / DriverKit
  /Library/Extensions/*.kext (legacy)
  System Extensions: systemextensionsctl list
```

一键扫：`KnockKnock`（Patrick Wardle/Objective-See）/ `BlockBlock` 监控变更。

## 签名 / SIP / TCC / AMFI 速查

```bash
# 签名细节
codesign -dv --verbose=4 Target
codesign --display --entitlements :- Target

# Notarization
xcrun stapler validate Target.app
spctl -a -vv -t execute Target.app

# Quarantine bit
xattr Target.app
xattr -dr com.apple.quarantine Target.app

# SIP（System Integrity Protection）
csrutil status
# 关闭：恢复模式 → csrutil disable

# TCC（Transparency, Consent, Control）
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db ".dump access" | head
sqlite3 /Library/Application\ Support/com.apple.TCC/TCC.db ".dump access" | head
# 类别: kTCCServiceAccessibility / Camera / Microphone / SystemPolicyAllFiles / FullDiskAccess / ScreenCapture

# AMFI 状态
sysctl amfi
# 关闭（仅恢复模式）：nvram boot-args="-arm64e_preview_abi amfi_get_out_of_my_way=1"
```

## ObjC / Swift Runtime 元数据

```bash
# 类列表 + 方法列表
ktool dump --objc Target
class-dump -H Target -o headers/

# Swift 反射
nm -mU Target | grep _$s        # Swift 符号
swift-demangle '_$s4Test...'

# 在 lldb 内
po object_getClassName($x0)
po [$x0 class]
po [(id)NSClassFromString(@"AppKit.NSWindow") superclass]

# Frida ObjC bridge
ObjC.classes.NSURLRequest['- URL'].implementation
```

ObjC 方法调用 = `objc_msgSend(receiver, selector, args...)`，前两个寄存器分别是 self 和 _cmd（SEL）。逆向 ObjC 的核心是把 SEL 名称映射回方法实现：

```c
// IDA / Ghidra 都会自动把 _objc_msgSend(@"NSString", @"stringWithFormat:") 改写成可读形式。
// 手动: 取 selector 字符串地址 → 在 __objc_classlist / __objc_const 找类 → 找方法 IMP
```

## Apple Silicon / ARM64e PAC

ARM64e（M1+）二进制使用 Pointer Authentication：

```text
PAC* 指令族:
  PACIA / PACIB / PACDA / PACDB        签名（指令/数据 + 上下文）
  AUTIA / AUTIB / AUTDA / AUTDB        验证
  XPACI / XPACD                        清除签名位
  RETAA / RETAB                        带签名验证的 ret
上下文寄存器: x16 / x17 常用作 modifier；SP 作 b key 上下文
PA 失败: 签名位被覆盖为 0xc00...，访问触发 BRK 0xc471（macOS 内核）
```

逆向时看到 `pacibsp` / `autibsp` / `retaa` / `retab` 就是 PAC，IDA / Ghidra 会标 stripped pointer。

## 实战入口

- **Objective-See / Patrick Wardle 系列工具与 talks** — `Mac Malware: Detection, Analysis & Hunting` 是最系统的 macOS 安全教材。
- **TheBigHonker / xorrior / Csaba Fitzl 博客**。
- **MalwareBazaar OSX 标签**、**theZoo OSX**。
- **SLEH / pwn.college MacOS 章节**。
- **CMU CSF / DEFCON macOS Security Village**。
- **Apple Open Source（apple-oss-distributions）** — dyld / xnu / Security 都开源。

## 自检（拿到 Mach-O 30 分钟内回答）

1. fat binary 还是 thin？arm64 / arm64e / x86_64？
2. 签名状态：team id / hardened runtime / library validation / library validation 例外？
3. entitlements 有哪些？是否 com.apple.security.* 类敏感？
4. SIP 保护范围内？quarantine bit？notarization？
5. 加载链：依赖 dylib 列表，是否有非系统位置？
6. ObjC 主要类与方法清单？Swift 反射符号有哪些？
7. 是否走 task_for_pid / DYLD_INSERT_LIBRARIES / XPC？

## 相邻技能

- `binrev` / `asmrev` / `abirev` — Mach-O 头/段、ARM64/ARM64e/x86_64 指令、AAPCS / Apple x64 ABI、ObjC/Swift class layout。
- `mrev` — iOS（IPA、UIKit/SwiftUI、TrustKit、Keychain）。
- `crashrev` / `memrev` / `debugrev` — sample / crashreport、coredump、lldb 高级用法。
- `cryptrev` — CommonCrypto / SecKey / Keychain / Apple CryptoKit 调用流。
- `protrev` — XPC / Mach msg 协议层。
- `containerrev` — App sandbox container 文件系统。
- `malrev` — macOS 恶意样本（XCSSET / Silver Sparrow / OSX.Shlayer 等）。
- `packrev` — macOS 上的加壳变体（少见，通常是自定义 stub）。
- `vmrev` — VMP/Themida 在 macOS 上的对等物（极少）。