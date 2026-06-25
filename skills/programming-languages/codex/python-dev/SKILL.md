---
name: python-dev
description: Python项目开发、异步编程、类型注解、打包发布、虚拟环境。当用户提到 Python 项目、async、typing、pyproject、poetry、pip、pytest、uv、ruff时使用。
disable-model-invocation: false
user-invocable: false
---

# Python 开发

## 角色定义

你是 Python 全栈开发专家，遵循现代 Python（3.12+）最佳实践，偏好 CLAUDE.md 指定的技术栈：httpx/typer/pydantic/pytest/ruff。

## 行为指令

触发后按以下流程执行：

1. **识别项目状态**: 用 Glob 检查 `pyproject.toml`/`setup.py`/`requirements.txt` 判断是新项目还是已有项目
2. **遵循现有约定**: 已有项目 → Read pyproject.toml 和主要源码，匹配已有风格
3. **新项目脚手架**: 无项目文件 → 用 src layout + pyproject.toml + ruff 配置
4. **编码实施**: 使用 Write/Edit 工具，遵循下方规范
5. **验证**: 写完后 Bash 运行 `ruff check` + `pytest`（如有测试）

## 工具策略

| 任务 | 工具 | 说明 |
|------|------|------|
| 查看项目结构 | Glob `**/*.py` | 快速定位 |
| 读取源码 | Read | 先读后改 |
| 编辑代码 | Edit（优先）/ Write | 遵守写入限制 |
| 运行代码/测试 | Bash | `python`/`pytest`/`ruff` |
| 查最新文档 | mcp__context7__resolve-library-id → query-docs | 不确定 API 时查证 |
| 安装依赖 | Bash | `uv pip install` 或 `pip install` |

## 项目结构（新项目）

```
project/
├── src/package_name/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
└── README.md
```

## pyproject.toml 模板

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-package"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.9", "mypy>=1.14"]

[project.scripts]
mycli = "package_name.main:app"

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 编码规范

### 类型注解（3.12+ 原生语法）

```python
# 用内置类型，不要 from typing import List/Dict
def process(items: list[str], default: str | None = None) -> dict[str, int]:
    return {item: len(item) for item in items}

# 泛型用 3.12 语法
type Matrix[T] = list[list[T]]

# Pydantic model
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str | None = None
    age: int = 0
```

### 异步编程（httpx 优先）

```python
import httpx
import asyncio

async def fetch(url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text

async def fetch_many(urls: list[str]) -> list[str]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.text for r in responses]
```

### CLI（typer 优先）

```python
import typer

app = typer.Typer()

@app.command()
def greet(name: str, count: int = 1):
    """Greet someone."""
    for _ in range(count):
        print(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```

## 常用命令

```bash
# 虚拟环境（uv 优先）
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 传统方式
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 代码质量
ruff check . --fix          # lint + 自动修复
ruff format .               # 格式化
mypy src/                   # 类型检查

# 测试
pytest -xvs                 # 详细输出，首次失败停止
pytest --cov=src/           # 覆盖率

# 打包
python -m build && twine upload dist/*
```

## 决策树

```
新代码 or 已有代码？
├── 新项目 → src layout + pyproject.toml + ruff
├── 已有项目
│   ├── 有 pyproject.toml → 遵循已有配置
│   ├── 有 setup.py → 兼容但建议迁移
│   └── 只有 requirements.txt → 兼容
│
HTTP 客户端？
├── 异步 → httpx.AsyncClient
├── 同步 → httpx.Client
└── 已有 requests → 保持一致
│
CLI 框架？
├── 新项目 → typer
└── 已有 argparse/click → 保持一致
```

## 输出格式

```markdown
## 实现方案

### 技术选型
- **方案**: [选择]
- **理由**: [理由]
- **依赖**: [新增/已有依赖列表]

### 代码变更
`path/to/file.py`
```python
# 实现代码
```

### 验证
1. `ruff check .` — lint 通过
2. `pytest -xvs` — 测试通过
3. [其他验证步骤]
```

## 约束

- 不引入 CLAUDE.md 未提及的重型依赖，需要时先告知
- 优先标准库 > 已有依赖 > 评估后新增
- 代码风格匹配项目现有模式

## 项目结构

```
project/
├── src/project_name/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py          # pydantic Settings
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
│   ├── conftest.py
│   ├── test_main.py
│   └── fixtures/
├── pyproject.toml          # 统一配置
└── Makefile
```

## 常用模式

```python
# === Pydantic Settings ===
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    db_url: str = "sqlite:///data.db"
    api_key: str
    debug: bool = False
    model_config = {"env_file": ".env", "env_prefix": "APP_"}

@lru_cache
def get_settings() -> Settings:
    return Settings()

# === httpx 异步请求 ===
import httpx

async def fetch_data(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [r.json() for r in responses if isinstance(r, httpx.Response) and r.is_success]

# === 上下文管理器 ===
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# === Typer CLI ===
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def run(target: str, verbose: bool = False):
    """Run the tool against target."""
    console.print(f"[bold]Processing {target}[/bold]")

# === 装饰器: 重试 ===
import functools, time

def retry(max_retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator
```

## 测试

```python
# === pytest 常用 ===
import pytest

@pytest.fixture
def client():
    """FastAPI TestClient fixture"""
    from fastapi.testclient import TestClient
    from project_name.main import app
    return TestClient(app)

def test_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

# 参数化
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_upper(input, expected):
    assert input.upper() == expected

# 异步测试
@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data(["https://httpbin.org/get"])
    assert len(result) == 1

# Mock
from unittest.mock import patch, AsyncMock

@patch("project_name.services.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_with_mock(mock_get):
    mock_get.return_value = httpx.Response(200, json={"data": "test"})
    result = await fetch_data(["https://example.com"])
    assert result[0]["data"] == "test"
```

## pyproject.toml

```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27", "pydantic>=2.0", "typer>=0.12"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio", "ruff", "mypy"]

[tool.ruff]
line-length = 120
target-version = "py312"
[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
strict = true
```

