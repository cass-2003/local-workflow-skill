---
name: flutter-development
description: Flutter 开发实战排障技能：覆盖 Flutter 3.x、Dart 3、版本矩阵、Widget rebuild、状态管理、Navigator 2.0/go_router、PlatformView、MethodChannel、离线缓存、响应式/a11y/i18n、Web/Desktop、Gradle/Kotlin、CocoaPods、Xcode signing、Firebase、Impeller/Skia、shader jank、deferred components、可观测、测试与发布打包。触发于 .dart、pubspec.yaml、Flutter 页面/路由/状态/插件/跨端/打包/性能问题。
---

# Flutter 开发

Flutter 开发（flutter-development，兼容 slug: fltr）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

## 快速总则

1. 先锁证据：必须确认 Flutter 3.x/Dart 3 版本、Flutter channel、FVM 配置、目标平台、设备/模拟器、Android API、iOS 版本、Gradle/Kotlin/JDK、Xcode、CocoaPods、Firebase 与关键插件版本。
2. 先定入口：确认 main/flavor、MaterialApp/CupertinoApp、路由入口、Navigator 2.0/go_router、初始化顺序、目标页面与状态所有者。
3. 先判平台：同一 Dart 代码在 Android/iOS/Web/Desktop 表现可能不同；PlatformView、MethodChannel、权限、后台、键盘、insets 必须按平台验证。
4. 先抓现象：截图/录屏、完整日志、最小复现路径、预期/实际、偶发频率；卡顿必须有 DevTools frame/rebuild/raster 证据。
5. 先查影响面：改 Widget、Provider/Bloc、路由、插件、pubspec、Gradle、Podfile、Info.plist、AndroidManifest 前搜调用方和生成物。
6. build 只渲染：禁止在 build 中网络、IO、注册监听、创建 Future、请求权限、启动动画或写全局状态。
7. 状态统一：Riverpod/Bloc/Provider/GetX/MobX 以项目既有方案为准，不为单点问题引入第二套状态模型。
8. 数据有源：端侧缓存、接口响应、乐观更新、后台同步必须明确权威数据源、失效规则和冲突策略。
9. 隐私合规：权限、日志、崩溃、埋点、本地加密、发布隐私声明不得绕过平台规则或审核要求。
10. 交付闭环：说明改动、影响面、验证命令、真机/模拟器矩阵、未覆盖风险；涉及逻辑/数据/权限后续交给 tst 与 aud 收口。

## 单技能开发闭环门禁

- 开发前必须把目标拆成页面/状态/路由/API/本地存储/平台能力/构建发布七个面；任一面涉及改动，都要列入口、所有者、失败态和验证证据。
- Widget 状态所有权先定责：临时 UI 输入态留在局部，业务事实进入既有状态层，缓存事实进入存储层；禁止同一字段在多个 Provider/Bloc/controller 中双写。
- 页面闭环必须覆盖 loading、success、empty、error、permission denied、offline、retry、leaving page after request、restore from background；只做 happy path 不算完成。
- 表单闭环必须覆盖初始值、空值、校验、禁用态、防重复提交、服务端错误回填、键盘遮挡、焦点顺序和离开页面未保存提示。
- API 入参和客户端字段必须做白名单映射；禁止把客户端传来的 userId、price、role、owner、tenant、isPaid 等敏感字段直接当服务端事实。
- 路由闭环必须覆盖冷启动、deep link、登录态 unknown、返回栈、pop result、重复点击、浏览器 history 和权限拒绝后的回退页。
- 平台能力闭环必须覆盖 Dart 侧错误模型、原生错误码映射、权限拒绝/永久拒绝、超时、取消、重复调用、后台前台切换和真机日志。
- 发布闭环必须至少有 debug 之外的 profile 或 release 真机证据；涉及签名、混淆、权限、网络安全、符号表、Firebase flavor 时不能用 simulator/debug 代替。

## 硬禁止与低级错拦截

- 禁止在 build、selector、builder、itemBuilder、redirect 中做网络、IO、权限弹窗、路由跳转、状态写入、controller 创建或订阅注册。
- 禁止 await 后直接 setState、Navigator、showDialog、context.read/watch；必须确认 mounted、当前路由、请求序号和取消状态。
- 禁止未 dispose 的 TextEditingController、FocusNode、AnimationController、ScrollController、StreamSubscription、Timer、TabController 和 PageController。
- 禁止 PlatformChannel 只返回 dynamic/map 而无 typed DTO、错误码、异常映射和超时策略；原生异常不能只吞成“失败”。
- 禁止只在 simulator、Chrome、debug、hot reload 下验收；权限、相机、推送、支付、后台、签名、混淆、网络安全必须按目标真机和构建模式验证。
- 禁止日志、toast、Crashlytics/Sentry breadcrumb 输出 token、手机号、身份证、精确地址、支付信息、服务端签名、原始请求头和完整响应体。
- 禁止为修一个页面引入第二套状态管理、第二套路由、全局单例缓存或大版本插件升级；没有影响面证据不做架构级变更。
- 禁止用清缓存、删 lockfile、降版本、关混淆、删权限、删 entitlements、跳过签名来掩盖 root cause。

## 场景执行卡

