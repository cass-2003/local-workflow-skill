---
name: feature-flags
description: "特性开关与渐进式发布。覆盖 kill switch / release toggle / experiment toggle / ops toggle / permission toggle 五类场景、progressive rollout、A/B 测试与统计显著性、targeting rules（按 user/percentage/geo/cohort）、配置存储（Redis/etcd/SDK push）、技术债清理、LaunchDarkly/Unleash/PostHog/OpenFeature 等平台对比、自建实现、SSR vs CSR 评估时机。当用户提到 feature flag、特性开关、kill switch、灰度发布、progressive rollout、canary、A/B 测试、experiment、LaunchDarkly、Unleash、OpenFeature、targeting 时使用。"
---

# Feature Flags Skill — 特性开关

## 何时使用

- 想发布一个功能但能立即关闭（不重新部署）
- 灰度放量（先 1% 用户 → 10% → 50% → 100%）
- A/B 测试不同版本效果
- 给特定客户 / 内部用户开放预览
- 故障应急：紧急关闭某条线路
- 业务参数调优（库存阈值 / 限额 / 折扣率）不想发版

## 一、五类 Toggle（Pete Hodgson 分类）

| 类型 | 寿命 | 例子 | 清理紧迫性 |
|---|---|---|---|
| **Release Toggle** | 短（数天-周） | "新支付流程" 灰度 | 高 — 上线后立刻清 |
| **Experiment Toggle** | 中（实验周期） | A/B 测试两种结账 UI | 中 — 实验结束清 |
| **Ops Toggle** | 长（月-永久） | "降级关闭推荐算法" | 低 — kill switch 永久保留 |
| **Permission Toggle** | 长（永久） | "premium 用户看新报表" | 低 — 业务逻辑 |
| **Kill Switch** | 永久 | "支付通道熔断" | 永久保留 |

**核心原则**：**Release Toggle 必须有清理 deadline**。否则代码库充满死代码，开关数指数膨胀。

## 二、Toggle Point 抽象

```typescript
// ✅ 抽象层
interface FeatureFlags {
  isEnabled(key: string, ctx: EvalContext): Promise<boolean>
  getVariant(key: string, ctx: EvalContext): Promise<string>     // 多变体
  getNumber(key: string, ctx: EvalContext, dflt: number): Promise<number>
  getJSON<T>(key: string, ctx: EvalContext, dflt: T): Promise<T>
}

// 业务代码不直接读环境变量 / 配置文件 / Redis
if (await flags.isEnabled('new-checkout-flow', { userId, country })) {
  return newCheckoutFlow()
}
return oldCheckoutFlow()
```

调用点叫 **Toggle Point**，决策代码（取值 / targeting）叫 **Toggle Router**。**业务代码只见 Toggle Point**。

## 三、Targeting Rules（决策规则）

```jsonc
{
  "key": "new-checkout-flow",
  "default": false,
  "rules": [
    // 优先级从上到下
    { "if": { "userId": { "in": ["u_admin", "u_test1"] } }, "then": true },
    { "if": { "country": { "eq": "JP" } }, "then": false },     // 日本暂不开
    { "if": { "isPremium": true }, "then": true },              // premium 用户先开
    { "if": { "userId": { "rolloutPercentage": 10 } }, "then": true },  // 其余 10%
    { "if": { "anyOf": [...] }, "then": true }
  ]
}
```

### Percentage rollout 的稳定性

```typescript
// ❌ 错：Math.random() — 同一用户每次结果不同
function isInRollout(pct: number) {
  return Math.random() * 100 < pct
}

// ✅ 对：基于 user ID hash — 同用户始终同结果
function isInRollout(userId: string, flagKey: string, pct: number) {
  const hash = crc32(`${flagKey}:${userId}`)
  return (hash % 100) < pct
}
```

**关键**：用 `flagKey + userId` 一起 hash，避免不同 flag 命中同一批用户（导致变体相关性）。

### Cohort（用户群组）

把用户分到稳定 cohort（A/B/C），所有 experiment 都基于该 cohort：

```
cohort = hash(userId) % 100   // 0-99 固定
```

便于跨 experiment 分析 / 防止用户在不同 flag 间漂移。

## 四、A/B 测试要点

### 1. 假设 + 指标

```
假设：新结账 UI 提升转化率 ≥ 2%
主指标：checkout_completed / checkout_started
次指标：avg_session_time / cart_abandonment_rate
```

### 2. 样本量计算

**经验公式**（基线 5% 转化、检测 2% 提升、α=0.05、power=0.8）：

```
样本量 ≈ 16 × σ² / Δ²
≈ 数千~数万每组（依基线）
```

