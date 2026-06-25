---
name: dockerfile-best
description: "Dockerfile 实战与镜像优化。覆盖 multi-stage build、layer 缓存策略、.dockerignore、non-root user、distroless / scratch / alpine 选型、镜像大小压缩、SBOM 与 supply chain（Sigstore / cosign / SLSA）、信号传递（tini / dumb-init）、健康检查、BuildKit 缓存挂载、跨架构构建（buildx/QEMU）、CVE 扫描（trivy/grype）。当用户提到 Dockerfile、镜像构建、multi-stage、layer 缓存、.dockerignore、non-root、distroless、scratch、镜像瘦身、cosign、SBOM、buildx、跨架构、trivy 时使用。"
---

# Dockerfile Best Practices Skill — 镜像构建实战

## 何时使用

- 写新 Dockerfile / 优化现有镜像
- 镜像太大（> 1GB）需要瘦身
- 排查 layer 缓存命中率低 / 构建慢
- 容器以 root 跑 / 信号收不到 / 僵尸进程
- CI 集成 SBOM / CVE 扫描 / 镜像签名

## 一、十条铁律

1. **Multi-stage build** — build 阶段与运行阶段分离
2. **最小 base image** — distroless / scratch / alpine（按需）
3. **non-root user** — 永不以 root 运行
4. **`.dockerignore`** — 比 `.gitignore` 更严格
5. **指令排序按变化频率** — 不变的在前，常变的在后（layer 缓存）
6. **复制依赖清单先于源码** — `package.json` 先 `COPY` + `install`，再 `COPY .`
7. **`COPY` 不用 `ADD`**（除非要解压 / URL）
8. **明确 EXPOSE / HEALTHCHECK** — 不依赖默认
9. **exec form CMD** —`CMD ["node","app.js"]` 而非 `CMD node app.js`
10. **pin 版本** — `node:20.11.1-alpine3.19` 而非 `node:latest`

## 二、Multi-stage 标准模板（Node.js）

```dockerfile
# ================ Stage 1: deps ================
FROM node:20.11.1-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --prod=false

# ================ Stage 2: build ================
FROM node:20.11.1-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable && pnpm build && pnpm prune --prod

# ================ Stage 3: runner ================
FROM node:20.11.1-alpine AS runner
WORKDIR /app

# non-root
RUN addgroup -S app && adduser -S app -G app
USER app

# 仅拷贝运行时所需
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
COPY --from=builder --chown=app:app /app/dist ./dist
COPY --from=builder --chown=app:app /app/package.json ./

ENV NODE_ENV=production
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --spider http://localhost:8080/healthz || exit 1

CMD ["node", "dist/server.js"]
```

## 三、Go 应用（极致小）

```dockerfile
# ================ build ================
FROM golang:1.22-alpine AS build
WORKDIR /src

# 缓存 modules（独立 layer）
COPY go.mod go.sum ./
RUN go mod download

COPY . .
# 静态链接 + strip
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -trimpath \
    -o /out/app ./cmd/server

# ================ runtime ================
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app /app
EXPOSE 8080
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

`distroless/static` ≈ 2MB。Go 静态二进制 + distroless = **总镜像 < 20MB**。

## 四、Python 应用

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app

# 系统编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && rm -rf /var/lib/apt/lists/*

# 用 venv 隔离
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段：不需要 gcc
FROM python:3.12-slim
RUN groupadd -r app && useradd -r -g app app
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY --chown=app:app . .
USER app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myapp.wsgi:application"]
```

## 五、Layer 缓存策略

**核心：变化频率从低到高排序**

```dockerfile
# ❌ 反模式：每次代码变都重装依赖
COPY . .
RUN npm install

# ✅ 正模式：依赖清单单独复制，缓存依赖层
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

**rule of thumb**：

```
1. base image (~ 月稳定)
2. system deps (~ 周变化)
3. language deps (~ 周变化)
4. application config (~ 天变化)
5. application source (~ 每次变化)
```

## 六、BuildKit 缓存挂载（构建提速）

```dockerfile
# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS build
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
# 挂载 pnpm store cache，跨构建复用
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    corepack enable && pnpm install --frozen-lockfile

COPY . .
RUN --mount=type=cache,target=/app/.next/cache \
    pnpm build
```

```dockerfile
# Go: 缓存 GOPATH + GOCACHE
FROM golang:1.22 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go mod download

COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -o /out/app ./cmd/server
```

需要 `DOCKER_BUILDKIT=1` 或新版 docker（默认）。CI 上加 `--cache-from` / `--cache-to` 跨 runner 共享。

## 七、Base image 选型

| Image | 大小 | 适用 | 风险 |
|---|---|---|---|
| `scratch` | 0 | Go / Rust 静态二进制 | 无 shell / 无 CA / 难调试 |
| `gcr.io/distroless/static` | ~2MB | Go / Rust | 同上但有 CA / TZ |
| `gcr.io/distroless/base` | ~20MB | 需要 glibc 的二进制 | 无 shell |
| `alpine:3.19` | ~7MB | 通用 | musl libc 偶尔与 glibc 程序冲突 |
| `debian:12-slim` | ~80MB | 兼容性最好 | 包多一些，攻击面大 |
| `ubuntu:22.04` | ~80MB | dev 友好 | 不必要的工具 |
| `node:20-alpine` | ~180MB | Node.js 应用 | musl 与某些 native module 冲突 |
| `python:3.12-slim` | ~150MB | Python | 不带 gcc，缺时再装 |

**默认选择**：
- Go / Rust → distroless
- Node / Python → alpine 或 slim
- C/C++ glibc 应用 → distroless/cc

## 八、`.dockerignore`（必备）

```
.git
.github
.vscode
node_modules
.env
.env.local
*.log
*.md
docs/
test/
__pycache__/
*.pyc
.pytest_cache/
coverage/
dist/
build/
.next/
.cache/
.DS_Store
Dockerfile
docker-compose*.yml
```

**作用**：
1. 减小 build context（上传 GB 级目录到 daemon 慢）
2. 防止 `.env` / 凭据被烤进镜像
3. 防止 `node_modules` 覆盖 build 阶段重装

## 九、Non-root user

```dockerfile
# alpine
RUN addgroup -S app && adduser -S app -G app
USER app