### 1. 版本与平台矩阵
- 先记录 flutter --version、dart --version、pubspec SDK 约束、Flutter channel、FVM 配置、.fvmrc/.fvm/fvm_config.json、CI 镜像和 lockfile 中关键插件版本。
- 查 FVM/channel drift：本机、CI、IDE、melos/workspace、脚本和缓存 key 是否使用同一 Flutter SDK；禁止只看全局 flutter。
- Android 查 compileSdk/minSdk/targetSdk、AGP、Gradle、Kotlin、JDK、namespace、NDK、R8/proguard、AndroidX 迁移状态。
- iOS 查 Xcode、CocoaPods、Ruby 环境、Podfile platform、deployment target、Swift 版本、隐私清单、签名与 capabilities。
- Flutter 3.16-3.35 期间重点查 Material 3 默认行为、Android edge-to-edge、Impeller 默认路径、插件 API 和 breaking changes。
- 不确定兼容性时先比对项目现有 lockfile、CI 镜像、构建日志第一处 root cause；不得凭感觉升级/降级大版本。
- 输出版本矩阵、异常平台、可复现命令和未覆盖平台。

### 2. Widget rebuild / 布局溢出 / 黑屏白屏
- 查父约束、Expanded/Flexible、Intrinsic、ListView/Column 嵌套、Sliver 层级、SafeArea、MediaQuery、键盘 insets。
- 查 rebuild 来源：setState 范围、Consumer/BlocBuilder selector、ValueListenable、AnimationController、StreamBuilder、FutureBuilder 创建位置。
- Controller、FocusNode、AnimationController、ScrollController、StreamSubscription、Timer 必须有生命周期和 dispose 证据。
- 黑屏白屏要区分首帧阻塞、异步初始化、路由跳转、资源缺失、平台插件注册失败和异常被吞。
- 证据：报错栈、Widget tree 关键父子、DevTools rebuild 视图、目标设备截图。

### 3. Riverpod/Bloc/Provider/GetX/MobX 状态错乱
- 查 provider/bloc/controller 生命周期、autoDispose、keepAlive、context.read/watch/select、事件去重、异步取消、缓存失效。
- await 后更新 UI 必看 mounted、路由仍在前台、请求序号或 token 是否过期。
- 不把业务状态塞进局部 State，也不把局部输入态提升成全局缓存。
- hydrated bloc、restoration、持久化状态、跨 isolate 同步必须明确序列化版本、恢复时机和清理策略。
- 多状态源展示同一业务字段时，先确认单一事实源和刷新广播路径。
- 状态层必须显式表达 loading/success/empty/error/offline/permission，不能用 null、空列表或 bool loading 混成不可区分状态。

### 4. 表单 / API 数据 / 页面状态闭环
- 查 DTO、form model、domain model、cache model 是否分层；接口 response 不直接灌 UI，UI 输入不直接作为提交 payload。
- 表单字段查默认值、null、空字符串、空数组、类型转换、金额/时间/时区、图片/文件、枚举未知值和服务端错误回填。
- 列表和详情查 loading/error/empty/skeleton/分页到底/刷新失败/缓存过期/旧版本字段缺失；不得只测有数据场景。
- 提交动作查防重复点击、幂等 token、取消请求、超时、弱网重试、乐观更新回滚、离开页面后的结果处理。
- 客户端只负责展示和输入约束；价格、权限、归属、会员态、库存、审核状态、租户隔离等服务端事实不得由 Flutter 端自信任。

### 5. Navigator 2.0/go_router 路由异常
- 查 redirect 循环、ShellRoute/StatefulShellRoute、嵌套路由、deep link、登录态初始化、pop 返回值、页面 key、browser history。
- 鉴权状态未加载完成时不得直接跳登录再跳回，需区分 unknown/authenticated/unauthenticated。
- Web 端查 URL strategy、浏览器前进后退、刷新恢复、query/path 参数解析和 deep link 与移动端差异。
- 输出需列出入口路由、触发路径、重定向条件、返回栈和回退行为。

### 6. MethodChannel / EventChannel / Pigeon / FFI
- 查 channel name、方法名、参数类型、线程、Activity/Fragment 生命周期、iOS main thread、错误码、超时、重复注册。
- 原生异常必须带 Android logcat 或 Xcode console；Dart 端只看到 PlatformException 不足以定责。
- 涉 BLE、相机、定位、通知、支付时同步检查权限、后台能力和插件版本。
- Pigeon/FFI 变更要查生成源、ABI、空安全、线程切换和异常映射，不直接改 generated 文件。
- 每个 channel 方法必须定义 typed request/response、错误码表、权限拒绝态、超时、取消、重试语义和原生日志定位方式。
- EventChannel 必须验证 listen/cancel、重复订阅、页面销毁、后台切换、热重启和原生资源释放。

### 7. PlatformView / WebView / Map / Camera
- 查 hybrid composition、Texture、手势竞争、z-order、键盘遮挡、透明背景、页面复用和 dispose。
- iOS 查 UIViewController 层级、WKWebView 配置、相册/相机权限；Android 查 Activity、Fragment、Surface/Texture、混淆。
- 性能问题区分 Dart UI thread、raster thread、平台 view 合成成本。
- 页面复用、Tab 保活、后台前台切换必须验证 pause/resume/dispose 和权限重新授权。

