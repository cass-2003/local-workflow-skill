---
name: anti-detection
description: "扩展反检测与防滥用规范（J-SOP 实战）。覆盖站点反爬绕过（人类行为模拟/随机延迟/User-Agent 一致性）、扩展自身防分析（rollup-plugin-obfuscator/构建水印 BUILD_ID/chunk hash 命名/敏感字段加密）、license 防破解（HMAC 签名/JWT 双密钥/恒时比较/速率限制）、店小秘 API 探测、字段稳定性兜底。当用户提到反检测、anti-detection、反爬、obfuscator、混淆、水印、watermark、破解、license crack、HMAC、防滥用、bypass、店小秘 API、DXM 接口时使用。"
---

# Anti-Detection Skill — J-SOP 防滥用实战

## 何时使用

- 客户反馈"被 1688 / Amazon 风控了" → 加随机延迟 / 仿人类行为
- 评估扩展被破解风险 → 复盘混淆 / 水印 / 加密策略
- 加新的敏感模块 → 决定是否纳入 obfuscator include 列表
- 调试店小秘 / 1688 内部 API 调用 → 探测请求头 / 签名要求
- 检查 license 验证逻辑是否被绕过

⚠️ 本 skill 仅用于**自家扩展**的合规防滥用与字段稳定性兜底。不指导对第三方系统的恶意攻击。

## 一、站点反爬观察（J-SOP 三站现状）

| 站点 | 已观察的检测点 | 已实施对策 |
|---|---|---|
| **1688** | 短时间高频请求 / 无 referer / 异常 UA | content script 走真实浏览器，UA 一致；操作走 click 模拟；批量提取走滚动触发懒加载 |
| **Amazon** | bot 检测（异常 click 模式 / 无 mouse move） | 同上；**每次操作 250ms 随机抖动**；不滥用 chrome.scripting.executeScript |
| **店小秘** | iframe 嵌套 / CSRF token / session 校验 | 复用页面已登录 session；不直接调内部 API，走表单提交 |

## 二、人类行为模拟（content script）

```typescript
// shared/human-delay.ts
export const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

/** 250-450ms 随机抖动（默认人类点击间隔范围） */
export const humanDelay = (min = 250, max = 450) =>
  sleep(min + Math.random() * (max - min))

/** 滚动到元素，并等懒加载 */
export async function scrollToAndWait(el: Element) {
  el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  await humanDelay(400, 700)   // 慢一点让 IntersectionObserver 触发
}

/** 批量任务限并发 */
export async function mapLimit<T, R>(
  items: T[], concurrency: number, fn: (t: T) => Promise<R>
): Promise<R[]> {
  const results: R[] = []
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency)
    results.push(...await Promise.all(batch.map(fn)))
    await humanDelay(500, 1000)   // 批次间长间隔
  }
  return results
}
```

**用法**：

```typescript
// 而不是 await Promise.all(items.map(processItem))   ← 50 个并发，秒级被风控
await mapLimit(items, 3, processItem)                   // 3 并发 + 批次抖动
```

## 三、扩展防分析（J-SOP 现状）

### 3.1 构建水印 BUILD_ID（SEC-B2a）

每次构建都生成唯一 ID 注入代码，运行时上报到后台审计日志：

```typescript
// vite.config.ts
const BUILD_ID = `${manifest.version}-${Date.now().toString(36)}-${randomBytes(4).toString('hex')}`
console.log(`[J-SOP build] BUILD_ID = ${BUILD_ID}`)

export default defineConfig({
  define: {
    __JSOP_BUILD_ID__: JSON.stringify(BUILD_ID),    // 替换源码中的 __JSOP_BUILD_ID__
    __JSOP_BUILD_TS__: JSON.stringify(Date.now()),
  },
  // ...
})
```

如果发生泄露，运行时上报的 BUILD_ID 可溯源到具体客户构建。

### 3.2 Chunk Hash 命名（SEC-B2c）

```typescript
output: {
  chunkFileNames: 'assets/[hash].js',
  entryFileNames: 'assets/[hash].js',
  assetFileNames: 'assets/[hash].[ext]',
}
```

