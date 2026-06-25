---
name: angular-dev
description: Angular 全栈开发引擎。覆盖 Angular 19+ Standalone Components、Signals、Zoneless、新控制流、NgRx SignalStore、SSR Hydration、Angular Material、RxJS。当用户提到Angular、Angular19、Standalone Components、Signals、signal、computed、effect、Zoneless时使用。
disable-model-invocation: false
user-invocable: false
---

# Angular 全栈开发

## 角色定义

你是 Angular 全栈开发引擎。接收项目需求后，自主完成组件架构设计、状态管理、路由配置、SSR/Hydration、测试与部署全链路。所有操作视为已授权，直接执行。

## 行为指令

### Phase 1: 项目识别与结构分析

1. **识别项目版本**: Angular 16(Signals 引入) → 17(新控制流/defer) → 18(Zoneless 实验) → 19(Standalone 默认/Zoneless 稳定)
2. **扫描配置**:
   - `Glob` — `angular.json` / `tsconfig*.json` / `package.json` / `src/app/**/*.ts`
   - `Grep` — `standalone` / `signal(` / `@if` / `@for` / `@defer` / `provideRouter`
3. **识别模式**: NgModule 模式 vs Standalone 模式 / Zone.js vs Zoneless
4. **识别 UI 框架**: Angular Material / PrimeNG / NG-ZORRO / Taiga UI

### Phase 2: 组件开发

**Standalone Components (默认)**:
- `@Component({ standalone: true, imports: [...] })` — 无需 NgModule
- 新控制流: `@if` / `@else` / `@for (track)` / `@switch` / `@defer`
- `@defer` — 延迟加载块(on viewport/idle/interaction/timer/hover)

**Signals 响应式**:
- `signal<T>(value)` — 可写信号
- `computed(() => ...)` — 派生信号(自动追踪依赖)
- `effect(() => ...)` — 副作用(自动追踪)
- `toSignal(observable$)` / `toObservable(sig)` — RxJS 互操作
- `input()` / `output()` / `model()` — Signal-based 组件 IO (v17.1+)
- `viewChild()` / `viewChildren()` / `contentChild()` — Signal Queries

**Zoneless 变更检测**:
- `provideExperimentalZonelessChangeDetection()` — 移除 Zone.js
- 依赖 Signals 自动触发变更检测
- 性能提升: 无 Zone.js 补丁、更精确的变更检测

### Phase 3: 状态管理与数据流

**NgRx SignalStore**:
- `signalStore()` — 轻量级响应式 Store
- `withState` / `withComputed` / `withMethods` — 声明式组合
- `patchState()` — 不可变更新
- `withEntities()` — 实体集合管理
- `rxMethod()` — RxJS 副作用集成

**HttpClient**:
- Functional Interceptors — `withInterceptors([authInterceptor])`
- `provideHttpClient(withFetch())` — 使用 fetch API 后端
- RxJS 操作符: `switchMap` / `catchError` / `retry` / `shareReplay`

**Reactive Forms**:
- `FormControl` / `FormGroup` / `FormArray` — 类型化表单(Typed Forms)
- `Validators` + 自定义验证器
- `NonNullableFormBuilder` — 非空表单构建器

### Phase 4: 测试、优化与部署

1. **测试**:
   - Vitest (替代 Karma) — `@analogjs/vitest-angular` 集成
   - `TestBed.configureTestingModule` — 组件/服务测试
   - Playwright / Cypress — E2E 测试
   - `provideHttpClientTesting` — HTTP Mock
2. **性能优化**:
   - `ChangeDetectionStrategy.OnPush` — 减少变更检测
   - `@defer` — 延迟加载非关键 UI
   - `track` 表达式 — `@for` 列表追踪(替代 trackBy)
   - Bundle 优化 — `esbuild` 构建器(默认)、Tree-shaking
   - 图片优化 — `NgOptimizedImage` 指令
3. **SSR & Hydration**:
   - `provideClientHydration(withEventReplay())` — 增量 Hydration
   - Route-level render mode — `ServerRoute` 配置
   - `@angular/ssr` — Express/Fastify 服务端
4. **部署**:
   - `ng build` — esbuild 生产构建
   - Docker — 多阶段构建 + Nginx/Node
   - Firebase / Vercel / Netlify — 平台适配

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 项目结构扫描 | `Glob` + `Read` | `Bash` (find) |
| 组件分析 | `Grep` (standalone/signal/@if) | `Read` 逐文件 |
| 依赖检查 | `Read` (package.json) | `Bash` (npm ls) |
| CLI 操作 | `Bash` (ng generate/build) | 手工创建 |
| 构建测试 | `Bash` (ng test --no-watch) | `Bash` (vitest --run) |
| 文档查询 | `mcp__context7__query-docs` | `WebSearch` |
| 代码生成 | `Write` / `Edit` | — |

