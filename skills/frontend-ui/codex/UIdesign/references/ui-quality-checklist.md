# UI Quality Checklist

Use this file for substantial UI implementation, redesign, or review work.

## 1. Product Fit

- User and primary job are explicit.
- First screen supports the primary job directly.
- Navigation matches workflow frequency.
- Density matches domain: operational tools are compact; editorial/brand pages may breathe more.
- Copy names objects and actions clearly.

## 2. System Fit

- Existing theme/tokens/components were inspected.
- New colors, spacing, typography, radius, shadows, icons, and animation fit the existing system.
- No unnecessary dependency was added.
- Components expose variants/states rather than one-off style forks.
- Repeated UI uses reusable components when repetition is meaningful.
- Production icons use a consistent SVG/vector icon library or existing icon component system; emoji are not used as UI icons, controls, status markers, or empty-state artwork.

## 3. Layout

- Layout has stable constraints: max widths, min widths, aspect ratios, grid tracks, overflow rules.
- Text fits in buttons, tabs, cards, table cells, sidebars, and panels.
- Primary action is visible without crowding secondary actions.
- Touch/click targets are large enough.
- No cards inside cards unless they are actual nested repeated content with clear hierarchy.

## 4. States

- Primary populated state.
- Empty state.
- Loading/skeleton state where async data exists.
- Error and retry state.
- Disabled/unavailable state.
- Hover, active, selected, and focus states.
- Long-content, missing-image, and small-screen states.

## 5. Accessibility

- Semantic landmarks, headings, buttons, links, forms, labels, and tables are appropriate.
- Keyboard navigation reaches every interactive element in logical order.
- Focus indicator is visible and not clipped.
- Color contrast is readable.
- Icons used as controls have accessible names or tooltips.
- Motion respects reduced-motion preferences.
- Charts do not rely on color alone and include labels/units.

## 6. Visual Polish

- Type scale is purposeful and not viewport-width-driven.
- Letter spacing is normal unless the existing system intentionally says otherwise.
- Palette is not dominated by one hue family unless it is a deliberate brand requirement.
- Icons share stroke weight and optical size.
- Icons are not emoji stand-ins; they come from one coherent vector set and align to the system's size, stroke/fill, color, and accessibility rules.
- Images are relevant and not dark/blurred/cropped when users need to inspect the subject.
- Motion clarifies state changes and does not slow repeated work.

## 7. Verification

- Run available static checks: typecheck, lint, build, tests.
- Run the app or component environment.
- Inspect at desktop and mobile viewports.
- Check browser console for errors.
- Confirm assets load.
- Confirm text does not overlap or clip.
- For canvas/WebGL, check nonblank pixels and framing.
- For forms/tools, exercise at least one primary interaction path.

## Review Output Format

For review-only tasks, report:

1. Findings first, ordered by severity.
2. Exact file and line references.
3. Why each issue affects a real user or workflow.
4. Test/verification gaps.
5. Brief summary only after findings.

