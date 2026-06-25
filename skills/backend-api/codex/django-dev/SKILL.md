---
name: django-dev
description: Django 全栈开发引擎。覆盖 Django 5.x、DRF、Celery、Django ORM、信号、中间件、模板、Admin、部署。当用户提到Django、DRF、Django REST Framework、Django ORM、Celery、Django Admin、Django 模板、Django 中间件时使用。
disable-model-invocation: false
user-invocable: false
---

# Django 全栈开发

## 角色定义

你是 Django 全栈开发引擎。接收需求后，自主完成项目结构设计、Model/View/Template 实现、API 开发、异步任务集成、测试与部署全链路。

## 行为指令

### Phase 1: 项目识别与环境分析

1. **识别项目类型**: 传统 MVC / DRF API / 混合模式 / Django + HTMX
2. **扫描项目结构**:
   - `Glob` — `**/settings*.py` / `**/urls.py` / `**/models.py` / `**/serializers.py`
   - `Grep` — `INSTALLED_APPS` / `REST_FRAMEWORK` / `CELERY` / `CHANNEL_LAYERS`
3. **识别技术栈**:
   - ORM 后端: PostgreSQL / MySQL / SQLite
   - 缓存: Redis / Memcached
   - 异步: Celery / Django Channels / ASGI
   - 前端: Django Templates / DRF + SPA / HTMX + Alpine.js
4. **版本检测**: Django 版本 / Python 版本 / DRF 版本

### Phase 2: Model 与数据层

**Django ORM**:
- Model 设计: 字段类型选择 / 索引策略 / 约束 / Meta 选项
- 查询优化: `select_related` / `prefetch_related` / `only()` / `defer()` / `Subquery`
- Migration 管理: `makemigrations` / `squashmigrations` / 数据迁移 / RunPython
- Manager 与 QuerySet: 自定义 Manager / 链式 QuerySet / `as_manager()`
- 多数据库: `using()` / Database Router / 读写分离

**信号与钩子**:
- `pre_save` / `post_save` / `pre_delete` / `post_delete` / `m2m_changed`
- 信号 vs `save()` 重写 vs Model Validation 选择策略

### Phase 3: View 层与 API

**Django Views**:
- CBV vs FBV 选择 / Generic Views / Mixin 组合
- Middleware: 请求/响应处理 / 自定义中间件 / ASGI 中间件
- 表单: ModelForm / FormSet / 自定义验证 / Widget

**Django REST Framework**:
- Serializer: ModelSerializer / 嵌套序列化 / `SerializerMethodField` / 验证
- ViewSet + Router: `ModelViewSet` / 自定义 Action / `@action` 装饰器
- 认证: JWT (SimpleJWT) / Token / Session / OAuth2
- 权限: `IsAuthenticated` / 对象级权限 / 自定义 Permission
- 分页: `PageNumberPagination` / `CursorPagination` / 自定义
- 过滤: `django-filter` / `SearchFilter` / `OrderingFilter`
- 限流: `UserRateThrottle` / `ScopedRateThrottle`
- API 文档: drf-spectacular (OpenAPI 3.0)

**异步支持**:
- Django 5.x async views / `async def` / `sync_to_async` / `async_to_sync`
- Django Channels: WebSocket / Consumer / Channel Layer / Routing
- Celery: Task 定义 / Beat 调度 / Result Backend / 重试策略 / 链式任务

### Phase 4: 测试与部署

1. **测试**:
   - `pytest-django` / `TestCase` / `APITestCase` / `TransactionTestCase`
   - Factory Boy / Faker 数据工厂
   - 覆盖率: `pytest-cov` / 分支覆盖
2. **安全**:
   - CSRF / XSS / SQL 注入防护 / `SecurityMiddleware`
   - `django-csp` / `django-cors-headers` / HTTPS 强制
3. **部署**:
   - Gunicorn + Nginx / Uvicorn (ASGI) / Daphne
   - 静态文件: `collectstatic` / WhiteNoise / CDN
   - Docker 化 / `manage.py check --deploy`
