---
name: typescript-advanced
description: "TypeScript 高级类型设计与类型体操。覆盖 utility types、conditional types、mapped types、template literal types、infer、branded types、discriminated unions、type predicates、satisfies 操作符、const 类型参数、类型层面 API 设计、tsconfig 严格选项调优。当用户提到 TypeScript 高级类型、type-level、类型体操、generics、conditional types、infer、branded types、discriminated union、satisfies、tsconfig strict、类型设计时使用。"
---

# TypeScript Advanced Skill — 高级类型设计

## 何时使用

- 设计公共库 / SDK 的类型 API（type-level public surface）
- 把"运行时检查"上提到"类型层面"消除整类 bug
- 调试 `Type 'X' is not assignable to 'Y'` 难以理解的错误
- TS 5.0+ 新特性落地（const type params / satisfies / decorators）
- 评审 PR 时检查 `as any` / `// @ts-ignore` / 弱类型

## 一、tsconfig 严格度（公共库 / 应用基线）

```jsonc
{
  "compilerOptions": {
    // 严格族（必开）
    "strict": true,                              // 一键开 8 个严格
    "noUncheckedIndexedAccess": true,            // arr[0] 推断为 T | undefined（强烈推荐）
    "exactOptionalPropertyTypes": true,          // { a?: T } 不允许 a: undefined 赋值
    "noImplicitOverride": true,                  // 子类必须 override 关键字
    "noPropertyAccessFromIndexSignature": true,  // obj.foo vs obj["foo"]，索引签名只能用方括号
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "useUnknownInCatchVariables": true,          // catch (e: unknown) 而非 any

    // 模块（现代项目）
    "module": "ESNext",
    "moduleResolution": "Bundler",               // 5.0+ 推荐（vite/turbopack）
    "verbatimModuleSyntax": true,                // import type 严格区分
    "isolatedModules": true,

    // 库构建
    "declaration": true,
    "declarationMap": true,
    "skipLibCheck": true,                        // 只跳过 node_modules 类型检查（速度）
  }
}
```

`noUncheckedIndexedAccess` 是新项目最该开的 — 把"索引访问可能 undefined"提到类型层。

## 二、Utility Types 速查（内置）

| 工具 | 含义 | 例子 |
|---|---|---|
| `Partial<T>` | 全字段可选 | `type PatchUser = Partial<User>` |
| `Required<T>` | 全字段必填 | `Required<{ a?: string }>` → `{ a: string }` |
| `Readonly<T>` | 全字段只读 | `Readonly<User>` |
| `Pick<T,K>` | 选子集 | `Pick<User, 'id' \| 'name'>` |
| `Omit<T,K>` | 排除子集 | `Omit<User, 'password'>` |
| `Record<K,V>` | 字典类型 | `Record<'zh' \| 'en', string>` |
| `Exclude<T,U>` | 联合类型剔除 | `Exclude<'a'\|'b'\|'c','b'>` → `'a'\|'c'` |
| `Extract<T,U>` | 联合类型提取 | `Extract<string\|number, string>` → `string` |
| `NonNullable<T>` | 去掉 null/undefined | `NonNullable<string\|null>` → `string` |
| `Parameters<F>` | 函数参数元组 | `Parameters<(a:string,b:number)=>void>` → `[string,number]` |
| `ReturnType<F>` | 函数返回 | `ReturnType<()=>Promise<User>>` → `Promise<User>` |
| `Awaited<T>` | unwrap promise | `Awaited<Promise<User>>` → `User` |
| `InstanceType<C>` | class 实例类型 | `InstanceType<typeof Foo>` |
| `ConstructorParameters<C>` | class 构造参数 | |

## 三、Conditional + infer（核心）

