---
name: datetime-timezones
description: "日期时间与时区处理。覆盖 IANA 时区数据库、UTC vs 本地时间、DST 夏令时、ISO 8601 / RFC 3339 / Unix 时间戳、JavaScript Temporal API、各语言时间库（dayjs/luxon/date-fns/Python zoneinfo/Go time/Java time）、数据库存储、跨时区调度、闰秒。当用户提到时区、timezone、IANA、UTC、DST、Temporal、ISO 8601、Unix 时间戳、跨时区、夏令时、time zone bug、闰秒时使用。"
---

# DateTime & Timezones Skill — 日期时区处理

## 何时使用

- 跨时区业务（用户在不同时区，服务部署在另一个时区）
- 调度任务 / cron / 报表统计（按"自然日"边界）
- 调试"为什么少了一小时" / "为什么 3 月 13 日变 2 月 28 日"
- 数据库存日期 / 时间戳的格式选型
- 国际化日期格式输出

## 一、核心概念（永远先理清）

### 三种时间表达

| 类型 | 例子 | 用途 |
|---|---|---|
| **UTC instant**（绝对时刻） | `2026-05-06T07:00:00Z` | 服务器存储 / 跨服务通信 |
| **Local DateTime**（"墙上时间"） | `2026-05-06 16:00` | 用户输入 / 显示（带时区上下文） |
| **Zoned DateTime**（带时区） | `2026-05-06 16:00 Asia/Tokyo` | 调度 / 跨时区精确锚点 |

**永远存 UTC，显示时按用户时区转换**。例外：跨夏令时调度需存 `Local + Zone`（见后）。

### Unix 时间戳

- **秒**：`1715000000` —— 绝大多数系统
- **毫秒**：`1715000000000` —— JS / Java
- **微秒/纳秒**：金融 / 高精度场景

无时区概念（Unix epoch = 1970-01-01 UTC），统一基准。

### IANA 时区 ID

```
Asia/Shanghai
Asia/Tokyo
Asia/Kolkata
America/New_York
America/Los_Angeles
Europe/London
Europe/Paris
Australia/Sydney
UTC
```

**永远不要用** `CST` / `EST` / `PST` —— 含糊（CST = China? 也是 Central Standard Time? 也是 Cuba Standard Time?）。

### DST（夏令时）

部分时区每年切换：

- **美国**：3 月第二周日 02:00 → 03:00（春进），11 月第一周日 02:00 → 01:00（秋退）
- **欧洲**：3 月最后周日 / 10 月最后周日
- **澳洲（南半球）**：相反方向
- **中国 / 日本 / 印度 / 大部分非洲**：**无 DST**

DST 切换日有"消失的小时"和"重复的小时"：

```
2026-03-08 (US):
  01:30 EST → 03:30 EDT   ← 02:30 不存在
2026-11-01 (US):
  01:30 EDT → 01:30 EST   ← 01:30 重复两次
```

## 二、ISO 8601 / RFC 3339

```
2026-05-06T07:00:00Z          ← UTC（Z = Zulu）
2026-05-06T16:00:00+09:00     ← 带 offset
2026-05-06T16:00:00.123+09:00 ← 毫秒
20260506T070000Z              ← basic 格式（不推荐）
```

**关键**：`+09:00` 是 **offset** 不是 **time zone**。日本永远 +09:00（无 DST），但纽约可能 -05:00（EST）或 -04:00（EDT）。

## 三、JavaScript：Temporal API（替代 Date）

```javascript
// ⚠️ Date 有大量坑：可变、月份从 0 开始、无时区、混淆 instant 和 local
//   → 用 Temporal（Stage 3，2025 部分浏览器原生 + polyfill）

// 1. UTC instant
const now = Temporal.Now.instant()
now.toString()    // '2026-05-06T07:00:00Z'

// 2. Zoned DateTime
const tokyo = Temporal.Now.zonedDateTimeISO('Asia/Tokyo')
tokyo.toString()  // '2026-05-06T16:00:00+09:00[Asia/Tokyo]'

// 3. 转换
const utc = tokyo.toInstant()
const ny = tokyo.withTimeZone('America/New_York')

// 4. 算术
tokyo.add({ days: 7 })
tokyo.subtract({ hours: 3 })
const diff = tokyo.until(other, { largestUnit: 'days' })

// 5. 解析
Temporal.Instant.from('2026-05-06T07:00:00Z')
Temporal.PlainDate.from('2026-05-06')
Temporal.ZonedDateTime.from('2026-05-06T16:00:00[Asia/Tokyo]')
```

