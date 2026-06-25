---
name: apple-development
description: Apple 平台真实开发与发布上架技能：覆盖 iOS/iPadOS/macOS/watchOS/tvOS/visionOS、Swift/SwiftUI/UIKit/AppKit、Xcode、签名证书、Provisioning Profile、Info.plist、entitlements、Privacy Manifest、APNs、StoreKit 2、App Store Connect、TestFlight、App Review、Crash/MetricKit/Instruments、Apple 相关 API 与服务端联动。修改 .swift/.xib/.storyboard/.plist/.entitlements/.xcworkspace/.xcodeproj、Apple 原生能力、上架审核、签名发布、StoreKit/APNs/Keychain/CloudKit/Widget/Live Activity 时使用。
---

# Apple 全链路开发与发布

Apple 全链路开发与发布（apple-development，兼容 slug: appl）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

## 定位 / 适用范围

本技能用于 Apple 生态真实项目的一次性开发、排障、测试、签名、发布和审核准备，目标是减少“本地能跑但真机/CI/TestFlight/审核失败”的返工。

策略：Apple 生态只保留 `appl` 一个总技能收口，不再按发布、签名、StoreKit、推送、隐私拆子技能；相邻能力通过 `api/be/db/tst/rls/pfe/wsec/msec/aud` 联动，但 Apple 平台判断、证据门禁和上架审核统一在本技能内完成。

适用范围：

- 平台：iOS、iPadOS、macOS、watchOS、tvOS、visionOS；未实际支持的平台必须标“非目标平台”。
- 语言与框架：Swift、Objective-C、SwiftUI、UIKit、AppKit、Combine、Swift Concurrency、Observation、SwiftData、Core Data。
- 工程：Xcode、xcodebuild、XCTest、XCUITest、Test Plan、SPM、CocoaPods、xcframework、fastlane、CI matrix。
- Apple 能力：Info.plist、entitlements、Signing & Capabilities、Provisioning Profile、Keychain、APNs、Associated Domains、Universal Links、CloudKit、iCloud、App Groups、Widget、App Intents、Live Activities、BackgroundTasks、StoreKit 2、Sign in with Apple、Passkeys、WeatherKit、MapKit、HealthKit、HomeKit、CoreLocation、AVFoundation、Photos、NFC。
- 发布：Archive、Export、TestFlight、App Store Connect、App Review Notes、App Privacy、Privacy Manifest、Required Reason API、IAP/订阅、账号删除、UGC、年龄分级、加密出口、ATT、Kids Category、macOS notarization/hardened runtime、崩溃与线上监控。

不适用范围：只读学习 Apple 概念、阅读官方文档、Apple 公司新闻/产品选购/iPhone 支持、普通 Swift 算法题、纯产品文案、Figma 视觉稿、纯后端接口设计、普通 Go/TypeScript 服务端任务、Android/Flutter/React Native 非原生问题、普通网页前端、仅依赖/README/目录出现 iOS/Swift/Xcode、没有 Apple 平台修改/调试/构建/测试/发布动作的任务。

## 铁律

1. 先定平台、系统、Xcode、Swift 语言模式、SDK、target、distribution channel；未定就不能给“已兼容”结论。
2. Apple 平台不能套用 iOS 单平台假设；macOS 沙盒/窗口/菜单、watchOS 电量与后台、tvOS 焦点、visionOS 空间交互必须单独判断。
3. 改能力前必须核 runtime API、Info.plist、entitlements、Developer Portal capability、Provisioning Profile、App Review 说明六者一致。
4. 每个 signed target 独立核对；主 App 配好不代表 Widget、Watch App、Share Extension、Notification Extension、App Clip、XPC/helper 已配好。
5. SwiftUI/UIKit/AppKit UI 状态更新默认 MainActor；跨 callback、delegate、Task、actor 回 UI 必须显式收口。
6. StoreKit 2 不信本地布尔值；必须处理 verified transaction、Transaction.updates、currentEntitlements、finish、restore、pending、revoked、expired、refund。
7. APNs 不把 sandbox、production、topic、bundle id、push type、device token 混用；TestFlight/生产要单独验证。
8. Privacy Manifest 和 App Privacy 必须与真实采集、SDK、Required Reason API、权限文案、隐私政策一致；源码存在不等于 archive 已打包。
9. Simulator、Preview、Debug、StoreKit Configuration 只能作辅助证据，不能替代真机、Release、Sandbox/TestFlight、Archive/App Review 证据。
10. 不用清 DerivedData、降 Swift 并发检查、关闭 ATS、全局信任证书、删 profile、重装 Xcode 当作修复；这些最多是诊断手段。
11. Token、密钥、session、支付凭证、证书私钥不进 UserDefaults、日志、剪贴板、URL query、截图或回复。
12. 涉及发布、账号、证书、App Store Connect、外部可见改动时先确认授权和影响面。
13. 不按审核账号、地区、时间、远程配置隐藏或切换审核后功能；远程开关不得启用未披露能力。
14. 服务端自称“验证过”不算证据；Apple 登录、StoreKit、APNs 等服务端结果必须核 issuer/audience/bundleId/environment、时间戳、nonce、重放保护和幂等。
15. 不把 Preview、Simulator、Debug、本地 .storekit、单一设备、单一系统版本当成交付完成；上线口径必须落到真机、Release、Archive、Sandbox/TestFlight 或线上证据。
16. 不只改主 target；任何 capability、permission、privacy、signing、build setting、依赖资源变化，都要同步核 extension、watch app、widget、notification service、app clip、helper 和 test target。
17. 不用“能编译”替代“可使用”；每个用户可见功能必须有空态、加载态、错误态、取消态、权限拒绝态、旧系统 fallback、升级路径和无网/弱网退路。
18. 不隐藏低置信度；没跑 Archive、TestFlight、真机 Release、服务端回调或审核路径时，只能写“未验证/需补证据”。

## 快速总则

