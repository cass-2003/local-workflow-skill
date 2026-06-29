---
name: perf-engineering
description: 性能工程技能实战排障版 - 覆盖慢接口、慢查询、N+1、缓存击穿/雪崩/一致性、CPU/内存/GC/JIT/AOT/锁/线程、队列背压、网络/CDN/Core Web Vitals、移动/桌面/跨端启动与渲染卡顿、Kubernetes autoscaling、eBPF/flamegraph/load test、GPU/NPU/硬件/功耗/热 throttling、容量规划、性能回归门禁、成本-性能权衡与回滚证据，并明确与 AI、嵌入式、HDL/ASIC/FPGA 专项边界。
---
# 性能工程

> 首次自称：性能工程（perf-engineering，兼容 slug: pfe）。
> 命名口径：frontmatter name 使用 manifest canonical name `perf-engineering`；目录名和 URL 继续兼容 slug `pfe`；自检不得要求 name 等于短 slug。

> 定位：把“慢、卡、抖、占用高、掉帧、耗电、发热、容量不够、回归了”收敛成可复核闭环：基线 → 瓶颈 → 负载 → 证据 → 最小优化 → 同口径复测 → 容量/成本/功耗评估 → 回滚证据。
> 铁律：没有 baseline 不谈收益；没有 p95/p99 或端侧帧率/启动/功耗口径不谈体验；没有 profiling/flamegraph/trace/EXPLAIN/waterfall/heap/JFR/eBPF/Perfetto/MetricKit/PMU 等证据不下瓶颈结论；没有同口径复测、回归门禁、灰度或目标设备证据不宣称完成。

## 快速总则：基线 / 瓶颈 / 负载 / 证据

### 单技能工程门禁

- 接到性能需求先锁定对象：接口、任务、页面、启动、渲染、查询、队列、模型、硬件链路、地域或发布版本；对象不清不得泛泛优化。
- 任何“提升/下降/变快/变慢”都必须绑定优化前基线、采样窗口、样本量、环境、数据量、负载模型、缓存状态、预热和观测来源。
- 优化前先写验收阈值：目标 p95/p99、吞吐、错误率、资源上限、端侧帧率/启动/功耗、容量 headroom、单位成本或回滚触发。
- 一次只改一个主瓶颈或一组可解释的联动项；混改代码、配置、容量、缓存和索引时必须拆证据，否则无法归因。
- 性能改动必须同时检查正确性、幂等、一致性、权限隔离、排序、分页、事务、重试和降级语义；性能收益不能覆盖业务错误。
- 发布前必须有同口径复测、灰度/回滚指标、监控或日志埋点、性能回归门禁和未验证项；只在本机跑通不能宣称完成。

### 硬禁止与低级错拦截

- 禁止用“感觉快了”“本地快了”“平均值下降”代替 p95/p99、吞吐、错误率、资源和样本量。
- 禁止把压测工具默认参数当真实流量；缺 think time、热点分布、数据规模、缓存状态和下游限额时只能写结论有限。
- 禁止未看 EXPLAIN、慢日志、SQL 次数、锁等待和扫描行数就加缓存或扩容。
- 禁止未看 profile/flamegraph/heap/trace 就改 GC、线程池、连接池、runtime 参数或锁结构。
- 禁止未做权限/租户/用户维度校验就改缓存 key、CDN cache key、本地缓存或预取逻辑。
- 禁止用旗舰机、模拟器、空库、小样本、预热缓存、单地域或单次运行代表线上体验。
- 禁止上线无回滚触发、无性能预算、无旧版本对照、无清缓存/回配置方案。
- 禁止把观测工具开销、采样偏差、符号化失败、trace 丢样或压测机瓶颈当业务瓶颈。

### 真实性能闭环验收

- 最小证据包：问题对象、优化前基线、瓶颈证据、改动点、同口径复测、正确性检查、容量/成本影响、灰度或发布观测、回滚方案。
- 负载闭环：至少说明并发/RPS、数据量、热点分布、预热、缓存命中、失败重试、下游 stub/真实依赖、压测机资源和采样窗口。
- 端侧闭环：至少覆盖低端机/主流机、弱网、冷/热启动、滚动/输入、前后台、内存峰值、功耗/温度和目标系统版本。
- 数据库闭环：性能技能只下瓶颈和验收目标；索引、表结构、迁移、Redis 数据模型必须交 db 并要求回读计划和一致性证据。
- 缓存闭环：每次缓存优化都要同时给 TTL、容量、命名空间、穿透/击穿/雪崩、防污染、失效、回源峰值和清理回滚。
- 发布闭环：上线后看同一时间窗、同一指标口径、发布标记、灰度对照、错误率、资源、成本、用户体验和回滚触发是否恢复。

### 基线与指标矩阵

- 服务端：记录接口/任务名、版本、地域、实例规格、数据量、缓存状态、并发/RPS、p50/p95/p99、错误率、吞吐、CPU、RSS/heap、GC、IO、网络、连接池和下游耗时。
- 数据库：记录 SQL 指纹、调用次数、扫描行数、返回行数、EXPLAIN、慢日志、锁等待、连接等待、buffer/cache 命中、复制延迟和事务范围。
- 前端 Web：记录 RUM 与实验室口径、LCP、INP、CLS、TTFB、资源体积、请求数、waterfall、JS 长任务、图片/字体、CDN 命中、弱网和低端机。
- 移动/桌面/跨端：记录冷/热启动、首帧、可交互、帧时间、jank/FPS、ANR/OOM/Jetsam、包体、主线程/渲染线程、内存峰值、功耗、温度和前后台恢复。
- 内存/并发/缓存：记录分配速率、引用链、峰值回落、句柄/goroutine/thread、队列长度、消费延迟、锁等待、重试次数、缓存命中、回源峰值、BigKey/HotKey。
- 判定口径：每个指标必须有优化前值、目标阈值、允许噪声、采样窗口、样本量、数据集、预热策略和失败条件；缺任何一项只能写“证据不足”。

