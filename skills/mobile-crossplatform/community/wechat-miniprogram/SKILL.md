---
name: wechat-miniprogram
description: 微信小程序原生开发实战排障版 - 面向基础库/app.json/page.json/WXML/WXSS/Page/Component/setData/分包/登录授权/手机号/订阅消息/支付/API/web-view/插件/云开发/隐私合规/真机调试/体验版/审核/Skyline/暗黑模式的证据先行定位、实现、验证与收口。
---

# 微信小程序

微信小程序（wechat-miniprogram，兼容 slug: wcmp）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

> 定位：本技能只负责微信小程序原生端的开发与排障口径，把问题收敛为“基础库明确、页面入口明确、能力边界明确、证据可复核”。跨端框架、通用 JS/TS、接口契约、支付资金链、测试矩阵和最终审计交相邻技能。
> 铁律：未确认基础库/页面配置/能力配置/真机证据前，不下兼容结论；未读 app.json、page.json、project.config.json、sitemap、privacy、后台白名单、体验版或审核反馈前，不改全局能力口径。

## 快速总则：基础库 / 页面 / 能力 / 证据

1. 基础库：记录最低基础库、目标基础库、开发者工具版本、微信客户端版本、iOS/Android、是否启用 Skyline、glass-easel、lazyCodeLoading；新 API 必须有 wx.canIUse、降级或阻断提示。
2. 页面：先确认 app.json 页面注册、page.json 覆盖项、tabBar/分包/独立分包、workers、networkTimeout、themeLocation、darkmode、rendererOptions、extendedLib、embeddedAppIdList、chatTools、supportedMaterials、冷启动/热启动/分享/扫码/订阅/支付/web-view 回跳入口；页面未注册或入口参数不清不改逻辑。
3. 能力：登录、手机号、订阅消息、支付、位置/相册/蓝牙等隐私接口、云开发、web-view、插件、canvas、上传下载、分享转发都要核后台配置、域名/模板/插件版本/隐私声明和审核材料。
4. 证据：结论必须绑定配置文件、WXML/WXSS、Page/Component 方法、Network/console、真机录屏、miniprogram-ci 预览/上传日志、体验版路径与二维码、sourcemap/JSError 映射、后台配置截图、审核反馈、云开发日志或接口 request_id；工具模拟器通过只是弱证据。
5. 状态：Page/Component 生命周期、openid/unionid、session 续期、缓存、query、scene、分享参数、回跳状态必须有初始化、过期、失败、重试、取消和空态。
6. 性能：setData 只传 path 级最小 diff；长列表、图片、canvas、动画、滚动、Skyline 迁移先控节点量、包体、频率、内存、低端 Android 和弱网。
7. 合规：requiredPrivateInfos、隐私弹窗、手机号授权、订阅消息、支付、web-view、插件和云开发数据处理必须与用户协议、后台配置和审核说明一致。
8. 发布：体验版、审核、灰度发布、回滚、旧版本兼容、线上监控、投诉入口和旧入口验证必须在上线前形成证据；维护状态和归档风险只短写事实，不替代验证。
9. 平台口径：遇到基础库升级、开放能力变化、隐私或审核口径变化，先查微信官方文档、开发者后台、基础库 release note 和审核反馈；旧项目经验只能作为假设，不写成结论。
10. 工程门禁：任何新增/修改页面都要同时列生命周期、状态真相源、接口字段兼容、权限拒绝态、弱网失败态、缓存失效、真机/体验版证据和回滚口径；缺一项就不能报“完整可上线”。
11. 安全门禁：secret、session_key、商户密钥、支付签名、云函数管理密钥、openid/unionid 归属、订单金额和权限角色都不能以前端为真相源；前端只能调用官方能力、展示状态和上传临时凭证。
12. 低级错门禁：禁止只测开发者工具、禁止关闭域名校验冒充线上通过、禁止 setData 大对象/整列表/每帧动画、禁止信客户端 openid/金额、禁止忽略拒绝授权和审核权限文案。

## 场景执行卡

### 1. 新页面 / 老页面改造
- 输入：页面目标、入口、最低基础库、路由、是否 tabBar/分包/独立分包、是否依赖登录/授权/接口。
- 动作：先定 app.json/page.json、页面路径、navigationStyle、renderer、usingComponents、分享落地、空/错/加载态，再写 WXML/WXSS/逻辑。
- 验证：开发者工具、iOS/Android 真机、体验版覆盖冷启动、热启动、返回、分享、扫码、弱网和低基础库降级。
- 兜底：入口参数缺失时渲染可解释错误页，不让 onLoad early return 跳过分享、埋点或兜底按钮。

### 1A. 导航、页面栈与入口参数
- 输入：入口类型（普通页/tabBar/分包/独立分包）、navigateTo 层级、返回路径、scene/query、分享/扫码/订阅/支付/web-view 回跳参数。
- 动作：按目的选择 navigateTo/redirectTo/switchTab/reLaunch/navigateBack；tabBar 页不假设 query 长期保留；复杂参数编码、长度和幂等校验；页面栈满时有降级路径。
- 验证：冷启动、热启动、扫码直达、分享回流、tab 切换、支付/授权/web-view 回跳、返回栈恢复和页面栈上限。
- 兜底：入口参数缺失、过期或非法时渲染可恢复错误页，不静默白屏或误下单。