- 入口：先搜 scheme、target、Info.plist、entitlements、Package.resolved、Podfile.lock、build settings、CI、fastlane、App Store Connect 依赖。
- 影响面：按 App target、extension target、watch/tv/mac/vision variant、Debug/Release、Ad Hoc/App Store/TestFlight 分组。
- 版本：新 API 必须写 availability、最低系统、fallback 或非目标平台说明。
- 状态：SwiftUI 明确 @State/@Binding/@StateObject/@ObservedObject/Observable 所有权，禁止把外部真相源复制成旧快照。
- 并发：优先结构化并发；Task 生命周期绑定页面/服务；跨 await 后重检对象仍有效；Swift 6 诊断不能靠 unchecked Sendable 糊掉。
- UI：自绘按钮、列表行、chip、toolbar、hover/disabled 区域必须验证视觉容器与 hit target 一致，并覆盖 VoiceOver、Dynamic Type、Reduce Motion、对比度、RTL、本地化；图标按钮保留可访问文本，颜色不能作为唯一状态表达。
- 网络：URLSession 同时看 HTTP 状态、业务错误、取消、超时、401 刷新去重、URLSessionTaskMetrics、ATS、证书策略。
- 数据：SwiftData/Core Data 迁移要用旧版本样本验证；CloudKit/iCloud 要定义真相源、冲突、删除传播、账号切换、离线恢复。
- 构建：锁依赖，记录 Xcode/SDK、xcode-select、scheme、configuration、destination、CI matrix 和 result bundle；本地绿不能替代 CI、Archive、真机 Release。
- 发布：TestFlight、App Review Notes、App Privacy、审核账号、恢复购买、账号删除、UGC、权限拒绝态、隐私政策都要证据化。

## 单技能开发闭环门禁

当用户要求“写一个 Apple 功能/页面/系统/模块出来”时，本技能必须自己把低级错拦住；不能只写 Swift 代码再把 API、DB、测试、发布全部留给组合技能。

1. 需求闭环：把入口、目标用户、平台、target、数据来源、权限、联网、离线、错误、空态、升级、发布渠道列成清单；未知项先标需确认，不默认补脑。
2. 工程入口：先定位 scheme、target、scene/app delegate、路由/导航、状态容器、网络层、本地存储、权限申请点、依赖锁、CI/fastlane；找不到入口不得直接新建平行实现。
3. 状态闭环：SwiftUI 必须说明谁拥有真相源；`@StateObject` 只在拥有者创建，`@ObservedObject`/`@Bindable` 只消费外部对象，`@State` 不复制服务端或数据库长期真相源。
4. 并发闭环：异步入口必须有取消、去重、超时、错误传播和 UI 回主线程策略；页面消失、用户重复点击、任务重入、对象释放后不得继续写 UI 或提交旧结果。
5. 权限闭环：先检查权限状态，再请求权限；必须有允许、拒绝、受限、系统设置关闭、再次进入的 UI 和业务 fallback；Info.plist 文案不能与真实用途不一致。
6. 数据闭环：SwiftData/Core Data/UserDefaults/Keychain/文件存储要明确 schema、迁移、默认值、回滚、加密/保护级别、App Group 路径和旧版本样本验证。
7. 网络闭环：请求必须处理 HTTP 状态、业务错误、取消、超时、401 刷新互斥、重试边界、幂等、日志脱敏、ATS 和证书策略；不得吞错后给成功 UI。
8. 服务端闭环：StoreKit、APNs、Sign in with Apple、Passkeys、CloudKit/自研同步、远程配置必须核客户端环境与服务端契约；客户端自报支付、登录或推送结果不算可信。
9. 发布闭环：涉及用户可见能力时同步检查 Archive 资源、Privacy Manifest、App Privacy、Review Notes、审核账号、TestFlight 冒烟、旧系统 fallback 和 Release 配置。
10. 收口闭环：输出必须分成已验证、部分验证、未验证；每个未验证项写下一步证据，不得用“应该可以”“看起来没问题”收尾。

## 禁止低级错清单

- 禁止在 `body`、computed property、cell reuse、view update 中发网络、写数据库、申请权限或创建长期任务。
- 禁止把 `Task.detached` 当后台万能入口；需要 UI、Core Data context、URLSession delegate、App lifecycle 的任务必须有隔离和生命周期归属。
- 禁止用 `try?`、空 catch、默认成功 toast、静默 return 掩盖支付、登录、权限、同步、迁移、推送失败。
- 禁止把 token、refresh token、session、authorization header、JWS、p8、证书路径、Keychain item、个人数据写进日志、截图、崩溃附件或回复。
- 禁止为了临时跑通而关闭 ATS、允许任意证书、禁用 sandbox/hardened runtime、降低 deployment target 判断、关闭 Swift concurrency 诊断、移除隐私声明。
- 禁止只配置 Debug 或主 App；Release、App Store/TestFlight、extension、widget、watch、app clip、helper 都要按影响面复核。
- 禁止新增权限、追踪、第三方 SDK、AI 上传、后台模式、外部购买、UGC、儿童场景而不补隐私、审核和拒绝态证据。
- 禁止只按最新 iOS/macOS 写法实现；低于目标系统的新 API 必须有 availability、fallback 或明确非目标平台说明。

## 强制流程

1. 任务定界：确认平台、target、系统版本、Xcode/Swift、是否发布/审核/线上问题、是否影响证书账号或 App Store Connect。
2. 证据收集：读取错误日志、crash、xcodebuild、archive/export、TestFlight、App Review 拒信、MetricKit、Crashlytics、Console、Device Logs；没有证据先标缺口。
3. 入口搜索：全量查调用方、target、scheme、Info.plist、entitlements、capability、依赖锁、CI/fastlane、App Store Connect 配置影响。
4. 最小修改：只改与目标有关的代码和配置；不顺手重构；不引入第三方库，除非明确收益大于隐私、体积、维护和审核风险。
5. Apple 能力对齐：代码、权限文案、entitlement、profile、developer portal、review notes、privacy manifest、server capability 同步核对。
6. 测试矩阵：至少区分 Simulator/real device、Debug/Release、旧系统/目标系统、权限允许/拒绝、弱网/离线、后台/冷启动、升级安装。
7. 发布门禁：需要上架时必须跑 Archive/export/TestFlight 冒烟，核 App Privacy、PrivacyInfo.xcprivacy、IAP、审核账号、恢复购买、账号删除、隐私政策、UGC。
8. 收口输出：按“已验证/部分验证/无法验证/需补证据”分档，不把未跑链路说成通过。

## 场景执行卡

### SwiftUI / UIKit / AppKit 页面与交互