### 8. Impeller / Skia / shader jank / 动画卡顿
- 确认渲染后端：iOS 默认 Impeller，Android 可能切换；记录 Flutter 版本和启动参数。
- 首帧/转场/列表卡顿用 DevTools frame chart、raster time、shader compilation、图片解码、overdraw 证据定位。
- 不用“加 const”当万能优化；要说明 rebuild、layout、paint、raster、IO 哪一段变好。
- 大图、透明 PNG、Lottie、blur、clip、shadow、PlatformView 叠加要看内存、解码、栅格和合成证据。
- 性能结论必须给 baseline、设备、profile/release 模式、优化前后指标和未测设备。

### 9. 离线缓存 / 本地存储 / 数据一致性
- 选择 Hive/Isar/sqflite/shared_preferences/secure storage 前先判断数据规模、查询模型、事务、加密、迁移、跨 isolate 和备份需求。
- shared_preferences 只适合少量配置，不承载复杂业务缓存、队列、关系查询或敏感明文。
- 缓存必须定义 TTL、ETag/Last-Modified、版本号、失效条件、清库策略和从旧 schema 迁移路径。
- 乐观更新、弱网重试、后台同步要记录操作队列、幂等键、冲突合并、回滚 UI 和重复提交防护。
- 安全存储区分 token、PII、业务缓存和可恢复数据；日志/崩溃不得输出敏感字段。
- 验证覆盖首次安装、升级、离线启动、弱网、并发写、用户切换、登出清理和恢复失败。

### 10. 响应式布局 / a11y / i18n
- 查断点、折叠屏、平板、桌面窗口、横竖屏、AdaptiveScaffold/NavigationRail/BottomNavigationBar 切换和 Sliver 结构。
- textScale、动态字体、最小触控面积、对比度、语义标签、焦点顺序、TalkBack/VoiceOver 需单独验证。
- RTL、ARB/l10n、locale fallback、复数、性别、日期/时区、数字/货币格式不得硬编码。
- 键盘、输入法、快捷键、焦点、系统返回和无障碍读取顺序要按平台验证。
- golden 或截图验证需锁字体、locale、textScale、屏幕尺寸、平台和主题。

### 11. Firebase / 推送 / deep link / 远程配置
- 查 firebase_options.dart、GoogleService-Info.plist、google-services.json、bundleId/applicationId/flavor 对齐。
- 推送查前后台/terminated、APNs token、通知权限、Android channel、iOS capabilities、消息 payload。
- deep link 查 universal links/assetlinks、路由初始化时序和冷启动 intent。
- Remote Config/Analytics/Crashlytics 要查初始化顺序、环境隔离、用户标识脱敏和离线默认值。

### 12. 错误上报 / 日志 / 可观测性
- 全局异常链路查 FlutterError.onError、PlatformDispatcher.instance.onError、runZonedGuarded、isolate error listener 和原生崩溃入口。
- Crashlytics/Sentry 必须验证 release 环境、用户路径 breadcrumb、关键上下文、日志脱敏和采样策略。
- Android mapping、iOS dSYM、Flutter split-debug-info/symbols 未上传时，release 崩溃不能宣称可定位。
- 性能监控查启动、页面切换、接口、帧耗时、卡顿、内存、图片解码和平台通道耗时。
- profile trace 需在 profile/release 近似环境采集，标明设备、Flutter channel/FVM、渲染后端、trace 文件、timeline 片段、baseline 与阈值。
- 输出需列异常捕获边界、字段白名单、符号化状态、验证崩溃/非致命错误的方法。

### 13. Gradle/Kotlin / CocoaPods / Xcode signing 打包失败
- Android 查 AGP/Gradle/JDK/Kotlin 版本矩阵、namespace、minSdk/compileSdk、NDK、R8、插件 Gradle 配置。
- iOS 查 Xcode、CocoaPods、Podfile platform、deployment target、Swift 版本、Info.plist、entitlements、Team、Provisioning Profile。
- 先读完整错误第一处 root cause，不用清缓存代替分析；清理命令只作为验证步骤。
- CI 与本机差异要查 Flutter SDK/FVM、Ruby/CocoaPods、JDK、证书、环境变量、缓存 key、flavor 注入和 codegen 顺序。
- CI gates 至少覆盖 dart format --set-exit-if-changed、flutter analyze fatal-warnings、lint、测试 random seed、coverage min、codegen diff 和依赖锁文件漂移。
- 构建问题必须区分 debug/profile/release、simulator/device、local/CI、flavor、签名和混淆；不能用 debug 通过推断 release 可用。

### 14. 发布 / 签名 / 合规 / 回滚
- 包发布查 pana/pub score、pub.dev dry-run、semver、CHANGELOG、README/API docs、LICENSE、SDK constraints、example、screenshots、platform support 和 breaking migration guide。
- monorepo/workspace 发布必须按包路径过滤变更与测试，确认 path dependency、dependency_overrides、melos bootstrap/version/publish 顺序和私有包不会泄漏。
- Android 发布查 AAB、applicationId、versionCode、签名、Play App Signing、proguard/R8、mapping 上传、权限说明和 Play 内测轨道。
- iOS 发布查 archive scheme、bundleId、version/build、证书/描述文件、entitlements、隐私清单、TestFlight、dSYM 上传和审核文案。
- 多 flavor 必须保证 Dart define、Firebase 文件、图标名称、bundleId/applicationId、API endpoint、权限和 CI secrets 一致。
- 回滚策略需明确旧版本兼容、后端开关、远程配置、缓存/数据库迁移是否可逆。
- 不绕过签名、权限、审核、隐私提示；不删除平台配置来“让编译过”。
- 发布前必须记录至少一个目标平台的 profile 或 release 真机启动、登录/主链路、权限、网络、崩溃符号化和日志脱敏证据。

