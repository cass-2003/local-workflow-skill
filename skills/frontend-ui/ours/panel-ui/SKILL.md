---
name: panel-ui
description: "J-SOP 简约风格 UI 设计系统。基于 j-sop-license-server/ui/assets/css 的统一设计令牌（tokens.css v1.0）+ 玻璃化组件（glass-panel）。覆盖 admin / user-panel / index 三个端的色板、间距、组件、布局、深浅双主题。当用户提到 panel-ui、jsop-ui、glass-panel、jsop-accent、面板 UI、简约 UI、后台面板 UI、设计系统、design system 时使用。"
---

# J-SOP Panel UI Skill — 简约风格设计系统

## 何时使用

- 在 `j-sop-license-server/ui/` 下新增 / 修改任何 HTML / CSS（admin、user-panel、index）
- 在扩展端 `j-sop-extension/src/styles/` 实现与后台面板视觉一致的 UI
- 评审 / 审计时检查是否硬编码了颜色 / 间距 / 圆角
- 给新页面（如 calculator、shipping rates、prompt templates）补 UI 时需要快速对齐风格

## 一、设计原则

1. **极简色板**：1 主色（accent #3b82f6）+ 3 状态色（success/warning/danger）+ 4 级文字灰 + 4 级底色 = **共 12 色**。已废弃 purple / teal / orange / cyan 装饰色。
2. **状态色仅语义**：success/warning/danger/info 只表达"成功/警告/危险/信息"语义，**严禁作装饰色**（如品牌强调用 accent，不用 success-绿）。
3. **令牌唯一真源**：颜色 / 间距 / 圆角 / 阴影 / 字号 / 动画 一律 `var(--jsop-*)`，**禁止业务层硬编码**。新增令牌须先改 `j-sop-license-server/ui/assets/css/tokens.css`，再同步到 `j-sop-extension/src/styles/tokens.css` 副本。
4. **4px 栅格**：所有 spacing 都是 4 的倍数（`--jsop-sp-1=4` 到 `--jsop-sp-12=48`），不接受 5px / 7px / 13px。
5. **玻璃化为骨架**：卡片用 `.glass-panel`（白底 + 1px subtle border + sm 阴影 + lg 圆角）。**禁止**给玻璃面板再叠 box-shadow 或 background-image 装饰。
6. **深浅双主题**：所有令牌都有 `data-theme="light"` / `data-theme="dark"` 两份。新增令牌必须同时给两份。
7. **响应式**：1024px 降级双列为单列；768px 降级所有多列网格为单列；不要写自定义断点。

## 二、设计令牌速查

引入：`<link rel="stylesheet" href="/assets/css/tokens.css">`（必须最先加载）

### 颜色

| 用途 | 令牌 | Light | Dark |
|---|---|---|---|
| **品牌强调** | `--jsop-accent` | `#3b82f6` | `#60a5fa` |
| **品牌 hover** | `--jsop-accent-hover` | `#2563eb` | `#3b82f6` |
| **品牌 soft 底** | `--jsop-accent-soft` | rgba 10% | rgba 14% |
| **focus ring** | `--jsop-accent-ring` | rgba 25% | rgba 30% |
| **成功** | `--jsop-success` / `-soft` | `#10b981` | `#34d399` |
| **警告** | `--jsop-warning` / `-soft` | `#f59e0b` | `#fbbf24` |
| **危险** | `--jsop-danger` / `-soft` | `#ef4444` | `#f87171` |
| **主文字** | `--jsop-text-primary` | `#0f172a` | `#f1f5f9` |
| **次文字** | `--jsop-text-secondary` | `#475569` | `#cbd5e1` |
| **三级文字 / placeholder** | `--jsop-text-tertiary` | `#94a3b8` | `#64748b` |
| **App 底** | `--jsop-bg-app` | `#f8fafc` | `#0f172a` |
| **卡片底** | `--jsop-bg-card` | `#ffffff` | `#1e293b` |
| **subtle 底** | `--jsop-bg-subtle` | `#f1f5f9` | `#334155` |
| **hover 蒙层** | `--jsop-bg-hover` | rgba 4% | rgba 6% |
| **scrim 遮罩** | `--jsop-bg-scrim` | rgba 35% | rgba 60% |
| **边框** | `--jsop-border` / `-strong` | `#e2e8f0` / `#cbd5e1` | `#334155` / `#475569` |