- 动作：核状态所有权、生命周期、导航栈、sheet/popover 竞争、delegate/coordinator 引用、observer/timer/task 释放、MainActor 边界；现代 SwiftUI 优先 `@Observable`，共享状态类需 `@MainActor`，拥有者用 `@State`/`@StateObject`，传递用 `@Binding`/`@Bindable`/`@Environment`；Swift/ObjC 混编需核 bridging header、module map、nullability、Swift name 导出、ObjC category/linker flags、ARC/MRC 边界、KVO/KVC selector 字符串和 Swift concurrency 回调隔离。
- 结构：`body` 过长、复杂 `some View` 计算属性、长期 `@ViewBuilder` helper、多个大型类型塞同一文件都要拆；Button action、`.task`、`onAppear` 不塞业务逻辑，抽到方法/ViewModel 便于测试。
- 导航/表单/动画：禁新代码继续用 `NavigationView`；同层级不要混用旧 `NavigationLink(destination:)` 与 `navigationDestination(for:)`；同一数据类型 destination 只注册一次；optional 数据弹层优先 `sheet(item:)`；避免在 `body` 临时创建有副作用的 `Binding(get:set:)`，数字输入优先 `TextField(value:format:)`；`.animation` 必须带明确 `value`，Reduce Motion 下大位移动画要降级。
- 布局/可访问性/性能：避免 `UIScreen.main.bounds` 和无边界 `GeometryReader`；优先现代布局 API、lazy 容器和稳定 identity；固定 frame 必须证明 Dynamic Type/多设备可容纳；图标按钮必须有可访问 label，装饰图隐藏，信息图补 label；避免 `AnyView`、在 `body`/`ForEach` 中排序过滤和无失效逻辑的派生缓存。
- 验证：主路径、快速进出、多次打开关闭、旋转/窗口尺寸、多窗口、键盘/鼠标/遥控器/空间输入、VoiceOver、Dynamic Type、RTL、Reduce Motion、权限弹窗打断、异步返回后页面已消失。
- 易错：body 做副作用、重复创建 ViewModel、把 `@ObservedObject` 当拥有者、把 `@State` 当服务端缓存、UIViewControllerRepresentable 重建状态、AppKit window 被提前释放、Button 只有图标可点、`onTapGesture` 冒充按钮但缺 trait、用颜色作为唯一状态、ObjC selector 字符串重构后运行期才崩。

### watchOS / Apple Watch / WatchConnectivity

- 动作：涉及 watchOS 时单独核 Watch App/Extension target、独立 Watch App vs companion app、WCSession 可达性、background transfer、App Group 数据边界、Smart Stack/complication timeline、RelevanceKit、Workout/extended runtime、HealthKit/传感器权限、Digital Crown/AssistiveTouch/Double Tap、低电量/锁屏/离腕状态。
- 验证：不能用 iOS 真机结果替代 watchOS；至少覆盖 paired/unpaired、iPhone reachable/unreachable、前台/后台、蓝牙/网络切换、低电量、锁屏/离腕、传输重试、timeline reload budget、系统预算过期、TestFlight 真表。
- 易错：把 iOS 后台网络/轮询套到 watchOS、WCSession 只测 reachable、complication 依赖主 App 内存、Workout/HealthKit 权限与后台模式缺失、复杂动画和高频刷新耗电。

### 权限 / Info.plist / entitlements / 签名

- 动作：逐 target 核 Usage Description、capability、entitlements、App ID、Provisioning Profile、certificate、Team ID、bundle id、Debug/Release 差异。
- 验证：首次授权、拒绝、受限、设置页关闭后回流、无权限业务 fallback、真机安装、archive/export、最终 signed entitlements、embedded profile。
- 易错：先调用能力再解释权限、Info.plist 文案和实际用途不一致、拒绝态死路、主 App 有 entitlement 但 Extension 没有、自动签名未刷新 profile、restricted entitlement 需要 Apple 审批却假设本地可开。

### 网络 / 登录 / Keychain / Passkeys

- 动作：核 URLSession 封装、token 刷新、并发刷新去重、Keychain access group、accessibility、SecAccessControl、biometryCurrentSet、ThisDeviceOnly、iCloud Keychain 同步预期、Sign in with Apple nonce/state、ASWebAuthenticationSession 回调、Passkeys 撤销/换设备；证书 pinning 需有轮换、过期、灾备和失败遥测。
- 验证：弱网、离线、超时、401/403、token 过期、并发请求同时刷新、重装/升级、锁屏态、取消登录、凭证撤销、账号合并/解绑、URLSessionTaskMetrics、errSecInteractionNotAllowed、access group 迁移。
- 易错：UserDefaults 存 token、日志打印 header、URL query 带敏感参数、ATS 全局放开、pin 到易失 leaf cert 且无轮换、证书校验绕过、Keychain access group 改动后旧 item 读不到、Sign in with Apple 不校验 nonce/state。

### 本地数据 / SwiftData / Core Data / CloudKit

- 动作：核模型版本、默认值、兼容解码、migration、context/actor 边界、App Group 路径、文件保护、CloudKit container/environment、schema migration/deploy、zones/subscriptions、CKShare、quota、partial failure、server change token 失效、conflict policy、账号切换。
- 验证：首次安装、旧版本升级、异常数据、低存储、清缓存、双设备同步、离线后恢复、删除传播、服务端限流、CloudKit partial failure 和 token reset、Release 真机迁移样本。
- 易错：新增非可选字段崩旧数据、默认值只在新安装生效、context 跨线程、预览数据污染生产逻辑、CloudKit schema 未 deploy 到 production、删除不传播、watch/iOS 共享数据时序错。

### 并发 / 后台任务 / 系统预算

- 动作：核 Task 生命周期、取消点、actor isolation、Sendable、BGTaskScheduler identifier、Info.plist、后台模式、register 时机、setTaskCompleted、earliestBeginDate、过期处理、低电量策略；Swift 6 strict concurrency 命中时记录 `SWIFT_VERSION`、`SWIFT_STRICT_CONCURRENCY`、target/configuration 差异。
- 验证：重复点击、取消、快速进出页面、后台/前台、系统杀进程、低电量、模拟触发/过期测试、TSAN、strict concurrency、CI matrix。
- 易错：Task.detached 写 UI、nonisolated 绕隔离、`@preconcurrency`/`@unchecked Sendable` 全局糊住数据竞争、BGTask register 晚于 launch 完成、忘记 setTaskCompleted、BGTask 当定时器、静默推送期望实时。

