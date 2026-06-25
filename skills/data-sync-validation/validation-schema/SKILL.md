---
name: validation-schema
description: "Schema 校验与运行时类型保证实战。覆盖 Zod / Valibot / ArkType / Yup（TS）、Pydantic v2（Python）、Joi（Node）、JSON Schema 标准、cattrs / msgspec、自动 OpenAPI 派生、客户端服务端 schema 共享、parse vs safeParse、错误信息国际化、性能对比、与表单库集成（react-hook-form / Formik）、与 ORM 集成（Prisma）。当用户提到 schema 校验、validation、Zod、Valibot、ArkType、Pydantic、Joi、JSON Schema、parse、safeParse、表单校验、OpenAPI 派生、运行时类型 时使用。"
---

# Validation Schema Skill — Schema 校验

## 何时使用

- API 边界校验请求 body / query / params
- 解析外部数据（JSON file / 第三方 API 响应 / env vars）
- 表单提交校验
- 配置文件校验启动时崩溃
- 想从一份 schema 同时拿到运行时校验 + TS 类型 + OpenAPI 文档

## 一、为什么需要 Schema 库

```typescript
// ❌ 仅 TS 类型
interface User { id: string; email: string; age: number }
const user: User = JSON.parse(rawJSON)
// 编译通过 — 但运行时 rawJSON 可能根本不是 User 形状
user.email.toLowerCase()    // 💥 cannot read of undefined

// ✅ 运行时校验 + 类型派生
import { z } from 'zod'
const User = z.object({
  id: z.string(),
  email: z.string().email(),
  age: z.number().int().min(0),
})
type User = z.infer<typeof User>          // 自动派生
const user = User.parse(rawJSON)           // 失败抛
```

**核心诉求**：边界处一次定义，类型 + 运行时校验 + 错误信息一起拿。

## 二、TS 生态主流库对比

| 库 | 大小 | 性能 | 特色 |
|---|---|---|---|
| **Zod** | ~12KB | 中 | 业界标准，生态最大 |
| **Valibot** | ~1KB | 高 | 模块化，tree-shakable，体积小 90% |
| **ArkType** | ~30KB | 极高 | TS 字面量语法，类型推导极强 |
| **Yup** | ~50KB | 中 | 老牌，Formik 集成好 |
| **Joi** | ~150KB | 中 | Node 后端老牌，类型推导弱 |
| **typia** | 编译时 | 极高 | TS 转译时生成校验代码 |

### Zod 示例

```typescript
import { z } from 'zod'

const Order = z.object({
  id:        z.string().uuid(),
  userId:    z.string().min(1),
  items:     z.array(z.object({
    sku: z.string(),
    qty: z.number().int().positive(),
  })).min(1),
  total:     z.number().nonnegative(),
  createdAt: z.coerce.date(),         // 字符串 → Date
  status:    z.enum(['pending','paid','shipped']),
  metadata:  z.record(z.string()).optional(),
})

type Order = z.infer<typeof Order>

// 严格 parse（失败抛）
const order = Order.parse(rawData)

// 软 parse（不抛）
const result = Order.safeParse(rawData)
if (!result.success) {
  console.log(result.error.issues)    // 详细错误数组
}
```

### Valibot 示例（pipe-friendly）

```typescript
import * as v from 'valibot'

const Order = v.object({
  id: v.pipe(v.string(), v.uuid()),
  total: v.pipe(v.number(), v.minValue(0)),
})

const result = v.safeParse(Order, rawData)
```

体积优势：bundle 只含用到的 validator（tree-shaking）。

### ArkType 示例（TS 字面量）

```typescript
import { type } from 'arktype'

const Order = type({
  id: 'string.uuid',
  total: 'number > 0',
  status: "'pending' | 'paid' | 'shipped'",
})

type Order = typeof Order.infer
const out = Order(rawData)
```

最强的类型推导：错误位置精确到字段。

## 三、Python：Pydantic v2

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class Order(BaseModel):
    model_config = ConfigDict(extra='forbid')   # 拒绝多余字段

    id: str = Field(pattern=r'^[0-9a-f-]{36}$')
    user_id: str
    total: float = Field(ge=0)
    status: Literal['pending', 'paid', 'shipped']
    items: list[OrderItem] = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)

# 解析
order = Order.model_validate(raw_data)

# Dict / JSON 输出
order.model_dump()
order.model_dump_json()
```

Pydantic v2 用 Rust 重写（pydantic-core），**性能 5-50x v1**。FastAPI 内置。

## 四、JSON Schema 标准

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["id", "email"],
  "properties": {
    "id":    { "type": "string", "format": "uuid" },
    "email": { "type": "string", "format": "email" },
    "age":   { "type": "integer", "minimum": 0 }
  },
  "additionalProperties": false
}
```

**优势**：跨语言 / 跨工具（OpenAPI 内嵌使用）/ AsyncAPI / Kubernetes CRD / VS Code 配置校验
**劣势**：手写啰嗦 / TS 类型不直接派生

工具：
- TS → JSON Schema：`zod-to-json-schema` / `valibot-to-json-schema`
- JSON Schema → TS：`json-schema-to-typescript`
- 校验器：`ajv`（TS / Node 最快）/ `jsonschema`（Python）

## 五、与 OpenAPI 派生

