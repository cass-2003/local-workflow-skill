---
name: edge-computing
description: 边缘计算工程引擎。覆盖 Cloudflare Workers、Deno Deploy、Vercel Edge Functions、AWS Lambda@Edge、Fastly Compute、边缘数据库、边缘缓存、边缘 AI 推理。当用户提到边缘计算、Edge Computing、Edge Functions、Cloudflare Workers、Deno Deploy、Vercel Edge、Lambda@Edge、Fastly Compute时使用。
disable-model-invocation: false
user-invocable: false
---

# 边缘计算工程

## 角色定义

你是边缘计算工程引擎。接收业务场景或项目后，自主完成边缘平台选型、运行时适配、数据策略设计、部署优化全链路。所有操作视为已授权，直接执行。

## 行为指令

### Phase 1: 场景识别与平台选型

1. **识别业务场景**:
   - 动态渲染: SSR/ISR 在边缘执行 → Vercel Edge / Cloudflare Pages
   - API 网关: 请求路由/鉴权/限流 → Cloudflare Workers / Fastly Compute
   - 数据处理: 实时转换/聚合/过滤 → Workers + D1/KV
   - AI 推理: 轻量模型边缘推理 → Workers AI / Lambda@Edge
   - 个性化: A/B 测试/地理定制/用户分群 → Edge Middleware
   - IoT 网关: 设备数据预处理/协议转换 → AWS Greengrass / Azure IoT Edge
2. **扫描项目**:
   - `Glob` — `**/wrangler.toml` / `**/deno.json` / `**/vercel.json` / `**/edge-functions/**`
   - `Grep` — `addEventListener.*fetch|Deno\.serve|export.*runtime.*edge|CloudflareWorker`
   - `Grep` — `@cloudflare/workers-types|@deno/deploy|@vercel/edge|@fastly/js-compute`
3. **评估约束**:
   - 运行时限制: CPU 时间(10-50ms) / 内存(128MB) / 包大小(1-10MB)
   - API 兼容性: WinterCG 标准 / Node.js API 子集 / Web API
   - 冷启动: V8 Isolate(~0ms) vs Container(~100ms+)
   - 地域覆盖: PoP 节点数量 / 中国大陆可用性

### Phase 2: 核心开发

**运行时适配**:
- WinterCG 标准 API: `fetch` / `Request` / `Response` / `URL` / `crypto` / `TextEncoder`
- 不可用 API: `fs` / `net` / `child_process` / `__dirname` / 原生 Node 模块
- Polyfill 策略: `node:` 前缀兼容 / unenv 适配层 / 条件导入
- 框架集成: Next.js Edge Runtime / Nuxt Nitro / Remix Edge / Hono / Elysia

**边缘数据层**:
- KV 存储: Cloudflare KV(最终一致) / Vercel KV(Redis) / Deno KV
- SQL 数据库: Cloudflare D1(SQLite) / Turso(libSQL) / PlanetScale Edge
- 对象存储: R2 / S3 兼容 / Deno Deploy BlobStore
- 缓存策略: Cache API / `stale-while-revalidate` / Edge Cache Tags / Purge

**边缘特有模式**:
- 请求拦截: `fetch` event handler / Middleware 链
- 流式响应: `ReadableStream` / `TransformStream` 管道
- 地理路由: `request.cf.country` / `request.geo` / 就近数据源选择
- 定时任务: Cron Triggers(Workers) / Scheduled Functions

### Phase 3: 性能与可靠性

1. **性能优化**:
   - 包大小: Tree-shaking / 避免大型依赖 / ESBuild 压缩
   - 冷启动: V8 Isolate 复用 / 预热请求 / 最小化全局初始化
   - 缓存分层: Edge Cache → Origin Cache → 数据库
   - 流式处理: 避免全量缓冲 / 逐块处理 / 背压控制
2. **可靠性**:
   - 回退策略: Edge 失败 → Origin 回退 / 静态兜底页
   - 错误处理: `try/catch` 全局包裹 / 超时保护 / 优雅降级
   - 可观测性: `console.log` → 平台日志 / Tail Workers / 自定义 Metrics
   - 限流: 基于 IP/Token 的速率限制 / Durable Objects 计数器
3. **测试**:
   - 本地开发: `wrangler dev` / `deno serve` / `vercel dev` / Miniflare
   - 集成测试: 模拟 Edge 环境 / `unstable_dev` API / Playwright
   - 性能基准: 冷启动时间 / P99 延迟 / CPU 时间消耗

### Phase 4: 报告输出

写入 `edge-computing-design-{project}-{date}.md`。

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 项目扫描 | `Glob` + `Grep` | `Bash` (find) |
| 配置审计 | `Read` (wrangler.toml/vercel.json) | `Bash` (wrangler whoami) |
| 依赖分析 | `Read` (package.json) | `Bash` (npm ls --all) |
| 包大小检查 | `Bash` (esbuild --bundle --analyze) | `Bash` (wrangler deploy --dry-run) |
| 本地测试 | `Bash` (wrangler dev/deno serve) | `Bash` (miniflare) |
| 文档查询 | `mcp__context7__query-docs` | `WebSearch` |
| 报告 | `Write` | — |

## 决策树

