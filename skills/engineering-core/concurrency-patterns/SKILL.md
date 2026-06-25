---
name: concurrency-patterns
description: "并发原语跨语言实战。覆盖 mutex/RWLock/atomic、channel/CSP（Go）、async/await（JS/Python/Rust）、goroutine vs thread vs fiber/coroutine、actor model（Erlang/Akka）、shared state vs message passing、Producer-Consumer、worker pool、fan-in fan-out、pipeline、context cancellation、race condition / deadlock / livelock、共享内存与原子操作、并发数据结构（concurrent map/sync.Map）、调试工具（race detector / TSan / asyncio debug）。当用户提到 并发、concurrency、goroutine、async await、mutex、锁、channel、CSP、actor、race condition、deadlock、worker pool、context cancellation、并行 时使用。"
---

# Concurrency Patterns Skill — 并发原语跨语言

## 何时使用

- 设计高并发服务（并行处理 / 流水线 / 扇出扇入）
- 排查 race condition / deadlock / 偶发崩溃
- 选择 mutex vs channel vs actor
- 实现 worker pool / 任务并行
- 跨语言移植并发代码

## 一、并发模型分类

| 模型 | 代表 | 哲学 |
|---|---|---|
| **共享内存 + 锁** | Java / C++ / Python threading | "用锁保护共享数据" |
| **CSP（消息传递）** | Go / Erlang | "Don't communicate by sharing memory; share memory by communicating" |
| **Actor** | Erlang / Akka / Elixir | "每个 actor 自封闭，邮箱接收消息" |
| **Async/Await** | JS / Python asyncio / Rust / C# | "单线程事件循环，IO 等待时让出" |
| **Software Transactional Memory** | Clojure / Haskell | "数据库事务般的内存原子块" |
| **Data Parallel** | OpenMP / CUDA | "同一操作并行作用于数据数组" |

不同语言混合使用。Go 主推 CSP 但也有 mutex；Rust 主推无锁但提供完整 sync 库。

## 二、关键概念区分

### 并发 vs 并行

```
并发（concurrency）：多个任务交替推进（可单核）
并行（parallelism）：多个任务同时执行（多核）
```

asyncio 是**并发**单线程；Go runtime / Java 线程池是**并行**多核。

### 进程 / 线程 / 协程

| | 切换成本 | 内存 | 隔离 |
|---|---|---|---|
| 进程 | 高（上下文 + TLB） | MB 级 | 完全 |
| 线程 | 中（寄存器） | KB-MB | 共享地址空间 |
| 协程 / fiber | 低（用户态） | KB 级 | 共享地址空间 |
| Goroutine | 极低 | 2KB 起 | 共享 |
| async task | 极低（栈复用） | 极小 | 共享 |

Goroutine = 用户态调度的轻量线程；async/await = 编译器变换的状态机。

## 三、Mutex（最基础）

```go
// Go
var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    defer mu.Unlock()
    counter++
}
```

```rust
// Rust
use std::sync::Mutex;
let counter = Mutex::new(0);
let mut guard = counter.lock().unwrap();
*guard += 1;
// guard 离开作用域自动释放（RAII）
```

```python
# Python
lock = threading.Lock()
with lock:
    counter += 1
```

```typescript
// JS 单线程，无 mutex；Web Worker 间用 SharedArrayBuffer + Atomics
const sab = new SharedArrayBuffer(4)
const view = new Int32Array(sab)
Atomics.add(view, 0, 1)
```

### RWLock（读多写少）

```go
var mu sync.RWMutex
mu.RLock(); ... mu.RUnlock()      // 多读
mu.Lock();  ... mu.Unlock()        // 独占写
```

读远多于写时显著快于普通 Mutex。

### Atomic

```go
import "sync/atomic"
var counter atomic.Int64
counter.Add(1)
counter.Load()
```

无锁，单变量级 / CPU 指令直接支持。比 mutex 快 5-10 倍。

## 四、Go 的 Channel（CSP）

```go
// 无缓冲 — 发送阻塞直到接收
ch := make(chan int)
go func() { ch <- 42 }()
val := <-ch

// 带缓冲
ch := make(chan int, 10)

// 关闭
close(ch)
for val := range ch { ... }   // 收到所有 + close

// select 多路
select {
case v := <-ch1: ...
case ch2 <- val: ...
case <-time.After(5*time.Second): // 超时
case <-ctx.Done():               // 取消
}
```

**Pipeline 模式**：