未原生支持时用 `@js-temporal/polyfill`。

### 当前主流库（过渡期）

| 库 | 大小 | 特点 |
|---|---|---|
| **date-fns** | tree-shakable | 不可变 / 函数式 / 无时区原生支持 |
| **dayjs** | 7KB | API 类似 moment / 时区需 plugin |
| **luxon** | 30KB | moment 团队继任 / 内置时区 |
| **moment** | 70KB **legacy** | **不再用**于新项目 |

`Intl.DateTimeFormat` 内置足够强：

```javascript
new Intl.DateTimeFormat('zh-CN', {
  timeZone: 'Asia/Shanghai',
  dateStyle: 'long',
  timeStyle: 'short',
}).format(new Date())
// '2026年5月6日 下午3:00'
```

## 四、Python：zoneinfo（3.9+）

```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# UTC instant
now_utc = datetime.now(timezone.utc)

# Zoned
tokyo = datetime.now(ZoneInfo('Asia/Tokyo'))
tokyo.isoformat()    # '2026-05-06T16:00:00+09:00'

# 转换
ny = tokyo.astimezone(ZoneInfo('America/New_York'))

# 解析
datetime.fromisoformat('2026-05-06T07:00:00+00:00')

# Naive datetime（无时区）— 危险，避免使用
datetime.now()    # 取 OS 本地时区，不可控
```

3.9 之前用 `pytz`（API 难用，要 `localize()`）。**新代码统一用 `zoneinfo`**。

## 五、Go：time 包

```go
import "time"

// UTC instant
now := time.Now().UTC()

// Zoned
tokyo, _ := time.LoadLocation("Asia/Tokyo")
t := time.Now().In(tokyo)
t.Format(time.RFC3339)    // "2026-05-06T16:00:00+09:00"

// 解析
t, _ := time.Parse(time.RFC3339, "2026-05-06T07:00:00Z")

// 算术
t.Add(7 * 24 * time.Hour)
t.AddDate(0, 0, 7)        // 加 7 天（DST 安全）

// 自定义格式（用参考时间 2006-01-02 15:04:05）
t.Format("2006-01-02 15:04:05")
```

**Linux 容器**：可能没装 tzdata：
```dockerfile
RUN apk add --no-cache tzdata
ENV TZ=UTC
```

或者 Go 1.15+ 可静态嵌入：
```go
import _ "time/tzdata"
```

## 六、Java：java.time（JSR 310）

```java
import java.time.*;
import java.time.format.DateTimeFormatter;

// UTC instant
Instant.now();

// Zoned
ZonedDateTime.now(ZoneId.of("Asia/Tokyo"));

// LocalDateTime（无时区，仅"墙上时间"）
LocalDateTime.now();

// 解析
ZonedDateTime.parse("2026-05-06T07:00:00Z[UTC]");
LocalDate.parse("2026-05-06");

// 算术
ZonedDateTime.now().plusDays(7).plusHours(3);

// 格式化
DateTimeFormatter.ISO_INSTANT.format(Instant.now());
```

**Java 8+ 永远用 `java.time`，不要用 `java.util.Date` / `Calendar`**（有大量坑）。

## 七、数据库存储

### PostgreSQL

| 类型 | 行为 | 推荐 |
|---|---|---|
| `timestamp` | 无时区 — 存什么显什么 | ❌ 跨时区危险 |
| `timestamptz` | 带时区 — 存为 UTC，按 client TZ 显示 | ✅ **默认用这个** |
| `date` | 仅日期 | 业务日（无时区概念） |

### MySQL

| 类型 | 行为 |
|---|---|
| `DATETIME` | 无时区，存什么显什么 |
| `TIMESTAMP` | 自动 UTC 转换（依赖 `time_zone` 会话变量） |

**踩坑**：MySQL 的 `TIMESTAMP` 4 字节，仅支持 1970-2038 范围。**新项目用 `DATETIME` + 应用层显式 UTC**。

### SQLite

无原生时间类型。一律存：

- ISO 8601 文本：`'2026-05-06T07:00:00Z'`（推荐，可读 + 排序）
- Unix 秒整数：`1715000000`

### Redis

存 ISO 8601 字符串或 Unix 秒。`EXPIREAT` 用 Unix 秒。

