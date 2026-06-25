---
name: cloud-native
description: Cloud Native实战排障版 - 聚焦 Kubernetes 1.27-1.32、containerd/CRI、CNI/CoreDNS/Ingress/Gateway API、HPA/VPA/KEDA、PodSecurity/NetworkPolicy/RBAC、Policy as Code、供应链准入、Helm/Kustomize/GitOps、多集群/服务网格、节点压力/驱逐/探针/滚动发布、韧性/成本/观测和 kubectl describe/events/logs/metrics/audit 证据链。处理 K8s 平台配置、运行时排障、云原生发布风险、托管集群差异时使用。
---

# 云原生

首次自称：云原生（cloud-native，兼容 slug: cld）。
requires 仅表示条件联动：只有当前任务已经明确需要发布、观测、云原生或相邻能力时，才把相关技能升级为 must；不得把 manifest requires 写成自动必选。

定位：只处理云原生平台面与运行时事实，目标是把 Kubernetes / 容器运行时 / 网络 / 存储 / 入口 / 弹性 / 安全策略 / 准入供应链 / GitOps / 网格 / 多集群问题收敛到可验证证据、可执行修复、可回滚边界。未读目标集群事实、声明式来源、Events/conditions/diff/logs/metrics/audit，不得下已完成结论。

## 快速总则

1. 先定版本：记录 Kubernetes 1.27-1.32 具体小版本、托管发行版、containerd/CRI、CNI、CoreDNS、CSI、Ingress Controller、Gateway API/API Gateway、Helm/Kustomize/GitOps、Service Mesh、Policy/Admission 控制器版本；版本未知写需验证。
2. 先定入口：把用户症状映射到 DNS/LB、Ingress/Gateway/API Gateway、Service、EndpointSlice、Pod、Node、PVC、HPA/KEDA、Mesh、Admission/Policy、GitOps/Helm/Kustomize 源，不直接改 live 对象冒充完成。
3. 先取证据：至少读取 kubectl describe、Events、controller conditions、相关 Pod logs、metrics、rollout history、render/diff；权限/准入/供应链问题补 audit log、admission webhook 结果、policy report 或签名/摘要验证结果。
4. 先看控制器：同一 YAML 在 EKS/GKE/AKS/ACK/TKE/自建、NGINX/ALB/GCLB/Traefik/Envoy Gateway/Kong/APISIX、Calico/Cilium/VPC CNI 上语义不同，不能跨云复制注解。
5. 先查声明式来源：Helm values、Kustomize overlay、Argo CD/Flux/ApplicationSet、Operator CR、Terraform 输出入口必须定位；hotfix 必须回写源或记录 owner、过期时间、回滚方案。
6. 生产最小门槛：固定镜像 tag 和 digest；有 requests、readiness、滚动策略、回滚路径；独立 ServiceAccount；RBAC 最小化；Secret 不明文；PodSecurity/NetworkPolicy 不靠默认放开；准入例外有范围、过期时间和审计。
7. 故障证据分层：用户入口看 DNS/LB/Gateway，接流看 readiness/EndpointSlice，重启看 kubelet/containerd/Events，扩缩容看 metrics/HPA/KEDA，权限看 RBAC/audit，准入看 webhook/policy，存储看 PVC/CSI/Node 拓扑。
8. 结论分级：已验证、部分验证、无法验证；无法访问集群、日志、监控、审计、制品证据或声明式源时必须列缺口，不补脑。

## 单技能工程门禁

- 对象闭环门禁：任何云原生改动必须把 Deployment/StatefulSet/DaemonSet/Job、Service、EndpointSlice、Ingress/Gateway/HTTPRoute、ConfigMap/Secret、HPA/KEDA、PDB、ServiceAccount/RBAC、NetworkPolicy、PodSecurity/Admission 和声明式来源连成一条链；只改其中一处不能报完成。
- 接流门禁：发布前确认 readiness 是否真正代表可接流，startup/liveness/readiness 是否分工清楚，EndpointSlice 是否只包含 ready 端点，云 LB/Gateway 健康检查是否和应用接流语义一致。
- 镜像门禁：生产禁止 latest、漂移 tag、未绑定 digest、未验证运行时 imageID；镜像 tag、digest、签名/准入结果、GitOps commit 和 rollout revision 必须能互相追溯。
- 资源门禁：生产 workload 必须有 CPU/内存 requests，按场景补 limits、ephemeral-storage、QoS、Quota/LimitRange；禁止用“先不设资源观察一下”上线核心链路。
- 伸缩门禁：HPA/KEDA/VPA、PDB、滚动策略、节点弹性和 Quota 必须一起看；不能只看到 DesiredReplicas 或 Pod Running 就判断扩缩容成功。
- 配置门禁：ConfigMap/Secret 变更必须说明投递方式、应用是否热加载、是否需要 checksum annotation/rollout restart、旧 Pod 是否仍持有旧配置。
- Secret 门禁：禁止明文 Secret、日志输出密钥、把 kubeconfig/token/admin key 写入清单；External Secrets/Secrets Store CSI 必须验证同步、权限、轮换和应用 reload。
- 权限门禁：默认 ServiceAccount、cluster-admin、跨 namespace list/watch、automount token 默认开启、hostPath/hostNetwork/privileged 都要被主动质疑；例外必须最小化、限时、可审计。
- 网络门禁：NetworkPolicy 不只看业务端口，必须覆盖 DNS、监控采集、外部依赖、mesh sidecar/ambient、egress、跨 namespace、默认 deny 和回滚入口。
- 入口门禁：Ingress/Gateway/API Gateway 不只看对象存在，必须读 controller conditions、LB target health、证书、Service targetPort、EndpointSlice、请求 ID 和后端日志。
- 数据变更门禁：涉及 migration、Job/CronJob、初始化任务、schema 变更或一次性修复时，必须确认幂等、重跑、并发、失败清理、回滚和数据面证据；不能把 Job Completed 当业务完成。
- 回滚门禁：任何发布必须能说明回滚对象、回滚命令/声明式 revision、数据兼容、配置/Secret 回退、Gateway 权重回退、HPA/PDB 阻塞点和验证指标。
- 观测门禁：每次改动至少能关联 Events、conditions、日志、metrics、trace/request id 或审计中的一种运行时证据；只看 kubectl apply/rollout status 不够。
- 漂移门禁：live hotfix、kubectl edit/scale/patch 必须回写 Helm/Kustomize/GitOps 源，或记录 owner、过期时间、回滚和漂移监控；不能让 GitOps 自愈把修复覆盖。
- 生产结论门禁：完成结论必须同时说明声明式输入已变、控制器已接受、数据面已生效、用户入口已验证、监控无异常、回滚可用；缺任一项只能说部分验证。

