---
name: http-caching
description: "HTTP 缓存全栈实战。覆盖 Cache-Control 指令完整语义、ETag/Last-Modified 协商、Vary 头、private/public/shared cache、stale-while-revalidate、CDN 行为（Cloudflare/Fastly/CloudFront）、proxy/reverse proxy（nginx/varnish）、浏览器缓存、Service Worker 缓存、API 缓存策略、缓存击穿/穿透/雪崩防护。当用户提到 HTTP 缓存、Cache-Control、ETag、CDN 缓存、Vary、stale-while-revalidate、缓存策略、cache miss、cache invalidation、s-maxage 时使用。"
---

# HTTP Caching Skill — 全栈缓存实战

## 何时使用

- 设计 API / 静态资源缓存策略
- 排查"为什么 CDN 没命中" / "为什么改了内容浏览器还显示旧版"
- 优化 TTFB / Core Web Vitals 中 LCP
- 评审静态资源构建产物的 cache header
- 实现 cache invalidation（部署后旧缓存失效）

## 一、缓存层级（从近到远）

```
[ Browser Memory Cache ]    ← 最快，关闭 tab 丢失
        ↓
[ Browser Disk Cache ]      ← 持久，跨会话
        ↓
[ Service Worker Cache ]    ← 可编程，离线能力
        ↓
[ ISP / Corporate Proxy ]   ← 共享缓存
        ↓
[ CDN Edge ]                ← 全球分发，TTL 可控
        ↓
[ Reverse Proxy (nginx) ]   ← 应用前端
        ↓
[ Application Memory ]      ← 进程内 LRU
        ↓
[ Distributed Cache (Redis) ]  ← 跨实例共享
        ↓
[ Database ]                ← 持久层
```

**每一层都受 HTTP header 控制**（除 app 内存 / Redis 是程序自管）。

## 二、Cache-Control 指令完全清单

```
Cache-Control: public, max-age=3600, s-maxage=86400, stale-while-revalidate=600, must-revalidate
```

| 指令 | 含义 |
|---|---|
| `public` | 任何缓存（包括 CDN / proxy）都可存 |
| `private` | 仅浏览器可存（不可 CDN） |
| `no-cache` | 可存但每次必须先验证（条件请求） |
| `no-store` | **绝对**不存 — 用于敏感数据 |
| `max-age=N` | 浏览器缓存 N 秒 |
| `s-maxage=N` | CDN / shared cache 缓存 N 秒（覆盖 max-age） |
| `must-revalidate` | 过期后必须验证，不可用 stale |
| `proxy-revalidate` | 同上但仅对 shared cache |
| `immutable` | 客户端不要做条件请求（带 hash 文件名时用） |
| `stale-while-revalidate=N` | 过期后 N 秒内可返回 stale，后台异步更新 |
| `stale-if-error=N` | 上游错误时可返回 stale N 秒 |

## 三、四种典型策略

### 1. 不可变文件（带 hash 文件名）

```
Cache-Control: public, max-age=31536000, immutable
```

`bundle.a1b2c3.js` — 1 年缓存，永不验证。文件变了 hash 也变了，URL 变了浏览器自然取新。

### 2. HTML 入口

```
Cache-Control: no-cache
```

每次必须验证。配合 ETag 实现 "未变 304"，变了拉新版（带新 hash 的 bundle 引用）。

### 3. API 响应（频繁更新）

```
Cache-Control: private, max-age=0, must-revalidate
```

或者用 ETag 节省带宽：

```
Cache-Control: private, max-age=60
ETag: "W/abc123"
```

### 4. CDN 强缓存 + SWR

```
Cache-Control: public, max-age=60, s-maxage=86400, stale-while-revalidate=600
```

- 浏览器：60s 内不发请求
- CDN：1 天内直接返回；过期后再 10 分钟可返 stale 同时后台更新
- 实际命中率极高，源站压力极低

## 四、ETag / Last-Modified 协商缓存

服务端响应：

