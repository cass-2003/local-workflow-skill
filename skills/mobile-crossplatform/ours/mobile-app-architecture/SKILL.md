---
name: mobile-app-architecture
description: "移动 App 架构设计。覆盖 iOS/Android/Flutter/React Native/Expo 的模块分层、导航、状态管理、网络层、本地存储、权限、错误处理、可观测性、测试、构建发布和多人协作边界。当用户提到 App 架构、移动端架构、客户端工程、移动项目地基、Flutter 架构、React Native 架构、Expo 架构、iOS/Android 工程结构时使用。"
---

# Mobile App Architecture

## Core Goal

Build a mobile app foundation that can survive product growth: clear layers, predictable data flow, safe permissions, testable modules, and reliable release paths.

## Architecture Layers

- App shell: startup, routing, navigation, auth bootstrap, feature flags, theme, localization.
- Feature modules: screens, view models/hooks, local UI state, feature-owned components.
- Domain layer: business rules, validation, commands, use cases.
- Data layer: API clients, cache, persistence, sync, repository adapters.
- Platform layer: permissions, push, camera, files, contacts, location, sensors, deep links.
- Observability: logging, crash reporting, analytics, performance traces.

Keep platform-specific code behind small adapters. Do not let every screen call native APIs directly.

## Workflow

1. Identify app type: content app, commerce, realtime collaboration, field work, offline-first, media, or internal tool.
2. Define navigation map and auth/session lifecycle before screens multiply.
3. Choose state ownership: server cache, local UI state, persistent local data, or platform state.
4. Define API, cache, and offline behavior for each feature.
5. Add permission and privacy boundaries.
6. Establish build variants, environment config, signing, and release workflow.
7. Add crash reporting, analytics events, and performance baselines before launch.

## App Foundation Checklist

- Route names and deep link paths are stable.
- API client has typed responses, timeout, retry, cancellation, and error mapping.
- Auth refresh does not create request storms.
- Local storage has migration/versioning strategy.
- Permissions are requested just-in-time with user-facing rationale.
- Secrets are not shipped in the app bundle.
- Feature flags have defaults and remote failure behavior.
- Crash reporting redacts sensitive data.
- Test plan includes cold start, background/foreground, offline, low storage, and slow network.

## Review Red Flags

- Business rules live only inside screen components.
- Every feature invents its own API client.
- Offline behavior is "spinner forever".
- Navigation, auth, and feature flags initialize in race-prone order.
- App store signing and environment setup are undocumented.
- Analytics events are added without naming conventions or privacy review.

## Validation

- Run app on at least one simulator/emulator and one real-device-equivalent profile when possible.
- Test fresh install, upgrade install, logout/login, offline start, and token expiry.
- Run unit tests for domain rules and integration tests for critical navigation flows.
- Confirm release build does not rely on development-only config.
