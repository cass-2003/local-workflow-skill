---
name: migration-zero-downtime
description: "零停机数据库 schema 变更实战。覆盖 expand-contract / dual-write / backfill / online ALTER（pt-online-schema-change、gh-ost、pg_repack）、向后兼容窗口、应用与 schema 多版本协作、删列删表的安全节奏、large table 加索引、改类型策略、外键变更、Vitess / Citus / TiDB 在线变更能力、回滚预案、PostgreSQL/MySQL/SQLite 差异。当用户提到零停机迁移、zero-downtime migration、expand-contract、online schema change、pt-online-schema-change、gh-ost、pg_repack、ALTER TABLE 卡住、加列加索引、删列删表 时使用。"
---

# Zero-Downtime Migration Skill — 零停机 schema 变更

## 何时使用

- 给生产数据库加列 / 删列 / 改类型 / 加索引
- 大表（千万 / 亿级）改 schema 想避免锁表
- 拆库 / 合库 / 改主键
- 评审 PR 中的 migration 是否安全
- 部署多副本应用时新旧版本短暂共存的兼容设计

## 一、核心原则：Expand-Contract（扩展-收缩）

任何 schema 变更都拆成最小**前向兼容**步骤，**应用与 schema 多版本共存**：

```
应用 v1 (旧)        应用 v2 (新)
   │                   │
   └──── 同时运行 ─────┘
   │                   │
   └──需要 schema 同时支持两个版本──┘
```

### 标准 6 步

```
[1] expand schema:    加新结构（向后兼容，旧 app 不受影响）
[2] backfill data:    历史数据迁移
[3] dual write:       app v2 同时写新旧（v2 部署）
[4] read switch:      app v3 改读新结构（v3 部署）
[5] stop dual write:  app v4 只写新（v4 部署）
[6] contract:         移除旧结构
```

每步独立部署 + 验证 + 必要时可回滚。

## 二、典型场景剧本

### 场景 1：加非空列

**直接 `ALTER TABLE x ADD COLUMN c TEXT NOT NULL DEFAULT 'x'`** —— PostgreSQL 11+ 元数据级（瞬间），但 MySQL 5.7 / 老版本会重写整表。

**保险做法**（任何 DB 都安全）：

```sql
-- 步骤 1: 加列允许 NULL
ALTER TABLE users ADD COLUMN locale TEXT;

-- 步骤 2: backfill（分批避免长事务）
UPDATE users SET locale = 'en' WHERE locale IS NULL AND id BETWEEN 1 AND 10000;
-- ... 循环

-- 步骤 3: 应用 v2 部署：新写入填值
INSERT INTO users (..., locale) VALUES (..., 'en');

-- 步骤 4: 加 NOT NULL（验证无 NULL 后）
ALTER TABLE users ALTER COLUMN locale SET NOT NULL;

-- 步骤 5（可选）: 加默认值
ALTER TABLE users ALTER COLUMN locale SET DEFAULT 'en';
```

### 场景 2：重命名列

**绝对不要**直接 `ALTER TABLE ... RENAME COLUMN`。中间窗口旧 app 找不到列直接崩。

```
[1] 加新列 new_name（兼容）
[2] 应用 v2: dual write — 同时写 old_name 和 new_name
[3] backfill: UPDATE ... SET new_name = old_name WHERE new_name IS NULL
[4] 应用 v3: 读 new_name（旧 fallback 读 old_name）
[5] 应用 v4: 只读写 new_name
[6] 删除 old_name
```

### 场景 3：删列

```
[1] 应用 v2: 不再写该列（保留读，避免 SELECT * 崩）
[2] 应用 v3: 不再读该列（彻底切断引用）
[3] 等所有版本下线（关键！）
[4] ALTER TABLE x DROP COLUMN old
```

**SELECT \* 是隐藏炸弹**：删列前先把所有 SELECT \* 改成显式列列表。

### 场景 4：改列类型

```sql
-- ❌ 直接 ALTER COLUMN TYPE 大表锁
ALTER TABLE orders ALTER COLUMN amount TYPE BIGINT;

-- ✅ 加新列
ALTER TABLE orders ADD COLUMN amount_v2 BIGINT;
-- dual write
-- backfill: UPDATE orders SET amount_v2 = amount::BIGINT;
-- 切读
-- 删旧列
```

PostgreSQL 12+ 的 in-place alter（如 INT → BIGINT 当 PG 内部表示一致时）可以瞬间，但仍建议 expand-contract 保险。