1. 基线先行：记录优化前版本、环境、硬件/设备、OS/内核/浏览器/运行时、数据量、缓存状态、预热策略、流量模型、样本量、P50/P95/P99、错误率、吞吐、CPU/内存/IO/网络/DB/缓存/队列/帧率/功耗/温度指标。
2. 瓶颈归一：先判断主因属于 CPU、内存/GC/泄漏、JIT/运行时、DB/锁/连接池、网络/CDN、渲染/启动/主线程、GPU/NPU、缓存、并发锁、队列背压、Kubernetes autoscaling、下游依赖、硬件 throttling、容量不足还是负载模型错误。
3. 负载可信：区分 micro benchmark、profile run、load、stress、spike、soak、端侧滚动/启动/弱网、硬件长稳、线上灰度；写明并发数、RPS/QPS、think time、热点分布、数据规模、设备档位、温度/电量、限流和第三方依赖替身。
4. 证据分层：trace 看链路，profiling/flamegraph/JFR/pprof/eBPF/perf/VTune 看 CPU/内存/锁/内核，EXPLAIN/慢日志看 DB，waterfall/Lighthouse/RUM 看前端，Perfetto/Instruments/MetricKit 看移动，PMU/功耗仪看硬件，heap snapshot 看泄漏，监控曲线看饱和。
5. 容量成模：把峰值、突增、季节性、headroom、饱和点、扩容提前量、降级容量、灾备容量、功耗/热持续能力写成可演练模型；必要时用 Little’s Law 校验并发、吞吐和排队等待。
6. 先改最大贡献项：一次只动主瓶颈；缓存、索引、异步化、连接池、扩容、HPA、CDN、SIMD、GPU offload、运行时参数都不是万能药，必须说明收益来源、正确性风险和单位成本。
7. 尾延迟和持续体验优先：默认看 p95/p99、错误率和吞吐下限；端侧看低端机、弱网、冷启动、帧时间、掉帧、ANR/OOM、功耗和热降频；平均值只能辅助。
8. 正确性红线：权限、金额、幂等、排序、分页、一致性、缓存隔离、回放安全、实时截止期、降级语义不得为性能让路。
9. 收口证据：给同环境同数据同负载复测、回归门禁、回滚方案、监控/告警、灰度指标、目标设备或目标硬件证据和未验证项；未跑只能写“需验证”。

## 场景执行卡

### 1. 性能分诊与证据建模

- 适用：只有“慢/卡/CPU 高/内存涨/偶发抖动/掉帧/耗电/发热/容量不够”。
- 输入：影响范围、时间窗口、SLO/SLA、版本、环境规格、设备/硬件档位、数据量、流量峰值、最近发布/配置/依赖/系统升级变更。
- 动作：画入口、应用、运行时、DB、缓存、队列、下游、网络/CDN、端侧渲染、GPU/NPU、Kubernetes 调度与硬件资源链路；按耗时、饱和度、用户影响和成本排序。
- 证据：trace span、APM、profiling、flamegraph、metrics、日志、RUM、EXPLAIN、heap、eBPF、Perfetto/Instruments、PMU、发布标记。
- 输出：主瓶颈、次瓶颈、容量风险、基线、证据缺口、最小修复顺序、回滚证据要求。

### 2. 慢接口 / 慢查询 / N+1 / 深分页

- 先查：trace 总耗时拆分、SQL 次数、慢查询日志、EXPLAIN、扫描行数、索引选择、锁等待、连接池等待、事务耗时、返回体积、序列化耗时。
- 常见错因：循环内 IO/N+1、SELECT *、深 OFFSET、排序/聚合临时表、缺失覆盖索引、事务过长、下游慢被误判成 DB 慢。
- 优先动作：批量查询、预加载、字段裁剪、游标分页、减少事务范围、连接池上限与超时预算；索引/表结构细节切 db。
- 验证：SQL 次数、扫描行数、DB CPU/IO、锁等待、连接等待、p95/p99、错误率、吞吐和结果一致性。

### 3. 数据库深水位 / 锁 / 复制 / 分片热点

- 先查：连接池饱和、事务年龄、行锁/表锁/死锁、等待事件、buffer hit、checkpoint/VACUUM/ANALYZE、复制延迟、主从读一致性、分区/分片热点、慢日志样本。
- 常见错因：应用连接池过大压垮 DB、长事务阻塞清理、读从库读到旧数据、热点租户/热点分片倾斜、统计信息过期导致执行计划漂移。
- 优先动作：收紧事务边界、隔离长任务、连接池预算、读写路由约束、热点拆分、补统计维护；结构性变更交 db。
- 验证：等待事件下降、锁等待消失、复制延迟可控、计划稳定、p99 和错误率改善，且旧数据/一致性路径未破坏。

### 4. CPU 热点 / 算法复杂度 / 主线程长任务

- 先查：profile、flamegraph、JFR/pprof/perf、Performance Long Task、采样窗口、符号化、热点函数累计占比、输入规模与复杂度曲线。
- 常见错因：大 JSON、正则回溯、重复排序过滤、加解密/压缩、图片处理、同步 IO、过度序列化、低复杂度输入掩盖高复杂度算法。
- 优先动作：降复杂度、减少分配、缓存纯计算、批处理、Worker/后台线程、分片让出主线程、SIMD/原生扩展需有收益和维护边界。
- 验证：CPU 利用率、单次耗时、热点占比、INP/输入延迟、吞吐、功耗和低端设备表现。

### 5. 语言运行时矩阵：Go / Python / JS / JVM / .NET / Ruby / PHP / Rust / C/C++

