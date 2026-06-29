---
name: fuzzing-reverse-engineering
description: Fuzzing 工程实战 + 逆向联动。AFL++ / honggfuzz / libFuzzer / fuzzilli / syzkaller / WinAFL / Jackalope / TrapFuzz / AFLNet / boofuzz；coverage-guided / grammar / structure-aware / differential / generation 模式；编译插桩 + 闭源 QEMU/TinyInst 黑盒；corpus / harness / minimize；KASAN/KMSAN/MSAN 联动；浏览器 / 协议 / 内核专项 fuzz；OSS-Fuzz / ClusterFuzz / FuzzBench 流水线。
---

# Fuzzing 与逆向联动

## 适用场景

- 拿到目标二进制 / 源码，想自动找崩溃 / 漏洞 / 异常分支。
- 已有崩溃想用 fuzzer 缩小输入、扩大覆盖。
- 闭源 SDK / 协议 / 内核 / 浏览器 / JIT / 解析器 系统化挖洞。
- 把 fuzz 集成到 CI/CD：每次构建自动跑 N 小时 → 自动 triage → 发 issue。
- Differential fuzz 找两个实现的语义差异（OpenSSL vs WolfSSL / V8 vs SpiderMonkey）。

## 不适用

- 单个 crash 的可利用性分析 → `crashrev`。
- 函数级静态逆向 → `binrev`。
- 协议字段位级还原 → `protrev`。
- IR / 数据流深挖找 sink → `irrev`。

## Fuzzer 选型

| 模式 | 代表 | 输入观察 | 适合 |
| --- | --- | --- | --- |
| **Coverage-guided (有源码)** | AFL++ / libFuzzer / honggfuzz | edge / block 计数 | C/C++/Rust/Go 解析器 |
| **Coverage-guided (闭源)** | AFL++ QEMU 模式 / WinAFL / TinyInst / Jackalope / frida-fuzzer | 动态插桩 + bb hash | 闭源二进制、商业软件 |
| **Grammar-aware** | nautilus / grammarinator / Domato / Dharma | 文法树变异 | JS / SQL / 高度结构化输入 |
| **Structure-aware** | libFuzzer + FuzzedDataProvider / libprotobuf-mutator / custom mutator | 自定义结构 | protobuf / 自家二进制格式 |
| **Differential** | DiFuzzer / cross-language oracle | 输入相同 → 输出比对 | TLS / crypto / 解析器对照 |
| **Generation-based** | Peach / boofuzz / Mutiny / sulley | 文法 + state-aware | 网络协议 |
| **Snapshot / Replayable** | LibAFL / Nyx / KAFL | full-system snapshot | 内核 / driver / firmware |
| **Concolic / Hybrid** | QSYM / SymCC / Driller (angr + AFL) | path-sat solver + coverage | 长 magic / 复杂校验 |
| **Kernel** | syzkaller / KAFL / kAFL+Nyx | KASAN/KMSAN + KCOV | Linux / Windows / macOS 内核 |
| **JS / Browser** | Fuzzilli / Domato / Jackalope | IR-based / DOM | V8 / SpiderMonkey / JSC / Chakra |
| **Protocol** | boofuzz / AFLNet / sulley / Mutiny / fuzzowski | network state machine | HTTP/SMB/SMTP/RTSP/SIP |
| **Smart Contract** | Echidna / Foundry forge / Medusa | EVM symbolic + property | Solidity / Vyper |

## AFL++ 全流程（首推）