```typescript
// 一份 schema → API + 文档 + 类型 + 客户端 SDK
import { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi'
extendZodWithOpenApi(z)

const Order = z.object({
  id: z.string().uuid().openapi({ example: '...' }),
}).openapi('Order')

// 生成 OpenAPI spec
const generator = new OpenApiGeneratorV3(registry.definitions)
const document = generator.generateDocument({ ... })
```

**Stack**：
- **Hono / Elysia / tRPC / Fastify** + Zod → OpenAPI / 类型化客户端
- **FastAPI** + Pydantic → OpenAPI 自动
- **NestJS** + class-validator + Swagger 装饰器

## 六、表单库集成

### react-hook-form + Zod

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

const Form = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'At least 8 characters'),
})

function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(Form),
  })

  return <form onSubmit={handleSubmit(submit)}>
    <input {...register('email')} />
    {errors.email && <span>{errors.email.message}</span>}
  </form>
}
```

`@hookform/resolvers` 也支持 valibot / arktype / yup / joi。

## 七、错误信息国际化

```typescript
const Email = z.string()
  .min(1, 'errors.required')
  .email('errors.invalid_email')

// 在表单 UI 处翻译
{errors.email && <span>{t(errors.email.message)}</span>}
```

或自定义 error map：

```typescript
z.setErrorMap((issue, ctx) => {
  if (issue.code === z.ZodIssueCode.invalid_string && issue.validation === 'email') {
    return { message: t('errors.invalid_email') }
  }
  return { message: ctx.defaultError }
})
```

## 八、性能比较（粗略）

| 库 | 解析 1M 简单对象 |
|---|---|
| typia | ~50ms (compile-time) |
| Pydantic v2 | ~80ms |
| ArkType | ~150ms |
| Valibot | ~200ms |
| Zod | ~600ms |
| Joi | ~800ms |
| Pydantic v1 | ~3000ms |

**热路径**慎选 Zod；冷路径（API 边界 + 表单）任意选。

## 九、Coercion / 类型转换

```typescript
// 字符串转数字
z.coerce.number()              // "42" → 42
z.coerce.date()                // ISO string → Date
z.coerce.boolean()             // "true" → true（注意："false" 也变 true！）

// 安全的 string-to-boolean
const Bool = z.enum(['true','false']).transform(v => v === 'true')

// transform 任意逻辑
const TrimmedEmail = z.string()
  .transform(s => s.trim().toLowerCase())
  .pipe(z.string().email())
```

## 十、配置文件校验（启动即崩）

```typescript
// 读 env vars
const Env = z.object({
  NODE_ENV: z.enum(['development','production','test']),
  DATABASE_URL: z.string().url(),
  PORT: z.coerce.number().int().positive(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
})

export const env = Env.parse(process.env)
// 启动时缺失立即崩 — 不要等到运行时才发现
```

**强烈推荐**所有项目都做。

## 十一、与 ORM 集成

### Prisma + Zod

```typescript
// Prisma 自动生成基础 schema
import { z } from 'zod'
import { UserSchema } from './prisma-zod-generated'    // zod-prisma-types 生成

// 业务校验在 Prisma 之上加
const CreateUserInput = UserSchema.pick({ email: true, name: true }).extend({
  password: z.string().min(8),
})
```

### Drizzle

Drizzle ORM 原生集成 Zod：

```typescript
import { createInsertSchema, createSelectSchema } from 'drizzle-zod'
const insertUser = createInsertSchema(users)    // 从表定义自动派生
```

## 十二、Don'ts

- ❌ 用 TS interface 当运行时校验 — 编译后类型擦除，只是文档
- ❌ `any` / `unknown` 后不校验直接用
- ❌ catch parse error 静默吞 — 应记日志 / 返 400
- ❌ schema 散落各处 — 统一 `schemas/` 目录
- ❌ 在 hot path 反复 parse 同一对象 — 缓存或在边界一次
- ❌ 服务端不校验仅依赖前端校验 — 用户能绕过任何客户端
- ❌ 错误信息英文 hardcode — 用 i18n key
- ❌ 把 password 字段 `.parse()` 后 log — 脱敏或 omit
- ❌ Pydantic v1 新项目 — 升 v2 性能巨大提升
- ❌ Joi 新项目 — 类型推导弱，Zod / Valibot 更现代

## 十三、最佳实践清单

- [ ] API 边界（请求 + 响应）都校验
- [ ] env vars 校验在启动时
- [ ] schema 与 type 用 `infer`，单一 source of truth
- [ ] 错误信息可 i18n
- [ ] 一份 schema 派生 OpenAPI / 表单 / SDK
- [ ] 客户端服务端共享 schema（monorepo 的 `packages/types`）
- [ ] 严格模式（`additionalProperties: false` / `strict()` / `extra='forbid'`）拒绝未知字段
- [ ] 测试边界：缺字段 / 多字段 / 错类型 / 边界值

## 十四、参考资料

- Zod: https://zod.dev/
- Valibot: https://valibot.dev/
- ArkType: https://arktype.io/
- Pydantic v2: https://docs.pydantic.dev/
- JSON Schema: https://json-schema.org/
- Ajv (JSON Schema validator): https://ajv.js.org/
- "Parse, don't validate"（Alexis King）：https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- typia: https://typia.io/
