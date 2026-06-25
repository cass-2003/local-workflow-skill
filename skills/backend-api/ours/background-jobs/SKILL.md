---
name: background-jobs
description: "后台任务系统实战。覆盖 cron / 定时任务、消息队列驱动的 worker、Sidekiq/Resque (Ruby)、Celery (Python)、Bull/BullMQ (Node)、asynq (Go)、River (Go/Postgres)、Temporal/Cadence 工作流、retry 与 dead-letter queue、可见性超时（visibility timeout）、并发控制、优先级队列、调度精度、跨进程任务幂等、worker 横向扩展、监控（Bull Board / Flower / asynqmon）。当用户提到 后台任务、background job、worker、queue、Sidekiq、Celery、Bull、BullMQ、asynq、Temporal、cron、定时任务、scheduled job、DLQ、visibility timeout、retry job 时使用。"
---

# Background Jobs Skill — 后台任务系统

## 何时使用

- 把慢操作（发邮件 / 生成 PDF / 转码视频 / 调用第三方 API）从请求路径剥离
- 定时任务（每天清理 / 每小时同步报表）
- 工作流编排（订单 → 库存 → 支付 → 发货 多步事务）
- 重试 / 失败处理 / 死信队列
- 选择 Sidekiq vs Bull vs Celery vs Temporal

## 一、基本架构

```
[ HTTP 请求 ]
       │  enqueue (毫秒级返回)
       ▼
[ Queue ]  ← Redis / RabbitMQ / SQS / Kafka / Postgres
       │
       ▼
[ Worker(s) ]  ← 多实例并行消费
       │
       ▼
[ DB / Email / 3rd-party API ]
```

**核心收益**：
- 解耦：请求快返回（用户体验）
- 削峰：突发流量入队，worker 按能力消费
- 重试：失败自动重新尝试
- 调度：未来某时执行

## 二、何时**不要**用 background job

- ❌ 简单同步够快（< 100ms）
- ❌ 用户期望立即看到结果（用 SSE / WS 反馈进度）
- ❌ 无幂等设计（队列默认 at-least-once，会重复）
- ❌ 只跑一次的小脚本（用 cron 直接跑）

## 三、跨语言库选型

| 语言 | 库 | 后端 | 卖点 |
|---|---|---|---|
| **Ruby** | Sidekiq | Redis | 业界标杆 / 简单 / 高性能 |
| **Ruby** | GoodJob / SolidQueue | Postgres | Rails 8 默认（无 Redis 依赖） |
| **Python** | Celery | Redis / RabbitMQ | 老牌 / 配置复杂 |
| **Python** | RQ | Redis | 简单替代 Celery |
| **Python** | Dramatiq / arq | Redis | 现代 / async |
| **Node** | BullMQ | Redis | 业界标准 / TS 友好 |
| **Node** | Agenda | MongoDB | 时间调度强 |
| **Go** | asynq | Redis | Sidekiq 风格 |
| **Go** | River | Postgres | 无 Redis / 事务级一致 |
| **Java** | Quartz | DB / 内存 | 老牌 / 调度强 |
| **多语言** | Temporal / Cadence | 自家集群 | 工作流 / Saga / 长事务 |
| **云** | AWS SQS + Lambda | / | 全托管 / 无 worker 维护 |
| **云** | GCP Cloud Tasks / Pub/Sub | / | 全托管 |

**默认推荐**：
- 简单任务：Sidekiq / BullMQ / asynq
- 复杂工作流（多步骤 / 长时间 / 补偿）：**Temporal**
- 不想运维 Redis：River（Go）/ SolidQueue（Rails）

## 四、BullMQ 标准模式（Node.js）

```typescript
import { Queue, Worker, QueueEvents } from 'bullmq'

const connection = { host: 'localhost', port: 6379 }

// 入队
const emailQueue = new Queue('email', { connection })
await emailQueue.add('welcome', {
  userId: '123',
  template: 'signup',
}, {
  jobId: `welcome-${userId}`,         // 幂等 key（重复 add 同 ID 不入队）
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
  removeOnComplete: { age: 3600, count: 1000 },
  removeOnFail: { age: 24 * 3600 },
})

// 延迟任务
await emailQueue.add('reminder', data, { delay: 60_000 })

// 定时任务（cron）
await emailQueue.add('daily-report', {}, {
  repeat: { pattern: '0 9 * * *', tz: 'Asia/Tokyo' },
})

// 优先级
await emailQueue.add('urgent', data, { priority: 1 })  // 越小越优先

// Worker
const worker = new Worker('email', async (job) => {
  switch (job.name) {
    case 'welcome': return sendWelcomeEmail(job.data)
    case 'reminder': return sendReminderEmail(job.data)
    case 'daily-report': return generateDailyReport()
  }
}, {
  connection,
  concurrency: 10,                    // 单 worker 并发数
  limiter: { max: 100, duration: 60_000 },  // 每分钟 100 个任务
})

worker.on('failed', (job, err) => {
  logger.error({ jobId: job?.id, err }, 'job failed')
})

// 优雅停机
process.on('SIGTERM', async () => {
  await worker.close()                // 等当前 job 处理完
  await emailQueue.close()
  process.exit(0)
})
```

