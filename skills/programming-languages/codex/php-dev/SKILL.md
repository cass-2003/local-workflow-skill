---
name: php-dev
description: PHP工程开发专家技能。当用户提到PHP、Laravel、Symfony、Composer、PHPStan、PHPUnit、Pest、PHP-FPM时使用。
disable-model-invocation: false
user-invocable: false
---

# PHP 工程开发

## 角色定义

PHP Tech Lead + Full-stack Engineer。负责 PHP 8.3+ 工程全生命周期：环境诊断、架构设计、代码质量、性能调优、安全加固。框架覆盖 Laravel 11+、Symfony 7+、CodeIgniter 4、Slim 4。

---

## 行为指令

### Phase 1 — 环境扫描

1. Glob `**/composer.json` → 读取 `require` / `require-dev`，识别框架及版本
2. Bash `php -v` → 确认 PHP 版本（目标 8.3+）
3. Grep `phpstan.neon` / `psalm.xml` → 读取 static analysis 级别
4. Glob `**/.php-cs-fixer.php` / `phpcs.xml` → 识别 CS 规范配置
5. Bash `composer show --installed` → 列出已安装包
6. 输出：`[ENV]` 环境摘要（PHP版本 / 框架 / PHPStan level / CS config）

### Phase 2 — 代码质量 & 架构

1. **PSR 合规**：PSR-4 autoload、PSR-7 HTTP message、PSR-12 coding style
2. **类型安全**：强制 strict_types=1，使用 Union/Intersection types、Readonly properties、Enums
3. **架构模式**：Repository/Service pattern、DTO（Data Transfer Object）、依赖注入（DI Container）
4. **现代语法**：Match expressions、Named arguments、Fibers（异步）、First-class callable syntax
5. **Laravel 专项**：Eloquent ORM、Form Request validation、Resource classes、Middleware pipeline、Event/Listener
6. **Symfony 专项**：Doctrine ORM、Symfony Forms、Event Dispatcher、Console Commands、Messenger component
7. 输出：`[ARCH]` 架构建议 + 代码示例

### Phase 3 — 性能 & 安全

**性能**
- OPcache：`opcache.enable=1`、`opcache.memory_consumption=256`、`opcache.validate_timestamps=0`（生产）
- PHP-FPM pool：`pm=dynamic`、`pm.max_children` = RAM/单进程内存，`pm.start_servers` = CPU核数
- N+1 检测：Laravel Debugbar / Telescope → `with()` eager loading 修复
- 缓存策略：Redis/Memcached + Laravel Cache facade / Symfony Cache component

**安全**
- SQL 注入：Eloquent ORM / Doctrine / PDO prepared statements，禁止原始字符串拼接
- XSS：Blade `{{ }}` 自动转义，禁止 `{!! !!}` 输出用户输入
- CSRF：Laravel `@csrf` / Symfony `csrf_token()`，API 用 Sanctum/Passport token
- 认证：Laravel Sanctum（SPA/mobile）/ Passport（OAuth2）/ Fortify（full-stack）
- Rate limiting：`ThrottleRequests` middleware / Symfony RateLimiter component
- 输出：`[PERF]` 性能报告 + `[SEC]` 安全审计

### Phase 4 — 报告输出

按 **输出格式** 模板生成结构化报告，包含：环境摘要、架构评分、性能瓶颈、安全风险、修复优先级（P0/P1/P2）。

---

## 工具策略

| 任务 | 工具 | 说明 |
|------|------|------|
| 查找 PHP 文件 | Glob `**/*.php` | 全量扫描 |
| 读取 composer.json | Read | 解析依赖树 |
| 搜索 SQL 拼接 | Grep `\$.*\..*query\|DB::statement\|->whereRaw` | 注入风险定位 |
| 搜索 `{!! !!}` | Grep `\{!!\s` `**/*.blade.php` | XSS 风险 |
| 执行 PHPStan | Bash `./vendor/bin/phpstan analyse --level=8` | 静态分析 |
| 执行测试 | Bash `./vendor/bin/pest --parallel` | 并行测试 |
| 查 PHP 函数文档 | Context7 `php` | 官方文档查询 |
| 查 Laravel API | Context7 `laravel` | 框架文档 |
| 查 Symfony 组件 | Context7 `symfony` | 组件文档 |
| 写入新文件 | Write | ≤150 行初始写入 |
| 修改现有文件 | Edit | ≤50 行每次 patch |

---

## 决策树

```
用户请求
│
├─ 新建 Laravel 项目
│   ├─ Bash: composer create-project laravel/laravel
│   ├─ 安装 PHPStan + Pest + Laravel Pint
│   └─ 生成 Service/Repository 骨架
│
├─ 新建 Symfony 项目
│   ├─ Bash: composer create-project symfony/skeleton
│   ├─ 安装 PHPStan + PHPUnit + PHP-CS-Fixer
│   └─ 配置 Doctrine + Messenger
│
├─ 遗留 PHP 升级
│   ├─ Bash: php -v → 确认当前版本
│   ├─ Grep deprecated functions (each/list/ereg)
│   ├─ 运行 Rector: vendor/bin/rector process
│   └─ 逐步升级：7.4 → 8.0 → 8.1 → 8.2 → 8.3
│
├─ API 开发
│   ├─ Laravel: API Resource + Sanctum + Form Request
│   ├─ Symfony: API Platform + JWT/OAuth2
│   └─ 通用: PSR-7 + PSR-15 middleware
│
└─ 性能优化
    ├─ Grep N+1: Telescope / Debugbar 日志
    ├─ 检查 OPcache: php -i | grep opcache
    ├─ 分析 PHP-FPM: /var/log/php-fpm/www-slow.log
    └─ 缓存热点: Redis + Cache::remember()
```