### 2. app.json / page.json / project.config.json / 基础库
- 输入：appid、compileType、miniprogramRoot、libVersion、lazyCodeLoading、renderer、subpackages、requiredPrivateInfos、permission、plugins、sitemap、workers、networkTimeout、themeLocation、darkmode、rendererOptions、extendedLib、embeddedAppIdList、chatTools、supportedMaterials。
- 动作：改配置前全量查页面注册、分包依赖、workers 路径、网络超时、主题与暗黑模式位置、渲染选项、扩展库、半屏/嵌入能力清单、插件、隐私接口、上传下载域名、web-view 业务域名、云开发环境和开发者工具本地开关。
- 验证：重新编译、预览、真机调试、体验版；确认详情面板基础库、线上目标版本和后台配置一致。
- 兜底：配置差异不可确认时标“需验证”，不把本地工具默认值当线上事实。

### 2A. 构建、CI 与环境配置入口
- 输入：project.config/private.config、miniprogram-ci、npm 构建、TS 类型、环境变量、appid、projectPath、privateKey/密钥注入方式、云环境、version、desc、上传版本、sourcemap、体验版二维码。
- 动作：本地私有配置不入库；miniprogram-ci 显式传 appid、projectPath、version、desc、privateKey 或安全密钥路径；环境差异用显式配置管理；CI 上传前检查包体、合法域名、隐私声明、插件版本、基础库、sourcemap 和 npm 构建产物。
- 验证：清缓存构建、CI 预览二维码、体验版二维码、上传结果、sourcemap/JSError 映射、不同 appid/环境隔离。
- 兜底：开发者工具本地开关、private.config、缺 privateKey/appid/projectPath/version/desc 或未构建 npm 不能作为线上事实；工程链深水区交 jsts/rls。

### 3. WXML / WXSS / Skyline / 暗黑模式 / 玻璃效果
- 输入：渲染器、页面结构、组件层级、rpx/px、safe-area、暗黑模式、glass-easel/玻璃效果、滚动容器、低端机范围。
- 动作：WXML 控节点量和条件渲染；WXSS 避免全局污染和复杂选择器；Skyline/glass-easel 按页面渐进启用；暗黑模式用主题变量，不简单反色。
- 验证：iOS/Android 真机、低端 Android、长文本、键盘、安全区、横竖屏、暗色/亮色、滚动穿透和玻璃效果降级。
- 兜底：工具里视觉正常不等于真机、Skyline 或暗黑模式可用，缺截图/录屏标未验证。

### 3A. 滚动、手势、键盘与安全区
- 输入：scroll-view/page 滚动、自定义导航栏、fixed/sticky、下拉刷新、上拉分页、输入框、键盘、胶囊和 safe-area。
- 动作：先定唯一滚动容器；避免 page 与 scroll-view 双滚动；键盘弹起时保存焦点和滚动位置；自定义导航栏按胶囊与安全区计算但不写死机型。
- 验证：iOS/Android、低端 Android、长列表、输入法、横竖屏、暗黑模式、下拉刷新、回弹、手势冲突和滚动穿透。
- 兜底：缺真机证据时，不声明滚动、键盘或安全区已适配。

### 4. Page / Component 生命周期与状态流
- 输入：onLoad、onShow、onReady、onHide、onUnload、observers、lifetimes、pageLifetimes、attached/detached、behaviors。
- 动作：区分一次性初始化、每次展示刷新、组件入树、属性变更和页面返回刷新；请求去重、取消、过期响应丢弃要明确。
- 验证：navigateTo、redirectTo、switchTab、reLaunch、navigateBack、分享回流、分包直达、后台恢复、支付/授权回跳逐项跑。
- 兜底：onShow 重复请求、observer 循环 setData、detached 未清计时器/监听都列风险。

### 4A. 组件契约、样式隔离与事件
- 输入：properties、data、observers、lifetimes、behaviors、relations、slot、externalClasses、事件和选择器。
- 动作：组件对外属性写清类型/默认值/边界；事件只抛业务必要字段；样式隔离策略明确；relations/selectComponent 只用于必要父子协作，避免隐式全局状态。
- 验证：多实例、嵌套、销毁重建、属性快速变化、slot 空态、样式覆盖、事件冒泡/捕获和低端机性能。
- 兜底：组件不能依赖单例页面状态；observer 不做网络请求或高频 setData。

### 5. setData、长列表、图片、canvas 与性能
- 输入：数据体积、更新频率、节点数、图片尺寸、滚动容器、canvas 数量、动画方式、低端设备。
- 动作：setData 只传最小 path；列表分页/虚拟/懒加载；图片裁剪压缩并占位；高频动画/拖拽/滚动不用 setData 硬推。
- 验证：Performance、真机帧率、内存、首屏、弱网图片加载、低端 Android、canvas 导出像素比和相册权限。
- 兜底：无设备和性能证据时只写“性能未验证”。

### 6. 分包 / 独立分包 / 预下载 / 包体
- 输入：主包体积、subpackages 路由、独立分包、preloadRule、公共组件、插件、静态资源归属。
- 动作：主包只放首屏必需；分包页自带最小初始化和登录续期；公共组件避免循环依赖和重复打包。
- 验证：清缓存冷启动、扫码直达分包页、弱网下载失败、预下载命中、体验版包体检查。
- 兜底：分包加载失败必须有重试/返回首页，不能白屏。

