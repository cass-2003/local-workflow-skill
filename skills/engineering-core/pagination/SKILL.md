---
name: pagination
description: "API 分页设计实战。覆盖 offset/limit vs cursor 分页对比、cursor 编码（base64 + 复合键）、深分页性能问题、SQL keyset pagination、total count 性能权衡、Link header（RFC 5988）、GraphQL Relay Connection 规范、稳定排序与 tie-breaker、分页与缓存交互、pagination 与无限滚动 UI、stream/scroll API（Elasticsearch search_after / scroll）。当用户提到分页、pagination、offset、cursor、keyset、深分页、deep pagination、search_after、Relay Connection、Link header、infinite scroll、page size、limit offset 时使用。"
---

# Pagination Skill — 分页设计

## 何时使用

- 设计 list API（任何返回多条记录的端点）
- 排查"翻到第 1000 页超慢" / "数据漏 / 重复"
- 需要无限滚动 UI（feed / timeline）
- Elasticsearch / Mongo 深分页性能问题
- GraphQL connection 规范实现

## 一、两大流派

### Offset/Limit（最熟悉，但坑最多）

```
GET /users?offset=0&limit=20
GET /users?page=1&page_size=20
```

**优点**：直观 / 跳页方便（"第 5 页"）/ 显示总数
**缺点**：
1. **深分页慢**：`OFFSET 100000` 数据库要扫描丢弃 10 万行
2. **数据漂移**：翻页期间有新数据插入 → 重复或漏数据
3. **不稳定排序**：相同排序值的多行顺序不定 → 翻页错乱

### Cursor（推荐用于 feed / 大数据集）

```
GET /users?cursor=eyJpZCI6MTIzNDV9&limit=20
```

**优点**：性能稳定（O(1) 不论第几页）/ 无漂移问题
**缺点**：不支持跳页 / 不显示总数 / 实现稍复杂

## 二、Cursor 实现模式

### 1. 简单单字段 cursor

```sql
-- 第一页
SELECT * FROM users ORDER BY id LIMIT 20

-- 后续页：用最后一条 ID 当 cursor
SELECT * FROM users WHERE id > $cursor ORDER BY id LIMIT 20
```

cursor = 最后一条的 id（base64 编码后给客户端）。

### 2. 复合键 cursor（按时间倒序）

```sql
SELECT * FROM posts
WHERE (created_at, id) < ($cursor_ts, $cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 20
```

**为什么加 id 做 tie-breaker**：相同 created_at 的多条不加 id 会乱序 / 翻页漏。

### 3. cursor 编码

```javascript
// 服务端
function encodeCursor(row) {
  return Buffer.from(JSON.stringify({
    ts: row.created_at.toISOString(),
    id: row.id,
  })).toString('base64url')
}

function decodeCursor(s) {
  return JSON.parse(Buffer.from(s, 'base64url').toString('utf8'))
}
```

**安全**：不要让客户端伪造 cursor 跳过权限。可以 HMAC 签名 / 加盐：

```javascript
const cursor = base64({ ts, id, sig: hmac(ts + id, secret) })
```

或者只暴露不可猜的 ID（UUID v7）— 让 cursor 自然失效。

### 4. 双向分页

```
GET /posts?after=cursor1&limit=20    # 下一页
GET /posts?before=cursor1&limit=20   # 上一页
```

```sql
-- after
WHERE (ts, id) < ($after.ts, $after.id) ORDER BY ts DESC, id DESC

-- before（注意结果集要再反转）
WHERE (ts, id) > ($before.ts, $before.id) ORDER BY ts ASC, id ASC
-- 然后 reverse() 给客户端
```

## 三、Keyset Pagination（SQL 索引利用）

```sql
-- ❌ OFFSET 慢
SELECT * FROM users ORDER BY created_at DESC OFFSET 100000 LIMIT 20;
-- 扫 100020 行丢弃 100000

-- ✅ Keyset（cursor 模式）
SELECT * FROM users
WHERE (created_at, id) < ('2024-01-01', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
-- 利用 (created_at, id) 索引直接 seek 到位置，扫 20 行
```

**索引设计**：

```sql
CREATE INDEX idx_posts_feed ON posts (created_at DESC, id DESC);
```

排序方向要与索引一致才能利用。

## 四、Total Count 的成本

`SELECT COUNT(*)` 大表慢。三种处理：

### 1. 不返回 total（推荐）

```json
{
  "items": [...],
  "next_cursor": "..."
}
```

让客户端做"加载更多"UI（无 total），无限滚动符合现代心智。

### 2. 返回近似值

```sql
-- PostgreSQL: pg_stat user_tables.n_live_tup
SELECT n_live_tup FROM pg_stat_user_tables WHERE relname = 'users';

-- MySQL information_schema
SELECT TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_NAME = 'users';
```

