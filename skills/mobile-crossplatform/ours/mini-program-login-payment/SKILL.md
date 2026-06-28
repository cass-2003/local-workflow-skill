---
name: mini-program-login-payment
description: "小程序登录、授权与支付闭环。覆盖微信/支付宝/抖音等小程序的登录态、手机号授权、用户身份绑定、订单创建、支付签名、回调验签、幂等、退款、对账、订阅消息和风控。当用户提到小程序登录、小程序支付、微信支付、支付宝小程序支付、openid、unionid、手机号授权、支付回调时使用。"
---

# Mini Program Login And Payment

## Core Rule

Login and payment are backend-owned security flows. The mini program client starts the flow and presents results; the server owns identity exchange, signing, order state, callbacks, refunds, and reconciliation.

## Login Flow

Define:

- Platform identity: `openid`, `unionid`, buyer/user id, or platform-specific equivalent.
- App account identity: internal user id and tenant/workspace if any.
- Session: short-lived access token or server session.
- Binding: phone number, email, enterprise account, or guest upgrade path.

Never store platform app secrets in client code.

## Payment Flow

1. Client requests backend to create order.
2. Backend validates price, inventory, user, risk, and idempotency key.
3. Backend signs platform payment parameters.
4. Client calls platform payment API.
5. Platform sends async callback to backend.
6. Backend verifies signature, updates order idempotently, and triggers fulfillment.
7. Client polls or refreshes order state; do not trust client-only success.

## Backend Invariants

- Order amount is computed server-side.
- Duplicate create/pay/callback requests are idempotent.
- Callback signature and certificate rules are verified.
- Refunds and cancellations have state-machine rules.
- Payment success triggers exactly-once fulfillment or a recoverable outbox event.
- Reconciliation detects missing callbacks or inconsistent order states.

## Review Red Flags

- Client passes trusted amount or product price.
- Payment success is accepted only from client callback.
- Callback endpoint is not idempotent.
- Refund path is manual and unaudited.
- Phone authorization is required before users understand value.
- Subscription messages are sent without consent and category control.

## Validation

- Test pay success, user cancel, timeout, duplicate callback, and callback-before-client-return.
- Test refund and partial refund when supported.
- Test login code expiry and account binding conflicts.
- Confirm logs can trace order id, platform transaction id, user id, and callback request id.
