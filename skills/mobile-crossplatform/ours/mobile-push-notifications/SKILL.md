---
name: mobile-push-notifications
description: "移动端推送通知工程。覆盖 APNs/FCM/Expo Push、本地通知、权限引导、设备 token、用户分群、深链接、通知点击行为、退订偏好、送达监控、测试和隐私合规。当用户提到 App 推送、push notification、APNs、FCM、Expo Push、通知权限、消息提醒、推送深链接时使用。"
---

# Mobile Push Notifications

## Core Goal

Make notifications useful, permission-safe, and observable. A push system must handle consent, targeting, delivery, click routing, and quiet failure.

## Workflow

1. Define notification types and user value.
2. Decide permission timing and rationale screen.
3. Register device token and bind it to user, app install, platform, locale, and environment.
4. Store notification preferences by category.
5. Implement payload schema and deep link routing.
6. Add delivery, open, dismiss, and conversion tracking.
7. Test foreground, background, killed app, logout, token rotation, and reinstall.

## Payload Contract

Every push type should define:

- `type`: stable event/category name.
- `title` and `body`: localized or localization key.
- `target`: deep link or route intent.
- `entity_id`: optional domain object.
- `dedupe_key`: prevents spam and duplicate display.
- `priority`: normal, time-sensitive, silent/background.
- `expires_at`: stops stale notifications.

Do not encode sensitive data in payloads that can appear on lock screens.

## Permission Strategy

- Ask only after the user understands why notifications help.
- Support "not now" without breaking core usage.
- Respect OS-level denial and do not nag every session.
- Provide in-app category preferences.
- Explain critical alerts or time-sensitive notifications carefully.

## Review Red Flags

- Push token is treated as permanent.
- Same token is shared across dev/staging/prod accidentally.
- Logout does not unregister or disassociate device tokens.
- Notification click opens a dead route.
- Payload contains PII or secrets.
- No dashboard exists for sent, delivered, opened, failed, and unsubscribed.

## Validation

- Test iOS and Android separately; notification behavior differs.
- Test app foreground, background, killed, and locked states.
- Rotate token or reinstall app and verify backend token state.
- Send malformed and stale payloads.
- Verify preference changes stop future sends.
