---
name: design-system-implementation
description: "设计系统工程落地。覆盖 design tokens、组件 API、可访问性、主题切换、视觉回归、Figma 到代码、CSS variables、Tailwind/shadcn 集成、组件文档、版本治理。当用户提到 design system、设计系统、组件库、tokens、主题、暗色模式、Figma 落地、storybook、视觉回归、组件 API、前端 UI 规范时使用。"
---

# Design System Implementation

## Core Goal

Turn visual direction into a reusable UI system that can survive real product changes. Do not stop at a pretty component; create tokens, component contracts, documentation, tests, and migration notes.

## Workflow

1. Audit existing UI primitives, brand direction, accessibility needs, and framework constraints.
2. Define tokens before components: color, typography, spacing, radii, shadows, motion, z-index, and breakpoints.
3. Build primitive components before composites.
4. Give every component a clear API: variants, sizes, states, slots, accessibility labels, and escape hatches.
5. Validate with keyboard navigation, screen readers where possible, responsive states, and visual regression.
6. Document usage, anti-patterns, migration steps, and versioning policy.

## Token Layers

Use three token layers:

- `core`: raw scales such as `blue-500`, `space-4`, `font-size-3`.
- `semantic`: product meaning such as `color-surface`, `color-danger`, `space-card`.
- `component`: local mappings such as `button-bg-primary`, `dialog-backdrop`.

Prefer semantic tokens in application code. Raw tokens should stay in system internals.

## Component Contract

For each component, define:

- Purpose: one sentence that explains when to use it.
- Anatomy: root, slots, optional regions, icon positions.
- Variants: visual intent, not implementation detail.
- States: hover, focus, active, disabled, loading, selected, invalid, empty.
- Accessibility: role, label, keyboard behavior, focus management.
- Composition rules: what can be nested, what should not be nested.
- Data contract: controlled/uncontrolled values, async loading shape, error shape.

## Iconography Rules

- Do not use emoji as production UI icons, navigation items, status markers, toolbar controls, or empty-state artwork.
- Prefer the project's existing SVG/vector icon component system.
- If the project has no icon system, choose one coherent vector set such as Lucide, Tabler, Heroicons, Phosphor, Fluent Icons, or the platform-native equivalent.
- Keep icons consistent in stroke/fill style, optical size, line cap, corner radius, color tokens, alignment, and hit target.
- Pair unfamiliar icon-only controls with accessible labels, tooltips, or visible text.
- Avoid importing a whole icon package when tree-shaken single-icon imports or local SVG components are available.

## Implementation Checklist

- Use CSS variables for themeable values.
- Keep variants finite; avoid arbitrary prop soup.
- Expose composition slots instead of one-off boolean props when layouts vary.
- Use a consistent vector icon system; never use emoji as formal UI iconography.
- Ensure focus rings are visible and not removed by reset CSS.
- Ensure disabled controls still communicate why action is unavailable when needed.
- Support RTL with logical properties when layout direction may change.
- Avoid color-only status communication; include text or iconography.
- Keep motion purposeful and respect `prefers-reduced-motion`.
- Add visual regression stories for critical states.
- Add examples for dense data, long text, empty state, error state, and mobile.

## Component API Pattern

```tsx
type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  leadingIcon?: React.ReactNode
  trailingIcon?: React.ReactNode
  children: React.ReactNode
}
```

Prefer meaning-based variants. Avoid names like `blue`, `leftIconButton2`, or `homepageSpecial`.

## Documentation Template

```md
## ComponentName

Use when:
- ...

Do not use when:
- ...

API:
- `variant`
- `size`
- `disabled`

Accessibility:
- Role:
- Keyboard:
- Focus:

Examples:
- Default
- Loading
- Error
- Mobile
```

## Review Red Flags

- Components hard-code colors instead of semantic tokens.
- Variant names are page-specific.
- Design tokens exist but product code bypasses them.
- Storybook examples only show happy paths.
- Component docs do not mention accessibility.
- Dark mode is implemented by duplicating whole stylesheets.
- `!important` is used to fight the system.
- Figma tokens and code tokens drift without a mapping table.

## Validation

- Run typecheck and UI tests if available.
- Run accessibility checks on interactive components.
- Capture screenshots or visual diffs for major variants.
- Manually tab through dialogs, menus, forms, popovers, and navigation.
- Confirm token changes update multiple components without one-off overrides.
