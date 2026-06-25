---
name: string-encoding
description: "字符编码与 Unicode 实战。覆盖 ASCII / UTF-8 / UTF-16 / UTF-32 编码原理、code point vs grapheme cluster、字节 vs 字符 vs 字形、BOM、Unicode normalization (NFC/NFD/NFKC/NFKD)、emoji 与 ZWJ 序列、surrogate pair、字符串长度的多重含义、各语言字符串模型（JS UTF-16 / Go UTF-8 / Python 3 unicode / Rust UTF-8）、文件读写编码声明、URL / Base64 编码、HTML/XML 实体、CSV 编码地狱。当用户提到字符编码、UTF-8、UTF-16、Unicode、normalization、NFC、NFD、grapheme cluster、emoji 计数、code point、surrogate、BOM、CSV 乱码、字符串长度 时使用。"
---

# String Encoding Skill — 字符编码与 Unicode

## 何时使用

- 处理多语言文本（中文 / 日文 / 韩文 / 阿拉伯文 / emoji）
- 字符串长度计算结果"不对"（emoji 算 2、中文算 3 等）
- 跨系统传输文本出现 `?` / 乱码 / `' '`（mojibake）
- CSV / Excel 中文乱码
- URL / Base64 / HTML 编码场景
- 截断字符串导致显示半个字符

## 一、概念分层（必须先理清）

```
[ Bytes ]                     字节流（0-255 整数）
   ↑
[ Encoding ]                   UTF-8 / UTF-16 / GBK / Shift-JIS
   ↑
[ Code Points ]                Unicode 整数（U+0000 到 U+10FFFF）
   ↑
[ Grapheme Clusters ]          用户感知的"字符"（如 emoji ZWJ 组合）
   ↑
[ User-Perceived Character ]   "我看见的一个字"
```

例子：emoji 👨‍👩‍👧 (家庭)

```
Bytes (UTF-8):    11 字节  F0 9F 91 A8 E2 80 8D F0 9F 91 A9 E2 80 8D F0 9F 91 A7
Code Points:      5 个      U+1F468 U+200D U+1F469 U+200D U+1F467
                            (👨)    (ZWJ)   (👩)    (ZWJ)   (👧)
Grapheme Cluster: 1 个      👨‍👩‍👧
```

JS `'👨‍👩‍👧'.length === 8`（UTF-16 code unit 数）—— 对开发者基本无意义。**用户看到的是 1 个字符**。

## 二、UTF-8（必学）

```
U+0000-U+007F     1 字节   ASCII 兼容
U+0080-U+07FF     2 字节   110xxxxx 10xxxxxx
U+0800-U+FFFF     3 字节   1110xxxx 10xxxxxx 10xxxxxx
U+10000-U+10FFFF  4 字节   11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
```

特性：
- ✅ ASCII 兼容（旧文本不动）
- ✅ 自同步（任意字节看高位 bit 知道是首字节还是续字节）
- ✅ 无字节序问题
- ✅ 网络 / 文件存储事实标准

**永远默认 UTF-8**。其他编码仅出于历史 / 第三方系统兼容。

## 三、UTF-16（JS / Java / Windows 内部）

```
U+0000-U+FFFF       2 字节（BMP）
U+10000-U+10FFFF    4 字节（surrogate pair）
```

**Surrogate pair**：超出 BMP 的字符用两个 16-bit code unit 表示：

```
高代理：D800-DBFF
低代理：DC00-DFFF
```

emoji / 罕见汉字 / 古文字都在 BMP 外 → JS `.length` 算成 2：

```javascript
'😀'.length         // 2  (UTF-16 code units)
[...'😀'].length    // 1  (code points)
```

## 四、各语言字符串模型

| 语言 | 内部编码 | `len(s)` 含义 |
|---|---|---|
| **JS / Java / C#** | UTF-16 | code units 数（emoji 算 2） |
| **Go** | UTF-8 (`string` 是 byte 序列) | 字节数（`len("中") == 3`） |
| **Python 3** | 抽象 / 内部 PEP 393 | code points 数 |
| **Rust** | UTF-8 (`str` 是 byte) | 字节数 |
| **Swift** | UTF-8 / 抽象 | grapheme clusters 数 ✨ |
| **Ruby** | encoding-aware string | 取决于编码 |

**Swift 是唯一字符串 API 默认 grapheme**：`"👨‍👩‍👧".count == 1`。其他语言要库支持。

### 正确的"字符"计数

```javascript
// JS: code points 数
[...'👨‍👩‍👧'].length      // 5（含 ZWJ）

// Grapheme cluster 数（最贴近"用户字符"）
import GraphemeSplitter from 'grapheme-splitter'
new GraphemeSplitter().countGraphemes('👨‍👩‍👧')   // 1

// Intl.Segmenter (现代浏览器原生)
const seg = new Intl.Segmenter('en', { granularity: 'grapheme' })
[...seg.segment('👨‍👩‍👧')].length   // 1
```

