---
name: mobile-reverse-engineering
description: 移动端逆向。Android APK/AAB/dex/Smali/native so/Manifest/resources、iOS IPA/Mach-O Universal/entitlements/Keychain、React Native/Flutter/Unity/Cocos 跨端、Frida/objection/Hook 框架、SSL pinning 与 root/jailbreak 检测识别、WebView JS 桥与混合栈调试。
---

# 移动端逆向

## 适用场景

- 拿到 APK / AAB / IPA / Frida pull 出来的 dump，要做权限审计、字符串/资源/接口审计、native so 还原、key 抓取、协议复现。
- 安全测试中要识别并绕过 SSL pinning / root / jailbreak / Frida / hook 检测，以便正常抓包做协议分析。
- 跨端框架（RN / Flutter / Unity IL2CPP / Cocos / Hermes / Xamarin）样本拆解。
- WebView 混合栈：H5 + JSBridge + native，要看桥的方法表与权限。

## 不适用

- 通用 ELF/PE/Mach-O 函数级深挖 → `binrev`。
- 加密算法识别 → `cryptrev`。
- 私有协议字段位级 → `protrev`。
- 移动端 Web JS（H5/PWA） → `webrev`。

## Android

### APK 结构

```text
target.apk
├── AndroidManifest.xml           # AXML 二进制
├── classes.dex / classes2.dex    # Java/Kotlin 编译后的字节码 (DEX)
├── lib/{arm64-v8a,armeabi-v7a,x86_64}/*.so   # native code
├── assets/                       # 任意资源（常藏配置/license/二级 dex）
├── res/                          # 编译后的资源
├── resources.arsc                # 资源索引表
├── META-INF/                     # CERT.RSA / CERT.SF / MANIFEST.MF / v2/v3 签名块
└── kotlin/ / okhttp3/ ...        # 类库残留 metadata
```

AAB（Android App Bundle）= ProtoBuf 形式的 base.zip + splits + dex。要先 `bundletool build-apks --mode=universal` 转成单 APK 再走常规流程。

### 拆包工具链

```bash
# 用 apktool 拆资源 + smali（默认带 baksmali）
apktool d -o apk_out target.apk
# 重打包: apktool b apk_out -o repacked.apk; apksigner sign --ks debug.keystore repacked.apk

# 用 jadx 直接出 Java 伪代码
jadx -d jadx_out target.apk           # CLI
jadx-gui target.apk                   # GUI

# 单独拿 dex 反编译
zipinfo target.apk classes.dex
unzip -p target.apk classes.dex > classes.dex
d2j-dex2jar classes.dex -o classes.jar
jd-gui classes.jar &
# 或更现代： cfr / procyon

# Manifest（AXML 二进制 → 文本）
apktool d target.apk -o /tmp/m
cat /tmp/m/AndroidManifest.xml
# 或更轻
aapt2 dump xmltree target.apk --file AndroidManifest.xml
```

### Manifest 关键字段

```bash
# 一行抓主要风险点
aapt2 dump xmltree target.apk --file AndroidManifest.xml | grep -E '(android:name|permission|exported|debuggable|networkSecurityConfig|usesCleartextTraffic|allowBackup|process|sharedUserId|requestLegacyExternalStorage)'
```

`exported="true"` 的 activity / service / receiver / provider 是外部攻击面。`networkSecurityConfig` 决定 pinning 与 cleartext 策略。

### Smali ↔ Java 对照

```text
# Smali (Dalvik 字节码文本格式)
.method public static checkSign(Ljava/lang/String;)Z
    .registers 3
    .param p0, "input"
    invoke-static {p0}, Lcom/x/Crypto;->md5(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    const-string v1, "deadbeef"
    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    return v0
.end method
```

对应 Java：

```java
public static boolean checkSign(String input){
    return Crypto.md5(input).equals("deadbeef");
}
```

直接改 Smali：把 `move-result v0` 后面塞 `const/4 v0, 0x1` 让它永远返回 true，再 `apktool b` + 自签名。

### Native so