### Swift Testing / XCTest / XCUITest / Test Plan

- 动作：区分 Swift Testing、XCTest、XCUITest 和 Test Plan；Swift Testing 覆盖 `@Test`、`#expect`/`#require`、async/throws、MainActor/actor 隔离、参数化测试；迁移期说明与 XCTest/Test Plan 共存边界。
- 验证：核心路径、错误路径、权限弹窗、StoreKit/推送/登录/迁移/弱网/升级用测试或手工证据覆盖；UI test 不用固定 sleep，异步测试用 expectation/confirmation；测试产物保存 `.xcresult`、截图、日志和失败重现命令。
- 易错：只有 Preview 或手工点一点、测试无断言、`try?` 吞错、UI test 靠 `sleep`、XCTestCase 在 Swift 6 MainActor 默认隔离下未显式处理、真实网络/真实 App Store 依赖导致 CI flaky。

### StoreKit 2 / IAP / 订阅 / 服务端验真

- 动作：核 product id、订阅组、价格/周期/试用、Transaction.updates、currentEntitlements、finish、restore、pending、revoked、expired、billing retry、App Store Server API、App Store Server Notifications v2、JWS 验签、服务端验真。
- 验证：StoreKit Testing、Sandbox、TestFlight、购买、取消、pending、恢复、续费、退款/撤权、跨设备、断网恢复、审核账号、服务端通知幂等与重放保护。
- 易错：只测 .storekit、不测 Sandbox/TestFlight；退款后不撤权；恢复购买入口隐藏；消耗品按非消耗品恢复；客户端永久发权益；服务端不验 JWS 或通知不幂等。

### APNs / Universal Links / App Intents / Widget / Live Activities

- 动作：核 APNs environment、topic、push type、collapse id、device token 上报、mutable-content、Notification Service/Content Extension、interruption level、relevance score、critical alert entitlement、VoIP Push/CallKit 合规、Associated Domains、AASA components/path 优先级、多 appID、URL scheme、Scene routing、App Group、supportedFamilies、reload budget、placeholder/snapshot/timeline、extension memory、ActivityKit push token、staleDate、end dismissalPolicy。
- 验证：真机推送、前台/后台/杀进程、冷启动、未登录/无权限、低电量、锁屏、Universal Link 网页回退、swcd 日志、用户手动禁用后的 fallback、Widget timeline、Intent 参数、TestFlight。
- 易错：sandbox/prod token 混用、AASA content-type/CDN 缓存错误、content-available 期望实时、critical alert 未获 entitlement、Widget 依赖主 App 内存、Live Activity 更新频率超预算。

### Xcode / 依赖 / CI / fastlane

- 动作：核 Xcode 版本、xcode-select、scheme、build configuration、xcconfig 继承、build settings、deployment target、architectures、OTHER_LDFLAGS、DEAD_CODE_STRIPPING、ENABLE_USER_SCRIPT_SANDBOXING、EXCLUDED_ARCHS、Build Phases 顺序、Run Script 输入输出声明、Package.resolved、Podfile.lock、Ruby/CocoaPods/Bundler 版本、PrivacyInfo.xcprivacy 打包、xcframework slice、fastlane match/sigh/gym/scan/pilot/precheck。
- 验证：xcodebuild 命令必须记录 scheme/configuration/destination，必要时跑 `-showBuildSettings`、`-resolvePackageDependencies`、`-resultBundlePath` 并保存 `.xcresult`；验证 test plan、archive/export、CI matrix、Release 真机、TestFlight processing、fastlane 日志；签名需区分 development/ad hoc/app-store/enterprise/profile 类型，核 UUID、expiration、device list、capability propagation、exportOptions.plist method/team/signingStyle。
- 易错：本地 Xcode 与 CI 不一致、只改 Debug 配置、SPM binary 缓存、未锁 Package.resolved/Podfile.lock、CI cache key 未绑定 Xcode 和 lockfile hash、Pods script phase、simulator 可编真机不可编、privacy manifest 源码有但未进 archive、Run Script 没输入输出导致 CI 不稳定、extension target 漏资源或签名。

### Crash / 性能 / MetricKit / Instruments

- 动作：先符号化；按 crash、hang、OOM、启动、掉帧、泄漏、线程竞争、网络阶段耗时、能耗分类；用 os.Logger/signpost/Points of Interest 建证据；若项目提供 xclog/xcsym/自定义 console/crash 工具，优先用项目工具采集 device logs、simulator logs、.ips、MetricKit、.crash 证据并记录命令。
- 验证：dSYM 上传、Crashlytics/Organizer/MetricKit、MXDiagnosticPayload、crash/hang/OOM payload 关联版本和 build、Time Profiler、Allocations、Leaks、Thread Sanitizer、Hangs、Animation Hitches、Energy Log、Network Instruments、Release 真机对比。
- 易错：无 dSYM 靠地址猜、只看均值不看 p95/p99、Simulator 性能当真机结论、没有把 crash/hang/OOM 与版本/build/设备分布关联、闭包/Timer/Task/observer 强引用。

### App Store Connect / TestFlight / App Review / 上架

- 动作：核 bundle id、SKU、primary locale、category、age rating、content rights、availability/pricing、phased release、version/build number、export compliance、metadata、app name/subtitle/promotional text/description/keywords/support URL/marketing URL、截图、app previews、隐私政策、App Privacy、tracking domains、PrivacyInfo.xcprivacy、Required Reason API、SDK privacy manifest、IAP/订阅 display name/description/本地化/价格/intro offer/promotional offer/grace period/billing retry/terms、审核账号、Review Notes、账号删除、UGC 举报/屏蔽/拉黑/过滤/内容审核/联系渠道、ATT、Kids Category、外部购买 entitlement。
- 平台矩阵：发布证据按 iOS/iPadOS/tvOS/visionOS App Store、macOS App Store sandbox、macOS Developer ID、TestFlight 内测/外测、Beta App Review 拆分；macOS Developer ID 需核 archive/export、hardened runtime、notarytool 日志、staple、Gatekeeper 首启、quarantine、XPC/helper/嵌套 framework 签名与 notarization。
- 验证：Archive 内容、exportOptions、TestFlight 内测/外测、Beta App Review、beta description、feedback email、测试信息、分组、设备/OS 覆盖、崩溃反馈、App Review Notes 可复现步骤、恢复购买/管理订阅、权限拒绝态、无账号路径、账号删除范围与保留数据说明、隐私同意/撤回、UGC 审核路径、notarization 日志；PrivacyInfo.xcprivacy 以最终 archive/bundle 为准，主 App、watch app、extension、widget、SPM/CocoaPods、xcframework/binary framework 都要核是否随包进入。
- 易错：TestFlight 当作不用审核；隐藏功能未披露；测试账号不可用；metadata 与实际功能不一致；隐私采集与 App Privacy 不一致；有账号创建但 App 内无删除入口；登录墙无必要；订阅条款不清楚；Kids Category 接入不合规广告/分析/追踪；ATT 同意前已追踪；未获 entitlement 就放外部购买链接；`codesign --deep` 掩盖嵌套二进制签名错误。