### 场景 5：加索引（大表）

```sql
-- ❌ 普通 CREATE INDEX 锁写
CREATE INDEX idx_users_email ON users(email);

-- ✅ PostgreSQL: CONCURRENTLY 不锁写（但慢 + 不能在事务里）
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
-- 注意：失败留 INVALID 索引，需 DROP + 重建

-- ✅ MySQL 5.6+: ONLINE DDL（默认，但有限制）
ALTER TABLE users ADD INDEX idx_email (email), ALGORITHM=INPLACE, LOCK=NONE;

-- ✅ 大流量场景: gh-ost / pt-online-schema-change（影子表 + 触发器/binlog）
```

## 三、在线 DDL 工具

### MySQL

| 工具 | 原理 | 优势 | 劣势 |
|---|---|---|---|
| **pt-online-schema-change** | 影子表 + 触发器 | 成熟 / 灵活 | 触发器开销 / 外键麻烦 |
| **gh-ost** | 影子表 + binlog | 无触发器 / 可暂停 / 可在 replica 跑 | 需 row-based binlog |
| **MySQL 8.0 instant DDL** | 元数据级 | 加列瞬间 | 仅特定操作 |

### PostgreSQL

| 工具 | 用途 |
|---|---|
| `CREATE INDEX CONCURRENTLY` | 加索引不锁写 |
| `pg_repack` | 重组表 / 清碎片 / 改 fillfactor 不锁 |
| `pg_squeeze` | 同上自动版 |
| 14+: `REINDEX CONCURRENTLY` | 重建索引不锁 |

### NewSQL

- **TiDB / CockroachDB / Vitess / Spanner**：原生 online DDL，大多操作秒级
- **AWS Aurora**：fast DDL（add column / nullable column）秒级

## 四、危险操作清单（生产慎用）

| 操作 | 危险度 | 替代 |
|---|---|---|
| `DROP COLUMN` 直接执行 | 高 | expand-contract |
| `RENAME TABLE` | 高 | view + 双写 |
| `ALTER ... NOT NULL` 大表 | 高 | 先 add NOT NULL CHECK NOT VALID + VALIDATE CONSTRAINT |
| `ADD FOREIGN KEY` | 中 | NOT VALID 加约束，再 VALIDATE |
| 改主键类型 | 极高 | 重建表 + 双写 + 切读（多版本） |
| 大表 `TRUNCATE` | 高 | 分批 DELETE 或重建表后重命名 |
| `CREATE INDEX` (无 CONCURRENTLY) | 中 | 加 CONCURRENTLY |
| 长事务 backfill | 高 | 分批 + 短事务 |

## 五、PostgreSQL 加 CHECK / FK 不锁

```sql
-- 第一步：加约束但不立即校验（O(1) 锁极短）
ALTER TABLE orders ADD CONSTRAINT chk_amount_positive
  CHECK (amount > 0) NOT VALID;

-- 第二步：后台校验（不阻塞写）
ALTER TABLE orders VALIDATE CONSTRAINT chk_amount_positive;
```

外键同理：

```sql
ALTER TABLE orders ADD CONSTRAINT fk_user
  FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT fk_user;
```

## 六、Backfill 策略

```sql
-- 分批 + 短事务，避免长锁 + bloat
DO $$
DECLARE
    batch_size INT := 1000;
    last_id BIGINT := 0;
    rows_affected INT;
BEGIN
    LOOP
        UPDATE users SET locale = 'en'
        WHERE id IN (
            SELECT id FROM users
            WHERE id > last_id AND locale IS NULL
            ORDER BY id LIMIT batch_size FOR UPDATE SKIP LOCKED
        )
        RETURNING id INTO last_id;

        GET DIAGNOSTICS rows_affected = ROW_COUNT;
        EXIT WHEN rows_affected = 0;

        PERFORM pg_sleep(0.1);   -- 给 replica 喘息
    END LOOP;
END $$;
```

**关键**：
- 批量 1000-10000 行
- 每批短事务
- 主键有序游标（不要 `WHERE locale IS NULL` 全扫）
- 监控 replica lag — 太大就暂停
- 跑在低峰时段

## 七、应用层兼容（dual write）