```go
func gen(n int) <-chan int {
    ch := make(chan int)
    go func() { defer close(ch); for i := 0; i < n; i++ { ch <- i } }()
    return ch
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() { defer close(out); for v := range in { out <- v * v } }()
    return out
}

// 使用
for v := range sq(sq(gen(10))) { fmt.Println(v) }
```

## 五、Worker Pool

```go
// Go
func workerPool(jobs <-chan Job, results chan<- Result, n int) {
    var wg sync.WaitGroup
    for i := 0; i < n; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    go func() { wg.Wait(); close(results) }()
}

jobs := make(chan Job, 100)
results := make(chan Result, 100)
go workerPool(jobs, results, 10)

for _, j := range allJobs { jobs <- j }
close(jobs)

for r := range results { use(r) }
```

```typescript
// Node.js
import pLimit from 'p-limit'
const limit = pLimit(10)        // 并发上限 10

const results = await Promise.all(
  items.map(item => limit(() => process(item)))
)
```

```python
# Python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(process, items))

# asyncio
import asyncio
sem = asyncio.Semaphore(10)
async def bound(item):
    async with sem:
        return await process(item)
results = await asyncio.gather(*(bound(i) for i in items))
```

## 六、Fan-out / Fan-in

```go
// Fan-out：1 input → N workers
func fanOut(in <-chan Job, n int) []<-chan Result {
    outs := make([]<-chan Result, n)
    for i := 0; i < n; i++ { outs[i] = worker(in) }
    return outs
}

// Fan-in：N outputs → 1 channel
func fanIn(channels ...<-chan Result) <-chan Result {
    out := make(chan Result)
    var wg sync.WaitGroup
    for _, c := range channels {
        wg.Add(1)
        go func(c <-chan Result) {
            defer wg.Done()
            for v := range c { out <- v }
        }(c)
    }
    go func() { wg.Wait(); close(out) }()
    return out
}
```

## 七、Context Cancellation

```go
// Go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()

req, _ := http.NewRequestWithContext(ctx, ...)
// ctx.Done() 在超时或显式 cancel 时关闭
// 所有遵守 context 的库（DB / HTTP / channel select）会停止
```

```typescript
// JS / Node 18+
const ctrl = new AbortController()
setTimeout(() => ctrl.abort(), 5000)

try {
  const r = await fetch(url, { signal: ctrl.signal })
} catch (e) {
  if (e.name === 'AbortError') { /* 取消 */ }
}
```

```python
# Python asyncio
async def with_timeout():
    try:
        await asyncio.wait_for(long_task(), timeout=5.0)
    except asyncio.TimeoutError: ...

# 显式取消
task = asyncio.create_task(work())
task.cancel()
```

**关键**：每个长操作都该接受 cancellation signal — 不让用户等 30s 没法退出。

## 八、Async/Await（JS / Python / Rust）

```typescript
// JS
async function fetchAll(urls: string[]) {
  // 串行
  const seq = []
  for (const u of urls) seq.push(await fetch(u))

  // 并行
  const par = await Promise.all(urls.map(u => fetch(u)))

  // 限并发
  const lim = pLimit(5)
  const bounded = await Promise.all(urls.map(u => lim(() => fetch(u))))

  // 任一完成
  const first = await Promise.race(urls.map(u => fetch(u)))

  // 全部 settle
  const settled = await Promise.allSettled(urls.map(u => fetch(u)))
}
```

```rust
// Rust
use tokio::join;
let (a, b) = join!(fetch_a(), fetch_b());

// JoinSet
let mut set = JoinSet::new();
for url in urls { set.spawn(fetch(url)); }
while let Some(r) = set.join_next().await { ... }
```

## 九、Race Condition（竞态）

```go
// ❌ Race
var counter int
for i := 0; i < 1000; i++ {
    go func() { counter++ }()
}

// 检测：go run -race / go test -race
// 修：mutex / atomic / channel
```

```python
# Python: 即使 GIL 也有竞态（i += 1 不是原子）
counter = 0
def increment():
    global counter
    counter += 1   # 在不同线程并发可能丢更新

# 修：lock 或 queue 或 multiprocessing
```

**Race detector**：
- Go：`-race` flag
- Rust：所有权 + Send/Sync 编译期防
- Java：CheckThread / Coverity / 工具检测
- C/C++：ThreadSanitizer (`-fsanitize=thread`)

## 十、Deadlock

```
线程 A: 持锁 1, 等锁 2
线程 B: 持锁 2, 等锁 1
→ 双方永远等
```

**避免**：
1. **固定加锁顺序**（按 ID 排序）
2. **try-lock + timeout**（拿不到回退）
3. **粗粒度锁**（少而大胜过多而小）
4. **避免锁内调用外部代码**（call back 可能再尝试加锁）