# debian / ubuntu
RUN groupadd -r app && useradd -r -g app -s /bin/false app
USER app

# distroless
USER nonroot:nonroot   # 已内置 65532 用户
```

**注意**：
- chown 文件：`COPY --chown=app:app . .`
- 端口绑定 < 1024 需 root → 改用 8080+ 或 setcap
- 部分应用需要 `/tmp` 可写 → 创建并 chown

## 十、信号 / PID 1

```dockerfile
# ❌ shell form：sh 是 PID 1，吞 SIGTERM
CMD npm start

# ✅ exec form：node 是 PID 1，直接收信号
CMD ["node", "server.js"]

# 或用 tini 处理僵尸进程 + 信号转发
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

详见 `graceful-shutdown` skill。

## 十一、跨架构构建（buildx / QEMU）

```bash
# 启用 buildx 多平台
docker buildx create --use --name multi
docker buildx inspect --bootstrap

# 构建 amd64 + arm64 同时推送
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myorg/app:v1.0.0 \
  --push .
```

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.22 AS build
ARG TARGETOS TARGETARCH
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build ...
```

`$BUILDPLATFORM` 是宿主架构（快），`$TARGETPLATFORM` 是目标。Go 可交叉编译（无需 QEMU）；Node / Python native module 仍需要 QEMU。

## 十二、Supply Chain 安全

### SBOM 生成

```bash
# Syft 生成 SBOM
syft myorg/app:v1.0.0 -o cyclonedx-json > sbom.json

# Docker 内置（24+）
docker buildx build --sbom=true -t myorg/app:v1.0.0 .
```

### 镜像签名（cosign / Sigstore）

```bash
# 签名（keyless，OIDC 认证）
cosign sign myorg/app:v1.0.0

# 验证
cosign verify myorg/app:v1.0.0 \
  --certificate-identity=ci@myorg.com \
  --certificate-oidc-issuer=https://accounts.google.com
```

K8s 准入控制（Kyverno / Cosign Policy Controller）只允许签名镜像运行。

### CVE 扫描

```bash
trivy image myorg/app:v1.0.0
grype  myorg/app:v1.0.0
docker scout cves myorg/app:v1.0.0
```

CI 集成：

```yaml
- name: Trivy scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myorg/app:v1.0.0
    severity: CRITICAL,HIGH
    exit-code: 1
```

## 十三、HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8080/healthz || exit 1
```

参数：
- `--interval` 检查间隔
- `--timeout` 单次超时
- `--start-period` 启动宽限期（容器刚起还在 init）
- `--retries` 连续失败次数后标记 unhealthy

K8s 不用 Dockerfile HEALTHCHECK（用自家 readinessProbe / livenessProbe），但 docker-compose / standalone 用得上。

## 十四、构建指标 / 调试

```bash
# 看 layer 大小
docker history myorg/app:v1.0.0

# 看 image 内文件大小
dive myorg/app:v1.0.0     # 工具：wagoodman/dive

# 看构建上下文实际大小（验证 .dockerignore）
docker build --no-cache --progress=plain -t test . 2>&1 | grep "transferring context"

# inspect
docker inspect myorg/app:v1.0.0 | jq '.[0].Config'
```

## 十五、Don'ts

- ❌ `RUN apt-get update` 不带 `&& apt-get install` 在同一 layer — 缓存陷阱（apt 数据 stale）
- ❌ `ADD https://...` 下载文件 — 用 `RUN curl -fsSL` 可控
- ❌ 暴露 SSH / 装 SSH server — 容器不该是宠物
- ❌ 把 secrets `ENV PASSWORD=xxx` — 通过运行时 env / secret mount 传入
- ❌ `COPY .env .` — 凭据烤进镜像，`.dockerignore` 必排
- ❌ `latest` tag 在生产 — 不可重现，pin 版本 + digest
- ❌ root 跑应用 — 容器逃逸权限放大
- ❌ Dockerfile 装一堆 dev 工具（vim / curl / jq）— 攻击面 + 镜像大
- ❌ 一个 RUN 装所有 — 拆开后 layer 都失效；但也不要每行一 RUN（layer 数限制）
- ❌ shell form CMD — 信号 / 僵尸问题
- ❌ 不写 HEALTHCHECK 也不写 K8s probe — 进程挂了没人知道
- ❌ `tail -f /dev/null` 当 CMD — entrypoint 应是真实进程

## 十六、参考资料

- Docker Best Practices：https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Distroless：https://github.com/GoogleContainerTools/distroless
- BuildKit：https://docs.docker.com/build/buildkit/
- Sigstore / cosign：https://www.sigstore.dev/
- SLSA framework：https://slsa.dev/
- "Docker Image Layers Explained" 系列博客
- Trivy：https://aquasecurity.github.io/trivy/
- dive (image explorer)：https://github.com/wagoodman/dive
- Snyk Container vulnerabilities database
- "Building Better Docker Images" (talks)
