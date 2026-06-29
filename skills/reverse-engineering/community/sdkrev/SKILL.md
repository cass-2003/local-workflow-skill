---
name: sdk-supply-chain-reverse-engineering
description: 闭源 SDK 与二进制供应链逆向审计。AAR / xcframework / framework / .so / .dylib / .dll / .a 静态库审计；包管理器（Maven/CocoaPods/SPM/npm/PyPI/Cargo/Go modules/NuGet/Hex/Composer）签名链；多端 SDK（同一 vendor 的 iOS+Android+Web+桌面）对照；symbol/DWARF/dSYM/PDB 还原；SDK 行为画像：网络/存储/PII/反作弊/远程更新。
---

# 闭源 SDK / 供应链逆向

## 适用场景

- 团队要集成第三方 SDK，必须先静态审计：网络发什么、本地存什么、是否带 device id / fingerprint、是否远程加载代码、是否带后门。
- 拿到一份 .aar / .xcframework / .so / .dylib / .a，要回答："对外 API 列表？依赖哪些其他 SDK？版本？是否签名？编译者是谁？"
- 多端 SDK 一致性核查：同一 vendor 的 Android + iOS + Web 三个版本，做的事情应该一致；不一致就是风险。
- 包管理器投毒检测：恶意包伪装成著名包名。

## 不适用

- ELF/PE/Mach-O 函数级 → `binrev`。
- 移动端整 App 反编译 → `mrev`。
- 浏览器侧 SDK → `webrev`。
- 协议字段 → `protrev`。

## 包格式速识

### Android: AAR

```text
.aar = zip
  AndroidManifest.xml          # 必须；声明 SDK 用的权限/组件
  classes.jar                  # Java/Kotlin 编译产物（dex 之前）
  res/                         # 资源
  R.txt                        # 资源 ID 对应表
  proguard.txt                 # 给集成方的 ProGuard 规则
  jni/<abi>/*.so               # 原生库（按 ABI 多份）
  assets/
  libs/*.jar                   # 嵌套 jar
  META-INF/MANIFEST.MF
```

```bash
# 拆解
unzip -d aar_out my-sdk.aar
file aar_out/jni/arm64-v8a/*.so

# 看 manifest 要什么权限
xmllint --format aar_out/AndroidManifest.xml | grep -E 'permission|service|receiver|provider'

# Java 反编译
cfr aar_out/classes.jar --outputdir cfr_out
# 或 jadx-gui aar_out/classes.jar
```

### iOS / macOS: xcframework / framework

```text
my.xcframework/
  Info.plist                   # 列出每个 slice 路径与 SupportedPlatforms
  ios-arm64/
    my.framework/
      my                       # Mach-O fat or thin
      Info.plist               # CFBundle*
      Headers/                 # 公开头
      Modules/
        module.modulemap       # Swift 模块定义（含子模块）
        my.swiftmodule/        # 多 arch 的 Swift API ABI 信息（.swiftinterface .swiftdoc .swiftsourceinfo）
      _CodeSignature/
  ios-arm64_x86_64-simulator/
    my.framework/...
  macos-arm64_x86_64/
    my.framework/...
```

```bash
# Mach-O 检查
file my.xcframework/ios-arm64/my.framework/my
otool -L my.xcframework/ios-arm64/my.framework/my
nm -m my.xcframework/ios-arm64/my.framework/my

# Swift 公开 API（无需反编译，直接读 .swiftinterface）
cat my.xcframework/ios-arm64/my.framework/Modules/my.swiftmodule/arm64.swiftinterface

# 签名
codesign -dvvv my.xcframework/ios-arm64/my.framework
codesign --display --entitlements - my.xcframework/ios-arm64/my.framework

# 老式 .a 静态库
ar -t libfoo.a                     # 列对象文件
ar -x libfoo.a                     # 解出每个 .o
file *.o
nm -m libfoo.a | grep -E '^.*[A-Z] _' | head    # 导出符号
```

### Linux .so / Windows .dll

```bash
# .so 普通 ELF
readelf -d libfoo.so | grep NEEDED                        # 依赖
readelf -s libfoo.so | head -30                           # 符号表
nm -D libfoo.so | grep ' T ' | head                       # 导出函数（T = .text 全局）
objdump -p libfoo.so | grep -E 'NEEDED|RUNPATH|RPATH'    # 路径线索
strings libfoo.so | grep -E 'http(s)?://|@version|build'

# .dll
dumpbin /exports libfoo.dll
dumpbin /imports libfoo.dll
dumpbin /headers libfoo.dll
# 或 rabin2 -E -i -I libfoo.dll

# 是否带 PDB
strings libfoo.dll | grep -i 'pdb\b'
# 找到 PDB 文件后用 cv2pdb / dia2dump / pdbex 拿全符号
```

## Symbol / 调试信息还原