### 15. add-to-app / EngineGroup / prebuilt 预构建产物
- add-to-app 先确认宿主 Android/iOS 生命周期、FlutterEngine 缓存、路由初始参数、插件注册、Activity/Fragment/ViewController 嵌入点和返回栈边界。
- EngineGroup 多实例要查 isolate 隔离、共享资源、插件单例、内存峰值、首帧耗时、销毁时机和 warm-up 策略。
- 预构建 AAR/XCFramework/Flutter module 查 Flutter SDK/channel/FVM、build mode、dart-define、flavor、symbols、Bitcode/签名、Podspec/Maven 坐标和宿主版本兼容。
- 宿主与 Flutter 权限、网络安全配置、deep link、推送和 analytics 事件归属必须明确，不把宿主问题误判为 Dart 问题。

### 16. Web / Desktop 差异
- Web 查 renderer、CanvasKit/HTML、资源跨域、CORS、base href、PWA/service worker、浏览器缓存和 history 行为。
- Web 文件、剪贴板、下载、通知、相机、定位权限要按浏览器能力和用户手势限制验证。
- Desktop 查 macOS/Windows/Linux 打包、签名/公证/沙盒、窗口最小尺寸、菜单、快捷键、拖拽、文件系统权限。
- 桌面输入法、焦点、滚轮、右键、键盘导航和大屏布局不能直接复用移动端假设。
- 输出需标明浏览器/系统版本、窗口尺寸、构建模式和平台未覆盖风险。

### 17. deferred components / 动态特性 / 资源体积
- 查 pubspec deferred components 配置、Android bundle、Play delivery、资源路径、首包/延迟包边界。
- 延迟加载失败要区分下载失败、install 失败、路由提前访问、资源未声明。
- 体积优化需给 APK/AAB/IPA 分析证据，不凭感觉删资源。
- 商店包、内测包、调试包的资源与动态模块行为可能不同，必须按目标发布形态验证。

### 18. 测试金字塔与回归
- Unit test 验纯 Dart 逻辑、序列化、缓存策略、状态 reducer/usecase；fake async 覆盖 debounce、timer、重试和超时。
- Widget test 验状态和布局边界，mock MethodChannel/接口响应，覆盖 loading/success/error/empty。
- Golden test 必须锁字体、屏幕尺寸、locale、textScale、平台差异和 Material 3 主题。
- Integration/e2e 验路由/权限/插件/登录/支付/推送/离线主链路；原生插件需真机矩阵。
- Firebase Test Lab/设备云用于 Android 真机矩阵时需固定机型、API、locale、网络状态、重试策略，并保留 logcat、截图、视频和性能指标。
- CI 分层运行 analyze、unit/widget、golden、integration/build；失败需保留截图、日志、视频或构建产物。
- 涉异步必须测加载、成功、失败、取消、重试、离开页面后返回；flaky 先归因时序、网络、动画、权限和设备差异。

## Dart / Flutter 语言陷阱速查（Widget/State/异步/null safety 独家）

Dart null safety 与类型：

- **sound null safety**（Dart 2.12+/Flutter 2.0+）：`String` 不可空、`String?` 可空；运行时也强制；不要 `as String?` 绕过编译器。
- `late` 关键字：延迟初始化非空变量；访问未初始化抛 `LateInitializationError`；适合 `late final user = await fetchUser();` 但要保证使用前已初始化。
- `!` null assertion：`x!.name` 当 x 为 null 抛 `Null check operator used on a null value`；与 Kotlin `!!` 同样 production code 应避免。
- `??` null coalescing / `??=` null-assignment / `?.` safe navigation；连接 `a?.b?.c ?? default`。
- type promotion：`if (x != null) { x.method() }` 自动 promote；但**对 instance field 无效**（其他线程可能改），用 local var 或 `if (case String x?)`（Dart 3 pattern）。

Widget / State 模型：

- StatelessWidget vs StatefulWidget：**Widget 是不可变描述**，每次 build 都重建；`State` 持久（除非 key 改变）。`setState(() { ... })` 标记 widget 脏，下帧 rebuild。
- `BuildContext` 是 widget 在树中的位置；`Theme.of(context)`/`MediaQuery.of(context)` 等需要 context；不要在 async 后用 stale context — 用 `if (!mounted) return;` 检查 State 还活着。
- `key` 决定 widget 复用：`ValueKey`/`UniqueKey`/`GlobalKey`；list item 没 key 时按 index 匹配，重排会错乱；动态列表用 stable id 作 key。
- `dispose()` 清理：`AnimationController`/`StreamSubscription`/`TextEditingController`/`FocusNode`/timer 等都要 dispose；忘记会内存泄漏。
- `WidgetsBindingObserver` 监听 app 生命周期（resume/pause/inactive/detached）；要在 dispose 时 removeObserver。

构建模型与性能：

- `build()` **必须 pure**：不能有副作用、不能依赖 build 顺序、不能改 widget 状态；Flutter 可能多次调用。
- 避免重建：把不变部分提到 `const` widget（`const Text("...")`）；用 `const` constructor；用 `ValueListenableBuilder`/`Selector`（Provider）/`select`（Riverpod）局部订阅。
- 大列表用 `ListView.builder` 不是 `ListView(children: [...])`；后者一次性构建所有 children。
- `Opacity(opacity: 0.5)` 触发 saveLayer 性能差；用 `Color.withOpacity()` 或 `FadeTransition`/`AnimatedOpacity`。
- DevTools profile mode 看 frame timing；rebuild stats 看哪些 widget 频繁 rebuild。

