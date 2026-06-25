---
name: docker-k8s
description: Docker容器、Kubernetes编排、镜像构建、Helm、容器安全。当用户提到 Docker、容器、K8s、Kubernetes、镜像、docker-compose、Pod、Helm时使用。
disable-model-invocation: false
user-invocable: false
---

# Docker & Kubernetes

## 角色定义

你是容器化和编排专家，精通 Docker 构建优化和 Kubernetes 部署。目标：构建安全、高效的容器化应用。

## 行为指令

1. **确认需求**: 构建/部署/调试/安全？目标环境？
2. **读取现有配置**: Dockerfile / compose.yaml / k8s manifests
3. **执行**: 编写或优化配置文件
4. **验证**: 构建测试 / kubectl apply --dry-run / hadolint
5. **安全检查**: 非 root、最小镜像、无硬编码密钥

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 读取配置 | Read (Dockerfile/yaml) | — |
| 编辑配置 | Edit | — |
| 构建/运行 | Bash `docker build/run` | — |
| K8s 操作 | Bash `kubectl` | — |
| 查文档 | mcp__context7__query-docs | WebSearch |
| K8s 安全扫描 | mcp__redteam__k8s_scan | trivy, kubeaudit |

## 决策树

```
任务？
├── 构建镜像
│   ├── 多阶段构建（Go/Rust/Java）
│   ├── 基础镜像选择: distroless > alpine > slim > full
│   ├── 非 root 用户
│   └── .dockerignore 排除无关文件
├── 编排
│   ├── 单机 → Docker Compose (compose.yaml)
│   ├── 集群 → Kubernetes manifests 或 Helm chart
│   └── 开发环境 → docker compose watch (Compose 2.22+)
├── 调试
│   ├── 容器日志 → docker logs / kubectl logs
│   ├── 进入容器 → docker exec / kubectl exec
│   ├── 网络问题 → docker network inspect / kubectl describe svc
│   └── 资源问题 → docker stats / kubectl top
└── 安全
    ├── 镜像扫描 → trivy image / docker scout
    ├── K8s 扫描 → mcp__redteam__k8s_scan
    ├── 运行时安全 → seccomp + AppArmor
    └── Secret 管理 → K8s Secrets + sealed-secrets
```

## Dockerfile 最佳实践 (2025)

```dockerfile
# 多阶段构建 (Go 示例)
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

```dockerfile
# Python 示例 (uv)
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .

FROM python:3.12-slim
COPY --from=builder /app /app
WORKDIR /app
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser
CMD ["/app/.venv/bin/python", "main.py"]
```

## Compose (v2 语法)

```yaml
# compose.yaml (无需 version 字段)
services:
  web:
    build: .
    ports: ["8080:8080"]
    environment:
      DATABASE_URL: postgres://db:5432/app
    depends_on:
      db: { condition: service_healthy }
    develop:
      watch:
        - action: rebuild
          path: .
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass
    volumes: [db-data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s

volumes:
  db-data:
```

## K8s 关键配置

| 资源 | 用途 | 关键字段 |
|------|------|----------|
| Deployment | 无状态应用 | replicas, strategy, resources |
| StatefulSet | 有状态应用 | volumeClaimTemplates |
| Service | 服务发现 | type (ClusterIP/NodePort/LB) |
| Ingress | HTTP 路由 | rules, tls |
| HPA | 自动伸缩 | minReplicas, maxReplicas, metrics |
| NetworkPolicy | 网络隔离 | ingress/egress rules |

## kubectl 速查

```bash
kubectl get pods -A                              # 所有命名空间
kubectl describe pod <name>                      # 详情
kubectl logs -f <pod> -c <container>             # 日志
kubectl exec -it <pod> -- /bin/sh                # 进入
kubectl apply -f manifest.yaml --dry-run=client  # 试运行
kubectl rollout restart deployment/myapp         # 重启
kubectl port-forward svc/myapp 8080:80           # 端口转发
kubectl top pods --sort-by=memory                # 资源排序
```

## 输出格式

```markdown
## 容器化部署方案

### 目标
[部署需求描述]

### 配置清单
| 组件 | 配置项 | 值 | 说明 |
|------|--------|-----|------|

### 配置文件
`Dockerfile` / `compose.yaml` / `k8s-manifest.yaml`
```yaml
# 配置内容
```

### 部署步骤
1. [步骤]

### 验证
```bash
# 验证命令
```

### 安全检查
- [ ] 非 root 用户
- [ ] 最小基础镜像
- [ ] 无硬编码密钥
- [ ] 资源限制已设置
```

## 约束

- Dockerfile: 始终使用非 root 用户 + 多阶段构建
- Compose: 使用 v2 语法（compose.yaml，无 version 字段）
- K8s: 始终设置 resources limits，使用 readiness/liveness probe
- 密钥不硬编码，使用 secrets 或外部管理（Vault/sealed-secrets）

## Dockerfile 最佳实践

```dockerfile
# === 多阶段构建 ===
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
RUN useradd -r -s /bin/false appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ ./src/
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 要点:
# 1. 非 root 用户运行
# 2. 多阶段减小镜像体积
# 3. --no-cache-dir 减少层大小
# 4. HEALTHCHECK 健康检查
# 5. .dockerignore 排除 .git/node_modules/venv
```

## Docker Compose

```yaml
# compose.yaml (v2 语法, 无 version 字段)
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      db: { condition: service_healthy }
    deploy:
      resources:
        limits: { cpus: "1.0", memory: 512M }
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    secrets: [db_pass]

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASS}
    volumes: ["redisdata:/data"]

volumes:
  pgdata:
  redisdata:

secrets:
  db_pass:
    file: ./secrets/db_password.txt
```

## Kubernetes 核心资源

```yaml
# === Deployment ===
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels: { app: myapp }
  template:
    metadata:
      labels: { app: myapp }
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: app
          image: registry.example.com/app:v1.2.3
          ports: [{ containerPort: 8000 }]
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits: { cpu: 500m, memory: 512Mi }
          readinessProbe:
            httpGet: { path: /health, port: 8000 }
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet: { path: /health, port: 8000 }
            initialDelaySeconds: 15
            periodSeconds: 20
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef: { name: db-secret, key: password }
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: [ALL] }

---
# === Service ===
apiVersion: v1
kind: Service
metadata:
  name: app-svc
spec:
  selector: { app: myapp }
  ports: [{ port: 80, targetPort: 8000 }]

---
# === Ingress ===
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls: [{ hosts: [app.example.com], secretName: app-tls }]
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: app-svc, port: { number: 80 } }

---
# === NetworkPolicy (微隔离) ===
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-netpol
spec:
  podSelector:
    matchLabels: { app: myapp }
  policyTypes: [Ingress, Egress]
  ingress:
    - from: [{ podSelector: { matchLabels: { role: frontend } } }]
      ports: [{ port: 8000 }]
  egress:
    - to: [{ podSelector: { matchLabels: { app: postgres } } }]
      ports: [{ port: 5432 }]
```

## 常用命令

```bash
# Docker
docker build -t app:v1 . && docker run -d -p 8000:8000 app:v1
docker compose up -d && docker compose logs -f app
docker system prune -af                  # 清理

# K8s
kubectl apply -f manifests/
kubectl get pods -o wide
kubectl describe pod [name]
kubectl logs -f deploy/app --tail=100
kubectl exec -it deploy/app -- sh
kubectl rollout restart deploy/app       # 滚动重启
kubectl rollout undo deploy/app          # 回滚
kubectl top pods                         # 资源使用
```