```
HTTP/1.1 200 OK
ETag: "v3-abc123"
Last-Modified: Wed, 06 May 2026 06:00:00 GMT
```

下次浏览器带条件头：

```
GET /api/users
If-None-Match: "v3-abc123"
If-Modified-Since: Wed, 06 May 2026 06:00:00 GMT
```

服务端比对未变：

```
HTTP/1.1 304 Not Modified
ETag: "v3-abc123"
```

返回 304 时无 body，节省带宽。

**ETag 类型**：
- **Strong**: `"abc123"` — 字节级一致才匹配
- **Weak**: `W/"abc123"` — 语义一致即可（如同一资源压缩 vs 未压缩）

实现：MD5/SHA 内容、版本号、updated_at 时间戳都行。**关键是稳定**（相同内容必须给相同 ETag）。

## 五、Vary 头（缓存按维度区分）

```
Cache-Control: public, max-age=3600
Vary: Accept-Encoding, Accept-Language
```

CDN 会按 `Accept-Encoding` (gzip/br) 和 `Accept-Language` (zh/en/ja) 分别缓存不同版本。

**陷阱**：`Vary: User-Agent` 几乎让缓存失效（每个 UA 都不同）。**避免**用 User-Agent。

如果用 cookie 区分用户：**不要用 `Vary: Cookie`** — 命中率太低。改用：
1. 路径区分（`/api/users/123/profile` 而非 `/api/me`）
2. 或者整体 `Cache-Control: private`

## 六、CDN 行为差异

| CDN | s-maxage 默认 | Vary 处理 | Purge API |
|---|---|---|---|
| **Cloudflare** | 仅当 `Cache-Control: public` 才缓存（除非 Page Rule） | 支持 | API + UI（按 URL / tag / 全清） |
| **Fastly** | VCL 自定义 | 支持 | Surrogate-Key 标签缓存（强大） |
| **CloudFront** | 受 cache policy 控制 | 支持但要白名单 | Invalidation（每月配额） |
| **Vercel** / Netlify | 边缘函数自动判断 | 部分 | 部署即清 |

**Surrogate-Control** 头给 CDN 专用，浏览器忽略：

```
Cache-Control: public, max-age=60        ← 浏览器
Surrogate-Control: max-age=86400          ← CDN
```

或 Cloudflare 用 `Cache-Tag` / Fastly 用 `Surrogate-Key`：

```
Surrogate-Key: user-123 product-456
```

部署后只 purge 含 `user-123` tag 的所有缓存，无需 URL 列表。

## 七、Service Worker 缓存策略

```javascript
// Cache First（资源）
self.addEventListener('fetch', e => {
  if (e.request.url.match(/\.(js|css|png)$/)) {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
        const clone = resp.clone()
        caches.open('assets-v1').then(c => c.put(e.request, clone))
        return resp
      }))
    )
  }
})

// Network First（API）
async function networkFirst(req) {
  try {
    const resp = await fetch(req)
    const cache = await caches.open('api-v1')
    cache.put(req, resp.clone())
    return resp
  } catch {
    return caches.match(req)
  }
}

// Stale-While-Revalidate
async function swr(req) {
  const cache = await caches.open('swr-v1')
  const cached = await cache.match(req)
  const networkPromise = fetch(req).then(resp => { cache.put(req, resp.clone()); return resp })
  return cached ?? networkPromise
}
```

用 Workbox 库简化：`workbox-routing` + `workbox-strategies`。

## 八、API 缓存策略矩阵

| 数据特征 | 推荐策略 |
|---|---|
| **公共，更新慢**（产品列表） | `public, max-age=60, s-maxage=600, stale-while-revalidate=300` |
| **私有，频繁查**（用户 profile） | `private, max-age=60` + ETag |
| **公共，实时**（股价） | `no-cache` + WebSocket / SSE 推 |
| **私有，敏感**（账户余额） | `private, no-store` 或 `private, max-age=0, must-revalidate` |
| **静态文件 hash 名**（bundle） | `public, max-age=31536000, immutable` |
| **HTML 入口** | `no-cache` + ETag |
| **图片 / 视频** | `public, max-age=31536000` + 文件名带 hash 或版本 |