## 场景执行卡

### 1. Kubernetes 版本与 API 迁移
- 适用：1.27-1.32 升级、弃用 API、旧 chart、托管集群版本差异。
- 动作：确认 server/client 版本、API resources、CRD conversion webhook、admission policy、PSA label、节点镜像/cgroup v2、containerd 版本。
- 证据：api-resources、deprecation scan、CRD served/storage versions、upgrade notes、Events、webhook 失败日志。
- 失败模式：只看 kubectl apply 成功，忽略控制器不识别字段、conversion webhook 超时、PSA 拒绝 privileged workload。

### 2. Workload、探针、滚动发布
- 适用：Deployment/StatefulSet/DaemonSet/Job/CronJob 异常、CrashLoop、卡发布、冷启动。
- 动作：检查 startup/readiness/liveness 分工、preStop、terminationGracePeriodSeconds、maxSurge/maxUnavailable、PDB、topologySpread、PriorityClass、Job backoffLimit、StatefulSet ordinal/PVC。
- 证据：rollout status/history、describe pod、Events、container lastState、probe 日志、EndpointSlice 接流变化、SLO 指标。
- 失败模式：liveness 依赖 DB、readiness 缺失导致未预热接流、PDB 与 maxUnavailable 互锁、preStop 短于 LB drain。

### 3. containerd / CRI / 镜像拉取
- 适用：ImagePullBackOff、RunContainerError、Exec format error、沙箱创建失败、私有仓库。
- 动作：确认 image tag/digest、架构 amd64/arm64、imagePullSecret、registry mirror、containerd snapshotter、RuntimeClass、seccomp/AppArmor、节点磁盘与 inode。
- 证据：Pod Events、kubelet 日志、containerd 日志、镜像 digest、节点架构、registry 返回码。
- 失败模式：latest 漂移、多架构 manifest 缺失、节点镜像切 containerd 后 Docker socket 依赖失效。

### 4. CNI、CoreDNS、NetworkPolicy
- 适用：Pod 间不通、DNS 慢、egress 失败、跨 namespace 访问、双栈问题。
- 动作：确认 CNI 类型和策略支持，检查 NetworkPolicy 默认 deny、DNS egress、kube-dns/CoreDNS、EndpointSlice、Service selector、SNAT/ENI/IPAM、MTU、IPv6/dual-stack；Cilium 场景补 L7 policy、Hubble、kube-proxy replacement 能力差异。
- 证据：NetworkPolicy 清单、CoreDNS logs/metrics、Pod 内解析结果、CNI agent logs、conntrack/MTU 线索、拒绝链路与允许链路对照。
- 失败模式：只放应用端口忘 DNS、VPC CNI IP 耗尽、Cilium/Calico 策略语义差异、CoreDNS 上游超时。

### 5. Ingress、Gateway API、API Gateway、云 LB
- 适用：404/502/503、TLS、路径重写、WebSocket/SSE、跨 namespace route、健康检查、认证鉴权、限流、WAF、mesh/GAMMA 绑定。
- 动作：检查 DNS、LB、IngressClass/GatewayClass、Gateway Listener、HTTPRoute/GRPCRoute、ReferenceGrant、TLS Secret、Service port/targetPort、health check、proxy timeout/body size；API Gateway 另查 JWT/OIDC、rate limit、WAF/TLS posture 与应用/mesh 策略叠加边界。
- 证据：Gateway/Route Accepted/Programmed/ResolvedRefs conditions、Ingress/Gateway controller logs、LB target health、证书链、EndpointSlice、请求 ID、后端日志、限流/WAF 命中记录。
- 失败模式：HTTPRoute Accepted=True 但 Programmed=False 被误判为生效、targetPort 写错、云 LB 健康检查路径和 readiness 不一致、跨云注解失效、多层限流叠加导致正常流量被拒。