### Apple API 与服务端接口联动

- 动作：把 Apple 客户端能力与后端契约一起核：APNs provider token/topic、StoreKit server verification、App Store Server API、App Store Server Notifications v2、Sign in with Apple client secret、CloudKit/自研同步真相源、deep link payload、配置下发、feature entitlement；Go/其他后端实现细节交给 `be/godv/api`，但 Apple 环境、验签、幂等和审核披露由 `appl` 兜底。
- 验证：服务端环境区分 sandbox/production、issuer/audience/bundleId/environment、JWS/回调验签、幂等、重放保护、时间戳/nonce、失败重试、灰度配置、审计日志。
- 易错：客户端改 product id 但后端没配；APNs token 环境写错；订阅通知不幂等；Apple 登录撤销不清 session；服务端接受客户端自报结果；远程配置启用未审核功能。

## 验证门禁

- 编译门禁：xcodebuild 或 Xcode build 成功；记录 Xcode、SDK、scheme、configuration、destination。
- 测试门禁：XCTest/XCUITest/Test Plan 覆盖核心路径、权限拒绝、弱网、升级、旧系统；TSAN/ASAN 按风险启用。
- UI 门禁：真机或 Simulator 操作证据；自绘可点击区域、accessibility、本地化、深浅色、动态字体、旋转/窗口尺寸。
- 签名门禁：每个 target 的 bundle id、team、certificate、profile、entitlements、final signed entitlements 一致。
- 隐私门禁：Info.plist usage、PrivacyInfo.xcprivacy、Required Reason API、第三方 SDK、App Privacy、隐私政策一致。
- StoreKit 门禁：StoreKit Testing 之外必须有 Sandbox 或 TestFlight；恢复、退款/撤权、pending、跨设备、订阅生命周期留证据。
- APNs/链接门禁：真机、sandbox/production、topic、push type、AASA、冷启动、后台/杀进程、未登录/无权限验证。
- 发布门禁：Archive/export、TestFlight 冒烟、Beta App Review、审核账号、Review Notes、metadata、IAP/订阅本地化和条款、恢复购买/管理订阅、账号删除、UGC、ATT、Kids Category、年龄分级、加密出口、外部购买 entitlement、macOS notarization/Gatekeeper、App Store Connect 配置截图或记录。
- 性能门禁：性能结论必须来自 Release 真机或线上指标；Instruments/MetricKit/Crashlytics 有前后对比。
- 低级错门禁：每次收口前复核状态所有权、MainActor、取消/重入、权限拒绝态、token/日志、旧系统 fallback、extension target、Release/Archive/TestFlight 证据；任一缺失写入风险和下一步。

## 输出要求

每次使用本技能，输出必须包含：

1. 命中场景卡：说明属于实现、排障、签名、发布、StoreKit、APNs、审核或 API 联动哪类。
2. 平台与版本：目标平台、最低系统、Xcode、Swift、target、真机/模拟器/TestFlight 条件；未知项标“需确认”。
3. 入口与影响面：列出已查 target、文件、调用方、配置、扩展、CI/fastlane/App Store Connect；未查写缺口。
4. 修改或建议：最小必要改动，不夹带无关重构。
5. 证据：编译、测试、日志、crash、Instruments、MetricKit、URLSessionTaskMetrics、Archive、TestFlight、审核拒信；未跑不得说通过。
6. 风险：权限、签名、隐私、并发、生命周期、数据迁移、购买、推送、审核、兼容、服务端契约中的具体风险。
7. 验证方案：正常/异常、允许/拒绝权限、弱网/离线、后台/冷启动、升级、旧系统、真机、Release/TestFlight。
8. 发布证据：若涉及上架，必须写 App Store Connect、App Privacy、Privacy Manifest、Review Notes、审核账号、恢复购买、账号删除、UGC、IAP/TestFlight 状态。
9. 联动技能：需要后端接口、数据库、测试、发布、安全、性能、代码审计时列出相关真实 slug。

## 安全边界

- 可以协助防御性安全、隐私合规、证书/签名排障、App Review 整改、授权项目的 APNs/StoreKit/登录验证。
- 不协助绕过 App Review、按审核账号/地区/时间隐藏功能、规避 IAP、伪造交易、盗用证书、提取他人 profile、绕过 ATS/证书校验上线、规避隐私披露、使用私有 selector/私有 framework/混淆符号规避静态审核、下载/解释/执行会改变 App 功能的代码或脚本。
- 不要求用户粘贴长期密钥；优先环境变量、钥匙串、CI secrets；发现泄露密钥必须建议轮换、撤销、清日志。
- 不输出证书私钥、App Store Connect API key、p8 key、session token、用户隐私数据、完整崩溃日志敏感字段；日志、crash、录屏、截图、审核材料导出前必须脱敏。
- 不建议把支付、订阅、登录、推送的服务端验签/幂等降级到客户端本地判断。
- IDFA、跨 App/站点追踪、指纹识别、SDK tracking 必须先核 ATT、Purpose String 和 App Privacy，同意前禁用；Kids Category/儿童用户默认不得接入行为广告、第三方分析或外链，除非规则明确允许并有家长门控。
- 接入第三方 SDK 或 AI 服务前核数据出境、训练使用、retention、DPA、隐私清单和用户同意；默认不得上传用户内容到 AI 服务。
- 不用“审核可能发现不了”作为方案依据；不确定规则查官方或标需人工确认。