```typescript
// 1. 提取 Promise 内层类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T

// 2. 提取数组元素类型
type Element<T> = T extends (infer U)[] ? U : never
type X = Element<number[]>      // number

// 3. 函数第一个参数
type FirstArg<F> = F extends (a: infer A, ...rest: any[]) => any ? A : never

// 4. 嵌套递归 unwrap
type DeepAwaited<T> = T extends Promise<infer U> ? DeepAwaited<U> : T

// 5. 字符串模板提取（template literal type）
type ExtractRoute<T> = T extends `/${infer P}/${infer Q}` ? { p: P; q: Q } : never
type R = ExtractRoute<'/user/123'>  // { p: 'user'; q: '123' }
```

**陷阱**：分布式条件类型（distributive conditional types）

```typescript
type ToArr<T> = T extends any ? T[] : never
type X = ToArr<string | number>   // string[] | number[]   ← 在联合类型上分发了！

// 想要 (string | number)[] 必须包裹元组防分发：
type ToArr2<T> = [T] extends [any] ? T[] : never
type Y = ToArr2<string | number>  // (string | number)[]
```

## 四、Mapped Types

```typescript
// 1. 把所有方法变 async
type Asyncify<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? (...args: A) => Promise<R>
    : T[K]
}

// 2. 把所有 string 字段变 nullable
type NullableStrings<T> = {
  [K in keyof T]: T[K] extends string ? string | null : T[K]
}

// 3. 重命名 key（key remapping，TS 4.1+）
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
}
type UserGetters = Getters<{ name: string; age: number }>
// { getName: () => string; getAge: () => number }

// 4. 过滤掉某些 key
type StringKeys<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K]
}
```

## 五、Discriminated Union（必学模式）

```typescript
// 不要写：interface Result { ok: boolean; data?: T; error?: E }
// → ok=true 时 data 可能 undefined，类型不安全

// 要写：判别联合
type Result<T, E = Error> =
  | { ok: true;  data: T }
  | { ok: false; error: E }

function handle(r: Result<User>) {
  if (r.ok) {
    r.data    // ✅ User
    r.error   // ❌ 类型错误
  } else {
    r.error   // ✅ Error
    r.data    // ❌ 类型错误
  }
}

// 配 exhaustive check
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'square'; size: number }

function area(s: Shape): number {
  switch (s.kind) {
    case 'circle': return Math.PI * s.radius ** 2
    case 'square': return s.size ** 2
    default: {
      const _exhaust: never = s   // 加新 kind 没处理时编译错误
      return _exhaust
    }
  }
}
```

## 六、Branded Types（运行时无开销的强类型）

防止"两个 string 误用"（user ID vs order ID）：

```typescript
// brand 用 unique symbol 或字面量字符串
declare const UserIdBrand: unique symbol
type UserId = string & { readonly [UserIdBrand]: typeof UserIdBrand }

declare const OrderIdBrand: unique symbol
type OrderId = string & { readonly [OrderIdBrand]: typeof OrderIdBrand }

function userIdFromString(s: string): UserId { return s as UserId }

function fetchUser(id: UserId) { /* ... */ }

const oid: OrderId = 'ord_123' as OrderId
fetchUser(oid)               // ❌ Type 'OrderId' is not assignable to 'UserId'
fetchUser(userIdFromString('u_123'))  // ✅
```

适用：ID / 经过校验的 string（Email / URL）/ 单位（Meters / Seconds）。

## 七、Type Predicates（自定义类型守卫）

```typescript
// 用户态守卫
function isString(v: unknown): v is string {
  return typeof v === 'string'
}

// 复杂结构守卫
interface User { id: string; email: string }
function isUser(v: unknown): v is User {
  return typeof v === 'object' && v !== null
    && typeof (v as any).id === 'string'
    && typeof (v as any).email === 'string'
}

// Asserts 守卫（断言函数）
function assertUser(v: unknown): asserts v is User {
  if (!isUser(v)) throw new TypeError('not a User')
}

const data = JSON.parse(...)
assertUser(data)
data.email   // ✅ 此后类型缩窄为 User
```

更安全：**用 zod / valibot / arktype** 一次定义 schema 同时拿到运行时校验 + 类型：

```typescript
import { z } from 'zod'
const User = z.object({ id: z.string(), email: z.string().email() })
type User = z.infer<typeof User>            // 自动派生类型
const u = User.parse(data)                  // 运行时校验 + 类型守卫
```

