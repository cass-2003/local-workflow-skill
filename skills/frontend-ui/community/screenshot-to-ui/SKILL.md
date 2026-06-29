---
name: screenshot-to-ui
description: 看图、截图、复刻、还原、设计稿、Figma、1:1、按图写代码的截图到 UI 实现技能。
---

# 截图/设计稿转 UI

> 首次自称：截图/设计稿转 UI（screenshot-to-ui，兼容 slug: i2u）。
> 命名口径：frontmatter name 使用 manifest canonical name `screenshot-to-ui`；目录名和 URL 继续兼容 slug `i2u`；自检不得要求 name 等于短 slug。

定位：把截图、设计稿、Figma 导出图、竞品截图、手绘稿或参考图快速转成可实现 UI。默认流程是识别 → layout DSL → 直接实现 → 截图复验；不把日常看图写代码变成冗长审计。

## 工作方式

- 先识别画布、区域、组件、文本、颜色、间距、圆角、阴影、图标、图片和状态。
- 立即输出 layout DSL，然后继续输出 HTML/JSX/CSS/组件代码；不要在 DSL 后停顿等确认。
- 证据不足不阻塞：标 `confidence: low` 或 `assumption:`，继续做可用近似。
- 用户说 1:1、像素级、完全还原时，更忠实于原图；用户说参考、照着风格做时，可按现有组件和 a11y 做合理工程化。
- 用户没有明确 1:1 时，默认执行“结构忠实、视觉降噪”：保留布局、信息层级、组件关系和文案，把过多颜色、深色大侧栏、彩色图标块、强阴影、渐变和装饰降成浅色极简。
- 如果参考图来自 AI 生图且显得花哨，先把它当 layout reference，不把它的彩色审美当品牌事实；默认转成中性灰 + 1 个主操作色 + 小面积状态 badge。
- 竞品和未授权素材只参考结构、比例和交互，不复制商标、图片、付费字体、插画或专有资产。
- 如果原图本身低对比、不可访问或内容不可读，给忠实还原版本时同时标风险和可访问替代。

## 样板：截图复刻 layout DSL

模型看到截图后直接输出这种 DSL，再直接出代码，不再先写 brief：

    canvas: { w: 390, h: 844, dpr: 3 }
    shell: vstack(gap=0)
      - region: header height=44 align=center
          content: text "订单详情" weight=600 size=17
          leading: icon "back" size=24
      - region: card-list padding=16 gap=12 grow=1 scroll=y
          repeat: order-card
      - region: footer height=64 padding=16 sticky=bottom
          content: button "立即支付" variant=primary block=true

    components:
      order-card:
        layout: vstack(gap=8) padding=16 radius=12 bg=surface border=subtle
        rows:
          - hstack: [text "#A12831" weight=500, spacer, badge "已支付" tone=success]
          - hstack: [text "2026-05-23 09:21" tone=muted size=13]
          - hstack: [spacer, text "¥1,280" weight=600 size=20 tabular]

约束：DSL 输出后不停顿、立即继续输出 HTML/JSX 代码。证据不足不再阻塞，标 `confidence: low` 继续做。

## 识别规则

- canvas：记录宽、高、DPR、设备感、状态栏/浏览器栏是否包含。
- shell：识别页面大骨架，如 header、sidebar、main、footer、tabbar、modal、drawer、toolbar。
- regions：按视觉区域输出尺寸、padding、gap、滚动、吸顶、固定和层级。
- components：识别按钮、输入框、卡片、列表、表格、tabs、badge、toast、empty、avatar、image、icon。
- tokens：采样主色、灰阶、状态色、背景、边框、文字、圆角、阴影和字体大小。
- color budget：记录图中颜色数量；非 1:1 任务超过 3 个主导色系时，输出 `normalization: light-minimal`，把状态色限制到小 badge。
- text：OCR 不确定时保留可读片段；不可读文字用 `[unreadable]`，不要编造产品文案。
- assets：可用图标库替代的图标直接替代；品牌图、人物图、插画和截图裁片标授权风险。
- states：截图只证明当前状态；hover、focus、loading、empty、error、disabled、selected 等按工程补齐。

## DSL 到代码

- 先映射项目组件；没有项目组件时用 shadcn 风 class 组合实现最小可维护版本。
- 布局用 flex/grid、固定区、滚动区、min/max、aspect-ratio 和 safe-area 表达，不靠绝对定位堆满屏。
- 文本使用真实可见内容；不可见或不确定内容用业务中性占位，并标注可替换。
- 字重按截图和场景决定；营销大标题可 700-800，移动常规 title 多用 600，正文 400-500。
- 图片区域给明确尺寸、object-fit、圆角和 fallback；不要让图片加载失败撑破布局。
- 颜色优先映射到 token：surface、text.primary、text.muted、border.subtle、accent、success、warning、danger。
- 后台/工作台/管理页默认浅色系：画布 #f8fafc、surface #fff、border #e4e4e7、text #18181b；主操作色只用于按钮/链接/当前项，状态色只用于 badge。
- 忠实还原不牺牲基础 a11y：按钮、输入框、导航、弹层仍要有语义、焦点和键盘路径。

## 参考实现片段

    <section class="min-h-screen bg-zinc-50 text-zinc-900">
      <header class="h-11 px-4 flex items-center justify-center border-b border-zinc-200 bg-white">
        <button class="absolute left-3 size-10 inline-flex items-center justify-center rounded-md hover:bg-zinc-100" aria-label="返回">
          <span class="text-xl">‹</span>
        </button>
        <h1 class="text-[17px] font-semibold">订单详情</h1>
      </header>
      <main class="p-4 space-y-3 pb-24">
        <article class="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
          <div class="flex items-center gap-3">
            <p class="text-sm font-medium">#A12831</p>
            <span class="ml-auto rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">已支付</span>
          </div>
          <p class="mt-2 text-[13px] text-zinc-500">2026-05-23 09:21</p>
          <p class="mt-3 text-right text-xl font-semibold tabular-nums">¥1,280</p>
        </article>
      </main>
      <footer class="fixed inset-x-0 bottom-0 bg-white/95 p-4 border-t border-zinc-200">
        <button class="h-11 w-full rounded-md bg-zinc-900 text-white text-sm font-medium hover:bg-zinc-800">立即支付</button>
      </footer>
    </section>

## 复验

- 同 viewport 截图，对比区域位置、文本折行、颜色、间距、圆角、阴影、图标和遗漏元素。
- 移动图检查安全区、底部操作、软键盘、长文本；桌面图检查最大宽、滚动区和宽屏留白。
- 每轮只修证据命中的差异，不整屏重写。
- 如果缺字体、资产、Figma、DOM 或原始高清图，继续交付近似版本，并说明哪些差异需要补证据才能收窄。
- 自检：本文件保持 DSL → 实现；没有要求先产出多张表；没有真实密钥、客户数据或未授权资产路径。