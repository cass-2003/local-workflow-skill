---
name: preact-popup
description: "Preact + Vite + chrome.storage popup 开发规范（J-SOP 实战）。覆盖 Preact 10 hooks、状态管理（无 Redux）、与 chrome.storage 双向绑定、tab 路由、SettingInput 组件模式、debounce 持久化、@types/chrome 类型、构建 hash chunk。当用户提到 popup、Preact、Vite popup、SettingInput、popup tab、chrome.storage 绑定、设置页面、扩展 UI、popup 构建时使用。"
---

# Preact Popup Skill — J-SOP popup 开发实战

## 何时使用

- 给 popup 加新 tab / 新设置项 / 新组件
- 调试 popup 与 chrome.storage 双向绑定不同步
- 改动 sidepanel（与 popup 同模式但更大）
- 优化 popup 启动速度 / 包体积

⚠️ **本项目用 Preact 不是 React**。所有 hooks 从 `preact/hooks` import，不是 `react`。

## 一、项目结构

```
src/popup/
├── index.html              # 入口 HTML（500x600 固定大小）
├── main.tsx                # render(<App />, document.getElementById('app'))
├── App.tsx                 # 主组件（含 tab 切换 + 设置组）
├── components/             # 复用组件（SettingInput / Toggle / Tab）
└── hooks/
    ├── useConfig.ts        # 双向绑定 chrome.storage.sync.config
    └── useDebounce.ts
```

## 二、Preact vs React 的实际差异

| 项 | Preact | React |
|---|---|---|
| 包体 | 3KB | 40KB |
| import hooks | `preact/hooks` | `react` |
| JSX 命名空间 | `preact` 自动注入（`@preact/preset-vite`） | `react` |
| 事件 | 原生 DOM 事件名（`onInput`, `onChange`） | Synthetic（同名但语义略不同） |
| `className` vs `class` | 都支持，**优先 `class`** | 必须 `className` |
| `htmlFor` vs `for` | 都支持 | 必须 `htmlFor` |
| 受控 input | `onInput` 实时 / `onChange` 失焦 | `onChange` 实时 |

**J-SOP 标准**：`class` + `onInput`（受控实时绑定）。

## 三、Popup 入口

```typescript
// src/popup/main.tsx
import { render } from 'preact'
import { App } from './App'
import '../styles/tokens.css'    // 必须最先 import 设计令牌
import '../styles/popup.css'
render(<App />, document.getElementById('app')!)
```

```html
<!-- src/popup/index.html -->
<!doctype html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>J-SOP</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="./main.tsx"></script>
</body>
</html>
```

popup 默认 800px 宽度上限 — 固定 `min-width: 480px; max-width: 600px`。

## 四、与 chrome.storage 双向绑定（核心模式）

```typescript
// hooks/useConfig.ts
import { useState, useEffect, useCallback } from 'preact/hooks'
import { syncStore } from '@shared/storage'
import type { Config } from '@shared/types'

export function useConfig() {
  const [config, setConfigState] = useState<Config | null>(null)

  // 1. 初始加载
  useEffect(() => { syncStore.get('config').then(setConfigState) }, [])

  // 2. 监听其他设备 / 其他 tab 的修改
  useEffect(() => {
    const handler = (changes: any, area: string) => {
      if (area === 'sync' && changes.config) setConfigState(changes.config.newValue)
    }
    chrome.storage.onChanged.addListener(handler)
    return () => chrome.storage.onChanged.removeListener(handler)
  }, [])

  // 3. 修改并持久化（debounce 800ms 防频繁写）
  const update = useCallback((patch: Partial<Config>) => {
    setConfigState(prev => prev ? { ...prev, ...patch } : prev)
    debouncedSave(patch)
  }, [])

  return { config, update }
}

const debouncedSave = debounce(async (patch: Partial<Config>) => {
  const cur = await syncStore.get('config') ?? {}
  await syncStore.set('config', { ...cur, ...patch })
}, 800)
```

## 五、SettingInput 组件模式（J-SOP 标准）

```tsx
// components/SettingInput.tsx
interface Props {
  label: string
  hint?: string
  value: string | number
  type?: 'text' | 'number' | 'password'
  onChange: (v: string) => void
}
export function SettingInput({ label, hint, value, type = 'text', onChange }: Props) {
  return (
    <div class="setting-row">
      <label>
        <span class="setting-label">{label}</span>
        {hint && <span class="setting-hint">{hint}</span>}
      </label>
      <input
        type={type}
        value={value as any}
        onInput={(e) => onChange((e.target as HTMLInputElement).value)}
      />
    </div>
  )
}
```

Toggle 同模式：

