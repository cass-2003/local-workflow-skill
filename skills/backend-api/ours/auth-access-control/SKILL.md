---
name: auth-access-control
description: "认证与访问控制工程。覆盖 authentication vs authorization、session/JWT/OAuth/OIDC、RBAC/ABAC/ReBAC、租户隔离、权限检查位置、token 生命周期、刷新令牌、CSRF、CORS、安全默认值和审计日志。当用户提到登录、权限、鉴权、授权、RBAC、ABAC、OAuth、OIDC、JWT、session、多租户、tenant isolation、access control 时使用。"
---

# Auth And Access Control

## Separate The Concepts

- Authentication answers: who are you?
- Authorization answers: what are you allowed to do?
- Tenant isolation answers: which data boundary applies?
- Audit answers: who did what, when, from where, and why was it allowed?

Do not mix these checks into one vague middleware.

## Workflow

1. Identify identities: user, service account, API key, webhook sender, admin, anonymous visitor.
2. Identify resources: project, workspace, organization, file, invoice, user profile.
3. Define actions: read, create, update, delete, approve, export, invite, impersonate.
4. Choose model: RBAC, ABAC, ReBAC, or a hybrid.
5. Decide enforcement points: route, service, query, storage, background job.
6. Add denial defaults, audit logs, tests, and migration path.

## Model Selection

| Model | Use When | Warning |
|---|---|---|
| RBAC | roles map cleanly to permissions | role explosion |
| ABAC | context matters: tenant, owner, status, region | policies get hard to debug |
| ReBAC | relationship graph matters: org/team/shared file | needs careful query design |
| ACL | small resource-specific grants | can become scattered |

## Enforcement Rules

- Deny by default.
- Check tenant boundary before object access.
- Do not rely only on frontend hiding.
- Put critical authorization in backend service/domain layer.
- Keep policy decisions testable and named.
- Use database constraints or scoped queries for tenant isolation when possible.
- Log privileged actions and authorization failures.

## Token And Session Guidance

- Prefer secure, httpOnly, SameSite cookies for browser sessions unless API constraints require bearer tokens.
- Keep access tokens short-lived.
- Rotate refresh tokens and detect reuse for high-risk systems.
- Store only token hashes when persistence is required.
- Never put secrets in localStorage for high-risk apps.
- Validate issuer, audience, expiration, signature, and algorithm for JWTs.
- Do not accept `alg=none`.

## Multi-Tenant Guardrail

Every data query should answer:

```text
Which tenant scope is active?
Which user/service identity is active?
Which resource is being touched?
Which action is requested?
Which policy allowed or denied it?
```

If a query can run without tenant scope in a tenant system, treat it as a bug unless explicitly administrative and audited.

## API Key Rules

- Show the full key only once.
- Store hashes, not raw keys.
- Prefix keys for identification without secret disclosure.
- Support rotation, expiration, owner, last-used timestamp, and revocation.
- Scope keys to actions and resources.

## Review Red Flags

- Authorization is implemented only in route handlers.
- Admin bypasses skip tenant checks accidentally.
- Background jobs process records without re-checking permission or tenant scope.
- JWT validation omits audience or issuer.
- Refresh tokens never rotate.
- API keys are stored in plaintext.
- CORS is treated as authorization.
- Frontend role checks are treated as security.

## Validation

- Add tests for allow and deny paths.
- Test cross-tenant access attempts.
- Test expired, malformed, wrong-audience, and revoked tokens.
- Test background job and webhook authorization separately.
- Verify audit logs for privileged actions.

