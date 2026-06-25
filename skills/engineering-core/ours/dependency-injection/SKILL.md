---
name: dependency-injection
description: "依赖注入跨语言实战。覆盖 manual constructor injection（最佳实践）、container/IoC 框架（Spring / NestJS / Inversify / typedi / wire / fx / dagger）、何时不用 DI 框架、生命周期 scope（singleton/transient/scoped）、循环依赖处理、interface vs concrete 依赖、testability、setter vs ctor injection、service locator 反模式、属性注入、Go 显式依赖图（wire）vs 反射（fx）、composition root 模式。当用户提到 dependency injection、DI、IoC、控制反转、constructor injection、Inversify、NestJS DI、Spring Bean、Wire、Uber Fx、composition root、service locator、Mock 注入 时使用。"
---

# Dependency Injection Skill — DI 模式

## 何时使用

- 设计模块化应用（让组件可测试 / 可替换）
- 选择手动 DI 还是用框架（NestJS / Spring / Inversify）
- 调试循环依赖
- 区分 singleton / scoped / transient 生命周期
- 评审 PR 中"new XXX()"是否合适

## 一、核心思想

> 依赖**注入**进来，不是依赖**主动获取**。

```typescript
// ❌ 主动依赖（hard-coded）
class UserService {
  private db = new PostgresClient()                  // 改实现要改这
  private logger = console                            // 测试无法 mock
  getUser(id: string) { return this.db.query(...) }
}

// ✅ 依赖注入（构造器）
class UserService {
  constructor(private db: Database, private logger: Logger) {}
  getUser(id: string) {
    this.logger.info({ id }, 'fetching user')
    return this.db.query(...)
  }
}

// 调用方决定具体实现
const svc = new UserService(new PostgresClient(), pino())
```

**收益**：
1. **可测试**：注入 fake / mock
2. **可替换**：切 SQLite / Mock DB / Redis
3. **显式依赖**：构造器签名是合同
4. **解耦**：组件不知道依赖如何创建

## 二、何时**不**用 DI 框架

**多数小项目不需要框架**。手动 DI 在 composition root（main / 启动文件）一处装配就够：

```typescript
// composition-root.ts
export function buildApp() {
  const db = new PostgresClient(env.DATABASE_URL)
  const logger = pino({ level: env.LOG_LEVEL })
  const cache = new RedisClient(env.REDIS_URL)
  const userRepo = new UserRepo(db)
  const userSvc = new UserService(userRepo, cache, logger)
  const authSvc = new AuthService(userRepo, logger, env.JWT_SECRET)
  // ...
  return { userSvc, authSvc }
}
```

**只在以下情况上框架**：
- 大量服务（> 30 个）相互依赖，手装配维护痛
- 需要按请求 scope 注入（NestJS / Spring Web）
- 团队习惯 / 框架要求（Spring Boot / NestJS / Angular）

## 三、四种注入方式

### 1. Constructor Injection（**首选**）

```typescript
class Service {
  constructor(private db: Database) {}
}
```

依赖立即可见 / 不可变 / 强制必填。

### 2. Setter Injection（次选）

```typescript
class Service {
  private db?: Database
  setDb(db: Database) { this.db = db }
}
```

适合可选依赖。但用前必须检查 null。

### 3. Property Injection（框架专用）

```typescript
// NestJS
class Service {
  @Inject('DB') private db: Database
}

// Spring
@Autowired private Database db;
```

简洁但隐藏依赖（看不出有哪些）。

### 4. Method Injection（罕见）

```typescript
class Service {
  process(data: Data, db: Database) {
    return db.save(data)
  }
}
```

依赖每次调用传入。适合**仅一个方法用**的依赖。

## 四、TypeScript / Node 生态

### NestJS（注解 + 模块）

```typescript
@Module({
  providers: [UserService, UserRepo, { provide: 'DB', useFactory: () => createDB() }],
  exports: [UserService],
})
class UserModule {}

@Injectable()
class UserService {
  constructor(
    private readonly repo: UserRepo,
    @Inject('DB') private readonly db: Database,
  ) {}
}
```

特点：开箱即用 / scope 完整 / 但学习曲线 + reflect-metadata 依赖。

### InversifyJS（独立 DI 容器）

```typescript
const TYPES = { Database: Symbol('Database'), Logger: Symbol('Logger') }

@injectable()
class UserService {
  constructor(
    @inject(TYPES.Database) private db: Database,
    @inject(TYPES.Logger) private logger: Logger,
  ) {}
}

const container = new Container()
container.bind<Database>(TYPES.Database).to(PostgresClient).inSingletonScope()
container.bind<Logger>(TYPES.Logger).toConstantValue(pino())
container.bind<UserService>(UserService).toSelf()

const svc = container.get(UserService)
```

### tsyringe / typedi

类似 Inversify，更轻量。

### awilix（无 decorator，纯 JS 友好）

```typescript
import { createContainer, asClass, asValue } from 'awilix'

const container = createContainer()
container.register({
  db: asClass(PostgresClient).singleton(),
  logger: asValue(pino()),
  userService: asClass(UserService).scoped(),
})

const svc = container.resolve('userService')
```

UserService 构造器参数名 = 容器 key（自动匹配）。

## 五、Java / Spring

```java
@Service
public class UserService {
    private final UserRepository repo;
    private final EmailSender mailer;

    // 构造器注入 — Spring 4+ 推荐
    public UserService(UserRepository repo, EmailSender mailer) {
        this.repo = repo;
        this.mailer = mailer;
    }
}

@Repository
public class UserRepository { ... }

@Component
@ConditionalOnProperty("email.enabled")
public class SmtpEmailSender implements EmailSender { ... }
```

Spring 自动扫描 + 装配。Bean 默认 singleton。

**Bean Scope**：
- `singleton`（默认）：容器生命周期一份
- `prototype`：每次请求新建
- `request`：HTTP 请求生命周期
- `session`：HTTP 会话
- `application`：ServletContext

## 六、Go：Wire（编译期）vs Fx（运行时）

### Wire（Google）

```go
//go:build wireinject
package main

import "github.com/google/wire"

func InitializeApp(env Env) (*App, error) {
    wire.Build(NewDB, NewLogger, NewUserRepo, NewUserService, NewApp)
    return nil, nil
}
```

`wire` 命令生成代码：

```go
func InitializeApp(env Env) (*App, error) {
    db, err := NewDB(env)
    if err != nil { return nil, err }
    logger := NewLogger(env)
    repo := NewUserRepo(db)
    svc := NewUserService(repo, logger)
    return NewApp(svc), nil
}
```

**编译期**：零运行时开销 / 无反射 / 易调试。

### Fx（Uber）

```go
fx.New(
    fx.Provide(
        NewDB,
        NewLogger,
        NewUserRepo,
        NewUserService,
    ),
    fx.Invoke(StartServer),
).Run()
```

**运行时**：使用反射 / 灵活但难调试。

**新 Go 项目推荐 Wire**（更符合 Go "explicit is better"）。

## 七、Python

```python
# dependency-injector
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db = providers.Singleton(Database, dsn=config.db.dsn)
    user_repo = providers.Factory(UserRepo, db=db)
    user_service = providers.Factory(UserService, repo=user_repo)

container = Container()
container.config.from_yaml('config.yml')
svc = container.user_service()
```

或 **FastAPI Depends**（非传统 DI 但同效果）：

```python
def get_db() -> Database:
    return Database(...)

def get_user_repo(db: Database = Depends(get_db)) -> UserRepo:
    return UserRepo(db)

@app.get('/users/{id}')
def get_user(id: str, repo: UserRepo = Depends(get_user_repo)):
    return repo.get(id)
```

简单清晰 / 测试时 `app.dependency_overrides[get_db] = lambda: MockDB()`。

## 八、循环依赖

```
A 依赖 B
B 依赖 A
```

**这是设计问题**，不是 DI 问题。修复：
1. 提取共同接口到第三方（C），A、B 都依赖 C
2. 把 B 中需要 A 的部分挪出，让 A 调
3. 用 event / 回调反转（B 触发 event，A 监听）

**绕过**（不推荐）：
- Setter / property injection 延后注入
- 接受循环并 lazy-init

```typescript
// NestJS forwardRef 临时方案
@Inject(forwardRef(() => UserService))
private userService: UserService
```

## 九、Service Locator 反模式

```typescript
// ❌ Service Locator
class UserService {
  process() {
    const db = Container.get('db')          // 主动从容器拿
    const logger = Container.get('logger')
    // ...
  }
}
```

问题：
- 依赖隐藏（看不出 process 需要什么）
- 测试时要先 setup container
- 紧耦合到容器