## Swift / Apple 平台陷阱速查（Optional/retain cycle/Concurrency/SwiftUI 独家）

Optional 与 force unwrap：

- Swift `Optional<T>` 显式建模缺失；`T?` 是 `Optional<T>` 简写；不存在 null pointer dereference 概念。
- `!` force unwrap：`x!` 当 x 为 nil 抛 trap（crash with EXC_BAD_INSTRUCTION）；production code 一律避免；用 `guard let x = x else { ... }`、`if let`、`x ?? default`、`x?.method()` safe navigation。
- `as!` force cast 同样 crash；用 `as?` 返回 Optional。
- IUO（implicitly unwrapped optional）`T!`：访问时自动 unwrap，nil 时 crash；IBOutlet/storyboard 用，普通 API 避免。
- `guard let` 早返回模式：`guard let user = user else { return }`；让 happy path 不嵌套；else 分支必须 diverge (return/throw/fatalError/continue)。

retain cycle 与 ARC：

- `Self` reference cycle：closure 默认 strong capture self；闭包内 `self.method()`/`self.property` 形成 closure → self → closure 循环。
- `[weak self]` 让 closure 弱引用 self：闭包内 `self?.method()`；self 已释放时为 nil 不调用。
- `[unowned self]` 让 closure 无主引用：闭包内 `self.method()` 直接调；self 已释放时 crash（不是 nil）。
- 选择：closure 生命周期 ≤ self 用 `[unowned self]`（性能略好）；closure 可能比 self 长用 `[weak self]`。
- 闭包参数同样：`Task { [weak self] in await self?.fetch() }`；deferred callbacks/observers/timer 默认要 `[weak self]`。
- delegate pattern：protocol delegate 一律 `weak var delegate: MyDelegate?`；不 weak 会循环；protocol 需 `: AnyObject` 才能 weak。

Concurrency（Swift 5.5+ async/await + actor）：

- `async`/`await`：非阻塞挂起；只能在 async context 内 await；同步代码调 async 用 `Task { await ... }`。
- `Task { ... }` 新 Task 在 inherited priority 上运行；`Task.detached { }` 不继承 context；记得 cancel（`task.cancel()`）。
- **structured concurrency**：`async let x = ...; async let y = ...; let result = await (x, y)` 并发等待；`withTaskGroup` 动态任务集；子任务自动随父 cancel。
- `actor` 隔离可变状态：actor 内方法默认 isolated（外部访问需 `await`）；非 isolated 用 `nonisolated`；类似 Erlang process 但单线程式 access。
- `@MainActor` 标记必须主线程跑：UI 代码、`@Published`/`@State` 改动；SwiftUI view body 默认 `@MainActor`。
- `Sendable` protocol：表示类型可跨 actor 安全传递；class 默认非 Sendable，要 `final` + 不可变 / 加锁；Swift 6 严格检查。
- `Swift 6` strict concurrency：编译期检查 data race；`@preconcurrency` 标记老代码暂缓；逐 module 启用。

SwiftUI / View 模型：

- `@State` private value type 状态；`@StateObject` ref type 拥有的；`@ObservedObject` ref type 借用的（不要在 view 里 new）；`@EnvironmentObject` 注入式 ref type；`@Environment(\.dismiss)` 系统注入。
- iOS 17+ `@Observable` macro 取代 `ObservableObject` + `@Published`：自动追踪属性；view 用 `@Bindable` 拿绑定。
- `@AppStorage("key")` 直接绑定 UserDefaults；`@SceneStorage` 绑定 scene；`@FocusState` 控制焦点。
- View body 必须 pure：每次重新计算 view 描述；不能有副作用；`onAppear` 做副作用、`task { await ... }` 启动 async。
- 不要在 init 启动 Task；用 `task { }` modifier 跟随 view 生命周期 cancel。
- NavigationStack（iOS 16+）替代 NavigationView；路径数据驱动 `NavigationStack(path: $path)` + `.navigationDestination(for: Type.self) { }`。

Codable / JSON：

- `Codable` = `Encodable & Decodable`；自动生成需所有 stored property 都 Codable；`enum` 默认 Codable 用 case name。
- `JSONDecoder().decode(MyType.self, from: data)` 解码；失败抛 typed error（`keyNotFound`/`valueNotFound`/`typeMismatch`/`dataCorrupted`）。
- 命名映射：`CodingKeys` enum + `case fieldName = "field_name"`；JSONDecoder `keyDecodingStrategy = .convertFromSnakeCase` 全局。
- Date 格式：`dateDecodingStrategy = .iso8601`/`.formatted(formatter)`；中文展示 `DateFormatter` + `locale = Locale(identifier: "zh_CN")` + dateFormat。
- Optional vs missing key：`let x: String?` 字段缺失时 nil；`let x: String?` 显式 null 也是 nil；要区分用 `decodeIfPresent` + manual coding。

UIKit / AppKit 与 SwiftUI 互操作：

- `UIHostingController(rootView: MySwiftUIView())` 把 SwiftUI 嵌入 UIKit；`UIViewRepresentable`/`UIViewControllerRepresentable` 把 UIKit 嵌入 SwiftUI。
- `@objc` 暴露给 Objective-C runtime；selector `#selector(MyClass.method(_:))`；KVO 需 `@objc dynamic`。
- 桥接 ObjC：参数自动 bridge（Swift String ↔ NSString）；返回值/参数标 `@objc`。
- AppKit macOS 与 UIKit iOS API 不一样（NSColor vs UIColor、NSView vs UIView、NSEvent vs UIEvent）；共享代码用 `#if os(macOS)` / `#if os(iOS)`。

## iOS 17/18 + macOS 14/15 + visionOS + Xcode 16 增量（2024-2026）

iOS 17（2023）/ macOS 14 Sonoma：

- **Observation framework** + `@Observable` macro：替代 `ObservableObject` + `@Published`；automatic dependency tracking；no `@Published` boilerplate。
- **SwiftData** 替代 CoreData 高层 API：`@Model` macro + `@Query` SwiftUI integration；底层仍是 CoreData；新项目首选但成熟度低于 CoreData。
- **Interactive widgets / Live Activities** + WidgetKit 改进。
- **TipKit**：内置 tooltip framework 标准化新功能引导。