### 6. Helm、Kustomize、CRD、GitOps
- 适用：环境漂移、Argo CD/Flux 不一致、hook/wave 乱序、CRD 升级。
- 动作：渲染 helm template/kustomize build，核对 values/overlay、schema、CRD 与 CR 时序、sync wave/hook、prune/self-heal、ignoreDifferences、shared resource owner；ApplicationSet/Fleet 场景补目标集群选择器和模板变量。
- 证据：渲染结果、live diff、Argo/Flux health/sync、ApplicationSet 生成对象、CRD conversion 日志、rollback revision、commit SHA。
- 失败模式：手工 kubectl edit 被 GitOps 覆盖，prune 删除共享 PVC/Secret/CRD，生产 overlay 漏配，多集群模板变量只在部分集群漂移。

### 7. HPA、VPA、KEDA、容量与成本
- 适用：不扩容、扩容抖动、Pending、成本突增、队列积压、idle cost、GPU/Spot 成本。
- 动作：确认 metrics-server/custom metrics/external metrics、HPA behavior、VPA mode、KEDA ScaledObject、min/maxReplicas、ResourceQuota、LimitRange、PDB、cluster autoscaler/Karpenter、节点 IP/CPU/内存/磁盘余量；补 requests/limits 右配、LB/PVC/日志/跨 AZ 流量成本分摊。
- 证据：HPA/KEDA conditions、metrics 查询、Quota 命中、Pod Pending Events、节点池扩容记录、业务队列指标、按 namespace/team 的资源与云账单标签。
- 失败模式：用 CPU 扩队列消费者、HPA 被 Quota/PDB/节点容量卡住、VPA 与 HPA 同改 CPU requests 导致震荡、只看计算资源忽略存储/LB/日志成本。

### 8. PodSecurity、RBAC、Secret、准入
- 适用：Forbidden、准入拒绝、Secret 轮换、镜像拉取、权限过大。
- 动作：检查 namespace PSA label、securityContext、runAsNonRoot、capabilities、hostPath/hostNetwork、ServiceAccount、Role/ClusterRole verbs/resources、automount token、External Secrets/Secrets Store CSI、admission webhook。
- 证据：Forbidden 错误、audit log、SubjectAccessReview、admission webhook response、Secret 引用与轮换时间、PodSecurity warnings。
- 失败模式：为读一个 Secret 授予 list/watch 全 namespace，旧 chart privileged 被 PSA 拒绝，Secret 更新后应用不热加载。

### 9. 供应链准入与制品可信
- 适用：镜像准入失败、漏洞例外、签名校验、SBOM/SLSA provenance、digest 漂移、私有仓库策略。
- 动作：核对镜像 digest 固定、签名验证、provenance/SBOM 证据、准入策略绑定的 subject、registry mirror 可信边界、漏洞例外范围/有效期/owner；只在 K8s 准入命中和运行时证据内判断，SCA/SBOM 生成与漏洞优先级归 dso。
- 证据：imageID/digest、admission response、policy report、registry 审计、签名验证结果、例外 CR/配置、Pod Events、GitOps commit。
- 失败模式：只固定 tag 未验 digest/signature、准入例外无过期时间、镜像被 mirror 替换后仍被放行、把扫描通过误判为运行时已部署可信制品。

### 10. Policy as Code 分层
- 适用：ValidatingAdmissionPolicy、Kyverno/Gatekeeper/OPA、Pod Security Standards、NetworkPolicy/RBAC 基线冲突、audit 到 enforce 晋级。
- 动作：分清 PSA 管 Pod 安全基线，VAP/Kyverno/Gatekeeper 管准入约束，RBAC 管谁能做什么，NetworkPolicy 管东西向/出向流量；检查 match 条件、namespace 选择器、failurePolicy、audit/enforce 状态、例外清单和渐进门禁。
- 证据：policy/admission conditions、policy report、audit log、denied request、namespace labels、GitOps diff、例外 owner/到期时间。
- 失败模式：audit 模式长期未切 enforce 却宣称已有保护、多个策略重复拒绝难以定位、为修发布关闭 admission/PSA/NetworkPolicy 而未设最小例外和回滚。

### 11. 存储、CSI、StatefulSet
- 适用：PVC Pending、挂载失败、跨 AZ、扩容、快照恢复、有状态升级。
- 动作：确认 StorageClass、provisioner、volumeBindingMode、reclaimPolicy、accessModes、fsGroup、拓扑/AZ、snapshot/backup、StatefulSet partition、数据格式兼容。
- 证据：PVC/PV describe、CSI controller/node logs、VolumeAttachment、节点拓扑、快照/恢复记录、应用写入验证。
- 失败模式：WaitForFirstConsumer 与节点选择冲突，单 AZ PV 调度到其他 AZ，回滚应用但数据 schema 已升级。

### 12. 多集群、服务网格、东西向流量
- 适用：Istio/Linkerd/Consul/Kuma、多集群服务发现、mTLS、流量拆分、熔断、Fleet/Cluster API/集群生命周期。
- 动作：确认注入方式、sidecar/ambient 模式、mTLS、AuthorizationPolicy、DestinationRule/VirtualService、retry/timeout/circuit breaker、east-west gateway、证书信任域；多集群补统一身份、网络连通模型、策略漂移、集群版本/插件生命周期。
- 证据：proxy config、mesh telemetry、sidecar logs、mTLS 状态、trace、跨集群 endpoint、策略命中结果、集群清单与同步状态。
- 失败模式：网格 retry 叠加应用 retry、ambient/sidecarless 按 sidecar 经验排障、跨集群证书信任域不一致、ApplicationSet 只在部分集群漂移。

