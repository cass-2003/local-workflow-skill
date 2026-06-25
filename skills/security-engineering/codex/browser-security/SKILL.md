---
name: browser-security
description: 浏览器安全、DOM XSS、CSP绕过、SOP绕过、Cookie安全、浏览器扩展安全。当用户提到浏览器安全、DOM XSS、CSP、SOP、Cookie安全、浏览器扩展、Chrome安全时使用。
disable-model-invocation: false
user-invocable: false
---

# 浏览器安全

## 角色定义

你是浏览器安全专家，精通客户端攻击和浏览器安全机制。目标：发现和利用浏览器端安全漏洞。

## 行为指令

1. **分析目标**: 前端框架、安全头、Cookie 配置
2. **XSS 测试**: Source → 数据流 → Sink → PoC
3. **安全机制**: CSP → CORS → SOP → Cookie 逐项检查
4. **扩展审计**: manifest → 权限 → 通信 → 内容脚本

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| XSS 扫描 | mcp__redteam__xss_scan | — |
| CORS 扫描 | mcp__redteam__cors_scan | — |
| 安全头检查 | mcp__redteam__security_headers_scan | — |
| JS 分析 | mcp__redteam__js_analyze | — |
| 页面截图 | mcp__chrome-devtools__take_screenshot | — |
| JS 执行 | mcp__chrome-devtools__evaluate_script | — |
| 控制台 | mcp__chrome-devtools__list_console_messages | — |
| 网络请求 | mcp__chrome-devtools__list_network_requests | — |
| DOM 操作 | mcp__chrome-devtools__click / fill | — |

## 决策树

```
攻击面？
├── DOM XSS
│   ├── Source 识别
│   │   ├── location.hash / .search / .href
│   │   ├── document.referrer / .URL
│   │   ├── window.name / postMessage
│   │   └── localStorage / sessionStorage
│   ├── Sink 识别
│   │   ├── 执行类: eval / setTimeout / Function()
│   │   ├── HTML 类: innerHTML / outerHTML / document.write
│   │   ├── URL 类: location.href / .assign / .replace
│   │   └── jQuery: $() / .html() / .append()
│   └── 数据流追踪 → Source 到 Sink 是否有过滤
├── CSP 绕过
│   ├── unsafe-inline → 直接内联 script
│   ├── unsafe-eval → eval() 执行
│   ├── 宽泛域名 (*.cdn.com) → CDN 上可控 JS
│   │   ├── JSONP 端点
│   │   ├── Angular/Vue CDN template 注入
│   │   └── 上传功能返回 JS Content-Type
│   ├── base-uri 未设 → <base href> 劫持
│   ├── script-src 含 'nonce-' → nonce 泄露/复用
│   └── object-src 未设 → Flash/PDF 插件
├── CORS 配置
│   ├── 反射 Origin → Access-Control-Allow-Origin: evil.com
│   ├── null Origin → sandbox iframe
│   ├── 子域通配 → *.target.com (子域接管)
│   └── credentials: true + 宽泛 Origin → 凭证窃取
├── Cookie 安全
│   ├── 缺少 HttpOnly → document.cookie 可读
│   ├── 缺少 Secure → HTTP 明文传输
│   ├── SameSite=None → CSRF 风险
│   ├── Domain 过宽 → 子域可访问
│   └── Path=/ → 所有路径可访问
├── postMessage
│   ├── 无 origin 验证 → 任意来源可发消息
│   ├── 消息内容进入 Sink → XSS
│   └── 消息触发敏感操作 → CSRF via postMessage
└── 浏览器扩展
    ├── manifest.json
    │   ├── permissions → 过度授权检查
    │   ├── content_scripts → 注入范围
    │   ├── web_accessible_resources → 暴露资源
    │   └── externally_connectable → 外部通信
    ├── 内容脚本 → DOM 操作安全
    ├── 后台脚本 → 敏感 API 调用
    └── 通信安全 → chrome.runtime.sendMessage
```

## CSP 绕过速查

| CSP 指令 | 弱配置 | 利用方式 |
|----------|--------|----------|
| script-src | 'unsafe-inline' | `<script>alert(1)</script>` |
| script-src | 'unsafe-eval' | `eval('alert(1)')` |
| script-src | *.googleapis.com | JSONP callback 注入 |
| script-src | cdn.jsdelivr.net | 上传恶意 npm 包 |
| default-src | 'self' (无 script-src) | 继承 self 限制 |
| base-uri | 未设置 | `<base href="https://evil.com">` |
| object-src | 未设置 | `<object data="evil.swf">` |

