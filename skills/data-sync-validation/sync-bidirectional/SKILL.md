---
name: sync-bidirectional
description: "扩展 ↔ 服务器双向同步设计规范（J-SOP 实战）。覆盖 chrome.storage.sync ↔ Echo /api/sync/* 的 push-and-merge / pull-and-merge 模式，敏感字段加密、tombstone deletedIds、id 去重、updatedAt 取新、IndexedDB 队列、license token 通道、SSRF 防护。当用户提到双向同步、bidirectional sync、push pull、merge、deletedIds、tombstone、IndexedDB、enqueue、sync-service、SOURCE_LIBRARY_FLUSH、syncStore 时使用。"
---

# Bidirectional Sync Skill — J-SOP 实战

## 何时使用

- 给某个用户配置 / 业务对象加跨设备同步
- 调试"另一台设备登录后数据没拉过来"或"删除了又冒出来"
- 改动 `sync-service.ts` 或 license-server 的 `/api/sync/*` 接口
- 设计新的同步对象（要规划 id / updatedAt / deletedIds / 加密字段）

## 一、双向同步整体模型

```
┌──────────────────┐     pullAndMerge      ┌──────────────────┐
│ chrome.storage   │  ◄────  GET /pull ──── │  License Server  │
│ .sync (config)   │                        │  user_data table │
│ .local (history) │  ──── POST /push ───►  │  (per user_id)   │
│  + IndexedDB     │     pushLocal          │   + cache        │
└──────────────────┘                        └──────────────────┘
       ▲                                              │
       │ enqueueUpsert                                │ encrypt sensitive
       │ flushSync (alarms 5min)                      │ rate-limit 10/min
```

J-SOP 真实实现：`@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\sync-service.ts`

## 二、同步对象的元字段约束（必备）

每个同步对象**必须**有以下字段：

| 字段 | 类型 | 用途 |
|---|---|---|
| `id` | string | 唯一 ID（`${ts}-${random}` 或 `crypto.randomUUID()`） |
| `updatedAt` | number (ms) | 最后修改时间 — merge 时取大者 |
| `createdAt` | number (ms) | 创建时间（不变） |
| `deletedAt?` | number (ms) | 软删除时间（用于 tombstone） |

**Server 侧额外**：
| `licenseKey` / `userId` | 数据隔离 |
| `serverUpdatedAt` | 服务器接收时间（防客户端时钟漂移） |

## 三、Pull 模式（pull-and-merge）

```typescript
// 启动 / 周期性拉取
async function pullAndMerge() {
  const remote = await fetchSync('/api/sync/pull')   // GET，license token
  const local = await syncStore.getAll()

  // 1. 合并 KV config（敏感字段先解密）
  const remoteConfig = await decryptSensitiveFields(remote.config)
  const merged = { ...local.config, ...remoteConfig }   // remote 优先（远程已是 merge 后的）
  // 但是！空字符串 / undefined 不要覆盖本地（B5 fix）
  for (const k of SENSITIVE_KEYS) {
    if (!remoteConfig[k]) merged[k] = local.config[k]
  }
  await syncStore.set('config', merged)

  // 2. 合并历史（按 id dedupe，updatedAt 取新）
  const localHistory = await localStore.get(IMAGE_HISTORY_KEY) ?? []
  const map = new Map(localHistory.map(h => [h.id, h]))
  for (const r of remote.imageHistory ?? []) {
    const existing = map.get(r.id)
    if (!existing || (r.updatedAt ?? 0) > (existing.updatedAt ?? 0)) {
      map.set(r.id, r)
    }
  }

  // 3. 应用 tombstone（删除 deletedIds 列表中的本地条目）
  for (const id of remote.imageHistoryDeletedIds ?? []) map.delete(id)

  // 4. 持久化（按 generatedAt 倒序，截断 MAX）
  const sorted = Array.from(map.values())
    .sort((a, b) => Number(b.generatedAt ?? 0) - Number(a.generatedAt ?? 0))
    .slice(0, IMAGE_HISTORY_MAX)
  await localStore.set(IMAGE_HISTORY_KEY, sorted)
}
```

## 四、Push 模式（push-local）

