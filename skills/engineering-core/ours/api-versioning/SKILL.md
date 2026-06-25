---
name: api-versioning
description: "API 版本控制实战。覆盖 URL path / header / media type / query param 四种版本载体，semver 在 API 上的语义、breaking vs additive change 判定、Stripe / GitHub / Twilio 的版本策略、deprecation 流程与 Sunset 头、N 个版本并行支持成本、客户端 SDK 协调、内部服务版本（gRPC / Protobuf 演进）、GraphQL 无版本心智、API gateway 路由、版本回归测试矩阵。当用户提到 API 版本、API versioning、breaking change、deprecation、Sunset 头、Stripe versioning、Protobuf 兼容、GraphQL 演进、版本回归 时使用。"
---

# API Versioning Skill — API 版本控制

## 何时使用

- 设计公开 API（SDK / 第三方集成）
- 想做 breaking change 但有存量客户
- 内部服务 (microservices) 间接口演进
- 评审 PR 是否 breaking change
- 制定 deprecation 流程

## 一、版本载体四种

### 1. URL Path（最常见）

```
GET /v1/users/123
GET /v2/users/123
```

**优点**：直观 / 缓存友好 / curl 易测 / 多版本并存简单
**缺点**：版本号"侵入" URL（看似资源是不同的）

### 2. Header

```
GET /users/123
Accept: application/vnd.example.v2+json
# 或自定义
X-API-Version: 2
```

**优点**：URL 干净 / 资源同一
**缺点**：浏览器不能直接打开 / 缓存键需 Vary 头

### 3. Media Type

```
GET /users/123
Accept: application/vnd.example.user.v2+json
```

GitHub API v3 用法。**学院派**，实践少见（开发心智成本高）。

### 4. Query Param

```
GET /users/123?version=2
```

不推荐 —— 不像版本，像参数。

### 5. Date-based（Stripe / GitHub GraphQL）

```
Stripe-Version: 2026-04-15
```

每次 breaking change 发版日期 stamp，旧客户端永远拿到当时的语义。**最强但最贵**：服务端要长期维护多个 schema 版本。

## 二、Breaking vs Additive Change

### Additive（向后兼容，不需要新版本）

- ✅ 加新 endpoint
- ✅ 加新 optional 字段（请求 / 响应）
- ✅ 加新 enum 值（**前提：客户端容忍未知值**）
- ✅ 放宽校验（要求 ≥ 18 → ≥ 0）
- ✅ 加新 HTTP method 在已有 path

### Breaking（必须升版本）

- ❌ 删字段 / 改字段名
- ❌ 改字段类型
- ❌ 加 required 字段
- ❌ 改默认值（行为改变）
- ❌ 删 enum 值
- ❌ 改 HTTP 状态码语义
- ❌ 收紧校验（≥ 0 → ≥ 1）
- ❌ 改错误格式
- ❌ 改分页 / 默认排序

**陷阱**：加 enum 值表面 additive，但若旧 SDK 用 switch 没 default，会崩。**枚举默认 breaking**，除非协议要求"未知值视为 X"。

## 三、SemVer 在 API 上的应用

```
v1.2.3
↑ ↑ ↑
│ │ └─ patch: bug fix（永不 breaking）
│ └─── minor: 加功能（永不 breaking）
└───── major: breaking change
```

**API URL 一般只暴露 major**（`/v1/`）。minor / patch 透明升级。

## 四、Deprecation 流程（业界标杆）

### 1. 公告期（≥ 3 月）

- 发布 changelog
- 邮件 / dashboard 通知用户
- API 响应加 header：

```
Sunset: Wed, 31 Dec 2026 23:59:59 GMT
Deprecation: true
Link: <https://api.example.com/v3/users>; rel="successor-version"
Warning: 299 - "v1 deprecated, use v3 by 2026-12-31"
```

### 2. 监控期

观察使用量下降曲线 / 联系大客户

### 3. 关闭期

- 返 410 Gone（不是 404）
- body 给迁移指引

```http
HTTP/1.1 410 Gone
Content-Type: application/problem+json

{
  "type": "/errors/api-version-sunset",
  "title": "API v1 has been sunset",
  "detail": "Migrate to v3. See https://api.example.com/migration/v1-to-v3",
  "successor": "/v3/users"
}
```

## 五、并行支持成本

```
v1 + v2 + v3 同时跑：
- 路由 / 控制器 ×3
- 测试用例 ×3
- 文档 ×3
- bug 修复 ×3
- 安全 patch ×3
```

**业界经验**：
- **Stripe**：长期所有版本（按日期）— 公司投资巨大
- **GitHub**：v3 (REST) + v4 (GraphQL)，每个版本数年
- **Twilio**：保持 2-3 个 major
- **Slack**：弃用就快，3-6 月窗口
- 大多数中小项目：**最多 2 个 major 同时**（current + previous）