误差 ±10%，但近瞬时返回。

### 3. 缓存 total

```redis
SET users:total 1234567 EX 60
```

写入触发失效或定期刷新。

### 4. 客户提示"超过 X 条"

GitHub 搜索经典：

```json
{ "total_count": 1000, "incomplete_results": false }
```

文档说明上限 1000（实际更多就停止计数）。

## 五、HTTP Link Header（RFC 5988）

```http
HTTP/1.1 200 OK
Link: <https://api.example.com/users?cursor=abc>; rel="next",
      <https://api.example.com/users?cursor=xyz>; rel="prev",
      <https://api.example.com/users>; rel="first"
X-Total-Count: 1234567
```

GitHub / GitLab 等用法。客户端 SDK 解析 Link 自动迭代。

## 六、GraphQL Relay Connection

标准化分页 schema：

```graphql
type Query {
  users(first: Int, after: String, last: Int, before: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int   # 可选
}

type UserEdge {
  cursor: String!
  node: User!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

**冗余但严格**：每个 edge 单独 cursor，pageInfo 含状态。Apollo / urql 客户端有现成 cache 集成。

## 七、Elasticsearch / OpenSearch 深分页

```json
// ❌ from + size 深分页：from > 10000 默认拒绝
{ "from": 10000, "size": 20, "query": ... }

// ✅ search_after（cursor 等价）
{
  "size": 20,
  "query": ...,
  "sort": [ { "created_at": "desc" }, { "_id": "desc" } ],
  "search_after": [1715000000000, "abc123"]
}

// ✅ point_in_time + search_after（一致快照）
POST /index/_pit?keep_alive=1m   // 拿快照 ID
// 后续查询带 pit + search_after，所有翻页基于同一时刻数据
```

## 八、稳定排序与 tie-breaker

**永远在排序末尾加唯一 tie-breaker**（通常是 PK）：

```sql
-- ❌ 不稳定
ORDER BY created_at DESC

-- ✅ 稳定
ORDER BY created_at DESC, id DESC
```

否则相同 `created_at` 的行翻页时顺序变化 → 漏 / 重复。

## 九、分页与缓存

cursor 分页天然适合 CDN / 客户端缓存：URL 不变结果不变。

```
GET /posts?cursor=abc123     ← 此 URL 永远返同样结果
Cache-Control: public, max-age=300
```

offset 分页则脆弱：插入新行后所有页"shift"，缓存失效。

## 十、Page Size 限制

```
default: 20
max: 100
```

服务端**强制截断**，防止恶意 `?limit=999999`。

```typescript
const limit = Math.min(parseInt(req.query.limit ?? '20'), 100)
```

## 十一、Don'ts

- ❌ 用 `LIMIT 1000000` 作为"导出全部"接口 — 用 cursor 流式或 batch export
- ❌ cursor 直接编码主键明文 — 暴露内部 ID
- ❌ 排序无 tie-breaker — 翻页混乱
- ❌ `OFFSET` + 实时数据集 — 数据插入造成重复 / 漏
- ❌ 大表每次 list 都 `SELECT COUNT(*)` — 慢死
- ❌ cursor 与排序条件不一致（按 name 排序但 cursor 是 id）— 跳过 / 重复
- ❌ 限制 page_size 但不限 cursor 深度 — 仍可被遍历全表
- ❌ 双向分页用 OFFSET — 心智混乱
- ❌ 给 cursor 不加签名 — 客户端可猜测 / 越权
- ❌ infinite scroll 没"返回顶部"按钮 — UX 灾难

## 十二、API 设计建议

```http
# 推荐响应结构
GET /api/v1/posts?cursor=abc&limit=20
HTTP/1.1 200 OK
{
  "items": [ ... 20 items ... ],
  "page_info": {
    "has_next": true,
    "next_cursor": "xyz789",
    "has_previous": false
  }
}
```

或加 Link header（RFC 5988）便于 SDK。

**不要**返回 `prev_cursor` 等于"前一页第一条"—— 应等于"前一页最后一条之前的 cursor"，否则定位混乱。简单做法：仅 next 单向。

## 十三、参考资料

- "We Need Tool Support for Keyset Pagination"：https://use-the-index-luke.com/no-offset
- Markus Winand 的 SQL 性能博客（深度讲 keyset）
- Relay Cursor Connections Specification：https://relay.dev/graphql/connections.htm
- RFC 5988 Web Linking
- Elasticsearch search_after & PIT docs
- Slack API pagination guide：https://api.slack.com/docs/pagination
- Stripe pagination docs：https://stripe.com/docs/api/pagination