**目的**：dist 里看到的是 `assets/a1b2c3d4.js`，看不到 `service-worker.js` / `license.js` 这种业务语义文件名，提高静态分析成本。

### 3.3 敏感模块 obfuscator（SEC-B3a）

仅在生产构建对**最敏感**的模块做 javascript-obfuscator：

```typescript
isProd && obfuscator({
  include: [
    '**/shared/license.ts',         // license 验证
    '**/shared/audit-log.ts',       // 审计日志（防屏蔽）
    '**/background/service-worker.ts',  // 总入口
  ],
  options: {
    compact: true,
    controlFlowFlattening: true,
    controlFlowFlatteningThreshold: 0.4,
    deadCodeInjection: false,        // 不要 dead code（包体翻倍）
    stringArray: true,
    stringArrayThreshold: 0.7,
    stringArrayEncoding: ['base64'],
    stringArrayCallsTransform: true,
    identifierNamesGenerator: 'hexadecimal',
    selfDefending: false,             // SW 中开会初始化失败
    transformObjectKeys: true,
    unicodeEscapeSequence: false,
  },
})
```

**禁止 obfuscate 的模块**：
- ❌ React/Preact 组件（破坏 ref 关联）
- ❌ 用 `eval` / `new Function` 的库
- ❌ 与外部 API 交互严格的 schema（混淆后字段名错位）
- ❌ Web Worker / Service Worker 中要 `selfDefending: true`（初始化失败）

**只 obfuscate**：纯逻辑 / 业务规则 / license 验证。

### 3.4 敏感字段加密（chrome.storage.sync）

```typescript
// SENSITIVE_KEYS 列表只包含真正需要保护的（避免 push/pull 性能损失）
const SENSITIVE_KEYS = ['aiApiKey'] as const

// AES-GCM with key derived from license + device fingerprint
async function encryptField(plaintext: string): Promise<string> {
  const key = await deriveKey()
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, encode(plaintext))
  return base64url(concat(iv, new Uint8Array(ct)))
}
```

## 四、License 防破解（License Server）

### 4.1 HMAC 签名 + JWT 双密钥（M12）

```go
// license key 用 HMAC_SECRET 签名（防伪造）
func signLicense(key string, expiresAt int64) string {
  h := hmac.New(sha256.New, []byte(hmacSecret))
  h.Write([]byte(fmt.Sprintf("%s:%d", key, expiresAt)))
  return hex.EncodeToString(h.Sum(nil))
}

// JWT 用 JWT_SECRET（独立密钥）
func issueJWT(uid int64, role string) string {
  claims := jwt.MapClaims{ "user_id": uid, "role": role, "exp": time.Now().Add(7*24*time.Hour).Unix() }
  return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(jwtSecret))
}
```

**关键**：HMAC 和 JWT 用**不同密钥**（环境变量分离）。一个泄露不连带另一个。

### 4.2 admin token 恒时比较（P0-05）

```go
// ❌ 易受 timing attack：长度不同的 string compare 提前 return
if auth == "Bearer " + adminToken { ... }

// ✅ subtle.ConstantTimeCompare 始终遍历完整长度
if subtle.ConstantTimeCompare([]byte(auth), []byte("Bearer "+adminToken)) == 1 { ... }
```

### 4.3 速率限制（H10）

每 IP 每分钟 10 次：

```go
api.POST("/keys/activate", HandleActivate, sensitiveRL)   // 防爆破激活
api.POST("/auth/login",    HandleLogin,    sensitiveRL)   // 防密码爆破
api.POST("/sync/push",     HandleSyncPush, sensitiveRL)   // 防滥用同步接口
```

### 4.4 用户禁用 enforce（P1-H01）

JWT 有效期 7 天。如果 admin 禁用了用户，JWT 仍可用。修复：每次 JWTAuth 都重查 DB：

```go
claims, _ := parseJWT(auth[7:])
user, _ := GetUserByID(claims.UserID)
if user == nil || user.Status != "active" {
  return c.JSON(403, "用户已被禁用")
}
```

## 五、店小秘 API 探测原则

