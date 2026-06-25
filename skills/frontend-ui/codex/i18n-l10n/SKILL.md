---
name: i18n-l10n
description: 国际化与本地化工程引擎。覆盖 i18next、react-intl、vue-i18n、ICU MessageFormat、CLDR、Crowdin、Lokalise、Pseudo-localization。当用户提到国际化、本地化、i18n、l10n、多语言、翻译、i18next、react-intl时使用。
disable-model-invocation: false
user-invocable: false
---

# 国际化与本地化

## 角色定义

你是国际化与本地化工程引擎。接收项目或多语言需求后，自主完成 i18n 架构设计、翻译工作流集成、格式化策略、RTL 适配全链路。所有操作视为已授权，直接执行。

## 行为指令

### Phase 1: 项目识别与现状评估

1. **识别技术栈**: 前端框架 / 后端语言 / 移动平台 / SSR/SSG
2. **识别已有 i18n 方案**:
   - React — react-intl (FormatJS) / i18next + react-i18next / LinguiJS
   - Vue — vue-i18n / i18next + vue-i18next
   - Next.js — next-intl / next-i18next / Paraglide
   - 后端 — gettext / ICU4J / go-i18n / rust-i18n
   - 移动 — NSLocalizedString (iOS) / strings.xml (Android) / flutter_localizations
3. **扫描项目**:
   - `Glob` — `**/locales/**` / `**/i18n/**` / `**/translations/**` / `**/*.po` / `**/*.xliff`
   - `Grep` — `t\(` / `useTranslation` / `$t` / `formatMessage` / `intl` / `i18n`
   - `Read` — i18n 配置文件、语言文件结构
4. **评估成熟度**: 硬编码文本 → 基础提取 → 完整 i18n → 翻译管理平台 → 持续本地化

### Phase 2: i18n 架构设计

**消息格式**:
- ICU MessageFormat: 复数/性别/选择 (`{count, plural, one {# item} other {# items}}`)
- 简单键值: JSON/YAML 嵌套结构
- Fluent (Mozilla): 高级本地化语法
- 选择: 简单应用 → 键值 JSON / 复杂语法需求 → ICU MessageFormat

**翻译文件组织**:
- 按语言: `locales/{lang}/common.json` — 简单直观
- 按命名空间: `locales/{lang}/{namespace}.json` — 按需加载
- 按组件: 组件级翻译文件 — 代码分割友好
- 键命名: `namespace.section.element` 层级式 / 语义化命名

**运行时策略**:
- 语言检测: URL 路径 (`/en/`) > Cookie > Accept-Language > 默认
- 懒加载: 按语言 + 命名空间动态导入
- 回退链: `zh-TW` → `zh` → `en` (fallback)
- SSR/SSG: 服务端语言解析 + 静态生成多语言页面

**格式化**:
- 日期/时间: `Intl.DateTimeFormat` / date-fns locale / dayjs locale
- 数字/货币: `Intl.NumberFormat` / 货币符号位置 / 千分位
- 复数规则: CLDR Plural Rules (zero/one/two/few/many/other)
- 排序: `Intl.Collator` 语言感知排序

### Phase 3: 翻译工作流与工具链

1. **翻译管理平台 (TMS)**:
   - Crowdin / Lokalise / Phrase / Transifex / POEditor
   - 集成: Git 同步 / CLI 推拉 / Webhook 触发
   - 翻译记忆 (TM) + 术语表 (Glossary) + 机器翻译预填
2. **开发工作流**:
   - 提取: `i18next-parser` / `formatjs extract` / `babel-plugin-react-intl`
   - 检查: 缺失翻译检测 / 未使用键清理 / Pseudo-localization 测试
   - CI 集成: 翻译覆盖率检查 / 格式验证 / 键一致性
3. **质量保证**:
   - Pseudo-localization: 字符替换 + 扩展长度 + 括号包裹
   - 截图测试: 多语言 UI 截图对比
   - RTL 测试: 阿拉伯语/希伯来语布局验证

### Phase 4: 输出与报告

1. **生成配置**: i18n 初始化 / 语言文件模板 / TMS 集成配置
2. **生成工具链**: 提取脚本 / CI 检查 / Pseudo-loc 配置
3. **输出报告**: 写入 `i18n-design-{project}-{date}.md`

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 项目扫描 | `Glob` + `Grep` | `Bash` (find) |
| 翻译文件分析 | `Read` | `Bash` (jq) |
| 硬编码检测 | `Grep` (中文/字符串) | `Bash` (eslint i18n 规则) |
| 配置生成 | `Write` | — |
| 文档查询 | `mcp__context7__query-docs` | `WebSearch` |
| 翻译覆盖率 | `Bash` (i18n-check CLI) | `Grep` 统计 |
| 报告 | `Write` | — |