```typescript
// app v2: dual write
async function updateUserLocale(id: string, locale: string) {
  await db.tx(async tx => {
    // 写新（也写旧）— 任意一个失败回滚
    await tx.query('UPDATE users SET locale = $1 WHERE id = $2', [locale, id])
    await tx.query('UPDATE user_settings SET locale = $1 WHERE user_id = $2', [locale, id])
  })
}

// app v4: stop dual write，只写新
async function updateUserLocale(id: string, locale: string) {
  await db.query('UPDATE users SET locale = $1 WHERE id = $2', [locale, id])
}
```

## 八、回滚策略

每步之前问自己：**如果立刻发现错了，怎么回退？**

| 步骤 | 回滚方式 |
|---|---|
| 加列 | DROP COLUMN（前提：v2 还没读） |
| Backfill | 没法回滚数据，但不破坏（旧字段还在） |
| Dual write | 部署旧版应用（停止双写） |
| 切读 | 部署旧版应用（继续读旧字段） |
| 删旧列 | **不能回滚** — 此步前必须确认所有 app 版本下线 + 备份 |

**最后一步删除尽量延后**（数月）— 给问题暴露时间。

## 九、Migration 工具集

| 工具 | 语言 | 特点 |
|---|---|---|
| **Flyway** | Java | 简单 / 版本化 / SQL-first |
| **Liquibase** | Java | XML/YAML/SQL / 支持回滚定义 |
| **golang-migrate** | Go | 多 DB 驱动 / up/down |
| **goose** | Go | 简单 / Go 函数迁移可写代码 |
| **Alembic** | Python | SQLAlchemy 集成 / autogenerate |
| **Prisma Migrate** | TS | 自动 diff schema |
| **Atlas** (Ariga) | 任 | declarative 状态对比 |
| **Sqitch** | Perl | DAG 依赖 / 跨 DB |

**规则**：
- migration 文件**永不修改已合入的版本**（创新版本回退）
- migration **幂等**（IF NOT EXISTS / IF EXISTS）
- 拒绝在 migration 里跑长 backfill — 用应用 batch job

## 十、SQLite 特殊性

SQLite **不支持** ALTER COLUMN / DROP COLUMN（3.35 之前）/ ADD CONSTRAINT。变更套路：

```sql
BEGIN;
CREATE TABLE users_new (...);
INSERT INTO users_new SELECT ... FROM users;
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;
COMMIT;
```

3.35+ 支持 DROP COLUMN，但仍是"复制重建"实现。

## 十一、Don'ts

- ❌ 直接 `RENAME COLUMN` / `DROP COLUMN` 在生产
- ❌ migration 里跑 `UPDATE users SET ...`（无 LIMIT，长事务）
- ❌ `CREATE INDEX` 不加 CONCURRENTLY (PG) / ALGORITHM=INPLACE (MySQL)
- ❌ 一个 PR 同时改 schema + 改读写代码（无法独立回滚）
- ❌ migration 文件被合入后修改 → 不同环境 schema 不一致
- ❌ migration 不带 down — 永久不可回退
- ❌ SELECT \* 满天飞 — 加列 / 删列时炸
- ❌ 没监控 replica lag 就 backfill — 副本追不上 → 读旧数据
- ❌ 没做 explain 就上索引 — 没用 / 浪费空间
- ❌ 改主键类型不评估 → 影响所有外键 / 应用代码

## 十二、PR 审计清单

每个 schema migration PR：

- [ ] 是否 expand-only（只加，不改不删）？如否，是否有多步规划文档？
- [ ] 是否独立部署（不依赖应用同时改）？
- [ ] 大表加索引是否 CONCURRENTLY / ONLINE？
- [ ] backfill 是否在 migration 里？应该挪到 job
- [ ] NOT NULL / FK 是否用 NOT VALID + VALIDATE 两步？
- [ ] 是否有 down / rollback 路径？
- [ ] 估算执行时间（千万行表 × 操作复杂度）？
- [ ] 低峰时段执行 + 监控 replica lag？

## 十三、参考资料

- "Online schema migrations at scale"（GitHub gh-ost paper）
- "Expand-Contract Pattern"：https://martinfowler.com/bliki/ParallelChange.html
- PostgreSQL ALTER TABLE locking levels：https://www.postgresql.org/docs/current/sql-altertable.html
- "MySQL 8.0 Online DDL"：https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl.html
- pt-online-schema-change docs
- gh-ost docs：https://github.com/github/gh-ost
- "PostgreSQL at Scale: Database Schema Changes Without Downtime"（Braintree blog）