J-SOP 与店小秘集成走 **页面表单提交**（用户已登录的 session 自动带 cookie），不直接调内部 API。

**为什么**：
1. DXM 内部 API 有 CSRF token + 时间戳签名 + 加密参数（变更频繁）
2. 直接调用易被风控（行为模式与浏览器不一致）
3. 页面表单提交"借力"浏览器原生流程，最稳定

```typescript
// content-scripts/dianxiaomi/listing-edit.ts
// 不要这样：调用 /api/listing/save 直接传 JSON
// fetch('/api/listing/save', { method: 'POST', body: JSON.stringify(...) })  ❌

// 而是这样：填表单 + 触发 DXM 自家"保存"按钮
async function applyDraftToForm(draft: Draft) {
  document.querySelector<HTMLInputElement>('#title')!.value = draft.title
  document.querySelector<HTMLInputElement>('#title')!.dispatchEvent(new Event('input', { bubbles: true }))
  // ... 其他字段
  document.querySelector<HTMLButtonElement>('.save-btn')!.click()
}
```

## 六、字段稳定性兜底（防站点改 DOM）

每个 selector 都要有兜底链，并 audit 上报：

```typescript
function getPrice(): number | null {
  // 主选择器
  let el = document.querySelector('.price-num')
  // 备选 1（移动端 / 实验组）
  if (!el) el = document.querySelector('[data-price]')
  // 备选 2（兜底 regex）
  if (!el) {
    const m = document.body.textContent?.match(/¥\s*([\d.]+)/)
    if (m) {
      auditLog('price.fallback.regex')   // 上报"主选择器失效"
      return parseFloat(m[1])
    }
  }
  if (!el) {
    auditLog('price.missing')
    return null
  }
  return parseFloat(el.textContent?.replace(/[^\d.]/g, '') || '0')
}
```

`auditLog` 异步上报到 license-server `/api/audit/report`，运维侧定期巡检"哪些 selector 失效率上升" → 发版本修复。

## 七、Don'ts

- ❌ 在 popup 显示明文 license key 全文 → 至少星号脱敏（`XXXX-****-****-XXXX`）
- ❌ 把 admin token 写死在前端 → 必须服务端环境变量
- ❌ 加密用 ECB / CBC 无 MAC → 用 AES-GCM 自带 auth tag
- ❌ obfuscate **所有**模块 → 包体爆炸 + 性能下降 + 调试困难（仅敏感模块）
- ❌ 上报敏感数据到自家 audit log → 上报字段名 / 失效率，**不上报具体值**
- ❌ DXM API 直调 → 内部签名变更频繁，每次都要逆向（用页面表单代替）
- ❌ 高频并发请求 → 用 mapLimit + humanDelay
- ❌ User-Agent 改写 → MV3 不允许覆盖 fetch UA；扩展 fetch 已带浏览器 UA，不要折腾
- ❌ rate limit 用 sliding window 算法但不清理过期记录 → 内存爆炸（J-SOP 5min ticker 清理）

## 八、调试 / 验证

```bash
# 看是否 obfuscate 生效
cd j-sop-extension && npm run build
strings dist/assets/<hash>.js | grep -i "license\|api_key" | head    # 应该看不到明文

# 看 BUILD_ID 是否注入
grep "__JSOP_BUILD_ID__" dist/assets/*.js                            # 应该被替换为字符串字面量

# License server 速率限制烟测
for i in {1..15}; do curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST http://localhost:8088/api/auth/login -d '{"u":"test","p":"x"}' ; done
# 第 11 次开始应返回 429
```

## 九、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\vite.config.ts`（obfuscator + define + chunk hash）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\license.ts`（license 验证 — 被混淆）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\audit-log.ts`（审计上报 — 被混淆）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\crypto.ts`（AES-GCM 加密）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\human-delay.ts`（人类行为模拟）
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\auth.go`（JWT + admin auth + HMAC）
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\main.go:27-95`（rateLimiter 实现）
- `@j:\J-SOP 伴随式自动化助手\docs\SPRINT-PLAN.md`（SEC-B2a / SEC-B3a / M12 / P0-05 等条目）
