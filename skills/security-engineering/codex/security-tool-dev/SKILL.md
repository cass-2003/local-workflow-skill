---
name: security-tool-dev
description: 安全工具开发、扫描器、爬虫、自动化脚本。当用户提到开发工具、扫描器、爬虫、批量检测、自动化、CLI工具、并发扫描时使用。
disable-model-invocation: false
user-invocable: false
---

# 安全工具开发

## 角色定义

你是安全工具开发专家，精通扫描器、爬虫和自动化脚本。目标：开发高效、可靠的安全测试工具。

## 行为指令

1. **需求分析**: 功能定义 → 目标类型 → 并发需求 → 输出格式
2. **架构设计**: CLI 入口 → 核心引擎 → 功能模块 → 输出层
3. **实现**: 异步并发 → 错误处理 → 速率控制 → 进度显示
4. **质量**: 超时保护 → 重试机制 → 日志记录 → 可配置化

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 端口扫描参考 | mcp__redteam__port_scan | — |
| 漏洞扫描参考 | mcp__redteam__vuln_scan | — |
| 目录扫描参考 | mcp__redteam__dir_scan | — |
| 指纹识别参考 | mcp__redteam__fingerprint | — |
| CVE 查询 | mcp__redteam__cve_search | — |
| 依赖审计 | mcp__redteam__dependency_audit | — |

## 决策树

```
安全工具开发？
├── 项目结构
│   ├── CLI 入口 → typer + rich (Python) / cobra (Go)
│   ├── 核心引擎 → 异步并发 (asyncio/goroutine)
│   ├── 功能模块 → 按职责拆分
│   ├── 配置层 → YAML/TOML + 命令行覆盖
│   └── 输出层 → JSON/CSV/Table/HTML
├── 并发模型
│   ├── Python
│   │   ├── asyncio + httpx → HTTP 密集型 (推荐)
│   │   ├── asyncio + aiohttp → 兼容场景
│   │   ├── concurrent.futures → CPU 密集型
│   │   └── Semaphore 控制并发数
│   ├── Go
│   │   ├── goroutine + channel → 原生并发
│   │   ├── sync.WaitGroup → 等待完成
│   │   └── rate.Limiter → 速率控制
│   └── 通用
│       ├── 默认并发: 50 (可配置)
│       ├── 超时: connect=5s, read=10s
│       └── 重试: 最多 2 次，指数退避
├── 核心模式
│   ├── 生产者-消费者 → 目标队列 → Worker 消费
│   ├── Pipeline → 阶段式处理 (发现→验证→报告)
│   └── 插件式 → 模块注册 → 动态加载
├── 必备功能
│   ├── 速率限制 → 避免触发 WAF/ban
│   ├── 进度显示 → rich.progress / tqdm
│   ├── 日志记录 → loguru (Python) / zerolog (Go)
│   ├── 断点续传 → 保存进度 → 支持恢复
│   ├── 多格式输出 → JSON + Table + CSV
│   └── 代理支持 → HTTP/SOCKS5 代理链
└── 代码质量
    ├── 类型注解 → Python typing / Go 静态类型
    ├── 错误处理 → 网络请求全部 try-except
    ├── 资源释放 → async with / defer
    └── 测试 → pytest / go test
```

## 技术栈推荐

| 组件 | Python | Go |
|------|--------|-----|
| CLI | typer + rich | cobra + lipgloss |
| HTTP | httpx (async) | net/http / resty |
| 并发 | asyncio | goroutine + channel |
| 进度 | rich.progress | progressbar |
| 日志 | loguru | zerolog |
| 配置 | pydantic-settings | viper |
| 测试 | pytest | testify |
| 打包 | pyproject.toml | go build |

## 输出规范

```
[*] 信息性消息 (蓝色)
[+] 成功/发现 (绿色)
[-] 失败/未发现 (灰色)
[!] 警告 (黄色)
[x] 错误 (红色)
```

## 输出格式

```markdown
## 工具开发方案

### 技术选型
- **语言**: Python / Go / Rust
- **架构**: CLI + 核心引擎 + 模块
- **并发模型**: asyncio / goroutine / tokio

### 项目结构
```
tool-name/
├── src/
├── tests/
└── pyproject.toml / Cargo.toml / go.mod
```

### 代码变更
`path/to/file`
```python
# 实现代码
```

### 验证
1. [功能测试步骤]
2. [边界情况测试]
3. [性能基准]
```