```bash
# 装
apt install afl++
# 或源码:
git clone https://github.com/AFLplusplus/AFLplusplus && cd AFLplusplus
make distrib && sudo make install                            # 全套 (gcc/clang/lto/qemu/unicorn/...)

# 1) 准备目标：有源码 → 用 afl-clang-fast (推荐 LTO 模式)
export AFL_USE_ASAN=1                                       # 同时开 sanitizer 找内存错误
export AFL_USE_UBSAN=1
export AFL_HARDEN=1
CC=afl-clang-fast++ AFL_LLVM_LTO=1 make
# 或 LTO 模式（覆盖最全）
CC=afl-clang-lto AFL_LLVM_LTO_AUTODICTIONARY=1 make

# 2) 准备 corpus（极重要）
mkdir corpus_in
cp samples/*.jpg corpus_in/
afl-cmin -i corpus_in -o corpus_min -- ./target @@           # 去重 / 最小集
ls corpus_min | wc -l                                        # 通常 < 200 个最优

# 3) 跑 fuzz（多线程是关键）
afl-fuzz -i corpus_min -o sync_dir -M main -- ./target @@   # 主 fuzzer
afl-fuzz -i corpus_min -o sync_dir -S sub1 -- ./target @@   # 副 fuzzer 1
afl-fuzz -i corpus_min -o sync_dir -S sub2 -- ./target @@
# CPU 核数 → 起对应多少进程，性能线性扩展

# 同时配多种策略（AFL++ 强项）
afl-fuzz -i corpus_min -o sync -S sub_explore -p explore -- ./target @@   # 探索模式
afl-fuzz -i corpus_min -o sync -S sub_fast -p fast -- ./target @@         # 快变异
afl-fuzz -i corpus_min -o sync -S sub_coe -p coe -- ./target @@           # cyclic
afl-fuzz -i corpus_min -o sync -S sub_mmopt -p mmopt -- ./target @@       # 老 corpus 偏好

# 4) 状态监控
watch -n5 'afl-whatsup sync_dir'                             # 全 fuzzer 统计
afl-plot sync_dir/main /tmp/plot_out                         # 出趋势图
# UI 中关键指标:
#   total paths, unique crashes, unique hangs, last new path/crash time, exec/sec

# 5) crash 处理
ls sync_dir/main/crashes/
afl-tmin -i sync_dir/main/crashes/id:000123 -o min.bin -- ./target @@   # 最小化
casr -t crashes/ -o casr_out -- ./target @@                  # 自动 triage (russian crash analysis)
afl-collect -d crashes -e ./target @@ -t triage_out          # 含 valgrind triage
```

### AFL++ 闭源黑盒（QEMU / Unicorn / FRIDA）

```bash
# QEMU 用户模式 (Linux x86/x86_64/ARM/AARCH64/MIPS)
afl-fuzz -i corpus_in -o sync -Q -- ./closed_binary @@
# 比有源码慢 5-10 倍但能跑任何 ELF

# QEMU + persistent 模式（更快）
# 在源码 LD_PRELOAD 一个 harness 注入 __AFL_LOOP

# Frida 模式（macOS/iOS/Android/Win 部分）
afl-fuzz -i in -o out -O -- ./binary @@                     # FRIDA persistent
# 配套环境变量
export AFL_FRIDA_PERSISTENT_ADDR=0x100002345
export AFL_FRIDA_PERSISTENT_HOOK=./hook.so

# Unicorn 模式（适合 embedded 固件、bootloader 片段）
# 自家 harness 把目标函数加载到 unicorn → 注入输入 → 执行 → 报覆盖

# Windows 闭源
WinAFL (afl 移植 + DynamoRIO 插桩)
  afl-fuzz.exe -i in -o out -D <DynamoRIO\bin64> \
      -t 5000 -- -coverage_module target.dll -fuzz_iterations 1000 \
      -target_module target.exe -target_method fuzzme -- target.exe @@

Jackalope (Google 出品，TinyInst 引擎，macOS+Win)
  jackalope.exe -i in -o out -t 5000 -instrument_module target.dll \
      -- target.exe @@
```

### AFL++ 高级特性

```bash
# 自动字典提取（LTO 模式自带）
afl-fuzz ... -x dict.txt                                     # 手动加字典
# AFL++ 还能从 strings 自动提

# 自定义 mutator（结构感知）
AFL_CUSTOM_MUTATOR_LIBRARY=./mutator.so afl-fuzz ...
# mutator 例子：libprotobuf-mutator / nautilus grammar / FuzzGen output

# corpus shuffle / 重要性采样
afl-cmin / afl-cmin.bash / afl-showmap

# 后处理: 算 coverage
afl-cov -d sync -e "make -C target clean coverage-build" \
        -c "./target AFL_FILE" --enable-branch-coverage

# CMin + CMplog (二进制感知)
afl-cmin -i in -o out_min -- ./target @@
afl-fuzz -i out_min -o sync -c ./target_cmplog -- ./target @@   # CMP 比较插桩

# Persistent mode (10-100 倍快)
// 在源码中插入:
#include <unistd.h>
__AFL_FUZZ_INIT();
int main() {
    __AFL_INIT();
    char *buf = __AFL_FUZZ_TESTCASE_BUF;
    while (__AFL_LOOP(10000)) {
        int len = __AFL_FUZZ_TESTCASE_LEN;
        process(buf, len);
    }
}
```

## libFuzzer (in-process)

```c
// fuzz_target.cc
#include <cstdint>
#include <cstddef>
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;
    parse(data, size);                                       // 待测函数
    return 0;
}
```