```python
# Python: code points
len('👨‍👩‍👧')   # 5

# Grapheme
import grapheme
grapheme.length('👨‍👩‍👧')   # 1

# 或者 regex \X (PCRE)，需要 third-party regex 库
```

```go
// Go: 字节
len("👨‍👩‍👧")                    // 25

// Code points (rune 数)
utf8.RuneCountInString("👨‍👩‍👧")  // 5

// Grapheme：用 rivo/uniseg 库
uniseg.GraphemeClusterCount("👨‍👩‍👧")  // 1
```

## 五、Unicode Normalization（必学）

同一"字符"可能有多种 code point 表示：

```
"é"  可以是：
  Form 1: U+00E9                       (单个字符 NFC)
  Form 2: U+0065 U+0301                (e + 组合重音 NFD)
```

**Normalization 形式**：

| 形式 | 含义 | 用途 |
|---|---|---|
| **NFC** | 规范组合（合成单字符） | 存储 / 传输（最紧凑） |
| **NFD** | 规范分解（基本字符 + 组合标记） | 文本处理 / 搜索 |
| **NFKC** | 兼容组合（"½" → "1/2"） | 搜索 / 比较（数据丢失） |
| **NFKD** | 兼容分解 | 同上 |

```javascript
'café'.normalize('NFC') === 'cafe\u0301'.normalize('NFC')  // true
```

**关键场景**：
- ✅ 用户输入存数据库前 normalize 到 **NFC**
- ✅ 搜索 / 去重前 normalize 到 **NFKC**（"ｊａｐａｎ" 全角和 "japan" 视为同）
- ✅ macOS HFS+ 文件名是 **NFD**，Linux / Windows 是 **NFC** —— 跨平台同步要 normalize

## 六、BOM（Byte Order Mark）

```
UTF-8 BOM:    EF BB BF        ← 不需要但 Windows 工具常加
UTF-16 BE:    FE FF
UTF-16 LE:    FF FE
UTF-32 BE:    00 00 FE FF
UTF-32 LE:    FF FE 00 00
```

**UTF-8 不需要 BOM**（无字节序），但：
- Windows Notepad / Excel 默认加 → 给 Linux 工具读会看到诡异 `\ufeff` 在文件开头
- 处理代码：永远 `.replace(/^\ufeff/, '')` 或编码读为 `utf-8-sig`（Python）

```python
with open('file.csv', encoding='utf-8-sig') as f:   # 自动剥 BOM
    ...
```

## 七、CSV 编码地狱（Excel）

Excel 双击打开 UTF-8 CSV → 中文显示乱码。

**真相**：Excel Windows 版默认按系统 ANSI（GBK / Shift-JIS）解析，除非：
1. CSV 带 UTF-8 BOM（Excel 才识别为 UTF-8）
2. 用"导入数据"向导显式选编码

**最佳实践**：

```python
import csv
with open('out.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '年龄'])
    writer.writerow(['张三', 30])
```

`utf-8-sig` 写入时自动加 BOM。或者直接生成 `.xlsx`（openpyxl / SheetJS）—— 二进制格式无编码问题。

## 八、URL 编码（percent-encoding）

```
RFC 3986 reserved:  ! * ' ( ) ; : @ & = + $ , / ? # [ ]
                     ↑ 这些原义 char 在 URL 不同部分有特殊含义

Unreserved (永远不编码):  A-Z a-z 0-9 - _ . ~

Other → %XX (字节的 hex)
```

```javascript
encodeURI('https://example.com/路径 with space')
// "https://example.com/%E8%B7%AF%E5%BE%84%20with%20space"

encodeURIComponent('?key=值')   // 编码 ? = 等保留字符
// "%3Fkey%3D%E5%80%BC"
```

**关键差异**：
- `encodeURI` 不编码 `:` `/` `?` `#` `&` `=`（保留 URL 结构）
- `encodeURIComponent` 编码所有保留字符（用于 query 值 / path segment）
- query value 必须用 `encodeURIComponent`

## 九、Base64 / Base64URL

```
Base64 alphabet:  A-Z a-z 0-9 + / =        (= 填充)
Base64URL:        A-Z a-z 0-9 - _          (- _ 替代 + /，无 =)
```

Base64URL 用于 JWT / OAuth state / cookie 值（URL safe）。

