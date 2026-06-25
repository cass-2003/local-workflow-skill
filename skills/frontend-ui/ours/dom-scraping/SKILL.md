---
name: dom-scraping
description: "DOM 爬取与逆向规范（J-SOP 实战）。覆盖 1688 / Amazon / 店小秘三站的 DOM 结构提取、Shadow DOM 穿透、懒加载等待、SKU 动态点击展开、SPA 路由切换、MutationObserver、第三方插件字段（如卖家精灵 22 字段）解析。当用户提到 DOM 爬取、爬虫、scraping、shadow DOM、懒加载、lazy load、MutationObserver、动态 SKU、1688 解析、Amazon 解析、店小秘解析、site reverse、网页逆向时使用。"
---

# DOM Scraping Skill — J-SOP 三站爬取规范

## 何时使用

- 给 1688 / Amazon / 店小秘加新字段提取（价格、评分、SKU、详情图）
- 排查"图片少了几张" / "SKU 没抓全" / "评分提取为 0" 等数据缺失问题
- 解析第三方插件注入的字段（如卖家精灵 sprite-card 22 字段）
- 处理 SPA 路由切换 / 懒加载 / Shadow DOM 嵌入的元素

## 一、三站 DOM 结构速查

### 1688

| 页面 | URL | 关键容器 |
|---|---|---|
| **搜索 SRP** | `s.1688.com/selloffer/offer_search.htm?keywords=...` | `.search-card-list .search-card-item` |
| **商品 PDP** | `detail.1688.com/offer/<offerId>.html` | `.detail-info`, `.sku-list`, `v-detail-e.html-description`（**Shadow DOM**） |
| **图片 CDN** | `cbu01.alicdn.com/img/ibank/...jpg` | 主图 / 详情图 / 变体图 |

### Amazon (.co.jp)

| 页面 | URL | 关键容器 |
|---|---|---|
| **搜索 SRP** | `amazon.co.jp/s?k=...` | `[data-component-type="s-search-result"]` |
| **商品 PDP** | `amazon.co.jp/dp/<asin>` | `#productTitle`, `#feature-bullets`, `#imageBlock` |
| **第三方插件** | sprite-card 注入 | `.JS-extension-sprite-card`（卖家精灵 22 字段） |

### 店小秘

| 页面 | URL | 关键容器 |
|---|---|---|
| **编辑** | `dianxiaomi.com/listing/index.htm` | iframe 嵌入 — 必须穿透 |
| **库存** | `*.dianxiaomi.com/inventory/...` | 主表 `.list-tbody` |

## 二、等待 DOM 就绪（J-SOP 标准）

```typescript
// src/shared/dom-utils.ts
export async function waitForElement(
  selector: string,
  opts: { timeout?: number; root?: ParentNode } = {}
): Promise<Element | null> {
  const { timeout = 5000, root = document } = opts
  const existing = root.querySelector(selector)
  if (existing) return existing

  return new Promise((resolve) => {
    const timer = setTimeout(() => { observer.disconnect(); resolve(null) }, timeout)
    const observer = new MutationObserver(() => {
      const el = root.querySelector(selector)
      if (el) { clearTimeout(timer); observer.disconnect(); resolve(el) }
    })
    observer.observe(root === document ? document.body : root as Element, {
      childList: true, subtree: true,
    })
  })
}

// 等元素**消失**（用于 loading 转圈结束）
export async function waitForElementGone(selector: string, opts = { timeout: 5000 }) { ... }

// 等待多个元素至少 N 个出现（用于商品列表加载）
export async function waitForCount(selector: string, min: number, opts = { timeout: 5000 }) { ... }
```

**陷阱**：
- 不要 `setTimeout(extract, 3000)` 写死延迟 — 网速慢的机器会失败
- MutationObserver 必须 `disconnect()`，否则内存泄漏
- timeout 兜底 → 5s 仍没出现就 resolve null，业务侧降级处理

## 三、Shadow DOM 穿透

1688 详情页的 `v-detail-e.html-description` 用 Shadow DOM 包详情图（开放 shadow，可通过 `.shadowRoot` 访问）：