`lib/arm64-v8a/libnative.so` 等价于 ELF，常规 binrev：

```bash
file lib/arm64-v8a/libnative.so
readelf -hd lib/arm64-v8a/libnative.so
nm -D lib/arm64-v8a/libnative.so | grep Java_                 # JNI 导出
objdump -d -M intel lib/arm64-v8a/libnative.so | head
# Ghidra / IDA / Binary Ninja 直接拖
```

JNI 函数命名规则：`Java_<package>_<class>_<method>`，`/`/`.` 都换成 `_`，重载用 `__JJ` 形式追加签名。

`JNI_OnLoad` 是动态注册入口：

```c
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved){
    (*vm)->GetEnv(vm, &env, JNI_VERSION_1_6);
    static const JNINativeMethod methods[] = {
        {"sign", "(Ljava/lang/String;)Ljava/lang/String;", (void*)real_sign},  // 名字 → 真实地址
    };
    (*env)->RegisterNatives(env, clazz, methods, sizeof(methods)/sizeof(methods[0]));
    return JNI_VERSION_1_6;
}
```

如果 `nm` 看不到 `Java_` 但 Manifest 里调到了，先 hook `RegisterNatives` 拿真实地址。

### Frida 入门 hook

```bash
# 准备
adb root && adb remount
adb push frida-server-16.4.10-android-arm64 /data/local/tmp/frida-server
adb shell 'chmod 755 /data/local/tmp/frida-server && /data/local/tmp/frida-server &'
frida-ps -U                       # 列进程

# 启动 + spawn
frida -U -l hook.js -f com.target.app --no-pause
```

```js
// hook.js — 抓 OkHttp 请求 + 跳过 cert pinning
Java.perform(() => {
  const Request = Java.use('okhttp3.Request');
  Request.toString.implementation = function(){
    const r = this.toString();
    console.log('[OkHttp]', r);
    return r;
  };

  // 通用 SSL pinning bypass（OkHttp / TrustKit / Conscrypt）
  const TM = Java.use('javax.net.ssl.X509TrustManager');
  const SSLContext = Java.use('javax.net.ssl.SSLContext');
  const TMImpl = Java.registerClass({
    name: 'com.x.bypass.TM',
    implements: [TM],
    methods: {
      checkClientTrusted(){}, checkServerTrusted(){}, getAcceptedIssuers(){ return []; }
    }
  });
  SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function(km, tm, sr){
    return this.init(km, [TMImpl.$new()], sr);
  };
});
```

### Objection（Frida 的高级前端）

```bash
objection -g com.target.app explore
# 进入交互后：
android sslpinning disable
android root disable
android hooking list classes
android hooking watch class_method com.x.Crypto.encrypt --dump-args --dump-return --dump-backtrace
android hooking generate simple com.x.Crypto      # 自动生成所有方法 hook
android intent launch_activity com.x.SecretActivity
android keystore list
ios sslpinning disable                 # iOS 也支持
```

### SSL pinning 检测面（识别）

| 实现 | 关键类/方法 |
| --- | --- |
| OkHttp `CertificatePinner` | `okhttp3.CertificatePinner.check(String,List)` |
| TrustKit | `TrustKitConfiguration` / `TSKPinningValidator.evaluateTrust` |
| Conscrypt | `org.conscrypt.TrustManagerImpl.checkTrustedRecursive` |
| WebView | `WebViewClient.onReceivedSslError` |
| Network Security Config | `res/xml/network_security_config.xml` 的 `<pin-set>` |
| 自实现 | 一般在 `X509TrustManager.checkServerTrusted` 抛 CertificateException |
| Native | OpenSSL / BoringSSL `SSL_CTX_set_verify` / `X509_verify` 在 native 层 |

### Root 检测面

```text
# 文件特征：/system/bin/su, /system/xbin/su, /sbin/su, /system/app/Superuser.apk, /system/app/Magisk.apk
# 包名特征: com.topjohnwu.magisk, eu.chainfire.supersu, com.koushikdutta.rommanager
# props: ro.build.tags=test-keys, ro.debuggable=1, service.adb.root=1
# Magisk 检测: /sbin/.magisk, /data/adb/magisk, magiskhide, zygisk
# Build 字段: Build.TAGS contains "test-keys"
# 可执行 which: which su, which busybox
# RootBeer/RootInspector 三方库
```

