---
name: STM32外设驱动开发
description: USART串口通信、TIM定时器与PWM、DMA直接内存访问、SPI/I2C总线、ADC/DAC模拟转换、EXTI外部中断。覆盖F103和F407，标准库与HAL库双版本示例。
disable-model-invocation: false
user-invocable: false
---

# STM32 外设驱动开发

---

## USART 串口通信

### 引脚分配

| 外设 | F103 TX/RX | F407 TX/RX | AF(F407) |
|------|-----------|-----------|----------|
| USART1 | PA9/PA10 | PA9/PA10 或 PB6/PB7 | AF7 |
| USART2 | PA2/PA3 | PA2/PA3 或 PD5/PD6 | AF7 |
| USART3 | PB10/PB11 | PB10/PB11 或 PD8/PD9 | AF7 |

### 标准库 — USART1 收发 (F103)

```c
#include "stm32f10x.h"

void USART1_Init(uint32_t baud)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    USART_InitTypeDef USART_InitStruct;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1 | RCC_APB2Periph_GPIOA, ENABLE);

    // TX: PA9 复用推挽
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStruct);

    // RX: PA10 浮空输入
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOA, &GPIO_InitStruct);

    USART_InitStruct.USART_BaudRate = baud;
    USART_InitStruct.USART_WordLength = USART_WordLength_8b;
    USART_InitStruct.USART_StopBits = USART_StopBits_1;
    USART_InitStruct.USART_Parity = USART_Parity_No;
    USART_InitStruct.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStruct.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    USART_Init(USART1, &USART_InitStruct);

    USART_Cmd(USART1, ENABLE);
}

void USART1_SendByte(uint8_t data)
{
    USART_SendData(USART1, data);
    while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
}

void USART1_SendString(const char *str)
{
    while (*str) USART1_SendByte(*str++);
}

uint8_t USART1_ReceiveByte(void)
{
    while (USART_GetFlagStatus(USART1, USART_FLAG_RXNE) == RESET);
    return (uint8_t)USART_ReceiveData(USART1);
}
```

### 标准库 — 中断接收 (F103)

```c
// 初始化时添加:
USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);

NVIC_InitTypeDef NVIC_InitStruct;
NVIC_InitStruct.NVIC_IRQChannel = USART1_IRQn;
NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 1;
NVIC_InitStruct.NVIC_IRQChannelSubPriority = 0;
NVIC_InitStruct.NVIC_IRQChannelCmd = ENABLE;
NVIC_Init(&NVIC_InitStruct);

// stm32f10x_it.c 中:
uint8_t rx_buf[256];
volatile uint16_t rx_len = 0;

void USART1_IRQHandler(void)
{
    if (USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
        rx_buf[rx_len++] = USART_ReceiveData(USART1);
        if (rx_len >= sizeof(rx_buf)) rx_len = 0;  // 防溢出
    }
}
```

### HAL 库 — USART + DMA 接收 (F407)

```c
// CubeMX 配置: USART1 → Async, 115200 8N1, DMA RX: Circular
// 生成后在 main.c 中:

uint8_t rx_dma_buf[128];

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_DMA_Init();       // DMA 必须在 USART 之前初始化!
    MX_USART1_UART_Init();

    // 启动 DMA 空闲中断接收 (变长帧最佳方案)
    __HAL_UART_ENABLE_IT(&huart1, UART_IT_IDLE);
    HAL_UART_Receive_DMA(&huart1, rx_dma_buf, sizeof(rx_dma_buf));

    while (1) { /* 处理接收数据 */ }
}

// 空闲中断回调 (在 stm32f4xx_it.c 的 USART1_IRQHandler 中调用)
void USART1_IDLE_Handler(void)
{
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_IDLE)) {
        __HAL_UART_CLEAR_IDLEFLAG(&huart1);
        uint16_t remain = __HAL_DMA_GET_COUNTER(huart1.hdmarx);
        uint16_t len = sizeof(rx_dma_buf) - remain;
        // 处理 rx_dma_buf[0..len-1]
        HAL_UART_DMAStop(&huart1);
        HAL_UART_Receive_DMA(&huart1, rx_dma_buf, sizeof(rx_dma_buf));
    }
}
```

---

## TIM 定时器

### 定时器分类

```
F103:
  高级: TIM1, TIM8           — 带死区/互补输出, 用于电机 PWM
  通用: TIM2, TIM3, TIM4, TIM5 — PWM/捕获/比较
  基本: TIM6, TIM7           — 仅定时, 无 IO 输出

F407:
  高级: TIM1, TIM8
  通用: TIM2-5 (32bit: TIM2,TIM5), TIM9-14
  基本: TIM6, TIM7

定时周期 = (PSC + 1) × (ARR + 1) / TIMx_CLK
```

