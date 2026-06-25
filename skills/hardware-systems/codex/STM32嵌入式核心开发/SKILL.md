---
name: STM32嵌入式核心开发
description: 芯片架构、时钟系统、GPIO编程、中断管理、启动流程、开发环境搭建与调试技巧。覆盖F103(Cortex-M3)和F407(Cortex-M4F)，支持标准库和HAL库。
disable-model-invocation: false
user-invocable: false
---

# STM32 嵌入式核心开发

## 芯片速查

```
┌─────────────────────────────────────────────────────────────────┐
│  STM32F103 (Cortex-M3)           │  STM32F407 (Cortex-M4F)     │
├──────────────────────────────────┼──────────────────────────────┤
│  主频: 72 MHz                    │  主频: 168 MHz               │
│  Flash: 64K-512K                 │  Flash: 512K-1M              │
│  SRAM: 20K-64K                   │  SRAM: 192K + 64K CCM        │
│  FPU: 无                         │  FPU: 单精度硬件浮点          │
│  供电: 2.0-3.6V                  │  供电: 1.8-3.6V              │
│  封装: LQFP48/64/100/144        │  封装: LQFP100/144/176       │
│  ADC: 12bit 1us                  │  ADC: 12bit 0.42us           │
│  定时器: 4通用+2高级+2基本       │  定时器: 10通用+2高级+2基本   │
│  DMA: 7ch(DMA1)                  │  DMA: 8ch×2(DMA1+DMA2)       │
│  USB: FS Device                  │  USB: FS+HS(OTG)             │
└──────────────────────────────────┴──────────────────────────────┘
```

### 常用型号选型

| 型号 | Flash | SRAM | 引脚 | 适用场景 |
|------|-------|------|------|----------|
| F103C8T6 | 64K | 20K | 48 | 入门学习、小型项目 |
| F103RCT6 | 256K | 48K | 64 | 中等项目、常用开发板 |
| F103ZET6 | 512K | 64K | 144 | 全引脚开发板、复杂项目 |
| F407VGT6 | 1M | 192K | 100 | 高性能项目、音视频 |
| F407ZGT6 | 1M | 192K | 144 | 全外设评估 |

---

## 开发环境

### Keil MDK 5 (推荐 Windows)

```
1. 安装 Keil MDK-ARM (≥5.30)
2. Pack Installer → 安装:
   - Keil::STM32F1xx_DFP (F103)
   - Keil::STM32F4xx_DFP (F407)
3. 新建工程 → 选择芯片型号
4. Manage Run-Time Environment → 勾选 CMSIS/CORE + Device/Startup
5. Options → Debug → 选择 ST-Link/J-Link
6. Options → C/C++ → Define: USE_STDPERIPH_DRIVER (标准库) 或 USE_HAL_DRIVER (HAL库)
7. Options → C/C++ → Include Paths: 添加库头文件路径
```

### STM32CubeIDE (跨平台, 免费)

```
1. 安装 STM32CubeIDE
2. File → New → STM32 Project
3. 芯片选型 → 图形化配置引脚和时钟
4. Project Manager → Toolchain: STM32CubeIDE
5. Generate Code → 自动生成 HAL 初始化代码
```

### VS Code + PlatformIO

```ini
; platformio.ini
[env:f103]
platform = ststm32
board = genericSTM32F103C8
framework = stm32cube  ; 或 cmsis
upload_protocol = stlink
debug_tool = stlink
monitor_speed = 115200

[env:f407]
platform = ststm32
board = disco_f407vg
framework = stm32cube
upload_protocol = stlink
```

---

## 启动流程

