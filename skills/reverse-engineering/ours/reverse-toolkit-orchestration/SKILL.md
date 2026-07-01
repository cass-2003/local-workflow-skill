---
name: reverse-toolkit-orchestration
description: "授权逆向工具链编排。用于 APK 逆向、Android App 协议分析、前端 JS 逆向、抓包参数还原、JADX、Apktool、Frida、IDA Pro MCP、IDA-NO-MCP、radare2、anything-analyzer、playwright-mcp、js-reverse-mcp 等多工具组合场景；负责先确认授权边界，再选择静态/动态/浏览器/二进制/报告技能路线。"
---

# Reverse Toolkit Orchestration

## Overview

Use this skill as the router for authorized APK and frontend JavaScript reverse workflows. It turns a mixed tool request into a bounded plan, delegates deep analysis to the right reverse-engineering skills, and keeps evidence reproducible.

Do not treat this as a bypass cookbook. The workflow is for owned apps, explicit client authorization, internal assessment, malware/CTF/lab samples, or interoperability/debugging work permitted by law and contract.

## Authorization Gate

Before technical steps, record:

- Scope owner and authorization source.
- Target type: APK/AAB, Web site, WebView, native library, traffic capture, or exported IDA/radare2 project.
- Allowed actions: static read-only analysis, dynamic instrumentation, traffic capture, test request replay, repack/sign test build, or report-only.
- Forbidden actions from the engagement: account abuse, production traffic replay, credential extraction, anti-fraud evasion, persistence, data exfiltration, or public target exploitation.

If authorization is unclear, do not provide operational bypass steps. Ask for scope clarification or keep the output at a high-level defensive assessment plan.

## Tool Routing

| Need | Preferred route | Delegate to |
| --- | --- | --- |
| Capture and compare app/Web requests | anything-analyzer, HAR/JSON export, mitmproxy/Burp when already authorized | `protrev`, `rev-report` |
| Browser-driven JS reverse | playwright-mcp or browser automation, DevTools/CDP, bundle capture | `webrev`, `scriptrev`, `cryptrev` |
| APK static analysis | jadx for Java/Kotlin, Apktool for resources/smali/manifest | `android-reversing`, `mobile-reverse-engineering`, `javarev`, `scriptrev` |
| Android dynamic instrumentation | Frida/objection on test devices, focused hooks, trace logs | `android-reversing`, `debugrev`, `cryptrev` |
| Native `.so` or desktop binary | IDA Pro MCP for interactive exploration; IDA-NO-MCP export for large offline review; radare2/rizin for CLI/batch | `binrev`, `abirev`, `asmrev`, `debugrev` |
| Packing, obfuscation, protector triage | identify packer/protector before deeper work | `packrev`, `scriptrev`, `mobile-reverse-engineering` |
| Reproducible delivery | evidence log, hashes, scripts, diagrams, report | `rev-report`, `revauto` |

Prefer existing project tools and already configured MCP servers. If a named tool is not installed or available, state that and choose the next safe equivalent instead of pretending it was used.

## APK Workflow

1. Identify the sample: package name, version, signature status, source, SHA-256, device/emulator, Android version, and authorization.
2. Capture baseline traffic in the permitted environment; label endpoints, headers, parameters, timestamps, and reproducibility notes.
3. Run static triage with jadx and Apktool: manifest, permissions, exported components, network config, strings, crypto imports, WebView bridges, native libraries, and suspicious reflection/loading.
4. Route Java/Kotlin logic to Android/Java reverse skills; route smali/resources to script/mobile reverse skills.
5. If native logic exists, decide:
   - Use IDA Pro MCP for interactive exploration, renaming, xrefs, and structure recovery.
   - Use IDA-NO-MCP export when a stable code corpus is better for AI IDE indexing or large-function slicing.
   - Use radare2 for headless, scripted, or lightweight batch inspection.
6. Use Frida only inside the authorized test environment. Hook narrowly around the suspected function, record inputs/outputs, and avoid collecting unrelated secrets or user data.
7. Reproduce the minimum algorithm or protocol behavior in a small script when allowed. Mark test data clearly.
8. If repack/sign is in scope, keep it to a lab build and document exact changes. Do not ship modified third-party apps or bypass production controls outside the engagement.
9. Verify with a controlled request, unit script, or device test, then write a report-ready evidence trail.

## Frontend JS Workflow

1. Capture the triggering request/response and page state. Save HAR/JSON, relevant JS bundles, source maps if available, and reproduction steps.
2. Use browser automation or DevTools/CDP to trigger the behavior and intercept XHR/fetch/WebSocket traffic.
3. Prefer source maps and de-bundling before manual deobfuscation. If unavailable, use AST/bundle tooling through `webrev` or `scriptrev`.
4. Search by stable anchors: parameter names, endpoint paths, header names, crypto constants, Webpack module IDs, call sites, and error strings.
5. Use runtime probes to dump only the needed local context: inputs, output, key schedule metadata, module exports, and call stack. Avoid harvesting unrelated credentials/session data.
6. Reimplement the minimum transformation with deterministic test vectors.
7. Validate by comparing generated parameters or body values against the captured baseline in an authorized test flow.

## Evidence Contract

Leave a durable record for any non-trivial run:

- Scope and authorization summary.
- Sample identity: hashes, package/version/build ID, file names, source, tool versions.
- Environment: OS, device/emulator, browser, Java/Android SDK, IDA/radare2/Frida versions where relevant.
- Commands or MCP actions used, with outputs summarized rather than pasted wholesale.
- Findings with evidence links: file/function/address/request ID/trace ID.
- Reproduction scripts or pseudocode using sanitized test data.
- Validation result and limitations.
- Next analysis routes or blocked questions.

## Stop Conditions

Stop or downgrade to a safe plan when:

- The user cannot confirm authorization for the target or action.
- The request asks for credential theft, fraud, account takeover, mass scraping, evasion against a public service, persistence, or deployment of modified third-party apps.
- Further progress requires real user data, production secrets, paid accounts, or destructive changes.
- Tool output suggests malware or regulated data handling and no lab isolation/reporting scope exists.
- Validation would hit production or third-party systems without explicit permission.

When stopping, still deliver a useful artifact: scoped plan, safe evidence checklist, tool availability gaps, or defensive review questions.