### 标准库 — 定时器中断 (F103, TIM3, 1秒)

```c
void TIM3_Init(void)
{
    TIM_TimeBaseInitTypeDef TIM_InitStruct;

    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);

    // TIM3 时钟 = 72MHz (APB1 分频 ≠1 时自动 ×2)
    TIM_InitStruct.TIM_Prescaler = 7200 - 1;     // 72MHz/7200 = 10kHz
    TIM_InitStruct.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_InitStruct.TIM_Period = 10000 - 1;        // 10kHz/10000 = 1Hz
    TIM_InitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseInit(TIM3, &TIM_InitStruct);

    TIM_ITConfig(TIM3, TIM_IT_Update, ENABLE);
    TIM_Cmd(TIM3, ENABLE);

    // NVIC
    NVIC_InitTypeDef NVIC_InitStruct;
    NVIC_InitStruct.NVIC_IRQChannel = TIM3_IRQn;
    NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 2;
    NVIC_InitStruct.NVIC_IRQChannelSubPriority = 0;
    NVIC_InitStruct.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStruct);
}

void TIM3_IRQHandler(void)
{
    if (TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET) {
        TIM_ClearITPendingBit(TIM3, TIM_IT_Update);
        // 1 秒触发一次
        GPIO_WriteBit(GPIOC, GPIO_Pin_13,
            (BitAction)(1 - GPIO_ReadOutputDataBit(GPIOC, GPIO_Pin_13)));
    }
}
```

### 标准库 — PWM 输出 (F103, TIM3 CH1, PA6)

```c
void PWM_Init(uint16_t psc, uint16_t arr)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    TIM_TimeBaseInitTypeDef TIM_InitStruct;
    TIM_OCInitTypeDef TIM_OCInitStruct;

    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    // PA6: TIM3_CH1 复用推挽
    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_6;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStruct);

    TIM_InitStruct.TIM_Prescaler = psc;
    TIM_InitStruct.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_InitStruct.TIM_Period = arr;
    TIM_InitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseInit(TIM3, &TIM_InitStruct);

    TIM_OCInitStruct.TIM_OCMode = TIM_OCMode_PWM1;  // CNT < CCR 时输出有效
    TIM_OCInitStruct.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OCInitStruct.TIM_Pulse = 0;  // 初始占空比 0
    TIM_OCInitStruct.TIM_OCPolarity = TIM_OCPolarity_High;
    TIM_OC1Init(TIM3, &TIM_OCInitStruct);

    TIM_OC1PreloadConfig(TIM3, TIM_OCPreload_Enable);
    TIM_ARRPreloadConfig(TIM3, ENABLE);
    TIM_Cmd(TIM3, ENABLE);
}

// 调节占空比: TIM_SetCompare1(TIM3, duty);  // duty: 0 ~ arr
// PWM 频率 = TIM_CLK / (PSC+1) / (ARR+1)
// 例: 72MHz / 72 / 1000 = 1kHz, duty=500 → 50%
```

### HAL 库 — PWM (F407, TIM4 CH1, PD12)

```c
// CubeMX: TIM4 → CH1 PWM Generation, PSC=83, ARR=999 → 84M/84/1000=1kHz

HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);

// 运行时改占空比:
__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, 500);  // 50%
```

### 输入捕获 — 测量脉冲频率 (标准库, F103)

```c
// TIM2 CH1 (PA0) 输入捕获
volatile uint32_t capture_val = 0;
volatile uint8_t capture_flag = 0;

void TIM2_Cap_Init(void)
{
    TIM_ICInitTypeDef TIM_ICInitStruct;

    // GPIO PA0 浮空输入 + TIM2 时钟使能 (略)

    TIM_ICInitStruct.TIM_Channel = TIM_Channel_1;
    TIM_ICInitStruct.TIM_ICPolarity = TIM_ICPolarity_Rising;
    TIM_ICInitStruct.TIM_ICSelection = TIM_ICSelection_DirectTI;
    TIM_ICInitStruct.TIM_ICPrescaler = TIM_ICPSC_DIV1;
    TIM_ICInitStruct.TIM_ICFilter = 0x0F;  // 滤波
    TIM_ICInit(TIM2, &TIM_ICInitStruct);

    TIM_ITConfig(TIM2, TIM_IT_CC1, ENABLE);
    TIM_Cmd(TIM2, ENABLE);
}

void TIM2_IRQHandler(void)
{
    if (TIM_GetITStatus(TIM2, TIM_IT_CC1) != RESET) {
        TIM_ClearITPendingBit(TIM2, TIM_IT_CC1);
        capture_val = TIM_GetCapture1(TIM2);
        TIM_SetCounter(TIM2, 0);
        capture_flag = 1;
    }
}
// 频率 = TIM_CLK / (PSC+1) / capture_val
```

