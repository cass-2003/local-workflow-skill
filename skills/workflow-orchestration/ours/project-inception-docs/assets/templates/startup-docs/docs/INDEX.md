# 文档索引

版本：v0.1
日期：<YYYY-MM-DD>
状态：<draft / reviewed / active>

## 1. 快速阅读顺序

第一次了解项目，按这个顺序读：

1. [PRD](PRD.md)
2. [信息架构与页面原型](信息架构-页面原型.md)
3. [技术架构](architecture/技术架构.md)
4. [AI 工作流](architecture/AI工作流.md)
5. [开发路线图](planning/开发路线图.md)

准备开发时，按这个顺序读：

1. [技术架构](architecture/技术架构.md)
2. [数据模型](architecture/数据模型.md)
3. [API 设计](api/API设计.md)
4. [测试验收计划](testing/测试验收计划.md)
5. [工程初始化方案](planning/工程初始化方案.md)

准备审计或验收预检时，按这个顺序读：

1. [PRD](PRD.md)
2. [当前工程状态](planning/当前工程状态.md)
3. [测试验收计划](testing/测试验收计划.md)
4. [审计报告索引](audit/INDEX.md)
5. [全局审计模板](audit/TEMPLATE-GLOBAL-AUDIT.md)

## 2. 产品文档

| 文档 | 用途 | 状态 |
|---|---|---|
| [PRD](PRD.md) | 产品定位、目标用户、MVP 范围、功能需求和验收标准 | draft |
| [信息架构与页面原型](信息架构-页面原型.md) | 页面结构、对象、流程和状态设计 | draft |
| [交互规范](信息架构-交互规范.md) | 布局、组件、状态、错误和文案规范 | draft |

## 3. 架构文档

| 文档 | 用途 | 状态 |
|---|---|---|
| [技术架构](architecture/技术架构.md) | 系统分层、技术栈、模块职责、数据流和安全边界 | draft |
| [数据模型](architecture/数据模型.md) | 核心实体、关系、索引和数据保留 | draft |
| [AI 工作流](architecture/AI工作流.md) | AI 阶段、组件、质量检查和成本控制 | draft |
| [Prompt 模板规范](architecture/Prompt模板规范.md) | Prompt 分类、字段、编译顺序和版本管理 | draft |
| [技术决策记录](architecture/技术决策记录.md) | 关键取舍和架构决策 | draft |
| [API 设计](api/API设计.md) | API 原则、请求响应、异步任务和状态轮询 | draft |

## 4. 计划与交付

| 文档 | 用途 | 状态 |
|---|---|---|
| [开发路线图](planning/开发路线图.md) | 阶段规划、任务拆分、里程碑和关键决策 | draft |
| [工程初始化方案](planning/工程初始化方案.md) | 目录、应用、共享包、环境变量和首轮命令 | draft |
| [当前工程状态](planning/当前工程状态.md) | 当前代码骨架、运行方式、已验证内容和下一步 | draft |
| [指标埋点](planning/指标埋点.md) | 北极星指标、漏斗、事件、质量和成本指标 | draft |
| [风险与成本](planning/风险成本.md) | 技术、产品、成本、安全和合规风险 | draft |
| [测试验收计划](testing/测试验收计划.md) | 测试类型、验收用例、异常场景和质量门槛 | draft |
| [部署运维](operations/部署运维.md) | 环境、服务、配置、部署、日志和回滚 | draft |
| [安全合规](operations/安全合规.md) | 密钥、上传、权限、数据、审计和发布检查 | draft |

## 5. 审计与自动产物

| 文档 | 用途 | 状态 |
|---|---|---|
| [审计报告索引](audit/INDEX.md) | 审计、验收预检、回归验证和重要 review 的入口 | active |
| [全局审计模板](audit/TEMPLATE-GLOBAL-AUDIT.md) | 审计报告固定结构，避免只在对话里给结论 | draft |

## 6. 参考资料

| 文档 | 用途 | 状态 |
|---|---|---|
| [参考项目迁移清单](../references/参考项目迁移清单.md) | 可复用、需重写、应丢弃和待验证内容 | draft |

## 7. 当前 MVP 决策摘要

| 决策 | 结论 |
|---|---|
| 产品形态 | <先做什么，不做什么> |
| 首版入口 | <用户从哪里开始> |
| 核心流程 | <A -> B -> C -> D> |
| 技术栈 | <前端 / 后端 / 数据 / 队列 / AI provider> |
| 任务模式 | <同步 / 异步 / 队列 / 手工> |
| 数据重点 | <必须保存和可追踪的数据> |

## 8. 自动产物规则

- `审计` / `audit` / `验收预检`：在 `docs/audit/` 生成报告，并更新 `docs/audit/INDEX.md`。
- `实现` / `修复`：更新 `state/LOG.md` 与 `state/PROGRESS.md`；若行为、架构、验证或风险变化，同步相关 docs。
- `文档同步`：更新本索引与相关目录索引，不让新增文件变成孤岛。