### Spacing / Radius / Shadow

```css
/* spacing 4px grid */
--jsop-sp-1: 4px;  --jsop-sp-2: 8px;   --jsop-sp-3: 12px; --jsop-sp-4: 16px;
--jsop-sp-5: 20px; --jsop-sp-6: 24px;  --jsop-sp-8: 32px; --jsop-sp-10: 40px; --jsop-sp-12: 48px;

/* radius */
--jsop-radius-sm: 6px;   /* 标签 / 小按钮 */
--jsop-radius-md: 10px;  /* 默认（卡片 / 输入框 / 按钮） */
--jsop-radius-lg: 14px;  /* glass-panel / stat-card */
--jsop-radius-xl: 20px;  /* 模态 / 登录框 */
--jsop-radius-pill: 999px; /* 仅用于 tag / 头像菜单触发器 */

/* shadow */
--jsop-shadow-sm: 0 1px 2px / 4%;          /* 默认卡片 */
--jsop-shadow-md: 0 2px 8px + 1px 2px / 6% /* 悬浮列表 */
--jsop-shadow-lg: 0 8px 24px + 2px 6px / 8%; /* 模态 / dropdown */
--jsop-shadow-focus: 0 0 0 3px var(--jsop-accent-ring);
```

### Typography

- Font: `--jsop-font-sans` 苹果系优先 / `--jsop-font-mono` SF Mono
- 字号：`xs 11 / sm 12 / base 13 / md 14 / lg 16 / xl 18 / 2xl 22 / 3xl 28`
- 行高：`tight 1.2 / snug 1.4 / normal 1.5 / relaxed 1.7`

### 动画

- `--jsop-duration-fast: 150ms`（hover / focus）
- `--jsop-duration-normal: 250ms`（open / close）
- `--jsop-duration-slow: 400ms`（页面切换）
- Easing：`--jsop-easing-spring`（弹性，UI 优先）/ `--jsop-easing-standard`（材料 4-0-2）

### Z-index

`dropdown 100 / sticky 200 / overlay 500 / modal 600 / toast 700` — 不要 999 / 9999。

## 三、核心组件清单

引入：`<link rel="stylesheet" href="/assets/css/components.css">` + `<link rel="stylesheet" href="/assets/css/layout.css">`

### 卡片

```html
<!-- 主容器卡片 -->
<div class="glass-panel">
  <h3>面板标题</h3>
  <!-- 内容 -->
</div>

<!-- Dashboard 统计卡片 grid -->
<div class="stat-cards">
  <div class="stat-card">
    <div class="label">许可证总数</div>
    <div class="value">128</div>
    <div class="sub">较昨日 +3</div>
  </div>
</div>
```

### 表格（标准列表页）

```html
<div class="toolbar">
  <input type="text" placeholder="搜索...">
  <select><option>全部</option></select>
</div>

<div class="glass-panel">
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>键名</th><th>状态</th><th>更新时间</th></tr>
      </thead>
      <tbody>
        <tr><td>...</td><td>...</td><td>...</td></tr>
        <tr><td colspan="3" class="empty-row">暂无数据</td></tr>
      </tbody>
    </table>
  </div>

  <div class="pagination">
    <button>‹</button>
    <button class="active">1</button>
    <button>2</button>
    <button>›</button>
    <span class="page-info">共 38 条</span>
  </div>
</div>
```

### 按钮

```html
<button class="btn btn-primary">主操作</button>
<button class="btn btn-secondary">次操作</button>
<button class="btn btn-danger">危险操作</button>
```

- 主操作每个区域 **最多 1 个** btn-primary
- danger 仅用于不可逆（删除 / 撤销绑定）
- 次操作用 secondary

### 表单