```
上电/复位
  ↓
Boot 引脚采样 (BOOT0/BOOT1)
  ├─ BOOT0=0: Flash 启动 (正常)     → 0x08000000
  ├─ BOOT0=1,BOOT1=0: 系统存储器    → 内置 Bootloader (串口下载)
  └─ BOOT0=1,BOOT1=1: 内置 SRAM     → 0x20000000
  ↓
取栈指针 (0x08000000 → MSP)
取复位向量 (0x08000004 → Reset_Handler)
  ↓
Reset_Handler (startup_stm32f10x_xx.s):
  1. 初始化 .data 段 (Flash → SRAM)
  2. 清零 .bss 段
  3. 调用 SystemInit() → 配置时钟
  4. 调用 __main → C 库初始化
  5. 跳转 main()
```

### 内存映射

```c
/* F103 内存布局 */
// 0x08000000 - 0x0807FFFF  Flash (最大 512K)
// 0x20000000 - 0x2000FFFF  SRAM  (最大 64K)
// 0x40000000 - 0x4000FFFF  APB1 外设
// 0x40010000 - 0x4001FFFF  APB2 外设
// 0x40020000 - 0x40023FFF  AHB 外设

/* F407 内存布局 */
// 0x08000000 - 0x080FFFFF  Flash (最大 1M)
// 0x20000000 - 0x2002FFFF  SRAM  (192K)
// 0x10000000 - 0x1000FFFF  CCM   (64K, 仅 CPU 访问, DMA 不可达)
// 0x40000000 - 0x4000FFFF  APB1 外设
// 0x40010000 - 0x4001FFFF  APB2 外设
// 0x40020000 - 0x4007FFFF  AHB1 外设
// 0x50000000 - 0x50060BFF  AHB2 外设 (USB OTG, DCMI, RNG 等)
```

---

## 时钟系统 (RCC)

### F103 时钟树

```
HSE (8MHz 外部晶振)
  ↓ ×9 (PLL)
SYSCLK = 72MHz
  ├─ AHB  = 72MHz  (HCLK, /1)
  ├─ APB1 = 36MHz  (PCLK1, /2)  — TIM2-7, USART2/3, UART4/5, SPI2/3, I2C, USB
  └─ APB2 = 72MHz  (PCLK2, /1)  — GPIOA-G, USART1, SPI1, TIM1/8, ADC
注意: APB1 定时器时钟 = 72MHz (分频 ≠1 时自动 ×2)
```

### 标准库 — 时钟配置 (F103, 72MHz)

```c
void RCC_Configuration(void)
{
    RCC_DeInit();  // 复位 RCC 到默认状态

    RCC_HSEConfig(RCC_HSE_ON);  // 启动 HSE
    if (RCC_WaitForHSEStartUp() == SUCCESS) {
        FLASH_PrefetchBufferCmd(FLASH_PrefetchBuffer_Enable);
        FLASH_SetLatency(FLASH_Latency_2);  // 72MHz 需要 2 等待周期

        RCC_HCLKConfig(RCC_SYSCLK_Div1);    // AHB = SYSCLK
        RCC_PCLK2Config(RCC_HCLK_Div1);     // APB2 = AHB
        RCC_PCLK1Config(RCC_HCLK_Div2);     // APB1 = AHB/2

        RCC_PLLConfig(RCC_PLLSource_HSE_Div1, RCC_PLLMul_9);  // 8×9=72MHz
        RCC_PLLCmd(ENABLE);
        while (RCC_GetFlagStatus(RCC_FLAG_PLLRDY) == RESET);

        RCC_SYSCLKConfig(RCC_SYSCLKSource_PLLCLK);
        while (RCC_GetSYSCLKSource() != 0x08);  // 等待 PLL 成为系统时钟
    }
}
// 注: 标准库工程通常在 system_stm32f10x.c 的 SystemInit() 中已完成
// 仅需确认 stm32f10x.h 中 HSE_VALUE=8000000
```

### HAL 库 — 时钟配置 (F103, 72MHz)

```c
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInit = {0};
    RCC_ClkInitTypeDef RCC_ClkInit = {0};

    RCC_OscInit.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInit.HSEState = RCC_HSE_ON;
    RCC_OscInit.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
    RCC_OscInit.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInit.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInit.PLL.PLLMUL = RCC_PLL_MUL9;  // 8×9=72MHz
    HAL_RCC_OscConfig(&RCC_OscInit);

    RCC_ClkInit.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                          | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInit.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInit.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInit.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInit.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInit, FLASH_LATENCY_2);
}
```

