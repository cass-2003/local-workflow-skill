---
name: mobile-offline-sync
description: "移动端离线优先与数据同步。覆盖本地缓存、SQLite/IndexedDB/AsyncStorage、同步队列、冲突解决、乐观更新、后台同步、重试、幂等、分页同步和弱网体验。当用户提到 App 离线、offline first、离线缓存、数据同步、弱网、同步冲突、移动端本地数据库、离线队列时使用。"
---

# Mobile Offline Sync

## Core Rule

Offline support is a product contract, not a cache toggle. Define what users can see, edit, queue, merge, and retry before writing sync code.

## Sync Model

Classify each data type:

- Read-through cache: safe to refresh and replace.
- Draft data: user-owned, must not disappear.
- Command queue: actions to replay later.
- Shared records: may conflict and need merge policy.
- Append-only events: usually easy to sync with idempotency keys.

## Workflow

1. Define offline capabilities per feature: view, create, edit, delete, attach files, submit.
2. Choose local storage by data shape and volume.
3. Add schema versioning and migrations.
4. Design sync queue with idempotency keys and retry/backoff.
5. Define conflict policy: server wins, client wins, field merge, manual review, or domain-specific merge.
6. Surface sync state in UI: pending, synced, failed, conflict, stale.
7. Test airplane mode, flaky network, app kill, duplicate requests, and clock drift.

## Storage Guidance

- Use simple key-value storage only for small settings and session-adjacent state.
- Use SQLite or equivalent for relational offline data, queryable lists, and large datasets.
- Store attachments separately from metadata.
- Encrypt sensitive local data when product risk requires it.
- Keep server IDs and local temporary IDs distinct until sync confirms.

## Conflict Handling

Every mutable record should define:

- What identifies the record?
- What version or timestamp proves freshness?
- Which fields can merge independently?
- Which conflicts require user choice?
- Can failed operations be safely retried?

Do not silently overwrite user edits after reconnect.

## Review Red Flags

- Offline cache has no migration path.
- Sync retries create duplicate orders, messages, or payments.
- The UI shows "saved" before durable local persistence.
- App restart loses queued operations.
- Conflict resolution is hidden from users.
- Background sync assumes OS will always run it on time.

## Validation

- Create and edit records offline, kill the app, reopen, then reconnect.
- Replay the same queued command twice and confirm idempotency.
- Force server-side edits during offline client edits and verify conflict behavior.
- Test low storage and local database migration from older app versions.