State management 选型：

- **Provider**：基于 InheritedWidget，简单；老项目主流。
- **Riverpod**（Provider 重写版）：无 BuildContext 依赖，compile-safe，更灵活；`ConsumerWidget`/`ConsumerStatefulWidget`/`ref.watch`/`ref.read`/`ref.listen`。
- **Bloc / Cubit**：基于 Stream + event 模式；适合复杂状态机；与 RxDart 整合。
- **GetX**：包含 routing/DI/state/i18n 大全；但耦合重 + 反模式多，不推荐新项目。
- 选型规则：小项目 Riverpod 或 Provider；大项目 + 复杂状态 Bloc；不混用多个全局状态库。

异步与 Isolate：

- `async`/`await` 基于 `Future`；single-threaded event loop（与 JS 类似）；CPU 密集 block UI。
- `compute(fn, arg)` 把函数 push 到 isolate（独立 heap，参数 SendPort 传递，需 cloneable）；适合 JSON 解析、图像处理、加密。
- `Isolate.run(fn)`（Dart 3+）：简化 isolate 创建；自动管理生命周期。
- `Stream` 是 async 序列；`StreamController` 创建；`broadcast` 多订阅 vs single-subscription；记得 cancel subscription（dispose 时）。
- `Timer.periodic`/`Future.delayed`：cancel 在 dispose；不 cancel 跨页面 timer 继续跑。
- DateTime/时区：`DateTime.now()` 本地时区；`DateTime.now().toUtc()` UTC；中文展示用 `intl` 包 `DateFormat('yyyy年MM月dd日 HH时mm分ss秒', 'zh_CN').format(date)`。

Dart 3 增量：

- **records**（Dart 3.0+）：`(int, String) record = (1, "a"); record.$1; record.$2;`；命名 `({int x, int y})`；轻量级 multi-return。
- **patterns**（Dart 3.0+）：`switch (x) { (int a, int b) => ..., {String name} => ..., var [first, ...rest] => ... }`；解构 + 守卫 `when`。
- **sealed class**（Dart 3.0+）：sealed + class 让 switch exhaustive；`sealed class Result<T> { } class Ok<T> extends Result<T> { final T value; } class Err<T> extends Result<T> { final String error; }`。
- **class modifier**：`base`/`final`/`interface`/`mixin class`/`sealed`；控制继承可见性。

## Flutter 3.x / Material 3 / Impeller 增量（2024-2026）

Flutter 3.16+ / 3.19 / 3.22 / 3.24 / 3.27+：

- **Material 3 默认**（Flutter 3.16+）：`useMaterial3: true` 默认；颜色 scheme 用 `ColorScheme.fromSeed`；旧 Material 2 组件需迁移（按钮、AppBar、Card 视觉变化大）。
- **Impeller**（Flutter 默认 iOS/Android 3.22+）：替代 Skia 渲染；首帧/jank 改进；自定义 shader 需重新适配（`FragmentShader` API）。
- **WASM target**：`flutter build web --wasm`（Flutter 3.22+）；性能大幅提升 vs JS 编译；不是所有 plugin 兼容。
- **Squad mode**（Cocoapods 替代 / Privacy manifest）：iOS 14.5+ requires Privacy manifest；Flutter 3.19+ 工具链支持。
- **adaptive components**：`SwitchListTile.adaptive`/`SegmentedButton`/`MenuAnchor` 等跨平台 native look。
- **shadcn-ui-flutter** / **forui** / **moon_design**：第三方设计系统替代 Material 3。

State management 现代：

- **Riverpod 2.x**：`@riverpod` annotation + `riverpod_generator`；Async/Family/AutoDispose；推荐新项目首选。
- **Bloc 8.x**：`emit` 异步、`on<Event>`、`HydratedBloc` 持久化、`bloc_test`。
- **flutter_hooks**：React-style hooks（`useState`/`useEffect`/`useMemoized`）；可与 Riverpod 组合。

平台与发布：

- **Platform Channels** + **Pigeon**：原生互操作；Pigeon 是 type-safe code gen 推荐替代手写 MethodChannel。
- **FFI** + **Dart Native Assets**（实验）：直接调 C/Rust library 无 channel 开销；适合性能敏感如图像处理、加密。
- **Privacy manifest**（iOS 14.5+）：声明 API 使用 reason；不合规无法上 App Store。
- **App Bundle (Android)** / **App Store** 提交：Flutter 3.x 默认 64-bit only；`--obfuscate --split-debug-info` 混淆减小体积。

测试：

- **flutter_test**：unit + widget test；`WidgetTester` 操作树；`pumpAndSettle` 等待动画结束。
- **integration_test**：跑在真机/模拟器；UI 交互完整流程；CI 集成。
- **golden test**：截图比对；跨平台字体差异需 `flutter test --update-goldens` 重生成；CI 固定 baseline image。
- **mockito** / **mocktail**：mock 对象；mocktail 不需 codegen + null-safety friendly。

## 高频坑 / 防遗漏