```bash
# 编译
clang++ -g -O1 -fsanitize=fuzzer,address -fno-omit-frame-pointer \
        fuzz_target.cc target.cc -o fuzz_target

# 跑
./fuzz_target -max_total_time=3600 -workers=8 -jobs=8 corpus/

# 关键选项
-print_corpus_stats=1           显示 corpus 统计
-max_len=8192                   单个输入最大长度
-dict=/path/to/dict.txt         字典
-only_ascii=1                   只用 ASCII 字符
-fork=8                         多进程
-rss_limit_mb=2048              内存上限
-malloc_limit_mb=1024
-timeout=10                     单 case 超时秒
-merge=1 new_corpus/ old_corpus/   merge 模式（去冗余）
-minimize_crash=1 crash_input   crash 最小化

# Structure-aware: FuzzedDataProvider
#include <fuzzer/FuzzedDataProvider.h>
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fdp(data, size);
    int x = fdp.ConsumeIntegralInRange<int>(0, 100);
    std::string s = fdp.ConsumeRandomLengthString();
    test(x, s);
    return 0;
}

# libprotobuf-mutator
#include "src/libfuzzer/libfuzzer_macro.h"
DEFINE_PROTO_FUZZER(const MyProto& m) { handle(m); }
```

## honggfuzz

```bash
# 装 + 编译
make
honggfuzz -i in_corpus -W workspace -- ./target ___FILE___

# 多输入路径
honggfuzz -i in -- ./target @@                              # @@ 替换为文件路径
honggfuzz -i in --persistent -- ./target                    # in-process LLVMFuzzerTestOneInput-style

# 网络 fuzz
honggfuzz -i in --socket_fuzzer -- ./server                 # 注入到 socket recv

# Sanitizer 自动联动
honggfuzz -i in --sanitizers -- ./target

# 自定义指令时间预算
honggfuzz -i in -t 10 -n 4 -- ./target
```

## syzkaller（Linux 内核 fuzz 头号）

```bash
# 安装
go install github.com/google/syzkaller/...@latest

# 准备配置
cat > my.cfg <<'EOF'
{
  "target": "linux/amd64",
  "http": "127.0.0.1:56741",
  "workdir": "/syzkaller/workdir",
  "kernel_obj": "/linux/",
  "image": "/syzkaller/wheezy.img",
  "sshkey": "/syzkaller/wheezy.id_rsa",
  "syzkaller": "/go/src/github.com/google/syzkaller",
  "procs": 8,
  "type": "qemu",
  "vm": { "count": 4, "kernel": "/linux/arch/x86/boot/bzImage", "cpu": 2, "mem": 2048 }
}
EOF

# 编内核要开
# CONFIG_KCOV=y         coverage
# CONFIG_KASAN=y        AddressSanitizer
# CONFIG_KMSAN=y        MemorySanitizer
# CONFIG_DEBUG_INFO=y
# CONFIG_KMEMLEAK=y

# 启动 fuzzer
syz-manager -config my.cfg
# Web UI: http://127.0.0.1:56741 → 实时 crash + coverage + reproducer

# crash → 自动产 C 复现
ls workdir/crashes/
cat workdir/crashes/<hash>/repro.c                          # 自动生成 C 触发器
```

## Fuzzilli（JS 引擎专用）

```bash
# 跑 V8
git clone https://github.com/googleprojectzero/fuzzilli
swift build -c release
.build/release/FuzzilliCli --profile=v8 \
    --storagePath=./fuzzdata/ \
    /path/to/v8/out/fuzzbuild/d8

# 现成 profile: v8 / spidermonkey / jsc / duktape / hermes / qjs
# 它会生成 FuzzIL → lift 成 JS → 跑 d8 → 命中 V8 bug

# 历史: 从 V8 找到几十个真实 CVE
```

## 协议 fuzz

```bash
# AFLNet (AFL + 网络 state-aware)
afl-fuzz -i in -o out -N tcp://127.0.0.1/80 -P HTTP -K -- ./web_server @@

# boofuzz (生成式)
pip install boofuzz
python3 - <<'PY'
from boofuzz import *
s = Session(target=Target(connection=TCPSocketConnection("127.0.0.1", 21)))
s.connect(s_get("ftp_user"))
s_initialize("ftp_user")
s_string("USER", fuzzable=False)
s_delim(" ", fuzzable=False)
s_string("anonymous")
s_static("\r\n")
s.fuzz()
PY

# Mutiny (Cisco Talos 出品，基于 pcap 重放)
mutiny.py -i pcap_template input.pcap

# fuzzowski (modern boofuzz 替代)
fuzzowski 127.0.0.1 1337 ftp -f USER
```