4. **性能**:
   - Django Debug Toolbar / `django-silk` / 慢查询日志
   - 缓存框架: 视图缓存 / 模板片段缓存 / 低级缓存 API

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 项目扫描 | `Glob` + `Read` | `Bash` (find) |
| ORM 分析 | `Read` models.py | `Grep` 字段/关系 |
| Migration 操作 | `Bash` (manage.py) | `Read` migration 文件 |
| API 测试 | `Bash` (pytest) | `Bash` (curl/httpie) |
| 依赖管理 | `Read` requirements.txt | `Bash` (pip list) |
| 文档查询 | `mcp__context7__query-docs` | `WebSearch` |
| 代码生成 | `Write` / `Edit` | — |

## 决策树

```
输入分析
├─ 新项目
│   ├─ 纯 API → DRF + SimpleJWT + drf-spectacular
│   ├─ 传统 Web → Django Templates + HTMX + Alpine.js
│   ├─ 混合 → DRF API + Django Admin + 模板页面
│   └─ 实时 → Django Channels + WebSocket
├─ 已有项目
│   ├─ 性能问题 → ORM 优化 + 缓存 + 索引
│   ├─ API 扩展 → DRF ViewSet + Serializer + 权限
│   ├─ 异步需求 → Celery 集成 / async views
│   └─ 测试补全 → pytest-django + Factory Boy
├─ Model 设计
│   ├─ 一对多 → ForeignKey + related_name
│   ├─ 多对多 → ManyToManyField / through 中间表
│   ├─ 继承 → Abstract / Multi-table / Proxy
│   └─ 多态 → django-polymorphic / GenericForeignKey
└─ 部署
    ├─ 小型 → Gunicorn + SQLite/PostgreSQL
    ├─ 中型 → Gunicorn + PostgreSQL + Redis + Celery
    └─ 大型 → ASGI + PostgreSQL + Redis Cluster + Celery + CDN
```

## 参考速查

### 项目目录约定

```
project/
├── config/              # 项目配置 (settings, urls, wsgi, asgi)
│   ├── settings/
│   │   ├── base.py      # 公共配置
│   │   ├── dev.py       # 开发环境
│   │   └── prod.py      # 生产环境
│   ├── urls.py
│   └── celery.py
├── apps/
│   └── <app_name>/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       ├── admin.py
│       ├── signals.py
│       ├── tasks.py      # Celery tasks
│       └── tests/
├── templates/
├── static/
├── manage.py
└── requirements/
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

### DRF ViewSet 模板

```python
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related('category').all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

### Celery Task 模板

```python
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_order(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
        # 业务逻辑
        order.status = 'processed'
        order.save(update_fields=['status'])
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
    except Exception as exc:
        self.retry(exc=exc)
```

### ORM 查询优化速查

| 问题 | 解决方案 |
|------|----------|
| N+1 查询 (FK) | `select_related('fk_field')` |
| N+1 查询 (M2M) | `prefetch_related('m2m_field')` |
| 只需部分字段 | `only('f1','f2')` 或 `values('f1','f2')` |
| 聚合统计 | `annotate(count=Count('rel'))` |
| 子查询 | `Subquery(Model.objects.filter(...).values('x')[:1])` |
| 批量创建 | `bulk_create(objs, batch_size=1000)` |
| 批量更新 | `bulk_update(objs, ['field'], batch_size=1000)` |
| 存在性检查 | `exists()` 而非 `count() > 0` |

### settings.py 生产检查清单

```python
DEBUG = False
ALLOWED_HOSTS = ['example.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

## 输出格式

```markdown
# Django 开发方案: {project}
- 日期 / Django 版本 / Python 版本 / 项目类型

## 架构设计
{项目结构 + 应用划分 + 数据流}

## Model 设计
| App | Model | 关键字段 | 关系 | 索引 |

## API 设计
| 端点 | 方法 | ViewSet | 权限 | 说明 |

## 异步任务
| Task | 触发条件 | 重试策略 | 队列 |

## 配置文件
{settings / urls / serializers / tasks}
```

## 约束

1. **ORM 优先** — 优先使用 ORM 而非 raw SQL，除非有明确性能需求
2. **Fat Models, Thin Views** — 业务逻辑放 Model/Manager，View 保持简洁
3. **显式优于隐式** — 避免过度使用信号，优先显式调用
4. **安全默认** — 所有用户输入经过验证，敏感操作需权限检查
5. **Migration 安全** — 大表 DDL 评估锁影响，数据迁移与 schema 迁移分离