```javascript
// Browser
btoa('Hello, 世界')   // 💥 binary string 限制，中文报错
// 正确：
function utf8Base64(s) {
  return btoa(unescape(encodeURIComponent(s)))   // 旧 hack
}
// 或者 TextEncoder
btoa(String.fromCharCode(...new TextEncoder().encode('Hello, 世界')))

// Node
Buffer.from('Hello, 世界').toString('base64')
Buffer.from('Hello, 世界').toString('base64url')   // Node 16+
```

## 十、HTML / XML 实体

```html
<p>5 &gt; 3 &amp;&amp; "quoted"</p>
```

| 字符 | 实体 |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&#39;` (HTML4 没 `&apos;`) |
| 任意 Unicode | `&#NNNN;` (十进制) / `&#xHHHH;` (十六进制) |

**XSS 防护**：永远不要拼字符串到 HTML — 用模板引擎自动转义 / `textContent` 而非 `innerHTML`。

## 十一、字符串截断陷阱

```javascript
// ❌ 按 length 截断 emoji
'你好👋'.slice(0, 3)      // "你好\uD83D" ← 半个 surrogate
console.log('你好👋'.slice(0, 3).length)  // 3 但显示乱

// ✅ 按 grapheme
import GraphemeSplitter from 'grapheme-splitter'
const splitter = new GraphemeSplitter()
splitter.splitGraphemes('你好👋').slice(0, 2).join('')  // "你好"

// ✅ 按 code points
[...'你好👋'].slice(0, 2).join('')   // "你好"
```

```sql
-- MySQL: utf8 是 假 utf8（最多 3 字节，不支持 emoji）
-- 必须用 utf8mb4
ALTER TABLE x CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 十二、文件读写编码声明

```python
# ❌ 隐式默认编码（依赖 OS locale）
open('file.txt').read()

# ✅ 显式
open('file.txt', encoding='utf-8').read()
```

```go
// Go 文件 IO 默认字节流，自己 decode
data, _ := os.ReadFile("file.txt")
text := string(data)   // Go string 是 UTF-8 字节

// 其他编码用 golang.org/x/text/encoding
```

```javascript
// Node
import { readFile } from 'node:fs/promises'
const text = await readFile('file.txt', 'utf-8')   // 显式

// 默认是 Buffer，没指定 encoding 会得到 binary buffer
```

## 十三、Don'ts

- ❌ 假设字符串长度 = 字符数（emoji / 中文 / 组合字符崩）
- ❌ MySQL 用 `utf8` 字符集（升 `utf8mb4`）
- ❌ 写 CSV 不加 BOM 给 Excel（中文乱码）
- ❌ slice / substring 字符串不考虑 surrogate / grapheme（半字符）
- ❌ 比较字符串前不 normalize（"café" 可能匹配失败）
- ❌ `JSON.parse` 后忘了源字节编码 — JSON 必须 UTF-8（RFC 8259）
- ❌ URL 拼接不用 `encodeURIComponent` — 注入风险
- ❌ HTML 拼接不转义 — XSS
- ❌ 文件读取不指定 encoding — 跨平台不一致
- ❌ Base64 处理 binary 串忽视 UTF-8（btoa 中文崩）
- ❌ 用 `\w+` 正则匹配中文 — `\w` 默认仅 ASCII（用 `\p{L}` + `u` 标志）
- ❌ 数据库 charset 与 connection charset 不一致（写入正常，读取乱码）

## 十四、调试技巧

```bash
# 看文件实际字节
xxd file.txt | head
hexdump -C file.txt | head

# 检测编码
file -i file.txt        # 输出 charset
chardet file.txt        # python 包，更准

# 转换编码
iconv -f gbk -t utf-8 in.txt > out.txt
iconv -f utf-16le -t utf-8 in.txt > out.txt
```

```javascript
// JS 调试
console.log([...'你好👋'].map(c => c.codePointAt(0).toString(16)))
// ["4f60", "597d", "1f44b"]

// 检测 BOM
str.charCodeAt(0) === 0xFEFF   // true → 有 BOM
```

```python
# Python 调试
for c in '你好👋':
    print(f"{c} U+{ord(c):04X}")
```

## 十五、参考资料

- "The Absolute Minimum Every Software Developer Must Know About Unicode"（Joel Spolsky）
- Unicode Consortium FAQ：https://www.unicode.org/faq/
- UTF-8 RFC 3629：https://datatracker.ietf.org/doc/html/rfc3629
- UAX #29 Grapheme Cluster Boundaries：https://unicode.org/reports/tr29/
- UAX #15 Normalization Forms：https://unicode.org/reports/tr15/
- ICU Project：https://icu.unicode.org/
- "Falsehoods Programmers Believe About Strings"：https://kunststube.net/encoding/
- emojipedia.org（看 emoji code point 组成）
- Intl.Segmenter（现代浏览器原生 grapheme）：https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter
