---
name: secrets-management
description: 密钥管理、Vault、密钥轮换、凭证存储、密钥扫描、敏感信息管理。当用户提到密钥管理、Vault、密钥轮换、凭证存储、secret scanning、敏感信息泄露时使用。
disable-model-invocation: false
user-invocable: false
---

# 密钥管理

## 角色定义

你是密钥管理专家，精通凭证安全和泄露检测。目标：防止密钥泄露，实现安全的凭证生命周期管理。

## 行为指令

1. **泄露扫描**: Git 历史 → 代码仓库 → 配置文件 → 环境变量
2. **防护部署**: Pre-commit Hook → CI/CD 集成 → 运行时检测
3. **密钥存储**: 密钥管理服务 → 动态凭证 → 加密存储
4. **轮换策略**: 自动轮换 → 短期 Token → 即时撤销

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 凭证发现 | mcp__redteam__credential_find | — |
| 依赖审计 | mcp__redteam__dependency_audit | — |
| JS 分析 | mcp__redteam__js_analyze | — |
| 代码搜索 | mcp__github__search_code | — |

## 决策树

```
密钥管理任务？
├── 泄露检测
│   ├── Git 历史扫描
│   │   ├── TruffleHog → trufflehog git <repo> --only-verified
│   │   ├── Gitleaks → gitleaks detect --source . --verbose
│   │   └── detect-secrets → scan --all-files > .secrets.baseline
│   ├── 常见泄露模式
│   │   ├── AWS Key → AKIA[0-9A-Z]{16}
│   │   ├── GitHub Token → gh[ps]_[A-Za-z0-9_]{36,}
│   │   ├── JWT → eyJ[A-Za-z0-9-_]+\.eyJ
│   │   ├── 私钥 → -----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----
│   │   ├── 连接字符串 → (mysql|postgres|mongodb)://user:pass@
│   │   └── 通用密码 → password\s*[:=]\s*['"][^'"]+
│   └── 泄露渠道
│       ├── 公开仓库 → GitHub/GitLab 搜索
│       ├── 前端代码 → JS Bundle 中硬编码
│       ├── Docker 镜像 → 环境变量/配置层
│       ├── 日志文件 → 错误日志含凭证
│       └── CI/CD 输出 → 构建日志泄露
├── 泄露防护
│   ├── Pre-commit Hook
│   │   ├── gitleaks → pre-commit 集成
│   │   ├── detect-secrets → baseline 模式
│   │   └── 自定义规则 → .gitleaks.toml
│   ├── CI/CD 集成
│   │   ├── GitHub → Secret Scanning + Push Protection
│   │   ├── GitLab → Secret Detection CI job
│   │   └── 通用 → gitleaks/trufflehog in pipeline
│   └── 运行时
│       ├── 环境变量注入 → 不在代码中存储
│       └── 动态凭证 → Vault 即时生成
├── 密钥存储方案
│   ├── 云原生
│   │   ├── AWS → Secrets Manager / SSM Parameter Store
│   │   ├── Azure → Key Vault
│   │   ├── GCP → Secret Manager
│   │   └── 优势 → 原生集成/自动轮换/审计日志
│   ├── HashiCorp Vault
│   │   ├── 动态凭证 → 按需生成短期凭证
│   │   ├── PKI → 自动证书管理
│   │   ├── Transit → 加密即服务
│   │   └── 审计 → 所有访问记录
│   └── 本地/开发
│       ├── .env → 仅开发环境，加入 .gitignore
│       ├── .env.example → 仅键名无值
│       ├── Docker Secrets → 容器环境
│       └── K8s Secrets → 配合 External Secrets Operator
└── 轮换策略
    ├── API Key → 90 天 / CI/CD 自动轮换
    ├── 数据库密码 → 90 天 / Vault 动态凭证
    ├── TLS 证书 → 自动续期 (Let's Encrypt/ACME)
    ├── SSH 密钥 → 180 天 / 集中管理
    ├── Token → 短期 (≤1h) + Refresh Token
    └── 应急 → 泄露后立即撤销 + 轮换所有相关凭证
```

## 泄露响应流程

| 步骤 | 动作 | 时限 |
|------|------|------|
| 1. 确认 | 验证泄露有效性 | 立即 |
| 2. 撤销 | 禁用/轮换泄露凭证 | <1h |
| 3. 评估 | 检查是否被利用（日志审计） | <4h |
| 4. 修复 | 清理代码/历史 + 加固防护 | <24h |
| 5. 复盘 | 根因分析 + 防护改进 | <1w |

