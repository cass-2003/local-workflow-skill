---
name: mobile-app-release-ops
description: "移动 App 发布与运营工程。覆盖 iOS/Android 签名、证书、构建号、TestFlight/Play Console、灰度发布、崩溃监控、版本兼容、强制升级、回滚策略、审核资料和发布检查清单。当用户提到 App 上架、发版、TestFlight、Play Store、App Store、签名证书、灰度发布、移动端 CI/CD、版本升级时使用。"
---

# Mobile App Release Ops

## Core Rule

Treat mobile releases as irreversible customer events. You cannot instantly roll back installed binaries, so prepare gates, telemetry, staged rollout, and server compatibility before release.

## Release Workflow

1. Confirm release scope, target platforms, and minimum supported versions.
2. Freeze version, build number, changelog, and feature flag plan.
3. Build signed release artifacts from CI or a reproducible local command.
4. Run smoke tests on release builds, not only debug builds.
5. Upload to internal testing, TestFlight, or closed testing.
6. Monitor crash-free sessions, startup time, API errors, and key funnels.
7. Roll out gradually when store/platform supports it.
8. Keep server backward-compatible until old app versions age out.

## Release Checklist

- Bundle identifiers, package names, schemes/flavors are correct.
- Certificates, provisioning profiles, keystores, and service accounts are valid.
- Environment config points to production endpoints.
- Debug menus and test credentials are disabled.
- Privacy manifest, permissions, and store disclosures match behavior.
- App icons, screenshots, descriptions, and review notes are updated.
- Crash reporting and analytics are enabled for release builds.
- Feature flags can disable risky server-driven features.

## Versioning Rules

- Use monotonically increasing build numbers.
- Separate marketing version from internal build number.
- Document minimum supported app version on the backend.
- Avoid breaking API changes until old app versions are blocked or migrated.
- Use remote config for copy, flags, and rollout behavior, not for secrets.

## Review Red Flags

- Release build is created from a developer laptop with undocumented state.
- Backend deploy assumes all users upgrade immediately.
- Keystore or signing identity has no backup/ownership record.
- Store review notes are missing for login-gated functionality.
- Crash alerts are not watched during rollout.

## Validation

- Install release build fresh and over the previous production build.
- Test login, purchase/payment if applicable, push, deep links, and offline start.
- Verify build symbols/dSYMs/proguard mappings are uploaded.
- Confirm staged rollout can be paused.
- Confirm server still supports the previous app version.