| 平台 | 调试信息 | 提取 |
| --- | --- | --- |
| **Linux ELF** | DWARF in-binary 或外置 .debug | `objdump -W` / `llvm-dwarfdump` / addr2line |
| **macOS Mach-O** | dSYM bundle (DWARF) | `dwarfdump path.dSYM` / `atos -o binary -l 0x100000000 0x102345` |
| **Windows PE** | PDB（外置） | DIA SDK / `cv2pdb` / `pdbex` / IDA loader |
| **Go binary** | 自带行号 + 类型 + buildinfo | GoReSym / `go tool addr2line` |
| **Rust** | DWARF + Itanium-like mangling | `rustfilt` |
| **Swift** | dSYM + 自家 mangling | `swift-demangle` / `xcrun atos` |

```bash
# DWARF 大全
llvm-dwarfdump --all libfoo.so | head -100
llvm-dwarfdump --debug-info libfoo.so | grep DW_TAG_subprogram | head

# 解 Go BuildID（即使没源码也能知道用了哪些库）
go version -m libfoo.so

# Rust + DWARF: 看 panic location 字符串
strings libfoo.so | grep -E '\.rs:[0-9]+' | head            # 暴露源代码路径名

# 如果上传了 source map / 源映射
ls libfoo.so.* libfoo.dSYM/Contents/Resources/DWARF/

# strip 程度
strip --strip-all -p libfoo.so      # 极端 strip（保 .dynsym）
strip --strip-debug libfoo.so       # 仅删 debug 不删动态符号
```

## SDK 行为画像（看 SDK 干了什么）

```bash
# 1) 网络
strings libfoo.so | grep -oE 'https?://[^"\s]+' | sort -u | head
strings libfoo.so | grep -oE '[a-z0-9-]+\.[a-z]{2,}\b' | sort -u | grep -v -E '^(www|api|cdn|static)\.' | head

# 2) 本地存储路径
strings libfoo.so | grep -oE '(\.config|\.cache|/data/data/|/Library/|~/Library/|%APPDATA%)' | sort -u

# 3) Device fingerprint API 命中
strings libfoo.so | grep -iE 'IMEI|MEID|MAC|UUID|androidId|advertisingId|IDFA|IDFV|DeviceID|fingerprint|sha256|hardware\.serial|sysctlbyname|getprop' | head

# 4) 反检测面：检查 root / Frida / Xposed
strings libfoo.so | grep -iE 'su\\b|busybox|magisk|frida|xposed|substrate|cydia|jailbreak'

# 5) 反调试
strings libfoo.so | grep -iE 'TracerPid|ptrace|isDebuggerConnected|/proc/self/status|dump_proc'

# 6) 加密
strings libfoo.so | grep -iE 'AES|RC4|ChaCha|HMAC|RSA|ECDSA|SM2|SM4|JNI_OnLoad|EVP_'

# 7) 反射 / 远程加载（动态加载代码 = 高危）
strings libfoo.so | grep -iE 'DexClassLoader|PathClassLoader|dlopen|LoadLibrary|System.load|loadClass|defineClass'

# 8) 自家 update 通道
strings libfoo.so | grep -iE 'update|upgrade|patch|hotfix|version_code|/v[0-9]+/'
```

## 多端 SDK 一致性对照

```text
核查同一 vendor 的多端 SDK 是否做相同的事:

iOS .xcframework:    抓 framework 的 Mach-O symbols + .swiftinterface
Android .aar:        抓 classes.jar 的 Java/Kotlin signatures + JNI 函数
Web .js:             webrev → bundle 还原 → API 列表
Go SDK:              go doc 列公开 API
.NET SDK:            ILSpy 反编译

对比维度:
  - 公开 API 数量与方法签名（如有意义对应）
  - 上行域名 / 端口 / 协议
  - 收集的字段（device id / location / contacts / ...）
  - 加密算法 / 签名方式 / 哈希算法
  - 远程更新通道 + 校验机制

不一致信号:
  - iOS 走 sentry.io, Android 走某个奇怪的 .com → 可能是隐藏的备用通道
  - iOS 不要 IMEI（拿不到）, Android 反复采 IMEI → 平台合规问题
  - 一端有反检测 / 反调试一端没有 → 可能针对某端有"异常"逻辑
```

## 包管理器 / 供应链验证