- Go：查 pprof、trace、goroutine dump、mutex/block profile、GC pause、alloc rate、逃逸、scheduler latency、CGO；PGO/版本升级前后重建基线。
- Python：查 cProfile/py-spy/scalene、GIL、async 阻塞、pickle/JSON、NumPy 向量化、内存引用、tracemalloc、进程模型和 C 扩展边界。
- Java/Kotlin/Scala：查 JFR、async-profiler、GC 日志、heap dump、lock/park、JIT warmup、virtual thread pinning、连接池和线程池。
- JS/TS/Node/Electron：查 V8 profiler、event loop lag、heap snapshot、GC、bundle parse/compile、IPC、stream/backpressure、hydration 和 main/renderer 进程。
- .NET：查 dotnet-trace/counters/dump、GC mode、LOH、async/ThreadPool starvation、JIT/AOT/NativeAOT、Span/alloc 和锁等待。
- Ruby/PHP：查 profiler、autoload、ORM N+1、GC、opcache/JIT、fiber/event loop、模板渲染、扩展和 FPM/worker 饱和。
- Rust/C/C++：查 perf/VTune/sanitizer、allocator、copy/clone、cache locality、锁、async executor、unsafe/FFI、LTO/PGO、SIMD 和未定义行为风险。
- 验证：运行时版本、参数、profile 证据、JIT/AOT/PGO/预热口径、allocator/分配速率、内存与锁指标、同输入规模复测；只改参数不解释机理不能下结论。

### 6. 内存 / GC / 泄漏 / 资源释放

- 先查：RSS/heap/native memory、heap snapshot diff、引用链、GC pause、对象分配速率、线程/goroutine/timer/observer/句柄、容器 OOMKill、Jetsam/tombstone。
- 常见错因：把缓存/预热误判泄漏，订阅/定时器未释放，对象池保留大对象，闭包引用大上下文，流式场景全量加载，native/GPU 内存未计入 heap。
- 优先动作：生命周期释放、缓存容量和淘汰、流式处理、减少大对象复制、图片降采样、连接/文件句柄关闭、GC 参数只在证据明确时调整。
- 验证：多轮进入退出、峰值回落、GC pause、OOM/ANR/Jetsam、句柄数量、容器 memory limit 与 request、低内存设备表现。

### 7. 缓存 / HotKey / 缓存击穿 / 雪崩 / 一致性

- 先查：命中率、key 分布、BigKey/HotKey、TTL 分布、容量、淘汰、穿透率、回源 QPS、身份隔离、失效路径、本地缓存与多级缓存一致性。
- 常见错因：缓存无 TTL/容量/命名空间，热点同时过期，负缓存缺失，写后读一致性没定义，缓存污染越权，Redis Cluster hot slot、reshard/failover、MOVED/ASK 或跨 slot pipeline 问题，BigKey 阻塞。
- 优先动作：请求合并、互斥重建、随机 TTL、预热、负缓存、限流降级、热点拆分、本地缓存边界、集群路由核验、失效事件和最终一致性说明。
- 验证：命中率、回源峰值、尾延迟、Redis CPU/内存/网络/碎片率、BigKey/HotKey、slot 分布、故障转移表现、数据一致性和回滚清缓存方案。

### 8. 并发 / 锁竞争 / 队列背压 / 重试风暴

- 先查：线程池/连接池、队列长度、消费速率、锁等待、死锁、重试次数、超时预算、下游错误率、限流丢弃率、partition/consumer group 状态。
- 常见错因：无界队列、同步锁包住 IO、失败立即重试、消费者慢无背压、批量任务无幂等、连接池放大下游压力、队列 rebalance、ack 超时或 visibility timeout 造成重复处理。
- 优先动作：有界队列、背压、限流、熔断、指数退避+jitter、减少锁粒度、批处理、幂等键、ack/续租/visibility timeout sizing、死信队列、DLQ 回放限速、降级策略。
- 验证：队列堆积时间、p95/p99、锁等待、下游 QPS、错误率、ack 超时、重复投递、丢弃/降级数量和恢复时间。

### 9. 网络 / TLS / DNS / LB / Service Mesh / IO

- 先查：DNS 解析、连接复用、TLS 握手、HTTP/2/3、队头阻塞、MTU、丢包、跨区延迟、LB 算法、mesh sidecar、重试/超时、磁盘 IOPS/queue depth/fsync。
- 常见错因：每请求建连、DNS 缓存失效、超时层级倒挂、mesh 重试叠加、跨区调用隐藏在服务发现后、磁盘同步写被误判成 CPU 慢。
- 优先动作：连接池和 keepalive、超时预算、就近路由、减少跨区、批量/异步 IO、压缩阈值、mesh/LB 策略联动 cld。
- 验证：握手次数、连接复用率、网络 p99、丢包/重传、磁盘 await/util、sidecar 指标、端到端错误率。

### 10. 前端 Web / CDN / Core Web Vitals / 渲染

- 先查：RUM、Lighthouse、waterfall、bundle analyzer、LCP 资源、INP 长任务、CLS 来源、缓存命中、CDN hit ratio、TTFB、字体和图片体积。
- 常见错因：只看实验室首屏不看真实用户，CDN 缓存键错误，图片未响应式，hydration 长任务，全量 rerender，虚拟列表缺失，布局抖动。
- 优先动作：CDN 缓存策略、资源裁剪、code splitting、预加载关键资源、图片压缩/懒加载/响应式、减少 JS 主线程、虚拟列表、稳定占位。
- 验证：LCP/INP/CLS、TTFB、资源体积、CDN 命中率、弱网、低端机、真实浏览器矩阵和回滚到旧资源策略。

### 11. 移动 / 跨端 / 桌面：启动、掉帧、ANR、OOM、耗电

- Android：查 cold/warm/hot start、first frame、ANR trace、Perfetto、Android vitals、RenderThread、binder、DEX/class loading、bitmap、wake lock、Doze/background 限制。
- iOS/macOS：查 cold/warm/hot start、MetricKit、Instruments Time Profiler/Allocations/Leaks、os_signpost、main thread checker、dyld、Jetsam、thermal state、background task。
- Flutter/React Native/WebView：区分 Dart/JS/native、UI/raster/GPU thread、bridge/JSI、shader warmup、Hermes/JSC、WebView 内核、热更新包体和首屏数据依赖。
- Electron/桌面：查 main/renderer 进程、IPC、bundle parse、模块加载、GPU process、native addon、内存预算、窗口冷启动和后台常驻。
- 验证：低端机/主流机/高端机、弱网、电量、温度、前后台切换、多轮启动、滚动/输入场景、帧时间、jank/FPS、ANR/OOM/Jetsam、功耗和包体。