iOS 18（2024）/ macOS 15 Sequoia：

- **Apple Intelligence** + Foundation Models + Writing Tools API（部分功能 device-specific）。
- **Control Center customization** + lock screen widgets。
- **iPadOS 18 Calculator + Math Notes**（Apple Pencil 集成）。
- **SwiftUI**：customizable tab/sidebar（`TabView` 重写）；mesh gradient、ShaderLibrary 强化。
- **App Intents** + Siri 集成更深。

visionOS 1.x / 2.x（Apple Vision Pro 2024-）：

- **RealityKit 4** + **SwiftUI visionOS modifiers**：`.windowStyle(.volumetric)`/`.glassBackgroundEffect()`/`HoverEffect`/`Ornament`。
- **immersive space** + Shared Spaces vs Full Space；用户 eye/hand tracking 输入。
- **ARKit 6+** session 在 visionOS 上有限制（Anchor/Plane 检测）。

工具链：

- **Xcode 15+** + Swift 5.9/5.10/6.0；`#Preview` macro 替代 `PreviewProvider`；新调试器 LLDB Swift。
- **Swift Package Manager (SPM)** 是官方标准；CocoaPods 仍存在但维护减少；Carthage 已弃用。
- **Swift Macros**（5.9+）：编译期代码生成；`@Observable`/`#Preview`/`@AddCompletionHandler` 等；自定义 macro 用 SwiftSyntax。
- **SwiftLint** + **SwiftFormat**：lint + format；CI 必跑。

App Store / Privacy：

- **Privacy manifest**（iOS 17+ 强制 2024-05）：`PrivacyInfo.xcprivacy` 文件声明 API/data type 使用 reason；第三方 SDK 也要提供；不合规无法上架。
- **App Tracking Transparency (ATT)** iOS 14.5+：跨 app track 必须 `ATTrackingManager.requestTrackingAuthorization` 用户授权；IDFA 默认不可用。
- **Code signing + provisioning profile** + **Notarization**（macOS）：`fastlane` 自动化；distribution profile 走 App Store / Ad Hoc / Enterprise / Developer ID。
- **TestFlight** internal/external testing：external 需 App Review；group 控制版本。
- **App Store Connect API** + xcrun altool/notarytool 自动化上传。

## 反例库

- 反例：只改 Swift 调相机 API，不补 NSCameraUsageDescription、拒绝态和审核说明。对法：代码、Info.plist、权限拒绝 UI、Review Notes 一起改。
- 反例：Widget 读主 App 内存状态。对法：通过 App Group/Timeline 快照传递可恢复数据。
- 反例：StoreKit 购买成功后写 UserDefaults isPremium=true。对法：从 verified transaction/currentEntitlements 派生权益，处理撤权。
- 反例：Debug APNs token 发到生产 provider。对法：按 aps-environment、topic、bundle id、环境分表或强校验。
- 反例：Swift 6 并发报错改回 Swift 5 模式。对法：修 actor/MainActor/Sendable 边界。
- 反例：Swift Testing 迁移后只留 XCTest 老断言和无断言 UI test。对法：按 `@Test`、`#expect/#require`、async/throws、MainActor 隔离和 Test Plan 共存路径补覆盖。
- 反例：崩溃无 dSYM，靠地址猜。对法：上传匹配 dSYM，符号化后再归因。
- 反例：App Store 拒信只改文案不复测审核路径。对法：按拒信条款、审核账号、录屏、Review Notes 复验。
- 反例：PrivacyInfo.xcprivacy 在源码有，但 archive 没打进去。对法：检查最终 bundle、SPM resources、Pods resource_bundles、xcframework 内嵌。
- 反例：macOS 保存用户选中文件 path，下次直接访问。对法：security-scoped bookmark 并处理失效。
- 反例：BGTask 当固定定时器。对法：按系统预算设计可恢复任务和前台兜底。
- 反例：Universal Link 只配 entitlement。对法：同时核 AASA、HTTPS、cache、fallback、Scene routing。
- 反例：TestFlight 只验证能打开。对法：覆盖登录、IAP、推送、权限、崩溃、Release 配置和审核账号路径。
- 反例：CI 通过但依赖来自本机缓存或自动解析最新版本。对法：锁 Package.resolved、Podfile.lock、Ruby/CocoaPods/Bundler 版本，CI cache key 绑定 Xcode 与 lockfile hash，并保留 `.xcresult`。
- 反例：服务端收到订阅通知直接改权益。对法：验证 App Store Server Notification JWS、做幂等和重放保护，再更新权益。
- 反例：未获外部购买 entitlement 就在 App 内引导网页支付数字内容。对法：按地区、业务类型和 Apple entitlement 要求确认后再设计。
- 反例：按审核账号或地区关闭真实功能，过审后远程打开。对法：所有可远程启用能力都在 Review Notes 和元数据披露，未审核能力不上线。
- 反例：证书 pinning 只 pin leaf cert，过期后全量断网。对法：设计 pin 轮换、备份 key、遥测和应急发布路径。
- 反例：Kids Category 接入默认分析 SDK。对法：先确认儿童数据、广告、追踪和外链规则，必要时禁用 SDK 或加家长门控。
- 反例：Swift/ObjC 混编改名只跑编译。对法：补 KVO/KVC/selector、运行时反射路径和 UI 自动化验证。
- 反例：SwiftUI 页面刷新时重新创建 ViewModel 导致重复下单或重复请求。对法：把所有权放到 `@StateObject` 或上层注入，重复点击加去重和取消。根因：状态所有权不清会把 UI 刷新变成业务重放。
- 反例：异步搜索返回后直接覆盖当前列表。对法：记录 query/request id，取消旧任务，跨 await 后确认页面和输入仍匹配。根因：并发结果乱序会把旧数据写回新状态。
- 反例：权限拒绝后只弹“请开启权限”没有业务退路。对法：提供只读模式、手动上传、设置页回流或明确阻断说明。根因：真实用户常拒绝权限，审核也会检查拒绝态。
- 反例：只给主 App 配 Associated Domains，Share Extension 打不开 Universal Link。对法：按每个 signed target 核 capability、entitlements、profile 和路由入口。根因：Apple 能力按 target 生效。
- 反例：Debug 真机能登录，Archive 后 Sign in with Apple 失败。对法：核 Release bundle id、service id、nonce/state、client secret、Team ID 和服务端 audience。根因：Apple 登录是客户端配置和服务端验签的组合契约。
- 反例：Core Data 新字段本地新装正常，老用户升级闪退。对法：用旧版本 store 样本跑 lightweight/custom migration 和 Release 真机升级。根因：迁移风险只在旧数据路径暴露。
- 反例：只看 Simulator 推送 UI。对法：真机验证 APNs token、environment、topic、push type、权限关闭、冷启动和 TestFlight。根因：推送链路依赖设备、签名、环境和服务端。
- 反例：Archive 前没查最终包，第三方 SDK 隐私清单漏进包。对法：解包核 PrivacyInfo.xcprivacy、SDK manifest、Required Reason API 和 App Privacy 一致。根因：源码存在不等于最终 bundle 生效。
- 反例：watchOS 只测 iPhone companion app。对法：真表验证 Watch App/Extension、WCSession reachable/unreachable、complication/Smart Stack、低电量/离腕和后台传输。根因：watchOS 的资源、后台和连接状态不是 iOS 的子集。
- 反例：SwiftUI 用 `NavigationView`、无 value 的 `.animation`、`AnyView` 和 body 内排序过滤堆出“能跑”的页面。对法：按 NavigationStack、显式动画 value、稳定 identity、lazy 容器和预计算/缓存失效策略重审。根因：SwiftUI 的现代 API、diff 和动画语义会直接影响可维护性、性能和可访问性。