```text
Maven Central (Java/Kotlin/Android):
  pom.xml + maven-metadata.xml 含 groupId/artifactId/version
  签名: PGP/GPG (.asc 文件), publisher 公钥在 keys.openpgp.org
  GAV 唯一: groupId:artifactId:version
  验证: gpg --verify foo-1.0.jar.asc foo-1.0.jar

CocoaPods (iOS):
  Podspec.json 含 source / git tag / sha256 (s.source)
  实质上是 git checkout，pod 仓库本身不打包二进制
  XCFramework 通过 .podspec 的 vendored_frameworks 引入

Swift Package Manager (SPM):
  Package.swift 含 .binaryTarget(url:..., checksum:...)
  binaryTarget 强制 sha256 校验
  XCFramework 直接由 SPM 拉 zip 解开

npm / yarn / pnpm:
  package.json + package-lock.json (含 integrity sha512)
  npm audit / npm audit signatures
  postinstall hook 是常见后门点

PyPI / pip:
  setup.py + pyproject.toml
  PEP 458 sigstore 签名（部分包，逐步推广）
  setup.py 任意代码执行 = 历史投毒最大入口

Cargo (Rust):
  Cargo.toml + Cargo.lock (sha256 in registry)
  build.rs 构建脚本是后门点

Go modules:
  go.mod + go.sum
  go.sum 强制 sha256 + h1 校验
  proxy.golang.org + sum.golang.org 提供透明日志
  GOFLAGS=-insecure 是危险开关

NuGet (.NET):
  .nupkg = zip
  Authenticode 可签

Hex (Erlang/Elixir):
  自带哈希校验

Composer (PHP):
  composer.lock 含 sha256
  vendor 目录可被覆盖
```

```bash
# 通用：拿 vendor 公布的 sha256 vs 本地下载
sha256sum my-sdk-1.2.3.aar
# 对照官网 / Maven Central / npm registry 上的 integrity 字段

# npm
npm view <pkg> dist.integrity
npm audit signatures

# pip 强制 hash mode
pip install -r requirements.txt --require-hashes

# Maven
mvn dependency:resolve -Dverbose
gpg --verify foo.jar.asc

# Go
GOFLAGS="-mod=readonly" go mod download  -x
```

## 投毒 / 恶意 SDK 检测面

```bash
# 1) postinstall / setup.py / build.rs 是否含网络下载
unzip -p package.tgz package/package.json | jq '.scripts'           # npm
grep -RE 'install_requires|os\.system|subprocess' setup.py
grep -RE 'std::process::Command|reqwest|ureq' build.rs

# 2) 二进制内嵌的可执行字节
binwalk libfoo.so                                   # 看是否藏了二级 payload
strings libfoo.so | grep -E '^/[a-z]+/[a-z]+/[a-z]+' | head    # 嵌入路径暴露

# 3) 时间戳与构建机
strings libfoo.so | grep -iE 'jenkins|gitlab|github|drone|builder|@.*\.local' | head
go version -m libfoo.so | grep CGO_ENABLED

# 4) 字符串里的 base64 / hex 大块（typosquatted 包常见）
strings libfoo.so | awk 'length($0) > 80 { print }' | head

# 5) 可疑域名（拼写相近的著名服务）
strings libfoo.so | grep -oE '[a-z0-9-]+\.[a-z]{2,}' | sort -u | grep -E 'goog1e|paypa1|amaz0n|microsft'
```

## 实战入口

- **Sonatype OSS Index / OSV.dev / GitHub Advisory Database** — 已知漏洞数据库。
- **Sigstore / Cosign / SLSA framework** — 现代供应链签名方案。
- **lavamoat / Snyk / Socket.dev / Phylum** — 包级威胁情报。
- **MalwareBazaar 标签 supply-chain** — 历史投毒样本。
- **typosquat 数据集（typosquat / typodetect）** — 训练识别。
- **过往真实事件 writeup** — npm event-stream / ua-parser-js / colors.js / left-pad / xz-utils backdoor (CVE-2024-3094)。

## 自检（拿到 SDK 30 分钟内回答）

1. 包格式 / 大小 / 平台覆盖 / 架构覆盖？
2. 公开 API 数量 + 主要功能（看 header / .swiftinterface / 反编译概要）？
3. 依赖（包管理器 transitively + 静态库的 NEEDED）？
4. 网络上行域名 / 端口 / 协议？
5. 是否带 device fingerprint / PII 收集？
6. 是否签名（Authenticode / GPG / cosign）？签名身份是否可信？
7. 是否有远程更新 / 远程加载代码 / 远程命令通道？

## 相邻技能

- `binrev` / `linuxrev` / `winrev` / `macrev` — 平台层与函数级。
- `mrev` — 移动 SDK 在 App 集成后的实际行为。
- `webrev` — Web SDK / npm 包反编译。
- `cryptrev` — SDK 内嵌加密算法识别与误用。
- `protrev` — SDK 上行协议字段位级。
- `cloudrev` — SDK 后台云服务行为。
- `containerrev` — SDK 通过容器分发的形态。
- `iotrev` — IoT SDK 在设备端的形态。
- `vmrev` — SDK 内嵌的自家 VM（部分反爬 / DRM SDK）。
- `scriptrev` — SDK 内嵌的脚本字节码（Lua / Python pyc / DEX）。