---

## DMA 直接内存访问

### 核心概念

```
DMA 在无需 CPU 干预下搬运数据:
  内存 → 外设 (如: 数组 → USART_DR)
  外设 → 内存 (如: ADC_DR → 数组)
  内存 → 内存 (仅 F407 DMA2)

F103: DMA1(7ch), DMA2(5ch, 仅大容量)  — 通道固定映射
F407: DMA1(8 stream), DMA2(8 stream) — 每 stream 可选通道 0-7
```

### 标准库 — DMA 发送 USART (F103)

```c
// DMA1 Channel4 → USART1_TX (F103 固定映射)
uint8_t tx_buf[] = "Hello DMA!\r\n";

void DMA_USART1_TX_Init(void)
{
    DMA_InitTypeDef DMA_InitStruct;

    RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);

    DMA_DeInit(DMA1_Channel4);
    DMA_InitStruct.DMA_PeripheralBaseAddr = (uint32_t)&USART1->DR;
    DMA_InitStruct.DMA_MemoryBaseAddr = (uint32_t)tx_buf;
    DMA_InitStruct.DMA_DIR = DMA_DIR_PeripheralDST;
    DMA_InitStruct.DMA_BufferSize = sizeof(tx_buf) - 1;
    DMA_InitStruct.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStruct.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStruct.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
    DMA_InitStruct.DMA_MemoryDataSize = DMA_MemoryDataSize_Byte;
    DMA_InitStruct.DMA_Mode = DMA_Mode_Normal;  // 单次
    DMA_InitStruct.DMA_Priority = DMA_Priority_Medium;
    DMA_InitStruct.DMA_M2M = DMA_M2M_Disable;
    DMA_Init(DMA1_Channel4, &DMA_InitStruct);

    USART_DMACmd(USART1, USART_DMAReq_Tx, ENABLE);
    DMA_Cmd(DMA1_Channel4, ENABLE);
}
```

### HAL 库 — ADC + DMA 连续采集 (F407)

```c
// CubeMX: ADC1 → IN0(PA0), Continuous, DMA Circular
uint16_t adc_buf[100];  // DMA 自动填充

HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_buf, 100);

// DMA 传输完成回调
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
    // adc_buf[0..99] 已就绪
    uint32_t sum = 0;
    for (int i = 0; i < 100; i++) sum += adc_buf[i];
    float voltage = (float)sum / 100 * 3.3f / 4096;
}
```

---

## SPI 通信

### 引脚速查

| 外设 | F103 | F407 | 最大速率 |
|------|------|------|---------|
| SPI1 | PA5(SCK)/PA6(MISO)/PA7(MOSI) | PA5/PA6/PA7, AF5 | APB2/2 |
| SPI2 | PB13(SCK)/PB14(MISO)/PB15(MOSI) | PB13/PB14/PB15, AF5 | APB1/2 |

### 标准库 — SPI 读写 W25Q Flash (F103)

```c
void SPI1_Init(void)
{
    SPI_InitTypeDef SPI_InitStruct;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1 | RCC_APB2Periph_GPIOA, ENABLE);
    // SCK PA5, MOSI PA7: AF_PP; MISO PA6: IN_FLOATING; CS PA4: Out_PP (手动控制)

    SPI_InitStruct.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
    SPI_InitStruct.SPI_Mode = SPI_Mode_Master;
    SPI_InitStruct.SPI_DataSize = SPI_DataSize_8b;
    SPI_InitStruct.SPI_CPOL = SPI_CPOL_High;    // W25Q: Mode 3
    SPI_InitStruct.SPI_CPHA = SPI_CPHA_2Edge;
    SPI_InitStruct.SPI_NSS = SPI_NSS_Soft;
    SPI_InitStruct.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_4;  // 72/4=18MHz
    SPI_InitStruct.SPI_FirstBit = SPI_FirstBit_MSB;
    SPI_Init(SPI1, &SPI_InitStruct);
    SPI_Cmd(SPI1, ENABLE);
}

uint8_t SPI1_ReadWriteByte(uint8_t data)
{
    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_TXE) == RESET);
    SPI_I2S_SendData(SPI1, data);
    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_RXNE) == RESET);
    return SPI_I2S_ReceiveData(SPI1);
}

// W25Q 读取 ID
#define W25Q_CS_LOW()   GPIO_ResetBits(GPIOA, GPIO_Pin_4)
#define W25Q_CS_HIGH()  GPIO_SetBits(GPIOA, GPIO_Pin_4)

uint16_t W25Q_ReadID(void)
{
    uint16_t id;
    W25Q_CS_LOW();
    SPI1_ReadWriteByte(0x90);  // Read Manufacturer/Device ID
    SPI1_ReadWriteByte(0x00);
    SPI1_ReadWriteByte(0x00);
    SPI1_ReadWriteByte(0x00);
    id = SPI1_ReadWriteByte(0xFF) << 8;
    id |= SPI1_ReadWriteByte(0xFF);
    W25Q_CS_HIGH();
    return id;  // W25Q64: 0xEF16, W25Q128: 0xEF17
}
```