## 八、跨时区调度（DST 陷阱）

**业务**："每天日本时间 9:00 跑报表"

```javascript
// ❌ 错：直接 setInterval / cron 用 UTC
//   日本无 DST，但服务可能在 EST → 你的 cron 会跟着 DST 漂移

// ✅ 用支持时区的 cron 库（node-cron / croner）
import { Cron } from 'croner'
new Cron('0 9 * * *', { timezone: 'Asia/Tokyo' }, () => runReport())
```

**业务**："会议在纽约时间 2026-03-08 03:30"（DST 切换日）

```
03:00 → 04:00（春进），03:30 实际不存在
解决方案：
1. 拒绝该输入（UI 校验）
2. Temporal: 显式策略
   ZonedDateTime.from('2026-03-08T02:30[America/New_York]', { disambiguation: 'reject' })
   选项: 'compatible' | 'earlier' | 'later' | 'reject'
```

**重复时间**（11 月秋退）：同一个 `01:30` 出现两次。同样需要 disambiguation 策略。

## 九、API 设计建议

```jsonc
// 请求 / 响应都用 ISO 8601 UTC（带 Z）
{
  "createdAt": "2026-05-06T07:00:00Z",
  "scheduledFor": "2026-05-06T16:00:00+09:00",
  "timezone": "Asia/Tokyo"
}
```

- 客户端发送：UTC Instant
- 服务端存：UTC Instant + （需要时）原始时区
- 显示：客户端按用户偏好时区转换
- **避免**用本地时间字符串（如 `"2026-05-06 16:00"`）— 缺乏时区信息

## 十、常见 Bug 速查

| 现象 | 原因 |
|---|---|
| "少了一小时" | DST 没处理 / 服务器和数据库时区不同 |
| "日期变了" | 客户端在 GMT+9，存的"今天"传给 GMT-5 服务器变成"昨天" |
| "排序结果错乱" | 字符串排序 `'9-1' > '10-1'` 用 ISO 8601 `'2026-09-01' < '2026-10-01'` 才正确 |
| "倒计时偶尔跳秒" | Date.now() 不单调 — 用 `performance.now()` |
| "Docker 容器时间错" | 容器没装 tzdata / TZ 环境变量未设 |
| "MySQL `now()` 和 `UNIX_TIMESTAMP()` 不一致" | session 时区与 system 时区不同 |
| "iOS Safari 解析 `'2026-05-06 07:00:00'` 返 NaN" | 用 ISO 格式 `'2026-05-06T07:00:00Z'` |
| "60 秒？" | 闰秒（应用层一般不感知；NTP smear 处理） |

## 十一、Don'ts

- ❌ 用 `Date.now()` 减去 `Date.now()` 算 elapsed — 系统时钟可被 NTP 校准；用 `performance.now()`
- ❌ 给数据库列名为 `created_at` 但类型 `timestamp`（无 tz）— 用 `timestamptz`
- ❌ 字符串拼日期：`'2026-' + month + '-' + day` — 用 ISO + zero-pad
- ❌ 用 `setTimeout` 实现"明天 9:00 跑" — 长 setTimeout 不可靠（休眠 / 系统钟变化）；用 cron lib
- ❌ JavaScript `new Date('2026-05-06')` — 解析为 UTC 午夜，本地时区可能显示 5 月 5 日
- ❌ 把"24:00:00" 当合法时间 — 标准是 00:00:00（次日）
- ❌ 假设一年 = 365 天 / 一月 = 30 天 — 用 Temporal Duration 算
- ❌ 用 `moment()` 新代码 — 已 legacy，迁移到 luxon / date-fns / Temporal
- ❌ 跨服务传"本地时间字符串"无 timezone — 一律 UTC + ISO 8601
- ❌ Linux 服务器时区设业务时区（`TZ=Asia/Tokyo`）— 一律 UTC，应用层做转换

## 十二、参考资料

- IANA 时区数据库：https://www.iana.org/time-zones
- TC39 Temporal proposal：https://tc39.es/proposal-temporal/docs/
- date-fns / luxon / dayjs 官方文档
- "Falsehoods programmers believe about time"：https://gist.github.com/timvisee/fcda9bbdff88d45cc9061606b4b923ca
- Python zoneinfo：https://docs.python.org/3/library/zoneinfo.html
- Go time 包：https://pkg.go.dev/time