## 自检清单

- [ ] frontmatter name 等于 canonical name（apple-development），旧 slug 只作兼容 alias/URL 主键。
- [ ] 已基于远端现有 raw 合并，未用本地旧文件覆盖远端事实。
- [ ] 覆盖开发、调试、测试、签名、发布、审核、Apple API/服务端联动。
- [ ] 覆盖 iOS/iPadOS/macOS/watchOS/tvOS/visionOS 的平台差异和非目标平台声明。
- [ ] 覆盖 SwiftUI/UIKit/AppKit、Swift Concurrency、SwiftData/Core Data、Xcode/SPM/CocoaPods/fastlane/CI。
- [ ] 覆盖 Swift Testing/XCTest/XCUITest/Test Plan、`.xcresult`、Swift 6 strict concurrency 构建配置和测试迁移边界。
- [ ] 覆盖 Info.plist、entitlements、Provisioning Profile、certificate、Privacy Manifest、Required Reason API。
- [ ] 覆盖 StoreKit 2、APNs、Keychain、Sign in with Apple、Passkeys、CloudKit、Widget、Live Activity、Universal Links。
- [ ] 覆盖 watchOS/Apple Watch 的 WatchConnectivity、complication/Smart Stack、Workout/HealthKit、后台预算、低电量/离腕和真表验证。
- [ ] 覆盖 App Store Connect metadata、Beta App Review、App Privacy、ATT、Kids Category、外部购买 entitlement、账号删除、UGC、macOS notarization。
- [ ] 验证门禁区分 Simulator、real device、Debug、Release、Sandbox、TestFlight、Archive、App Review。
- [ ] 已显式检查 SwiftUI 状态所有权、MainActor、async cancellation、重复点击/重入和跨 await 旧结果覆盖。
- [ ] 已显式检查权限拒绝态、Info.plist 文案、Keychain/ATS/token 日志、旧系统 fallback 和 extension target。
- [ ] 已显式检查真机、Release、Archive、TestFlight、Privacy Manifest/App Privacy、App Review 证据缺口。
- [ ] 输出要求包含证据分档和未验证缺口。
- [ ] 安全边界拒绝绕审核、绕 IAP、伪造交易、泄露证书密钥和上线信任绕过。
- [ ] related 只使用远端 manifest 中真实 slug；requires 只填确有必需前置。

## 相邻技能边界

- Apple 全链路开发与发布/apple-development（appl） 负责 Apple 原生开发、签名、权限、隐私、StoreKit、APNs、Keychain、Xcode、TestFlight、App Review 和 Apple 客户端能力落地。
- API 工程/api-engineering（api） 负责接口契约、认证语义、错误码、幂等、服务端推送/订阅通知/API 设计；Apple 全链路开发与发布/apple-development（appl） 只提出 Apple 端契约需求和验证证据。
- 后端工程/backend-engineering（be）/Go 开发/go-development（godv） 负责后端和 Go 实现、服务端验签、APNs provider、App Store Server Notifications、配置下发；Apple 全链路开发与发布/apple-development（appl） 负责 Apple 端契约、环境、验签证据和发布审核联动。
- 数据库工程/database-engineering（db） 负责服务端表结构、迁移、事务和一致性；Apple 全链路开发与发布/apple-development（appl） 负责本地数据、SwiftData/Core Data、CloudKit/iCloud 客户端约束。
- 测试验证/test-engineering（tst） 负责测试策略、覆盖矩阵、CI 证据；Apple 全链路开发与发布/apple-development（appl） 提供 Apple 特有测试场景和门禁。
- 发布部署/release-engineering（rls） 负责 CI/CD、灰度、回滚、发布节奏和线上监控；Apple 全链路开发与发布/apple-development（appl） 提供 Archive、TestFlight、签名、审核证据。
- 性能工程/perf-engineering（pfe） 负责系统性性能优化和 SLO；Apple 全链路开发与发布/apple-development（appl） 提供 Instruments、MetricKit、URLSessionTaskMetrics、真机 Release 证据。
- Web 安全/web-security（wsec）/移动安全/mobile-security（msec） 负责安全专项审计；Apple 全链路开发与发布/apple-development（appl） 负责 Apple 平台最小权限、Keychain、ATS、证书、隐私披露落地。
- 代码审计/code-audit（aud） 负责改动后需求对账、影响面、安全质量复盘；Apple 非纯说明类改动完成前应由 代码审计/code-audit（aud） 收口。
- Android 开发/android-development（andr）/Flutter 开发/flutter-development（fltr）/Tauri 桌面应用/tauri-development（taur）/微信支付/wechat-pay（wx）/Vue 开发/vue-development（vue）/TypeScript 实战开发/typescript-development（ts） 负责各自技术栈；只有触及 Apple 原生 target、签名、App Store、iOS/macOS 平台能力时才联动 Apple 全链路开发与发布/apple-development（appl）。