- Material 3 默认主题、颜色、按钮高度、NavigationBar、Dialog、TextField 与旧 Material 行为不同。
- Dart 3 null safety、records/patterns/sealed class 迁移会影响序列化、泛型和 exhaustive switch。
- pubspec 改 assets/fonts 后必须重跑构建；路径大小写在 iOS/Android/macOS 上可能表现不同。
- 图片大图、透明 PNG、Lottie、blur、clip、shadow 容易造成 raster 压力，不等于 Dart 代码慢。
- keyboard insets、SafeArea、系统手势、刘海屏、折叠屏、平板横屏必须单独看。
- iOS 后台、通知、相机、相册、定位、蓝牙权限不只在 Dart 插件配置，还在 Info.plist/entitlements/capabilities。
- Android 13+ 通知权限、Android 14/15 前台服务/精确闹钟/照片权限/edge-to-edge 变化会让旧插件静默失败或遮挡 UI。
- Android debug/profile 变体常因调试、热重载或本地网络带 INTERNET/cleartext/usesCleartextTraffic，release 权限差异、network security config、混淆和签名可能不同，必须逐变体核对。
- Hot reload 不等于冷启动；初始化、路由、Firebase、插件注册问题必须 cold restart 或重装验证。
- 不在多个 Provider/Bloc 间复制同一业务字段，避免刷新一处、展示另一处。
- 用 null 表示 loading、empty、error 三种状态会让页面误判；状态模型必须可枚举、可测试、可回放。
- BuildContext 跨 await、跨 isolate、跨 overlay、跨 nested navigator 使用前必须确认来源和生命周期。
- PlatformChannel 的 Map 参数在 Android/iOS 类型宽松度不同，数字、bool、null、list/map 嵌套必须做双端兼容验证。
- 生成文件、Pod、Gradle cache、pub cache 可清理验证，但不能把“清缓存”当根因。
- 离线缓存、崩溃符号化、Web history、桌面窗口、a11y/i18n 属于线上质量，不是发布后再补的边角。

## 输出要求

- 必报：Flutter/Dart 版本、Flutter channel/FVM、目标平台、设备、入口文件/路由、涉及状态方案、插件/原生配置、复现路径。
- 必报：改动文件、关键行、调用方/消费方、影响面、验证命令和结果。
- 数据必报：本地存储类型、缓存失效、迁移、冲突、弱网/离线、登出清理和敏感字段处理。
- 页面必报：状态所有者、loading/error/empty/permission/offline、表单校验、防重复提交、离开页面后的异步处理。
- 平台必报：PlatformChannel 方法、参数 DTO、错误码映射、权限拒绝、真机日志和 Android/iOS 差异。
- 性能必报：baseline、profile trace/DevTools/Firebase Test Lab 工具、关键指标、优化前后对比、未覆盖设备。
- 打包发布必报：flavor、签名、bundleId/applicationId、构建命令、失败 root cause、产物、mapping/dSYM、审核/权限风险。
- Web/Desktop 必报：浏览器/系统、窗口尺寸、权限能力、history/快捷键/文件行为和未覆盖平台。
- 未验证必须标“未验证”，不得把未跑的 flutter test/build/analyze 写成已通过。

## 约束

- 不改与目标无关的架构、状态方案、主题系统、路由系统和插件版本。
- 不在证据不足时升级 Flutter、Dart、AGP、Kotlin、Xcode、CocoaPods 或大版本插件。
- 不绕过签名、权限、审核、隐私提示；不删除平台配置来“让编译过”。
- 不把服务端事实、权限判断、金额价格、租户归属、会员状态交给 Flutter 端决定。
- 不用 debug/simulator/hot reload 验收 release、签名、混淆、权限、推送、相机、支付和后台链路。
- 不把 Android/iOS/Web/Desktop 原生问题完全归入 Flutter；跨边界时调用对应相邻技能。
- 不新增本地文档总结，交付信息直接写在回复中。

## 高频 Bug 反例库