---

## I2C 通信

### 标准库 — 软件 I2C (推荐, 避免硬件 I2C bug)

```c
// F103 硬件 I2C 存在已知的 BUSY 死锁 bug
// 软件 I2C 更可靠, 可任意引脚

#define I2C_SCL_PIN  GPIO_Pin_6   // PB6
#define I2C_SDA_PIN  GPIO_Pin_7   // PB7
#define I2C_GPIO     GPIOB

#define SCL_H()  GPIO_SetBits(I2C_GPIO, I2C_SCL_PIN)
#define SCL_L()  GPIO_ResetBits(I2C_GPIO, I2C_SCL_PIN)
#define SDA_H()  GPIO_SetBits(I2C_GPIO, I2C_SDA_PIN)
#define SDA_L()  GPIO_ResetBits(I2C_GPIO, I2C_SDA_PIN)
#define SDA_READ() GPIO_ReadInputDataBit(I2C_GPIO, I2C_SDA_PIN)

static void I2C_Delay(void) { volatile uint8_t i = 10; while(i--); }

void I2C_Start(void)
{
    SDA_H(); I2C_Delay();
    SCL_H(); I2C_Delay();
    SDA_L(); I2C_Delay();  // SCL 高时 SDA 下降沿 = START
    SCL_L(); I2C_Delay();
}

void I2C_Stop(void)
{
    SDA_L(); I2C_Delay();
    SCL_H(); I2C_Delay();
    SDA_H(); I2C_Delay();  // SCL 高时 SDA 上升沿 = STOP
}

uint8_t I2C_WriteByte(uint8_t data)
{
    for (uint8_t i = 0; i < 8; i++) {
        if (data & 0x80) SDA_H(); else SDA_L();
        data <<= 1;
        I2C_Delay();
        SCL_H(); I2C_Delay();
        SCL_L(); I2C_Delay();
    }
    // 读 ACK
    SDA_H(); I2C_Delay();
    SCL_H(); I2C_Delay();
    uint8_t ack = SDA_READ();
    SCL_L(); I2C_Delay();
    return ack;  // 0=ACK, 1=NACK
}
```

### HAL 库 — I2C 读取传感器 (F407)

```c
// 读取 MPU6050 (地址 0x68)
#define MPU6050_ADDR  (0x68 << 1)

uint8_t reg_data;
HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, 0x75, I2C_MEMADD_SIZE_8BIT,
                 &reg_data, 1, 100);
// reg_data 应为 0x68 (WHO_AM_I)

// 读取加速度 (6 字节)
uint8_t accel[6];
HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, 0x3B, I2C_MEMADD_SIZE_8BIT,
                 accel, 6, 100);
int16_t ax = (accel[0] << 8) | accel[1];
int16_t ay = (accel[2] << 8) | accel[3];
int16_t az = (accel[4] << 8) | accel[5];
```

---

## ADC 模数转换

### 标准库 — 单通道采集 (F103)

