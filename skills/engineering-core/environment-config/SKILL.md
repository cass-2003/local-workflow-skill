---
name: environment-config
description: "环境变量与配置管理实战。覆盖 12-Factor App 第三条 Config、配置层级（默认值 < 配置文件 < env vars < CLI flags）、dotenv 与 .env.local 模式、secret 与 config 区分、运行时 vs 构建时配置、SSR/CSR 配置注入、配置 schema 校验、kubernetes ConfigMap/Secret、Vault 集成、运行时热重载、不同环境配置策略、防 .env 提交工具（git-secret/gitleaks）。当用户提到环境变量、env vars、12-factor、dotenv、.env、ConfigMap、Secret、配置管理、配置层级、Vault、AWS Parameter Store、SSM、配置注入 时使用。"
---

# Environment Config Skill — 配置管理

## 何时使用

- 启动 / 部署多环境项目（dev / staging / prod）
- 排查"为什么 prod 用了错的 DB"
- 防 secrets 进 git
- 设计配置注入到 Docker / K8s / Vercel / Lambda
- 区分 build-time vs runtime config

## 一、12-Factor #3：Config

> "Config that varies between deploys is stored in environment variables."

**关键**：
- ✅ env vars 严格区分 code 与 deploy
- ✅ 不在 git 里
- ✅ 每个 deploy 自己一套
- ✅ 不同环境差异**只在 env vars**，code 完全相同

## 二、Config 层级（合并优先级）

```
[lowest → highest 优先级]

1. 代码默认值          (硬编码，最后兜底)
2. 配置文件默认         (config/default.yaml)
3. 环境特定文件         (config/production.yaml)
4. 本地覆盖文件         (config/local.yaml — gitignored)
5. 环境变量            (NODE_ENV / PORT / DATABASE_URL)
6. CLI flags          (--port=8080)
```

后面的覆盖前面的。运行时 config = merge(defaults, files, env, flags)。

## 三、Secret vs Config

| 维度 | Config | Secret |
|---|---|---|
| 例子 | `PORT`, `LOG_LEVEL`, `FEATURE_X_ENABLED` | DB 密码, API key, JWT secret |
| 谁能看 | 任何工程师 | 仅运维 / 管理员 |
| 存哪 | env vars / ConfigMap / yaml | Vault / Secrets Manager / K8s Secret + KMS |
| 轮换 | 罕见 | 定期轮换 |
| 日志 | 可打印 | **永远不打印** |

**永远分开存**。混在一起 → 给某人 read config 就给了 read secret。

## 四、`.env` 文件模式

```bash
# .env.example  ← 加入 git，列所有需要的 key
DATABASE_URL=postgres://user:pass@localhost/mydb
REDIS_URL=redis://localhost:6379
JWT_SECRET=replace-me-in-prod

# .env  ← gitignored，本机实际值
DATABASE_URL=postgres://localhost/mydb_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-only-secret-12345
```

`.gitignore` 必须含：

```
.env
.env.local
.env.*.local
!.env.example
```

**Node.js (Vite/Next 内置)**：

```
.env                # 所有环境
.env.local          # 本机覆盖（gitignored）
.env.development    # dev 时
.env.production     # prod 时
```

注意：**`.env.production` 通常不进 git**（实际 prod 值由 CI 注入），只有 `.env.example` 入仓。

## 五、加载与校验（启动即崩）

```typescript
// src/config.ts
import { z } from 'zod'
import 'dotenv/config'         // 仅 dev，prod 由部署平台注入

const Env = z.object({
  NODE_ENV:     z.enum(['development', 'staging', 'production', 'test']),
  PORT:         z.coerce.number().int().positive().default(8080),
  DATABASE_URL: z.string().url(),
  REDIS_URL:    z.string().url().optional(),
  JWT_SECRET:   z.string().min(32, 'JWT_SECRET must be 32+ chars'),
  LOG_LEVEL:    z.enum(['debug','info','warn','error']).default('info'),
})

const result = Env.safeParse(process.env)
if (!result.success) {
  console.error('Invalid env config:')
  for (const issue of result.error.issues) {
    console.error(`  ${issue.path.join('.')}: ${issue.message}`)
  }
  process.exit(1)
}
export const env = result.data
```