### 13. 韧性、DR、节点压力、驱逐、调度
- 适用：OOMKilled、Evicted、NodeNotReady、磁盘压力、CPU throttling、调度失败、区域故障、Spot 替换、容量降级。
- 动作：检查 node conditions、taints/tolerations、requests/limits、ephemeral-storage、image GC、PID pressure、cgroup v2、topologySpread、affinity、PriorityClass、preemption；韧性补故障域、多 AZ、PDB、Karpenter/Cluster Autoscaler、备份恢复演练、混沌/故障注入验收和降级策略。
- 证据：Node describe、kubelet Events、metrics、Pod QoS、eviction threshold、调度器事件、节点池/Spot 中断记录、备份恢复记录、演练结果。
- 失败模式：只加 replicas 不加节点资源，忽略 ephemeral-storage requests，BestEffort Pod 压力下优先被驱逐，Karpenter Spot 替换与 PDB/PVC 拓扑冲突导致长时间 Pending。

### 14. 可观测与审计证据
- 适用：线上事故、变更验证、根因定位、权限与准入追踪、成本/容量归因。
- 动作：关联 kubectl describe/events/logs、metrics、traces、Ingress/Gateway logs、mesh telemetry、HPA/KEDA metrics、audit log、release markers、GitOps commit；补事件导出、control plane logs、OpenTelemetry trace、Prometheus label cardinality、exemplars、Hubble/Kiali/Loki 等证据边界。
- 证据：按时间线列症状、变更、控制器动作、用户影响、恢复动作；保留对象名、namespace、UID、版本、commit、request id，敏感字段脱敏。
- 失败模式：只看应用日志忽略 Events，Events 已过期未及时导出，指标无 namespace/pod/version/team 标签无法关联发布或成本，label cardinality 爆炸导致监控不可用。

### 15. 平台工程与租户边界
- 适用：namespace vending、租户隔离、自服务模板、golden path、配额/guardrail、平台产品化争议。
- 动作：本技能只验证 K8s 运行时 guardrail 是否生效：namespace/SA/RBAC/Quota/LimitRange/NetworkPolicy/PSA/admission/GitOps owner；IDP、Backstage、自服务产品设计归 plt。
- 证据：租户 namespace 清单、配额命中、策略报告、GitOps owner、模板渲染结果、audit log、成本标签。
- 失败模式：模板创建成功但准入/配额未生效，租户共用默认 SA 或 cluster-admin，golden path 没有漂移检测和回滚边界。

## 高频坑 / 防遗漏

- 改 workload：同步查 Service selector、EndpointSlice、readiness、PDB、HPA/KEDA、SA、PodSecurity、Events、rollout history。
- 改入口：同步查 DNS、云 LB、Ingress/GatewayClass、TLS、Route conditions、health check、Service targetPort、EndpointSlice、controller logs、API Gateway 认证/限流/WAF。
- 改网络：同步查 CNI、CoreDNS、NetworkPolicy 默认态、DNS egress、外部 API、监控采集、MTU、IPAM、双栈、eBPF 模式。
- 改扩缩容/成本：同步查 metrics 来源、HPA behavior、KEDA trigger、VPA mode、Quota/LimitRange、PDB、节点池、冷启动、requests 右配、LB/PVC/日志成本。
- 改安全/准入：同步查 PSA、securityContext、RBAC verbs/resources、audit、admission、Policy as Code、Secret 来源/轮换、imagePullSecret、digest/signature。
- 改存储：同步查 StorageClass、CSI、AZ 拓扑、VolumeAttachment、reclaimPolicy、扩容、快照恢复、StatefulSet 数据兼容。
- 改 GitOps/Helm：同步查渲染、diff、sync wave/hook、CRD 顺序、prune、ignoreDifferences、rollback revision、ApplicationSet/Fleet 目标集群。
- 改 mesh/多集群：同步查注入、mTLS、AuthorizationPolicy、retry/timeout、sidecar/ambient、telemetry、trace、信任域、东西向网关、策略漂移。
- 改节点/韧性：同步查 node pressure、taints、requests、ephemeral-storage、image GC、cgroup v2、RuntimeClass、Spot 中断、PDB、拓扑、备份恢复演练。
- 改多云：同步查 IAM/Workload Identity、LB 注解、CNI/IPAM、CSI/AZ、私有镜像、控制面日志、审计开关、托管控制面限制。

## 输出要求

1. 场景：明确属于版本/API、workload、containerd/CRI、网络/DNS、Ingress/Gateway/API Gateway、GitOps、弹性、准入供应链、Policy as Code、RBAC/PodSecurity、存储、网格、多集群、韧性/成本、节点压力、观测审计、多云哪类。
2. 环境：Kubernetes 小版本、云厂商/发行版、namespace、CNI/CSI/Ingress/Gateway/API Gateway/Mesh、container runtime、Policy/Admission 控制器、声明式来源；未读写需验证。
3. 影响面：列 DNS/LB、Gateway/Ingress、Service/EndpointSlice、Pod/Node、PVC、HPA/KEDA/PDB、RBAC/NetworkPolicy、Admission/Policy、GitOps/Helm/Kustomize、Secret、镜像制品、成本标签。
4. 证据：列命令或系统证据摘要，包括 describe、Events、logs、metrics、diff/render、audit、controller conditions、policy report、admission response、镜像 digest/signature。
5. 风险：接流、回滚、权限、密钥、网络隔离、存储持久化、节点容量、探针、准入误拒/漏放、漂移、多云差异、成本失控、韧性缺口。
6. 验证：dry-run/render/diff、连通性、权限最小化、准入策略命中、扩缩容触发、存储恢复、故障域演练、灰度 SLO、告警、回滚演练。
7. 联动：涉及 Terraform、CI/CD、应用代码、安全扫描、制品签发、测试矩阵、SLO/事故复盘、平台产品化、最终审计时说明切换对应技能，不在本技能越权完成。
8. 结论：标已验证/部分验证/无法验证；列剩余缺口和下一步，区分可直接执行与需目标集群验证。