```c
void ADC1_Init(void)
{
    ADC_InitTypeDef ADC_InitStruct;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1 | RCC_APB2Periph_GPIOA, ENABLE);
    RCC_ADCCLKConfig(RCC_PCLK2_Div6);  // 72/6=12MHz (不超过 14MHz)

    // PA0 → ADC_IN0, 模拟输入模式

    ADC_InitStruct.ADC_Mode = ADC_Mode_Independent;
    ADC_InitStruct.ADC_ScanConvMode = DISABLE;
    ADC_InitStruct.ADC_ContinuousConvMode = DISABLE;
    ADC_InitStruct.ADC_ExternalTrigConv = ADC_ExternalTrigConv_None;
    ADC_InitStruct.ADC_DataAlign = ADC_DataAlign_Right;
    ADC_InitStruct.ADC_NbrOfChannel = 1;
    ADC_Init(ADC1, &ADC_InitStruct);

    ADC_Cmd(ADC1, ENABLE);

    // 校准 (必须)
    ADC_ResetCalibration(ADC1);
    while (ADC_GetResetCalibrationStatus(ADC1));
    ADC_StartCalibration(ADC1);
    while (ADC_GetCalibrationStatus(ADC1));
}

uint16_t ADC1_Read(uint8_t channel)
{
    ADC_RegularChannelConfig(ADC1, channel, 1, ADC_SampleTime_239Cycles5);
    ADC_SoftwareStartConvCmd(ADC1, ENABLE);
    while (!ADC_GetFlagStatus(ADC1, ADC_FLAG_EOC));
    return ADC_GetConversionValue(ADC1);  // 0-4095
}

// 电压 = ADC1_Read(ADC_Channel_0) * 3.3f / 4096;
```

### HAL 库 — 多通道 DMA 采集 (F407)

```c
// CubeMX: ADC1 → IN0+IN1+IN4, Scan+Continuous, DMA Circular
uint16_t adc_vals[3];  // 对应 3 个通道

HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_vals, 3);
// adc_vals[0]=CH0, adc_vals[1]=CH1, adc_vals[2]=CH4 持续更新
```

---

## EXTI 外部中断

### 标准库 — 按键中断 (F103, PA0 上升沿)

```c
void EXTI0_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    EXTI_InitTypeDef EXTI_InitStruct;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_AFIO, ENABLE);

    GPIO_InitStruct.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IPD;  // 下拉
    GPIO_Init(GPIOA, &GPIO_InitStruct);

    GPIO_EXTILineConfig(GPIO_PortSourceGPIOA, GPIO_PinSource0);

    EXTI_InitStruct.EXTI_Line = EXTI_Line0;
    EXTI_InitStruct.EXTI_Mode = EXTI_Mode_Interrupt;
    EXTI_InitStruct.EXTI_Trigger = EXTI_Trigger_Rising;
    EXTI_InitStruct.EXTI_LineCmd = ENABLE;
    EXTI_Init(&EXTI_InitStruct);

    // NVIC 配置 (略, 参考前面 NVIC 章节)
}

void EXTI0_IRQHandler(void)
{
    if (EXTI_GetITStatus(EXTI_Line0) != RESET) {
        EXTI_ClearITPendingBit(EXTI_Line0);
        // 延时消抖后处理按键
    }
}
```

### HAL 库 — 外部中断 (F407)

```c
// CubeMX: PA0 → GPIO_EXTI0, Rising Edge, Pull-Down

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == GPIO_PIN_0) {
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
    }
}
```

---

## 常用外设接线速查

```
OLED SSD1306 (I2C):   SCL=PB6, SDA=PB7, 地址=0x3C
OLED SSD1306 (SPI):   SCK=PA5, MOSI=PA7, CS=PA4, DC=PA3, RST=PA2
W25Q64 (SPI):         SCK=PA5, MISO=PA6, MOSI=PA7, CS=PA4
DS18B20 (1-Wire):     DQ=PA1 (需外接 4.7K 上拉)
DHT11 (1-Wire):       DATA=PA1 (内置上拉)
HC-SR04 (超声波):     TRIG=PA0(Out_PP), ECHO=PA1(IN_FLOATING, 捕获)
ESP8266 (UART):       TX→RX(PA10), RX→TX(PA9), 3.3V 供电
NRF24L01 (SPI):       SCK=PA5, MISO=PA6, MOSI=PA7, CSN=PA4, CE=PA3, IRQ=PA2
```

---

## 编码规范

```c
// 1. 外设初始化前必须开时钟 (最常见错误!)
// 2. GPIO 配置完整填写所有字段 (HAL库 Init 前清零结构体)
// 3. 中断处理函数内不做耗时操作 (设标志位, main 循环处理)
// 4. DMA 缓冲区避免放在 CCM (F407, DMA 不可访问)
// 5. 共享变量加 volatile (ISR 与 main 之间)
// 6. SPI/I2C 操作前确认总线空闲
// 7. ADC 通道对应引脚必须配置为模拟输入 (AIN / ANALOG)
```

