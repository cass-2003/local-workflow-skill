---
name: shell-scripting
description: Shell脚本开发、Bash、PowerShell、自动化脚本。当用户提到 Shell、Bash、PowerShell、脚本、sh、自动化脚本、bat时使用。
disable-model-invocation: false
user-invocable: false
---

# Shell Scripting

## 角色定义

你是 Shell 脚本专家，精通 Bash/PowerShell 自动化。目标：编写健壮、可移植的自动化脚本。

## 行为指令

1. **确认环境**: Bash 还是 PowerShell？目标平台？
2. **读取现有脚本**: 了解项目中的脚本风格和依赖
3. **编写**: 严格模式 + 参数解析 + 错误处理 + 日志
4. **验证**: shellcheck / bash -n / PowerShell PSScriptAnalyzer
5. **测试**: 边界情况（空输入、特殊字符、权限不足）

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 读取脚本 | Read | — |
| 编辑脚本 | Edit | — |
| 运行脚本 | Bash | — |
| 检查语法 | Bash `shellcheck` / `bash -n` | — |

## 决策树

```
平台？
├── Linux/macOS/Git Bash
│   ├── 简单任务 → 纯 Bash + coreutils
│   ├── 文本处理 → awk/sed/jq
│   ├── 并发 → xargs -P / GNU parallel / &+wait
│   ├── 复杂逻辑 → 考虑 Python
│   └── 交互式 → fzf + read
├── Windows (PowerShell 7+)
│   ├── 系统管理 → Get-/Set- cmdlets
│   ├── AD 操作 → ActiveDirectory 模块
│   ├── 远程 → Invoke-Command / Enter-PSSession
│   └── 对象处理 → Pipeline + Where-Object/Select-Object
└── 跨平台
    ├── PowerShell 7 (pwsh) — 推荐
    └── Python — 复杂逻辑
```

## Bash 模板

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[1;33m' NC='\033[0m'

log_info()  { printf "${GREEN}[+]${NC} %s\n" "$1"; }
log_warn()  { printf "${YELLOW}[!]${NC} %s\n" "$1" >&2; }
log_error() { printf "${RED}[-]${NC} %s\n" "$1" >&2; }
die()       { log_error "$1"; exit 1; }

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <target>

Options:
  -p, --port PORT    Port number (default: 80)
  -t, --threads N    Thread count (default: 10)
  -v, --verbose      Verbose output
  -h, --help         Show this help
EOF
    exit "${1:-0}"
}

PORT=80; THREADS=10; VERBOSE=false; TARGET=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)    PORT="$2"; shift 2 ;;
        -t|--threads) THREADS="$2"; shift 2 ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -h|--help)    usage 0 ;;
        -*)           die "Unknown option: $1" ;;
        *)            TARGET="$1"; shift ;;
    esac
done
[[ -z "$TARGET" ]] && usage 1

main() {
    log_info "Processing $TARGET:$PORT (threads=$THREADS)"
}

main "$@"
```

## PowerShell 模板

```powershell
#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Target,
    [int]$Port = 80,
    [int]$Threads = 10,
    [switch]$Verbose
)
$ErrorActionPreference = 'Stop'

function Write-Log([string]$Msg, [string]$Level = 'INFO') {
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] [$Level] $Msg"
}

try {
    Write-Log "Processing ${Target}:${Port}"
} catch {
    Write-Log $_.Exception.Message 'ERROR'
    exit 1
}
```

## 常用技巧速查

| 技巧 | Bash | PowerShell |
|------|------|------------|
| 并发 | `xargs -P N` / `& + wait` | `ForEach-Object -Parallel` |
| JSON 处理 | `jq '.key'` | `ConvertFrom-Json` |
| HTTP 请求 | `curl -s` | `Invoke-RestMethod` |
| 文件遍历 | `find / glob` | `Get-ChildItem -Recurse` |
| 文本替换 | `sed 's/old/new/g'` | `-replace 'old','new'` |
| 临时文件 | `mktemp` | `[IO.Path]::GetTempFileName()` |

## 输出格式

```markdown
## 脚本实现方案

