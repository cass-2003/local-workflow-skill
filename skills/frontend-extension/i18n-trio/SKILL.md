---
name: i18n-trio
description: "J-SOP 三语 i18n 维护规范（zh / en / ja）。覆盖 admin.html / user-panel.html / index.html / popup 四个端点的 i18n 字典结构、data-i18n 属性、动态文本、嵌套 key、placeholder、变量插值、新增 key 同步检查清单。当用户提到 i18n、国际化、多语言、translate、字典、locale、zh/en/ja、data-i18n、三语时使用。"
---

# i18n Trio Skill — J-SOP 三语规范

## 何时使用

- 给 admin / user-panel / index 加新文案 → 必须三语全填
- popup 加新 setting → 三语 + 配对 hint 文案
- 审计漏译 / 错译 / 未本地化（写死中文）
- 改动 i18n 加载逻辑 / locale 切换

## 一、三语 = zh / en / ja

J-SOP 支持中文（默认）/ 英文 / 日文，存于浏览器 localStorage / chrome.storage：

| 端 | 语言来源 | 字典位置 |
|---|---|---|
| **admin.html** | `localStorage.lang` | 内联 `<script>` 中 `const I18N = { zh: {...}, en: {...}, ja: {...} }` |
| **user-panel.html** | 同上 | 同上 |
| **index.html** | 同上 | 同上 |
| **popup** | `chrome.storage.sync.locale` | `src/shared/i18n.ts` 三个 ts 字典 |
| **content scripts** | popup 同 | 同上（inject 时读取） |

## 二、HTML 端 i18n 模式

### 字典结构（admin.html / user-panel.html）

```javascript
const I18N = {
  zh: {
    'common.save': '保存',
    'common.cancel': '取消',
    'settings.title': '设置',
    'settings.api.endpoint': 'API 接入地址',
    'settings.api.endpoint.hint': '需以 https:// 开头',
    'license.bind.success': '绑定成功，许可证：{key}',  // 变量插值
    'license.expire.warning': '将在 {days} 天后过期',
  },
  en: {
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    // ... 必须每个 key 都有
  },
  ja: {
    'common.save': '保存',
    // ...
  },
}

function t(key, vars) {
  const lang = localStorage.getItem('lang') || 'zh'
  let s = I18N[lang]?.[key] ?? I18N.zh[key] ?? key
  if (vars) for (const k in vars) s = s.replace(`{${k}}`, vars[k])
  return s
}

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n
    if (key) el.textContent = t(key)
  })
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder
    if (key) el.placeholder = t(key)
  })
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.dataset.i18nTitle
    if (key) el.title = t(key)
  })
}

document.addEventListener('DOMContentLoaded', applyI18n)
```

### HTML 标记

```html
<!-- 文本节点 -->
<button data-i18n="common.save">保存</button>      <!-- 默认中文兜底 -->

<!-- placeholder -->
<input data-i18n-placeholder="settings.api.endpoint.hint" placeholder="需以 https:// 开头">

<!-- title -->
<span data-i18n-title="common.delete" title="删除">🗑</span>

<!-- 动态文本（JS 渲染时） -->
<script>
  document.getElementById('msg').textContent = t('license.bind.success', { key: 'XXX' })
</script>
```

## 三、popup / content scripts 端 i18n

```typescript
// src/shared/i18n.ts
const DICTS = {
  zh: { 'popup.tab.basic': '基础', 'popup.tab.ai': 'AI 文案', ... },
  en: { 'popup.tab.basic': 'Basic', 'popup.tab.ai': 'AI Copy', ... },
  ja: { 'popup.tab.basic': '基本', 'popup.tab.ai': 'AIコピー', ... },
} as const

let currentLang: 'zh' | 'en' | 'ja' = 'zh'

export async function initI18n() {
  const cfg = await syncStore.get('config')
  currentLang = cfg?.locale ?? 'zh'
}

export function t(key: keyof typeof DICTS.zh, vars?: Record<string, string | number>): string {
  let s = DICTS[currentLang][key] ?? DICTS.zh[key] ?? key
  if (vars) for (const k in vars) s = s.replace(`{${k}}`, String(vars[k]))
  return s
}
```

```tsx
// 在组件里
<button>{t('popup.tab.basic')}</button>
<span>{t('license.expire.warning', { days: 7 })}</span>
```

## 四、新增 key 的同步检查清单

每次新加一个文案 key（如 `settings.dropship.toggle`）：