## 约束

- 未确认声明式来源，不得把 kubectl edit、scale、patch 作为最终完成；只能作为带过期时间的止血。
- 未确认 Kubernetes/控制器/云厂商版本，不得复用 Ingress、Gateway、LB、CSI、CNI、IAM、Policy、Admission 注解或默认值。
- 禁止生产 latest、默认 ServiceAccount、cluster-admin、明文 Secret、无 requests/readiness/rollback 的 workload。
- 禁止无 requests/limits、无 PDB/HPA 影响判断、无 rollout history、无入口验证、无观测证据的核心 workload 直接上线。
- 禁止只看 Pod Running、Deployment Available、Job Completed、Helm diff clean、Argo Synced、HTTP 200 单点探测就报告生产健康。
- 禁止 readiness 查询慢依赖、liveness 查询外部依赖、startupProbe 缺失却把初次冷启动失败归因给应用不稳定。
- 禁止 kubectl apply 后不验 Ingress/Gateway/LB/Service/EndpointSlice/后端日志；入口链路未验只能说配置已提交。
- 禁止 ConfigMap/Secret 改完不触发 rollout、不验证旧 Pod 配置、不说明热加载机制和失败回退。
- 禁止为排障直接关闭 NetworkPolicy、PSA、mTLS、admission、签名校验或扩大 RBAC；必须写最小例外、证据、回滚和过期时间。
- 禁止把 Helm/GitOps diff 干净说成运行时健康；必须读 conditions、Events、logs/metrics。
- 禁止把扫描通过、签名存在或策略 audit 模式说成生产准入已 enforce；必须读实际准入结果和运行对象 digest。
- 禁止把应用健康接口、业务重试、DB 迁移、CI/CD 发布编排、安全扫描、测试矩阵、SLO 设计、平台产品路线写成本技能职责。
- 禁止输出 Secret、token、admin key、完整 kubeconfig、私有镜像凭据、审计日志中的敏感字段。
- 所有建议必须区分可直接执行与需目标集群验证。

## 高频 Bug 反例库

- 反例 1：liveness 查询数据库
  - 错法：数据库抖动时 liveness 失败，kubelet 批量重启 Pod，连接风暴放大故障。
  - 对法：liveness 只验证进程存活；readiness 反映下游依赖和接流；冷启动用 startupProbe。
  - 根因：把存活性、就绪性、依赖健康三种信号混成一个探针。
- 反例 2：readiness 缺失仍滚动发布
  - 错法：新 Pod 未预热就进入 EndpointSlice，LB 立即打流量导致 5xx。
  - 对法：readiness 覆盖启动缓存、连接池、关键依赖；发布观察 EndpointSlice 与 SLO。
  - 根因：只看容器 Running，没看服务是否可接流。
- 反例 3：Gateway API 跨 namespace 缺 ReferenceGrant
  - 错法：HTTPRoute 引用其他 namespace Service/TLS，Route Accepted=False 或 backend 无效。
  - 对法：补 ReferenceGrant，检查 Gateway/Route conditions 和 controller logs。
  - 根因：Gateway API 明确要求跨 namespace 引用授权。
- 反例 4：Gateway Accepted=True 但 Programmed=False
  - 错法：只看 Accepted=True 就认为入口生效，实际 listener、LB 或 controller 未完成下发。
  - 对法：同时检查 Accepted、Programmed、ResolvedRefs、controller logs、LB target health 与端到端请求。
  - 根因：Gateway API 的路由接受、引用解析和数据面编程是不同阶段。
- 反例 5：API Gateway 与 mesh 多层限流叠加
  - 错法：Gateway、mesh、应用各自设置 rate limit，正常流量被叠加拒绝。
  - 对法：统一限流层级和预算，核对 429/503 来源、请求 ID、策略命中与业务容量。
  - 根因：入口治理没有建立全链路容量预算。
- 反例 6：NetworkPolicy 默认 deny 忘放 DNS
  - 错法：只放业务端口，Pod 无法解析域名，外部依赖全失败。
  - 对法：显式放行 CoreDNS/kube-dns egress，再按依赖放行外部 API。
  - 根因：DNS 是运行时依赖，不是应用端口的一部分。
- 反例 7：HPA 指标不对应瓶颈
  - 错法：队列积压但 CPU 不高，HPA 不扩；或 CPU 抖动导致无效扩缩。
  - 对法：用 custom/external metrics 或 KEDA 绑定队列长度、延迟、吞吐等瓶颈指标。
  - 根因：把资源利用率误当业务负载信号。
- 反例 8：HPA 被 Quota/PDB/节点容量卡住
  - 错法：HPA DesiredReplicas 增长但 Pod Pending 或无法驱逐，误判为 HPA 失效。
  - 对法：同时查 HPA conditions、ResourceQuota、PDB、scheduler Events、cluster autoscaler/Karpenter。
  - 根因：扩容是控制器、调度、配额、节点池共同结果。
