---
name: chrome-mv3-ext
description: "Chrome MV3 扩展开发规范（J-SOP 实战）。覆盖 service worker / content scripts / popup / sidepanel / messaging / storage / permissions / CSP / @crxjs/vite-plugin 构建链。当用户提到 Chrome 扩展、MV3、manifest、service worker、content script、chrome.runtime.sendMessage、chrome.storage、CRX、CRXJS、扩展开发、扩展通信、扩展权限时使用。"
---

# Chrome MV3 扩展开发 Skill — J-SOP 实战版

## 何时使用

- 给 `j-sop-extension` 加新页面（popup tab / sidepanel page / content script 注入）
- 调试扩展间通信（content ↔ service worker ↔ popup）
- 加新站点注入（修改 `host_permissions` + `content_scripts.matches`）
- 服务工人启动失败 / 内存泄漏 / message port 关闭报错排查
- 评审 PR 时检查 manifest / 权限 / CSP 合规

## 一、项目结构（J-SOP 标准）

```
j-sop-extension/
├── manifest.json                      # MV3 manifest（必须 manifest_version: 3）
├── vite.config.ts                     # Vite 6 + @crxjs/vite-plugin
├── package.json                       # type: module, preact 10, biome lint
├── src/
│   ├── background/
│   │   └── service-worker.ts          # 唯一 SW 入口（type: module）
│   ├── content-scripts/
│   │   ├── alibaba/index.ts           # 1688 注入（s.1688.com + detail.1688.com）
│   │   ├── amazon/index.ts            # Amazon 注入（amazon.co.jp）
│   │   └── dianxiaomi/index.ts        # 店小秘注入（*.dianxiaomi.com）
│   ├── popup/
│   │   ├── index.html
│   │   └── App.tsx                    # Preact (NOT React)
│   ├── sidepanel/
│   │   └── index.html
│   ├── shared/                        # 跨上下文共享：types / config / storage / sync / logger / crypto
│   └── styles/
│       ├── tokens.css                 # 与 license-server 主同步副本
│       ├── alibaba.css / amazon.css / dianxiaomi.css
└── dist/                              # vite build 输出（manifest.json + assets/[hash].*）
```

## 二、Manifest 关键约束

```json
{
  "manifest_version": 3,
  "permissions": ["storage","tabs","activeTab","scripting","alarms","sidePanel","unlimitedStorage"],
  "host_permissions": [
    "https://*.amazon.co.jp/*","https://amazon.co.jp/*",
    "https://s.1688.com/*","https://detail.1688.com/*",
    "https://*.dianxiaomi.com/*",
    "https://cbu01.alicdn.com/*",
    "https://license.haiio.xyz/*",
    "https://generativelanguage.googleapis.com/*"
  ],
  "optional_host_permissions": ["https://*/*"],
  "background": { "service_worker": "src/background/service-worker.ts", "type": "module" },
  "content_scripts": [{
    "matches": [...],
    "js": ["src/content-scripts/<site>/index.ts"],
    "css": ["src/styles/<site>.css"],
    "run_at": "document_idle"
  }],
  "action":      { "default_popup": "src/popup/index.html" },
  "side_panel":  { "default_path": "src/sidepanel/index.html" }
}
```

**规则**：
- `permissions` 只加最小集 — 新增任何权限要写理由（见 `docs/SPRINT-PLAN.md` 风险评审）
- `host_permissions` 严格枚举三个业务站 + License 服务器 + Gemini API；其他站点用 `optional_host_permissions` + `chrome.permissions.request()` 动态申请
- `run_at: document_idle` 是默认；只有需要拦截网络的才用 `document_start`
- 新增 content script matches 必须同步在 `src/content-scripts/<site>/index.ts` 加入页面类型检测（PDP / SRP / 列表）

## 三、Service Worker 模式（J-SOP idiom）

