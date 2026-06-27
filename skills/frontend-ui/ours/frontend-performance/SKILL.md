---
name: frontend-performance
description: "前端性能优化。覆盖 Core Web Vitals、LCP/INP/CLS、bundle 分析、代码分割、图片与字体优化、渲染性能、hydration、prefetch/preload、虚拟列表、性能预算、RUM 与 Lighthouse。当用户提到前端性能、页面慢、首屏、LCP、INP、CLS、bundle 太大、hydration、图片优化、字体优化、Lighthouse、Core Web Vitals 时使用。"
---

# Frontend Performance

## Performance Model

Optimize with evidence. Measure first, identify the bottleneck, then apply the smallest fix.

Primary metrics:

- LCP: largest contentful paint, usually hero text/image or main content.
- INP: responsiveness to user interactions.
- CLS: layout stability.
- TTFB: server and edge response latency.
- JS cost: parse, compile, execute, hydrate.

## Workflow

1. Establish baseline with field data if available, otherwise Lighthouse/WebPageTest plus browser Performance panel.
2. Identify page type: content page, dashboard, app shell, checkout, editor, or realtime UI.
3. Find the dominant bottleneck: network, server, JavaScript, render, image, font, third-party, or data waterfall.
4. Set a performance budget.
5. Apply targeted fixes.
6. Re-measure under throttled CPU/network and on mobile viewport.
7. Add regression guardrails in CI where possible.

## Fast Wins

- Compress and resize hero images; serve AVIF/WebP with correct dimensions.
- Preload only the true LCP asset.
- Use `font-display: swap` or `optional`; subset fonts.
- Remove unused third-party scripts.
- Split heavy routes and admin-only tools.
- Defer non-critical analytics.
- Avoid hydration for static islands when the framework supports it.
- Replace layout-thrashing animations with transform/opacity.
- Virtualize long lists.
- Cache API responses and eliminate duplicate requests.

## Bundle Discipline

- Analyze production bundles, not development builds.
- Watch for accidental imports of full icon packs, date libraries, charting libraries, editors, and SDKs.
- Prefer route-level splitting before micro-splitting.
- Avoid shipping server-only utilities to the client.
- Check tree-shaking by inspecting output, not by assuming ESM is enough.

## Rendering Discipline

- Keep expensive calculations out of render paths.
- Avoid state updates during layout effects unless necessary.
- Prevent cascading re-renders from app-shell global state.
- Memoize only after proving render cost; do not cargo-cult memoization.
- Use virtual scrolling for lists that exceed the DOM comfort zone.
- Avoid measuring layout in loops; batch reads before writes.

## Image And Font Rules

- Always set width and height or aspect ratio for images.
- Use responsive `srcset` or framework image components.
- Do not lazy-load the LCP image.
- Lazy-load below-the-fold media.
- Preconnect only to origins actually used early.
- Subset fonts and avoid loading many weights.

## Performance Budget Example

```md
Page: marketing homepage
- LCP p75 mobile: <= 2.5s
- INP p75: <= 200ms
- CLS p75: <= 0.1
- Initial JS gzip: <= 180KB
- Third-party blocking scripts: 0
```

## Review Red Flags

- Lighthouse is green locally but field data is bad.
- LCP image is lazy-loaded.
- Layout shifts because image or ad slots lack dimensions.
- A dashboard fetches data serially when requests can run in parallel.
- Hydration loads a full app for static content.
- Global provider updates re-render the entire page.
- Performance fixes are not re-measured.

## Validation

- Capture before/after metrics.
- Test mobile CPU throttling.
- Inspect network waterfall for blocked or duplicate requests.
- Inspect main thread tasks longer than 50ms.
- Confirm no new layout shifts during loading, auth transitions, or async data replacement.