- 反例 9：VPA 与 HPA 同时控制 CPU
  - 错法：VPA 调 requests，HPA 又按 CPU 利用率扩缩，副本震荡。
  - 对法：明确 VPA recommendation/off 或仅管内存；HPA 使用稳定业务指标。
  - 根因：两个控制器改同一控制变量。
- 反例 10：GitOps prune 删除共享资源
  - 错法：从应用目录移除共享 Secret/PVC/CRD，自动同步把共享资源删掉。
  - 对法：共享资源独立 owner，prune 加门禁，删除前列消费者和备份/回滚。
  - 根因：资源所有权与应用目录边界混乱。
- 反例 11：Helm values 本地通过生产漏配
  - 错法：本地 values 有 imagePullSecret/limits，生产 overlay 漏掉导致 ImagePullBackOff 或 OOM。
  - 对法：对目标环境渲染并 diff，绑定 release revision 和 commit SHA。
  - 根因：验证了错误的声明式输入。
- 反例 12：ApplicationSet 模板变量漏配
  - 错法：多集群模板在部分集群生成不同 ServiceAccount、region 或策略，只有局部集群漂移。
  - 对法：按目标集群列生成对象、diff、sync status、cluster selector 和变量来源。
  - 根因：验证了模板仓库，未验证每个集群的渲染结果。
- 反例 13：PDB 与滚动策略互锁
  - 错法：replicas 少、maxUnavailable=0、PDB minAvailable 过高，rollout 或节点维护卡死。
  - 对法：联合校验 replicas、PDB、maxSurge/maxUnavailable、节点 drain 和 SLO。
  - 根因：可用性约束没有与发布/维护动作共同建模。
- 反例 14：containerd 后 Docker socket 依赖失效
  - 错法：节点从 dockershim 迁移到 containerd 后，CI/sidecar 仍挂 /var/run/docker.sock。
  - 对法：改用兼容 CRI 的构建/运行方案或隔离构建节点；验证 RuntimeClass 和节点镜像。
  - 根因：把 Docker daemon 当成 Kubernetes 运行时标准接口。
- 反例 15：镜像 tag 固定但未验 digest/signature
  - 错法：tag 看似固定，registry 或 mirror 中制品被替换，准入仍允许部署。
  - 对法：部署清单绑定 digest，准入校验签名/provenance，核对运行时 imageID 与 GitOps commit。
  - 根因：tag 是可变引用，不等于可信制品身份。
- 反例 16：Kyverno/Gatekeeper audit 长期未切 enforce
  - 错法：policy report 有违规但发布仍放行，团队误以为生产已有保护。
  - 对法：标明 audit/enforce 阶段、例外和截止时间，晋级前用 dry-run/admission 验证拒绝路径。
  - 根因：监控性策略和阻断性准入被混为一谈。
- 反例 17：PVC 单 AZ 绑定后跨 AZ 调度
  - 错法：Pod 被调到另一个 AZ，VolumeAttachment 失败或 Pending。
  - 对法：检查 StorageClass volumeBindingMode、PV node affinity、拓扑约束和节点池 AZ。
  - 根因：存储拓扑与调度拓扑未一起验证。
- 反例 18：Secret 轮换后应用不热加载
  - 错法：External Secrets 已更新，应用进程仍用旧连接串，重启后才恢复。
  - 对法：确认 Secret 投递方式、刷新延迟、应用 reload 机制和滚动重启策略。
  - 根因：K8s Secret 更新不等于应用内存配置已刷新。
- 反例 19：PSA 拒绝旧 chart
  - 错法：升级 namespace 到 restricted 后，旧 chart 的 privileged、hostPath、runAsRoot 被拒。
  - 对法：先 dry-run/admission 验证，改 securityContext 或设最小例外并限期移除。
  - 根因：PodSecurity Admission 替代 PSP 后，准入从部署时直接拦截。
- 反例 20：Service mesh retry 放大故障
  - 错法：Envoy/Istio retry 与应用 retry 叠加，下游抖动时请求倍增。
  - 对法：统一 retry/timeout budget，查 mesh telemetry 与应用日志，限制幂等请求重试。
  - 根因：多层重试没有共享超时和容量预算。
- 反例 21：Karpenter Spot 替换撞上 PDB/PVC 拓扑
  - 错法：Spot 中断后新节点不满足拓扑或 PDB 无法驱逐，Pod 长时间 Pending。
  - 对法：联合检查 NodePool、PDB、topologySpread、PV node affinity、DaemonSet overhead 和中断事件。
  - 根因：节点弹性、可用性约束和存储拓扑没有统一建模。
- 反例 22：节点 ephemeral-storage 未设 requests
  - 错法：日志/临时文件涨满磁盘，Pod 被 Evicted，但 CPU/内存看起来正常。
  - 对法：设置 ephemeral-storage requests/limits，检查 kubelet eviction、日志轮转和 emptyDir。
  - 根因：忽略磁盘和 inode 是 kubelet 驱逐信号。
- 反例 23：namespace 配额忽略非计算成本
  - 错法：只管 CPU/内存，LB、PVC、日志、跨 AZ 流量成本持续增长且无法归属。
  - 对法：补存储/LB/日志/流量标签和配额/预算告警，按 namespace/team 归因。
  - 根因：平台容量治理没有覆盖云资源和观测成本。
- 反例 24：只看应用日志忽略 Events
  - 错法：日志无报错就断言应用问题，漏掉 OOMKilled、FailedMount、FailedScheduling、ProbeFailed。
  - 对法：describe Pod/Node/PVC，导出 Events 并按时间线关联日志、指标、发布记录。
  - 根因：Kubernetes 故障常发生在应用进程外。
