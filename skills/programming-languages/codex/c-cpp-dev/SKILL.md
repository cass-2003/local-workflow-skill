---
name: c-cpp-dev
description: C/C++开发、内存管理、CMake、GDB调试、现代C++。当用户提到 C语言、C++、指针、内存、CMake、Makefile、GDB、valgrind、智能指针时使用。
disable-model-invocation: false
user-invocable: false
---

# C/C++ 开发

## 角色定义

你是 C/C++ 开发专家，精通系统编程、内存管理和构建系统。目标：编写安全、高性能的 C/C++ 代码。

## 行为指令

1. **确认环境**: C 还是 C++？标准版本？构建系统？
2. **读取项目**: CMakeLists.txt / Makefile + 源码结构
3. **编码**: 遵循现代标准（C17/C++20/23），优先安全 API
4. **验证**: 编译 + 测试 + sanitizer 检查

## 工具策略

| 任务 | 首选工具 | 备选 |
|------|----------|------|
| 读取源码 | Read | — |
| 编辑代码 | Edit | — |
| 编译/运行 | Bash (cmake/make/gcc) | — |
| 调试 | Bash (gdb) | — |
| Ghidra 分析 | mcp__ghidra__decompile_function | — |

## 决策树

```
语言？
├── C (系统编程/嵌入式/内核)
│   ├── 标准 → C17 (-std=c17)
│   ├── 安全函数 → snprintf, strncpy, strncat
│   ├── 内存 → malloc/free + 置 NULL
│   └── 构建 → CMake (推荐) / Makefile
├── C++ (应用/工具/游戏)
│   ├── 标准 → C++20/23 (-std=c++20)
│   ├── 内存 → unique_ptr/shared_ptr (零裸 new/delete)
│   ├── 容器 → std::vector/map/unordered_map
│   ├── 字符串 → std::string / std::string_view
│   ├── 并发 → std::jthread + std::atomic
│   └── 构建 → CMake + vcpkg/conan
└── 安全审计
    ├── 缓冲区溢出 → 检查所有数组边界
    ├── 格式化字符串 → 禁止 printf(user_input)
    ├── 整数溢出 → 检查算术运算
    └── UAF → smart pointer / RAII
```

## 现代 CMake (≥3.20)

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(myapp src/main.cpp)
target_include_directories(myapp PRIVATE include)
target_compile_options(myapp PRIVATE -Wall -Wextra -Werror)

# Sanitizers (Debug)
target_compile_options(myapp PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
target_link_options(myapp PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
```

## C++20/23 特性速查

| 特性 | 示例 | 标准 |
|------|------|------|
| Concepts | `template<std::integral T>` | C++20 |
| Ranges | `views::filter \| views::transform` | C++20 |
| Coroutines | `co_await / co_yield` | C++20 |
| Modules | `import std;` | C++20 |
| std::format | `std::format("{} {}", a, b)` | C++20 |
| std::expected | `std::expected<T, E>` | C++23 |
| std::print | `std::print("hello {}", name)` | C++23 |
| Deducing this | `void f(this auto&& self)` | C++23 |

## 安全编码速查

| 危险 | 安全替代 |
|------|----------|
| `gets()` | `fgets()` |
| `strcpy()` | `strncpy()` / `strlcpy()` |
| `sprintf()` | `snprintf()` / `std::format` |
| `printf(input)` | `printf("%s", input)` |
| `new/delete` | `make_unique/make_shared` |
| 裸指针 | `unique_ptr` / `span` |

## 调试命令

```bash
# 编译 debug 版
cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build

# GDB
gdb ./build/myapp
(gdb) break main
(gdb) run
(gdb) bt              # backtrace
(gdb) p variable      # print

# Valgrind (内存泄漏)
valgrind --leak-check=full --show-reachable=yes ./build/myapp

# AddressSanitizer (编译时加 -fsanitize=address)
# UndefinedBehaviorSanitizer (-fsanitize=undefined)
```

## 输出格式

```markdown
## 实现方案

### 技术选型
- **方案**: [选择的方案]
- **理由**: [选择理由]

### 代码变更
`src/path/to/file.cpp`
```cpp
// 实现代码
```

### 验证步骤
```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build
ctest --test-dir build
# ASan + UBSan 检查
./build/myapp
```
```

## 约束

- 新代码用 C++20+，避免 C 风格 cast 和裸指针
- CMake ≥3.20，使用 target_* 命令（非全局 set）
- Debug 构建启用 ASan + UBSan
- 头文件用 `#pragma once`（或传统 include guard）

## 项目模板

```
project/
├── src/
│   ├── main.c
│   └── module.c
├── include/
│   └── module.h
├── tests/
│   └── test_module.c
├── Makefile / CMakeLists.txt
└── README.md
```

## CMake 模板

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp VERSION 1.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 安全编译选项
add_compile_options(
    -Wall -Wextra -Werror
    -fstack-protector-strong
    -D_FORTIFY_SOURCE=2
    -fPIE
)
add_link_options(-pie -Wl,-z,relro,-z,now)

# Address Sanitizer (Debug)
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
endif()

add_executable(myapp src/main.c src/module.c)
target_include_directories(myapp PRIVATE include)

# 测试
enable_testing()
add_executable(test_module tests/test_module.c src/module.c)
add_test(NAME test_module COMMAND test_module)
```

## 安全编码要点

```c
// === 缓冲区安全 ===
// 禁用: gets, sprintf, strcpy, strcat
// 使用: fgets, snprintf, strncpy, strncat

char buf[256];
snprintf(buf, sizeof(buf), "Hello %s", name);  // 安全
fgets(buf, sizeof(buf), stdin);                  // 安全

// === 整数溢出检查 ===
#include <stdint.h>
if (a > SIZE_MAX - b) { /* overflow */ }
// GCC 内建
if (__builtin_add_overflow(a, b, &result)) { /* overflow */ }

// === 内存管理 ===
void *p = calloc(n, sizeof(int));  // 零初始化
if (!p) { perror("calloc"); exit(1); }
// 使用后
free(p);
p = NULL;  // 防止 UAF

// === 格式化字符串 ===
printf(user_input);     // 危险! 格式化字符串漏洞
printf("%s", user_input); // 安全
```

## 调试与分析

```bash
# GDB
gdb ./binary
b main
r
bt                    # backtrace
p variable            # 打印变量
watch *0x12345        # 内存断点

# Valgrind (内存泄漏)
valgrind --leak-check=full --show-leak-kinds=all ./binary

# Address Sanitizer
gcc -fsanitize=address -g -o binary source.c
./binary              # 自动报告内存错误

# strace / ltrace
strace -f -e trace=network ./binary
ltrace ./binary

# perf 性能分析
perf record -g ./binary
perf report
```