## 五、Sidekiq 标准模式（Ruby）

```ruby
class WelcomeEmailJob
  include Sidekiq::Job
  sidekiq_options queue: 'email', retry: 3, dead: true

  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome(user).deliver_now
  end
end

# 入队
WelcomeEmailJob.perform_async(user.id)
WelcomeEmailJob.perform_in(1.hour, user.id)
WelcomeEmailJob.perform_at(Time.parse('2026-05-07 09:00'), user.id)
```

定时（sidekiq-cron / sidekiq-scheduler）：

```yaml
# config/schedule.yml
daily_report:
  cron: "0 9 * * *"
  class: DailyReportJob
  queue: reports
```

## 六、Celery 标准模式（Python）

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_welcome(self, user_id):
    user = User.objects.get(id=user_id)
    user.send_welcome_email()

# 入队
send_welcome.delay(user.id)                          # async
send_welcome.apply_async((user.id,), countdown=60)   # 60s 后
send_welcome.apply_async((user.id,), eta=datetime(2026,5,7,9))  # 指定时间
```

定时（Celery Beat）：

```python
app.conf.beat_schedule = {
    'daily-report': {
        'task': 'tasks.daily_report',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

## 七、可见性超时与重复消费

**at-least-once 投递**默认：

```
worker 取消息 → 消息隐藏 N 秒
worker 处理（< N 秒成功）→ ack → 消息删除
worker 处理超时 / 崩溃 → N 秒后消息重新可见 → 另一 worker 处理
```

**关键**：worker 必须在可见性超时内 ack；处理慢的任务需续期（heartbeat）或调大超时。

```typescript
// BullMQ: lockDuration / lockRenewTime
new Worker('queue', handler, {
  lockDuration: 60_000,           // 60s 内必须 ack 否则 stalled
  stalledInterval: 30_000,
})

// 任务内部续期
await job.extendLock(token, 30_000)
```

```python
# Celery: visibility_timeout (Redis broker)
app.conf.broker_transport_options = {'visibility_timeout': 3600}
# 长任务自己心跳
@app.task(bind=True)
def long_task(self):
    for chunk in chunks:
        process(chunk)
        self.update_state(state='PROGRESS')   # 更新 + 心跳
```

**业务必须幂等**（见 idempotency-design skill）— 重复消费是常态。

## 八、Retry 策略

```
[ 失败 ]
   │
   ├─▶ 是否可重试？（瞬时错？）
   │     │ 否 → 标记永久失败 → DLQ
   │     │ 是
   ├─▶ 退避（exponential + jitter）
   │     例：1s, 4s, 16s, 64s, 256s
   ├─▶ 重试 N 次后仍失败 → DLQ
   └─▶ 成功 → ack
```

```typescript
// BullMQ
{ attempts: 5, backoff: { type: 'exponential', delay: 1000 } }
// 实际间隔: 1s, 2s, 4s, 8s, 16s
```

**判断瞬时**：
- ✅ 可重试：网络超时 / 5xx / 数据库死锁 / 限流 429
- ❌ 不可重试：4xx 客户端错 / 业务校验失败 / 数据不存在

```typescript
// 抛 UnrecoverableError 跳过重试
import { UnrecoverableError } from 'bullmq'
if (!user) throw new UnrecoverableError(`user ${id} not found`)
```

## 九、Dead Letter Queue（DLQ）

重试用尽的任务进 DLQ：
- 不丢（保留供调试）
- 不阻塞（不再自动重试）
- 监控 / 告警 / 手动重放

```typescript
// BullMQ: 自动 — failed jobs 保留可手动 retry
const failed = await queue.getFailed()
await failed[0].retry()

// Sidekiq: dead set
# Sidekiq Web UI 看 Dead 队列，点 retry / delete

# AWS SQS: 配置 DLQ
RedrivePolicy: { deadLetterTargetArn: '...', maxReceiveCount: 5 }
```

**DLQ 报警必备**：DLQ 长度 > 阈值 → 告警 → 工程师介入。

## 十、定时任务（cron）精度

```
精度 vs 复杂度：
- ms 级实时调度    → Quartz / 自家 priority queue
- 秒级               → Sidekiq Cron / asynq Scheduler
- 分钟级 (常见)      → BullMQ repeat / Celery Beat / k8s CronJob
- 小时 / 天          → 任意工具
```

**单点 vs 分布式调度**：
- 多实例运行 BullMQ Repeat → 自动选举单实例触发，不重复
- Celery Beat 是单实例 → 部署多份会重复（用 redbeat / sentinel 解）
- K8s CronJob → 集群级单点

**漂移**：跨 DST / 夏令时区切换的 cron 行为不一致。生产 cron 跑 UTC 或显式时区。

## 十一、Temporal / 工作流

简单任务用 queue；**复杂多步业务**（订单流程）用 Temporal：

```typescript
// 工作流（持久化每步状态，崩了恢复）
async function orderWorkflow(orderId: string) {
  await reserveInventory(orderId)
  try {
    const charge = await chargePayment(orderId)
  } catch (e) {
    await releaseInventory(orderId)   // 补偿事务
    throw e
  }
  await sendShipment(orderId)
  await sendNotification(orderId)
}
```

**Temporal 优势**：
- 自动重试每个 activity
- 工作流状态持久化（worker 重启自动恢复）
- 支持长事务（数月）
- Saga 模式天然
- 可视化 UI 看每步执行

代价：架构复杂 + 学习曲线 + 需运维 Temporal cluster。

## 十二、监控与可观测

```
指标（Prometheus）:
- jobs_enqueued_total{queue, name}
- jobs_completed_total{queue, name}
- jobs_failed_total{queue, name, attempt}
- jobs_duration_seconds (histogram)
- queue_size{queue}
- queue_oldest_seconds          ← 关键：超阈值 = 处理跟不上
- worker_concurrent_active

告警：
- queue_oldest_seconds > 300        ← 任务积压
- failed rate > 5%
- DLQ size > 100
- worker 全挂（worker_count == 0）
```

**Web UI**：
- Sidekiq Web
- Bull Board / Bull Dashboard
- Flower (Celery)
- asynqmon
- Temporal UI

## 十三、Worker 横向扩展

```
QPS / (1 / 平均处理时长) = 所需并发

例：1000 jobs/s 任务，每个平均 100ms
   → 100 并发 worker

按业务高峰分配：
- 单 worker 进程 concurrency 10
- 跑 10 个 worker 实例 = 100 并发
```

K8s HorizontalPodAutoscaler 按队列长度扩缩容（KEDA）：

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
spec:
  scaleTargetRef: { name: email-worker }
  minReplicaCount: 1
  maxReplicaCount: 50
  triggers:
  - type: redis
    metadata:
      address: redis:6379
      listName: bull:email:wait
      listLength: "100"        # 每 100 个待处理 +1 实例
```

## 十四、Don'ts

- ❌ 任务 payload 含整个对象（user 完整 record）— 用 ID 让 worker 自己 fetch
- ❌ 任务带敏感数据（密码 / 卡号）— 队列日志可能泄漏
- ❌ 任务非幂等且 at-least-once — 重复处理（重复扣款）
- ❌ 同步调用第三方 API 不超时 — worker 卡死耗光并发
- ❌ Retry 不退避 / 不限次 — 雪崩
- ❌ DLQ 不监控 — 任务静默失败
- ❌ 1 个 worker 处理所有队列 — 慢任务阻塞快任务（用多队列 + 优先级）
- ❌ 长任务（10 分钟）没心跳 — 触发 visibility timeout 重新派发
- ❌ Celery Beat 多副本部署 — 任务重复（用 redbeat 锁）
- ❌ 用 cron 触发多实例 cmd 跑同一任务 — 加分布式锁或单点 leader
- ❌ Worker 不实现优雅停机 — kill 时 in-flight 任务丢失
- ❌ 在事务里 enqueue 任务，事务回滚但任务已入队（Outbox 模式解决）

## 十五、Outbox 模式（事务一致）

```sql
-- 在同一事务里写业务表 + outbox
BEGIN;
INSERT INTO orders (...) VALUES (...);
INSERT INTO outbox (event, payload) VALUES ('order_created', '{...}');
COMMIT;
```

后台 poller 读 outbox → enqueue 队列 → 删除已发送行。保证业务和任务"全成功或全失败"。

## 十六、参考资料

- Sidekiq Wiki：https://github.com/sidekiq/sidekiq/wiki
- BullMQ docs：https://docs.bullmq.io/
- Celery docs：https://docs.celeryq.dev/
- asynq docs：https://github.com/hibiken/asynq
- River（Postgres queue）：https://riverqueue.com/
- Temporal docs：https://docs.temporal.io/
- "Designing a Job Queue System" 系列文章
- "Pattern: Transactional outbox" / Microservices.io
- KEDA: https://keda.sh/
