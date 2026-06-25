---
name: database
description: 数据库操作、SQL优化、MySQL、PostgreSQL、Redis、MongoDB。当用户提到数据库、SQL、MySQL、PostgreSQL、Redis、MongoDB、查询优化、索引时使用。
disable-model-invocation: false
user-invocable: false
---

# 数据库

## 角色定义

你是数据库专家，精通关系型/NoSQL 数据库设计与优化。目标：编写高效的数据库操作和优化查询性能。

## 行为指令

1. **确认数据库**: 类型（MySQL/PG/Redis/Mongo）、版本、当前问题
2. **读取 Schema**: 先看现有表结构、索引、查询
3. **执行**: 编写/优化 SQL、设计 Schema、配置调优
4. **验证**: EXPLAIN ANALYZE 验证查询计划

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 读取配置/SQL | Read | — |
| 编辑 SQL/配置 | Edit | — |
| 执行查询 | Bash (mysql/psql/redis-cli) | — |
| 查文档 | mcp__context7__query-docs | WebSearch |

## 决策树

```
问题类型？
├── Schema 设计
│   ├── 关系数据 → MySQL/PostgreSQL (范式化)
│   ├── 文档数据 → MongoDB (嵌套 vs 引用)
│   ├── 缓存/会话 → Redis
│   └── 时序数据 → TimescaleDB / InfluxDB
├── 查询优化
│   ├── 慢查询 → EXPLAIN → 缺少索引？全表扫描？
│   ├── N+1 问题 → JOIN / 批量查询
│   ├── 聚合慢 → 物化视图 / 预计算
│   └── 锁争用 → 事务隔离级别 / 乐观锁
├── 索引策略
│   ├── WHERE 条件列 → B-tree 索引
│   ├── 全文搜索 → GIN/FULLTEXT
│   ├── JSON 字段 → GIN (PG) / 多键索引 (Mongo)
│   └── 复合条件 → 复合索引 (遵循最左前缀)
└── 运维
    ├── 备份恢复 → pg_dump/mysqldump
    ├── 主从复制 → streaming replication
    └── 连接池 → PgBouncer / ProxySQL
```

## 索引优化速查

| 场景 | PostgreSQL | MySQL |
|------|-----------|-------|
| 等值查询 | B-tree (默认) | B-tree |
| 范围查询 | B-tree | B-tree |
| 全文搜索 | GIN + tsvector | FULLTEXT |
| JSON 查询 | GIN (jsonb) | 虚拟列+索引 |
| 数组包含 | GIN | — |
| 前缀匹配 | text_pattern_ops | INDEX(col(N)) |
| 覆盖索引 | INCLUDE | — (联合索引) |

```sql
-- 查看慢查询
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- 索引使用统计 (PG)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes ORDER BY idx_scan;

-- 未使用索引
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

## Redis 模式速查

| 模式 | 命令 | 适用场景 |
|------|------|----------|
| 缓存 | SET/GET + TTL | 热点数据 |
| 计数器 | INCR/DECR | 限流、统计 |
| 分布式锁 | SET NX EX | 互斥操作 |
| 排行榜 | ZADD/ZRANGE | 排名 |
| 消息队列 | XADD/XREAD (Stream) | 异步任务 |
| 发布订阅 | PUBLISH/SUBSCRIBE | 实时通知 |

## 安全要点

- 参数化查询，禁止字符串拼接 SQL
- 最小权限原则（只读用户 vs 管理员）
- 敏感数据加密存储（密码 bcrypt/argon2，PII 列加密）
- 审计日志（pgaudit / MySQL audit plugin）

## 输出格式

```markdown
**数据库**: [类型 + 版本]
**问题**: [描述]
**方案**: [SQL/配置变更]
**验证**: [EXPLAIN 结果 / 性能对比]
**风险**: [兼容性/数据影响评估]
```

## 约束

- 优化前必须 EXPLAIN，用数据说话
- 索引不是越多越好，写密集场景注意索引开销
- Redis 大 key 拆分（单 key value < 10KB）
- MongoDB 嵌套深度 ≤3 层

## MongoDB 操作速查

```javascript
// === CRUD 操作 ===

// 查询：精确匹配 + 条件过滤
db.users.find({ status: "active", age: { $gte: 18 } }, { name: 1, email: 1 })
db.users.findOne({ _id: ObjectId("507f1f77bcf86cd799439011") })

// 插入
db.orders.insertOne({
  userId: ObjectId("507f1f77bcf86cd799439011"),
  items: [{ sku: "A001", qty: 2, price: 99.5 }],
  status: "pending",
  createdAt: new Date()
})

// 更新：原子操作符
db.orders.updateOne(
  { _id: ObjectId("..."), status: "pending" },
  { $set: { status: "shipped" }, $inc: { version: 1 }, $currentDate: { updatedAt: true } }
)

// 删除
db.sessions.deleteOne({ token: "abc123" })
db.logs.deleteMany({ createdAt: { $lt: ISODate("2025-01-01") } })

// === 查询分析 ===
db.users.explain("executionStats").find({ email: "test@example.com" })
// 关注: executionStats.totalDocsExamined vs nReturned，COLLSCAN 表示全集合扫描

// === 索引创建 ===

// 复合索引（遵循 ESR 原则：Equality → Sort → Range）
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 })

// 全文索引
db.articles.createIndex({ title: "text", content: "text" }, { weights: { title: 10, content: 1 } })

// TTL 索引：自动过期删除
db.sessions.createIndex({ expireAt: 1 }, { expireAfterSeconds: 0 })

// 唯一索引 + 部分索引
db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { email: { $exists: true } } })

// === 聚合管道 ===
db.orders.aggregate([
  { $match: { status: "completed", createdAt: { $gte: ISODate("2026-01-01") } } },
  { $group: { _id: "$userId", totalSpent: { $sum: "$amount" }, orderCount: { $sum: 1 } } },
  { $sort: { totalSpent: -1 } },
  { $limit: 20 }
])

// === Schema 验证 ===
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price", "category"],
      properties: {
        name: { bsonType: "string", description: "产品名称，必填" },
        price: { bsonType: "decimal", minimum: 0, description: "价格，必须 ≥ 0" },
        category: { enum: ["electronics", "clothing", "food"], description: "分类枚举" },
        tags: { bsonType: "array", items: { bsonType: "string" } }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

## 连接池配置

### PgBouncer 最小配置

```ini
; pgbouncer.ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; 连接池模式：transaction（推荐）| session | statement
pool_mode = transaction

; 最大客户端连接数
max_client_conn = 1000

; 每个数据库的默认连接池大小
default_pool_size = 25

; 连接池中最少保留的服务端连接
min_pool_size = 5

; 服务端连接空闲超时（秒）
server_idle_timeout = 300

; 客户端登录超时
client_login_timeout = 60
```

### ProxySQL 配置

```sql
-- 添加后端 MySQL 服务器
INSERT INTO mysql_servers (hostgroup_id, hostname, port, weight, max_connections)
VALUES
  (10, '10.0.0.1', 3306, 100, 200),  -- 写组
  (20, '10.0.0.2', 3306, 100, 200),  -- 读组
  (20, '10.0.0.3', 3306, 100, 200);  -- 读组

-- 读写分离规则
INSERT INTO mysql_query_rules (rule_id, active, match_pattern, destination_hostgroup, apply)
VALUES
  (1, 1, '^SELECT .* FOR UPDATE$', 10, 1),   -- SELECT FOR UPDATE → 写组
  (2, 1, '^SELECT',                20, 1),    -- 普通 SELECT → 读组
  (3, 1, '.*',                     10, 1);    -- 其余 → 写组

LOAD MYSQL SERVERS TO RUNTIME;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
SAVE MYSQL QUERY RULES TO DISK;
```

### 应用层连接池

```python
# Python asyncpg 连接池
import asyncpg

pool = await asyncpg.create_pool(
    dsn="postgresql://user:pass@localhost:5432/mydb",
    min_size=5,          # 最小连接数
    max_size=20,         # 最大连接数
    max_inactive_connection_lifetime=300,  # 空闲连接回收（秒）
    command_timeout=30,  # 查询超时
)

async with pool.acquire() as conn:
    rows = await conn.fetch("SELECT * FROM users WHERE id = $1", user_id)
```

```javascript
// Node.js pg 连接池
const { Pool } = require('pg')

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'app',
  password: 'secret',
  max: 20,                   // 最大连接数
  idleTimeoutMillis: 30000,  // 空闲连接超时
  connectionTimeoutMillis: 5000,  // 连接超时
  allowExitOnIdle: false
})

const { rows } = await pool.query('SELECT * FROM users WHERE id = $1', [userId])
```

## 在线 Schema 变更

### PostgreSQL

```sql
-- ✅ 非阻塞操作（仅获取 ACCESS EXCLUSIVE 极短时间）
ALTER TABLE orders ADD COLUMN notes TEXT;                    -- 无默认值，瞬间完成
ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending';  -- PG 11+ 非阻塞
ALTER TABLE orders ALTER COLUMN notes SET DEFAULT 'N/A';    -- 仅修改元数据
CREATE INDEX CONCURRENTLY idx_orders_user ON orders(user_id);  -- 不阻塞写入

-- ⚠️ 阻塞操作（需要重写表或长时间锁）
ALTER TABLE orders ALTER COLUMN price TYPE NUMERIC(12,2);   -- 重写整张表，阻塞读写
ALTER TABLE orders ADD COLUMN total INT NOT NULL DEFAULT 0; -- PG 10 及以下会重写表
ALTER TABLE orders SET (fillfactor = 70);                   -- 不立即重写，但 VACUUM FULL 时重写
```

### MySQL pt-online-schema-change

```bash
# Percona pt-online-schema-change：在线加列
pt-online-schema-change \
  --alter "ADD COLUMN notes TEXT, ADD INDEX idx_status (status)" \
  --host=127.0.0.1 --port=3306 \
  --user=root --ask-pass \
  --chunk-size=1000 \
  --max-lag=1s \
  --check-interval=1 \
  --critical-load="Threads_running=50" \
  --max-load="Threads_running=25" \
  --execute \
  D=mydb,t=orders
# --dry-run 先预演，确认无误后改 --execute
```

### PostgreSQL pg_repack（消除表/索引膨胀）

```bash
# 安装扩展
psql -c "CREATE EXTENSION pg_repack;" mydb

# 重整单张表（在线，不阻塞读写）
pg_repack -d mydb -t orders --no-superuser-check

# 仅重建索引
pg_repack -d mydb -t orders --only-indexes

# 重整整个数据库
pg_repack -d mydb
```

## 备份恢复命令

### PostgreSQL

```bash
# 自定义格式备份（压缩，支持并行恢复）
pg_dump -Fc -Z6 -j4 -h localhost -U postgres -d mydb -f /backup/mydb_$(date +%Y%m%d).dump

# 恢复到指定数据库
pg_restore -h localhost -U postgres -d mydb_restore -j4 --clean --if-exists /backup/mydb_20260318.dump

# 仅备份 Schema（不含数据）
pg_dump -Fc --schema-only -d mydb -f /backup/mydb_schema.dump

# 仅备份指定表
pg_dump -Fc -t orders -t users -d mydb -f /backup/partial.dump
```

### MySQL

```bash
# 全库备份（InnoDB 一致性快照）
mysqldump -h 127.0.0.1 -u root -p \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --set-gtid-purged=OFF \
  --all-databases | gzip > /backup/all_$(date +%Y%m%d).sql.gz

# 恢复
gunzip < /backup/all_20260318.sql.gz | mysql -u root -p

# 单库备份
mysqldump --single-transaction --routines --triggers -u root -p mydb > /backup/mydb.sql
```

### Redis

```bash
# 手动触发 RDB 快照（后台执行，不阻塞）
redis-cli BGSAVE
# RDB 文件位置
redis-cli CONFIG GET dir
# 复制 dump.rdb 到备份目录
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%Y%m%d).rdb

# AOF 持久化配置（redis.conf）
# appendonly yes
# appendfsync everysec
# AOF 重写
redis-cli BGREWRITEAOF

# 恢复：将 dump.rdb 或 appendonly.aof 放回 dir 目录，重启 Redis
```

### MongoDB

```bash
# 全库备份（BSON 格式，支持 oplog 用于时间点恢复）
mongodump --uri="mongodb://user:pass@localhost:27017" \
  --oplog \
  --gzip \
  --out=/backup/mongo_$(date +%Y%m%d)

# 单库备份
mongodump --db=mydb --gzip --out=/backup/mydb_$(date +%Y%m%d)

# 恢复（--drop 先删除已有集合再恢复）
mongorestore --uri="mongodb://user:pass@localhost:27017" \
  --oplogReplay \
  --gzip \
  --drop \
  /backup/mongo_20260318

# 单集合恢复
mongorestore --db=mydb --collection=orders --gzip /backup/mydb_20260318/mydb/orders.bson.gz
```

## 性能监控查询

### PostgreSQL

```sql
-- 当前活跃查询（排查慢查询/锁等待）
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       state, wait_event_type, wait_event,
       left(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state != 'idle'
  AND pid != pg_backend_pid()
ORDER BY duration DESC;

-- 锁等待链
SELECT blocked.pid AS blocked_pid,
       blocked.query AS blocked_query,
       blocking.pid AS blocking_pid,
       blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks gl ON gl.locktype = bl.locktype
  AND gl.database IS NOT DISTINCT FROM bl.database
  AND gl.relation IS NOT DISTINCT FROM bl.relation
  AND gl.granted
JOIN pg_stat_activity blocking ON blocking.pid = gl.pid
WHERE blocked.pid != blocking.pid;

-- pg_stat_statements Top 10 耗时查询（需先启用扩展）
SELECT left(query, 80) AS query,
       calls,
       round(total_exec_time::numeric, 2) AS total_ms,
       round(mean_exec_time::numeric, 2) AS avg_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### MySQL

```sql
-- 当前连接与活跃查询
SHOW PROCESSLIST;
-- 或更详细
SELECT id, user, host, db, command, time, state, left(info, 100) AS query
FROM information_schema.processlist
WHERE command != 'Sleep'
ORDER BY time DESC;

-- Top 10 耗时 SQL（需启用 performance_schema）
SELECT DIGEST_TEXT AS query,
       COUNT_STAR AS calls,
       ROUND(SUM_TIMER_WAIT / 1e12, 2) AS total_sec,
       ROUND(AVG_TIMER_WAIT / 1e12, 4) AS avg_sec,
       SUM_ROWS_EXAMINED AS rows_examined,
       SUM_ROWS_SENT AS rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

### Redis

```bash
# 内存使用概览
redis-cli INFO memory
# 关注: used_memory_human, used_memory_peak_human, mem_fragmentation_ratio

# 慢查询日志（默认记录执行 >10ms 的命令）
redis-cli SLOWLOG GET 10
# 配置慢查询阈值（微秒）
redis-cli CONFIG SET slowlog-log-slower-than 5000

# 大 key 扫描（生产环境用 --no-auth-warning）
redis-cli --bigkeys --no-auth-warning

# 实时监控命令（调试用，生产慎用）
redis-cli MONITOR
```

### MongoDB

```javascript
// 当前正在执行的操作
db.currentOp({ active: true, secs_running: { $gte: 3 } })

// 终止慢操作
db.killOp(<opId>)

// 服务器状态：操作计数器
db.serverStatus().opcounters
// { insert: ..., query: ..., update: ..., delete: ..., command: ... }

// 集合级别统计
db.orders.stats({ scale: 1024 * 1024 })  // 单位 MB

// 当前连接数
db.serverStatus().connections
// { current: ..., available: ..., totalCreated: ... }

// Profiler：记录慢查询（level 1 = 仅慢查询，阈值 100ms）
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