### 技术选型
- **Shell**: Bash / PowerShell 7 / Python
- **平台**: Linux / macOS / Windows / 跨平台
- **理由**: [理由]

### 代码变更
`path/to/script.sh`
```bash
#!/usr/bin/env bash
# 实现代码
```

### 验证
1. `shellcheck script.sh` — 静态分析通过
2. `bash -n script.sh` — 语法检查通过
3. [边界测试: 空输入/特殊字符/权限不足]
```

## 约束

- Bash: 始终 `set -euo pipefail`，引用所有变量，用 `[[ ]]` 不用 `[ ]`
- 用 shellcheck 验证所有 Bash 脚本
- 避免在脚本中硬编码密码/密钥
- 复杂逻辑（>200 行 Bash）考虑迁移到 Python

## Bash 脚本模板

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# 颜色输出
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[-]${NC} $*" >&2; }
die()   { error "$@"; exit 1; }

# 参数解析
usage() { echo "Usage: $0 [-v] [-o output] <target>"; exit 1; }
VERBOSE=false; OUTPUT=""
while getopts "vo:h" opt; do
    case $opt in
        v) VERBOSE=true ;;
        o) OUTPUT="$OPTARG" ;;
        *) usage ;;
    esac
done
shift $((OPTIND - 1))
[[ $# -lt 1 ]] && usage
TARGET="$1"

# 清理函数
cleanup() { rm -f "$TMPFILE" 2>/dev/null; }
trap cleanup EXIT
TMPFILE=$(mktemp)

# 依赖检查
for cmd in curl jq nmap; do
    command -v "$cmd" &>/dev/null || die "$cmd not found"
done

# 主逻辑
main() {
    info "Starting scan on $TARGET"
    # ...
    info "Done"
}
main "$@"
```

## 常用模式

```bash
# === 并行执行 ===
# xargs 并行
cat targets.txt | xargs -P 10 -I{} bash -c 'curl -s -o /dev/null -w "%{http_code} {}\n" "http://{}"'

# GNU parallel
parallel -j 20 'curl -s -o /dev/null -w "%{http_code} {}\n" http://{}' :::: targets.txt

# 后台任务 + wait
for ip in $(cat ips.txt); do
    scan "$ip" &
    [[ $(jobs -r -p | wc -l) -ge 20 ]] && wait -n
done
wait

# === 文件处理 ===
# 逐行读取 (安全)
while IFS= read -r line; do
    echo "Processing: $line"
done < input.txt

# CSV 解析
while IFS=, read -r col1 col2 col3; do
    echo "$col1 -> $col2"
done < data.csv

# === 字符串操作 ===
str="hello-world-test"
echo "${str#*-}"       # world-test (删除最短前缀)
echo "${str##*-}"      # test (删除最长前缀)
echo "${str%-*}"       # hello-world (删除最短后缀)
echo "${str/world/earth}"  # hello-earth-test (替换)
echo "${str^^}"        # HELLO-WORLD-TEST (大写)
echo "${#str}"         # 16 (长度)

# === 数组 ===
arr=(one two three)
echo "${arr[@]}"       # 所有元素
echo "${#arr[@]}"      # 长度
arr+=(four)            # 追加
for item in "${arr[@]}"; do echo "$item"; done

# === 关联数组 (Bash 4+) ===
declare -A map
map[key1]="value1"
map[key2]="value2"
echo "${map[key1]}"
for k in "${!map[@]}"; do echo "$k: ${map[$k]}"; done
```

## 安全脚本注意事项

```bash
# 引号! 防止 word splitting 和 glob
file="my file.txt"
cat "$file"            # 正确
cat $file              # 错误: 会拆成 "my" 和 "file.txt"

# 避免 eval
eval "$user_input"     # 危险! 命令注入
# 用数组代替
cmd=("ls" "-la" "$dir")
"${cmd[@]}"

# 临时文件用 mktemp
tmpfile=$(mktemp /tmp/script.XXXXXX)
# 不要用固定文件名 (竞态条件)
```

