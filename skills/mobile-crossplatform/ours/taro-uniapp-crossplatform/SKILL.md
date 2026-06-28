---
name: taro-uniapp-crossplatform
description: "Taro/uniapp 跨端小程序与 App 工程。覆盖多端条件编译、平台适配层、组件差异、路由、状态、请求封装、分包、构建发布、原生插件、H5/App/微信/支付宝/抖音多端一致性。当用户提到 Taro、uniapp、跨端小程序、多端适配、一套代码多端、条件编译、跨端组件库时使用。"
---

# Taro And Uniapp Cross-Platform

## Core Goal

Ship one product across multiple runtimes without pretending all runtimes are the same. Centralize shared domain logic; isolate platform differences.

## Platform Strategy

Classify code into:

- Shared domain logic: validation, formatting, API contracts, state machines.
- Shared UI primitives: only when behavior is truly portable.
- Platform adapters: login, payment, permissions, storage, upload, share, maps.
- Platform-specific pages: when UX or review rules differ materially.

Avoid scattering `#ifdef` or platform checks inside every component.

## Workflow

1. List target runtimes: WeChat, Alipay, Douyin, H5, Android/iOS app.
2. Define a platform capability matrix.
3. Create adapters for auth, payment, request, storage, navigation, and analytics.
4. Define build targets and environment configs.
5. Add platform-specific test checklist.
6. Keep release notes and review materials per platform.

## Capability Matrix Template

```md
| Capability | WeChat | Alipay | Douyin | H5 | App |
|---|---|---|---|---|---|
| Login | | | | | |
| Payment | | | | | |
| Share | | | | | |
| Push/message | | | | | |
| File upload | | | | | |
```

## Engineering Rules

- Use typed wrappers for platform APIs.
- Keep platform environment variables explicit.
- Split platform-only dependencies from shared code.
- Avoid assuming CSS, layout, and component behavior are identical.
- Keep design tokens shared but allow platform-specific component implementations.
- Test real target runtimes, not only H5 preview.

## Review Red Flags

- Platform checks are copy-pasted through business logic.
- One payment implementation is reused across incompatible platforms.
- H5 works but mini program package size or API limits fail.
- Review requirements are discovered after build completion.
- Native plugin dependencies are undocumented.

## Validation

- Build every target platform before declaring done.
- Run smoke tests for login, navigation, payment, upload, and share per platform.
- Check package size and subpackage behavior for mini programs.
- Verify release configs do not point to dev APIs.
