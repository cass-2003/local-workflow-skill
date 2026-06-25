---
name: UIdesign
description: UI design and frontend implementation workflow for Claude Code and Codex. Use this skill whenever the user asks to design, redesign, polish, modernize, improve, implement, or review a web/app UI, dashboard screen, SaaS screen, admin panel, design system, component library, visual style, responsive layout, accessibility, interaction states, icons, design tokens, screenshots, or frontend UX. Chinese triggers include UI 设计、前端视觉、截图还原、页面重做、视觉优化、交互状态、响应式、可访问性、移动端适配、SaaS 页面和后台页面. Especially use it for UI-only or UI-dominant tasks where the model must turn vague product intent into a coherent, usable interface and verify it visually. If the request is mainly full-stack, API, database, auth, RAG/Agent, or multi-module delivery, use dev as the main workflow and apply this skill only to the UI portion.
---

# UI Design Workflow

Use this skill to turn a UI request into a coherent, implemented, and visually verified interface. It is optimized for Claude Code and Codex working inside real codebases, where the agent must infer constraints, use existing design systems, make conservative product decisions, and validate the result in a browser or screenshot.

## Essential Principles

1. **Design from the user's job, not decoration.** Identify the primary user, their task, and the density they need before choosing layout, tone, or visual expression.
2. **Use the project's system before inventing one.** Existing components, tokens, spacing, typography, icons, routes, and copy patterns are the source of truth unless they are broken or absent.
3. **Make the first screen useful.** Apps and tools should open directly into the working experience; marketing-style landing pages belong only when the user explicitly asks for one.
4. **Treat accessibility as structure.** Keyboard flow, focus states, contrast, semantic labels, target sizes, and reduced-motion behavior shape the UI, not a final lint pass.
5. **Design every state.** Empty, loading, error, disabled, active, hover, focus, overflow, small-screen, and long-content states are part of the component contract.
6. **Verify visually before claiming success.** Run the app, inspect the UI at relevant desktop and mobile viewports, and fix obvious overlap, blank areas, clipping, broken assets, and unreadable text.

## When To Use

- Building or redesigning a frontend screen, dashboard, app, internal tool, SaaS view, landing page, or game-like interface.
- Creating or extending a component library, design system, tokens, theme, icon system, or reusable UI pattern.
- Improving UI polish, layout, hierarchy, responsive behavior, accessibility, visual consistency, or interaction quality.
- Translating a screenshot, mockup, product description, `DESIGN.md`, brand guide, or vague "make this look better" request into code.
- Reviewing a UI implementation for design risks before handoff.
- Acting as the UI quality pass inside a larger `dev` workflow.

## When Not To Use

- Pure backend work with no user-visible interface.
- Full-stack features where backend/API/database/auth/RAG/Agent work is the main complexity; use `dev` as the main workflow.
- Tiny copy edits or one-line style fixes where the surrounding UI does not need analysis.
- Security/code reviews where the user wants bug findings first; use the host review behavior.
- Destructive production changes, publishing, payments, credentials, or external account actions; ask for confirmation first.

## Skill Routing

Choose the workflow by the center of gravity:

| User intent | Use |
|---|---|
| UI quality, visual design, responsive behavior, screenshots, accessibility, frontend UX | `UIdesign` |
| End-to-end feature with backend/API/database/auth/jobs/RAG/Agent pieces | `dev` |
| Full-stack feature with important UI | `dev` owns the full workflow; use `UIdesign` for the UI module and visual verification. |

## Workflow

### Phase 1: Intake And Context

**Entry:** The user has requested UI design, UI implementation, redesign, polish, or review.