### 12. 图形 / GPU / NPU / AI 推理性能

- 先查：GPU/NPU 利用率、kernel timeline、occupancy、显存/带宽、PCIe/拷贝、batch size、tensor shape、delegate fallback、shader/pipeline 编译、驱动版本。
- 常见错因：CPU-GPU 拷贝占主导，显存碎片或带宽瓶颈，NPU 不支持算子回退 CPU，batch 过大导致尾延迟，shader 首次编译造成 jank。
- 优先动作：减少拷贝、算子融合、预热、量化/裁剪需验证质量、合理 batch、显存复用、异步 pipeline、fallback 明确标注。
- 验证：首帧/首 token、p95/p99、吞吐、显存峰值、功耗、温度、驱动/设备矩阵、模型质量或渲染正确性不回退。

### 13. 硬件 / OS / 内核 / 功耗 / 热 throttling

- 先查：CPU frequency、thermal state、PMU counters、IPC、cache/TLB/branch miss、NUMA locality、memory bandwidth、context switch、syscall、IRQ、RSS/softirq、cgroup throttling、battery current。
- 常见错因：把热降频当代码回归，把 NUMA/内存带宽当 CPU 算力不足，把 cgroup throttling 当应用慢，把观测采样开销当真实负载。
- 优先动作：固定 governor/电源模式或记录其状态，绑核/NUMA 需有证据，减少拷贝和 syscall，调整中断/RSS/线程亲和需联动平台 owner。
- 验证：频率/温度/功耗曲线、PMU 指标、长稳 soak、低电量/高温、容器限制、同硬件同系统复测。

### 14. Kubernetes / 容器 / autoscaling / 发布容量

- 先查：requests/limits、CPU throttling、OOMKill、HPA/VPA/KEDA 指标、pod 启动、探针、连接耗尽、DNS、service mesh、PDB、滚动发布期间可用容量、节点饱和、冷启动。
- 常见错因：CPU limit 触发 throttling 却误判代码慢，HPA 指标滞后，扩容慢于流量尖峰，探针过重，滚动发布期间容量掉洞，跨区网络和 mesh sidecar 放大延迟。
- 优先动作：修正 request/limit、HPA 指标和冷却窗口、预扩容、连接复用、探针瘦身、节点池容量、PDB/滚动参数、灰度与回滚指标交 cld/rls。
- 验证：pod ready 时间、扩容时延、throttling、p95/p99、错误率、节点饱和度、发布窗口容量和回滚后指标恢复。

### 15. 压测 / 容量规划 / 性能回归门禁

- 先查：目标是 micro benchmark、单接口 load test、整链路容量、stress、spike、soak、恢复性压测、降级压测、发布前基线、端侧场景基准还是 CI 回归冒烟。
- 容量模型：记录日常峰值、活动峰值、突增斜率、季节性、数据增长、下游限额、队列排队、饱和资源、headroom、扩容提前量、降级容量、灾备容量和热/功耗持续能力。
- 压测动作：固定环境、数据量、热点分布、预热、采样窗口、think time、第三方 stub 或限流口径、监控；覆盖长稳、spike 后恢复、故障注入、限流/熔断/降级验证。
- 门禁动作：定义性能预算、自动基线、噪声范围、统计显著性、失败分级、阻断条件、豁免记录、灰度对比和回滚触发。
- 门槛：关键接口 p95/p99 上限、吞吐下限、错误率上限、资源上限、单位成本上限；前端 CWV budget；移动启动/掉帧；K8s 扩缩容恢复时间。
- 失败兜底：无 think time、无真实数据、无热点、无生产限流、样本太小、端侧设备不足或噪声未控时，只能写“压测结论有限”。
- 回归阈值：默认比较同口径基线与候选版本；p95/p99、错误率、OOM/ANR、资源峰值、单位成本或关键端侧指标超过预算即阻断，除非有记录的业务豁免。
- 压测可信度：必须证明瓶颈不在压测机、脚本、网络出口、DNS、端口、stub、日志写入或观测系统；不能证明时不得把结果归因到被测服务。
- 验收闭环：压测报告必须包含基线、改动版本、负载模型、监控截图或指标源、瓶颈证据、复测差值、正确性抽样、容量结论、回滚触发和未覆盖风险。

### 16. LLM / 向量检索 / serverless / 边缘

- LLM：拆首 token、总延迟、吞吐、上下文长度、工具调用、RAG、缓存、批量、流式、并发限额、重试、质量和成本；延迟不能脱离输出质量。
- 向量检索：查 HNSW/IVFFlat、维度、过滤条件、topK、召回率、VACUUM/ANALYZE、冷热数据、索引构建和写入延迟；性能与召回共同验收。
- Serverless：冷/热启动分开报，包体、依赖初始化、连接复用、地域、预热、并发限制和账单粒度都要入基线。
- 边缘与多地域：查地域路由、边缘计算、CDN cache key、边缘缓存失效、多区域一致性、HTTP/3 回退、局部区域 p99 和边缘观测。

### 17. 嵌入式 / RTOS / FPGA / ASIC 性能边界

- 嵌入式/RTOS：性能结论必须绑定 MCU/SoC、clock、功耗模式、ISR latency、任务优先级、stack/heap、DMA/cache coherency、WCET、仪器或 HIL 证据；细节切 embd。
- FPGA/ASIC：吞吐、latency、area、power、timing closure 必须区分仿真、综合、STA、板级/硅后；约束、CDC/RDC、资源和功耗报告细节切 hfa。
- 兜底：QEMU/Renode、RTL sim、开源 EDA 或 host benchmark 不等于目标硬件持续性能；缺目标板/目标器件证据必须标“未验证”。

### 18. 成本-性能 / 可观测性专项