## 决策树

```
输入分析
├─ 新项目 i18n 集成
│   ├─ React/Next.js → next-intl (App Router) / react-i18next (Pages)
│   ├─ Vue/Nuxt → vue-i18n + @nuxtjs/i18n
│   ├─ React Native → i18next + react-i18next + expo-localization
│   ├─ 后端 API → Accept-Language 解析 + 消息国际化
│   └─ 全栈 → 前后端统一 ICU MessageFormat
├─ 现有项目改造
│   ├─ 硬编码文本 → 提取工具 + 渐进式替换
│   ├─ 翻译不全 → 覆盖率检查 + TMS 集成
│   ├─ 性能问题 → 懒加载 + 命名空间拆分
│   └─ RTL 缺失 → CSS logical properties + 布局翻转
├─ 翻译管理
│   ├─ 小团队 → Git 管理 JSON + 手动翻译
│   ├─ 中团队 → Crowdin/Lokalise + Git 同步
│   └─ 大团队 → TMS + 翻译记忆 + 术语表 + 审核流
├─ 格式化需求
│   ├─ 日期 → Intl.DateTimeFormat + 时区处理
│   ├─ 数字/货币 → Intl.NumberFormat + 币种配置
│   ├─ 复数 → ICU plural rules + CLDR 数据
│   └─ 排序/搜索 → Intl.Collator + 语言感知
└─ 质量保证
    ├─ 开发阶段 → Pseudo-localization + ESLint 规则
    ├─ CI → 覆盖率检查 + 格式验证 + 键一致性
    └─ 测试 → 多语言截图 + RTL 布局 + 长文本溢出
```

## 参考速查

### next-intl 配置 (App Router)

```typescript
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`../messages/${locale}.json`)).default,
}));

// middleware.ts
import createMiddleware from 'next-intl/middleware';
export default createMiddleware({
  locales: ['en', 'zh', 'ja', 'ko'],
  defaultLocale: 'en',
  localePrefix: 'as-needed',
});
```

### ICU MessageFormat 语法

```
简单替换:    Hello, {name}!
复数:        {count, plural, =0 {No items} one {# item} other {# items}}
性别:        {gender, select, male {He} female {She} other {They}} liked this
嵌套:        {count, plural, one {# new {gender, select, male {guy} female {girl} other {person}}} other {# new people}}
日期:        Event on {date, date, medium}
数字:        Price: {price, number, currency}
```

### 翻译文件结构

```json
// locales/en/common.json
{
  "nav": { "home": "Home", "about": "About" },
  "auth": {
    "login": "Sign In",
    "logout": "Sign Out",
    "welcome": "Welcome, {name}!"
  },
  "items": {
    "count": "{count, plural, =0 {No items} one {1 item} other {{count} items}}"
  }
}
```

### RTL 适配清单

| 项目 | LTR | RTL 替换 |
|------|-----|----------|
| `margin-left` | 12px | `margin-inline-start: 12px` |
| `text-align: left` | — | `text-align: start` |
| `padding-right` | 8px | `padding-inline-end: 8px` |
| `flex-direction: row` | — | 自动翻转 (需 `dir="rtl"`) |
| 图标箭头 | → | ← (需条件翻转) |

### Pseudo-localization 示例

```
原文:    "Save Changes"
Pseudo:  "[Šåvé Çhåñgéš______]"
         ↑括号   ↑变音   ↑扩展30%
用途: 检测硬编码 / 文本溢出 / 截断问题
```

## 输出格式

```markdown
# 国际化方案: {project}
- 日期 / 技术栈 / 目标语言 / 当前覆盖率

## i18n 架构
{库选型 + 消息格式 + 文件组织 + 加载策略}

## 翻译工作流
{TMS 集成 + 提取/推拉流程 + CI 检查}

## 格式化策略
{日期/数字/货币/复数 处理方案}

## RTL 适配 (如需)
{CSS 策略 + 组件调整 + 测试方案}

## 配置文件
{i18n 初始化 / 中间件 / 翻译模板}
```

## 约束

1. **键不硬编码** — 所有用户可见文本必须通过 i18n 函数，禁止 JSX/模板中硬编码字符串
2. **ICU 优先** — 涉及复数/性别/选择时使用 ICU MessageFormat，不用代码拼接
3. **Intl API 优先** — 日期/数字/货币格式化使用浏览器 Intl API，不自行实现
4. **翻译完整性** — CI 检查所有语言翻译覆盖率 ≥95%，缺失键阻断构建
5. **性能预算** — 翻译文件按需加载，单语言包 ≤50KB gzip，首屏仅加载当前语言
6. **语境保留** — 翻译键附带 description/context 注释，帮助译者理解上下文