- 反例 25：只看 Pod Running
  - 错法：Pod Running 后就宣称上线成功，实际 readiness 未过、EndpointSlice 未接流或 LB target unhealthy。
  - 对法：同时看 readiness、EndpointSlice、Service targetPort、入口健康检查、真实请求和 SLO。
  - 根因：容器运行状态不等于用户入口可用。
- 反例 26：kubectl apply 后不验入口
  - 错法：Ingress/Gateway apply 成功就结束，实际 controller 没 Programmed、证书错或 targetPort 写错。
  - 对法：读 conditions、controller logs、LB target health、证书链、EndpointSlice 和后端请求日志。
  - 根因：声明式提交、控制器下发和数据面生效是三个阶段。
- 反例 27：ConfigMap 改了但 Pod 没重启
  - 错法：更新 ConfigMap 后等待业务恢复，旧 Pod 仍持有旧环境变量或启动时读取的配置。
  - 对法：确认挂载/环境变量/SDK 热加载机制，必要时用 checksum annotation 或 rollout restart。
  - 根因：K8s 对象更新不等于进程内配置更新。
- 反例 28：Secret 明文进 Git
  - 错法：为了快速发布把密码写进 YAML 或 values，后续被 GitOps、日志、审计和备份扩散。
  - 对法：使用 External Secrets、Secrets Store CSI 或密文管理，验证 RBAC、轮换、投递和脱敏。
  - 根因：把 Kubernetes Secret 误当加密边界。
- 反例 29：readiness 检查慢依赖
  - 错法：readiness 每次查慢 DB/外部 API，依赖抖动时 Pod 全部摘流，入口雪崩。
  - 对法：readiness 只表达本实例可接流能力；慢依赖用缓存状态、熔断、降级和业务指标验证。
  - 根因：把深度业务健康检查塞进接流开关。
- 反例 30：无 requests/limits 上核心链路
  - 错法：Deployment 未设 requests，调度看似成功，节点压力时 CPU 抢占、OOM 或 BestEffort 驱逐。
  - 对法：按压测和历史指标设置 requests，配合 limits、Quota、HPA 分母和 eviction 风险验证。
  - 根因：未把资源声明当成调度和稳定性的契约。
- 反例 31：RBAC 为省事给 cluster-admin
  - 错法：控制器报 Forbidden 后直接绑定 cluster-admin，误把权限扩大当修复。
  - 对法：用 SubjectAccessReview/audit 定位缺失 verbs/resources，授予 namespace/资源级最小权限。
  - 根因：没有区分排障提权和长期运行权限。
- 反例 32：migration Job 不可重跑
  - 错法：Job 部分成功后重跑造成重复写、锁冲突或数据二次迁移，回滚无路径。
  - 对法：迁移 Job 必须幂等、可重入、可观测，记录版本、RowsAffected、失败清理和回退方案。
  - 根因：把 Kubernetes Job Completed 当成数据层成功。
- 反例 33：rollback 只回镜像
  - 错法：回滚 Deployment 镜像，但 ConfigMap/Secret、DB schema、Gateway 权重、HPA 参数仍停留在新版本。
  - 对法：回滚清单列镜像、配置、Secret、入口、伸缩、数据兼容和验证指标，按 revision/commit 追溯。
  - 根因：云原生发布是多对象变更，不是单个镜像替换。
- 反例 34：NetworkPolicy 放开全 egress
  - 错法：为修 DNS 或外部 API 失败直接允许 0.0.0.0/0，长期绕过隔离。
  - 对法：先放 CoreDNS，再按命名空间、端口、FQDN/CIDR 或 egress gateway 最小放行并设过期复核。
  - 根因：没有把网络排障临时例外和长期策略分开。

## 提交前自检清单

- [ ] frontmatter name 使用 manifest canonical name（cloud-native），H1 为“云原生”，目录/URL slug 保持 cld。
- [ ] 行数 <= 500，正文不含 fenced code block。
- [ ] 覆盖 Kubernetes 1.27-1.32、containerd/CRI、CNI/CoreDNS、Ingress/Gateway API/API Gateway。
- [ ] 覆盖 HPA/VPA/KEDA、PodSecurity/NetworkPolicy/RBAC、Policy as Code、供应链准入、Helm/Kustomize/GitOps。
- [ ] 覆盖多集群/服务网格、节点压力/驱逐/探针/滚动发布、韧性/DR、成本观测、云厂商 LB/CSI 差异。
- [ ] 覆盖 Deployment/Service/Ingress/Gateway、probe 分工、resources、HPA/PDB、ConfigMap/Secret rollout、RBAC/NetworkPolicy/PodSecurity、image digest、migration/job、rollback。
- [ ] 已明确禁止 latest tag、无 requests/limits、secret 明文、只看 Pod Running、kubectl apply 后不验入口、readiness 查慢依赖。
- [ ] 证据要求含 kubectl describe、Events、logs、metrics、audit、diff/render、controller conditions、policy report、admission response、镜像 digest/signature。
- [ ] 高频 Bug 反例库不少于 10 条，且每条含错法、对法、根因。
- [ ] 边界没有把 Terraform、CI/CD、应用代码、安全扫描、SLO 设计、测试工程、平台产品化职责搬进本技能。
- [ ] 涉测试/回归联动 tst；最终改动由 aud 收口。
- [ ] 不输出 Secret、admin key、kubeconfig、token 或敏感审计字段。

