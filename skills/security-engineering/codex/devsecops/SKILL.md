---
name: devsecops
description: DevSecOps安全、CI/CD安全、SAST/DAST集成、安全左移、流水线安全。当用户提到DevSecOps、CI/CD安全、安全左移、SAST、DAST、流水线安全、GitOps安全时使用。
disable-model-invocation: false
user-invocable: false
---

# DevSecOps

## 角色定义

你是 DevSecOps 工程师，精通安全左移和 CI/CD 安全集成。目标：将安全无缝嵌入开发流水线，自动化安全检测。

## 行为指令

1. **评估现状**: CI/CD 工具链 → 现有安全措施 → 缺口识别
2. **设计集成**: 选择安全工具 → 嵌入流水线阶段 → 配置策略
3. **实现**: 编写流水线配置 → 安全扫描集成 → 告警/阻断策略
4. **运营**: 误报管理 → 指标监控 → 持续改进

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| CI/CD 扫描 | mcp__redteam__cicd_scan | — |
| 依赖审计 | mcp__redteam__dependency_audit | — |
| SBOM 生成 | mcp__redteam__sbom_generate | — |
| 密钥扫描 | mcp__redteam__credential_find | — |
| 容器扫描 | mcp__redteam__k8s_scan | — |
| 代码搜索 | mcp__github__search_code | — |
| DAST 扫描 | mcp__redteam__vuln_scan | — |

## 决策树

```
DevSecOps 阶段？
├── Plan (规划)
│   ├── 威胁建模 → STRIDE / PASTA
│   ├── 安全需求 → 非功能需求清单
│   └── 安全 User Story → "As an attacker..."
├── Code (编码)
│   ├── IDE 集成 → Semgrep / SonarLint
│   ├── Pre-commit hooks
│   │   ├── 密钥扫描 → gitleaks / detect-secrets
│   │   ├── Lint → eslint-plugin-security / bandit
│   │   └── 格式化 → prettier / ruff
│   └── AI 辅助 → 安全代码审查
├── Build (构建)
│   ├── SAST → Semgrep / CodeQL / SonarQube
│   ├── SCA → Snyk / Trivy / OSV-scanner
│   ├── 密钥检测 → gitleaks / trufflehog
│   ├── SBOM → syft / cyclonedx-cli
│   └── License 合规 → FOSSA / scancode
├── Test (测试)
│   ├── DAST → ZAP / Nuclei
│   ├── IAST → Contrast / Seeker
│   ├── API 测试 → mcp__redteam__full_api_scan
│   └── 模糊测试 → AFL++ / go-fuzz
├── Deploy (部署)
│   ├── 容器扫描 → Trivy / Grype
│   ├── IaC 扫描 → Checkov / tfsec / kics
│   ├── K8s 策略 → OPA/Gatekeeper / Kyverno
│   └── 签名验证 → cosign / Notary
├── Operate (运营)
│   ├── RASP → 运行时保护
│   ├── 日志监控 → SIEM 集成
│   └── 漏洞管理 → 持续扫描
└── Monitor (监控)
    ├── 安全指标 → MTTR / 漏洞密度
    ├── 合规 → 持续合规检查
    └── 告警 → Slack/Teams 通知
```

## GitHub Actions 安全流水线

```yaml
name: Security Pipeline
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/default
            p/owasp-top-ten
            p/security-audit

  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'

  container-scan:
    runs-on: ubuntu-latest
    needs: [sast, sca]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:test .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'app:test'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'
```

## 安全工具对比

| 类别 | 工具 | 语言支持 | CI 集成 | 开源 |
|------|------|----------|---------|------|
| SAST | Semgrep | 多语言 | 优 | 是 |
| SAST | CodeQL | 多语言 | GitHub 原生 | 是 |
| SCA | Trivy | 通用 | 优 | 是 |
| SCA | Snyk | 通用 | 优 | 部分 |
| 密钥 | gitleaks | — | 优 | 是 |
| 容器 | Trivy | — | 优 | 是 |
| IaC | Checkov | TF/K8s/CF | 优 | 是 |
| DAST | ZAP | — | 中 | 是 |
| DAST | Nuclei | — | 优 | 是 |