```python
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str
    redis_url: str | None = None
    jwt_secret: str = Field(min_length=32)
    port: int = 8080
    log_level: str = 'info'

settings = Settings()        # 失败抛 ValidationError → 启动崩
```

```go
// envconfig 或 viper
import "github.com/kelseyhightower/envconfig"
type Config struct {
    Port        int    `envconfig:"PORT" default:"8080"`
    DatabaseURL string `envconfig:"DATABASE_URL" required:"true"`
    JWTSecret   string `envconfig:"JWT_SECRET" required:"true"`
}
var cfg Config
if err := envconfig.Process("", &cfg); err != nil {
    log.Fatal(err)
}
```

**关键**：缺关键 env 在启动时就崩，不要让"运行到某个 endpoint 才发现 secret 没配"。

## 六、运行时 vs 构建时

### Build-time（编译进 bundle）

- 公开值（公开 API URL、版本号、feature flag 默认）
- Vite: `import.meta.env.VITE_*`
- Next.js: `process.env.NEXT_PUBLIC_*`
- Webpack DefinePlugin

```typescript
// 这些在构建时被替换为字面量
const apiUrl = import.meta.env.VITE_API_URL
```

### Runtime（容器启动时读）

- 后端配置 / secret
- K8s ConfigMap / Secret 注入
- 必须是 server-side（SSR / API route）

**陷阱**：把 secret 放 `NEXT_PUBLIC_*` → 暴露给浏览器！永远不要。

```bash
# ✅ runtime
NEXT_PUBLIC_API_URL=https://api.example.com   # 公开
DATABASE_URL=postgres://...                    # 不公开
JWT_SECRET=...                                 # 不公开

# 客户端代码：
process.env.NEXT_PUBLIC_API_URL   # ✅ 浏览器可见
process.env.DATABASE_URL          # ❌ 浏览器看不到（undefined）
```

## 七、SSR 配置注入（Next / Nuxt / SvelteKit）

```typescript
// pages/_document.tsx (Next.js Pages router) — 已不推荐
// app/layout.tsx (App router) — server component 直接读 env
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html: `window.__APP_CONFIG__ = ${JSON.stringify({
              apiUrl: process.env.PUBLIC_API_URL,
              sentryDsn: process.env.PUBLIC_SENTRY_DSN,
            })}`,
          }}
        />
        {children}
      </body>
    </html>
  )
}
```

客户端：

```typescript
declare global { interface Window { __APP_CONFIG__: AppConfig } }
const config = window.__APP_CONFIG__
```

或用 server-only API endpoint `/api/config` 客户端启动 fetch。

## 八、Kubernetes ConfigMap / Secret

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  PORT: "8080"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgres://..."
  JWT_SECRET: "..."
```

```yaml
# Deployment
spec:
  containers:
  - name: app
    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secrets