```go
// 死锁例
func transfer(from, to *Account, amount int) {
    from.mu.Lock()
    to.mu.Lock()      // ← 反向并发调用 → 死锁
    ...
}

// 修：固定顺序
func transfer(from, to *Account, amount int) {
    a, b := from, to
    if a.id > b.id { a, b = b, a }
    a.mu.Lock(); defer a.mu.Unlock()
    b.mu.Lock(); defer b.mu.Unlock()
    ...
}
```

## 十一、Actor Model

```erlang
% Erlang
loop(State) ->
    receive
        {get, Caller}    -> Caller ! State, loop(State);
        {set, NewState}  -> loop(NewState);
        stop             -> ok
    end.

Pid = spawn(fun() -> loop(0) end).
Pid ! {set, 42}.
```

```scala
// Akka
class Counter extends Actor {
  var n = 0
  def receive = {
    case Increment => n += 1
    case Get => sender() ! n
  }
}
```

**优点**：每 actor 单线程内部 → 无锁；横向扩展天然（actor 散布到多机）
**缺点**：心智重 / 调试难

## 十二、并发数据结构

```go
// Go: sync.Map（特定场景，多读多写）
var m sync.Map
m.Store("k", 1)
v, ok := m.Load("k")

// 或自家 mutex + map（90% 场景更好）
type Map struct { mu sync.RWMutex; m map[string]int }
```

```java
// Java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.compute("k", (k, v) -> v == null ? 1 : v + 1);

CopyOnWriteArrayList   // 读多写极少
ArrayBlockingQueue     // 生产-消费
```

```rust
// Rust
use dashmap::DashMap;
let map: DashMap<String, i32> = DashMap::new();

// 或 Arc<RwLock<HashMap>>
```

## 十三、调试工具

| 语言 | 工具 |
|---|---|
| Go | `go test -race` (内置 race detector) |
| Rust | 编译期 + `loom` 库做 unit test |
| Java | jstack（dump）/ CheckThread / VisualVM |
| C/C++ | ThreadSanitizer / Helgrind |
| Python | py-spy / threading.settrace |
| Node | `--inspect` + async_hooks / clinic |

```bash
# Go
go test -race ./...

# Rust loom
[dev-dependencies]
loom = "0.7"
# 运行：
LOOM_MAX_PREEMPTIONS=2 cargo test --test loom_tests --release
```

## 十四、并发安全清单

```
[ ] 共享数据明确所有权（"谁写"）
[ ] 写都加锁 / atomic / 走 channel
[ ] 长锁内不调外部代码 / IO
[ ] context / signal 接受 cancellation
[ ] timeout 防卡死
[ ] 限并发数（防资源耗尽）
[ ] 启动 race detector 跑测试
[ ] 关 channel 正确（接收方关闭会 panic）
[ ] 错误传播（goroutine 错误不能默默吞）
[ ] 优雅退出（worker 收到信号停止取新任务）
```

## 十五、Don'ts

- ❌ 共享数据不加锁就并发改 — race
- ❌ 锁粒度过细（每字段一锁）— deadlock 风险
- ❌ 加锁顺序不一致 — deadlock
- ❌ goroutine / async task fire-and-forget 不等不收错
- ❌ 用 `time.Sleep` 等并发完成 — 用 WaitGroup / channel
- ❌ 长 critical section（锁内做 IO）— 阻塞所有等待者
- ❌ 在 mutex 内 channel send — 可能死锁
- ❌ Goroutine 不带 context — 永远不知道何时该停
- ❌ Python multiprocessing 共享对象（pickle 失败）
- ❌ asyncio 中调用同步阻塞 IO — 整个事件循环卡住
- ❌ 拿到值不用就 `_, _ := ...` 忽略错误
- ❌ 用 sleep 调试并发问题 — 偶尔过偶尔不过，要用 race detector

## 十六、参考资料

- "The Go Programming Language" Ch.8-9（Donovan & Kernighan）
- "Concurrency in Go" (Katherine Cox-Buday)
- "Java Concurrency in Practice" (Brian Goetz)
- "Programming Erlang" (Joe Armstrong)
- "Rust Atomics and Locks" (Mara Bos) — 必读
- Go Memory Model：https://go.dev/ref/mem
- "The Reactive Manifesto"
- Akka docs：https://doc.akka.io/
- "Designing Data-Intensive Applications" Ch.7-9（一致性 + 共识）
- C++ memory ordering / std::atomic docs