## Browser fuzz

```bash
# Domato (Project Zero, DOM grammar)
git clone https://github.com/googleprojectzero/domato
python3 generator.py --no_of_files 1000 --output_dir tests/
# 每个 test.html 喂浏览器 + 监控 crash

# Jackalope (TinyInst Mac/Win 闭源 fuzzer)
# 配合 Domato 一起：Domato 生成 HTML，Jackalope 启 browser

# 自家流程
for i in $(seq 1 1000); do
    chrome --headless --disable-gpu --crash-dumps-dir=/tmp/crashes \
           "file://$(pwd)/tests/test$i.html"
done
```

## Differential fuzz

```python
# 同一输入喂两个实现，比对输出
def diff(data):
    try: a = openssl_parse(data)
    except Exception as e: a = ('exc', str(type(e)))
    try: b = wolfssl_parse(data)
    except Exception as e: b = ('exc', str(type(e)))
    if a != b:
        record(data, a, b)

# libFuzzer harness
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    auto r1 = parser_A(data, size);
    auto r2 = parser_B(data, size);
    if (r1.status != r2.status) abort();
    if (r1.value != r2.value)   abort();
    return 0;
}
```

## Snapshot fuzzer (Nyx / KAFL / LibAFL)

```text
原理: 把整个 VM 在 ready-to-fuzz 状态做 snapshot，每次 fuzz iteration
      → 注入 testcase → 跑 → restore snapshot
适合: 内核 / driver / 固件 / 难初始化的复杂状态

LibAFL (现代 Rust fuzzer 工程框架):
  github.com/AFLplusplus/LibAFL
  内置 frida_executor / qemu_executor / tinyinst_executor / nyx_executor
  写 Rust 几十行就有 production-grade fuzzer

KAFL (Linux 内核 hypervisor 级):
  github.com/IntelLabs/kAFL
  Intel PT (Processor Trace) 收集 coverage → 无插桩内核 fuzz

Nyx (KAFL 升级版):
  github.com/nyx-fuzz
  Snapshot-based, full VM, 适合 Linux/Windows driver
```

## Concolic / Hybrid (符号执行 + fuzz)

```bash
# Driller (angr + AFL)
# AFL 找通用路径 → angr 解 magic 检查 / hash 校验
git clone https://github.com/shellphish/driller
driller -b ./target -i corpus/ -o out/

# QSYM (libdft + Z3)
# 比 angr 快 100x，工业级
QSYM_BIN=./qsym ./qsym ./target ./out/queue

# SymCC (compile-time symbolic execution)
clang -fpass-plugin=SymCC.so target.c -o target_sym
./target_sym ./input.bin                                     # 直接跑出 path 约束

# Eclipser / IntelliFuzz / Angora 也是同类
```

## Harness 编写要点

```text
1) 隔离要 fuzz 的函数
   - 把 main() 拆成 parse(buf, len) + 主流程
   - LLVMFuzzerTestOneInput / __AFL_LOOP 都喂 buf+len

2) 关掉无关:
   - 日志、网络、文件、随机
   - 用 stubbing 替换 (LD_PRELOAD / hook)

3) 抑制误报:
   - 已知非崩溃的 abort/assert → 用 setenv("ASAN_OPTIONS","abort_on_error=0")
   - 输入太大 → max_len 限制

4) 性能:
   - persistent mode > exec mode (10-100x)
   - 大 corpus 用 cmin 压缩到 < 200 个种子
   - 关掉 mmap-based COW 检测，减少 syscall

5) 反混淆:
   - 用 cmplog mode 让 fuzzer 知道 strcmp/memcmp 的 token
   - 提取 strings 作字典

6) ASAN/UBSAN 配合:
   - 同时开找 UB / OOB / UAF / leak
   - ASAN_OPTIONS="detect_stack_use_after_return=1:strict_string_checks=1:check_initialization_order=1:detect_invalid_pointer_pairs=2"

7) 内存 / 时间预算:
   - rss_limit_mb 防 OOM
   - timeout 防 hang
   - 一个 case 应 < 100 ms（最优）
```

## 与逆向联动

