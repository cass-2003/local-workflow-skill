# Research Synthesis

This synthesis is based on a May 2026 review of 40 GitHub repositories and 12 design/UI resources listed in `source-inventory.md`.

## What Top Repositories Converge On

1. **Component systems win when they separate behavior from styling.** Radix UI, Headless UI, Ariakit, React Aria, and Floating UI show that robust behavior, positioning, keyboard support, and ARIA semantics should be solved before visual skinning.
2. **Design tokens are the shared language between design and code.** Style Dictionary, Tokens Studio, Polaris, Carbon, Fluent, Material, and Primer all point toward named colors, spacing, typography, radius, shadows, and motion values rather than ad hoc CSS.
3. **Modern UI work is component-driven.** Storybook's popularity and most design-system repos show that UI should be developed, documented, and tested in isolated states as well as in full screens.
4. **Accessibility is built into primitives, not patched later.** Chakra UI, React Spectrum, Radix, Headless UI, Ariakit, axe-core, and WAI-ARIA-oriented docs all make accessibility a component contract.
5. **Framework choice matters less than consistency.** React, Vue, Angular, and Svelte ecosystems all have mature options; the correct choice inside an existing repo is usually the one already present.
6. **Agent-friendly design context is emerging.** `google-labs-code/design.md` formalizes visual identity for coding agents. Agents should read it when present and create a compact design brief when absent.
7. **Visual verification is part of implementation.** Playwright, Storybook, and axe-core reinforce that UI quality requires browser checks, screenshots, and automated testing where possible.
8. **Icons and motion need systems.** Lucide, Tabler Icons, and Motion show that consistent icon geometry and purposeful animation improve polish without requiring custom art each time.
9. **Data visualization needs semantic choices.** D3, Chart.js, and Recharts suggest choosing chart types, scales, legends, units, labels, and color accessibility deliberately, not decorating data.
10. **Enterprise systems value density and predictability.** Ant Design, Blueprint, Carbon, Fluent, Polaris, and Primer favor reliable navigation, tables, forms, filters, commands, and repeatable workflows over flashy composition.

## Design Workflow Pattern For Agents

Use a sequential pipeline:

1. **Understand the job.** Who uses this and what must they accomplish in the first minute?
2. **Extract the system.** Read existing components, tokens, layout, routes, and brand artifacts.
3. **Choose the product pattern.** SaaS/dashboard/editor/marketing/game each has different defaults.
4. **Specify states before coding.** Primary, empty, loading, error, disabled, focus, hover, overflow, and responsive states.
5. **Implement with local primitives.** Prefer existing components and libraries already in the repo.
6. **Verify in browser.** Screenshots catch what typecheck cannot: overlap, clipping, broken assets, poor hierarchy, and blank canvases.
7. **Report only what matters.** Changed files, verification, URL/path, known risk.

## Product Pattern Notes

### SaaS / Admin / CRM / Ops

- Prioritize scanability, density, stable navigation, filters, tables, forms, batch actions, and clear status.
- Avoid oversized hero sections, decorative card grids, vague illustration, and sparse marketing rhythm.
- Use subdued backgrounds with enough contrast between work surfaces, controls, and selected rows.

### Dashboard / Analytics

- Put filters and time range close to the data they control.
- Label units and baselines directly.
- Include empty states and explain unavailable data.
- Use color for meaning sparingly; never rely on color alone.

### Consumer / Landing / Brand

- Make the product/place/person/offer visible in the first viewport.
- Use real or generated bitmap imagery when visual inspection matters.
- Keep the next section hinted below the fold.
- Do not put the hero text inside a decorative card unless the design system demands it.

### Editor / Tool

- Start in the workspace, not an intro page.
- Prefer icon buttons for tool commands and pair unfamiliar icons with tooltips.
- Stabilize toolbars and canvases with fixed dimensions, min/max sizes, and overflow rules.
- Preserve undo/redo, selection, preview, export, and keyboard flows when relevant.

### Component Library / Design System

- Define tokens, variants, states, accessibility behavior, and examples.
- Prefer unstyled/headless primitives for reusable behavior when the app has a strong custom brand.
- Include usage examples and anti-examples where misuse is likely.

## Common Agent Failure Modes

| Failure | Better behavior |
|---|---|
| Adds a generic landing page for an app/tool request | Build the actual working interface as the first screen. |
| Invents a new visual language in an existing app | Extract and extend existing tokens/components first. |
| Makes a pretty static mock with dead controls | Implement controls, states, navigation, and feedback. |
| Uses oversized text inside compact panels | Match type scale to container and information density. |
| Creates nested cards and heavy decoration | Use full-width sections or unframed layouts; reserve cards for repeated items/modals/tools. |
| Ignores long text and mobile widths | Test realistic long labels, narrow screens, and overflow. |
| Claims success after build only | Run browser/screenshot verification for UI work. |