### HAL 库 — 时钟配置 (F407, 168MHz)

```c
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInit = {0};
    RCC_ClkInitTypeDef RCC_ClkInit = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

    RCC_OscInit.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInit.HSEState = RCC_HSE_ON;
    RCC_OscInit.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInit.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInit.PLL.PLLM = 8;    // 8MHz / 8 = 1MHz
    RCC_OscInit.PLL.PLLN = 336;  // 1MHz × 336 = 336MHz
    RCC_OscInit.PLL.PLLP = RCC_PLLP_DIV2;  // 336/2 = 168MHz SYSCLK
    RCC_OscInit.PLL.PLLQ = 7;    // 336/7 = 48MHz (USB)
    HAL_RCC_OscConfig(&RCC_OscInit);

    RCC_ClkInit.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                          | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInit.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInit.AHBCLKDivider = RCC_SYSCLK_DIV1;    // 168MHz
    RCC_ClkInit.APB1CLKDivider = RCC_HCLK_DIV4;     // 42MHz
    RCC_ClkInit.APB2CLKDivider = RCC_HCLK_DIV2;     // 84MHz
    HAL_RCC_ClockConfig(&RCC_ClkInit, FLASH_LATENCY_5);
}
```

---

## GPIO 编程

### 引脚模式速查

| 模式 | StdPeriph 常量 | HAL 常量 | 典型用途 |
|------|---------------|----------|----------|
| 推挽输出 | GPIO_Mode_Out_PP | GPIO_MODE_OUTPUT_PP | LED、控制信号 |
| 开漏输出 | GPIO_Mode_Out_OD | GPIO_MODE_OUTPUT_OD | I2C、电平转换 |
| 复用推挽 | GPIO_Mode_AF_PP | GPIO_MODE_AF_PP | USART_TX、SPI |
| 复用开漏 | GPIO_Mode_AF_OD | GPIO_MODE_AF_OD | I2C (HAL) |
| 浮空输入 | GPIO_Mode_IN_FLOATING | GPIO_MODE_INPUT | 外部已有上/下拉 |
| 上拉输入 | GPIO_Mode_IPU | GPIO_MODE_INPUT + PULL_UP | 按键(默认高) |
| 下拉输入 | GPIO_Mode_IPD | GPIO_MODE_INPUT + PULL_DOWN | 按键(默认低) |
| 模拟输入 | GPIO_Mode_AIN | GPIO_MODE_ANALOG | ADC 采集 |

### 标准库 — LED 闪烁 (F103, PC13)

```c
#include "stm32f10x.h"

void GPIO_Config(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE);  // 开时钟!

    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_13;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_2MHz;  // LED 低速即可
    GPIO_Init(GPIOC, &GPIO_InitStruct);
}

void delay_ms(uint32_t ms)
{
    // 简易延时, 72MHz 主频下粗略延时
    volatile uint32_t i;
    for (; ms > 0; ms--)
        for (i = 0; i < 7200; i++);
}

int main(void)
{
    GPIO_Config();
    while (1) {
        GPIO_ResetBits(GPIOC, GPIO_Pin_13);  // 点亮 (低电平点亮)
        delay_ms(500);
        GPIO_SetBits(GPIOC, GPIO_Pin_13);    // 熄灭
        delay_ms(500);
    }
}
```

### HAL 库 — LED 闪烁 (F407, PD12-PD15 四色 LED)

```c
#include "stm32f4xx_hal.h"

void GPIO_Config(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOD_CLK_ENABLE();  // 开时钟!

    GPIO_InitStruct.Pin = GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    GPIO_Config();

    while (1) {
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);  // 绿
        HAL_Delay(200);
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_13);  // 橙
        HAL_Delay(200);
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_14);  // 红
        HAL_Delay(200);
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_15);  // 蓝
        HAL_Delay(200);
    }
}
```