```text
binrev → fuzzrev:
  1) 反编译目标，找 parser / decoder / validator 函数
  2) 找 syscall 入口 (read/recv/recvfrom/file open)
  3) 提取该函数的入参 sig (buf, len)
  4) 写 harness 把它 hook 出来作 LLVMFuzzerTestOneInput
  5) 用 strings + 自动字典 加速

irrev → fuzzrev:
  1) angr / Triton 做覆盖率引导 / 路径约束求解
  2) hybrid fuzz (Driller / QSYM) 解 magic / hash / CRC
  3) 数据流分析找到 source(read)→sink(write/exec)，重点 fuzz 该路径

crashrev ← fuzzrev:
  1) afl-tmin / honggfuzz --minimize 最小化输入
  2) 按 stack hash 去重 (afl-collect / casr)
  3) ASAN log 直接进 crashrev 分析

corpus 来源:
  - 公开 OSS-Fuzz corpus (gs://oss-fuzz-corpus/)
  - GitHub 开源 + Google Code Search 找该格式的样本
  - 已有崩溃后用 afl-cmin 精简，作下一轮 seed
```

## OSS-Fuzz / 持续 fuzz

```text
OSS-Fuzz: Google 出品，给开源项目免费跑 fuzz
  https://github.com/google/oss-fuzz
  写一个 build.sh + Dockerfile + fuzz_target.cc
  PR 接受后 Google 跑 16 vCPU × 24x7
  发现 bug 自动建 issue (90 天 disclosure)

ClusterFuzzLite: 自家轻量版
  GitHub Actions / GitLab CI / Drone 都能集成
  每次 PR 跑 ≤ 30min fuzz，发现 regression 阻挡 merge

FuzzBench: Google 出品 fuzzer 基准测试
  https://github.com/google/fuzzbench
  把 N 个 fuzzer × M 个 target 跑 24h，出 coverage 曲线 + 排名

商业流水线参考:
  - GitHub Actions: ClusterFuzzLite
  - CircleCI/Buildkite: 自家 fuzz job → S3 corpus → SaaS triage
  - Mayhem (ForAllSecure, 商业)
  - Fuzzbuzz (商业)
  - Code Intelligence (商业)
```

## 实战入口

- **OSS-Fuzz Trophies**：历年开源 bug 大全 + reproducer。
- **FuzzBench**：fuzzer 跑分平台 + 全量 trace。
- **FuzzGoat / DARPA CGC binaries**：练手 corpus。
- **AFL++ docs / awesome-fuzzing GitHub**：工具集成索引。
- **Project Zero blog**：Fuzzilli / Domato / Jackalope 原作者讲解。
- **FuzzingLabs / Hackueneca / LiveOverflow YouTube**。
- **Fuzzing 101 (Antonio Morales)**：每周一个真实 CVE，AFL 复现教程。
- **The Fuzzing Book (Andreas Zeller, free online)**：理论 + 代码。
- **DEF CON / Black Hat / OffensiveCon fuzzing tracks**。
- **Phantasmal Phantasm / @fuzzing_io / @gamozolabs Twitter**。

## 自检（开始 fuzz 前 30 分钟内回答）

1. 目标输入入口在哪？harness 怎么把它隔离出来？
2. 有源码吗？哪个编译器 + sanitizer 组合最适合（ASAN/UBSAN/MSAN/TSAN）？
3. corpus 来源 + 起点大小（≤ 200 个最优）？需要字典 / 文法吗？
4. 单 case 执行时间能压到 < 100ms 吗（persistent mode）？
5. 闭源 → 用 QEMU / FRIDA / TinyInst / Jackalope / WinAFL 哪个引擎？
6. 是否需要 hybrid（Driller/QSYM）解 magic / hash / CRC 阻塞？
7. crash triage / dedup 用 casr / afl-collect / stack hash 哪种？
8. coverage 报告生成（afl-cov / kcov / SanCov）+ 看 coverage 增长曲线？

## 相邻技能

- `binrev` — 找 harness 入口、参数 / 数据流。
- `crashrev` — 接收 fuzzer 产出的 crash 分析。
- `irrev` — Driller/QSYM/SymCC 符号执行联动。
- `debugrev` — Frida / WinDbg 配合 fuzzer 抓现场。
- `protrev` — 协议 fuzz harness 编写。
- `linuxrev` / `winrev` / `macrev` — 平台 sanitizer / coredump 配置。
- `cryptrev` — 解析器中的加密 / hash 校验绕过。
- `vmrev` — VM / JIT / 解释器 fuzz（Fuzzilli 等）。
- `revauto` — fuzz + analysis 自动化流水线。
- `revlab` — 实验室 fuzz 集群搭建。