```html
<!-- form-group：垂直堆叠 label + input -->
<div class="form-group">
  <label>许可证名称</label>
  <input type="text" placeholder="输入名称">
</div>

<!-- form-row：自动响应 200px-1fr 多列 -->
<div class="form-row">
  <div class="form-group"><label>开始日期</label><input type="date"></div>
  <div class="form-group"><label>到期日期</label><input type="date"></div>
</div>

<!-- settings-section / -row：水平 label-input 紧凑布局 -->
<div class="settings-section">
  <h4>账户信息</h4>
  <div class="settings-row">
    <label>邮箱</label>
    <span class="info-text">user@example.com</span>
  </div>
  <div class="settings-row">
    <label>显示名</label>
    <input type="text">
  </div>
</div>
```

### 模态

```html
<div class="modal-overlay show">
  <div class="modal">
    <h3>确认删除</h3>
    <p>此操作不可逆，确认继续？</p>
    <div class="modal-actions">
      <button class="btn btn-secondary">取消</button>
      <button class="btn btn-danger">删除</button>
    </div>
  </div>
</div>
```

### Toast（通知，2s 自动消失）

```html
<div class="toast success show">操作成功</div>
<div class="toast error show">网络错误，请重试</div>
```

### 侧边栏 + 顶栏（应用框架）

```html
<div class="app-layout" style="display:flex">
  <aside class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-icon">J</span>
      <div class="logo-text-wrap">
        <span class="logo-text">J-SOP</span>
        <span class="logo-sub">License Manager</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <div class="sidebar-section">主功能</div>
      <div class="sidebar-item active"><span class="nav-icon">📊</span>仪表盘</div>
      <div class="sidebar-item"><span class="nav-icon">🔑</span>许可证</div>
      <div class="sidebar-item admin-only"><span class="nav-icon">👑</span>管理员</div>
    </nav>
    <div class="sidebar-bottom"><div class="version">v2.0.0-alpha.1</div></div>
  </aside>

  <main class="main-area">
    <header class="topbar">
      <div class="topbar-search">
        <span class="topbar-search-icon"><!-- svg --></span>
        <input class="topbar-search-input" placeholder="全局搜索...">
        <span class="topbar-search-kbd">⌘K</span>
      </div>
      <div class="topbar-actions">
        <button class="topbar-icon-btn" title="主题">🌗</button>
        <div class="topbar-user-wrap">
          <button class="topbar-user-trigger">
            <span class="topbar-user-avatar">U</span>
            <span class="topbar-user-name">user@example.com</span>
            <span class="topbar-user-arrow">▾</span>
          </button>
        </div>
      </div>
    </header>

    <div class="page-content">
      <div class="page active">
        <div class="page-header">
          <h2 class="page-title">仪表盘</h2>
        </div>
        <!-- glass-panel / stat-cards / table 等 -->
      </div>
    </div>
  </main>
</div>
```

### 占位页（空数据状态）

```html
<div class="placeholder-page">
  <div class="ph-title">还没有数据</div>
  <div class="ph-desc">绑定第一个许可证后，这里会展示绑定列表。</div>
</div>
```

### 流程指示器

```html
<div class="flow-steps">
  <div class="flow-step current">1. 选品</div>
  <span class="flow-arrow">›</span>
  <div class="flow-step">2. 文案</div>
  <span class="flow-arrow">›</span>
  <div class="flow-step">3. 发布</div>
</div>
```

## 四、布局栅格速查

```css
/* Stat cards grid */
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;

/* Form 自动多列 */
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;

/* Settings 紧凑双列（>1024px） */
grid-template-columns: 1fr 1fr; gap: 16px;

/* Account info 双列文本 */
grid-template-columns: 1fr 1fr; gap: 10px 20px;

/* AI 供应商双列（>1024px） */
grid-template-columns: 1fr 1fr; gap: 32px;

/* 修改密码 3 栏内联 */
grid-template-columns: 1fr 1fr 1fr; gap: 12px;
```

响应式断点：
- `≤1024px` → AI 供应商 / 双列降为单列
- `≤768px` → 所有 settings-two-col / chpw-form-inline 全部降为单列

## 五、新增页面 Recipe

新增一页（如 `calculator` / `shipping-rates` / `prompt-templates`）的标准流程：

1. **HTML 页面骨架**（在 `user-panel.html` 或 `admin.html` 内）：

