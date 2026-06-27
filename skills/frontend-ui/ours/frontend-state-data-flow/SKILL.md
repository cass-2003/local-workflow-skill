---
name: frontend-state-data-flow
description: "前端状态与数据流设计。覆盖 server state vs client state、URL state、form state、cache invalidation、optimistic updates、React Query/TanStack Query、SWR、Redux/Zustand/Jotai、状态归属、并发请求、错误和加载态。当用户提到前端状态管理、数据流、缓存、乐观更新、React Query、SWR、Redux、Zustand、表单状态、URL 状态时使用。"
---

# Frontend State And Data Flow

## Core Rule

Do not choose a state library first. Classify the state first, then choose the smallest tool that preserves correctness.

## State Categories

| Category | Owner | Examples | Preferred Tool |
|---|---|---|---|
| Server state | backend/cache | user profile, lists, detail pages | TanStack Query, SWR, framework loader |
| URL state | browser URL | filters, tabs, pagination, search | route params, search params |
| Form state | form component | draft values, validation errors | form library or local state |
| UI state | component tree | modal open, selected row, hovered item | local state or small store |
| App session state | app shell | auth session, feature flags, tenant | context/store with clear source |
| Derived state | computed | totals, filtered views | derive on read, do not duplicate |

## Workflow

1. Inventory state and assign ownership.
2. Move shareable navigation state into the URL.
3. Put remote data in a server-state cache with invalidation rules.
4. Keep ephemeral UI state local until proven shared.
5. Avoid duplicating server state into global stores.
6. Define loading, empty, error, stale, and offline behavior.
7. Add optimistic updates only when rollback rules are clear.

## Server State Rules

- Cache by stable query keys.
- Invalidate by domain event, not by random component location.
- Use stale time deliberately; do not rely on defaults blindly.
- Keep mutation side effects near the mutation.
- Always handle retry, cancellation, and race conditions for critical screens.
- Prefer optimistic updates for reversible operations only.
- Prefer pessimistic confirmation for payment, destructive, or compliance actions.

## URL State Rules

Put these in the URL:

- Search query
- Filters
- Sort
- Pagination
- Selected tab when linkable
- View mode when it changes shared context

Do not put these in the URL:

- Open tooltip
- Draft password
- Transient hover state
- Large JSON blobs

## Form State Rules

- Keep draft form data close to the form.
- Validate at field level for quick feedback and at submit level for business rules.
- Preserve dirty state across route changes only when the product expects drafts.
- Separate client validation errors from server validation errors.
- Prevent duplicate submit with idempotency or disabled pending state.

## Global Store Rules

Use a global store only when at least one is true:

- Many distant components need the same client-owned state.
- State must survive route transitions.
- State has actions and invariants that benefit from a central reducer.
- Devtools/time-travel/debugging materially helps.

Avoid global stores for data already owned by the server cache.

## Loading And Error Contract

Every data surface should define:

- Initial loading
- Background refresh
- Empty result
- Partial failure
- Permission failure
- Offline or timeout
- Retry behavior

Do not render a spinner forever. Give the user a next action.

## Review Red Flags

- Same data exists in React Query and Redux.
- Search filters reset on refresh because they are not in URL state.
- Components refetch on every render due to unstable keys.
- Mutation succeeds but stale list remains visible.
- Optimistic update cannot roll back cleanly.
- Loading state hides existing useful data during background refresh.
- Derived values are stored and drift from source state.

## Validation

- Refresh the page and confirm URL-owned state survives.
- Navigate away and back; confirm expected cache behavior.
- Trigger slow network and error responses.
- Perform two concurrent mutations and verify final UI correctness.
- Test optimistic rollback with a forced failure.

