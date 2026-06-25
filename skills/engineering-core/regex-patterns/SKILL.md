---
name: regex-patterns
description: "正则表达式实战。覆盖语法速查、分组与捕获、lookahead/lookbehind 零宽断言、反向引用、Unicode 模式（\\p{}）、贪婪/惰性/独占量词、catastrophic backtracking 性能陷阱、各语言 flavor 差异（PCRE/POSIX/JS/Python/Go RE2）、调试与可视化。当用户提到正则、regex、regexp、PCRE、lookahead、lookbehind、catastrophic backtracking、Unicode regex、命名分组、捕获组时使用。"
---

# Regex Patterns Skill — 正则实战

## 何时使用

- 写或调试正则
- 性能问题：CPU 跑满 / ReDoS 攻击
- 跨语言移植正则（JS → Python → Go）发现行为不一致
- 处理 Unicode 文本（中日韩 / emoji / 组合字符）
- 评审用户输入校验是否安全（catastrophic backtracking）

## 一、语法速查

### 字符类

| 符号 | 含义 |
|---|---|
| `.` | 任意字符（默认不含 `\n`，加 `s` 标志含） |
| `\d` `\D` | 数字 / 非数字 |
| `\w` `\W` | 单词字符（字母数字下划线）/ 非 |
| `\s` `\S` | 空白 / 非空白 |
| `[abc]` `[^abc]` | 集合 / 反集合 |
| `[a-z]` | 范围 |
| `\b` `\B` | 单词边界 / 非边界 |
| `\p{L}` `\p{N}` `\p{Han}` | Unicode 类别（**必须 `u` 标志**） |

### 量词

| 符号 | 含义 |
|---|---|
| `*` | 0+ |
| `+` | 1+ |
| `?` | 0 或 1 |
| `{n}` | 恰好 n |
| `{n,}` | 至少 n |
| `{n,m}` | n 到 m |
| **后接 `?`** | 惰性（最少匹配）：`.*?` |
| **后接 `+`** | 独占（不回溯，PCRE/Java/Ruby 支持，JS 不支持）：`.*+` |

### 锚点 / 边界

| 符号 | 含义 |
|---|---|
| `^` | 行首（`m` 标志下每行；否则字符串首） |
| `$` | 行尾 |
| `\A` `\z` | 字符串开始 / 结束（不受 `m` 影响，JS 不支持） |
| `\b` | 单词边界 |

### 分组

```
(abc)          捕获组 #1
(?:abc)        非捕获组（性能更好）
(?<name>abc)   命名捕获组
\1             反向引用第 1 组
\k<name>       反向引用命名组
```

### 标志（flag）

| 标志 | 含义 |
|---|---|
| `i` | 大小写不敏感 |
| `g` | 全局（JS / 部分语言）|
| `m` | 多行（影响 `^` `$`） |
| `s` | 单行（让 `.` 匹配 `\n`） |
| `u` | Unicode（启用 `\p{}`、4 字节 emoji 等） |
| `x` | 扩展（忽略空白和注释，便于多行写） |
| `y` | sticky（JS）— 从 lastIndex 严格匹配 |

## 二、Lookaround（零宽断言）

不消耗字符，仅断言位置。

| 语法 | 含义 |
|---|---|
| `(?=...)` | 后面是 ... |
| `(?!...)` | 后面不是 ... |
| `(?<=...)` | 前面是 ... |
| `(?<!...)` | 前面不是 ... |

**例子**：

```regex
# 提取价格数字（前面有 $ 符）
(?<=\$)\d+(?:\.\d+)?

# 密码至少有 1 大写 + 1 数字 + 长度 8+
^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$

# 不是 .png 结尾的文件
^.+(?<!\.png)$
```

JavaScript / Python / .NET / PCRE / Java 都支持 lookaround。Go 的 RE2 **不支持**。

## 三、Unicode 模式（`u` 标志）

```regex
# 不加 u：只能匹配 ASCII
/\w+/.test('café')           // true，但只匹配 'caf'，'é' 不算
/^.$/u.test('🎉')            // true（u 标志下识别为单字符）

# 类别匹配
/\p{Letter}+/u               // 任何语言字母（拉丁/中文/阿拉伯/...）
/\p{Han}+/u                  // 中文汉字
/\p{Emoji}/u                 // emoji
/\p{Script=Hiragana}/u       // 平假名
/\p{Script=Katakana}/u       // 片假名
/\p{Script=Hangul}/u         // 韩文

# 现代 emoji（含 ZWJ 序列、肤色变体）
/\p{RGI_Emoji}/v             // v 标志（更新的 Unicode 引擎，2023+）
```

**注意**：处理用户输入文本（中日韩 / emoji），**永远加 `u` 或 `v` 标志**，否则 4 字节字符被拆成两半判断。

## 四、Catastrophic Backtracking（致命陷阱）

```regex
^(a+)+$
```

输入 `"aaaaaaaaaaaaaaaaaaab"` —— 会**爆炸式回溯**，CPU 跑满几秒甚至几分钟。这就是 **ReDoS**（Regex DoS）攻击源。

**根因**：嵌套量词 `(a+)+` 让引擎尝试无数种切分方式。

**易出问题的模式**：

```regex
(a+)+              # 嵌套
(a*)*
(a|a)*
(a|aa)*
(a|b|ab)*
```

**修复**：

