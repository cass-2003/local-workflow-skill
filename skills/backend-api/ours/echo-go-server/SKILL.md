---
name: echo-go-server
description: "J-SOP License Server 后端开发规范（Go + Echo v4 + SQLite）。覆盖路由分组 / 中间件链 / JWT+HMAC 双密钥 / 速率限制 / SQLite migration / handler idiom / 静态文件 / CORS / panic recover / 审计日志。当用户提到 Go server、Echo、license server、handler、JWT、SQLite、go build、middleware、admin API、user API、speed limit、rate limit 时使用。"
---

# Echo Go Server Skill — J-SOP License Server 实战

## 何时使用

- 给 `j-sop-license-server` 加新 API endpoint（admin / user / sync 三组）
- 改动数据库 schema（用户/许可证/审计/选品库等表）
- 调试 401/403 认证问题、CORS 报错、速率限制误伤
- 评审后端 PR 时检查中间件顺序、错误返回、SQL 注入、N+1 查询

## 一、项目结构

```
j-sop-license-server/
├── main.go                 # 入口：CLI flag / DB init / Echo 路由表 / 中间件
├── db.go                   # SQLite 连接池、schema migration
├── auth.go / auth_user.go  # JWT 签发 + 中间件 + 用户认证
├── keys.go                 # license key CRUD (admin)
├── user_keys.go            # license key 绑定 (user)
├── sync.go                 # 双向同步 API
├── stats.go                # 统计 handler
├── audit.go                # 审计日志
├── cleanup.go              # TTL 清理 goroutine
├── ui/                     # 静态资源（admin.html / user-panel.html / index.html / assets/*）
├── data/license.db         # SQLite (gitignored)
└── go.mod                  # echo/v4 + sqlite3 依赖
```

## 二、运行 / 构建

```bash
# 本地启动
cd j-sop-license-server
go build ./... && ./j-sop-license-server -port 8088 -db data/license.db -admin-token=xxx

# 环境变量优先级：CLI flag > ENV > default
export ADMIN_TOKEN=xxx
export JWT_SECRET=xxx
export HMAC_SECRET=xxx
export CORS_ORIGINS="https://license.haiio.xyz,chrome-extension://abc"

# 生产交叉编译（Linux amd64 v1，无 CGO 依赖 sqlite 用 modernc.org/sqlite）
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GOAMD64=v1 go build -o j-sop-license-server-new
```

## 三、Echo 路由表（J-SOP 标准）

```go
e := echo.New()
e.HideBanner = true

// 中间件顺序至关重要：Logger → Recover → BodyLimit → CORS → 认证
e.Use(middleware.Logger())
e.Use(middleware.Recover())
e.Use(middleware.BodyLimit("5M"))                 // P2-14: 防超大 payload
e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
  AllowOrigins: corsOrigins,                       // 默认仅 chrome-extension://*
  AllowHeaders: []string{echo.HeaderAuthorization, ...},
}))

// 静态资源
e.Static("/", filepath.Join(execDir, "ui"))        // 内部用 path.Clean 防 ../

// 公开 API（带速率限制）
api := e.Group("/api")
sensitiveRL := rateLimitMiddleware(rl, 10)         // 每 IP 每分钟 10 次
api.POST("/keys/activate", HandleActivate, sensitiveRL)
api.POST("/auth/login",    HandleLogin,    sensitiveRL)

// 用户 API（JWT）
user := api.Group("/user", JWTAuth())
user.GET("/keys", listUserKeysHandler)
user.GET("/source-products", HandleUserListSourceProducts)

// 同步 API（license token 通道）
api.POST("/sync/push", HandleSyncPush, sensitiveRL)
api.GET("/sync/pull",  HandleSyncPull,  sensitiveRL)

// 管理员（双模式认证：Admin Token OR JWT role=admin）
admin := api.Group("/admin", AdminAuth(*adminToken))
admin.POST("/keys/generate", HandleGenerate)
admin.GET("/audit-logs",     HandleListAuditLogs)
```

## 四、认证三种模式

| 模式 | 中间件 | 适用 | 头部 |
|---|---|---|---|
| **device license token** | `LicenseAuth()` | content script 同步 | `Authorization: License <token>` |
| **user JWT** | `JWTAuth()` | 用户面板 | `Authorization: Bearer <jwt>` |
| **admin** | `AdminAuth(token)` | 管理面板 | `Bearer <admin-token>` OR `Bearer <admin-jwt>` |

```go
// AdminAuth 双模式（main.go:312）
func AdminAuth(token string) echo.MiddlewareFunc {
  return func(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
      auth := c.Request().Header.Get("Authorization")
      // 模式 1：admin-token（恒时比较防 timing attack — P0-05）
      if token != "" && subtle.ConstantTimeCompare([]byte(auth), []byte("Bearer "+token)) == 1 {
        adminUser, _ := GetFirstAdminUser()
        c.Set("user_id", adminUser.ID); c.Set("role", "admin")
        return next(c)
      }
      // 模式 2：JWT role=admin（每次都重查 DB 确认未禁用 — P1-H01）
      if strings.HasPrefix(auth, "Bearer ") {
        claims, err := parseJWT(auth[7:])
        if err == nil && claims.Role == "admin" {
          user, _ := GetUserByID(claims.UserID)
          if user == nil || user.Status != "active" {
            return c.JSON(403, map[string]string{"error": "用户已被禁用"})
          }
          c.Set("user_id", claims.UserID); c.Set("role", "admin")
          return next(c)
        }
      }
      return c.JSON(401, map[string]string{"error": "未授权"})
    }
  }
}
```

