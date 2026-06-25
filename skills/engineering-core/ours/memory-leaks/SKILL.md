---
name: memory-leaks
description: "内存泄漏排查跨语言实战。覆盖 Node.js heap snapshot 三快照对比法、Chrome DevTools Memory Profiler、Go pprof / 内存分析、Python tracemalloc / objgraph、Java VisualVM / heap dump、JVM GC 调优、Rust 工具、常见泄漏模式（闭包 / 监听器 / 缓存无界 / 全局引用 / 定时器）、容器 OOMKilled 排查、内存增长曲线诊断流程。当用户提到 内存泄漏、memory leak、heap snapshot、heap dump、OOM、OOMKilled、pprof、tracemalloc、heap profiling、内存增长、GC 问题、JVM 内存、垃圾回收 时使用。"
---

# Memory Leaks Skill — 内存泄漏排查

## 何时使用

- 服务跑久了内存爆 / OOMKilled
- Chrome 页面用一会卡顿 / 标签页崩溃
- 容器 RSS 持续增长不释放
- 单元测试通过但生产泄漏
- 怀疑某个改动引入泄漏

## 一、判断真泄漏 vs 假象

```
真泄漏：内存 monotonic 增长，永不下降，最终 OOM
   → 引用链让 GC 无法回收

假象：
  - 工作集大但稳定（cache 满了）→ 不是泄漏
  - 临时峰值（处理大请求）→ 不是泄漏
  - V8 / GC 延迟回收 → 等几分钟看是否下降
```

**最可靠诊断**：长时间观察 RSS 曲线。

```bash
# 容器
docker stats <container>
kubectl top pod <pod>

# 进程
ps aux | grep app
top -p <pid>
```

观察 **趋势**，不是瞬时值。

## 二、Node.js 内存模型

```
RSS = Resident Set Size（OS 视角，进程占的物理内存）
     = V8 heap + native heap + libuv buffers + ...

V8 heap = JS 对象（GC 管）
  - new space (young generation)
  - old space (long-lived)
  - large object space

外部缓冲区 = Buffer / ArrayBuffer
原生模块内存 = N-API addon 自管
```

```javascript
console.log(process.memoryUsage())
// { rss, heapTotal, heapUsed, external, arrayBuffers }
```

## 三、Node 三快照对比法（黄金流程）

```
1. 服务启动 + 跑一会 → snapshot 1（baseline）
2. 触发可疑操作 N 次
3. 强制 GC → snapshot 2
4. 再触发 N 次 → snapshot 3
5. 对比 snapshot 2 → snapshot 3：净增长就是泄漏
```

```javascript
// 启动允许 inspect 和 expose-gc
node --inspect --expose-gc app.js

// 代码或 console:
global.gc()
require('v8').writeHeapSnapshot('./snap-1.heapsnapshot')
```

Chrome → `chrome://inspect` → "Memory" → "Load profile" → Comparison view。

**Comparison 看什么**：
- "Delta" 列正数 = 增加的对象
- 按 retained size 排序
- 点对象看 **Retainers**（谁持有它，回溯到 GC root）

## 四、Node 常见泄漏模式

### 1. 闭包持有大对象

```typescript
// ❌ 整个 huge 被闭包捕获
function makeHandler(huge) {
  return () => console.log('hi')   // 没用 huge 但仍引用作用域
}

// ✅ 显式提取需要的
function makeHandler(huge) {
  const id = huge.id   // 只引用 id
  return () => console.log(id)
}
```

### 2. EventEmitter 监听器累积

```typescript
// ❌ 每次 add 都加，never remove
emitter.on('data', handler)
// 1000 次 emitter.on 后，1000 个 handler 引用 closure

// ✅ 用 once 或显式 off
emitter.once('data', handler)
emitter.off('data', handler)
emitter.removeAllListeners('data')

// 检测
emitter.setMaxListeners(20)   // 超出告警
emitter.listenerCount('data')
```

### 3. setInterval 不清

```typescript
// ❌
const t = setInterval(() => doStuff(largeObj), 1000)
// largeObj 被 closure 抓住直到 clearInterval

// ✅
const t = setInterval(...)
on('shutdown', () => clearInterval(t))

// Node-specific：让 timer 不阻止退出
t.unref()
```

### 4. 全局缓存无界

