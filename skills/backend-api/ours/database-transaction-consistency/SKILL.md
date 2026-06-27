---
name: database-transaction-consistency
description: "数据库事务与一致性设计。覆盖 ACID、隔离级别、锁、乐观/悲观并发控制、幂等写入、唯一约束、outbox、saga、读写一致性、分布式事务替代方案和迁移安全。当用户提到事务、一致性、并发写、脏读、幻读、死锁、乐观锁、悲观锁、outbox、saga、幂等、数据库约束时使用。"
---

# Database Transaction Consistency

## Core Rule

Correctness belongs in the database and domain layer, not only in application if-statements.

## Workflow

1. Identify invariants: what must never be false?
2. Put simple invariants in constraints: primary key, unique, foreign key, check, not-null.
3. Define transaction boundaries around invariant changes.
4. Choose concurrency strategy: optimistic, pessimistic, unique insert, queue, or serialized workflow.
5. Define idempotency for retries.
6. Add outbox or saga when side effects cross process boundaries.
7. Test concurrent writes, retries, rollback, and deadlock behavior.

## Isolation Levels

| Level | Protects | Still Risky |
|---|---|---|
| Read committed | dirty reads | non-repeatable reads, write skew |
| Repeatable read | non-repeatable reads | some write skew depending on DB |
| Serializable | strongest correctness | more retries and aborts |

Use the weakest level that preserves the invariant, but prove it with tests.

## Constraint First

Prefer:

- Unique constraints for duplicate prevention.
- Foreign keys for relationship integrity.
- Check constraints for simple domain bounds.
- Exclusion constraints when ranges must not overlap.
- Partial unique indexes for conditional uniqueness.

Application validation improves UX; database constraints enforce truth.

## Concurrency Patterns

### Optimistic Locking

Use for low-conflict user edits.

```sql
UPDATE documents
SET title = ?, version = version + 1
WHERE id = ? AND version = ?;
```

If affected rows = 0, return conflict and ask the caller to reload or merge.

### Pessimistic Locking

Use for high-value, short critical sections.

```sql
SELECT * FROM accounts WHERE id = ? FOR UPDATE;
```

Keep locked sections short. Never call slow external APIs while holding DB locks.

### Unique Insert As Lock

Use for idempotency and once-only operations.

```sql
INSERT INTO idempotency_keys (key, status)
VALUES (?, 'processing')
ON CONFLICT DO NOTHING;
```

## Outbox Pattern

When a transaction must emit an event, write the event into an outbox table in the same transaction. A worker publishes the event later.

```sql
BEGIN;
UPDATE orders SET status = 'paid' WHERE id = ?;
INSERT INTO outbox_events (topic, payload) VALUES ('order.paid', ?);
COMMIT;
```

This avoids "DB committed but message not sent" and "message sent but DB rolled back".

## Saga Pattern

Use for multi-step workflows across services:

```text
reserve inventory -> charge payment -> create shipment
        | failure      | failure
        v              v
release inventory <- refund payment
```

Each step must have a compensating action or be explicitly irreversible.

## Review Red Flags

- Check-then-insert without unique constraint.
- External API call inside a DB transaction.
- Retry loops that are not idempotent.
- Long-running transaction around user think time.
- Missing tenant key in unique indexes for multi-tenant data.
- Background workers update records without concurrency checks.
- Distributed transaction attempted where outbox or saga is enough.

## Validation

- Add concurrency tests with parallel workers.
- Force duplicate requests and confirm idempotency.
- Simulate process crash after DB commit but before event publish.
- Test deadlock retry behavior.
- Verify migration adds constraints without locking large tables unexpectedly.