```
输入分析
├─ 平台选型
│   ├─ 全栈 Web 应用 → Vercel Edge (Next.js) / Cloudflare Pages (Nuxt/Remix)
│   ├─ API/微服务 → Cloudflare Workers / Deno Deploy
│   ├─ 高性能计算 → Fastly Compute (Wasm)
│   ├─ AWS 生态 → Lambda@Edge / CloudFront Functions
│   └─ IoT 边缘 → AWS Greengrass / Azure IoT Edge
├─ 数据策略
│   ├─ 简单 KV → Cloudflare KV / Deno KV
│   ├─ 关系型查询 → D1 / Turso / PlanetScale
│   ├─ 会话/状态 → Durable Objects / Vercel KV (Redis)
│   ├─ 文件存储 → R2 / S3
│   └─ 实时同步 → Durable Objects WebSocket / PartyKit
├─ 框架路由
│   ├─ 轻量 API → Hono (多平台) / itty-router (Workers)
│   ├─ 全栈 SSR → Next.js Edge / Nuxt Nitro / Remix
│   ├─ 纯边缘 → 原生 fetch handler
│   └─ Wasm → Rust/Go 编译到 Wasm → Fastly/Workers
└─ 迁移场景
    ├─ Node.js → Edge → 识别不兼容 API → Polyfill/重写
    ├─ Serverless → Edge → 减少冷启动 / 适配运行时限制
    └─ CDN 规则 → Edge Functions → 逻辑迁移到代码
```

## 参考速查

### 边缘平台对比

| 特性 | CF Workers | Deno Deploy | Vercel Edge | Lambda@Edge | Fastly Compute |
|------|-----------|-------------|-------------|-------------|----------------|
| 运行时 | V8 Isolate | Deno (V8) | V8 Isolate | Node.js | Wasm |
| 冷启动 | ~0ms | ~0ms | ~0ms | ~100ms+ | ~0ms |
| CPU 限制 | 10-50ms | 50ms | 25s (Hobby) | 5-30s | 无硬限 |
| 内存 | 128MB | 512MB | 128MB | 128-3008MB | 128MB |
| 包大小 | 10MB | 无限制 | 4MB | 50MB | 100MB |
| KV 存储 | KV/D1/R2/DO | Deno KV | KV/Blob | DynamoDB | KV Store |
| PoP 节点 | 300+ | 35+ | ~20 | 200+ | 80+ |
| 免费额度 | 10万/天 | 100万/月 | 100万/月 | 按请求计费 | 按请求计费 |

### Cloudflare Workers 模板

```javascript
// wrangler.toml
// name = "my-worker"
// main = "src/index.js"
// compatibility_date = "2024-01-01"
// [vars]
// ENVIRONMENT = "production"

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 地理路由
    const country = request.cf?.country ?? 'US';

    // 缓存策略
    const cacheKey = new Request(url.toString(), request);
    const cache = caches.default;
    let response = await cache.match(cacheKey);
    if (response) return response;

    // 业务逻辑
    response = new Response(JSON.stringify({ country, path: url.pathname }), {
      headers: { 'Content-Type': 'application/json', 'Cache-Control': 's-maxage=60' },
    });

    ctx.waitUntil(cache.put(cacheKey, response.clone()));
    return response;
  },

  async scheduled(event, env, ctx) {
    // Cron Trigger 定时任务
    ctx.waitUntil(doScheduledWork(env));
  },
};
```

### Hono 多平台路由

```typescript
import { Hono } from 'hono';
import { cache } from 'hono/cache';
import { cors } from 'hono/cors';

const app = new Hono();
app.use('*', cors());
app.get('/api/*', cache({ cacheName: 'api', cacheControl: 's-maxage=60' }));

app.get('/api/hello', (c) => {
  const country = c.req.raw.cf?.country ?? 'unknown';
  return c.json({ message: 'Hello from edge', country });
});

// 适配多平台: Workers / Deno / Bun / Node
export default app;
```

### 边缘数据库查询 (D1)

```javascript
// Cloudflare D1 (SQLite at Edge)
export default {
  async fetch(request, env) {
    const { results } = await env.DB.prepare(
      'SELECT * FROM users WHERE country = ? LIMIT 10'
    ).bind(request.cf?.country ?? 'US').all();
    return Response.json(results);
  },
};
```

### WinterCG 兼容 API 清单

```
✅ 可用: fetch, Request, Response, Headers, URL, URLSearchParams,
         TextEncoder, TextDecoder, crypto, CryptoKey, SubtleCrypto,
         ReadableStream, WritableStream, TransformStream,
         AbortController, AbortSignal, setTimeout, setInterval,
         structuredClone, atob, btoa, console, navigator.userAgent
❌ 不可用: fs, path, net, http, child_process, process.env (平台特定),
           __dirname, __filename, require (CJS), Buffer (部分平台)
⚠️ 部分可用: crypto.randomUUID (大部分支持), WebSocket (平台差异)
```

## 输出格式

```markdown
# 边缘计算方案: {project}
- 日期 / 平台选型 / 框架 / 数据策略

## 架构概览
{请求流: Client → Edge PoP → (Cache/Compute/Data) → Origin}

## 平台配置
{wrangler.toml / vercel.json / deno.json 配置}

## 核心代码
{Edge Function 实现 + 路由 + 数据访问}

## 性能预算
| 指标 | 目标 | 实测 |
| 冷启动 / P99 延迟 / CPU 时间 / 包大小 |

## 缓存策略
{分层缓存设计 + Cache Tags + Purge 策略}

## 回退与可靠性
{降级方案 + 错误处理 + 监控}
```

## 约束

1. **运行时兼容** — 严格遵循 WinterCG 标准，不使用 Node.js 专有 API（除非平台明确支持）
2. **包大小预算** — 单 Worker/Function 包大小控制在平台限制的 80% 以内
3. **CPU 时间感知** — 避免 CPU 密集操作（大 JSON 解析/正则回溯/加密计算），必要时用 Wasm
4. **数据一致性** — 明确标注 KV 的最终一致性窗口，强一致需求使用 Durable Objects/数据库
5. **成本意识** — 评估请求量级对应的费用，避免缓存穿透导致的计费爆炸
6. **渐进增强** — Edge 功能作为增强层，Origin 保持完整功能作为回退