```typescript
async function pushLocal() {
  const local = await getLocalSnapshot()

  // 1. 加密敏感字段（aiApiKey 等）
  const config = { ...local.config }
  for (const k of SENSITIVE_KEYS) {
    if (config[k]) config[k] = await encryptField(config[k])
  }

  // 2. 收集 deletedIds（tombstone）
  const deletedIds = await localStore.get(IMAGE_HISTORY_DELETED_KEY) ?? []

  // 3. 推送
  const resp = await fetchSync('/api/sync/push', {
    method: 'POST',
    body: JSON.stringify({
      config,
      imageHistory: { items: local.imageHistory, deletedIds },
      copyHistory: local.copyHistory,
      copyTemplates: local.copyTemplates,
    }),
  })

  // 4. 推送成功后清空 deletedIds（已被服务器吸收）
  if (resp.ok) await localStore.set(IMAGE_HISTORY_DELETED_KEY, [])
}
```

## 五、Tombstone（软删除）模式

**问题**：本地删了，pull 又从远程拉回来，永远删不掉。

**解决**：本地保留 `deletedIds: string[]`，push 时上传，服务器把这些 id 加入"墓碑"，以后 pull 就不返回它们。

```typescript
// 本地删除
async function deleteImageHistory(id: string) {
  const list = await localStore.get(IMAGE_HISTORY_KEY) ?? []
  await localStore.set(IMAGE_HISTORY_KEY, list.filter(h => h.id !== id))

  // 加入 tombstone（capped 200，防膨胀）
  const deleted = await localStore.get(IMAGE_HISTORY_DELETED_KEY) ?? []
  const next = Array.from(new Set([id, ...deleted])).slice(0, IMAGE_HISTORY_DELETED_MAX)
  await localStore.set(IMAGE_HISTORY_DELETED_KEY, next)

  // 异步触发 push（debounce）
  schedulePush()
}
```

## 六、敏感字段加密（push/pull 透明）

```typescript
// J-SOP idiom: SENSITIVE_KEYS 列表 — 仅这些字段透明加解密
const SENSITIVE_KEYS = ['aiApiKey'] as const

// push 前
for (const k of SENSITIVE_KEYS) {
  if (config[k]) config[k] = await encryptField(config[k])
}

// pull 后
for (const k of SENSITIVE_KEYS) {
  if (config[k]) config[k] = await decryptField(config[k]).catch(() => config[k])
}
```

加密用 `crypto.subtle.encrypt(AES-GCM)`，密钥派生自 license key + 设备指纹（见 `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\crypto.ts`）。

**专用 endpoint**：`aiImageKey` 较敏感，单独走 `GET/PUT /api/sync/ai-image-settings` —— 服务器内部加密入库（B5 fix）。

## 七、IndexedDB 写入队列（业务对象）

业务对象（如选品库 SourceProduct）量大、要立即查询，用 IndexedDB + 推送队列：

```typescript
// 写入立即生效本地，异步 enqueue 推送
async function putProduct(product: SourceProduct) {
  await indexedDb.put('source_products', product)
  await enqueueUpsert(product)   // 写入 syncQueue 表
  schedulePush()                  // debounce 5s 后批量 flush
}

async function flushSync() {
  const queue = await indexedDb.getAll('syncQueue')
  if (!queue.length) return
  const resp = await fetchSync('/api/sync/source-products', {
    method: 'POST', body: JSON.stringify({ items: queue }),
  })
  if (resp.ok) await indexedDb.clear('syncQueue')
}

// service-worker.ts
chrome.alarms.create('sync-flush', { periodInMinutes: 5 })
chrome.alarms.onAlarm.addListener(a => { if (a.name === 'sync-flush') flushSync() })
```

## 八、Server 侧 handler 模式

