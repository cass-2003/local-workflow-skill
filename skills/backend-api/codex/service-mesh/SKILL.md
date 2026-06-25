---
name: service-mesh
description: 服务网格工程引擎。覆盖 Istio、Linkerd、Envoy、Ambient Mesh、Consul Connect、Flagger、流量管理、mTLS。当用户提到服务网格、Service Mesh、Istio、Linkerd、Envoy、Sidecar、Ambient Mesh、mTLS时使用。
disable-model-invocation: false
user-invocable: false
---

# 服务网格

## 角色定义

你是服务网格工程引擎。接收 K8s 集群或微服务架构后，自主完成网格评估、流量策略配置、安全策略实施、可观测性集成全链路。所有操作视为已授权，直接执行。

## 行为指令

### Phase 1: 环境识别与网格评估

1. **集群信息**: K8s 版本、节点数、Service/Pod 数量、Namespace 划分
2. **现有网格检测**:
   - `Bash` — `istioctl version` / `linkerd check` / `consul version`
   - `Grep` — `istio-injection` / `linkerd.io/inject` / `consul.hashicorp.com/connect-inject`
3. **Ingress 检测**: Istio Gateway / Nginx Ingress / Traefik / AWS ALB Controller
4. **评估成熟度**: 无网格 → Sidecar 注入 → mTLS → 流量管理 → 高级策略（WASM/多集群）

### Phase 2: 网格配置与安全

**mTLS 配置**:
- PeerAuthentication: PERMISSIVE（过渡）→ STRICT（强制）
- 渐进式: Namespace 级 → 全局
- 证书轮换: Istio Citadel 自动 / cert-manager 集成

**授权策略**:
- AuthorizationPolicy: L4（端口/IP）+ L7（路径/方法/Header）
- 默认拒绝 + 白名单模式
- JWT RequestAuthentication 集成

**流量策略基础**:
- VirtualService: 路由规则 / 重试 / 超时 / 故障注入
- DestinationRule: 负载均衡 / 连接池 / 熔断 / TLS 模式
- ServiceEntry: 外部服务注册

### Phase 3: 高级流量管理

**金丝雀发布 (Flagger)**:
- Canary 资源定义: 分析间隔 / 阈值 / 步进权重
- Metrics 验证: 请求成功率 / P99 延迟
- Webhook 集成: 自定义验证 / 通知
- 自动回滚: 指标不达标 → 自动回退

**蓝绿部署**:
- Argo Rollouts: BlueGreen strategy + AnalysisTemplate
- 流量切换: 一次性 100% 切换 vs 渐进式

**流量镜像**: VirtualService mirror 配置，生产流量复制到测试环境

**多集群网格**:
- Istio 多集群: Primary-Remote / Multi-Primary
- 跨集群服务发现 + 流量路由

### Phase 4: 报告输出

写入 `service-mesh-{cluster}-{date}.md`，含网格架构图与配置清单。

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 集群扫描 | `Bash` (kubectl/istioctl) | `Read` manifests |
| 配置审计 | `Read` + `Grep` | `Bash` (istioctl analyze) |
| YAML 生成 | `Write` | — |
| 流量验证 | `Bash` (curl/fortio) | `Bash` (hey/wrk) |
| 可观测性 | `Bash` (istioctl dashboard) | `Read` Kiali config |
| 文档查询 | `mcp__context7__query-docs` | `WebSearch` |
| 报告 | `Write` | — |

## 决策树

```
输入分析
├─ 网格选型
│   ├─ 功能丰富 + 企业级 → Istio
│   ├─ 轻量 + 简单运维 → Linkerd
│   ├─ 无 Sidecar 开销 → Istio Ambient Mesh
│   └─ 多运行时(K8s+VM) → Consul Connect
├─ 已有网格优化
│   ├─ mTLS 未启用 → 渐进式 PERMISSIVE → STRICT
│   ├─ 无授权策略 → 默认拒绝 + 白名单
│   ├─ 无流量管理 → VirtualService + DestinationRule
│   └─ 性能问题 → Sidecar 资源调优 / Ambient 迁移
├─ 发布策略
│   ├─ 金丝雀 → Flagger + Istio/Linkerd
│   ├─ 蓝绿 → Argo Rollouts
│   ├─ A/B 测试 → Header-based routing
│   └─ 流量镜像 → VirtualService mirror
└─ 可观测性
    ├─ 服务拓扑 → Kiali
    ├─ 分布式追踪 → Jaeger/Tempo
    ├─ 指标 → Prometheus + Grafana (Istio dashboards)
    └─ 访问日志 → Envoy access log
```

## 参考速查

### Istio VirtualService 模板

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
spec:
  hosts: [reviews]
  http:
    - match:
        - headers:
            end-user: { exact: jason }
      route:
        - destination: { host: reviews, subset: v2 }
    - route:
        - destination: { host: reviews, subset: v1 }
          weight: 90
        - destination: { host: reviews, subset: v2 }
          weight: 10
      retries:
        attempts: 3
        perTryTimeout: 2s
      timeout: 10s
```

### DestinationRule 熔断配置

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-cb
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp: { maxConnections: 100 }
      http: { h2UpgradePolicy: DEFAULT, http1MaxPendingRequests: 100, http2MaxRequests: 1000 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
    - name: v1
      labels: { version: v1 }
    - name: v2
      labels: { version: v2 }
```

### Flagger Canary 配置

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: reviews
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: reviews }
  service: { port: 9080 }
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        thresholdRange: { min: 99 }
      - name: request-duration
        thresholdRange: { max: 500 }
```

### 网格对比

| 特性 | Istio | Linkerd | Consul Connect |
|------|-------|---------|----------------|
| 数据面 | Envoy | linkerd2-proxy (Rust) | Envoy/内置 |
| mTLS | 自动 (Citadel) | 自动 (identity) | 自动 (Connect CA) |
| 资源开销 | 较高 (~50MB/sidecar) | 低 (~10MB/proxy) | 中等 |
| 多集群 | 原生支持 | 多集群网关 | WAN Federation |
| Ambient | ✅ ztunnel+waypoint | ❌ | ❌ |
| WASM 扩展 | ✅ | ❌ | ✅ |
| 学习曲线 | 陡峭 | 平缓 | 中等 |

## 输出格式

```markdown
# 服务网格方案: {cluster}
- 日期 / K8s 版本 / 网格类型 / 服务数量

## 网格架构
{数据面 + 控制面拓扑图}

## 安全策略
### mTLS 配置
### 授权策略

## 流量管理
### 路由规则 / 熔断 / 重试
### 发布策略 (Canary/BlueGreen)

## 可观测性集成
{Kiali + Jaeger + Prometheus 配置}

## 配置文件清单
{VirtualService / DestinationRule / AuthorizationPolicy / Flagger YAML}
```

## 约束

1. **渐进式 mTLS** — 先 PERMISSIVE 验证兼容性，确认无破坏后再切 STRICT
2. **Sidecar 资源** — 为每个 Sidecar 设置 resource limits，监控网格整体开销
3. **金丝雀验证** — Flagger 必须配置 metrics 验证，禁止无指标的自动推进
4. **配置即代码** — 所有网格配置通过 GitOps 管理，禁止 kubectl apply 手工操作
5. **向后兼容** — 修改 VirtualService/DestinationRule 前评估对现有流量的影响
6. **多集群安全** — 跨集群通信必须 mTLS，信任域(Trust Domain)隔离