## 六、内部服务版本（不同心法）

### gRPC / Protobuf 演进

```protobuf
// v1
message User {
  string id = 1;
  string email = 2;
}

// v2 — 加字段（兼容！）
message User {
  string id = 1;
  string email = 2;
  string locale = 3;   // 新字段，老客户端忽略
}
```

**Protobuf 规则**：
- ✅ 加字段（新 number）
- ✅ 删字段：保留 number `reserved 5;`（永不复用）
- ❌ 改 type / 改 number / 删字段不 reserve

正确演进的 .proto 文件可以**永不升 major**，几年都向前兼容。这是 gRPC 服务"无版本"心智的关键。

工具 `buf breaking` 在 CI 上自动检测 .proto breaking change。

### REST 内部服务

如果消费方都是自家服务：
- 用 path 版本（简单）
- 强制升级（短窗口 deprecation）
- API gateway 做版本路由

## 七、GraphQL 无版本心智

GraphQL 鼓励**不用版本号**：

```graphql
# v1
type User {
  id: ID!
  email: String!
  fullName: String!
}

# 演进 — 加新字段
type User {
  id: ID!
  email: String!
  fullName: String! @deprecated(reason: "Use firstName + lastName")
  firstName: String
  lastName: String
}
```

客户端只查需要的字段，不影响。`@deprecated` 在 schema 标注，IDE / 文档自动展示。

**但仍需要协调**：
- 字段移除：先 deprecate → 监控 query → 确认无客户端用 → 才删
- 改类型：仍是 breaking — 加新字段 + deprecate 旧
- enum 改：同 REST

## 八、客户端 SDK 协调

```typescript
// SDK 在请求时声明版本
const stripe = new Stripe(key, { apiVersion: '2026-04-15' })
```

服务端按 header 路由到对应版本逻辑。客户端 SDK 升级版本是显式动作（不会被动 break）。

**SDK 自身 semver**：
- SDK v3.0.0 默认调 API v2
- SDK v3.1.0 (minor) 不能让默认 API 版本切到 v3 — 那是 breaking

## 九、API Gateway 路由模式

```yaml
# nginx / Envoy / Kong
location /v1/ { proxy_pass http://service-v1/; }
location /v2/ { proxy_pass http://service-v2/; }

# 或 header-based
if ($http_x_api_version = "2") { proxy_pass http://service-v2; }
```

新版本 → 新 deployment → 灰度切流。旧版本服务仍然运行直至 sunset。

## 十、版本回归测试矩阵

| | v1 | v2 | v3 |
|---|---|---|---|
| 端到端测试套件 | ✅ | ✅ | ✅ |
| 旧 SDK 兼容（v1.x） | ✅ | ❌ | ❌ |
| 旧 SDK 兼容（v2.x） | - | ✅ | ✅ |
| 文档 freshness | ⚠️ | ✅ | ✅ |

CI 跑全矩阵：每发一个 PR 跑所有版本的 E2E。

## 十一、版本演进的真实路线图

```
T+0     v1 GA
T+12mo  v2 GA, v1 still supported
T+15mo  v1 deprecated, Sunset header
T+24mo  v1 returns 410 Gone
T+18mo  v3 GA, v2 still supported
...
```

**节奏建议**：
- 公开 API：每 18-24 月可发新 major / 旧版至少支持 12 月
- 内部 API：3-6 月 deprecation 即可

## 十二、Don'ts

- ❌ 把 bug 修复也叫"breaking change" — 修 bug 不算
- ❌ 在 patch 版本里改 enum 值 / 加 required 字段
- ❌ 公开 API 第一天不分版本（"我们小没必要"）— 后期改 URL 极痛
- ❌ 多版本支持却共享代码 / 数据库 schema —— 一动俱动
- ❌ deprecation 没有 Sunset header / 没有 changelog
- ❌ 410 Gone 后 body 没给迁移说明
- ❌ 同一 endpoint 同时支持新旧字段，response 体里两份 — 用版本头分流
- ❌ 改 default 行为（"now we paginate by default"）— 会爆量
- ❌ Protobuf 删字段不 `reserved` 编号
- ❌ 内部服务无 buf breaking / contract test，改 schema 全靠人

## 十三、参考资料

- Stripe API Versioning: https://stripe.com/docs/api/versioning
- GitHub API: https://docs.github.com/en/rest/overview/api-versions
- Twilio Versioning Strategy: https://www.twilio.com/docs/usage/api-version
- "Versioning REST APIs"（Roy Fielding 反对版本号思想）
- "Sunset HTTP Header"（RFC 8594）
- buf 工具: https://buf.build/
- "API Stewardship Crew"（Slack 的 API 治理实践）
- "Web API Design: The Missing Reference"（Apigee 白皮书）