```typescript
// ❌
const cache = new Map()
function get(key) {
  if (!cache.has(key)) cache.set(key, fetch(key))
  return cache.get(key)
}
// 永不释放

// ✅ LRU + TTL
import { LRUCache } from 'lru-cache'
const cache = new LRUCache({ max: 1000, ttl: 60_000 })
```

### 5. 闭包持有 DOM（浏览器）

```javascript
// ❌
function setup() {
  const big = new ArrayBuffer(10 * 1024 * 1024)
  document.querySelector('#btn').addEventListener('click', () => {
    console.log(big.byteLength)   // big 永远跟随 button
  })
}
```

### 6. WeakRef / WeakMap 误用

`Map` 强引用，`WeakMap` 弱引用（key 是对象，可被 GC）。缓存类数据用 `WeakMap`：

```typescript
const meta = new WeakMap()
meta.set(user, { ... })   // user 被回收时，meta 自动清
```

## 五、Chrome DevTools Memory（前端 / Electron）

| 工具 | 用途 |
|---|---|
| **Heap Snapshot** | 时刻快照 + 三快照 diff |
| **Allocation instrumentation on timeline** | 实时分配火焰图 |
| **Allocation sampling** | 低开销采样（生产可用） |

诊断：
1. 录 timeline，正常使用 1 分钟
2. 看锯齿图：每个 GC 后底部应回到基线，不回 → 泄漏
3. 对象列表按 "Constructor" 分组，找异常累积的类型

## 六、Go pprof

```go
import _ "net/http/pprof"
import "net/http"

func init() {
    go http.ListenAndServe("localhost:6060", nil)
}
```

```bash
# 实时
go tool pprof http://localhost:6060/debug/pprof/heap
(pprof) top
(pprof) list <function>
(pprof) web              # SVG 火焰图

# 比较两个时刻
curl http://localhost:6060/debug/pprof/heap > heap1.prof
# ... 一段时间后
curl http://localhost:6060/debug/pprof/heap > heap2.prof
go tool pprof -base heap1.prof heap2.prof

# Goroutine 泄漏
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

**Go 常见泄漏**：
- Goroutine 泄漏：channel 阻塞 / context 没取消
- Slice 切片保留底层数组（小切片引用大底层 → copy 释放）
- Map 仅 delete key 不释放底层 bucket（重建 map 才彻底释放）
- runtime.SetFinalizer 用错

```go
// Goroutine 泄漏例
func leak() {
    ch := make(chan int)
    go func() { val := <-ch; use(val) }()    // 永远阻塞
    return                                     // ch 没人写
}
```

## 七、Python tracemalloc / objgraph

```python
import tracemalloc
tracemalloc.start()

# ... run code ...

snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)

# 比较两时刻
snap1 = tracemalloc.take_snapshot()
# ... ...
snap2 = tracemalloc.take_snapshot()
for stat in snap2.compare_to(snap1, 'lineno')[:10]:
    print(stat)
```

```python
# objgraph: 看对象引用图
import objgraph
objgraph.show_most_common_types()             # 各类型计数
objgraph.show_growth()                         # 自上次调用以来增长

# 找谁引用某对象
objgraph.show_backrefs(some_obj, max_depth=5, filename='backref.png')
```

**Python 常见泄漏**：
- 全局列表 / 字典累积
- 循环引用 + `__del__` 阻止 GC（用 `weakref`）
- C 扩展模块自管内存
- multiprocessing 子进程没回收

## 八、Java / JVM

```bash
# heap dump
jmap -dump:format=b,file=heap.hprof <pid>
# OOM 时自动 dump
java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heap.hprof ...

# 分析
- VisualVM (free)
- JProfiler / YourKit (commercial)
- Eclipse MAT (Memory Analyzer Tool) — 大堆首选
```

**MAT 关键功能**：
- "Leak Suspects" 报告
- "Dominator Tree" 看谁占最多
- "Path to GC Roots" 找引用链

**JVM 常见**：
- ThreadLocal 不 remove → 线程池常驻
- 静态 Map 缓存
- Listener / 回调注册不解绑
- ClassLoader 泄漏（hot reload 框架常见）

## 九、Rust（罕见但可能）

Rust 借用检查器防大多数泄漏，但仍可能：
- `Rc<RefCell<T>>` 循环引用 → 用 `Weak`
- `Box::leak` 显式调用
- 全局 `Mutex<HashMap>` 无 GC

工具：
- `valgrind --tool=memcheck` 检测 leaks（unsafe / FFI）
- `heaptrack`
- `dhat`（Rust 原生 heap profiler）

## 十、容器 OOMKilled 排查

```bash
# 看是否 OOM kill
kubectl describe pod <pod> | grep -A 5 "Last State"
# Reason: OOMKilled

