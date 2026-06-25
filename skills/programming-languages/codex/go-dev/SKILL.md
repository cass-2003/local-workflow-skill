---
name: go-dev
description: Go语言开发、并发编程、goroutine、channel、Go模块。当用户提到 Go、Golang、goroutine、channel、go mod、cobra、gin、泛型时使用。
disable-model-invocation: false
user-invocable: false
---

# Go 开发

## 角色定义

你是 Go 开发专家，精通并发模式、性能优化和工具链。目标：编写地道、高性能的 Go 代码。

## 行为指令

1. **确认环境**: `go version`、go.mod 中的 Go 版本、项目结构
2. **遵循惯例**: 先 Read 项目现有代码风格，保持一致
3. **编码**: 使用 Go 1.22+ 特性（泛型、range over func、enhanced routing）
4. **验证**: `go vet` + `golangci-lint run` + `go test`
5. **优化**: 仅在必要时做 benchmark 驱动优化

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 查看项目结构 | Glob `**/*.go` | Bash `tree` |
| 读取源码 | Read | — |
| 编辑代码 | Edit | — |
| 运行/测试 | Bash `go test/run` | — |
| 查依赖文档 | mcp__context7__resolve-library-id → query-docs | WebSearch |

## 决策树

```
任务类型？
├── 新项目
│   ├── CLI 工具 → cobra + viper
│   ├── HTTP 服务 → net/http (标准库) 或 gin/echo/fiber
│   ├── gRPC 服务 → google.golang.org/grpc + protobuf
│   └── 安全工具 → cobra + net/http + 并发
├── 现有项目
│   ├── 先读 go.mod 确认版本和依赖
│   ├── 读 cmd/ 和 internal/ 理解架构
│   └── 遵循已有错误处理/日志模式
└── 性能问题
    ├── pprof 分析 → go tool pprof
    ├── 竞态检测 → go test -race
    └── benchmark → go test -bench
```

## Go 1.22+ 现代特性

```go
// 泛型
func Filter[T any](s []T, f func(T) bool) []T {
    var result []T
    for _, v := range s {
        if f(v) { result = append(result, v) }
    }
    return result
}

// range over int (Go 1.22)
for i := range 10 { fmt.Println(i) }

// Enhanced ServeMux routing (Go 1.22)
mux := http.NewServeMux()
mux.HandleFunc("GET /api/users/{id}", getUser)
mux.HandleFunc("POST /api/users", createUser)

// log/slog 结构化日志 (Go 1.21+)
slog.Info("request", "method", r.Method, "path", r.URL.Path)
```

## 项目结构 (标准布局)

```
project/
├── cmd/myapp/main.go       # 入口
├── internal/                # 私有包
│   ├── handler/             # HTTP handler
│   ├── service/             # 业务逻辑
│   └── repository/          # 数据层
├── pkg/                     # 公共包 (可选)
├── go.mod
├── go.sum
├── Makefile
└── .golangci.yml
```

## 并发模式速查

| 模式 | 适用场景 | 关键构件 |
|------|----------|----------|
| Fan-out/Fan-in | 并行处理 + 汇总 | goroutine + channel |
| Worker Pool | 限制并发数 | buffered chan + N goroutine |
| Pipeline | 流式处理 | chain of channels |
| Context 取消 | 超时/取消传播 | context.WithTimeout/Cancel |
| errgroup | 并发 + 错误收集 | golang.org/x/sync/errgroup |
| singleflight | 去重并发请求 | golang.org/x/sync/singleflight |

## 错误处理

```go
// 自定义错误 (推荐 fmt.Errorf 包装)
if err != nil {
    return fmt.Errorf("read config: %w", err)
}

// errors.Is / errors.As
if errors.Is(err, os.ErrNotExist) { /* ... */ }

// 哨兵错误
var ErrNotFound = errors.New("not found")
```

## 常用命令

```bash
go mod init github.com/user/project   # 初始化
go mod tidy                            # 整理依赖
go build -o bin/app ./cmd/myapp        # 构建
go test ./... -v -race -cover          # 测试
golangci-lint run                      # Lint
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o app  # 交叉编译+瘦身
```

## 输出格式

```markdown
## 实现方案

### 技术选型
- **方案**: [选择的方案]
- **理由**: [选择理由]

### 代码变更
`path/to/file.go`
```go
// 实现代码
```

### 验证步骤
```bash
go vet ./...
golangci-lint run
go test ./... -v -race -cover
```
```

## 约束

- Go 版本 ≥1.22，使用泛型和新路由语法
- 错误处理用 `%w` 包装，不吞错误
- 并发必须处理 context 取消和 goroutine 泄漏
- golangci-lint 作为必选 linter

## Go 项目结构

```
project/
├── cmd/
│   └── server/
│       └── main.go          # 入口
├── internal/
│   ├── handler/             # HTTP handlers
│   ├── service/             # 业务逻辑
│   ├── repository/          # 数据访问
│   └── model/               # 数据模型
├── pkg/                     # 可导出的库
├── api/                     # OpenAPI/proto 定义
├── go.mod
├── go.sum
├── Makefile
└── Dockerfile
```

## 常用模式

```go
// === HTTP Server (标准库 + chi) ===
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    r := chi.NewRouter()
    r.Use(middleware.Logger, middleware.Recoverer, middleware.Timeout(30*time.Second))

    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("ok"))
    })
    r.Route("/api/v1", func(r chi.Router) {
        r.Get("/users/{id}", getUser)
        r.Post("/users", createUser)
    })

    srv := &http.Server{Addr: ":8080", Handler: r}
    go func() { srv.ListenAndServe() }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, os.Interrupt)
    <-quit
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    srv.Shutdown(ctx)
}

// === 错误处理模式 ===
type AppError struct {
    Code    int    `json:"-"`
    Message string `json:"error"`
}

func (e *AppError) Error() string { return e.Message }

// === 并发模式 (errgroup) ===
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(ctx)
for _, url := range urls {
    url := url
    g.Go(func() error {
        return fetch(ctx, url)
    })
}
if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

## 测试与工具

```bash
# 测试
go test ./... -v -race -cover
go test -run TestSpecific -count=1 ./pkg/...
go test -bench=. -benchmem ./...

# Lint
golangci-lint run ./...

# 构建
CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o bin/server ./cmd/server

# 依赖
go mod tidy
go mod vendor
go list -m -u all   # 检查更新
```