### 资源 / 配置取证

```bash
# 设备文件
adb shell run-as com.target.app ls -al /data/data/com.target.app/
adb pull /sdcard/Android/data/com.target.app

# SharedPreferences
adb shell run-as com.target.app cat /data/data/com.target.app/shared_prefs/*.xml

# SQLite
adb shell run-as com.target.app sqlite3 /data/data/com.target.app/databases/main.db .dump

# Keystore
adb shell 'cat /data/misc/keystore/user_0/* | xxd | head'   # 受保护，root 后才看得到
```

## iOS

### IPA 结构

```text
target.ipa (zip)
└── Payload/Target.app/
    ├── Target              # Mach-O fat binary
    ├── Info.plist          # 应用元数据
    ├── embedded.mobileprovision    # 描述文件 + 团队 ID + entitlements
    ├── _CodeSignature/     # 签名 / 资源哈希
    ├── Assets.car          # 资源（Assets.xcassets 编译产物）
    ├── Frameworks/*.framework
    ├── PlugIns/*.appex     # extensions
    └── *.nib / *.storyboardc
```

### 拆包工具链

```bash
# 解压
unzip -d ipa_out target.ipa

# 拿 Mach-O
file ipa_out/Payload/Target.app/Target          # universal binary
lipo -info Target
lipo -thin arm64 Target -output Target.arm64

# 二进制信息
otool -hl Target.arm64
otool -L Target.arm64                            # 链接的 framework
codesign -dvvv ipa_out/Payload/Target.app
codesign -d --entitlements :- ipa_out/Payload/Target.app

# Asset 解出
acextract Assets.car -o assets_out
xcrun --sdk iphoneos assetutil --info Assets.car

# nib/storyboard 解
ibtool nib --extract output.xib input.nib

# class-dump（去除 ObjC 类信息）
class-dump -H Target.arm64 -o headers/
# 或
ktool dump --headers Target.arm64
```

### Frida on iOS

```bash
# 越狱：装 Frida (Cydia 源 / Sileo: build.frida.re)
ssh root@iphone.local 'frida-ps'
frida -U -f com.target.app -l hook.js --no-pause

# 非越狱：用 frida-gadget 注入到重签 IPA（objection patchipa / theos）
objection patchipa --source target.ipa --codesign-signature 'iPhone Developer: ...'
ideviceinstaller -i target-patched.ipa
```

### Hook 例

```js
// hook NSURLSession：抓所有请求
const NSURLSession = ObjC.classes.NSURLSession;
Interceptor.attach(NSURLSession['- dataTaskWithRequest:completionHandler:'].implementation, {
  onEnter(args){
    const req = new ObjC.Object(args[2]);
    console.log('[NSURLSession]', req.HTTPMethod(), req.URL().absoluteString());
    const headers = req.allHTTPHeaderFields();
    console.log('  headers:', headers ? headers.toString() : '');
    const body = req.HTTPBody();
    if (body && body.length()){
      console.log('  body:', body.bytes().readUtf8String(body.length()));
    }
  }
});

// SSL pinning bypass 通用思路
['SSL_CTX_set_verify','SSL_set_verify'].forEach(s=>{
  const p = Module.findExportByName(null, s);
  if (p) Interceptor.replace(p, new NativeCallback(()=>0, 'void', []));
});
```

### Jailbreak detect 检测面

```text
# 常见路径检查
/Applications/Cydia.app, /Applications/Sileo.app, /var/lib/cydia, /usr/sbin/sshd
/private/var/lib/apt, /private/var/stash, /usr/bin/ssh
/Library/MobileSubstrate/MobileSubstrate.dylib

# fork() / system() / popen() 是否可用
# canOpenURL: cydia://, sileo://
# fopen / stat 上面那些路径
# dyld 列举：检查是否注入了 MobileSubstrate / FridaGadget / libsubstitute
# DyldHookCheck 库
```