```html
<div class="page" id="page-calculator">
  <div class="page-header">
    <h2 class="page-title">利润计算器</h2>
    <div><button class="btn btn-secondary">导出 CSV</button></div>
  </div>

  <!-- 工具栏 -->
  <div class="toolbar">
    <select id="calc-mode"><option>加价模式</option><option>毛利模式</option></select>
  </div>

  <!-- 主体：双列玻璃化 -->
  <div class="settings-two-col">
    <div class="glass-panel">
      <h3>输入</h3>
      <div class="settings-section">
        <div class="settings-row"><label>采购价 ¥</label><input type="number" id="calc-cost"></div>
        <div class="settings-row"><label>运费 ¥</label><input type="number" id="calc-shipping"></div>
      </div>
    </div>
    <div class="glass-panel">
      <h3>结果</h3>
      <div class="settings-row"><label>售价 ¥</label><span class="info-text" id="calc-price">—</span></div>
      <div class="settings-row"><label>毛利率</label><span class="info-text" id="calc-margin">—</span></div>
    </div>
  </div>
</div>
```

2. **侧边栏导航**：在 `sidebar-nav` 加 `<div class="sidebar-item" data-page="calculator">...</div>`
3. **路由表**：在 `pages` 数组加 `'calculator'`，`titleMap` 加 `calculator: '利润计算器'`
4. **JS 逻辑**：单独写 `assets/js/user/calculator.js`，挂在 `loadCalculator()` 函数
5. **i18n**：三语 `<span data-i18n="calc.label.cost">采购价</span>`，三份字典都加
6. **权限**：admin 专属页加 `class="admin-only"`，body 上 `class="role-admin"` 时才显示

## 六、Don'ts（硬性禁止项）

- ❌ 硬编码颜色：`color: #1a1a1a` → ✅ `color: var(--jsop-text-primary)`
- ❌ 自定义间距：`padding: 13px 17px` → ✅ `padding: var(--jsop-sp-3) var(--jsop-sp-4)`
- ❌ 自定义阴影：`box-shadow: 0 5px 12px rgba(0,0,0,.15)` → ✅ `var(--jsop-shadow-md)`
- ❌ 在 `.glass-panel` 内再叠 background-image / box-shadow 装饰
- ❌ 用 success / warning 色当装饰（如绿色 hero 按钮）
- ❌ 引入新色板（purple / teal）— 数据可视化用 `--jsop-chart-1..4`
- ❌ 写 999 / 9999 z-index — 用 `--jsop-z-*` 系列
- ❌ 内联 `<style>` 写 component 级样式 — 抽到 `components.css` / 模块 CSS
- ❌ 仅写 light 不写 dark 的新令牌 — 必须双主题对齐
- ❌ 用第三方 UI 库（Bootstrap / Material UI / AntD）覆盖现有面板风格

## 七、参考文件

| 文件 | 作用 |
|---|---|
| `j-sop-license-server/ui/assets/css/tokens.css` | **唯一真源**：所有令牌定义（深浅双主题） |
| `j-sop-license-server/ui/assets/css/base.css` | 全局 reset（box-sizing / margin / padding） |
| `j-sop-license-server/ui/assets/css/layout.css` | sidebar / topbar / page-content 框架 |
| `j-sop-license-server/ui/assets/css/components.css` | glass-panel / table / btn / form / modal / toast / pagination |
| `j-sop-license-server/ui/assets/css/admin.css` | admin 专用样式覆盖 |
| `j-sop-license-server/ui/assets/css/user-panel.css` | user-panel 专用样式覆盖 |
| `j-sop-license-server/ui/assets/css/index.css` | 登录页玻璃化 |
| `j-sop-license-server/ui/assets/icons/sprite.svg` | SVG 图标雪碧（`<use href="/assets/icons/sprite.svg#i-home">`） |
| `j-sop-extension/src/styles/tokens.css` | 扩展端令牌副本（与 license-server 主同步） |

## 八、一句话总结

> **1 主色 + 3 状态色 + 4 文字 + 4 底色 + 4px 栅格 + 玻璃面板**。永远 `var(--jsop-*)`，永远双主题，永远响应式。