```regex
# 1. 用独占量词（不回溯，PCRE 支持，JS 不支持）
^(?>a+)+$
^a++$

# 2. 简化逻辑
^a+$               # 同等效果，无回溯

# 3. 避免重叠选项
(a|b)*             # OK
(a|ab)*            # 危险 — 'a' 也是 'ab' 的前缀
```

**安全工具**：
- safe-regex npm 包检测危险模式
- regex101.com 调试时显示步数

## 五、命名捕获组（强烈推荐）

```javascript
const re = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/
const m = '2026-05-06'.match(re)
m.groups.year   // '2026'
m.groups.month  // '05'
m.groups.day    // '06'
```

比 `m[1]` `m[2]` `m[3]` 可读性强一万倍。**所有现代正则都用命名组**。

替换时引用：

```javascript
'2026-05-06'.replace(re, '$<day>/$<month>/$<year>')
// '06/05/2026'
```

## 六、各语言 flavor 差异（坑）

| 特性 | JS | Python | Go (RE2) | PCRE (PHP/Perl) |
|---|---|---|---|---|
| Lookahead `(?=)` | ✅ | ✅ | ❌ | ✅ |
| Lookbehind `(?<=)` | ✅ (ES2018) | ✅ | ❌ | ✅ |
| 反向引用 `\1` | ✅ | ✅ | ❌ | ✅ |
| 命名组 `(?<name>)` | ✅ | ✅ Python 3.6+ | ✅ `(?P<name>)` 语法 | ✅ |
| `\p{Han}` Unicode | ✅ (`u` 标志) | ✅ `regex` 库 | ❌ | ✅ |
| 独占量词 `++` `*+` | ❌ | ❌ | ❌ | ✅ |
| 性能保证 | 引擎差 | 引擎差 | ✅ 线性时间 | 引擎差 |

**Go RE2 不支持 lookaround / 反向引用** —— 但保证线性时间（无 ReDoS 风险）。如果业务需要 lookaround，要么换库（regexp2），要么改算法。

## 七、常用模式集

```regex
# Email（实用版，不严格 RFC 5322）
^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$

# URL（http/https）
^https?:\/\/[^\s/$.?#].[^\s]*$

# IPv4
^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$

# 国际手机号（粗略）
^\+?[1-9]\d{1,14}$

# UUID v4
^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$

# ISO 8601 日期
^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$

# CSS 颜色（hex 3/6/8 位）
^#(?:[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$

# 中文（仅汉字）
^\p{Han}+$       # 需 u 标志

# 美国 SSN 格式
^\d{3}-\d{2}-\d{4}$

# 强密码（8+ 含大写、小写、数字、特殊符号）
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$

# 提取 Markdown 链接
\[([^\]]+)\]\(([^)]+)\)

# 提取 HTML 标签内容（粗略，不处理嵌套）
<(\w+)[^>]*>(.*?)<\/\1>
```

## 八、性能建议

1. **预编译**：循环外编译，循环内复用
   ```javascript
   const re = /\d+/g                  // ✅ 一次
   for (const s of items) s.match(re)
   ```
2. **优先字符串方法**：简单的用 `indexOf` / `startsWith` / `includes` 比 regex 快几倍
3. **避免 `.*` 贪婪**：能精确就精确，`[^"]*` 比 `.*` 在 `"..."` 匹配中快很多
4. **用非捕获组 `(?:...)`** 替代 `(...)` —— 不需要捕获时省内存
5. **锚定 `^...$`** 减少引擎尝试位置
6. **避免嵌套量词**：见上节
7. **大数据流式处理**：用 `match-all` / `findAllString` 迭代而非 `match` 全量

## 九、调试技巧

1. **regex101.com**：可视化、解释、显示回溯步数、各语言 flavor 切换
2. **regexr.com**：实时高亮 + cheatsheet
3. **debuggex.com**：状态机可视化
4. **打印中间结果**：

```javascript
const m = str.matchAll(/(\d{4})-(\d{2})-(\d{2})/g)
console.log([...m].map(x => x.groups))
```

5. **拆分多行 + `x` 标志**（Python / PCRE 支持）：

```python
re.compile(r"""
    (?<year>\d{4})    # 4 位年
    -
    (?<month>\d{2})   # 2 位月
    -
    (?<day>\d{2})     # 2 位日
""", re.VERBOSE)
```

## 十、Don'ts

- ❌ 用正则解析 HTML / JSON / SQL — 用专门 parser
- ❌ 邮箱用 RFC 5322 完整正则（一千多字符）— 实用版 + 发邮件验证
- ❌ 嵌套量词 `(.+)+` — ReDoS
- ❌ 用户输入直接当 regex pattern — 转义或拒绝（npm `escape-string-regexp`）
- ❌ 不加 `u` 处理多语言 / emoji
- ❌ Go 项目想用 lookaround — RE2 不支持
- ❌ `[a-zA-Z0-9_]` — 用 `\w`
- ❌ `[ \t\r\n]` — 用 `\s`
- ❌ 同一个正则重复编译 — 提到模块顶层
- ❌ 用 regex 做安全过滤（XSS/SQLi）— 用专门库

## 十一、参考资料

- regex101.com（必备调试器）
- MDN Regular Expressions：https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions
- Mastering Regular Expressions（书 / Jeffrey Friedl）
- Russ Cox 的正则匹配文章（讲 RE2 为何线性）：https://swtch.com/~rsc/regexp/
- safe-regex（ReDoS 检测）：https://www.npmjs.com/package/safe-regex
- Unicode Property Escapes：https://262.ecma-international.org/#sec-runtime-semantics-unicodematchproperty-p