```go
// handlers/sync.go
func HandleSyncPush(c echo.Context) error {
  licenseKey := c.Get("license_key").(string)        // LicenseAuth 中间件设置
  userID, err := GetUserIdByLicense(licenseKey)
  if err != nil { return c.JSON(401, err) }

  var payload SyncPushPayload
  if err := c.Bind(&payload); err != nil {
    return c.JSON(400, map[string]string{"error": "invalid body"})
  }

  // 1. config KV 写入（已加密字段不解密，原样存）
  for k, v := range payload.Config {
    if !IsAllowedConfigKey(k) { continue }            // 白名单
    db.Exec(`INSERT INTO user_data(user_id, key, value, updated_at)
             VALUES(?, ?, ?, ?)
             ON CONFLICT(user_id, key) DO UPDATE SET
               value = excluded.value,
               updated_at = excluded.updated_at`,
      userID, k, v, time.Now().UnixMilli())
  }

  // 2. tombstone 吸收
  for _, id := range payload.ImageHistory.DeletedIds {
    db.Exec(`UPDATE image_history SET deleted_at = ? WHERE user_id = ? AND id = ?`,
      time.Now().UnixMilli(), userID, id)
  }

  // 3. items merge（按 id, updatedAt 取新）
  for _, item := range payload.ImageHistory.Items {
    UpsertImageHistory(userID, item)
  }

  return c.JSON(200, map[string]string{"ok": "true"})
}

func HandleSyncPull(c echo.Context) error {
  userID := getUserIDFromLicense(c)

  // 拉取未删除的（deleted_at IS NULL）
  config := QueryUserConfig(userID)
  history := QueryImageHistory(userID, false)        // false = 不含已删除
  deletedIds := QueryDeletedIdsAfter(userID, c.QueryParam("since"))

  return c.JSON(200, map[string]interface{}{
    "config": config,
    "imageHistory": map[string]interface{}{
      "items": history,
      "deletedIds": deletedIds,
    },
  })
}
```

## 九、SSRF 防护（H-4）

如果同步对象包含用户提交的 URL（aiImageEndpoint），**必须**校验：

```typescript
// shared/url-validator.ts
export function validateEndpointUrl(url: string): { ok: boolean; reason?: string } {
  let u: URL
  try { u = new URL(url) } catch { return { ok: false, reason: 'invalid' } }

  // 1. 协议白名单
  if (!['http:', 'https:'].includes(u.protocol)) return { ok: false, reason: 'protocol' }

  // 2. 内网 / 元数据 IP 黑名单
  const host = u.hostname.toLowerCase()
  if (host === 'localhost' || host === '127.0.0.1' || host === '169.254.169.254')
    return { ok: false, reason: 'private' }
  if (/^10\.|^172\.(1[6-9]|2\d|3[01])\.|^192\.168\./.test(host))
    return { ok: false, reason: 'private' }

  return { ok: true }
}
```

## 十、Don'ts

- ❌ 用 `Date.now()` 客户端时钟做 last-write-wins → 客户端时钟漂移会丢数据，应该用 `serverUpdatedAt`
- ❌ pull 后整个 `localStore.set(history, remote)` 覆盖 → 丢失本地未推送的新增
- ❌ tombstone 列表无上限 → 长期累积爆内存（cap 200）
- ❌ 加密字段忘了 push 前加密 / pull 后解密 → 服务器存明文 / 客户端读乱码
- ❌ push 后不清空本地 deletedIds → 永远在推送相同 tombstone
- ❌ KV config 无白名单 → 用户能写任意 key 污染服务器
- ❌ 不限速 → 客户端死循环 push 把服务器 DDoS
- ❌ 服务器返回未删除 + deletedIds 不一致 → merge 死循环（删→拉→删→拉）

## 十一、调试清单

1. **设备 A 改后没在 B 看到** → 检查 A 是否触发了 `flushSync`（service-worker.ts alarms）
2. **删除了又冒出来** → 检查 deletedIds 是否成功 push 到服务器（看 admin user_data 表）
3. **敏感字段为乱码** → 检查 SENSITIVE_KEYS 列表 vs encrypt/decrypt 调用是否对称
4. **空字段覆盖本地** → 检查 `if (!remoteConfig[k]) merged[k] = local[k]`（B5 fix 模式）
5. **本地条数比服务器多** → 检查是否漏了 `pushLocal` 之前的初始 push

## 十二、参考文件

- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\sync-service.ts`（核心同步逻辑 785 行）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\storage.ts`（syncStore / localStore 抽象）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\crypto.ts`（敏感字段 AES-GCM）
- `@j:\J-SOP 伴随式自动化助手\j-sop-extension\src\shared\url-validator.ts`（SSRF 防护）
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\sync.go`（服务端 handler）
- `@j:\J-SOP 伴随式自动化助手\j-sop-license-server\db.go`（user_data 表 schema）
