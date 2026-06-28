---
name: wechat-miniprogram-engineering
description: "微信小程序工程化开发。覆盖微信开发者工具、app.json、页面/组件、WXML/WXSS、setData 优化、分包、云开发、登录、订阅消息、支付、隐私协议、性能面板、体验版和审核发布。当用户提到微信小程序、wx.login、openid、unionid、订阅消息、微信支付、小程序云开发、微信审核时使用。"
---

# WeChat Mini Program Engineering

## Core Workflow

1. Confirm appid, project type, base library version, and whether cloud development is used.
2. Define `app.json` routes, tabBar, subpackages, permissions, and required plugins.
3. Keep pages thin; put domain logic in services and reusable components.
4. Wrap WeChat APIs such as login, request, storage, payment, upload, and subscription messages.
5. Optimize startup package, `setData`, image loading, and list rendering.
6. Prepare experience version, test account, privacy declaration, and release notes before audit.

## Auth Model

WeChat auth usually involves:

- `wx.login` returns a temporary code.
- Backend exchanges code for session identity.
- Backend maps `openid` and optionally `unionid` to user account.
- Client stores only short-lived session material.

Do not put app secret in the mini program bundle.

## Engineering Rules

- Use a request wrapper with timeout, retry policy, auth refresh, and error mapping.
- Keep environment configs separated for dev, trial, and production.
- Avoid massive `setData`; update only changed fields.
- Put infrequent pages in subpackages.
- Use component props/events instead of global state where possible.
- Centralize subscription message template IDs and permission prompts.

## Review Red Flags

- App secret or payment secret appears in client code.
- Payment flow lacks backend order verification.
- User data is requested before explaining purpose.
- The privacy declaration is stale.
- The experience version cannot be tested without private operator steps.
- Cloud functions and client routes disagree on environment.

## Validation

- Test on WeChat DevTools and a real device.
- Test first launch, denied permissions, login expiry, and session refresh.
- Test payment success, cancel, duplicate callback, and backend reconciliation.
- Use performance tools for startup time and package size.
- Verify audit materials before submission.