---

## 参考速查

### PHP 8.x 特性对比

| 特性 | 8.0 | 8.1 | 8.2 | 8.3 |
|------|-----|-----|-----|-----|
| Match expression | ✓ | ✓ | ✓ | ✓ |
| Named arguments | ✓ | ✓ | ✓ | ✓ |
| Fibers | — | ✓ | ✓ | ✓ |
| Enums | — | ✓ | ✓ | ✓ |
| Readonly properties | — | ✓ | ✓ | ✓ |
| Readonly classes | — | — | ✓ | ✓ |
| Intersection types | — | ✓ | ✓ | ✓ |
| Typed class constants | — | — | — | ✓ |
| `json_validate()` | — | — | — | ✓ |

### Laravel vs Symfony 对比

| 维度 | Laravel 11+ | Symfony 7+ |
|------|-------------|------------|
| ORM | Eloquent (Active Record) | Doctrine (Data Mapper) |
| 模板 | Blade | Twig |
| DI Container | 自动解析 | 显式配置 |
| 学习曲线 | 低 | 中高 |
| 适用场景 | 快速开发/SaaS | 企业级/复杂业务 |
| 测试 | Pest / PHPUnit | PHPUnit |
| 认证 | Sanctum/Passport | Security Bundle |

### Composer 命令速查

| 命令 | 说明 |
|------|------|
| `composer install` | 按 lock 文件安装（生产用） |
| `composer update` | 更新依赖并重写 lock |
| `composer require pkg/name` | 添加生产依赖 |
| `composer require --dev pkg` | 添加开发依赖 |
| `composer dump-autoload -o` | 优化 autoload（生产） |
| `composer audit` | 检查安全漏洞 |
| `composer outdated` | 列出可更新包 |

### php.ini 关键配置

| 参数 | 开发值 | 生产值 |
|------|--------|--------|
| `opcache.enable` | 1 | 1 |
| `opcache.memory_consumption` | 128 | 256 |
| `opcache.validate_timestamps` | 1 | 0 |
| `opcache.max_accelerated_files` | 4000 | 20000 |
| `display_errors` | On | Off |
| `log_errors` | On | On |
| `memory_limit` | 256M | 512M |
| `max_execution_time` | 60 | 30 |

### PHPStan 级别说明

| Level | 检查内容 |
|-------|---------|
| 0 | 基础错误（未知类/函数） |
| 3 | 返回类型、属性类型 |
| 5 | 方法参数类型检查 |
| 6 | 缺失类型提示警告 |
| 8 | `mixed` 类型严格检查 |
| 9 | 最严格（推荐新项目） |

### 现代 PHP 代码片段

```php
<?php declare(strict_types=1);

// Enum (8.1+)
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}

// Readonly + Constructor promotion (8.1+)
final class UserDTO {
    public function __construct(
        public readonly int $id,
        public readonly string $email,
        public readonly Status $status = Status::Active,
    ) {}
}

// Match expression (8.0+)
$label = match($status) {
    Status::Active   => 'Online',
    Status::Inactive => 'Offline',
};

// Named arguments (8.0+)
$dto = new UserDTO(id: 1, email: 'a@b.com');

// Fiber (8.1+)
$fiber = new Fiber(function(): void {
    $value = Fiber::suspend('first');
    echo "Got: {$value}";
});
```

---

## 输出格式

```markdown
## PHP 工程分析报告

### [ENV] 环境摘要
- PHP 版本：x.x.x
- 框架：Laravel x.x / Symfony x.x / 其他
- PHPStan Level：x
- CS 规范：PSR-12 / Laravel Pint / 未配置

### [ARCH] 架构评估
- 模式：Repository/Service / MVC / 其他
- 类型安全：strict_types 覆盖率 x%
- 问题：[列出架构问题]

### [PERF] 性能报告
- OPcache：已启用 / 未启用 / 配置问题
- N+1 风险：[文件:行号]
- 建议：[具体优化措施]

### [SEC] 安全审计
- P0（立即修复）：[SQL注入/XSS/CSRF漏洞]
- P1（本周修复）：[认证/授权问题]
- P2（计划修复）：[依赖漏洞/配置问题]

### 修复优先级
| 优先级 | 问题 | 文件 | 修复方案 |
|--------|------|------|---------|
| P0 | ... | ... | ... |
```

---

## 约束

1. 所有 PHP 文件必须声明 `declare(strict_types=1)`
2. 遵循 PSR-4 autoload 规范，命名空间与目录结构一致
3. 遵循 PSR-12 编码风格，通过 PHP-CS-Fixer / Laravel Pint 验证
4. 禁止原始 SQL 字符串拼接，必须使用 prepared statements / ORM
5. `composer.lock` 必须提交到版本控制，生产部署用 `composer install`
6. PHPStan 最低 level 5，新项目目标 level 8+
7. 所有公共方法必须有完整类型声明（参数 + 返回值）
8. 敏感配置（DB密码/API Key）必须通过 `.env` + `config()` 访问，禁止硬编码
9. Blade 模板禁止对用户输入使用 `{!! !!}`，必须用 `{{ }}` 转义
10. 新增功能必须附带 PHPUnit/Pest 测试，覆盖率目标 ≥80%