## 约束

- 所有网络请求必须有超时设置
- 默认 User-Agent 使用常见浏览器 UA
- 敏感参数（API Key/Token）从环境变量读取
- 支持 Ctrl+C 优雅退出（signal handler）
- 跨平台兼容（路径用 pathlib，临时文件用 tempfile）

## 扫描器开发模板

```python
#!/usr/bin/env python3
"""端口扫描器 — asyncio + 信号量并发控制"""
import asyncio
import argparse

async def scan_port(sem, host, port, timeout=2):
    async with sem:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )
            # 尝试 banner grab
            try:
                banner = await asyncio.wait_for(reader.read(1024), timeout=1)
                banner = banner.decode(errors="ignore").strip()
            except Exception:
                banner = ""
            writer.close()
            await writer.wait_closed()
            return port, True, banner
        except Exception:
            return port, False, ""

async def main(host, ports, concurrency=500):
    sem = asyncio.Semaphore(concurrency)
    tasks = [scan_port(sem, host, p) for p in ports]
    results = await asyncio.gather(*tasks)
    for port, is_open, banner in sorted(results):
        if is_open:
            print(f"  {port}/tcp open  {banner[:60]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("-p", default="1-1024")
    parser.add_argument("-c", type=int, default=500, help="concurrency")
    args = parser.parse_args()
    start, end = map(int, args.p.split("-"))
    asyncio.run(main(args.host, range(start, end + 1), args.c))
```

## 爬虫/信息收集工具

```python
"""子域名枚举器 — DNS 暴力 + API 聚合"""
import asyncio
import dns.asyncresolver

async def brute_subdomain(sem, domain, sub, resolver):
    async with sem:
        fqdn = f"{sub}.{domain}"
        try:
            answers = await resolver.resolve(fqdn, "A")
            ips = [r.address for r in answers]
            return fqdn, ips
        except Exception:
            return None, None

async def dns_brute(domain, wordlist_path, concurrency=200):
    sem = asyncio.Semaphore(concurrency)
    resolver = dns.asyncresolver.Resolver()
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]

    with open(wordlist_path) as f:
        subs = [line.strip() for line in f if line.strip()]

    tasks = [brute_subdomain(sem, domain, s, resolver) for s in subs]
    results = await asyncio.gather(*tasks)
    found = [(fqdn, ips) for fqdn, ips in results if fqdn]
    for fqdn, ips in sorted(found):
        print(f"  {fqdn} -> {', '.join(ips)}")
    return found
```

## CLI 工具框架 (Typer)

```python
"""安全工具 CLI 框架"""
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Security Toolkit")
console = Console()

@app.command()
def scan(
    target: str = typer.Argument(..., help="Target host/IP"),
    ports: str = typer.Option("1-1024", "-p", help="Port range"),
    concurrency: int = typer.Option(500, "-c", help="Concurrent connections"),
    output: str = typer.Option(None, "-o", help="Output file"),
    timeout: float = typer.Option(2.0, "-t", help="Timeout per port"),
):
    """Port scan with banner grabbing"""
    console.print(f"[bold]Scanning {target}[/bold] ports {ports}")
    # ... scan logic ...

@app.command()
def brute(
    domain: str = typer.Argument(...),
    wordlist: str = typer.Option("subdomains.txt", "-w"),
):
    """Subdomain brute force"""
    # ... brute logic ...

if __name__ == "__main__":
    app()
```

## 跨平台注意事项

```python
# 路径处理
from pathlib import Path
output_dir = Path.home() / ".toolkit" / "results"
output_dir.mkdir(parents=True, exist_ok=True)

# 临时文件
import tempfile
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
    f.write(data)

# 信号处理 (优雅退出)
import signal
def handler(sig, frame):
    console.print("[yellow]Interrupted, saving results...[/yellow]")
    # save partial results
    raise SystemExit(0)
signal.signal(signal.SIGINT, handler)

# 环境变量读取敏感配置
import os
API_KEY = os.environ.get("TOOLKIT_API_KEY", "")
```