- 成本-性能：记录单位请求成本、资源利用率、峰谷利用、缓存/CDN/DB/GPU 成本曲线、过度扩容风险和优化 ROI；降延迟不能隐藏成本暴涨。
- APM/eBPF：写明采样策略、开销预算、权限风险、生产启停、符号化失败处理、trace-profile 关联和数据保留；观测本身不能显著改变生产表现。
- 发布观测：性能改动必须有发布标记、核心指标、告警阈值、回滚触发、灰度对照和清理动作；观测缺口先补观测，不硬宣称完成。

## 高频坑 / 防遗漏

### 高频坑

1. 无 baseline 或换环境对比，宣称优化成功。
2. 只看平均值，不看 p95/p99、错误率、样本量和吞吐。
3. 用 benchmark 代替生产 load test，把缓存预热当优化收益。
4. 循环内查库/HTTP/文件 IO 形成 N+1。
5. 深分页 OFFSET、SELECT *、过大响应体、过度序列化。
6. 缓存无 TTL、容量、失效、隔离，导致击穿、雪崩、污染或不一致。
7. 重试无超时预算、退避和 jitter，放大下游故障。
8. 无界队列和锁包 IO，没有背压和降级。
9. CPU limit throttling、GC pause、连接池等待被误判成业务代码慢。
10. 只优化 LCP，不看 INP/CLS、CDN 命中和真实用户低端机。
11. 移动只测旗舰机 Wi-Fi，忽略低端机、弱网、电量、后台恢复和 WebView/跨端边界。
12. HPA 指标滞后、滚动发布容量下降或冷启动慢，扩容赶不上 spike。
13. 容量只按平均 QPS 算，不看 p99、突增、队列等待和 headroom。
14. CI 性能测试噪声未控，误阻断或完全不阻断，缺豁免记录。
15. 为降延迟盲目扩容，单位成本暴涨，资源利用率长期低。
16. soak 时间不够，上线后连接泄漏、缓存膨胀、队列堆积、热降频才暴露。
17. eBPF/APM 采样无边界，观测开销或符号化错误导致误判。
18. 边缘/CDN 缓存键或地域路由错误，局部区域 p99 被全局均值掩盖。
19. GPU/NPU fallback、shader warmup、显存拷贝或驱动差异被漏掉。
20. 运行时升级、JIT/PGO、GC 参数、内核/OS 升级后沿用旧基线。
21. 上线无回滚证据、监控阈值和性能回归门槛。

### 防遗漏清单

- 慢接口/DB：trace、SQL 次数、EXPLAIN、慢日志、扫描行数、锁等待、连接池、事务、复制延迟、N+1、分页、响应体。
- CPU/运行时：profiling、flamegraph、采样窗口、热点累计占比、分配速率、GC pause、JIT/PGO、符号化、锁/线程/协程。
- 内存：heap/native/GPU memory、heap diff、引用链、缓存上限、timer/observer/goroutine/thread、句柄、多轮复现、OOMKill/Jetsam。
- 缓存：TTL、容量、key 设计、BigKey/HotKey、穿透/击穿/雪崩、回源、隔离、一致性、清缓存回滚。
- 并发/队列：锁等待、连接池、线程池、队列长度、消费速率、partition、rebalance、背压、限流、熔断、死信、幂等。
- 前端/CDN：waterfall、bundle、LCP、INP、CLS、TTFB、CDN hit ratio、图片、字体、hydration、弱网低端机。
- 移动/桌面：冷/热启动、首帧、帧时间、ANR、OOM/Jetsam、Perfetto/Instruments、IPC、包体、耗电、温度、前后台恢复。
- K8s/网络/IO：requests/limits、throttling、HPA/VPA/KEDA、pod ready、DNS、mesh、跨区、探针、PDB、节点、磁盘 await、连接复用。
- GPU/NPU/硬件：occupancy、显存/带宽、PCIe copy、delegate fallback、shader compile、PMU、IPC、cache/TLB miss、NUMA、频率、温度、功耗。
- 压测/容量：负载模型、think time、热点分布、数据量、预热、采样、错误率、吞吐、资源、headroom、饱和点、扩容提前量。
- 回归门禁：性能预算、自动基线、噪声控制、统计阈值、阻断条件、失败分级、豁免、灰度验证。
- 成本/边缘/APM：单位成本、资源利用率、地域路由、HTTP/3 回退、采样开销、trace-profile 关联、回滚触发。

## 输出要求

性能工程输出必须极简但可复核，至少包含：

1. 问题类型：慢接口/慢查询/CPU/内存/GC/JIT/IO/网络/CDN/渲染/启动/缓存/并发/队列/锁/Kubernetes/GPU/NPU/功耗/容量/成本/移动/桌面/边缘/LLM/回归。
2. 症状指标：影响范围、时间窗口、p50/p95/p99、错误率、吞吐、CPU/内存/IO、DB/缓存/队列、CWV/FPS/启动/ANR/OOM/功耗/温度、单位成本。
3. 环境与基线：版本、规格、地域、硬件/设备/OS/运行时、数据量、缓存状态、预热、流量模型、样本量、优化前口径。
4. 定位证据：trace、profiling、flamegraph、EXPLAIN、慢日志、waterfall、heap、JFR/eBPF/perf、RUM、Perfetto/Instruments、PMU、监控曲线。
5. 瓶颈归因：主因、次因、证据链、排除项和证据缺口。
6. 容量、成本与功耗：峰值、headroom、饱和点、扩容提前量、降级策略、演练证据、单位成本、ROI、功耗/热持续能力。
7. 优化方案：最小改动、收益来源、正确性风险、观测项、回滚方式。
8. 验证门槛：同口径复测、load/stress/spike/soak、端侧/硬件矩阵、CI 门禁、灰度结果、性能预算、上线监控和剩余风险。
9. 联动技能：DB/索引切 db；后端链路切 be；K8s/发布切 cld/rls；前端/Node 切 jsts；移动/跨端切对应端技能；成本切 fop；数据/AI 细节切 de/aie；嵌入式切 embd；RTL/FPGA/ASIC 切 hfa；验证切 tst；最终 aud 收口。