**修复**：用 constructor injection。

## 十、生命周期 scope

```
Singleton:   整个应用一份
Scoped:      每次请求一份（HTTP 请求、消息、job）
Transient:   每次注入新建
```

**陷阱**：在 singleton 中注入 scoped → scoped 实例被升级为 singleton 行为，跨请求共享 → 数据泄露。

```typescript
// ❌ NestJS 反模式
@Injectable({ scope: Scope.DEFAULT })   // singleton
class UserController {
  constructor(private req: Request) {}   // request-scoped
  // 第一个请求的 req 被永久持有
}

// ✅ Controller 也声明 request scope
@Injectable({ scope: Scope.REQUEST })
```

## 十一、Testability（最大收益）

```typescript
describe('UserService', () => {
  const mockDb = { query: jest.fn() }
  const mockLogger = { info: jest.fn(), error: jest.fn() }
  const svc = new UserService(mockDb as any, mockLogger as any)

  it('logs and queries', async () => {
    mockDb.query.mockResolvedValue([{ id: '1' }])
    const u = await svc.getUser('1')
    expect(mockDb.query).toHaveBeenCalled()
    expect(mockLogger.info).toHaveBeenCalledWith({ id: '1' }, 'fetching user')
  })
})
```

不需要 framework / 不需要 container — 直接 `new` + 传 mock。

## 十二、Composition Root 模式

应用唯一一处"装配"所有对象图。其他地方不创建依赖：

```
[ main.ts / app.ts ]              ← Composition Root
   │ build all dependencies
   │
   ▼
[ HTTP server / CLI / worker ]
   │ inject built objects
   │
   ▼
[ Services ]
   │ pure constructor injection
   │
   ▼
[ Repositories / Clients ]
```

**Don't**：在 service 内部 `new SomeClient()`。

## 十三、interface vs concrete

```typescript
// ✅ 依赖接口（可换实现）
interface Database {
  query(sql: string): Promise<Row[]>
}
class UserService {
  constructor(private db: Database) {}
}

// 单元测试：
new UserService({ query: async () => [{ id: '1' }] })
```

**何时不需要接口**：
- 仅一种实现且永远只有一种
- 单元测试可以直接 mock 类（jest.mock）

不要为"未来可能"先抽象。Go 哲学：**消费方定义接口**（在使用处声明 interface 仅含需要的方法）。

## 十四、Don'ts

- ❌ 在 service 内部 `new RepoX()` — 失去测试 / 替换能力
- ❌ Singleton 注入 Scoped — scope 升级，跨请求泄漏
- ❌ Service Locator（主动 `container.get()`）
- ❌ 用 DI 框架就为了"看起来高级"，小项目用不上
- ❌ Property/Setter injection 当默认（用构造器）
- ❌ 构造器超长（10+ 参数）— 信号过度耦合，拆服务
- ❌ 注入"上下文"对象（God object）— 注入实际依赖
- ❌ 循环依赖用 forwardRef 不重构 — 治标不治本
- ❌ 用反射 DI 在 hot path（启动一次 OK，请求级有开销）
- ❌ DI 容器装"配置数据" / "数字 / 字符串" — 用 config 对象
- ❌ 在测试用真容器 + mock 替换 — 太复杂，直接 new + 传 mock

## 十五、何时合适何时过度

| 场景 | 用 DI |
|---|---|
| 小脚本 / CLI 工具 | ❌ 直接 new |
| 中型后端（10-30 服务） | ✅ 手动 + composition root |
| 大型后端（30+ 服务） | ✅ 框架（NestJS/Spring） |
| 前端组件 | 偶尔（React Context 也算 DI） |
| 库 / SDK | 内部用，对外简单 API |

## 十六、参考资料

- "Dependency Injection Principles, Practices, and Patterns" (Mark Seemann)
- "Composition Root" pattern：https://blog.ploeh.dk/2011/07/28/CompositionRoot/
- Spring DI Documentation
- NestJS Custom Providers：https://docs.nestjs.com/fundamentals/custom-providers
- Wire（Google）：https://github.com/google/wire
- Uber Fx：https://github.com/uber-go/fx
- Awilix：https://github.com/jeffijoe/awilix
- Martin Fowler "Inversion of Control Containers and the Dependency Injection pattern"
- "Why Constructor Injection Should be Preferred"
