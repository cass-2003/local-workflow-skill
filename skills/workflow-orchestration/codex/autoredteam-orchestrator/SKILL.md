---
name: autoredteam-orchestrator
description: AutoRedTeam-Orchestrator 仓库开发专用。当用户提到 AutoRedTeam、MCP 工具开发、mcp_stdio_server、auto_recon、MCP 注册时使用。
disable-model-invocation: false
user-invocable: false
---

# AutoRedTeam-Orchestrator 仓库工作指南

## 角色定义

你在 AutoRedTeam-Orchestrator 仓库中工作。这是基于 MCP 的 AI 驱动自动化渗透测试框架，提供 100+ 纯 Python 安全工具，覆盖 OWASP Top 10，无外部依赖运行于 Windows/Linux/macOS。Python ≥ 3.10。

## 常用命令

```bash
pip install -r requirements.txt        # 安装依赖
python mcp_stdio_server.py             # 启动 MCP server
python auto_recon.py                   # 独立侦察引擎
python tests/test_v25_integration.py   # 集成测试
python tests/test_poc_engine.py        # PoC 引擎测试
```

## 架构速览

```
AI Editor (MCP Protocol)
        │
        ▼
mcp_stdio_server.py ────► Tool Modules
        │                      │
        ├── core/              ├── lateral/ (SMB/SSH/WMI)
        │   ├── session_manager.py
        │   ├── c2/ (Beacon/DNS隧道)
        │   ├── evasion/ (混淆免杀)
        │   ├── stealth/ (流量混淆/代理池)
        │   └── exploit/ (SQLi/端口扫描)
        │
        └── modules/
            ├── oob_detector.py
            ├── smart_payload_engine.py
            ├── vuln_verifier.py
            └── redteam_tools.py
```

## 关键文件

| 文件 | 职责 |
|------|------|
| `mcp_stdio_server.py` | MCP 入口，100+ 工具注册 |
| `auto_recon.py` | 独立自动侦察引擎 |
| `core/session_manager.py` | HTTP session（含认证） |
| `modules/redteam_tools.py` | Red Team MCP 工具整合层 |
| `utils/task_queue.py` | 异步任务队列（默认 3 workers） |

## 工具分类

- **Core**: auto_pentest / pentest_phase / generate_report / smart_analyze
- **Recon**: port_scan / dns_lookup / http_probe / tech_detect / full_recon
- **Vuln**: sqli_detect / xss_detect / ssrf_detect / xxe_detect / cmd_inject_detect
- **Red Team**: lateral_* / c2_* / evasion_* / stealth_*
- **Task Queue**: task_submit / task_status / task_cancel / task_list

完整列表以 `README.md` 为准。

## 新增 MCP 工具流程

1. 在 `modules/` 或 `core/` 实现函数（参考现有模块的输入校验、异常处理与返回格式）
2. 在 `mcp_stdio_server.py` 用 `@mcp.tool()` 装饰器注册
3. 本地 `python mcp_stdio_server.py` 或测试脚本验证

## MCP 配置

```json
{
  "mcpServers": {
    "redteam": {
      "command": "python",
      "args": ["/path/to/mcp_stdio_server.py"]
    }
  }
}
```

## 行为指令

1. **定位上下文**: 确认当前在 AutoRedTeam-Orchestrator 仓库根目录，检查 `mcp_stdio_server.py` 存在
2. **理解需求**: 分析任务属于哪类——新增工具 / 修 bug / 改架构 / 写测试 / 运行调试
3. **定位代码**: 根据任务类型定位到 `modules/`、`core/`、`mcp_stdio_server.py` 中的相关代码
4. **执行变更**: 按编码规范实现变更，确保跨平台兼容
5. **验证**: 运行相关测试脚本验证功能正确性

## 工具策略

| 任务 | 首选工具 | 备选工具 |
|------|----------|----------|
| 查找工具注册 | Grep `@mcp.tool` | Read `mcp_stdio_server.py` |
| 定位模块 | Glob `modules/**/*.py` | Bash `ls modules/` |
| 运行测试 | Bash `python tests/test_*.py` | Bash `pytest tests/` |
| 启动 MCP server | Bash `python mcp_stdio_server.py` | — |
| 依赖安装 | Bash `pip install -r requirements.txt` | Bash `pip install <pkg>` |
| 代码搜索 | Grep pattern | Read 具体文件 |
| 架构理解 | Read `README.md` | Glob + Read 多文件 |

## 决策树

```
AutoRedTeam 任务？
├── 新增 MCP 工具
│   ├── 纯 Python 实现？ → modules/ 新建文件
│   ├── 需要外部依赖？ → shutil.which() 检查 → requirements.txt 更新
│   ├── 注册工具 → mcp_stdio_server.py @mcp.tool()
│   └── 写测试 → tests/ 对应测试文件
├── 修复 Bug
│   ├── 定位异常 → Grep traceback 关键字
│   ├── 复现 → 运行对应测试
│   └── 修复 → 最小改动原则
├── 架构变更
│   ├── 影响范围 → Grep 调用链
│   ├── 涉及 session_manager → 注意认证状态一致性
│   └── 涉及 task_queue → 注意并发安全
├── 运行与调试
│   ├── 依赖缺失 → pip install -r requirements.txt
│   ├── 路径错误 → 检查跨平台兼容性
│   └── 编码问题 → 确认 encoding='utf-8'
└── 安全工具开发
    ├── OWASP 类工具 → 参考现有 vuln_*.py 模式
    ├── Red Team 工具 → 参考 lateral/c2/evasion 模块
    └── 侦察工具 → 参考 auto_recon.py 模式
```

## 输出格式

```markdown
### 任务：[任务描述]

**变更文件**:
- `path/to/file.py` — [变更说明]

**新增工具** (如适用):
- `tool_name` — [功能描述] | 注册于 `mcp_stdio_server.py` L[行号]

**测试结果**:
- [x] `test_*.py` — PASSED / FAILED
- [ ] 手动验证 — [验证步骤]

**注意事项**:
- [跨平台/安全/性能相关提醒]
```

## 编码规范（强制）

- **跨平台**: 必须可运行于 Windows/Linux/macOS
- **路径处理**: 禁止硬编码 `/tmp/`；用 `pathlib.Path` / `tempfile.gettempdir()`
- **编码**: 读写文件统一 `encoding='utf-8'`
- **外部工具**: 执行前 `shutil.which()` 检查可用性
- **语言**: 注释与文档简体中文为主

## 约束

- 所有工具必须纯 Python 实现，禁止依赖外部二进制（nmap、sqlmap 等）
- 新增工具必须包含输入校验和异常处理，返回结构化 dict
- 安全工具仅用于授权测试环境，工具内不硬编码目标地址
- 修改 `mcp_stdio_server.py` 注册后必须本地启动验证
- 不直接修改 `core/session_manager.py` 的认证逻辑，除非明确要求