### 7. 登录授权、手机号、openid / unionid
- 输入：wx.login code、服务端换取 openid/unionid、session_key、手机号授权、用户资料、缓存过期、账号合并。
- 动作：前端只拿临时凭证和授权结果；身份真相在后端；手机号新旧授权 API 按基础库和按钮形态核验；拒绝授权可恢复。
- 验证：首次进入、拒绝授权、重新授权、换微信号、unionid 缺失、401 续登、code 过期、旧缓存过期。
- 兜底：不能把 openid、unionid、session_key 或手机号明文当作前端可信安全凭证。

### 8. wx.request / 上传下载 / API 边界
- 输入：request/upload/download 合法域名、证书、超时、鉴权 header、错误码、重试、文件大小、临时路径。
- 动作：统一封装 loading、401、403、5xx、超时、取消、弱网、进度和 request_id；字段/状态码/幂等交 api。
- 验证：打开域名校验、真机弱网、Network、HTTPS 证书、后台日志、文件打开和临时路径生命周期。
- 兜底：开发者工具“不校验合法域名”通过不能作为线上证据。

### 8A. 缓存、离线与数据清理
- 输入：storage key、版本、过期时间、登录态、业务缓存、隐私数据、弱网/离线策略。
- 动作：缓存 key 带版本和用户维度；登录退出或换号清理敏感缓存；弱网可重试但不重复提交；乐观更新必须能回滚。
- 验证：首次进入、换号、退出登录、缓存升级、弱网、离线恢复、重复点击、接口失败和隐私数据清理。
- 兜底：前端缓存只做体验优化，不作为权限、订单、支付或身份最终态。

### 9. 订阅消息、支付与后端回调
- 输入：模板 ID、订阅场景、wx.requestSubscribeMessage、wx.requestPayment、订单号、支付签名、回调幂等。
- 动作：订阅消息只在真实用户动作后触发；支付参数来自后端；前端只展示处理中，最终态以后端回调/查单为准；资金链交 wx。
- 验证：允许/拒绝订阅、模板失效、环境不一致、重复支付、取消支付、成功未回调、回调延迟、体验版与正式商户配置。
- 兜底：wx.requestPayment success 不等于订单成功。

### 10. 云开发、web-view、插件、媒体与开放组件
- 输入：云环境 ID/envId、TCB_ENV、云函数/数据库集合权限、文件 ID、业务域名、H5 路由、postMessage、插件 appid/版本、camera/video/canvas 权限。
- 动作：云开发规则按最小权限；envId/TCB_ENV 按开发版、体验版、正式版显式隔离；集合权限、文件 ID 生成/访问、云函数入口和触发器按环境核验；web-view 核业务域名和登录桥接；插件核版本、隐私与审核；postMessage 必须校验来源、schema、版本、nonce/一次性业务标识和允许动作列表。
- 验证：iOS/Android 真机、云函数日志、云数据库集合权限拒绝、文件 ID 读写、环境隔离、web-view 返回栈、H5 登录态、插件不可用降级、媒体权限拒绝。
- 兜底：H5 能开、云函数本地能跑或插件开发版可用，不代表体验版/正式版可用；scene/query/二维码参数按不可信输入处理，日志不得输出 code、session_key、手机号、token、支付参数和隐私字段。

### 11. 隐私授权、审核、体验版与灰度发布
- 输入：requiredPrivateInfos、隐私弹窗、用户协议、资质、测试账号、敏感能力、审核说明、灰度范围。
- 动作：调用隐私接口前补声明和用户授权；审核材料写清入口和测试步骤；体验版跑主链路；灰度发布保留回滚版本和旧接口兼容。
- 验证：首次/拒绝/再授权、审核反馈复现、体验版扫码、灰度比例、线上监控、投诉入口和回滚演练。
- 兜底：审核通过不等于所有端通过，灰度期间必须保留旧版兼容。

### 11A. 自动化验证、可观测与灰度阈值
- 输入：核心路径、页面列表、设备矩阵、基础库、体验版二维码、审核路径、性能基线、启动耗时、白屏、JS error、接口错误率、支付/订阅/登录转化、投诉和灰度比例。
- 动作：能自动化的用 miniprogram-ci/miniprogram-automator 跑编译、预览、上传、核心冒烟、截图和包体检查；miniprogram-ci 参数必须有 appid、projectPath、privateKey 或密钥路径、version、desc、sourcemap 策略和体验版二维码留存；关键链路埋点带页面、入口、基础库、客户端版本、设备和 request_id；灰度前定义回滚阈值和观察窗口。
- 验证：CI 日志、预览二维码、体验版二维码、截图、Network、性能数据、真机录屏、sourcemap/JSError、云函数日志/request_id，且开发版/体验版/正式版日志能贯通。
- 兜底：自动化通过不替代支付、授权、隐私、审核和低端真机验证；无指标阈值和回滚版本，不建议全量发布。

### 11B. 单元测试、npm 构建与组件依赖
- 输入：Jest、miniprogram-simulate、组件路径、usingComponents、npm 包、npm dist/lib/miniprogram_npm、基础库下限、CI 构建缓存。
- 动作：组件逻辑可用 Jest + miniprogram-simulate 覆盖 properties、事件、slot、生命周期和渲染快照；引入 npm 后确认构建产物落在 dist/lib/miniprogram_npm 或项目实际 miniprogram_npm；usingComponents 指向构建后路径；依赖新 API 时写清基础库下限与降级。
- 验证：清缓存 npm 构建、组件测试、开发者工具编译、真机/体验版加载组件、低基础库降级路径。
- 兜底：Jest/simulate 只能证明组件契约，不代表原生能力、样式、授权、网络、云开发或审核通过。

