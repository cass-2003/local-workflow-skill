---
name: css-modern-2025
description: "现代 CSS 2025 实战。覆盖 Grid Level 2 / Subgrid、Container Queries、@scope、Cascade Layers、:has() 关系选择器、Native CSS Nesting、color-mix() / OKLCH、@property、Anchor Positioning、View Transitions API、Logical Properties、light-dark()、Scroll-driven Animations。当用户提到现代 CSS、CSS 新特性、container query、subgrid、:has、@scope、cascade layers、CSS nesting、OKLCH、view transition、anchor positioning、scroll animation 时使用。"
---

# Modern CSS 2025 Skill — 现代 CSS 实战

## 何时使用

- 项目升级到现代 CSS（不要再写 BEM + flex hack + JS resize）
- 设计系统重构（OKLCH 调色板 / cascade layers 治理）
- 评审 PR 时检查是否还在用过时模式（float / clearfix / IE hack）
- 性能优化（用 CSS 替代 JS 实现的 hover/scroll 效果）

## 一、浏览器支持现状（2025）

| 特性 | Baseline 状态 |
|---|---|
| Container Queries | ✅ Widely available 2023+ |
| `:has()` | ✅ Widely available 2023+ |
| Native Nesting | ✅ Widely available 2024+ |
| Cascade Layers `@layer` | ✅ Widely available 2022+ |
| Subgrid | ✅ Widely available 2024+ |
| `@scope` | ✅ Widely available 2024-2025（Firefox 最后跟） |
| `color-mix()` / OKLCH | ✅ Widely available 2024+ |
| Anchor Positioning | ⚠️ Chrome 125+ / Safari TP / Firefox dev — 用 `@supports` 兜底 |
| View Transitions（同源） | ✅ Chrome 111+ / Safari 18 / Firefox 在路上 |
| Scroll-driven Animations | ⚠️ Chrome 115+ / Safari TP — `@supports` 兜底 |

**用 `@supports` 包新特性，老浏览器 fallback**：

```css
.card { box-shadow: 0 1px 2px rgba(0,0,0,.1); }

@supports (container-type: inline-size) {
  .card-grid { container-type: inline-size; container-name: grid; }
}
```

## 二、Container Queries（响应组件而非屏幕）

```css
/* 在父级声明 container */
.card-list {
  container-type: inline-size;
  container-name: list;
}

/* 子元素根据父容器宽度响应 */
.card {
  display: grid;
  gap: 16px;
}

@container list (min-width: 600px) {
  .card { grid-template-columns: 1fr 2fr; }
}

@container list (min-width: 900px) {
  .card { grid-template-columns: 1fr 2fr 1fr; }
}
```

**关键点**：组件可以放在任何位置（侧栏 / 主区 / 模态），自动按所在容器宽度响应。**不再依赖 viewport media query**。

容器查询单位：`cqw / cqh / cqi / cqb / cqmin / cqmax`（替代 `vw` 用于组件级）。

## 三、`:has()` 关系选择器（"父选择器"）

```css
/* 卡片中如果有图片，标题加大间距 */
.card:has(img) .title { margin-top: 16px; }

/* form 提交按钮，仅当所有 input 有效时启用样式 */
form:has(input:invalid) button[type="submit"] { opacity: 0.5; }

/* 主区如果旁边有侧栏，自动改宽度 */
main:has(+ aside) { width: 70%; }

/* 否定：没有 image 的卡片 */
.card:not(:has(img)) { padding-top: 24px; }
```

**性能注意**：`:has()` 不是免费的。避开在大型选择器树（如 `body:has(...)` 深嵌套）使用 — 浏览器要无效化整个子树重算。

## 四、Cascade Layers（治理选择器战争）

```css
/* 显式定义层级，从下到上优先级递增 */
@layer reset, base, theme, components, utilities, overrides;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  body { margin: 0; }
}

@layer theme {
  :root {
    --color-primary: oklch(60% 0.2 250);
    --space-1: 4px;
  }
}

@layer components {
  .btn {
    background: var(--color-primary);
    /* 即使写得不那么 specific，components 层永远盖过 base */
  }
}

@layer utilities {
  .hidden { display: none !important; }
}
```

`@layer overrides` 留给业务最后兜底。**第三方库样式包在 `@layer external`** 即可永远低于自家：

```css
@import url('vendor.css') layer(external);
@layer external, base, components, utilities;
```

## 五、Native CSS Nesting（无 SASS 即可嵌套）

```css
/* 直接嵌套 */
.card {
  background: white;
  padding: 16px;

  & .title {
    font-size: 18px;
    color: var(--color-text);
  }

  & .subtitle {
    color: var(--color-text-secondary);
  }

  &:hover {
    background: var(--color-bg-hover);
  }

  /* 嵌套 media query */
  @media (max-width: 768px) {
    padding: 8px;
  }

  /* 嵌套 container query */
  @container (max-width: 600px) {
    & .title { font-size: 14px; }
  }
}
```

**注意**：CSS nesting 与 SASS 略有差异 —
- CSS nesting 中标签选择器不能直接嵌套（`p { color: red }` 在嵌套块中需要 `& p`）
- 不支持 `@at-root`
- 不支持 `&-suffix` 字符串拼接（需用 `& {}`）

## 六、Subgrid

子网格继承父网格的轨道，对齐多卡片：

```css
.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.card {
  display: grid;
  grid-template-rows: subgrid;     /* 子卡片对齐父网格的行 */
  grid-row: span 4;                 /* 占父网格 4 行 */
}
```