## 约束

- 不凭体感、平均值、单次本地结果、无预热 benchmark 或旗舰设备单点体验下结论。
- 不在缺少数据量、流量模型、样本量、环境和设备/硬件说明时承诺容量或端侧体验。
- 不把缓存、索引、异步、连接池、扩容、HPA、CDN、GPU offload、运行时参数当默认答案；每项必须绑定证据。
- 不为性能牺牲权限、幂等、一致性、排序、事务、实时截止期、可恢复性和可维护性。
- 不把测试环境绿、压测绿、模拟器绿、RTL sim 绿包装成线上/真机/真实硬件绿；必须说明与生产或目标硬件差距。
- 不用平均 QPS 代替容量规划；必须说明峰值、突增、headroom、饱和点、扩容提前量、降级容量和持续功耗/热边界。
- 不用“扩容解决”掩盖单位成本、资源利用率、长期 ROI 和功耗；成本或功耗不可验证时标“需验证”。
- 涉及 SQL/索引/迁移必须联动 db；涉及实现联动对应语言/端；涉及验证联动 tst；涉及发布/灰度/回滚联动 rls 或 cld；改动完成前用 aud 收口。

## 高频 Bug 反例库

- 反例 1：无基线宣称优化
  - 错：改完说“快了很多”，没有优化前 p95/p99、吞吐、CPU、数据量和样本量。
  - 对：固定环境、数据量、负载模型和采样窗口，保存优化前后同口径指标。
  - 根因：没有基线就无法排除缓存预热、环境漂移和噪声。
- 反例 2：只看平均延迟
  - 错：平均耗时下降就上线，p99、错误率和超时重试变差未发现。
  - 对：同时比较 p50/p95/p99、错误率、吞吐、资源和样本量。
  - 根因：用户体验和容量风险主要由尾延迟决定。
- 反例 3：benchmark 冒充 load test
  - 错：本地 micro benchmark 快 30%，就承诺生产容量提升。
  - 对：补真实负载、热点分布、think time、数据量、下游限流和线上灰度验证。
  - 根因：单点基准不能覆盖排队、锁、网络、DB 和下游饱和。
- 反例 4：慢查询只加缓存
  - 错：SQL 扫描百万行却先加缓存，失效时数据库被打穿。
  - 对：先用 EXPLAIN、慢日志、扫描行数定位；索引/分页/表结构交 db，同时设计缓存失效。
  - 根因：缓存掩盖主瓶颈，不能替代查询结构优化。
- 反例 5：缓存一致性和隔离缺失
  - 错：缓存 key 不带租户/权限维度，写后读旧数据或串用户数据。
  - 对：定义 key 命名空间、失效事件、写后读策略、TTL、清理和回滚方案。
  - 根因：性能优化改变了数据可见性和安全边界。
- 反例 6：重试风暴
  - 错：下游超时后立即并发重试，连接池占满，故障扩大。
  - 对：超时预算、最大次数、指数退避、jitter、熔断、限流和幂等。
  - 根因：重试是额外负载，不受控会压垮依赖。
- 反例 7：锁竞争包住 IO
  - 错：全局锁内查库/HTTP，低并发正常，高并发线程全部等待。
  - 对：缩小临界区、拆锁、无锁/分段、IO 移出锁外，并用 profile/JFR/eBPF 验证锁等待。
  - 根因：串行化热点把吞吐上限压到单线程。
- 反例 8：无界队列无背压
  - 错：生产速度大于消费速度仍无限入队，内存上涨、延迟失真、最终 OOM。
  - 对：有界队列、背压、限流、死信、丢弃策略、消费扩容和堆积告警。
  - 根因：队列隐藏失败，把延迟转成内存和恢复时间。
- 反例 9：GC/内存泄漏误判
  - 错：看到 RSS 不降就改 GC 参数，没看 heap diff、引用链、native 内存、缓存和容器限制。
  - 对：多轮复现、heap snapshot、分配速率、GC pause、OOMKill/Jetsam 和资源释放验证。
  - 根因：内存占用高、缓存保留、碎片化和真实泄漏是不同问题。
- 反例 10：Core Web Vitals 只看首屏
  - 错：只压 LCP，主线程 hydration 和大 JSON 让 INP 变差，CLS 来源未修。
  - 对：同时看 LCP/INP/CLS、RUM、长任务、低端机、弱网和 CDN 命中。
  - 根因：真实用户性能由加载、交互和视觉稳定共同决定。
- 反例 11：移动性能只测旗舰机
  - 错：旗舰机 Wi-Fi 流畅，低端机冷启动、弱网、耗电、后台恢复和 WebView 场景全劣化。
  - 对：覆盖 Android/iOS、低端机、弱网、电量、ANR/jank、内存峰值、跨端边界和前后台恢复。
  - 根因：移动性能强依赖设备、网络、系统调度和运行时。
- 反例 12：Kubernetes 扩容误判
  - 错：代码没变 p99 升高，忽略 CPU throttling、HPA 滞后、pod cold start、PDB 和滚动发布容量下降。
  - 对：检查 requests/limits、HPA/VPA/KEDA、pod ready、throttling、节点资源、PDB 和发布标记。
  - 根因：平台层容量和调度会直接改变应用尾延迟。
- 反例 13：容量只按平均 QPS 估算
  - 错：用日均 QPS 规划机器数，没算 p99、突增斜率、队列等待、headroom 和下游限额。
  - 对：建峰值/突增/季节性模型，找饱和资源、扩容提前量、降级容量，并做容量演练。
  - 根因：容量风险来自峰值和排队，平均值会掩盖饱和点。
- 反例 14：CI 性能门禁噪声失控
  - 错：同一脚本在共享环境波动很大，时而误阻断，时而完全放行。
  - 对：固定环境和数据，记录自动基线、噪声范围、统计阈值、失败分级、豁免和复测规则。
  - 根因：没有统计口径的门禁会变成随机信号。