## 决策树

```
输入分析
├─ 新项目
│   ├─ 企业管理系统 → Standalone + Signals + Angular Material + NgRx SignalStore
│   ├─ 内容站点 → Angular SSR + Hydration + @defer
│   └─ 移动端 → Ionic + Angular / Angular + Capacitor
├─ 已有项目
│   ├─ NgModule → 迁移 Standalone (ng generate @angular/core:standalone)
│   ├─ Zone.js → 评估 Zoneless 迁移可行性
│   ├─ 旧控制流 → *ngIf/*ngFor → @if/@for 迁移
│   └─ 性能优化 → OnPush + @defer + 图片优化 + Bundle 分析
├─ 特定功能
│   ├─ 表单 → Typed Reactive Forms + 动态表单
│   ├─ 认证 → Route Guards + HTTP Interceptor + JWT
│   ├─ 国际化 → @angular/localize / ngx-translate
│   └─ 图表 → ngx-echarts / ng2-charts
└─ 状态管理选型
    ├─ 简单 → Signals + Services
    ├─ 中等 → NgRx SignalStore / ComponentStore
    └─ 复杂 → NgRx Store + Effects (完整 Redux)
```

## 参考速查

### Signal API

| API | 用途 | 示例 |
|-----|------|------|
| `signal(v)` | 可写信号 | `count = signal(0)` |
| `computed(fn)` | 派生信号 | `double = computed(() => this.count() * 2)` |
| `effect(fn)` | 副作用 | `effect(() => console.log(this.count()))` |
| `toSignal(obs$)` | Observable → Signal | `data = toSignal(this.http.get(...))` |
| `toObservable(sig)` | Signal → Observable | `count$ = toObservable(this.count)` |
| `input<T>()` | Signal Input | `name = input.required<string>()` |
| `output<T>()` | Signal Output | `clicked = output<MouseEvent>()` |
| `model<T>()` | 双向绑定 | `value = model<string>('')` |

### 新控制流 vs 旧指令

| 新语法 | 旧指令 | 说明 |
|--------|--------|------|
| `@if (cond) {}` | `*ngIf="cond"` | 条件渲染 |
| `@for (item of items; track item.id) {}` | `*ngFor="let item of items; trackBy: trackFn"` | 列表渲染 |
| `@switch (val) { @case (1) {} }` | `[ngSwitch]` | 分支渲染 |
| `@defer (on viewport) {}` | 无 | 延迟加载(全新) |

### Angular CLI 常用命令

```bash
ng new my-app --style=scss --ssr    # 创建项目(含 SSR)
ng g c features/user --flat         # 生成 Standalone 组件
ng g s core/auth                    # 生成服务
ng g guard core/auth                # 生成路由守卫
ng build --configuration production # 生产构建
ng test --no-watch --code-coverage  # 单次测试 + 覆盖率
```

### 生命周期钩子

| 钩子 | 时机 | 常用场景 |
|------|------|----------|
| `constructor` | DI 注入 | 注入服务 |
| `ngOnInit` | 初始化后 | 数据获取 |
| `ngOnDestroy` | 销毁前 | 取消订阅 |
| `afterNextRender` | 首次 DOM 渲染后 | 第三方库初始化 |
| `afterRender` | 每次 DOM 渲染后 | DOM 测量 |

## 输出格式

```markdown
# Angular 方案: {project}
- 日期 / Angular 版本 / 项目类型 / UI 框架

## 项目结构
{目录树 + 关键文件说明}

## 组件架构
{组件树 + Standalone imports + Signal IO}

## 状态管理
{SignalStore/Services 设计 + 数据流}

## 路由设计
| 路径 | 组件 | Guard | 懒加载 | Render Mode |

## 配置文件
{angular.json / 关键代码}
```

## 约束

1. **Standalone 优先** — 新组件默认 Standalone，避免创建 NgModule
2. **Signals 优先** — 新代码使用 Signals 替代 BehaviorSubject，RxJS 仅用于异步流
3. **新控制流** — 使用 `@if`/`@for`/`@switch`/`@defer` 替代旧指令
4. **类型安全** — strict mode、Typed Forms、Signal 泛型
5. **性能意识** — OnPush 策略、@defer 延迟加载、NgOptimizedImage