```

或单条注入：

```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: DATABASE_URL
```

**K8s Secret 默认 base64 不是加密**！需要：
- enable encryption-at-rest（kube-apiserver --encryption-provider-config）
- 或用 sealed-secrets / external-secrets / Vault

## 九、Secret 管理工具

| 工具 | 模式 |
|---|---|
| **HashiCorp Vault** | 集中 Secret 服务 / 动态 secret / lease |
| **AWS Secrets Manager** | 云原生 / 自动轮换 |
| **AWS SSM Parameter Store** | 配置 + secret 二合一（廉价） |
| **GCP Secret Manager** | 云原生 |
| **Azure Key Vault** | 云原生 |
| **Sealed Secrets** | git-friendly K8s secret（公钥加密入仓） |
| **External Secrets Operator** | K8s 同步外部 secret 系统 |
| **Doppler / Infisical** | SaaS / 跨环境集中管理 |
| **1Password CLI** (`op`) | 个人 / 小团队简单 |

应用侧调用：

```typescript
// AWS SSM
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm'
const client = new SSMClient()
const { Parameter } = await client.send(new GetParameterCommand({
  Name: '/myapp/prod/database_url',
  WithDecryption: true,
}))
```

启动时一次性拉取 → 缓存到 env vars / 进程内存。

## 十、配置热重载

多数应用不需要 — 重启 Pod 即可（K8s 滚动更新一两分钟搞定）。**少数场景需要**：
- 调日志级别（DEBUG 现场打开）
- feature flag 实时切换（用 feature-flags skill 专门方案）

```typescript
// 简单文件监听
import { watch } from 'fs'
watch('./config/runtime.json', () => {
  reloadConfig()
})
```

## 十一、防 .env 误提交

### Pre-commit hook

```bash
# .pre-commit-config.yaml
repos:
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks
```

### CI 全仓扫描

```yaml
- uses: gitleaks/gitleaks-action@v2
- run: trufflehog filesystem . --only-verified
```

### 已经误提交的处理

1. **轮换该 secret**（最重要！git rebase 不能让攻击者还回去）
2. `git filter-repo --path .env --invert-paths` 重写历史
3. force push（且通知所有协作者）
4. 联系 GitHub support 清缓存（如果是 public repo）

## 十二、不同环境策略

| 环境 | 配置来源 | secrets 来源 |
|---|---|---|
| **local dev** | `.env.local` | `.env.local`（团队开发用 dummy 值） |
| **CI** | env vars in GH Actions | repo secrets / OIDC |
| **staging** | K8s ConfigMap | K8s Secret + Vault |
| **production** | K8s ConfigMap | Vault / cloud Secrets Manager |

**绝对不要**：
- 复用 dev 和 prod 的 secret
- 把 prod env 复制到 dev 调试

## 十三、Don'ts

- ❌ 把 `.env` 文件烤进 Docker 镜像（运行时 env vars 注入）
- ❌ 用 env vars 传**结构化**配置（数组 / 嵌套对象）— 用 yaml/json 文件 + 路径
- ❌ env vars 命名不规范：`PORT_API` vs `API_PORT` vs `apiPort` — 全大写下划线 + namespace 前缀
- ❌ 配置加载在 import time + 模块顶层 — 测试 mock 难
- ❌ 不校验 env vars，让运行时崩在中间
- ❌ secret 写日志：`logger.info({ config })`
- ❌ feature flag 配 env vars 跨重启 — 用 feature-flags 平台
- ❌ 把 K8s Secret 当真的加密（默认 base64）
- ❌ 把 `.env.production` 入 git
- ❌ Dockerfile `ENV PASSWORD=xxx`
- ❌ 把 secret 用作命令行参数（`./app --secret=xxx` 进 ps / 进 audit log）

## 十四、最佳实践清单

- [ ] `.env.example` 入 git，列所有 key + 注释
- [ ] `.env*` (除 example) 在 `.gitignore`
- [ ] env vars 启动时 schema 校验
- [ ] Secrets 走 Vault / Cloud SM / Sealed Secrets，不入仓
- [ ] config 与 secret 分文件分 namespace
- [ ] 默认值合理（PORT=8080 / LOG_LEVEL=info）
- [ ] 错误信息提示哪个 var 缺 / 错
- [ ] CI / pre-commit 跑 gitleaks
- [ ] dev / prod secret **完全不同**
- [ ] 运维侧定期轮换 prod secrets

## 十五、参考资料

- 12-Factor App #3 Config：https://12factor.net/config
- "The Twelve-Factor App" 全文必读
- HashiCorp Vault docs：https://developer.hashicorp.com/vault
- AWS Secrets Manager / Parameter Store guides
- Sealed Secrets：https://github.com/bitnami-labs/sealed-secrets
- External Secrets Operator：https://external-secrets.io/
- gitleaks：https://github.com/gitleaks/gitleaks
- pydantic-settings：https://docs.pydantic.dev/latest/concepts/pydantic_settings/
