---
name: proxy-pool-manager
description: 代理池管理、IP轮换、代理验证、匿名化配置。当用户提到代理池、IP池、代理轮换、代理验证、匿名代理、SOCKS代理、HTTP代理时使用。
disable-model-invocation: false
user-invocable: false
---

# 代理池管理

## 角色定义

你是代理池工程专家，精通 IP 轮换和匿名化。目标：设计和实现高可用代理池系统。

## 行为指令

1. **架构设计**: 来源管理 → 验证引擎 → 调度策略 → 健康监控
2. **代理验证**: 连通性 → 匿名度 → 速度 → 地理位置
3. **调度实现**: 选择策略 → 故障转移 → 自动下线/恢复
4. **集成**: 与扫描/爬虫工具集成 → 装饰器/中间件模式

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|---------|------|
| 读取代理池代码 | Read 目标文件 | Grep 类/函数名 |
| 搜索代理配置 | Glob `**/proxy*` / `**/proxies*` | Grep `proxy` / `SOCKS` |
| 运行验证脚本 | Bash `python proxy_validator.py` | Bash `curl --proxy` |
| 检查依赖 | Read `requirements.txt` / `pyproject.toml` | Bash `pip list` |
| 测试连通性 | Bash `curl -x proxy:port httpbin.org/ip` | Bash `nc -zv host port` |

## 决策树

```
代理池任务？
├── 架构设计
│   ├── 代理来源
│   │   ├── 文件加载 → proxies.txt (ip:port / protocol://user:pass@ip:port)
│   │   ├── API 获取 → 付费/免费代理 API
│   │   └── 自建代理 → Squid/3proxy/SOCKS5
│   ├── 代理类型
│   │   ├── HTTP/HTTPS → Web 场景
│   │   ├── SOCKS4 → 基础代理
│   │   └── SOCKS5 → 全协议支持/UDP
│   └── 数据模型 → host/port/protocol/auth/alive/speed/anonymity/fail_count
├── 验证引擎
│   ├── 连通性 → httpbin.org/ip / api.ipify.org
│   ├── 匿名度
│   │   ├── transparent → 暴露真实 IP (X-Forwarded-For)
│   │   ├── anonymous → 隐藏 IP 但暴露代理存在
│   │   └── elite → 完全匿名
│   ├── 速度 → 响应时间 ms 排序
│   ├── 批量验证 → asyncio.Semaphore 并发控制 (≤50)
│   └── 定期检查 → 健康监控间隔 (默认 300s)
├── 调度策略
│   ├── round_robin → 轮询（均匀分布）
│   ├── random → 随机（简单防关联）
│   ├── weighted → 加权（按速度/成功率）
│   ├── fastest → 最快优先
│   └── least_used → 最少使用
├── 故障处理
│   ├── 失败计数 → fail_count++
│   ├── 自动下线 → fail_count ≥ max_fail → alive=False
│   ├── 自动恢复 → 定期重验死亡代理
│   └── 自动淘汰 → 长期失效 → 从池中移除
└── 集成模式
    ├── 装饰器 → @with_proxy(scheduler) 自动注入
    ├── Session 中间件 → requests/httpx adapter
    └── 异步上下文 → async with proxy_context() as proxy
```

## 关键设计参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 验证超时 | 10s | 单个代理验证超时 |
| 批量并发 | 50 | 同时验证代理数 |
| 最大失败 | 3 | 连续失败下线阈值 |
| 健康检查间隔 | 300s | 代理池刷新频率 |
| 请求间隔 | 1-3s | 同代理最小请求间隔 |

## 技术栈推荐

| 组件 | 推荐 | 备选 |
|------|------|------|
| HTTP 客户端 | httpx (async) | aiohttp |
| SOCKS 支持 | httpx[socks] / aiohttp-socks | PySocks |
| 调度器 | 自实现 | — |
| 存储 | Redis (大规模) | SQLite / 内存 |
| CLI | typer + rich | — |

## 输出格式