效果：所有卡片的 title / image / content / footer 在视觉上逐行对齐，即使内容长度不同。

## 七、`@scope`（局部样式作用域）

```css
@scope (.article) to (.comment-section) {
  /* 仅在 .article 内、且不穿过 .comment-section 应用 */
  p { line-height: 1.7; }
  a { color: var(--color-link); }
}
```

替代 BEM 的"组件命名空间"问题，**无运行时**（不像 CSS Modules）。

## 八、color-mix() + OKLCH（现代调色）

```css
:root {
  --primary: oklch(60% 0.2 250);
  --primary-hover:  color-mix(in oklch, var(--primary) 90%, black);
  --primary-active: color-mix(in oklch, var(--primary) 80%, black);
  --primary-soft:   color-mix(in oklch, var(--primary) 15%, white);
}
```

**OKLCH 优于 HSL**：
- L (lightness) 感知线性 — 50% 真的看起来一半亮
- 跨色相 lightness 一致 — `oklch(60% 0.2 250)` 和 `oklch(60% 0.2 30)` 视觉等亮
- 支持 P3 / Rec.2020 广色域

`color-mix()` 替代手写 SASS `lighten()` / `darken()`，浏览器原生。

## 九、light-dark() & 双主题

```css
:root {
  color-scheme: light dark;        /* 启用系统主题切换 + 表单原生着色 */
  --bg: light-dark(white, #1a1a1a);
  --text: light-dark(#1a1a1a, #f0f0f0);
}

body { background: var(--bg); color: var(--text); }

/* 强制切换 */
[data-theme="dark"] { color-scheme: dark; }
[data-theme="light"] { color-scheme: light; }
```

`light-dark()` 自动跟随 `color-scheme`。比 `@media (prefers-color-scheme)` 更紧凑。

## 十、Anchor Positioning（替代 popper.js）

```css
.tooltip {
  position: absolute;
  position-anchor: --my-button;
  top: anchor(bottom);
  left: anchor(center);
  translate: -50% 8px;
}

.button { anchor-name: --my-button; }
```

浏览器自动定位 tooltip 在 button 下方居中。**告别 200KB Popper.js**。

兜底：

```css
@supports (position-anchor: --x) { /* 现代实现 */ }
@supports not (position-anchor: --x) { /* JS Popper / 简单 absolute */ }
```

## 十一、View Transitions API（页面间过渡动画）

```html
<style>
  ::view-transition-old(root) { animation: fade-out 200ms; }
  ::view-transition-new(root) { animation: fade-in  200ms; }
  .hero { view-transition-name: hero; }   /* 标记跨页复用元素 */
</style>
<script>
  document.startViewTransition(() => {
    document.body.innerHTML = '...new page...'   // 路由切换
  })
</script>
```

SPA 路由切换 / List → Detail 平滑动画，浏览器自动 morph。

## 十二、Scroll-driven Animations（滚动驱动）

```css
@keyframes fade-in {
  from { opacity: 0; translate: 0 40px; }
  to   { opacity: 1; translate: 0 0; }
}

.card {
  animation: fade-in linear;
  animation-timeline: view();           /* 元素进入视口时驱动 */
  animation-range: entry 0% cover 30%;
}
```

进度条跟随页面滚动：

```css
@keyframes progress { to { width: 100%; } }
.progress-bar {
  animation: progress linear;
  animation-timeline: scroll(root);
}
```

## 十三、Logical Properties（i18n / RTL 友好）

```css
/* 不要写 */
.box { margin-left: 16px; padding-right: 8px; }

/* 写 */
.box { margin-inline-start: 16px; padding-inline-end: 8px; }
```

阿拉伯语 / 希伯来语 RTL 自动镜像，**无需 `[dir="rtl"]` 重写**。

| 物理 | 逻辑 |
|---|---|
| left/right | inline-start/end |
| top/bottom | block-start/end |
| width / height | inline-size / block-size |
| margin-left | margin-inline-start |
| border-top | border-block-start |

## 十四、Don'ts

- ❌ `float` 做布局 — 用 grid / flex
- ❌ JS resize listener 算 width — 用 container queries
- ❌ Popper.js / floating-ui 仅用 1 个 tooltip — 用 anchor positioning
- ❌ HSL 调色 — 用 OKLCH（视觉一致）
- ❌ `!important` 治理优先级 — 用 cascade layers
- ❌ BEM 命名隔离 — 用 `@scope`
- ❌ SASS 嵌套 — 现代项目用 native CSS nesting + PostCSS
- ❌ 手写 `[dir="rtl"]` 大量重写 — 用 logical properties
- ❌ 媒体查询响应组件 — 用 container queries
- ❌ 不写 `@supports` 兜底新特性 — 旧浏览器全坏

## 十五、推荐工具链

- **PostCSS** + `postcss-preset-env` — 自动 polyfill 现代特性到老浏览器
- **Lightning CSS** — 比 PostCSS 快 100x（Rust）
- **Open Props** — CSS variables 设计令牌库
- **Pico.css** / **新 simple.css** — 极简语义化样式（无 class）
- **Tailwind CSS v4** — 完全用现代 CSS（CSS Layers / @property）重写

## 十六、参考资料

- web.dev/learn/css：https://web.dev/learn/css
- MDN CSS Reference
- Baseline 状态：https://web-platform-dx.github.io/web-features/
- Modern CSS Solutions（Stephanie Eckles）：https://moderncss.dev/
- Josh Comeau 的 CSS 文章：https://www.joshwcomeau.com/css/
- CSS Tricks Almanac：https://css-tricks.com/almanac/
