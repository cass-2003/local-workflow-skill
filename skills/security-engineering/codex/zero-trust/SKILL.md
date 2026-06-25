---
name: zero-trust
description: 零信任架构、微隔离、持续验证、最小权限。当用户提到零信任、Zero Trust、微隔离、持续验证、BeyondCorp、ZTNA时使用。
disable-model-invocation: false
user-invocable: false
---

# 零信任安全架构

## 角色定义

你是零信任架构专家，精通身份验证和微隔离。目标：设计和评估零信任架构，实现"永不信任，始终验证"。

## 行为指令

1. **评估**: 现有架构 → 信任边界识别 → 差距分析
2. **设计**: 身份验证 → 设备信任 → 微隔离 → 策略引擎
3. **实施**: 分阶段推进 → 身份先行 → 网络隔离 → 持续监控
4. **验证**: 策略测试 → 绕过尝试 → 覆盖率评估

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 安全头检查 | mcp__redteam__security_headers_scan | — |
| CORS 检查 | mcp__redteam__cors_scan | — |
| OAuth 扫描 | mcp__redteam__oauth_scan | — |
| JWT 测试 | mcp__redteam__jwt_scan | — |
| K8s 安全 | mcp__redteam__k8s_scan | — |
| 端口扫描 | mcp__redteam__port_scan | — |

## 决策树

```
零信任任务？
├── 三大核心原则
│   ├── 显式验证 (Verify Explicitly)
│   │   ├── 身份 → 用户身份 (MFA/SSO/Passwordless)
│   │   ├── 设备 → 设备状态 (合规性/健康度/注册)
│   │   ├── 位置 → 地理位置/网络位置/IP 信誉
│   │   ├── 行为 → 访问模式/异常检测
│   │   └── 风险 → 实时风险评分 → 自适应策略
│   ├── 最小权限 (Least Privilege)
│   │   ├── JIT → Just-In-Time 访问 (按需/限时)
│   │   ├── JEA → Just-Enough-Access (仅够完成任务)
│   │   ├── RBAC/ABAC → 基于角色/属性的访问控制
│   │   └── 数据分类 → 按敏感度限制访问
│   └── 假设被入侵 (Assume Breach)
│       ├── 微隔离 → 限制爆炸半径
│       ├── 端到端加密 → 即使内网也加密
│       ├── 持续监控 → 实时行为分析
│       └── 自动响应 → 异常即阻断
├── 架构组件
│   ├── 策略引擎 (PDP)
│   │   ├── 输入 → 主体+资源+动作+上下文
│   │   ├── 评估 → 策略匹配 → 风险计算
│   │   ├── 决策 → 允许/拒绝/需 Step-up
│   │   └── 默认 → 拒绝 (Deny by Default)
│   ├── 策略执行点 (PEP)
│   │   ├── 网络 → ZTNA 网关/SDP/反向代理
│   │   ├── 应用 → API 网关/服务网格 Sidecar
│   │   └── 数据 → DLP/加密/访问日志
│   ├── 身份提供者 (IdP)
│   │   ├── 认证 → MFA/Passwordless/FIDO2
│   │   ├── SSO → SAML/OIDC 集中认证
│   │   └── 目录 → Entra ID/Okta/Keycloak
│   └── 持续监控
│       ├── UEBA → 用户实体行为分析
│       ├── SIEM → 安全事件关联
│       ├── EDR → 端点检测
│       └── NTA → 网络流量分析
├── 微隔离实施
│   ├── 网络层
│   │   ├── K8s NetworkPolicy → deny-all + 白名单
│   │   ├── 云安全组 → 最小入出站规则
│   │   └── 服务网格 → Istio/Linkerd mTLS
│   ├── 应用层
│   │   ├── 服务间 mTLS → 双向证书认证
│   │   ├── SPIFFE/SPIRE → 服务身份框架
│   │   └── API 网关 → 请求级策略执行
│   └── 数据层
│       ├── 加密 → 传输(TLS) + 存储(AES-256)
│       ├── 分类标签 → 数据敏感度标记
│       └── 访问控制 → 列级/行级权限
├── 成熟度评估
│   ├── Level 1 传统 → 基于网络边界/静态ACL/有限可见性
│   ├── Level 2 进阶 → 身份感知/设备信任/基本隔离
│   └── Level 3 最优 → 持续验证/自适应策略/全面隔离/自动响应
└── 安全测试
    ├── 策略绕过 → 未授权访问/权限提升
    ├── 横向移动 → 微隔离有效性验证
    ├── 认证绕过 → MFA/SSO 攻击
    ├── 设备伪造 → 伪装合规设备
    └── 持续验证 → 会话劫持/Token 重放
```

## 零信任 vs 传统安全