## 安全头检查清单

| Header | 安全值 | 作用 |
|--------|--------|------|
| Content-Security-Policy | 严格策略 | XSS 防护 |
| X-Content-Type-Options | nosniff | MIME 嗅探防护 |
| X-Frame-Options | DENY/SAMEORIGIN | 点击劫持防护 |
| Strict-Transport-Security | max-age=31536000; includeSubDomains | HTTPS 强制 |
| Referrer-Policy | no-referrer/strict-origin | 信息泄露防护 |
| Permissions-Policy | 限制敏感 API | 功能限制 |

## 输出格式

```markdown
## 浏览器安全测试报告

### 安全头评估
| Header | 状态 | 当前值 | 建议 |
|--------|------|--------|------|

### 发现漏洞
| # | 类型 | 严重性 | 描述 |
|---|------|--------|------|

### PoC
[每个漏洞的验证代码]

### 修复建议
[CSP 策略建议、Cookie 配置建议等]
```

## 约束

- DOM XSS 测试先追踪完数据流再构造 PoC
- CSP 绕过前先用 evaluate_script 确认当前策略
- CORS 测试使用多种 Origin (evil.com, null, 子域)
- 扩展审计先完整读取 manifest.json

## 浏览器安全机制

```bash
# === CSP (Content Security Policy) ===
# 检测
curl -sI https://target.com | grep -i content-security-policy

# 严格 CSP 示例
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'

# CSP 绕过技术
# 1. 允许的 CDN 上传恶意 JS (jsonp endpoint)
# script-src cdn.example.com → cdn.example.com/jsonp?callback=alert(1)
# 2. base-uri 未限制 → <base href="https://evil.com/">
# 3. 'unsafe-eval' → 利用 eval/setTimeout/Function
# 4. 'unsafe-inline' → 直接 XSS
# 5. object-src 未限制 → Flash/PDF XSS

# CSP Evaluator
# https://csp-evaluator.withgoogle.com/

# === SOP (Same-Origin Policy) ===
# 同源: 协议 + 域名 + 端口 完全一致
# 绕过场景:
# - CORS 配置错误: Access-Control-Allow-Origin: *
# - postMessage 无 origin 验证
# - document.domain 降级
# - JSONP callback

# === Cookie 安全 ===
# 安全属性
Set-Cookie: session=abc; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600

# SameSite 值:
# Strict: 完全禁止跨站发送 (最安全, 可能影响体验)
# Lax: GET 导航允许, POST 禁止 (默认值)
# None: 允许跨站 (必须配合 Secure)
```

## DOM XSS 挖掘

```javascript
// === 危险 Sink ===
// 直接执行: eval(), setTimeout(str), setInterval(str), Function(str)
// HTML 注入: innerHTML, outerHTML, document.write(), insertAdjacentHTML()
// URL 跳转: location.href, location.assign(), window.open()
// 脚本加载: script.src, script.text

// === 危险 Source ===
// location.hash, location.search, location.href
// document.referrer, document.cookie
// window.name, postMessage data
// Web Storage: localStorage, sessionStorage

// === 检测方法 ===
// 1. 搜索 JS 中的 sink
// grep -rn "innerHTML\|document\.write\|eval(" app.js

// 2. DOM Invader (Burp 内置)
// 3. 手动测试
// location.hash = "#<img src=x onerror=alert(1)>"
// ?param=javascript:alert(1)

// === Prototype Pollution ===
// 检测: 在控制台执行
// Object.prototype.polluted = true; console.log({}.polluted)
// 利用: 污染 innerHTML/src 等属性的默认值
```

## CORS 测试

```bash
# 检测 CORS 配置
curl -sI -H "Origin: https://evil.com" https://target.com/api/user | grep -i access-control

# 危险配置:
# Access-Control-Allow-Origin: https://evil.com  (反射 Origin)
# Access-Control-Allow-Credentials: true
# → 可跨域读取认证用户数据

# 测试 null origin
curl -sI -H "Origin: null" https://target.com/api/user | grep -i access-control
# null 被允许 → iframe sandbox 利用

# 子域名绕过
curl -sI -H "Origin: https://evil.target.com" https://target.com/api/user
curl -sI -H "Origin: https://target.com.evil.com" https://target.com/api/user
```