- 反例 1：错法 / 在 build 里创建 FutureBuilder 的 future 并请求接口；对法 / future 在 initState 或状态层创建并可取消；根因 / Widget rebuild 会重复触发副作用。
- 反例 2：错法 / setState 后直接认为全局列表已刷新；对法 / 用 Riverpod/Bloc 统一刷新事件和缓存失效；根因 / 局部 State 与业务状态源分裂。
- 反例 3：错法 / go_router redirect 未等登录态加载完就跳登录；对法 / 增加 unknown 状态和 refreshListenable；根因 / 初始化竞态导致重定向循环。
- 反例 4：错法 / await 请求后无 mounted 检查就 Navigator.pop；对法 / 检查 mounted、当前路由和请求序号；根因 / 页面销毁后仍操作 context。
- 反例 5：错法 / ListView 放 Column 里只加 shrinkWrap 解决；对法 / 重构为 Expanded 或 CustomScrollView/Sliver；根因 / 无界约束与高成本布局被掩盖。
- 反例 6：错法 / 卡顿只批量加 const；对法 / 用 DevTools 区分 Widget rebuild、layout、paint、raster、shader jank；根因 / 性能瓶颈不一定在 Dart rebuild。
- 反例 7：错法 / MethodChannel 只看 Dart PlatformException；对法 / 同步读 logcat/Xcode console 和原生栈；根因 / 原生线程、权限或生命周期才是 root cause。
- 反例 8：错法 / PlatformView 黑屏就换插件版本；对法 / 查 hybrid composition、Texture、z-order、页面复用和 dispose；根因 / 平台视图合成链路与普通 Widget 不同。
- 反例 9：错法 / iOS Pod 报错直接删 Podfile.lock；对法 / 对齐 Xcode/CocoaPods/deployment target/Swift 版本后再 pod install；根因 / 依赖矩阵冲突不是锁文件本身。
- 反例 10：错法 / Android 构建失败就降 compileSdk；对法 / 查 AGP/Gradle/JDK/Kotlin/namespace/minSdk 矩阵；根因 / 新插件依赖新版 Android 构建约束。
- 反例 11：错法 / Firebase 推送收不到只改 Dart 监听；对法 / 校验 APNs、Android channel、权限、flavor 配置和 payload；根因 / 推送链路跨 Firebase、系统权限和原生配置。
- 反例 12：错法 / Material 3 迁移后用固定高度硬压旧样式；对法 / 调整 ThemeData、ColorScheme、组件主题和设计确认；根因 / 组件默认 token 与交互规范变了。
- 反例 13：错法 / deferred components 加载失败就把资源移回首包；对法 / 查 Play delivery 配置、路由访问时机和资源声明；根因 / 延迟模块下载/安装/引用边界未闭合。
- 反例 14：错法 / shader jank 靠预热所有动画资源；对法 / 先定位 shader compilation、图片解码、过度裁剪或平台视图合成；根因 / 盲目预热可能增加启动和内存压力。
- 反例 15：错法 / 离线缓存只写 shared_preferences；对法 / 设计 TTL、schema 迁移、冲突合并和清理策略；根因 / 配置存储不能替代业务缓存层。
- 反例 16：错法 / 乐观更新失败后只弹 toast；对法 / 回滚 UI、记录幂等键、重试队列和冲突状态；根因 / 弱网下本地与服务端事实源分裂。
- 反例 17：错法 / Crashlytics 接入后不上传 dSYM/mapping；对法 / CI 上传符号表并验证 release 崩溃可符号化；根因 / 未符号化日志无法定位线上栈。
- 反例 18：错法 / golden test 使用本机字体和默认 locale；对法 / 锁字体、locale、textScale、尺寸和主题；根因 / 渲染环境漂移导致截图 flaky。
- 反例 19：错法 / Web 端直接复用移动端 deep link；对法 / 单独验证 URL strategy、browser history、刷新和返回；根因 / 浏览器导航模型不同于移动路由栈。
- 反例 20：错法 / Android edge-to-edge 后只调按钮 padding；对法 / 系统处理 insets、SafeArea、IME 和导航栏对比；根因 / 系统栏策略变化影响全局布局。
- 反例 21：错法 / iOS 隐私清单和权限文案上线前才补；对法 / 开发阶段同步维护 Info.plist、PrivacyInfo 和审核说明；根因 / 本地可跑不代表 TestFlight/审核通过。
- 反例 22：错法 / 桌面端使用移动端固定宽布局；对法 / 处理窗口缩放、快捷键、焦点、菜单和大屏导航；根因 / Desktop 交互与窗口模型不同。
- 反例 23：错法 / 用 null 同时代表加载中、空数据和接口失败；对法 / 建模 loading/empty/error/offline/permission 状态；根因 / UI 无法区分真实业务状态。
- 反例 24：错法 / 表单提交直接传整个 controller/model；对法 / 白名单组装 DTO 并过滤客户端不可决定字段；根因 / mass assignment 会污染权限、价格和归属。
- 反例 25：错法 / async 回来后直接 showDialog 或 Navigator.push；对法 / 检查 mounted、当前路由、请求序号和 nested navigator；根因 / BuildContext 生命周期已失效。
- 反例 26：错法 / EventChannel 页面离开后仍持续推送；对法 / cancel 订阅并释放原生监听；根因 / stream 生命周期不跟随 Widget 自动结束。
- 反例 27：错法 / PlatformChannel 把所有原生失败都映射成 -1；对法 / 建错误码表、权限态、超时态和可恢复动作；根因 / Dart UI 无法给出正确恢复路径。
- 反例 28：错法 / 只在 Chrome/debug 验证下载和文件预览；对法 / Android/iOS release 真机验证权限、存储、MIME 和分享入口；根因 / 平台能力和构建模式差异被漏掉。
- 反例 29：错法 / token 和完整接口响应写入 debugPrint/Crashlytics breadcrumb；对法 / 日志字段白名单和脱敏；根因 / 端侧日志会进入设备、CI 和第三方平台。
- 反例 30：错法 / release 崩溃用 debug 包复现失败就关闭混淆；对法 / 保留 release/profile 真机、mapping/dSYM/symbols 和最小复现；根因 / 构建模式差异就是问题现场。

## 提交前自检清单