## 九、缓存击穿 / 穿透 / 雪崩

### 击穿（cache breakdown）

热点 key 过期瞬间所有请求打到 DB。

**解决**：
- **Mutex / single-flight**：第一个请求加锁查 DB，后续请求等结果
- **永不过期 + 后台刷新**：业务可接受短期 stale

### 穿透（cache penetration）

请求不存在的 key（攻击 / bug），每次都查 DB。

**解决**：
- **空值缓存**：DB 查不到也缓存 `null` 5 秒
- **Bloom filter**：先在 bloom 看 key 是否可能存在

### 雪崩（cache avalanche）

大量 key 同时过期，瞬时 QPS 把 DB 打挂。

**解决**：
- **TTL 加随机抖动**：`ttl + random(0, 30s)`
- **预热**：发版后主动 warm 关键 key
- **降级**：DB 压力大时返回 stale

## 十、cache invalidation 策略

### 1. TTL 自然过期（最简单）

写完不管，等过期。适合最终一致即可的数据。

### 2. 写后失效（write-through invalidation）

```
write DB → delete cache key
```

**陷阱**：先删 cache 再写 DB 会有小窗口写入旧值；先写 DB 再删 cache 也有 race（但更安全）。

### 3. Cache-Aside

```
read:  cache miss → DB → 写 cache → return
write: 写 DB → 失效 cache key
```

经典模式，易理解。

### 4. Write-Behind

写 cache 立即返回，异步刷 DB。性能高，但风险：cache 挂了未刷的数据丢失。

### 5. 标签/版本号（CDN 推荐）

```
Surrogate-Key: products user-123
```

部署后 purge by tag，不用列 URL。

## 十一、调试 / 验证

```bash
# 1. 看实际响应头
curl -I https://example.com/bundle.js
# 关注：Cache-Control / ETag / Age / X-Cache (CDN 命中标志)

# 2. 强制不带缓存
curl -H 'Cache-Control: no-cache' -I https://...

# 3. 模拟条件请求
curl -H 'If-None-Match: "abc"' -I https://...    # 应返 304

# 4. Cloudflare 命中状态
# CF-Cache-Status: HIT / MISS / EXPIRED / DYNAMIC / BYPASS
# Age: 1234     ← CDN 已缓存秒数

# 5. 浏览器 DevTools Network
# Size 列：from disk cache / from memory cache / 200 / 304
# Disable cache 选项可测试无缓存表现
```

## 十二、Don'ts

- ❌ 静态文件 hash 名却写 `max-age=300` — 浪费，应该 `max-age=31536000, immutable`
- ❌ HTML 入口写 `max-age=86400` — 用户看不到新版本，应 `no-cache`
- ❌ 用户专属数据返回 `Cache-Control: public` — 上一个用户的数据被下一个用户拿到（**严重数据泄露**）
- ❌ `Vary: User-Agent` 或 `Vary: Cookie` — 命中率接近 0
- ❌ 改了内容不改 ETag / 文件名 — 缓存永不更新
- ❌ ETag 用随机数 / 时间戳 — 永远不命中
- ❌ 不加 `stale-while-revalidate` — 过期瞬间 latency 暴涨
- ❌ 用 cache 当唯一存储 — Redis 也会丢数据
- ❌ Cache key 把整个 URL（含 query）编码 — 不同顺序 query 重复缓存
- ❌ 改 ENV 后忘了 purge CDN — 旧版本还跑

## 十三、参考资料

- MDN HTTP Caching：https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- web.dev/articles/http-cache：https://web.dev/articles/http-cache
- RFC 9111 (HTTP Caching)：https://www.rfc-editor.org/rfc/rfc9111
- Cloudflare Cache docs：https://developers.cloudflare.com/cache/
- Fastly VCL Caching：https://docs.fastly.com/en/guides/caching-overview
- Workbox（Service Worker 缓存）：https://developer.chrome.com/docs/workbox