- 反例 15：GPU/NPU 加速反而变慢
  - 错：把算子 offload 到 GPU/NPU 后只看平均耗时，忽略拷贝、fallback、显存和冷启动。
  - 对：看 kernel timeline、显存、PCIe/拷贝、delegate fallback、p95/p99、功耗和质量指标。
  - 根因：加速器收益常被数据搬运、算子不支持和预热成本抵消。
- 反例 16：热降频被当代码回归
  - 错：长稳后延迟升高就改代码，没看频率、温度、电量和功耗模式。
  - 对：记录 thermal state、CPU/GPU frequency、功耗曲线、环境温度和长稳 soak。
  - 根因：持续性能受硬件散热和电源策略限制。
- 反例 17：运行时升级沿用旧结论
  - 错：升级 Go/Node/JDK/.NET 后沿用旧 profile 和 GC/JIT 参数。
  - 对：重建基线，比较热点、GC、JIT、锁、内存和尾延迟。
  - 根因：运行时版本会改变优化器、调度器、GC 和标准库行为。
- 反例 18：上线无回滚证据
  - 错：只给优化代码，不给回滚条件、监控阈值、清缓存方案和灰度对比。
  - 对：定义回滚触发、旧版本指标、缓存/配置回退、灰度窗口和告警。
  - 根因：性能改动常跨缓存、容量和依赖，无法回退就无法安全发布。
- 反例 19：压测机先瓶颈
  - 错：压测结果 QPS 上不去就改服务端，没看压测机 CPU、连接数、网卡、端口耗尽和脚本阻塞。
  - 对：压测端、服务端、下游和网络同时观测，确认瓶颈不在压测工具或压测环境。
  - 根因：负载发生器也是系统一部分，先饱和会制造假瓶颈。
- 反例 20：预热收益冒充优化收益
  - 错：第一次跑慢、第二次跑快，就把缓存/JIT/连接预热当代码优化。
  - 对：固定冷/热口径，分别记录预热策略、缓存状态、JIT warmup 和连接复用。
  - 根因：冷启动、热路径和持续负载是不同场景。
- 反例 21：连接池越大越好
  - 错：接口慢就把 DB/HTTP 连接池翻倍，结果下游锁等待和错误率上升。
  - 对：按下游容量、超时预算、队列长度和 p99 调整池大小，并设置背压。
  - 根因：连接池放大并发压力，不创造下游处理能力。
- 反例 22：HPA 看 CPU 忽略业务队列
  - 错：CPU 不高就认为不用扩容，队列堆积和消费延迟持续增长。
  - 对：把队列长度、消费延迟、lag、错误率和业务 SLO 纳入扩缩容或预扩容策略。
  - 根因：CPU 不是所有工作负载的饱和信号。
- 反例 23：CDN 命中率好但用户慢
  - 错：全局 CDN hit ratio 很高就判定静态资源没问题，忽略某地域、某运营商和 cache key 分裂。
  - 对：按地域、网络、资源类型、cache key、TTFB、LCP 和回源错误分层看。
  - 根因：全局均值会掩盖局部 p99 和路由问题。
- 反例 24：异步化丢失事务语义
  - 错：为降低接口耗时把关键写入丢到异步队列，失败补偿、幂等和用户可见状态没定义。
  - 对：定义同步/异步边界、状态机、幂等键、补偿、DLQ 和用户提示，再评估性能收益。
  - 根因：异步化改变一致性和可恢复性。
- 反例 25：批处理放大尾延迟
  - 错：为提高吞吐把所有请求攒大批，低流量时等待时间暴涨。
  - 对：设置 max batch size、max wait、优先级和超时，分别验吞吐与 p99。
  - 根因：吞吐优化常以等待时间为代价。
- 反例 26：观测采样漏掉慢路径
  - 错：trace 采样率太低或只采成功请求，慢请求、错误请求和取消请求没证据。
  - 对：对错误、超时、慢请求提升采样，关联 trace/profile/log 和发布标记。
  - 根因：采样策略决定能看到什么问题。
- 反例 27：优化图片破坏业务质量
  - 错：大幅压缩图片后 LCP 下降，但商品图、证件图或医学图失真。
  - 对：按业务质量阈值、格式、DPR、响应式尺寸和关键页面验收。
  - 根因：性能指标不能替代用户可用性和业务正确性。
- 反例 28：限流降级没有用户语义
  - 错：加限流后 p99 好看了，但核心用户被随机拒绝，重试风暴更严重。
  - 对：按优先级、配额、排队、降级内容、Retry-After 和幂等重试设计。
  - 根因：限流是产品和系统语义，不只是技术开关。
- 反例 29：索引优化没看写入成本
  - 错：为读查询加多个索引，读 p95 下降，写入延迟、存储和复制延迟恶化。
  - 对：读写比例、索引选择、写放大、存储、复制延迟和维护成本一起验收。
  - 根因：索引收益和写入/存储成本绑定。
- 反例 30：灰度样本不代表全量
  - 错：灰度只覆盖低流量租户，宣布全量容量安全。
  - 对：覆盖大租户、热点数据、地域、设备、权限路径和峰值窗口，必要时做影子流量。
  - 根因：性能风险往往集中在长尾大户和热点路径。

## 提交前自检清单

- [ ] frontmatter name/description 存在，name 为 perf-engineering；H1 为“性能工程”；自检不得要求 name 等于短 slug。
- [ ] 行数 < 500，正文无 fenced code block，正文不出现反引号围栏。
- [ ] 必需章节齐全：快速总则、场景执行卡、高频坑/防遗漏、输出要求、约束、反例库、自检、新坑速查、相邻边界。
- [ ] 已覆盖 profiling、flamegraph、load test、stress、spike、soak、p95/p99、吞吐/延迟、DB 慢查询、N+1、锁竞争、队列背压。
- [ ] 已覆盖容量规划、性能回归门禁、成本-性能、移动/桌面/跨端性能、边缘性能、APM/eBPF 操作规范。
- [ ] 已覆盖缓存击穿/雪崩/一致性、CPU/内存/GC/JIT、CDN/Core Web Vitals、Kubernetes autoscaling、eBPF、基准对比和回滚证据。
- [ ] 已覆盖语言运行时矩阵、GPU/NPU、硬件/OS/内核、功耗/热 throttling、嵌入式/FPGA/ASIC 性能边界。
- [ ] 已覆盖单技能工程门禁、硬禁止与低级错拦截、真实性能闭环验收。
- [ ] 每个性能结论都有证据、基线、负载口径、样本量、资源指标和同口径复测要求。
- [ ] 容量结论包含峰值、headroom、饱和点、扩容提前量、降级策略和演练证据。
- [ ] 门禁结论包含预算阈值、统计口径、阻断条件、豁免、灰度验证和回滚条件。
- [ ] 反例不少于 30 条，且每条包含错法、对法、根因。
- [ ] 已明确 db、be、obs、cld、rls、jsts、端技能、fop、de、aie、embd、hfa、tst、aud 的边界。