- 已确认 Flutter 3.x、Dart 3、Flutter channel、FVM、Gradle/Kotlin/JDK、Xcode、CocoaPods、插件版本与目标平台。
- 已列出入口、路由、状态所有者、目标页面、调用方和消费方。
- 已完成单技能开发闭环门禁：页面/状态/路由/API/本地存储/平台能力/构建发布涉及面均有失败态和验证证据。
- 表单、空值、错误、loading、empty、permission denied、offline、retry、防重复提交已覆盖或明确未涉及。
- 客户端 payload 已做白名单映射，未直接信任 userId、price、role、owner、tenant、isPaid 等服务端事实字段。
- build 中无新副作用；controller/focusNode/animation/stream/timer/subscription 已释放。
- Riverpod/Bloc/Provider/GetX/MobX 刷新、取消、错误、重试、离开页面后返回已覆盖。
- Navigator 2.0/go_router 深链、鉴权、返回栈、嵌套路由、Web history 已检查。
- PlatformView/MethodChannel/EventChannel 涉及 typed DTO、错误映射、超时、原生日志、权限、生命周期和线程证据已齐。
- Material 3、SafeArea、键盘、横屏/平板/折叠屏/桌面窗口、暗色模式未被破坏或已声明未测。
- a11y、i18n、RTL、textScale、语义标签、locale fallback 已验证或明确未验证。
- 本地存储、离线缓存、迁移、冲突、弱网、登出清理和敏感数据处理已检查。
- Impeller/Skia、shader jank、Widget rebuild 性能结论有 DevTools 或构建产物证据。
- 错误上报、日志脱敏、Crashlytics/Sentry、mapping/dSYM/split-debug-info 状态已确认。
- Android/iOS/Web/Desktop 打包签名、flavor、Firebase 配置、deferred components 未被误改；profile/release 真机证据已记录或明确未跑。
- 已运行或明确未运行 dart format --set-exit-if-changed、flutter analyze fatal-warnings、lint、flutter test --coverage、random seed、codegen diff、目标平台 build/integration test。

## 2024-2026 新坑速查

- Flutter/Dart：Flutter 3.x 持续升级带来 Material 3 默认行为、Impeller 默认路径、插件 API 变化；Dart 3 records/patterns/sealed/final class 会影响序列化、泛型和 exhaustive switch。
- Android：AGP 8+ 强制 namespace、JDK 17、Kotlin/Gradle 矩阵更严格；Android 13/14/15 权限、通知、照片、前台服务、精确闹钟、后台启动、edge-to-edge 限制会影响插件和布局。
- iOS：iOS 17/18、Xcode 15/16、隐私清单、签名、最低系统版本、Swift 编译设置会让旧 Pod 或二进制插件失败。
- CocoaPods/CI：CocoaPods CDN、Ruby、arm64 simulator、static/dynamic framework、CI 镜像和缓存 key 会导致同一 Pod 在 CI 和本机结果不同。
- 渲染：Impeller 与 Skia 对 shader、滤镜、裁剪、PlatformView 的性能特征不同，不能用一个平台结论覆盖全部。
- 路由：go_router 新版本 redirect、ShellRoute、StatefulShellRoute、browser history 变化会影响登录态、Tab 栈和 Web 返回。
- 发布：Firebase 多 flavor、隐私清单、Play/App Store 权限说明、AAB/IPA 符号表、pana/pub score、semver/migration、monorepo path filter 和 CI secrets 需要与每个平台环境一致。
- 动态交付：deferred components 与 Play Feature Delivery、资源声明、路由懒加载强绑定，调试包通过不代表商店包通过。

## 与相邻技能的边界

- 品牌与视觉方向/brand-visual-direction（b）：负责产品视觉方向、品牌调性、设计取舍；Flutter 开发/flutter-development（fltr） 只落实 Flutter 技术可行性和实现风险。
- UI 架构/ui-architecture（a）：负责页面结构、多端布局信息架构、组件层级方案；Flutter 开发/flutter-development（fltr） 负责 Widget、状态、路由和平台差异实现。
- UI 设计实现/ui-design（u）：负责颜色、间距、字体、图标、Material 3 视觉规范；Flutter 开发/flutter-development（fltr） 负责主题落地、约束、适配和渲染问题。
- Android 开发/android-development（andr）：负责 Android 原生 Manifest、Activity、Service、Gradle/Kotlin、权限、签名、插件原生实现；Flutter 开发/flutter-development（fltr） 负责 Dart 侧调用、插件接入和跨端联调。
- Apple 全链路开发与发布/apple-development（appl）：负责 Info.plist、entitlements、Xcode signing、CocoaPods、Swift/ObjC、iOS capabilities；Flutter 开发/flutter-development（fltr） 负责 Dart 侧、Pod 集成触发点和 Flutter 构建链路。
- API 工程/api-engineering（api）：负责接口契约、状态码、鉴权、分页、错误模型；Flutter 开发/flutter-development（fltr） 负责端侧请求、解析、缓存、重试、UI 状态呈现。
- 数据库工程/database-engineering（db）：负责持久化模型、迁移、事务和数据一致性原则；Flutter 开发/flutter-development（fltr） 负责 Flutter 本地存储接入、端侧缓存策略和离线体验。
- 可观测性/observability（obs）：负责日志、指标、Trace、SLO、告警和线上定位体系；Flutter 开发/flutter-development（fltr） 负责 Flutter 端异常捕获、性能 trace 和符号化接入证据。
- Web 安全/web-security（wsec）：负责 Web/CORS/OAuth/JWT/XSS/CSRF 等安全边界；Flutter 开发/flutter-development（fltr） 负责端侧安全调用、Web 构建差异和敏感信息不落日志。
- 测试验证/test-engineering（tst）：负责测试矩阵、自动化策略、回归覆盖和验收；Flutter 开发/flutter-development（fltr） 提供 Flutter 场景、风险点和本地验证证据。
- 代码审计/code-audit（aud）：负责改动后全局质量、安全、影响面收口；Flutter 开发/flutter-development（fltr） 不替代最终审计。