## 八、`satisfies` 操作符（TS 4.9+）

保留字面量类型同时校验形状：

```typescript
// 之前：as 会扩展 / 丢字面量
const palette = {
  red:   '#FF0000',
  green: [0, 255, 0],
  blue:  '#0000FF',
} as const
palette.red.toUpperCase()    // ✅
// 但失去类型校验：写错 key 不报错

// satisfies：检查形状 + 保留字面量
type Color = string | [number, number, number]
const palette = {
  red:   '#FF0000',
  green: [0, 255, 0],
  blue:  '#0000FF',
} satisfies Record<string, Color>

palette.red.toUpperCase()    // ✅ string 可调
palette.green.length          // ✅ 知道是 tuple
```

## 九、const Type Parameters（TS 5.0+）

```typescript
// 不加 const：参数被扩展
function api<T extends string[]>(routes: T) { return routes }
const r1 = api(['/a', '/b'])    // string[]，丢失字面量

// 加 const：保留字面量
function api2<const T extends readonly string[]>(routes: T) { return routes }
const r2 = api2(['/a', '/b'])   // readonly ['/a', '/b']
```

## 十、template literal types 实战

```typescript
// CSS 单位
type CSSLength = `${number}${'px' | 'rem' | '%' | 'vh' | 'vw'}`
const a: CSSLength = '12px'      // ✅
const b: CSSLength = '12'        // ❌

// 路径参数
type ExtractParams<S> =
  S extends `${string}:${infer P}/${infer Rest}`
    ? P | ExtractParams<`/${Rest}`>
    : S extends `${string}:${infer P}`
      ? P
      : never

type Params = ExtractParams<'/users/:userId/posts/:postId'>
// "userId" | "postId"

// 强制 prefix
type EventName = `on${Capitalize<string>}`
```

## 十一、Don'ts

- ❌ `any` — 永远用 `unknown` + 类型守卫替代
- ❌ `as Type` 强转 — 运行时不检查；用 zod / type predicate
- ❌ `// @ts-ignore` — 用 `// @ts-expect-error` 才会在错误消失时报错提醒移除
- ❌ `Function` / `Object` 顶层类型 — 用 `(...args: never[]) => unknown` / `Record<string, unknown>`
- ❌ enum — 用 union literal type 或 `as const` 对象（运行时无开销 + tree-shake 友好）
- ❌ namespace — 用 module
- ❌ 在 interface 上加复杂条件类型 — 抽到 type alias 更易读
- ❌ 滥用类型体操让人看不懂 — public API 类型应**对调用方透明**
- ❌ `noUncheckedIndexedAccess` 不开 — 大量隐式 undefined bug
- ❌ 用 class 装数据 — 优先 `type` + 纯函数（FP 风格 + 序列化友好）

## 十二、调试技巧

```typescript
// 1. 用 type 别名 + hover 看实际类型
type _Debug = ExtractParams<'/users/:userId/posts/:postId'>
//    ^? 鼠标悬停看推断结果

// 2. 强制展开类型（解决 hover 显示 utility type 不展开问题）
type Expand<T> = T extends infer U ? { [K in keyof U]: U[K] } : never
type ShowMe = Expand<Pick<User, 'id' | 'email'>>

// 3. ts-toolbelt / type-fest 辅助库
import type { CamelCase, KebabCase, SnakeCase, Merge } from 'type-fest'

// 4. tsc --listFilesOnly 看实际 include 哪些文件
// 5. tsc --extendedDiagnostics 看编译瓶颈
```

## 十三、参考资料

- TS Handbook：https://www.typescriptlang.org/docs/handbook/2/types-from-types.html
- type-fest（实用类型库）：https://github.com/sindresorhus/type-fest
- TypeScript 类型体操题库：https://github.com/type-challenges/type-challenges
- Effective TypeScript（书 / Dan Vanderkam）
- Total TypeScript（Matt Pocock）：https://www.totaltypescript.com/
- Zod（运行时 + 类型）：https://zod.dev/