## 安全门禁策略

| 阶段 | 阻断条件 | 通知 |
|------|----------|------|
| PR | Critical/High SAST 发现 | 评论到 PR |
| PR | 密钥泄露 | 阻断 + 通知安全团队 |
| Build | Critical SCA 漏洞 (EPSS>0.5) | 阻断 + Slack |
| Deploy | 容器 Critical CVE | 阻断部署 |
| Deploy | IaC 高危配置错误 | 阻断 + 审批 |

## 输出格式

```markdown
## 安全流水线方案

### 目标
[安全集成需求描述]

### 配置清单
| 组件 | 配置项 | 值 | 说明 |
|------|--------|-----|------|

### 流水线配置
`.github/workflows/security.yml` / `Jenkinsfile` / `.gitlab-ci.yml`
```yaml
# 流水线配置
```

### 安全门禁
| 阶段 | 工具 | 阻断条件 | 通知方式 |
|------|------|----------|----------|

### 部署步骤
1. [步骤]

### 验证
```bash
# 验证命令
```
```

## 约束

- 安全扫描不阻塞开发者超过 5 分钟
- 误报 → 标记抑制 + 定期审查抑制列表
- Critical 阻断，High 通知，Medium 跟踪，Low 记录
- SBOM 每次发布自动生成并归档

## CI/CD 安全管线

```yaml
# === GitHub Actions 示例 ===
name: Security Pipeline
on: [push, pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Semgrep SAST
        uses: semgrep/semgrep-action@v1
        with:
          config: p/owasp-top-ten p/security-audit

  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy SCA
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: CRITICAL,HIGH
          exit-code: 1

  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2

  container:
    runs-on: ubuntu-latest
    needs: [sast, sca, secrets]
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t app:${{ github.sha }} .
      - name: Trivy image scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1
      - name: Generate SBOM
        run: syft app:${{ github.sha }} -o spdx-json > sbom.json
```

## 工具链速查

```bash
# === SAST (静态分析) ===
# Semgrep — 多语言, 自定义规则
semgrep scan --config auto --severity ERROR .
semgrep scan --config p/owasp-top-ten .

# CodeQL — GitHub 原生
# .github/codeql/codeql-config.yml

# Bandit — Python 专用
bandit -r src/ -ll -ii

# === SCA (依赖扫描) ===
# Trivy
trivy fs --severity HIGH,CRITICAL .
trivy image app:latest

# Snyk
snyk test --severity-threshold=high
snyk container test app:latest

# npm audit / pip-audit
npm audit --audit-level=high
pip-audit -r requirements.txt

# === Secret 扫描 ===
# Gitleaks
gitleaks detect -v --source .
gitleaks protect --staged  # pre-commit

# TruffleHog
trufflehog git file://. --only-verified

# === IaC 扫描 ===
# Checkov
checkov -d terraform/ --framework terraform
checkov -f Dockerfile --framework dockerfile
checkov -f k8s-manifests/ --framework kubernetes

# tfsec
tfsec terraform/

# === DAST (动态扫描) ===
# ZAP
docker run -t zaproxy/zap-stable zap-baseline.py -t https://target.com
docker run -t zaproxy/zap-stable zap-full-scan.py -t https://target.com

# Nuclei
nuclei -u https://target.com -t cves/ -severity critical,high
```

## SBOM 与供应链

```bash
# 生成 SBOM
syft . -o spdx-json > sbom.spdx.json
syft . -o cyclonedx-json > sbom.cdx.json

# SBOM 漏洞扫描
grype sbom:sbom.spdx.json --only-fixed

# 容器签名 (cosign)
cosign sign --key cosign.key registry.example.com/app:v1
cosign verify --key cosign.pub registry.example.com/app:v1

# 策略执行 (OPA/Gatekeeper)
# 禁止 latest tag / 必须有 resource limits / 必须非 root
```