**密钥分离**（M12）：JWT 签名用 `JWT_SECRET`，许可证 HMAC 用 `HMAC_SECRET` —— 不同泄露不互相影响。

## 五、Handler Idiom

```go
// 标准 user handler（按 user_id 隔离数据）
func HandleUserListSourceProducts(c echo.Context) error {
  uid := c.Get("user_id").(int64)              // JWTAuth 已 c.Set
  page, size := parsePagination(c)              // 公共工具

  rows, err := db.Query(`
    SELECT offer_id, title, ... FROM source_products
    WHERE license_key IN (SELECT key FROM license_keys WHERE user_id = ?)
    ORDER BY created_at DESC LIMIT ? OFFSET ?`, uid, size, (page-1)*size)
  if err != nil {
    return c.JSON(500, map[string]string{"error": "DB error"})
  }
  defer rows.Close()

  items := []SourceProduct{}
  for rows.Next() {
    var p SourceProduct
    if err := rows.Scan(&p.OfferID, &p.Title, ...); err != nil {
      log.Printf("scan failed: %v", err)
      continue
    }
    items = append(items, p)
  }
  return c.JSON(200, map[string]interface{}{"items": items, "page": page})
}
```

**规则**：
- 所有 user handler 必须按 `user_id → license_keys → 业务表` 链式隔离
- SQL 一律用 `?` 占位符，**严禁字符串拼接**
- `defer rows.Close()` 不能漏（go vet 会报 SA9001）
- 错误返回不要泄露 SQL / 路径，统一 `{"error": "msg"}`
- HTTP 状态码：200 成功 / 400 入参错 / 401 未认证 / 403 权限不足 / 404 不存在 / 429 限流 / 500 服务器错

## 六、SQLite Migration 模式

```go
// db.go
func InitDB(path string) error {
  os.MkdirAll(filepath.Dir(path), 0o755)
  d, err := sql.Open("sqlite", path)             // modernc.org/sqlite 纯 Go 驱动
  if err != nil { return err }
  d.SetMaxOpenConns(1)                            // SQLite 单写
  if _, err := d.Exec("PRAGMA journal_mode=WAL"); err != nil { return err }
  if _, err := d.Exec("PRAGMA foreign_keys=ON"); err != nil { return err }
  db = d
  return runMigrations()
}

// 增量 migration（幂等！）
func runMigrations() error {
  // 表 1：v1 创建
  if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS license_keys (...)`); err != nil { return err }

  // 表 2：v2 加列（idempotent）
  if !columnExists("license_keys", "user_id") {
    db.Exec(`ALTER TABLE license_keys ADD COLUMN user_id INTEGER REFERENCES users(id)`)
  }

  // 索引
  db.Exec(`CREATE INDEX IF NOT EXISTS idx_license_user ON license_keys(user_id)`)
  return nil
}
```

**规则**：
- 永远 `CREATE TABLE IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS`
- 加列用 `ALTER TABLE ADD COLUMN`，先 `columnExists()` 防重复
- WAL 模式 + `foreign_keys=ON` 是默认
- **不要删列**（SQLite 不支持），用 `<column>_deprecated` 标记 + 应用层不读

## 七、速率限制（内存版）

```go
// main.go:27-95
type rateLimiter struct { mu sync.Mutex; records map[string][]time.Time }

// 每 IP 每分钟 N 次
func (rl *rateLimiter) allow(ip string, max int) bool { ... }

// 后台 5 分钟清理一次过期记录（防内存膨胀）
go func() {
  ticker := time.NewTicker(5 * time.Minute); defer ticker.Stop()
  for range ticker.C { ... cleanup ... }
}()
```

适用场景：登录、激活、心跳、同步、注册 — **任何外部入口都该挂限流**。

## 八、Don'ts

- ❌ 路由直接写在 main，不分组 → 用 `e.Group("/api")` + 子组
- ❌ handler 里直接 `db.Query` 不带 user_id 过滤 → 跨用户数据泄露
- ❌ 错误信息回显 SQL / 文件路径 → 攻击面暴露
- ❌ JWT/HMAC 用同一密钥 → 一处泄露全盘失守
- ❌ admin token 用 `==` 字符串比较 → timing attack（用 `subtle.ConstantTimeCompare`）
- ❌ `CGO_ENABLED=1` 编译 sqlite → 部署机要装 gcc，跨平台麻烦（用 modernc.org/sqlite 纯 Go）
- ❌ panic 不 recover → 用 `middleware.Recover()` 全局兜底
- ❌ 不限 BodyLimit → 攻击者上传 100MB 把内存耗尽
- ❌ CORS `AllowOrigins: ["*"]` → 用环境变量精确白名单

## 九、验证 Pipeline

```bash
# 编译
go build ./...

# 静态检查
go vet ./...

# 单测（如有）
go test ./... -v

# Race 检测（关键）
go test -race ./...

# 启动后烟测
curl http://localhost:8088/api/status
curl -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:8088/api/admin/stats
```

部署前必须 `go build ./...` 返回 exit 0 + 浏览器烟测三个面板（admin / user-panel / index）能加载。

## 十、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\main.go`
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\db.go`
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\auth.go`
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\sync.go`
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\go.mod`
- Echo 文档：https://echo.labstack.com/docs
- modernc.org/sqlite：https://pkg.go.dev/modernc.org/sqlite