- [ ] **zh 字典**：加 key + 简体中文
- [ ] **en 字典**：加同 key + 英文
- [ ] **ja 字典**：加同 key + 日文
- [ ] **HTML / TSX 引用**：用 `data-i18n="..."` 或 `t('...')`
- [ ] 变量插值用 `{var}` 占位（不要混用 `${}` 或 `%s`）
- [ ] **配对 hint key**：如果有提示文案，约定 key 后缀 `.hint`
- [ ] **审计扫描**：搜索 `>[\u4e00-\u9fa5]+<` 确认没有写死中文
- [ ] **三端联动**：如果 admin / user-panel / popup 都用，要在三处字典各加一份（除非抽到共享 helper）

## 五、key 命名规范

```
<scope>.<group>.<feature>[.<modifier>]

scope:    common / settings / license / dashboard / source / candidate / popup
group:    name 名词类 / action 动词类 / msg 提示类 / err 错误类
feature:  具体功能名
modifier: hint / placeholder / title / desc / btn / disabled
```

例子：
- `common.save` / `common.cancel`
- `settings.api.endpoint` / `settings.api.endpoint.hint`
- `license.bind.success` / `license.bind.err.invalid`
- `popup.tab.basic` / `popup.tab.ai`
- `dashboard.stat.total` / `dashboard.stat.active`

**禁止**：
- ❌ 中文 key：`'保存': 'Save'`
- ❌ 一句话当 key：`'确定要删除吗？这个操作不可恢复': '...'` — 用 `common.delete.confirm`
- ❌ 嵌套对象 key（除非语言库支持）：`{common: {save: '...'}}` —— 我们用扁平 dot key

## 六、动态语言切换

```javascript
function setLang(lang) {
  localStorage.setItem('lang', lang)
  applyI18n()                   // 重新替换所有 data-i18n 节点
  // 通知打开的 tab 也切换
  chrome.runtime?.sendMessage?.({ type: 'LOCALE_CHANGED', lang })
}
```

popup 切换：

```typescript
async function setLocale(lang: 'zh' | 'en' | 'ja') {
  await syncStore.set('config', { ...await syncStore.get('config'), locale: lang })
  currentLang = lang
  // Preact 用 signal / state 触发 re-render；最简单 location.reload()
  location.reload()
}
```

## 七、复数 / 时态（J-SOP 当前不复杂处理）

J-SOP 不引入 ICU MessageFormat / i18next 复数变体（项目复杂度不需要）。中英日三语都用：

```
1 个许可证 / 1 license / 1 ライセンス      ← 单数
3 个许可证 / 3 licenses / 3 ライセンス     ← 复数（英文 +s，中日不变）
```

简化处理：

```javascript
'license.count': {
  zh: '{n} 个许可证',
  en: '{n} license{s}',  // {s} 占位：n>1 替 's'，n=1 替 ''
  ja: '{n} ライセンス',
}

function tCount(key, n) {
  return t(key, { n, s: n > 1 ? 's' : '' })
}
```

## 八、Don'ts

- ❌ 漏掉某语言（zh 有 / en 缺）→ 必须三语对称
- ❌ 拼字符串：`'已绑定 ' + n + ' 个'` → 用 `t('license.count', { n })`
- ❌ 把 key 直接当文案显示 → fallback 链 `currentLang → zh → key`
- ❌ 字典放外部 JSON 文件 → admin.html 是单文件 inline，加载顺序复杂；放内联
- ❌ 用浏览器 `navigator.language` 自动选 → 用户在 popup 显式选过的优先
- ❌ HTML 写死英文："Save" 后期想本地化要回头改 → 一开始就 `data-i18n`
- ❌ 把 hint 文案塞 title 属性 → 移动设备看不到 → 用独立 `<span class="setting-hint">`

## 九、审计扫描

```bash
# 找 admin.html 里写死中文
rg -n '>[\u4e00-\u9fa5]+<' j-sop-license-server/ui/admin.html | grep -v 'data-i18n'

# 找扩展里写死的中文 string
rg -n '"[\u4e00-\u9fa5]+"' j-sop-extension/src --type ts | grep -v 'i18n.ts\|@deprecated\|console\.\|logger\.'

# 找三语字典 key 数量是否一致
rg -c "^\s+'[\w.]+':" j-sop-license-server/ui/admin.html | head
```

## 十、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\ui\admin.html`（admin 字典 + applyI18n）
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\ui\user-panel.html`（user 字典）
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\ui\index.html`（登录字典）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\i18n.ts`（扩展端字典 + t() 函数）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\popup\App.tsx`（popup 用 t() 示例）