### F407 GPIO 复用 (AF) — 关键区别

```c
// F103: 复用功能由引脚硬件决定, 无需指定 AF 编号
// F407: 必须通过 GPIO_PinAFConfig / Alternate 指定复用功能编号

// 标准库 F407 — USART1 TX(PA9)
GPIO_PinAFConfig(GPIOA, GPIO_PinSource9, GPIO_AF_USART1);

// HAL 库 F407 — USART1 TX(PA9)
GPIO_InitStruct.Alternate = GPIO_AF7_USART1;
```

---

## NVIC 中断管理

### 中断优先级

```
F103/F407 均使用 4 位优先级 (0-15), 分为:
  - 抢占优先级 (Preemption): 高优先级可打断低优先级 ISR
  - 子优先级 (Sub): 同抢占优先级时决定响应顺序

优先级分组 (全局设置一次):
  Group 0: 0位抢占 / 4位子  → 无抢占
  Group 1: 1位抢占 / 3位子
  Group 2: 2位抢占 / 2位子  ← 推荐
  Group 3: 3位抢占 / 1位子
  Group 4: 4位抢占 / 0位子  → 16级全抢占 (FreeRTOS 常用)
数字越小优先级越高!
```

### 标准库

```c
// 设置分组 (在 main 初始化时调用一次)
NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);

// 配置具体中断
NVIC_InitTypeDef NVIC_InitStruct;
NVIC_InitStruct.NVIC_IRQChannel = USART1_IRQn;
NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 1;
NVIC_InitStruct.NVIC_IRQChannelSubPriority = 0;
NVIC_InitStruct.NVIC_IRQChannelCmd = ENABLE;
NVIC_Init(&NVIC_InitStruct);
```

### HAL 库

```c
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
HAL_NVIC_SetPriority(USART1_IRQn, 1, 0);
HAL_NVIC_EnableIRQ(USART1_IRQn);
```

---

## 调试工具

### J-Link vs ST-Link

| 特性 | J-Link | ST-Link V2 |
|------|--------|------------|
| 价格 | 高 (正版)/低 (盗版) | 低 |
| 速度 | 快 (USB 高速) | 中 |
| 支持芯片 | ARM 全系列 | 仅 STM32 |
| 接口 | SWD + JTAG | SWD + JTAG |
| RTT 调试 | 支持 (高速串口替代) | 不支持 |
| 软件 | J-Flash, Ozone | STM32 ST-LINK Utility |

### SWD 接线 (最常用, 仅 4 线)

```
调试器          目标板
SWDIO  ────────  SWDIO (PA13)
SWCLK  ────────  SWCLK (PA14)
GND    ────────  GND
3.3V   ────────  VCC (可选, 目标板自供电时不接)
```

### 串口 printf 重定向 (标准库)

```c
#include <stdio.h>

// Keil MDK: Options → Target → 勾选 Use MicroLIB
int fputc(int ch, FILE *f)
{
    USART_SendData(USART1, (uint8_t)ch);
    while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
    return ch;
}

// 用法: printf("Tick = %d\r\n", SysTick->VAL);
```

### 串口 printf 重定向 (HAL 库)

```c
// 方式1: 重定向 fputc (需 MicroLIB)
int fputc(int ch, FILE *f)
{
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

// 方式2: 直接使用 HAL_UART_Transmit
char buf[64];
int len = snprintf(buf, sizeof(buf), "ADC = %d\r\n", adc_val);
HAL_UART_Transmit(&huart1, (uint8_t *)buf, len, 100);
```

### J-Link RTT (无需串口, 通过 SWD 传输)

```c
#include "SEGGER_RTT.h"

// 比串口快 10 倍以上, 不占用 USART
SEGGER_RTT_printf(0, "RTT: val=%d\r\n", val);
```

### 常见调试问题