| 维度 | 传统 | 零信任 |
|------|------|--------|
| 信任模型 | 内网可信 | 永不信任 |
| 边界 | 网络边界 | 身份边界 |
| 访问控制 | 网络 ACL | 策略引擎 (PDP/PEP) |
| 认证 | 一次登录 | 持续验证 |
| 加密 | 仅外部 | 端到端 |
| 隔离 | VLAN | 微隔离 |
| 监控 | 边界流量 | 全流量 + 行为 |

## 实施路线图

| 阶段 | 目标 | 关键动作 |
|------|------|----------|
| 1. 身份 | 强认证 | MFA 全覆盖 + SSO + 条件访问 |
| 2. 设备 | 设备信任 | MDM/EDR + 合规检查 + 证书 |
| 3. 网络 | 微隔离 | ZTNA + NetworkPolicy + mTLS |
| 4. 应用 | 应用保护 | API 网关 + WAF + 服务网格 |
| 5. 数据 | 数据保护 | 分类 + 加密 + DLP |
| 6. 监控 | 持续验证 | UEBA + SIEM + 自动响应 |

## 输出格式

```markdown
## 零信任评估报告
- **成熟度**: [初始/发展/优化 + 各支柱评分]
- **身份安全**: [MFA 覆盖率/SSO 接入率/条件访问策略]
- **网络隔离**: [微隔离覆盖率/ZTNA 部署状态]
- **数据保护**: [分类覆盖率/加密状态/DLP 策略]
- **Gap 分析**: [差距项 + 优先级 + 建议]
- **路线图**: [短期/中期/长期实施计划]
```

## 约束

- 零信任是持续旅程，非一次性项目
- 从高风险资产和用户群体开始（非全面铺开）
- 用户体验不能显著下降（透明安全）
- 遗留系统需特殊处理（代理/网关封装）

## 零信任架构实施

```yaml
# === 核心原则 ===
# 1. 永不信任, 始终验证 (Never Trust, Always Verify)
# 2. 最小权限访问 (Least Privilege)
# 3. 假设已被入侵 (Assume Breach)

# === 身份验证层 ===
# Keycloak 配置示例 (OIDC Provider)
# realm-export.json
{
  "realm": "corp",
  "sslRequired": "all",
  "bruteForceProtected": true,
  "failureFactor": 5,
  "maxDeltaTimeSeconds": 600,
  "otpPolicyType": "totp",
  "otpPolicyAlgorithm": "HmacSHA256",
  "clients": [{
    "clientId": "internal-app",
    "protocol": "openid-connect",
    "publicClient": false,
    "authorizationServicesEnabled": true,
    "directAccessGrantsEnabled": false
  }]
}
```

## 微隔离 (Micro-Segmentation)

```bash
# === Kubernetes NetworkPolicy ===
cat << 'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-default
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
EOF

# 仅允许特定服务间通信
cat << 'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
spec:
  podSelector:
    matchLabels:
      app: api-server
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - port: 5432
EOF

# === iptables 主机微隔离 ===
# 默认拒绝所有
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
# 仅允许必要端口
iptables -A INPUT -p tcp --dport 443 -s 10.0.1.0/24 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 5432 -d 10.0.2.10 -j ACCEPT
```

## 设备信任评估

```bash
# === 设备合规检查 (伪代码) ===
# 每次访问前评估设备状态
device_check:
  os_updated: patch_level >= "2026-02"
  disk_encrypted: bitlocker_enabled or filevault_enabled
  antivirus: running and signatures_updated
  firewall: enabled
  jailbroken: false
  certificate: valid_client_cert

# 不合规 → 降级访问或拒绝
# 合规 → 授予请求的资源访问

# === mTLS 双向认证 ===
# Nginx 配置
# ssl_client_certificate /etc/nginx/ca.crt;
# ssl_verify_client on;
# ssl_verify_depth 2;

# 生成客户端证书
openssl req -new -key client.key -out client.csr -subj "/CN=device-001"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

# 测试
curl --cert client.crt --key client.key https://api.corp.com/resource
```

## 零信任评估框架

```
CISA 零信任成熟度模型 (5 支柱):
1. 身份 (Identity): MFA → 无密码 → 持续认证
2. 设备 (Device): 资产清单 → 合规检查 → 实时评估
3. 网络 (Network): 分段 → 微隔离 → 加密所有流量
4. 应用 (Application): SSO → 动态授权 → 持续监控
5. 数据 (Data): 分类 → 加密 → DLP → 最小暴露

评估检查:
- [ ] 所有访问经过身份验证 (包括内部)
- [ ] MFA 覆盖所有用户和管理接口
- [ ] 网络分段, 无扁平内网
- [ ] 日志集中收集, 异常行为检测
- [ ] 最小权限, 定期审查
- [ ] 数据加密 (传输 + 存储)
```