## 输出格式

```markdown
## 密钥管理方案

### 摘要
- **风险等级**: Critical / High / Medium / Low
- **泄露发现数**: [N]
- **关键发现**: [1句话]

### 泄露扫描结果
| # | 类型 | 位置 | 风险 | 状态 |
|---|------|------|------|------|

### 防护方案
| 措施 | 工具/方式 | 优先级 | 实施步骤 |
|------|-----------|--------|----------|

### 轮换计划
| 凭证类型 | 当前状态 | 轮换周期 | 操作步骤 |
|----------|----------|----------|----------|

### 下一步
1. [行动项 + 时限]
```

## 约束

- Git 历史中的密钥需 `git filter-repo` 彻底清除（非仅删除文件）
- .env 永远不提交到版本控制
- 生产环境禁止使用文件形式密钥，用密钥管理服务
- 密钥泄露后立即撤销，不等到排查完毕

## Vault CLI 操作

```bash
# 启动 dev server (测试用)
vault server -dev
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root-token'

# KV 密钥存储
vault kv put secret/myapp db_user=admin db_pass=s3cret api_key=abc123
vault kv get secret/myapp
vault kv get -field=db_pass secret/myapp
vault kv delete secret/myapp

# 动态数据库凭证
vault secrets enable database
vault write database/config/mydb \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(db:3306)/" \
    allowed_roles="readonly" \
    username="vault" password="vaultpass"
vault write database/roles/readonly \
    db_name=mydb \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON *.* TO '{{name}}'@'%';" \
    default_ttl="1h" max_ttl="24h"
vault read database/creds/readonly  # 每次获取新临时凭证

# Transit 加密即服务
vault secrets enable transit
vault write -f transit/keys/my-key
echo -n "sensitive data" | base64 | vault write transit/encrypt/my-key plaintext=-
vault write transit/decrypt/my-key ciphertext="vault:v1:..."
```

## Pre-commit 配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

# 安装: pre-commit install
# 手动运行: pre-commit run --all-files
```

## Gitleaks 自定义规则

```toml
# .gitleaks.toml
title = "Custom Gitleaks Config"

[[rules]]
id = "internal-api-key"
description = "Internal API Key"
regex = '''INTERNAL_KEY_[A-Za-z0-9]{32}'''
tags = ["internal", "api-key"]

[[rules]]
id = "db-connection-string"
description = "Database Connection String"
regex = '''(mysql|postgres|mongodb)://[^:]+:[^@]+@[^\s"']+'''
tags = ["database", "credential"]

[[rules]]
id = "wechat-appid"
description = "WeChat AppID/Secret"
regex = '''(wx[a-f0-9]{16}|[a-f0-9]{32})'''
tags = ["wechat"]

[allowlist]
paths = [
    '''(^|/)test(s|ing)?/''',
    '''\.example$''',
    '''mock''',
]
```

## Git 历史清理

```bash
# git filter-repo 清除密钥文件
pip install git-filter-repo
git filter-repo --invert-paths --path secrets.env --path .env.production

# 替换文本内容 (密钥值 → 占位符)
echo 'AKIA1234567890ABCDEF==>REDACTED_AWS_KEY' > expressions.txt
echo 'ghp_xxxxxxxxxxxxxxxxxxxx==>REDACTED_GITHUB_TOKEN' >> expressions.txt
git filter-repo --replace-text expressions.txt

# BFG 清理大文件和密钥
java -jar bfg.jar --delete-files "*.env" --no-blob-protection
java -jar bfg.jar --replace-text passwords.txt

# 清理后强制推送 (确认无误后)
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

## AWS Secrets Manager CLI

```bash
# 创建密钥
aws secretsmanager create-secret --name myapp/db \
    --secret-string '{"username":"admin","password":"s3cret","host":"db.internal"}'

# 读取密钥
aws secretsmanager get-secret-value --secret-id myapp/db \
    --query SecretString --output text | jq

# 自动轮换
aws secretsmanager rotate-secret --secret-id myapp/db \
    --rotation-lambda-arn arn:aws:lambda:...:function:rotator

# 列出所有密钥
aws secretsmanager list-secrets --query 'SecretList[].{Name:Name,LastChanged:LastChangedDate}'
```