### 12. 单技能开发闭环门禁
- 输入：需求原话、目标页面/组件、入口路径、依赖 API、登录/手机号/支付/订阅/隐私能力、最低基础库、真机/体验版条件。
- 动作：先把“入口 -> 生命周期 -> 状态 -> 请求 -> 渲染 -> 能力调用 -> 失败态 -> 缓存 -> 分享/回跳 -> 验收证据”串成闭环，再写页面；任何字段、权限、金额、身份、订单状态都回到服务端真相源。
- 验证：至少给出开发者工具编译、真机主链路、体验版路径、弱网/失败态、低基础库或 canIUse 降级、后台日志/request_id；涉及支付/订阅/手机号/隐私时补审核材料和拒绝态。
- 兜底：资料不足时输出缺口和切换条件，不用“微信能力应该可以”“工具里能跑”替代证据。

### 13. API 字段兼容、缓存升级与旧版本用户
- 输入：接口字段新增/删除/改名、缓存 key、storage 结构、灰度版本、线上旧版本小程序、服务端兼容窗口。
- 动作：接口消费侧给默认值、字段存在性判断、旧字段 fallback、空数组/空对象/空字符串语义；缓存带 schemaVersion、用户维度、过期时间和迁移/清理策略。
- 验证：旧缓存启动、新接口缺字段、老接口多字段、弱网重试、换号、退出登录、灰度回滚后再进入。
- 兜底：小程序用户不会立刻升级；服务端字段切换和前端缓存升级必须保留兼容窗口。

## 高频坑 / 防遗漏

### 高频坑
1. 只用开发者工具调通，没跑真机调试和体验版。
2. 未锁最低基础库，线上低版本缺 API 或 Skyline 行为不同。
3. app.json、page.json、project.config.json、sitemap、privacy、requiredPrivateInfos 漏同步。
4. WXML 节点过多、WXSS 全局污染、暗黑模式简单反色或玻璃效果无降级。
5. onShow 重复请求，支付/授权/返回后覆盖用户状态。
6. Component observer 内 setData 触发循环更新。
7. setData 传大对象或高频传数组，导致卡顿和内存飙升。
8. 分包页依赖主包初始化状态，扫码直达白屏。
9. wx.login code 复用，openid/unionid 获取失败无兜底。
10. 手机号授权只测旧接口或只测允许态，拒绝/基础库不兼容未测。
11. 订阅消息无真实触发动作，模板 ID 与环境不一致。
12. 支付以前端 success 改订单状态。
13. 工具关闭域名校验后误判 wx.request 线上可用。
14. web-view 域名、H5 登录态、postMessage 来源未核。
15. 云开发数据库权限过宽或云函数只在本地通过。
16. 插件版本、主体、隐私与审核材料未核。
17. canvas 导出未处理像素比、跨域图片和相册权限。
18. 隐私接口未声明就调用，审核或真机失败。
19. 上传下载临时路径、大小限制、超时和弱网未测。
20. 灰度发布无监控、回滚和旧版本兼容策略。
21. 导航 API 选型错误、页面栈满、tabBar query 丢失或回跳参数未编码导致白屏/错单。
22. page 与 scroll-view 双滚动、sticky/fixed/键盘/胶囊安全区只在单端验证。
23. 组件 properties、slot、externalClasses、relations 和事件契约不清，复用后状态串扰。
24. 本地 private.config、miniprogram-ci 缺 privateKey/appid/projectPath/version/desc、未构建 npm、关闭校验或 sourcemap 缺失被当成线上事实。
25. storage 缓存无用户维度、无版本、退出不清理，弱网重试造成重复提交。
26. 小程序 scene/query、二维码和 web-view 消息未做 schema/nonce/允许动作校验。
27. 没有自动化冒烟、包体/截图/性能基线、JS error/request_id 贯通和灰度回滚阈值。
28. app.json 新字段 workers、networkTimeout、themeLocation、darkmode、rendererOptions、extendedLib、embeddedAppIdList、chatTools、supportedMaterials 漏核，导致体验版与本地表现不一致。
29. 云开发 envId/TCB_ENV、集合权限、文件 ID 和云函数日志未按环境隔离，开发版数据或权限误带到正式版。
30. usingComponents 指向源码路径但 npm 构建产物在 dist/lib/miniprogram_npm，组件测试通过而体验版加载失败。
31. App/Page/Component 生命周期混用，把登录、支付、分享、路由和组件渲染副作用揉在一起，复用后重复弹窗或重复下单。
32. 客户端提交 openid、金额、会员价、角色、优惠金额或订单状态，服务端没重新校验就落库。
33. secret、session_key、商户密钥、云函数管理能力、支付签名逻辑、接口 token 或手机号明文出现在前端包、日志、storage 或错误上报里。
34. 授权拒绝态缺失：定位、相册、摄像头、手机号、订阅消息拒绝后页面卡死、反复弹窗或无法返回主流程。
35. 隐私协议、requiredPrivateInfos、权限用途说明和审核截图没跟代码同步，真机或审核才失败。
36. API 字段和 storage 结构只兼容最新版，旧版本用户或旧缓存启动后白屏。
37. 分包策略缺失：新页面、大图、npm 依赖和插件全塞主包，首启变慢或包体超限。
38. 体验版只跑 happy path，没有覆盖弱网、401、5xx、支付取消、订阅拒绝、手机号失败和回跳参数缺失。

### 防遗漏清单
- 基础库：最低版本、目标版本、微信客户端、开发者工具、API 可用性和降级策略写清了吗？
- 页面：app.json/page.json、tabBar、分包、独立分包、分享/扫码/回跳入口都列了吗？
- 能力：登录、手机号、订阅消息、支付、隐私接口、云开发、web-view、插件、上传下载、canvas 的后台配置和审核材料都查了吗？
- 结构样式：WXML/WXSS、Skyline、glass-easel、暗黑模式、safe-area、键盘、低端机都覆盖了吗？
- 网络：wx.request、上传、下载、超时、401、弱网、域名校验和后台 request_id 有证据吗？
- 发布：体验版、审核、灰度发布、回滚、监控和投诉入口是否闭环？
- 导航：页面栈、tabBar、回跳、scene/query 编码、参数过期和非法参数兜底是否覆盖？
- 滚动交互：唯一滚动容器、下拉/上拉、sticky/fixed、键盘、胶囊、安全区和手势冲突是否真机验证？
- 组件：properties、slot、externalClasses、relations、事件字段、样式隔离和多实例是否有契约？
- 工程与观测：miniprogram-ci/automator、appid、projectPath、privateKey、version、desc、体验版二维码、npm 构建、sourcemap、JS error、request_id、灰度阈值是否闭环？
- 数据安全：storage 版本/用户维度/清理、离线重试、乐观回滚、scene/query/web-view 消息校验是否到位？
- 云开发：envId/TCB_ENV、集合权限、文件 ID、云函数日志、开发版/体验版/正式版环境隔离是否有证据？
- 测试依赖：Jest + miniprogram-simulate、usingComponents、dist/lib/miniprogram_npm 和基础库下限是否一致？
- 工程闭环：入口、生命周期、状态真相源、请求、渲染、开放能力、失败态、缓存、分享/回跳和验收证据是否串起来？
- 安全真相源：openid/unionid、手机号、session_key、支付金额、订单状态、会员身份、权限角色是否都由后端确认？
- 权限拒绝态：定位、相册、摄像头、蓝牙、文件、手机号、订阅消息和隐私授权拒绝后是否能继续主流程或明确降级？
- 兼容升级：API 字段、storage schemaVersion、旧缓存、旧小程序版本、灰度回滚和低基础库 fallback 是否有样本？

## 输出要求

1. 场景卡：列命中的卡片和原因。
2. 基础库 / 页面 / 能力 / 证据：列基础库、微信客户端、开发者工具、设备、页面入口、已读配置和证据来源。
3. 改动口径：涉及 app.json、page.json、project.config.json、WXML、WXSS、Page、Component、setData、分包、wx.request、开放能力的具体范围。
4. 风险清单：兼容、性能、权限、隐私、审核、支付、网络、云开发、插件、发布风险逐条给结论。
5. 验证方案：开发者工具、真机调试、体验版、体验版二维码、正式灰度、miniprogram-ci/automator、Jest + miniprogram-simulate、日志/截图/录屏/Network/云函数日志/sourcemap/request_id 证据；未跑标“无法验证”。
6. 联动技能：JS/TS 实现交 jsts；UI/暗黑/玻璃效果交 u；跨端交 unap；支付资金链交 wx；接口契约交 api；测试交 tst；最终收口交 aud。
7. 剩余缺口：缺设备、缺账号、缺后台配置、缺审核材料、缺云环境、缺线上灰度时必须明确。

## 约束

- 不读取本地旧技能或本地 SQLite 作为权威；技能内容以远端 Skill Hub raw 为准。
- 不把开发者工具通过包装成真机、体验版、审核或正式版通过。
- 不写死基础库、状态栏、胶囊、安全区、canvas 像素比、网络环境、页面栈余量或插件版本。
- 不用高频 setData 驱动动画、拖拽或滚动。
- 不在前端保存或信任 session_key、openid、unionid、手机号明文作为安全授权依据。
- 不绕过微信登录、订阅消息、支付、隐私接口、审核、域名白名单和插件审核的官方口径。
- 不把跨端框架、API 契约、支付资金链、测试矩阵、发布工程深水区或代码审计写成本技能职责。
- 涉状态、接口、权限、支付、隐私、发布或关键链路时，必须按风险补 tst，并由 aud 收口。

## 高频 Bug 反例库

- 反例 1：基础库只看开发者工具。
  - 错：开发者工具新基础库可用，线上低基础库白屏。
  - 对：锁定最低基础库和目标基础库，对不可用 API 做 wx.canIUse、降级或阻断。
  - 根因：工具默认基础库常高于用户真实环境。
- 反例 2：开发者工具关闭域名校验。
  - 错：本地 wx.request 成功就说网络通过。
  - 对：打开域名校验，用真机和体验版验证 HTTPS、证书、request/upload/download 白名单。
  - 根因：工具开关会掩盖线上限制。
- 反例 3：page.json 覆盖项漏查。
  - 错：只改 app.json 的 navigationStyle，却被页面 page.json 覆盖导致体验版表现不同。
  - 对：同时读 app.json、page.json 和页面路径，确认局部配置优先级。
  - 根因：页面级配置会覆盖全局假设。
- 反例 4：WXML 节点和 WXSS 全局污染。
  - 错：长列表一次渲染全部节点，WXSS 写全局选择器影响其他页。
  - 对：分页/虚拟/懒加载，样式限定组件或页面作用域并回归相邻页面。
  - 根因：小程序视图层通信和样式隔离成本不同于普通 Web。
- 反例 5：Skyline / glass-easel 无降级。
  - 错：页面启用 Skyline 后 fixed、滚动、玻璃效果在部分基础库或 Android 异常。
  - 对：按页面灰度启用，记录基础库和端差异，为 glass-easel/玻璃效果准备降级样式。
  - 根因：新渲染链路和 WebView 行为不完全兼容。
- 反例 6：暗黑模式简单反色。
  - 错：只把背景改黑，边框、图标、玻璃效果和 canvas 导出不可读。
  - 对：用主题变量覆盖文本、背景、边框、图表和导出素材，亮暗都真机验证。
  - 根因：暗黑模式是语义主题，不是颜色反转。
- 反例 7：Page onShow 重复覆盖。
  - 错：每次 onShow 拉取详情并覆盖表单，支付回跳或返回后用户输入丢失。
  - 对：区分初始化、刷新和回跳状态，用脏标记/版本号/请求取消控制。
  - 根因：生命周期触发频率被低估。
- 反例 8：Component observer 循环 setData。
  - 错：observer 监听 props 后 setData 回写同源字段，组件卡死。
  - 对：只派生内部字段，比较前后值，避免观察链闭环。
  - 根因：组件属性、data 和 observer 不是单向自动防抖。
- 反例 9：setData 大对象刷新列表。
  - 错：滚动或输入时 setData 整个列表数组。
  - 对：按 path 更新最小字段，分页/虚拟化/节流，图片懒加载。
  - 根因：逻辑层到视图层通信成本高。
- 反例 10：分包路径能编译但不能直达。
  - 错：subpackages 内页面依赖主包初始化后的全局状态，扫码直达白屏。
  - 对：分包页自带最小初始化和登录续期，公共资源放正确包位。
  - 根因：分包加载顺序与普通导航不同。
- 反例 11：wx.login code 复用。
  - 错：失败重试复用旧 code，后端换 openid 失败。
  - 对：每次换取失败重新 wx.login，并处理 unionid 为空和 session 过期。
  - 根因：code 一次性且有效期短。
- 反例 12：手机号授权只测允许态。
  - 错：按钮拿到手机号就上线，拒绝、基础库不支持、后端解密失败无兜底。
  - 对：覆盖允许/拒绝/取消/低基础库/后端失败，前端不落手机号明文。
  - 根因：手机号能力受基础库、授权形态和后端换取共同约束。
- 反例 13：订阅消息静默调用。
  - 错：页面加载就调 wx.requestSubscribeMessage，用户无感且失败。
  - 对：绑定真实点击/提交动作，模板 ID 按环境配置，拒绝后有替代提醒。
  - 根因：订阅消息受触发场景和用户授权限制。
- 反例 14：支付 success 当成订单成功。
  - 错：wx.requestPayment success 后前端直接展示已支付并发货。
  - 对：以后端支付回调和订单查询为准，处理取消、延迟、重复回调和幂等。
  - 根因：前端回调不是资金最终态。
- 反例 15：web-view H5 直接复用网页登录。
  - 错：H5 浏览器登录态在小程序 web-view 中不可用，返回栈和分享失效。
  - 对：核业务域名、登录桥接、postMessage 来源、返回路径和分享参数。
  - 根因：web-view 是受限容器，不等同普通浏览器。
- 反例 16：云开发权限按本地管理员假设。
  - 错：本地云函数能读写，正式环境数据库规则拒绝或越权。
  - 对：按环境 ID、云函数日志、数据库规则和用户身份分别验证。
  - 根因：云开发本地调试和线上权限边界不同。
- 反例 17：插件开发版可用就上线。
  - 错：插件版本、主体授权、隐私声明或审核材料未核，体验版/正式版不可用。
  - 对：锁插件 appid/版本，核授权、隐私、审核说明和降级路径。
  - 根因：插件是独立能力和审核边界。
- 反例 18：canvas 导出模糊或失败。
  - 错：按 CSS 尺寸绘制，不处理 devicePixelRatio、跨域图片和相册授权。
  - 对：按像素比放大画布，图片先合法下载，保存前处理权限拒绝。
  - 根因：canvas 绘制、图片安全和系统权限叠加。
- 反例 19：隐私接口未提前声明。
  - 错：调用定位、相册、麦克风等隐私接口时才发现弹窗/审核失败。
  - 对：在 app.json requiredPrivateInfos、隐私协议和调用前提示中保持一致。
  - 根因：隐私合规是配置、文案、调用时机三件事。
- 反例 20：审核只给账号不给路径。
  - 错：审核员找不到支付/订阅/资质入口，驳回“功能不可用”。
  - 对：审核说明提供测试账号、入口路径、操作步骤、资质和异常说明。
  - 根因：审核按可见入口验证，不替开发者探索。
- 反例 21：真机调试没测低端 Android。
  - 错：iPhone 真机流畅，低端 Android 长列表、Skyline 或 canvas 卡顿崩溃。
  - 对：至少补一台低端 Android 或设备云证据，记录内存、帧率和包体。
  - 根因：端性能差异大，工具和高端机不能代表用户。
- 反例 22：灰度发布无回滚。
  - 错：全量发布后才发现旧缓存和新接口不兼容。
  - 对：灰度发布前确认兼容窗口、监控指标、回滚版本和旧入口验证。
  - 根因：小程序版本切换和用户缓存不是瞬时一致。

- 反例 23：导航 API 选型靠感觉。
  - 错：支付回跳用 navigateTo 堆栈，tabBar 页依赖 query，页面栈满后白屏。
  - 对：按入口和目标选 redirectTo/switchTab/reLaunch/navigateBack，复杂参数编码并校验过期与幂等。
  - 根因：小程序页面栈和 tabBar 生命周期不是普通 URL 路由。
- 反例 24：滚动和键盘只测一个机型。
  - 错：iPhone 正常就认为 fixed、sticky、输入框和安全区都适配。
  - 对：统一滚动容器，覆盖 iOS/Android、低端机、输入法、胶囊、安全区、下拉刷新和手势冲突。
  - 根因：小程序滚动、原生组件和键盘在端侧差异大。
- 反例 25：组件契约靠调用方自觉。
  - 错：properties 类型、slot、externalClasses、事件字段不定，复用后样式串扰或状态串线。
  - 对：写清属性默认值和边界，限定事件载荷，验证多实例、嵌套、销毁重建和样式隔离。
  - 根因：组件是复用边界，不是页面内部变量。
- 反例 26：缓存提升体验却污染身份。
  - 错：storage 不分用户和版本，换号后读取旧手机号、订单或权限。
  - 对：key 带用户维度和版本，退出/换号清敏感缓存，离线重试防重复提交，乐观更新可回滚。
  - 根因：前端缓存不是身份、权限、订单或支付最终态。
- 反例 27：灰度没有可观测阈值。
  - 错：体验版主流程能跑就全量，线上白屏和接口失败无法定位。
  - 对：启动耗时、首屏、JS error、接口错误率、转化漏斗、投诉和 request_id 贯通，灰度前设观察窗口和回滚阈值。
  - 根因：小程序版本、缓存、入口和基础库碎片化会放大线上差异。
- 反例 28：前端信任 openid 和金额。
  - 错：页面提交 openid、金额、优惠和订单状态，服务端直接创建订单。
  - 对：前端只传临时凭证和用户选择，后端按登录态、商品、优惠、库存和风控重新计算。
  - 根因：客户端字段可伪造，资金和身份必须以后端为真相源。
- 反例 29：密钥和 session_key 进前端。
  - 错：把 session_key、商户密钥、支付签名逻辑、云函数管理 key 或接口 token 写进小程序包。
  - 对：所有密钥只在服务端或安全注入环境，前端只拿短期业务 token 和临时凭证。
  - 根因：小程序包、日志和 storage 都不是密钥保存边界。
- 反例 30：授权拒绝没有产品路径。
  - 错：用户拒绝定位/相册/手机号/订阅后页面空白或持续弹授权。
  - 对：给拒绝态、手动设置入口、无权限降级和可继续主流程的替代方案。
  - 根因：授权是用户选择，不是必然成功的前置条件。
- 反例 31：setData 大对象当状态同步。
  - 错：接口返回整棵对象、长列表和图片数据每次都全量 setData。
  - 对：只传视图需要的最小字段，按 path 更新，列表分页，图片用 URL/缩略图和懒加载。
  - 根因：逻辑层到视图层通信和渲染节点是小程序性能瓶颈。
- 反例 32：隐私文案和代码分叉。
  - 错：新增相册/定位/手机号能力但不更新 requiredPrivateInfos、隐私协议、用途说明和审核截图。
  - 对：代码、配置、用户可见文案、后台声明和审核材料同批更新。
  - 根因：微信审核看能力调用、配置声明和用户理解是否一致。
- 反例 33：API 字段只测最新版。
  - 错：服务端改字段名，最新版页面正常，旧版本和旧缓存用户白屏。
  - 对：保留兼容字段、默认值和 schemaVersion 迁移，灰度期验证旧版本启动。
  - 根因：小程序版本和缓存升级不是强一致。
- 反例 34：只测开发者工具 happy path。
  - 错：模拟器能登录、下单、分享就报完成。
  - 对：真机、体验版、低基础库、弱网、授权拒绝、支付取消、接口 4xx/5xx 都要走样本。
  - 根因：开发者工具会掩盖域名、权限、基础库、端差异和性能问题。

## 提交前自检清单

