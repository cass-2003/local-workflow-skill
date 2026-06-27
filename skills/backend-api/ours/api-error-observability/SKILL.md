---
name: api-error-observability
description: "API 错误模型与可观测性。覆盖错误码设计、HTTP status、Problem Details、trace id、structured logging、metrics、distributed tracing、SLO、告警、请求审计、错误边界和客户端可恢复错误。当用户提到 API 错误、错误码、日志、trace id、observability、OpenTelemetry、SLO、告警、structured logging、Problem Details 时使用。"
---

# API Error And Observability

## Core Goal

Make failures understandable to users, clients, operators, and future agents. Every important error should answer: what happened, who is affected, can it be retried, and where is the evidence?

## Error Contract

Use a stable error shape:

```json
{
  "type": "https://docs.example.com/errors/quota-exceeded",
  "code": "quota_exceeded",
  "message": "Quota exceeded for this workspace.",
  "request_id": "req_123",
  "retryable": false,
  "details": {
    "limit": 1000,
    "window": "month"
  }
}
```

Expose safe messages to clients. Put sensitive internals only in logs.

## HTTP Status Guidance

| Status | Use For |
|---|---|
| 400 | invalid request shape |
| 401 | not authenticated |
| 403 | authenticated but not allowed |
| 404 | not found or intentionally hidden |
| 409 | conflict, version mismatch, duplicate invariant |
| 422 | semantic validation failure |
| 429 | rate limited |
| 500 | unhandled server error |
| 503 | temporary service unavailable |

Do not return `200` with an error object for normal APIs.

## Logging Rules

- Log structured fields, not only prose.
- Include request id, trace id, user id if safe, tenant id if safe, route, method, status, duration, and error code.
- Redact secrets and PII.
- Log at boundaries: request start/end, external calls, queue jobs, auth failures, and critical domain transitions.
- Avoid logging full request bodies by default.

## Trace And Metrics

Minimum metrics:

- request count by route/status
- latency histogram by route
- error count by code
- dependency latency and failure rate
- queue lag if API enqueues work

Minimum tracing:

- inbound request span
- database query spans or summarized DB timing
- external HTTP calls
- queue publish/consume spans
- cache calls when they affect latency

## SLO And Alerting

Alert on symptoms before causes:

- p95/p99 latency above SLO
- error rate above threshold
- dependency failure spike
- queue lag above threshold
- no traffic when traffic is expected

Avoid alerts that require humans for non-actionable noise.

## Client Recoverability

For each error code, define:

- Can client retry?
- Should retry use backoff?
- Should user change input?
- Is login required?
- Is support needed?
- Should the UI preserve draft state?

## Review Red Flags

- Errors are free-form strings only.
- Logs cannot be correlated to a user request.
- Client sees stack traces.
- Authorization failures log secrets or full tokens.
- All failures map to 500.
- Rate limits omit reset/retry guidance.
- Metrics use raw user IDs as labels, causing cardinality explosions.
- Alerts fire on every individual error instead of SLO burn or rate.

## Validation

- Trigger representative 4xx and 5xx errors.
- Confirm response shape is stable.
- Confirm request id appears in response and logs.
- Confirm trace links external calls and database time.
- Confirm PII and secrets are redacted.
- Confirm dashboards show latency, error rate, and top error codes.