```typescript
function collectImagesFromShadowRoot(root: ShadowRoot | Document): string[] {
  const urls: string[] = []
  // 1. 普通 <img>
  root.querySelectorAll('img').forEach(img => {
    const src = img.currentSrc || img.src || img.dataset.src || img.dataset.lazySrc
    if (src) urls.push(src)
  })
  // 2. background-image inline style
  root.querySelectorAll<HTMLElement>('[style*="background"]').forEach(el => {
    const m = el.style.backgroundImage.match(/url\(["']?(.+?)["']?\)/)
    if (m) urls.push(m[1])
  })
  // 3. 递归子 shadow
  root.querySelectorAll('*').forEach(el => {
    if (el.shadowRoot) urls.push(...collectImagesFromShadowRoot(el.shadowRoot))
  })
  return urls
}

// 调用：
const detailEl = document.querySelector('v-detail-e.html-description')
const detailImgs = detailEl?.shadowRoot
  ? collectImagesFromShadowRoot(detailEl.shadowRoot)
  : []
```

**封闭 Shadow DOM**（`mode: 'closed'`）：JS 无法访问 — 需要在 `attachShadow` 调用前 hook（页面 script 注入），content script 隔离世界做不到。fallback 用 `Element.prototype.attachShadow` proxy（但需 `world: "MAIN"` 注入）。

## 四、懒加载图片提取

1688 / Amazon 都用懒加载，img 默认 src 是 placeholder，真实地址在多种属性：

```typescript
function getRealImgUrl(img: HTMLImageElement): string | null {
  return img.dataset.src         // 标准懒加载
      || img.dataset.lazySrc     // 1688 懒加载
      || img.dataset.original    // jquery lazy
      || img.dataset.imgUrl
      || img.getAttribute('data-ks-lazyload')
      || (img.currentSrc !== img.src.replace(/^.*?placeholder/, '') ? img.currentSrc : null)
      || (img.src.startsWith('data:') ? null : img.src)  // base64 placeholder 不要
}
```

**触发懒加载**：
```typescript
// 滚动触发 IntersectionObserver
async function triggerLazyLoad(container: Element) {
  container.scrollIntoView({ behavior: 'instant', block: 'center' })
  await new Promise(r => setTimeout(r, 300))
}
```

## 五、动态 SKU 点击展开（1688 PDP）

1688 PDP 的 SKU 颜色变体图，**只有点击该色块后** DOM 才填充对应图片，不点击 src 是空。

```typescript
async function collectAllSkuImages(): Promise<Map<string, string[]>> {
  const result = new Map<string, string[]>()
  const skuButtons = document.querySelectorAll<HTMLElement>('.sku-item-wrapper .sku-item')

  for (const btn of skuButtons) {
    const skuName = btn.querySelector('.sku-name')?.textContent?.trim() ?? ''
    btn.click()
    await new Promise(r => setTimeout(r, 200))   // 等图片填充

    const galleryImgs = Array.from(document.querySelectorAll<HTMLImageElement>('.gallery img'))
      .map(getRealImgUrl).filter(Boolean) as string[]
    result.set(skuName, galleryImgs)
  }
  return result
}
```

**注意**：
- 必须 `await` 每次点击间隔，否则 DOM 还没填好下一次就跳过
- 完成后**复位到第一个 SKU**（避免影响用户）
- 加 try/catch — 部分商品没 sku 区域，querySelector 返回 null

## 六、第三方插件字段解析（卖家精灵 22 字段）

Amazon 搜索页插入卖家精灵插件后，每个 result 卡片旁有 `.JS-extension-sprite-card`，含 22 个字段。J-SOP 提取其中 11 个（FBM/FBA、月销、上架时间、中国卖家、ACOS 等）：