```
问题: 下载后程序不运行
  → 检查 BOOT0 是否为低电平 (GND)
  → 检查复位电路, NRST 需有 100nF 滤波

问题: HardFault
  → 查看 SCB->CFSR 寄存器定位原因
  → 常见: 未对齐访问、栈溢出、空指针、除零
  → Keil: Debug → Fault Reports 窗口

问题: 时钟配置失败 (HSE 不起振)
  → 检查外部晶振焊接, 负载电容值
  → 检查 HSE_VALUE 宏是否与实际晶振匹配
  → 回退到 HSI (内部 8MHz) 测试

问题: GPIO 不输出
  → 确认已开启对应 GPIO 端口时钟!
  → F103: RCC_APB2PeriphClockCmd
  → F407: __HAL_RCC_GPIOx_CLK_ENABLE()
```

---

## 标准库 vs HAL 库对比

| 维度 | 标准库 (StdPeriph) | HAL 库 |
|------|-------------------|--------|
| 抽象层级 | 薄封装, 接近寄存器 | 厚封装, 回调驱动 |
| 代码效率 | 高 (编译体积小) | 中 (较多封装开销) |
| 可移植性 | 仅同系列 | 跨 STM32 系列 |
| 学习曲线 | 需理解寄存器 | CubeMX 生成, 上手快 |
| 官方支持 | 已停止更新 | 持续更新 |
| 适用场景 | 老项目维护、追求极致性能 | 新项目、快速原型 |
| DMA/IT模式 | 手动管理 | HAL_xxx_IT / HAL_xxx_DMA |

**建议**: 新项目用 HAL + CubeMX 快速搭建，学习阶段用标准库理解底层原理。

---

## 位带操作 (Bit-Band)

```c
// F103/F407 支持位带操作, 实现原子位操作 (无需 读-改-写)
// 外设位带区: 0x40000000-0x400FFFFF → 别名区: 0x42000000-0x43FFFFFF
// SRAM位带区: 0x20000000-0x200FFFFF → 别名区: 0x22000000-0x23FFFFFF

// 外设位带宏
#define BITBAND_PERI(addr, bitnum) \
    ((volatile uint32_t *)(0x42000000 + ((uint32_t)(addr) - 0x40000000) * 32 + (bitnum) * 4))
// SRAM 位带宏
#define BITBAND_SRAM(addr, bitnum) \
    ((volatile uint32_t *)(0x22000000 + ((uint32_t)(addr) - 0x20000000) * 32 + (bitnum) * 4))

// 示例: 快速操作 PC13
#define GPIOC_ODR_Addr (GPIOC_BASE + 0x0C)  // F103 ODR 偏移 0x0C
#define PC13_OUT  *BITBAND_PERI(GPIOC_ODR_Addr, 13)

PC13_OUT = 0;  // PC13 输出低
PC13_OUT = 1;  // PC13 输出高 (单条指令, 原子操作)
```

---

## 工程模板结构

```
Project/
├── Core/
│   ├── Inc/           # 用户头文件
│   └── Src/
│       ├── main.c
│       ├── stm32f1xx_it.c    # 中断服务函数
│       └── system_stm32f1xx.c
├── Drivers/
│   ├── CMSIS/         # ARM CMSIS 核心文件
│   └── STM32F1xx_HAL_Driver/  # 或 StdPeriph_Lib
│       ├── Inc/
│       └── Src/
├── Startup/
│   └── startup_stm32f103xb.s  # 启动文件 (选对型号!)
├── MDK-ARM/           # Keil 工程文件
└── STM32F103C8Tx_FLASH.ld    # 链接脚本 (GCC)
```

### 启动文件选择

```
F103:
  startup_stm32f10x_ld.s   — 低密度 (Flash ≤ 32K)
  startup_stm32f10x_md.s   — 中密度 (Flash 64-128K) ← C8T6 用这个
  startup_stm32f10x_hd.s   — 高密度 (Flash 256-512K) ← RCT6/ZET6
  startup_stm32f10x_xl.s   — 超高密度 (Flash > 512K)

F407:
  startup_stm32f407xx.s     — 所有 F407 型号通用
```