- [ ] frontmatter 包含 name、description，H1 等于 manifest title（微信小程序）。
- [ ] 行数 <= 500，fenced code block 数 = 0。
- [ ] 章节齐全：快速总则、场景执行卡、高频坑 / 防遗漏、输出要求、约束、高频 Bug 反例库、提交前自检清单、2024-2026 新坑速查、与相邻技能的边界。
- [ ] 高频 Bug 反例库不少于 10 条，且每条能被“反例 数字”命中，含错法、对法、根因。
- [ ] 覆盖基础库、app.json/page.json、workers/networkTimeout/themeLocation/darkmode/rendererOptions/extendedLib/embeddedAppIdList/chatTools/supportedMaterials、导航/页面栈、滚动/键盘/安全区、组件契约、WXML/WXSS、setData、分包/预下载、npm 构建、usingComponents、dist/lib/miniprogram_npm、缓存/离线、隐私授权、安全输入、手机号/登录、订阅消息、云开发 envId/TCB_ENV/集合权限/文件ID/云函数日志/环境隔离、web-view、插件、审核、miniprogram-ci、Jest + miniprogram-simulate、自动化/观测、真机/开发者工具差异、Skyline/玻璃效果/暗黑模式。
- [ ] 已声明基础库、页面、能力、证据，不用“应该可以”替代验证。
- [ ] 已区分开发者工具、真机调试、体验版、正式版、审核和灰度发布证据。
- [ ] 已明确与 jsts、u、unap、wx、api、tst、aud 的边界。
- [ ] 已覆盖单技能工程闭环：生命周期、状态真相源、setData 粒度、API 字段兼容、权限拒绝态、弱网失败态、缓存升级、真机/体验版证据。
- [ ] 已禁止低级错：只测开发者工具、信客户端 openid/金额、前端放 secret、忽略隐私/权限审核文案、主包塞爆、旧版本无兼容。

## 2024-2026 新坑速查

- Skyline / glass-easel / 玻璃效果：老 WebView 布局、fixed、滚动、层级、组件行为和玻璃拟态不能无脑迁移；按页面渐进启用并保留降级。
- 暗黑模式：页面、组件、canvas 导出、web-view 容器、图标和玻璃效果都要亮暗双测，不能简单反色。
- 隐私接口治理：requiredPrivateInfos、隐私弹窗、用户协议、后台配置和调用时机必须一致。
- 手机号授权变化：按钮形态、基础库、后端换取、拒绝授权和手机号明文处理要按现网能力验证。
- 基础库碎片化：新 API、订阅消息、渲染器、插件、云开发和隐私能力要按最低基础库核验。
- 开发者工具差异：模拟器、域名校验开关、ES 转换、上传压缩、Skyline 模拟和真机表现可能不同。
- 分包与包体：主包压线、独立分包、预下载、公共依赖重复、插件资源会影响冷启动与审核。
- 云开发：环境 ID、数据库权限、云函数日志、定时触发、云托管域名和体验版权限经常与本地不同。
- web-view 限制：业务域名、文件下载、H5 登录态、postMessage、分享和返回栈要逐项验证。
- canvas 2D / 离屏绘制：像素比、内存、跨域图片、导出格式和低端 Android 易出兼容问题。
- 订阅消息模板：模板类目、环境、触发动作、长期订阅和一次性订阅口径可能变化。
- 支付合规：商户号、主体一致性、回调幂等、退款/分账和审核说明要前后端联动。
- 支付联动边界：小程序只负责调起和展示，订单创建、金额计算、签名、回调、查单、退款和对账都必须以后端/支付技能为准。
- 插件合规：插件 appid/版本、主体授权、用户隐私、审核说明和不可用降级都要证据化。
- 审核与灰度发布：审核通过不代表全量安全；灰度监控、投诉入口、回滚版本和旧缓存兼容要提前准备。
- 导航与入口：页面栈上限、tabBar query、scene 编码、二维码参数、分享/支付/web-view 回跳必须按不可信输入和幂等处理。
- 自动化与观测：miniprogram-ci、miniprogram-automator、Jest + miniprogram-simulate、sourcemap、JS error、白屏、首屏、request_id 和灰度阈值成为发布证据的一部分。
- CI 上传：privateKey、appid、projectPath、version、desc、sourcemap 和体验版二维码要可追溯，密钥只走安全注入。
- app.json 能力：workers、networkTimeout、themeLocation、darkmode、rendererOptions、extendedLib、embeddedAppIdList、chatTools、supportedMaterials 要按基础库和后台开关核验。
- npm 与组件：dist/lib/miniprogram_npm、usingComponents、基础库下限和构建缓存不一致会造成体验版缺组件。
- 维护状态：官方能力变更、插件停更、仓库归档或示例失维护只短写状态和风险，不扩展成无证据结论。

## 与相邻技能的边界

- 本技能负责：微信小程序原生开发、基础库、app.json/page.json/project.config.json、WXML/WXSS、Page/Component、setData、分包、微信开放能力、云开发、web-view、插件、真机调试、体验版、审核和灰度发布口径。
- JavaScript/TypeScript 开发/javascript-typescript-development（jsts）：负责 JavaScript/TypeScript 语言、类型、异步竞态、构建脚本和通用前端安全；本技能只约束小程序运行时证据。
- UI 设计实现/ui-design（u）：负责视觉层级、暗黑模式、玻璃效果、可访问性、状态和 Token；本技能只要求小程序端 WXML/WXSS/真机边界。
- UniApp 开发/uniapp-development（unap）：负责 UniApp/跨端条件编译、manifest.json/pages.json、App/H5/多小程序；原生微信小程序深水区回到本技能。
- 微信支付/wechat-pay（wx）：负责微信支付 API v3、商户/证书/订单/回调/退款/分账/对账；本技能只处理小程序调起和前端证据。
- API 工程/api-engineering（api）：负责接口契约、认证授权、错误码、幂等、Webhook/Event、OpenAPI/SDK；本技能只列小程序消费侧证据和失败模式。
- 测试验证/test-engineering（tst）：负责测试矩阵、miniprogram-automator 深化、真机/体验版/回归证据；本技能提供小程序场景和风险输入。
- 代码审计/code-audit（aud）：负责完成前按需求、影响面、安全、回归和证据最终收口；本技能不替代审计结论。