## 2024-2026 新坑速查

- Kubernetes 1.27-1.32：PSP 已移除，PodSecurity Admission、ValidatingAdmissionPolicy、sidecar containers、Job/Indexed Job、API 弃用和 CRD conversion 行为需按目标小版本验证。
- containerd/CRI：dockershim 迁移后的 Docker socket、日志路径、镜像 GC、snapshotter、RuntimeClass 和节点镜像差异会改变排障入口。
- Gateway/API Gateway：conformance profile 不等于实现一致；HTTPRoute filters、GRPCRoute、TLSRoute、ReferenceGrant、Accepted/Programmed、GAMMA/mesh 绑定、JWT/OIDC、rate limit、WAF/TLS posture 要读 conditions 和控制器证据。
- Cilium/eBPF：NetworkPolicy、L7 policy、Hubble、kube-proxy replacement、Cilium Gateway、MTU/IPAM 能力强但与 Calico/VPC CNI 语义不同。
- CoreDNS：上游 DNS、NodeLocal DNSCache、缓存、loop、rewrite、stub domain 会把网络问题伪装成应用超时。
- HPA/KEDA/VPA：external metrics 延迟、scale-to-zero 冷启动、触发器认证、fallback、cooldownPeriod、VPA 改 requests 与 HPA 分母耦合都会影响扩缩容。
- Cluster autoscaler/Karpenter：快速节点替换会放大 PDB、拓扑、PVC、镜像预热、DaemonSet overhead、Spot 中断和成本波动。
- cgroup v2/节点 OS：CPU throttling、OOM、memory pressure、ephemeral-storage、PID pressure 指标口径变化会影响告警和扩缩容判断。
- Secrets Store CSI/External Secrets：外部密钥同步、权限、轮换延迟、应用热加载和审计链路要单独验证。
- Mesh ambient/sidecarless：mTLS、AuthorizationPolicy、telemetry、流量捕获不再完全等同 sidecar 模式。
- Multi-cluster：多集群 DNS、证书信任域、服务发现、东西向网关、Fleet/ApplicationSet、统一身份、故障域和配置漂移必须逐项验证。
- IPv6/dual-stack：Service、Pod CIDR、NetworkPolicy、DNS、Ingress、云 LB 健康检查和客户端源地址保留都可能变。
- Supply chain admission：SBOM、SLSA provenance、Sigstore/cosign、镜像 digest 与 admission policy 要绑定制品，不只看 tag；例外必须可审计、可过期、可回滚。
- Policy as Code：PSA、VAP、Kyverno/Gatekeeper/OPA、RBAC、NetworkPolicy 分层不同；audit/enforce、failurePolicy、namespace selector 和例外策略必须显式验证。
- 韧性/成本/观测：多 AZ、PDB、备份恢复、故障注入、requests 右配、idle/GPU/Spot、LB/PVC/日志/跨 AZ 流量、label cardinality 和事件导出都可能成为生产缺口。
- 托管云差异：EKS/GKE/AKS/ACK/TKE 的 IAM/Workload Identity、LB controller、CSI 拓扑、CNI IPAM、控制面日志和审计开关默认不同。

## 与相邻技能的边界

- 本技能负责：Kubernetes 对象、容器运行时、CNI/CoreDNS、Ingress/Gateway/API Gateway 运行时证据、Service Mesh、HPA/VPA/KEDA、PodSecurity/RBAC/NetworkPolicy、Policy as Code 命中证据、供应链准入命中证据、CSI/PVC、节点压力、多集群和运行时证据链。
- IaC / Terraform / terraform-iac（itf）：Terraform state、provider、plan/apply、云资源创建归 itf；Terraform 输出的集群/Helm/K8s 对象进入运行时排障后由本技能接手。
- DevSecOps / devsecops（dso）：SAST/DAST/SCA/SBOM 生成、签名策略设计、CI 安全门禁、漏洞优先级归 dso；K8s admission、PodSecurity、RBAC、NetworkPolicy、运行时制品 digest 的命中证据由本技能提供。
- 发布部署 / release-engineering（rls）：发布窗口、晋级、制品唯一性、灰度总控、回滚决策归 rls；K8s rollout、Gateway 权重、HPA/PDB/Events 证据由本技能提供。
- 后端工程 / backend-engineering（be）：应用健康接口、业务重试、DB/队列依赖、日志字段由 be；探针如何接流、Service/Mesh/Gateway 如何影响运行由本技能判断。
- 可观测性 / observability（obs）：SLI/SLO、告警、dashboard、incident/postmortem 归 obs；K8s Events、controller conditions、mesh telemetry、HPA/KEDA 指标、control plane logs 作为本技能证据输入。
- FinOps 云成本 / finops（fop）：预算、分摊模型、采购和组织成本治理归 fop；本技能只指出 K8s requests、节点池、PVC、LB、日志、跨 AZ 流量等运行时成本证据与风险。
- 平台工程 / platform-engineering（plt）：IDP、Backstage、golden path 产品设计、自服务平台路线归 plt；本技能只验证 namespace vending、租户隔离、配额、guardrail 的 K8s 运行时状态。
- 测试验证 / test-engineering（tst）：测试矩阵、回归、CI 证据、冒烟结论归 tst；本技能只列云原生风险点和目标集群验证项。
- 代码审计 / code-audit（aud）：任何技能正文或配置改动完成前由 aud 收口，核对需求、影响面、证据、缺口和是否越界。