```typescript
// src/background/service-worker.ts
// MV3 SW 不是常驻进程：30 秒空闲会被 terminate，被消息唤醒重启。
// → 不能用模块级变量做缓存（每次重启会丢）。
// → 用 chrome.storage.session 做短期缓存，chrome.storage.local 做持久缓存。

import { logger } from '@shared/logger'
import type { PushToDxmMsg, SourceLibraryFlushMsg } from '@shared/types'

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  // ⚠️ 关键：异步 handler 必须 return true 保持 message port 打开，
  // 否则 sendResponse 时会触发 "The message port closed before a response was received."
  switch (msg.type) {
    case 'PUSH_TO_DXM':
      handlePushToDxm(msg as PushToDxmMsg).then(sendResponse).catch(e => sendResponse({ ok: false, error: String(e) }))
      return true
    case 'SOURCE_LIBRARY_FLUSH':
      handleFlush().then(sendResponse).catch(...)
      return true
  }
  return false
})

// 周期任务用 chrome.alarms（替代 setInterval — SW 重启时 setInterval 会丢失）
chrome.alarms.create('sync-flush', { periodInMinutes: 5 })
chrome.alarms.onAlarm.addListener((alarm) => { if (alarm.name === 'sync-flush') flushSync() })
```

**陷阱清单**：
- ❌ `setTimeout(fn, 60000)` SW 30s 后被 kill → 用 `chrome.alarms`
- ❌ 模块级 `let cache = {}` 重启即丢 → 用 `chrome.storage.session`
- ❌ async handler 不 `return true` → message port closed
- ❌ `import('./module')` 动态导入在 SW 里有限制 → 静态 import 优先
- ❌ 在 SW 用 `window` / `document` / `localStorage` → 不存在
- ❌ DOMParser / fetch with FormData 部分 polyfill 缺失 → 用 vite-plugin-node-polyfills 补 buffer

## 四、Content Script 模式

```typescript
// src/content-scripts/alibaba/index.ts
// 入口必须幂等：SPA 路由切换 / pjax 跳转会重复执行
let initialized = false
async function init() {
  if (initialized) return
  initialized = true

  // 1. 等 DOM 就绪（document_idle 已经晚于 DOMContentLoaded，但仍要等业务节点）
  await waitForElement('.search-card-list', { timeout: 5000 })

  // 2. 检测页面类型（SRP / PDP）
  const url = location.href
  if (url.includes('s.1688.com')) initSearchPage()
  else if (url.includes('detail.1688.com')) initDetailPage()
}

// 3. 监听 SPA 路由切换（1688 / Amazon 都用 history pushState）
const origPush = history.pushState
history.pushState = function(...args) {
  origPush.apply(this, args)
  setTimeout(reinit, 500)
}
window.addEventListener('popstate', reinit)

init()
```

**幂等 + 防重复注入**：
- 用 `data-jsop-injected` 属性标记已处理元素；MutationObserver 二次扫描时跳过
- 入口 `if (window.__JSOP_INJECTED__) return; window.__JSOP_INJECTED__ = true`
- 注入按钮要 `removeChild` 旧的再加新的，避免 DOM 残留

## 五、Messaging 模式（J-SOP 标准）

### 三种通道

| From | To | API | 用途 |
|---|---|---|---|
| Content / Popup | SW | `chrome.runtime.sendMessage(msg)` | 业务请求（PUSH_TO_DXM / FETCH_API） |
| SW | 特定 tab content | `chrome.tabs.sendMessage(tabId, msg)` | SW 唤醒指定 tab（如 SOURCE_SELECTED） |
| Popup ↔ Popup 同上下文 | — | `customEvent` / 全局变量 | 不要用 chrome.runtime |

### 类型化（必须）

```typescript
// src/shared/types.ts
export interface PushToDxmMsg {
  type: 'PUSH_TO_DXM'
  sessionId: string
  source: { offerId: string; title: string }
}
export type ExtMsg = PushToDxmMsg | SourceLibraryFlushMsg | ...

// 调用：
const resp = await chrome.runtime.sendMessage<PushToDxmMsg, { ok: boolean }>({
  type: 'PUSH_TO_DXM', sessionId: crypto.randomUUID(), source: {...}
})
```

### 失败处理

```typescript
try {
  const resp = await chrome.runtime.sendMessage(msg)
  if (!resp?.ok) throw new Error(resp?.error || 'unknown')
} catch (e) {
  // 常见：Could not establish connection. Receiving end does not exist.
  // 通常是 SW 没有该消息类型的 handler，或目标 tab 没有 content script
  logger.warn('sendMessage failed', e)
}
```

## 六、Storage 三层（J-SOP 标准）

| 层 | API | 容量 | 用途 |
|---|---|---|---|
| **chrome.storage.sync** | KV | 100KB / 8KB per item | 用户配置（账户跨设备同步）— 加密敏感字段 |
| **chrome.storage.local** | KV | unlimitedStorage | 大对象 / 草稿 / 缓存 |
| **chrome.storage.session** | KV | 内存 | SW 重启即丢 — 短期 token |
| **IndexedDB** | 结构化 | 浏览器额度 | 选品库 / 候选列表（用 `idb` 类库简化） |

J-SOP 用 `src/shared/storage.ts` 封装 `syncStore` / `localStore` 统一接口。**永远不直接调用 `chrome.storage.*` API**。

## 七、CSP 与外部资源

MV3 默认 CSP：`script-src 'self'; object-src 'self'`，**不允许内联 script / eval**。

- ❌ `<script>doSomething()</script>` → 报 CSP error
- ❌ `eval(...)` / `new Function(...)`
- ✅ 所有 JS 文件作为 `<script src>` 加载（Vite 自动处理）
- ✅ 调外部 API 需在 `host_permissions` 列出

## 八、@crxjs/vite-plugin 构建

```typescript
// vite.config.ts
plugins: [
  preact(),
  crx({ manifest }),                      // 自动从 manifest.json 拿入口
  nodePolyfills({ include: ['buffer'], globals: { Buffer: true } }),  // 部分 npm 包需要
  isProd && obfuscator({                   // 仅敏感模块混淆
    include: ['**/shared/license.ts','**/shared/audit-log.ts','**/background/service-worker.ts'],
    options: { controlFlowFlattening: true, stringArray: true, stringArrayEncoding: ['base64'] },
  }),
],
build: {
  rollupOptions: {
    input: { popup: 'src/popup/index.html', sidepanel: 'src/sidepanel/index.html' },
    output: {
      chunkFileNames: 'assets/[hash].js',   // SEC-B2c：不暴露业务语义
      entryFileNames: 'assets/[hash].js',
      assetFileNames: 'assets/[hash].[ext]',
    },
  },
}
```

`define` 注入构建水印 `__JSOP_BUILD_ID__` 用于审计溯源。

## 九、Don'ts

- ❌ MV2 idiom：`background.scripts` / `chrome.extension.getBackgroundPage()` / `chrome.runtime.onMessage` 同步返回值
- ❌ 在 service worker 用 `setInterval` / `setTimeout > 30s`
- ❌ 在 content script 直接读页面 `window` 变量 — content script 是隔离世界，要 `document.dispatchEvent` 或 inject 真实 page script
- ❌ `host_permissions: ["<all_urls>"]` — 用最小集 + `optional_host_permissions`
- ❌ 内联 `<style>` / `<script>` 写在 popup HTML — 抽到 .ts / .css
- ❌ 把 API key 硬编码在源码里 — 用 `chrome.storage.sync` 用户配置 + 服务端代理

## 十、调试清单

1. `chrome://extensions` → 开发者模式 → 加载已解压 `j-sop-extension/dist`
2. SW 日志：`chrome://extensions` → 该扩展 → "service worker" 链接 → DevTools console
3. Content script 日志：F12 该 tab → console（自动隔离世界）
4. Popup 日志：popup 上右键 → "审查弹出内容"
5. Storage 检查：DevTools → Application → Storage → Extension Storage
6. 网络：SW 的 fetch 在 SW DevTools 看；content 的 fetch 在 tab DevTools 看

## 十一、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\manifest.json`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\vite.config.ts`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\background\service-worker.ts`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\storage.ts`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\types.ts`
- 官方文档：https://developer.chrome.com/docs/extensions/mv3/
- CRXJS 文档：https://crxjs.dev/vite-plugin