```tsx
export function SettingToggle({ label, hint, checked, onChange }) {
  return (
    <div class="setting-row">
      <label class="toggle-row">
        <span>
          <span class="setting-label">{label}</span>
          {hint && <span class="setting-hint">{hint}</span>}
        </span>
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange((e.target as HTMLInputElement).checked)}
        />
      </label>
    </div>
  )
}
```

## 六、Tab 路由（无 router 库）

```tsx
// App.tsx
const TABS = [
  { id: 'basic',    label: '基础' },
  { id: 'pricing',  label: '定价' },
  { id: 'ai',       label: 'AI 文案' },
  { id: 'about',    label: '关于' },
] as const
type TabId = typeof TABS[number]['id']

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>('basic')
  const { config, update } = useConfig()
  if (!config) return <div class="loading">加载中…</div>

  return (
    <div class="popup-app">
      <header class="popup-header">
        <h1>J-SOP</h1>
        <span class="version">v{__JSOP_BUILD_ID__}</span>
      </header>
      <nav class="tabs">
        {TABS.map(t => (
          <button
            class={`tab ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >{t.label}</button>
        ))}
      </nav>
      <main class="tab-content">
        {activeTab === 'basic' && <BasicTab config={config} update={update} />}
        {activeTab === 'pricing' && <PricingTab ... />}
        {activeTab === 'ai' && <AiTab ... />}
        {activeTab === 'about' && <AboutTab />}
      </main>
    </div>
  )
}
```

记住状态在 popup 关闭时丢失。如果需要持久化最后查看的 tab，放 `chrome.storage.local.set('lastTab', ...)`。

## 七、@types/chrome 类型

`package.json` 已引入 `@types/chrome`，所有 chrome.* API 都有类型：

```typescript
const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
const [tab] = tabs
if (tab?.id) {
  await chrome.tabs.sendMessage<MyMsg, MyResp>(tab.id, { type: 'PING' })
}
```

`@types/chrome` 0.0.306 仍偶有 API 滞后（尤其 sidePanel / declarativeNetRequest）— 用 `as any` 兜底，加 `// @types/chrome 滞后` 注释。

## 八、Vite popup 构建

```typescript
// vite.config.ts
build: {
  rollupOptions: {
    input: { popup: 'src/popup/index.html', sidepanel: 'src/sidepanel/index.html' },
    output: {
      chunkFileNames: 'assets/[hash].js',  // 所有 chunk 名匿名（SEC-B2c）
      entryFileNames: 'assets/[hash].js',
      assetFileNames: 'assets/[hash].[ext]',
    },
  },
}
```

`@crxjs/vite-plugin` 自动处理：
- 把 popup/sidepanel HTML 入口写入 dist/manifest.json 的 `action.default_popup`
- HMR 监听 src/ 变化（`vite dev` 模式可不刷新扩展自动更新）

## 九、popup 启动性能

popup 每次点击都重新构造 — 慢启动 = 用户感知差。

**优化清单**：
- ✅ 主 bundle ≤ 100KB gzip — 重组件懒加载（如 AI 历史预览）
- ✅ 不要在 render 同步执行长任务 — `useEffect` 异步加载
- ✅ 静态 import 优先（CRX SW 不喜欢动态 import；popup 可以但浪费 round-trip）
- ✅ tokens.css / popup.css 内联到 HTML 减少请求
- ❌ 不要在 popup 启动时 `chrome.runtime.sendMessage` 等 SW 响应（可能要等 SW 重启 200ms+）— 改为 popup 自己读 storage，SW 后台异步刷新

## 十、Don'ts

- ❌ 用 React import：`from 'react'` → 编译报错或拉两份运行时
- ❌ JSX 用 `className` —— Preact 推荐 `class`（项目一致性）
- ❌ `useState` 不带类型注释 — TS 推断不出复杂结构 → 显式 `useState<Config | null>(null)`
- ❌ 直接调用 `chrome.storage.sync.set` —— 用 `syncStore` 抽象（自动加锁 + 加密）
- ❌ popup 关闭时未 flush —— 长任务用 SW 跑，popup 只下指令
- ❌ 用 `setTimeout` 做 debounce —— 用 `lodash.debounce` 或自写（保留 cancel 能力）
- ❌ 大量内联 style —— 抽到 popup.css 用 `var(--jsop-*)` 令牌
- ❌ popup 不自适应窄屏 —— 至少做到 480px 宽度可用

## 十一、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\popup\App.tsx`（主组件 1400+ 行）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\popup\index.html`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\styles\popup.css`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\storage.ts`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\package.json`
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\vite.config.ts`
- Preact 文档：https://preactjs.com/guide/v10/