```typescript
// src/shared/sprite-card-parser.ts
export interface SpriteFields {
  fulfillment?: 'FBM' | 'FBA' | 'AMZ'
  monthlySales?: number
  listingDate?: string         // ISO
  isChineseSeller?: boolean
  acos?: number
  // ... 11 字段
}

export function parseSpriteCard(cardEl: Element): SpriteFields {
  const fields: SpriteFields = {}
  cardEl.querySelectorAll('[class*="field-"]').forEach(field => {
    const key = field.className.match(/field-(\w+)/)?.[1]
    const value = field.querySelector('.value')?.textContent?.trim()
    if (!key || !value) return

    switch (key) {
      case 'fulfillment': fields.fulfillment = value as any; break
      case 'monthlySales': fields.monthlySales = parseInt(value.replace(/[^\d]/g, ''), 10); break
      case 'listingDate':  fields.listingDate = parseListingDate(value); break
      // ...
    }
  })
  return fields
}
```

**陷阱**：
- 第三方插件 DOM 结构不稳定，每次升级都要回归
- 必须做 fallback — 字段不存在不能让整体提取崩溃
- 字段缺失返回 `undefined`，不要返回 0 / '' 假数据（影响下游过滤）

## 七、SPA 路由切换处理

Amazon / 1688 搜索页都用 history pushState，URL 变了但页面不刷新，content script 不会重跑：

```typescript
let currentUrl = location.href
const reinit = () => {
  if (location.href === currentUrl) return
  currentUrl = location.href
  setTimeout(init, 500)   // 等新页面 DOM 替换完
}

// 1. history API 监听
const origPush = history.pushState
history.pushState = function(...args) { origPush.apply(this, args); setTimeout(reinit, 0) }
window.addEventListener('popstate', reinit)

// 2. URL 轮询兜底（500ms 一次，防 hash 变化漏掉）
setInterval(() => { if (location.href !== currentUrl) reinit() }, 500)
```

## 八、Don'ts（爬取陷阱）

- ❌ `await new Promise(r => setTimeout(r, 5000))` 写死等待 → 用 `waitForElement`
- ❌ `img.src` 直接用 → 懒加载是 placeholder，必须查 `data-*`
- ❌ 不处理 Shadow DOM → 详情图缺失（H1/H2 客户 P0 风险）
- ❌ SKU 不点击就提取 → 变体图全是默认值
- ❌ MutationObserver 不 disconnect → 长期内存膨胀
- ❌ 拼字符串拼图片 URL（如 `cbu01.alicdn.com/${id}.jpg`）→ 要从 DOM 真实 src
- ❌ 同步 click 不等响应 → 数据捕获窗口错过
- ❌ 重复注入按钮 → 用 `data-jsop-injected="1"` 标记
- ❌ 在 SPA 切页后不重新 init → 旧元素引用失效
- ❌ 解析 textContent 没 trim / 没去 `\u200b` 零宽字符 → 字段比较失败

## 九、字段缺失分级处理

| 缺失字段 | 分级 | 处理 |
|---|---|---|
| 主图 URL | **Critical** | 中断流程，提示用户刷新 |
| 标题 / 价格 | **High** | 跳过该 item，记录 audit log |
| 详情图 | **Medium** | 用主图占位，标记 `incomplete=true` |
| SKU 变体图 | **Medium** | 用主图，前端提示"未抓到变体图" |
| ACOS / 第三方字段 | **Low** | 留空 — 不影响主流程 |

## 十、调试技巧

```typescript
// 在 content script 里临时挂全局变量调试
;(window as any).__JSOP_DEBUG = { lastExtracted, parseSpriteCard, getRealImgUrl }

// F12 console:
__JSOP_DEBUG.lastExtracted               // 看上次提取结果
__JSOP_DEBUG.parseSpriteCard($0)         // 用选中的 DOM 元素测试
```

DevTools "Pause on DOM mutation" → 选目标 element → 右键 → Break on subtree modifications，可定位是哪个 script 在改 DOM。

## 十一、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\content-scripts\alibaba\source-picker.ts`（1688 PDP 主图/SKU/详情图 + Shadow DOM）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\content-scripts\alibaba\supplier-filter.ts`（1688 SRP 卡片提取）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\content-scripts\amazon\metrics.ts`（Amazon PDP 基础字段）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\content-scripts\amazon\sop-filter.ts`（Amazon SRP 过滤）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\sprite-card-parser.ts`（卖家精灵 22 字段解析）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\content-scripts\dianxiaomi\image-process.ts`（DXM 图片分组）