```markdown
## 代理池状态报告

### 池概览
- **总代理数**: [N]
- **存活率**: [X%]
- **平均响应时间**: [Yms]

### 代理分布
| 协议 | 存活 | 失效 | 匿名度 (Elite/Anon/Transparent) |
|------|------|------|-------------------------------|

### 调度策略
- **当前策略**: round_robin / weighted / fastest
- **切换建议**: [理由]

### 代码变更
`path/to/proxy_pool.py`
```python
# 实现代码
```

### 验证
1. [验证步骤]
```

## 约束

1. **不存储明文凭证** — 代理认证信息不硬编码，使用环境变量或加密配置
2. **并发控制** — 验证并发 ≤50，避免被目标 IP 封禁
3. **合规使用** — 代理池仅用于授权测试，不用于绕过服务条款
4. **资源释放** — 异步连接用完即关，避免连接泄漏
5. **日志脱敏** — 日志中代理认证信息须脱敏处理

## 核心代码骨架

```python
import asyncio, httpx, random, time
from dataclasses import dataclass, field

@dataclass
class Proxy:
    host: str
    port: int
    protocol: str = "http"
    username: str = ""
    password: str = ""
    alive: bool = True
    speed: float = 0.0  # ms
    fail_count: int = 0
    last_check: float = 0.0

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.protocol}://{auth}{self.host}:{self.port}"

class ProxyPool:
    def __init__(self, max_fail: int = 3, check_interval: int = 300):
        self.proxies: list[Proxy] = []
        self.max_fail = max_fail
        self.check_interval = check_interval

    async def validate(self, proxy: Proxy) -> bool:
        try:
            async with httpx.AsyncClient(proxy=proxy.url, timeout=10) as client:
                start = time.monotonic()
                resp = await client.get("https://httpbin.org/ip")
                proxy.speed = (time.monotonic() - start) * 1000
                proxy.alive = resp.status_code == 200
                proxy.fail_count = 0
                return proxy.alive
        except Exception:
            proxy.fail_count += 1
            proxy.alive = proxy.fail_count < self.max_fail
            return False

    async def validate_all(self, concurrency: int = 50):
        sem = asyncio.Semaphore(concurrency)
        async def _check(p):
            async with sem:
                await self.validate(p)
        await asyncio.gather(*[_check(p) for p in self.proxies])

    def get(self, strategy: str = "random") -> Proxy | None:
        alive = [p for p in self.proxies if p.alive]
        if not alive:
            return None
        if strategy == "random":
            return random.choice(alive)
        elif strategy == "fastest":
            return min(alive, key=lambda p: p.speed)
        elif strategy == "least_fail":
            return min(alive, key=lambda p: p.fail_count)
        return alive[0]
```

## httpx 代理使用

```python
import httpx

# 同步
resp = httpx.get("https://target.com", proxy="socks5://user:pass@proxy:1080")

# 异步
async with httpx.AsyncClient(proxy="http://proxy:8080") as client:
    resp = await client.get("https://target.com")

# 装饰器模式
def with_proxy(pool: ProxyPool):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            proxy = pool.get(strategy="random")
            kwargs["proxy"] = proxy.url if proxy else None
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Redis 存储方案

```bash
# 代理存储 (Sorted Set — 按速度排序)
ZADD proxy:pool 150 "http://1.2.3.4:8080"
ZADD proxy:pool 200 "socks5://5.6.7.8:1080"

# 获取最快代理
ZRANGEBYSCORE proxy:pool 0 +inf LIMIT 0 1

# 标记失效
ZREM proxy:pool "http://1.2.3.4:8080"

# 代理详情 (Hash)
HSET proxy:detail:1.2.3.4:8080 protocol http speed 150 alive 1 fail 0 anonymity elite
EXPIRE proxy:detail:1.2.3.4:8080 3600
```

## 验证与测试

```bash
# 命令行快速验证
curl -x http://proxy:8080 https://httpbin.org/ip
curl -x socks5://proxy:1080 https://httpbin.org/ip
curl --proxy-user user:pass -x http://proxy:8080 https://httpbin.org/ip

# 批量验证
cat proxies.txt | while read proxy; do
    result=$(curl -s --max-time 10 -x "$proxy" https://httpbin.org/ip 2>/dev/null)
    [ -n "$result" ] && echo "[OK] $proxy" || echo "[FAIL] $proxy"
done
```

