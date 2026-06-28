---
name: mini-program-architecture
description: "小程序通用架构设计。覆盖微信/支付宝/抖音/百度/快应用等小程序的页面路由、分包、组件、状态、接口层、登录授权、缓存、性能、平台差异、审核发布和多端复用。当用户提到小程序架构、微信小程序、支付宝小程序、抖音小程序、分包、setData 性能、小程序工程化时使用。"
---

# Mini Program Architecture

## Core Goal

Build mini programs with clear page boundaries, small packages, predictable platform APIs, and review-safe behavior.

## Architecture Layers

- App bootstrap: launch, update check, global config, platform detection.
- Pages: route-level screens with minimal business logic.
- Components: reusable UI with explicit props/events.
- Services: API clients, auth, payment, upload, analytics.
- State: global session state, page state, cached data, derived view state.
- Platform adapters: WeChat, Alipay, Douyin, Baidu, or framework runtime.

## Workflow

1. Identify target platforms and whether native mini program, Taro, uniapp, or another framework is used.
2. Define route map and package split plan.
3. Set API, auth, payment, and upload adapters.
4. Design state ownership and cache expiration.
5. Add performance guardrails for startup, package size, and `setData`/render updates.
6. Prepare review constraints: privacy, content, payment rules, required screenshots, and test account.
7. Add release checklist for dev, trial, audit, and production versions.

## Package And Performance Rules

- Split low-frequency pages into subpackages.
- Keep startup package small and avoid loading admin/rare flows initially.
- Avoid sending large objects through view updates.
- Use pagination and virtualized patterns for long lists.
- Cache stable dictionaries and configuration with versioning.
- Lazy-load heavy images and non-critical components.

## Review Red Flags

- Business logic is duplicated across pages.
- Platform APIs are called directly everywhere instead of through adapters.
- Main package includes every page and asset.
- Login is forced before the user sees value without product justification.
- Privacy prompts do not match actual data collection.
- Payment, subscription, or content behavior violates platform review rules.

## Validation

- Test cold start, route navigation, subpackage loading, and low-end device performance.
- Test login denial, permission denial, network failure, and update flow.
- Run platform preview/trial build before submission.
- Verify audit account, screenshots, and privacy declarations.