# 容器日志
kubectl logs <pod> --previous

# Node 指标历史
kubectl top pod <pod> --containers
```

**对策**：
1. 调高 limit（短期）
2. 真泄漏 → heap snapshot 诊断
3. 工作集就是大 → 横向扩展
4. JVM / V8 → 显式设 max heap < container limit（避免 GC 不及时被 kill）

```yaml
# K8s
resources:
  requests: { memory: "512Mi" }
  limits:   { memory: "1Gi" }
env:
- name: NODE_OPTIONS
  value: "--max-old-space-size=768"      # < 1Gi 限制，留余量
```

JVM：

```
-Xmx768m
-XX:+UseContainerSupport               # JDK 11+ 自动识别 cgroup limit
```

## 十一、生产监控

```
指标（Prometheus）：
- process_resident_memory_bytes
- nodejs_heap_size_used_bytes
- jvm_memory_used_bytes{area="heap"}
- go_memstats_alloc_bytes
- go_memstats_heap_inuse_bytes

告警：
- 持续 1h 单调增长
- > 80% limit 持续 10 min
- GC 频率 / 暂停时间异常
- OOMKilled 事件
```

## 十二、防御性写法清单

- [ ] 缓存有界 + TTL（LRU）
- [ ] 监听器 add 必须 remove
- [ ] setInterval / setTimeout 必须 clear
- [ ] 长生命周期对象不持有短生命周期引用
- [ ] 关连接 / 关 stream / 关 cursor
- [ ] WeakMap 替代 Map 用于"附加属性"
- [ ] context cancellation（Go） / AbortController（JS）
- [ ] 启动跑一遍 sanity 测试看 baseline
- [ ] 集成 leak detection 测试（Node: `clinic` / `0x` / `leakage`）

## 十三、Don'ts

- ❌ 看到 RSS 高就以为泄漏（先看趋势）
- ❌ 仅靠 console.log 调试（用 heap snapshot）
- ❌ V8 默认 heap 1.5GB / 不显式设（生产建议显式 `--max-old-space-size`）
- ❌ 在生产打开高开销 profiler 一直跑（用采样模式 / 短期）
- ❌ 见 listener 多就 `removeAllListeners()` 暴力清（删别人的回调）
- ❌ 把内存增长归因 "GC 不及时" 不深查
- ❌ 不用 weakref / WeakMap，自己写"半弱引用"
- ❌ 日志里塞超大对象（容器 stdout buffer 持续增长）
- ❌ 生产环境跑 `--inspect` 暴露 Chrome DevTools 端口（安全风险）
- ❌ 没 OOMKilled 时不增加 memory limit，靠"重启脚本"

## 十四、调试 checklist

```
1. [ ] 复现：压测 / 长期运行能否复现
2. [ ] 量化：内存增长率（MB/min）
3. [ ] 隔离：bisect 找引入泄漏的 commit (git bisect)
4. [ ] 三快照：第一次和第二次 trigger 后对比
5. [ ] retainer 链：从泄漏对象回溯到 GC root
6. [ ] 修复 + 验证：压测看曲线
7. [ ] 回归测试：自动化检测（每次 PR 跑短期 stress）
```

## 十五、参考资料

- "Node.js Memory Leak Detection" 系列文章
- Chrome DevTools Memory：https://developer.chrome.com/docs/devtools/memory-problems/
- Go pprof：https://go.dev/blog/pprof
- "High Performance Browser Networking"（Ilya Grigorik）
- Eclipse MAT：https://www.eclipse.org/mat/
- "Java Performance" (Scott Oaks)
- clinic.js：https://clinicjs.org/
- objgraph：https://mg.pov.lt/objgraph/
- 各语言 GC 文档（V8 / G1 GC / CPython refcount + cycle collector）