**Actions:**
1. Inspect the existing app structure before designing: routes/pages, components, styling setup, package scripts, assets, icons, and tests.
2. Look for design context in `README*`, `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, Storybook config, theme files, token files, CSS variables, Tailwind config, component docs, screenshots, and existing UI.
3. Identify the product type and target workflow: SaaS/admin, consumer content, ecommerce, portfolio/brand, data visualization, editor/tool, game, or docs.
4. Define a compact need package: user, primary job, first-screen goal, key actions, data/states, visual tone, constraints, and assumptions.
5. Ask only when a missing decision changes the product direction, brand, production risk, paid resource, or destructive action.

**Exit:** You can state the UI's user, purpose, constraints, existing design system, and assumptions in 5-8 bullets.

### Phase 2: Pattern And System Selection

**Entry:** Phase 1 exit criteria are met.

**Actions:**
1. Choose the nearest existing UI pattern from the codebase; if none exists, use the product-type defaults below.
2. Select the styling route that matches the project: existing design system, component library, Tailwind/utilities, CSS modules, CSS-in-JS, or plain CSS.
3. Define the UI contract: layout grid, navigation, primary actions, information hierarchy, component inventory, state model, responsive behavior, and accessibility requirements.
4. For substantial work, sketch a short implementation plan and list likely changed files before editing.
5. Reject visual gimmicks that do not serve the user's job: decorative cards inside cards, one-note palettes, unreadable hero type, arbitrary gradients, and vague stock-like media.

**Exit:** The design direction is specific enough to implement without inventing major decisions mid-code.

### Phase 3: Implement The Interface

**Entry:** Phase 2 exit criteria are met.

**Actions:**
1. Reuse local components, tokens, utilities, icon libraries, and data-fetching patterns before adding dependencies.
2. Build the complete workflow, not just a pretty static shell: controls, navigation, validation, feedback, empty/loading/error states, and realistic content.
3. Keep layout dimensions stable with explicit constraints for fixed-format UI such as boards, tables, toolbars, cards, panels, charts, media, and icon buttons.
4. Use semantic HTML and accessible component APIs. Preserve keyboard navigation, labels, focus indicators, hit targets, and reduced-motion options.
5. Use visual assets when the domain needs inspection or atmosphere. Prefer real/product/place/person media or existing assets; use generated or custom assets only when appropriate.
6. Keep changes scoped. Do not refactor unrelated modules or replace the project's design language unless the user requested a redesign.

**Exit:** The UI is implemented in code with all primary states and responsive behavior represented.

### Phase 4: Visual And Functional Verification

**Entry:** Phase 3 exit criteria are met.

**Actions:**
1. Run available checks: typecheck, lint, unit tests, build, Storybook, or focused component tests as appropriate.
2. Start the local dev server when needed. If the UI can run as a static HTML file, provide that path instead of starting a server.
3. Verify visually in a browser or screenshot at minimum one desktop and one mobile viewport. For dense tools, also test a narrow tablet or constrained panel width.
4. Check for: blank render, console errors, broken assets, overlap, clipped text, unreadable contrast, layout shift, inaccessible focus order, unusable controls, and missing states.
5. For canvas/WebGL/Three.js work, verify pixels are nonblank and the scene is framed, animated/interactive when expected, and not hidden behind overlays.
6. Fix issues and re-run the relevant verification. If the same approach fails twice, change strategy and record the reason.

**Exit:** Verification results are known and any remaining risk is explicit.

### Phase 5: Handoff

**Entry:** The UI has been implemented or reviewed and verification is complete or blocked for a stated reason.

**Actions:**
1. Summarize the user-visible result, changed files, verification commands, browser URL or static file path, and known limitations.
2. For review-only tasks, lead with findings ordered by severity and include exact file/line references.
3. Keep the final answer short. Do not describe every design decision unless the user asked for rationale.

**Exit:** The user knows what changed, how it was verified, and what remains.

## Product-Type Defaults

| Product type | Default UI direction |
|---|---|
| SaaS, CRM, admin, ops | Dense, calm, scan-first, predictable navigation, strong tables/forms, restrained decoration. |
| Analytics/dashboard | Clear hierarchy, filters near data, explain empty/error states, accessible charts, legends and units. |
| Consumer/product site | Strong first-viewport signal, real imagery, concise value prop, visible next section, responsive conversion path. |
| Editor/tool | Workspace-first, stable toolbars, icon controls with tooltips, keyboard-friendly flows, no marketing shell. |
| Design system/components | Tokens, variants, docs/examples, accessibility notes, visual regression path. |
| Game/interactive | Use game-appropriate visuals, animation, feedback, and proven engines for rules/physics where relevant. |

## Quick Checks

Before finishing, confirm:

- [ ] Existing design system or styling conventions were inspected.
- [ ] The first screen supports the user's main task.
- [ ] Primary, empty, loading, error, disabled, hover/focus, and small-screen states are handled where relevant.
- [ ] Text does not overflow or overlap at tested viewports.
- [ ] Icons, images, charts, and media render correctly.
- [ ] Keyboard/focus/labels/contrast are acceptable for the changed UI.
- [ ] Verification commands and browser/screenshot checks were actually run, or blockers are stated.

## Reference Index

| File | Use |
|---|---|
| [references/research-synthesis.md](references/research-synthesis.md) | Lessons distilled from 40 repositories and 12 UI/design resources. |
| [references/ui-quality-checklist.md](references/ui-quality-checklist.md) | Detailed implementation and review checklist. |
| [references/source-inventory.md](references/source-inventory.md) | Source inventory with repository and article URLs. |
| [templates/design-brief.md](templates/design-brief.md) | Optional compact brief for substantial UI work. |