## 跨端框架

### React Native

`assets/index.android.bundle`（Android）/ `main.jsbundle`（iOS）= 完整 JS bundle，直接 `webrev` 思路：

```bash
# 美化
npx react-native-decompiler -i index.android.bundle -o decompiled/
# 或 webcrack
npx webcrack index.android.bundle -o decompiled/

# Hermes 字节码（新版 RN 默认）
hbcdump index.android.bundle -out raw.txt        # 反汇编
# 或 hermes-dec / hbctool
```

### Flutter

```bash
# 主体在 lib/arm64-v8a/libapp.so （AOT 编译的 Dart）
# 公开工具：
# - reFlutter（已被广泛使用，可以 hook 并解析 libapp.so）
# - blutter（基于 Dart SDK 版本符号的 IDA 脚本，准确率高）
blutter --dart-version 3.x.x libapp.so out_blutter
# 抓包：用自家 CA + Frida hook ssl_verify_peer_cert（BoringSSL）
```

### Unity（IL2CPP）

```bash
# 入口在 lib/arm64-v8a/libil2cpp.so + assets/bin/Data/Managed/Metadata/global-metadata.dat
# 工具
il2cppdumper -b libil2cpp.so -m global-metadata.dat -o dumped/
# 输出：DummyDll/Assembly-CSharp.dll （能丢 dnSpy） + script.json （恢复符号给 IDA）
```

### Cocos2d-x / Cocos Creator

主逻辑常在 `assets/main.bin` (jsc) 或 lua/luac，配合 `cocos2d::lua` / `JSCompiler`，常用 `lua-decompile` / `unluac`。

### Xamarin

`assemblies/*.dll` 用 `dnSpy` / `ILSpy` 反编译；外加 `mono-symbolicate`。

## 实战入口

- **OWASP MASVS / MASTG** — 移动安全测试方法论 + 测试用例集 + 训练靶场（DIVA / InsecureBankv2 / iGoat）。
- **InsecureShop / Damn Vulnerable iOS App** — 实操靶场。
- **theZoo / MalwareBazaar 移动样本** — 隔离 VM 内做。
- **Frida CodeShare** — `https://codeshare.frida.re` 海量公开 hook 脚本。
- **OALabs / 雪人 / Maddie Stone GP Talks** — 系列实战视频。
- **Flare-On / DEFCON / RealWorldCTF Mobile 题目** — 公开赛题。

## 自检（拿到 APK/IPA 30 分钟内回答）

1. 包名 / Bundle ID / 版本 / 签名指纹 / 编译 SDK / minSdk？
2. 平台架构（armv7/arm64/x86_64）？是否带 native so？多大？
3. 是否跨端框架（RN/Flutter/Unity/Cocos/Xamarin/Hermes）？
4. exported component / 高危 permission / cleartext / NSC pin-set？
5. 主登录/接口签名调用栈到哪一层？是否走 native？
6. 是否有 root/jailbreak/frida 检测？SSL pinning 在哪一层？
7. 关键字符串：URL / API base / token 名 / 第三方 SDK 字符串？

## 相邻技能

- `binrev` / `asmrev` / `abirev` — native so 函数 / 指令级深挖。
- `linuxrev` — Android 底层（Linux 内核 + Bionic libc）。
- `macrev` — iOS Mach-O 与 dyld 行为细节。
- `cryptrev` — 接口签名/加密算法识别与 key flow。
- `protrev` — 接口字段、私有 binary 协议、TLS 抓包后的协议层分析。
- `webrev` — WebView 内 JS 桥与混合栈调试。
- `scriptrev` — DEX / Hermes / Lua / .NET IL / Dart snapshot 字节码深挖。
- `fwrev` / `iotrev` — 配套硬件设备固件。
- `packrev` — 加固壳（梆梆 / 爱加密 / 360 / 腾讯乐固 / Bangcle / Promon）识别与脱壳。