工具：[Optimizely sample size calculator](https://www.optimizely.com/sample-size-calculator/)、Evan's Awesome A/B Tools

### 3. 统计显著性

- **t-test / chi-square** 看是否显著
- **CUPED** 用历史数据降方差
- **避免 peeking bug**：实验中途多次看 p-value 会人为造成"显著" — 用顺序 t-test 或固定终止时间

### 4. 实验做错的常见模式

- **样本太少就发**：噪声大于信号
- **没保留 holdout**：长期效果未知（短期升 1% 长期可能跌 2%）
- **新奇效应**：用户尝鲜短期升，3 周后回归
- **网络效应**：A/B 用户互相影响（社交场景）— 改成 cluster 实验

## 五、配置存储与分发

### 1. 自建（轻量）

```
DB / config service (etcd, Consul) → SDK 拉取或推送 → 进程缓存 30s
```

```go
// 简单实现
var flags atomic.Value    // map[string]any

func init() {
    go func() {
        for range time.Tick(30 * time.Second) {
            cfg := fetchFromDB()
            flags.Store(cfg)
        }
    }()
}

func IsEnabled(key string, ctx EvalContext) bool {
    cfg := flags.Load().(map[string]any)
    return evaluate(cfg[key], ctx)
}
```

### 2. SaaS 平台

| 平台 | 模型 | 卖点 |
|---|---|---|
| **LaunchDarkly** | 商业 | 业界标杆 / 完整 / 企业级 / 贵 |
| **Statsig** | 商业 | 实验 + 分析一体 |
| **PostHog** | 开源 + 云 | 产品分析 + flags / 可自托管 |
| **Unleash** | 开源 + 云 | Apache-2.0 / Java + Node SDK 多 |
| **GrowthBook** | 开源 + 云 | 实验导向 / SQL 驱动 |
| **OpenFeature** | 标准 | 厂商无关 SDK 抽象，对接多个 provider |

新项目首选 **OpenFeature SDK + 任一 provider**（LaunchDarkly / Unleash / Statsig / 自建）。这样未来换平台不用改业务代码。

### 3. SDK 模式

**Server-side SDK**（Java / Go / Python / Node）：
- 全量规则 + 用户列表本地决策（毫秒级 / 不依赖网络）
- 启动时拉一次 + WebSocket 增量推送

**Client-side SDK**（JS / iOS / Android）：
- 仅暴露已决策的 flag → user 看不到其他用户的 targeting 规则
- 启动时调评估 API 拿"该用户的 flag 集合"

```typescript
// SSR (server-side) — 安全 / 低延迟
const isEnabled = await ldClient.variation('new-checkout', user, false)
return isEnabled ? <NewCheckout /> : <OldCheckout />

// Client — 慎用，flag 暴露风险
const isEnabled = ldClient.variation('new-checkout', false)
```

## 六、技术债清理流程

**新 flag 上线立即建 ticket：30 天后清理**。

```
1. flag 添加：commit 时同时建 issue: "remove-flag-xxx by 2026-06-06"
2. flag 上线后稳定 1-2 周
3. 100% 放量 1 周
4. 删 flag：
   - 删 toggle point（保留启用分支代码）
   - 删平台配置
   - 删监控告警
5. PR review 检查 commit message: "chore: remove flag <key>"
```

**自动化检测**：扫描代码 vs 平台 flag 列表，差集报告：
- 平台有但代码没用 → 残留配置
- 代码有但平台没有 → flag 可能被误删，业务永远 false

## 七、Don'ts

- ❌ flag 命名不规范：`v2_new_thing` / `temp_fix` — 用 `enable-<feature>` 或 `<area>-<feature>-<version>`
- ❌ 嵌套 flag（flag 内部依赖另一个 flag）— 决策矩阵爆炸
- ❌ 用 flag 替代权限 RBAC — flag 不是审计 / 不带角色概念
- ❌ flag 用于个性化（每个用户配置不同） — 用专门的 user preference 系统
- ❌ flag 取值不缓存 — 每次都 RPC，延迟翻倍
- ❌ 评估失败 throw exception — 必须有 default value 兜底
- ❌ 所有 flag 全在一个文件 / 一个表 — 按 owner / domain 分
- ❌ flag 永不清理 — 死代码 + 决策树爆炸
- ❌ A/B 实验中途偷看 p-value 就停 — peeking bug
- ❌ flag 无 audit log — 谁什么时候改的不知道，事后无法追责

## 八、关键代码模式

### 默认值兜底

```typescript
// SDK / 平台挂掉时不能让业务挂
async function safeFlag(key: string, ctx: Ctx, dflt: boolean): Promise<boolean> {
  try {
    return await flags.isEnabled(key, ctx)
  } catch (e) {
    metrics.increment('flag.eval.error', { key })
    logger.warn({ key, err: e }, 'flag eval failed, using default')
    return dflt
  }
}
```

### 包装移除时易于清理

```typescript
// ❌ 散落在各处
if (await flags.isEnabled('new-checkout', ctx)) { /* 1000 行 */ }

// ✅ 集中点
async function getCheckoutFlow(ctx: Ctx) {
  return await flags.isEnabled('new-checkout', ctx)
    ? newCheckoutFlow
    : oldCheckoutFlow
}
// 全局只此一处用到该 flag → 删除时改一处
```

### 监控

```typescript
metrics.increment('flag.evaluated', { key, variant: result, source: 'cache|fetch' })
```

报告：每个 flag 每分钟评估次数 / 各变体占比 / 错误率。

## 九、Kill Switch 模式

```typescript
// 紧急关闭依赖（如下游 API 故障）
if (await flags.isEnabled('disable-recommendations', { region })) {
  return []   // 降级：不显示推荐
}
return await fetchRecommendations()
```

**关键**：
- Kill switch flag 永久保留
- 默认 OFF（即正常运行）
- 操作运行时改为 ON 即降级
- 配 dashboard + 一键开关
- 演练定期触发，确保确实生效

## 十、参考资料

- Pete Hodgson "Feature Toggles"：https://martinfowler.com/articles/feature-toggles.html
- OpenFeature 标准：https://openfeature.dev/
- LaunchDarkly Best Practices Guide
- "Trustworthy Online Controlled Experiments"（Kohavi 等，A/B 圣经）
- Booking.com / Airbnb / Spotify 的 experimentation 工程博客
- statsig docs：https://docs.statsig.com/