## 2024-2026 新坑速查

- [Chrome INP] INP 替代 FID 成为 Core Web Vitals 关键指标；只优化首屏会漏交互长任务，必须结合 RUM p75/p95。
- [OpenTelemetry profiling] trace 只能解释链路，profiling 才解释 CPU/内存热点；采样率、符号化和 span 关联要写清。
- [eBPF] 线上低侵入 profiling 适合查锁、内核、网络和 off-CPU，但受内核版本、权限、符号和采样偏差影响。
- [Go PGO] PGO/AutoFDO 会改变热路径表现；优化前后记录 Go 版本、PGO 是否启用和 profile 来源。
- [Java virtual threads] 虚拟线程不消除 DB、锁、连接池瓶颈；JFR 仍要看 pinning、锁等待、分配和 GC。
- [Node/V8] Node 20/22/24、V8 优化层、GC、fetch/stream 行为变化会让热点漂移；升级后必须重建基线。
- [Mobile startup] Android/iOS 冷/热启动、首帧、包体、动态库、DEX/Hermes/JS bundle 和首屏数据依赖必须分开看。
- [Flutter/RN/WebView] UI/raster/GPU thread、bridge/JSI、shader warmup、WebView 内核和热更新包体会改变 jank 来源。
- [Electron/Desktop] main/renderer/IPC、module loading、GPU process、native addon 和多进程内存预算常是桌面性能主因。
- [Redis 7.4 field TTL] Hash field TTL 改变缓存拆分策略，但 BigKey、HotKey、淘汰和过期风暴仍要验证。
- [HTTP/3/QUIC/CDN] 弱网可能改善握手与队头阻塞，但连接迁移、负载均衡、观测、回退和 CDN 缓存键要验证。
- [Kubernetes autoscaling] HPA/VPA/KEDA、CPU throttling、pod cold start、PDB、rolling capacity 和 metrics lag 会影响 p99。
- [Serverless] 冷/热启动必须分开报；包体、依赖初始化、连接复用、地域和预热决定尾延迟。
- [LLM latency/cost] 首 token、总 token、上下文长度、工具调用、RAG、重试、批量和并发限额共同决定延迟与成本。
- [Vector DB] HNSW/IVFFlat、过滤条件、topK、召回率、VACUUM/ANALYZE、冷热数据会影响延迟，不能只看毫秒。
- [GPU/NPU] kernel occupancy、显存带宽、PCIe/拷贝、delegate fallback、驱动和 tensor shape 会决定真实收益。
- [Thermal/power] 手机、笔记本、边缘设备和 GPU 长稳性能受温度、电源模式、电池和散热约束，必须记录持续曲线。
- [Cache stampede] 热点 key 同时失效会击穿下游；互斥重建、随机 TTL、请求合并、预热、限流和降级必须成套验证。
- [Capacity drift] 数据增长、峰值迁移、热门对象变化和下游配额会让旧容量模型失效；容量基线需周期重算。
- [Edge routing] 边缘函数、地域路由、缓存键和多区域一致性会造成局部 p99；必须按地域和缓存层级看指标。

## 与相邻技能的边界

- perf-engineering：负责性能症状量化、基线、负载模型、证据链、瓶颈归因、容量模型、成本/功耗权衡、性能预算、回归门槛和回滚证据。
- be：负责后端具体实现、API 中间件、连接池、限流熔断、任务队列和运行时配置；本技能只给性能证据和目标。
- db：负责 SQL、索引、表结构、事务、迁移、Redis 数据模型与一致性细节；本技能只指出慢查询证据和性能目标。
- obs：负责监控、日志、trace、profile 接入、SLO、告警、incident 和 dashboard 治理；本技能消费并要求这些证据。
- cld：负责 Kubernetes、HPA/VPA/KEDA、Ingress、service mesh、资源配额、探针、PDB、灰度和集群容量配置；本技能判断其对 p95/p99 的影响。
- rls：负责发布、灰度、回滚、制品和环境门禁；本技能定义性能发布指标和回滚触发。
- jsts 与端技能：负责前端、Node、移动、桌面、跨端具体代码和框架实现；本技能定义 CWV、启动、主线程、帧率、功耗和资源预算。
- fop：负责预算、成本分摊、单位经济性和资源治理；本技能输出性能-成本证据与取舍。
- de：负责 ETL、流批、Kafka/Spark/Flink/数仓链路性能；本技能只做性能分诊与验收口径。
- aie：负责 LLM/RAG/向量检索模型质量、架构和评测；本技能只覆盖延迟、吞吐、并发、缓存、GPU/NPU 和成本证据。
- embd：负责 MCU/SoC、RTOS、DMA/cache、功耗和板级/HIL 证据；本技能只定义性能指标和验收边界。
- hfa：负责 RTL/FPGA/ASIC 的 timing、area、power、STA、CDC 和板级/硅后报告；本技能只定义吞吐/延迟/功耗口径。
- tst：负责测试矩阵、性能回归自动化、CI 证据、E2E/负载脚本质量；本技能定义性能验收指标。
- aud：负责改动后的影响面、安全/正确性/回归证据收口；性能改动完成前必须最终审计。
