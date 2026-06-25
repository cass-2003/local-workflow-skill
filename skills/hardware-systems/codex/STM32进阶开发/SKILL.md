---
name: STM32进阶开发
description: USB设备/主机、CAN总线通信、RTC实时时钟、看门狗、低功耗模式、Flash编程、SDIO/SD卡、FSMC/FMC外部存储器、以太网、摄像头DCMI。覆盖F103和F407。
disable-model-invocation: false
user-invocable: false
---

# STM32 进阶开发

---

## USB 通信

### USB 模式对比

```
F103: USB Full-Speed Device (12Mbps), 无 DMA
F407: USB OTG FS (12Mbps) + USB OTG HS (480Mbps, 需外部 PHY)

常用设备类:
  CDC  — 虚拟串口 (最简单, 免驱)
  HID  — 键盘/鼠标/自定义
  MSC  — U盘 (配合 Flash/SD卡)
  DFU  — 固件升级
```

### HAL 库 — USB CDC 虚拟串口 (F103)

```c
// CubeMX: USB → Device → CDC, 自动生成 usbd_cdc_if.c

// 发送数据:
uint8_t buf[] = "USB CDC Hello\r\n";
CDC_Transmit_FS(buf, sizeof(buf) - 1);

// 接收数据 (在 usbd_cdc_if.c 中):
static int8_t CDC_Receive_FS(uint8_t *Buf, uint32_t *Len)
{
    // Buf 中有 *Len 字节数据
    // 处理接收到的数据...

    // 重新启动接收 (必须调用!)
    USBD_CDC_SetRxBuffer(&hUsbDeviceFS, &Buf[0]);
    USBD_CDC_ReceivePacket(&hUsbDeviceFS);
    return USBD_OK;
}
```

### HAL 库 — USB HID 自定义设备 (F407)

```c
// CubeMX: USB_OTG_FS → Device → Custom HID
// 修改报告描述符 (usbd_custom_hid_if.c):

__ALIGN_BEGIN static uint8_t CUSTOM_HID_ReportDesc_FS[25] __ALIGN_END = {
    0x06, 0x00, 0xFF,  // Usage Page (Vendor Defined)
    0x09, 0x01,        // Usage (Vendor Usage 1)
    0xA1, 0x01,        // Collection (Application)
    0x09, 0x01,        //   Usage (Vendor Usage 1)
    0x15, 0x00,        //   Logical Minimum (0)
    0x26, 0xFF, 0x00,  //   Logical Maximum (255)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x40,        //   Report Count (64)
    0x81, 0x02,        //   Input (Data,Variable)
    0x09, 0x01,        //   Usage (Vendor Usage 1)
    0x91, 0x02,        //   Output (Data,Variable)
    0xC0               // End Collection
};

// 发送: USBD_CUSTOM_HID_SendReport(&hUsbDeviceFS, data, 64);
```

---

## CAN 总线

### 基本概念

```
波特率 = APB1_CLK / (Prescaler × (BS1 + BS2 + 1))
F103: APB1 = 36MHz
F407: APB1 = 42MHz

常用波特率:
  500Kbps (F103): Prescaler=8, BS1=7, BS2=1 → 36M/(8×9)=500K
  1Mbps   (F103): Prescaler=4, BS1=7, BS2=1 → 36M/(4×9)=1M

引脚: F103 CAN1 → PA11(RX)/PA12(TX), 或 PB8(RX)/PB9(TX) 需重映射
      F407 CAN1 → PA11(RX)/PA12(TX), AF9
```

### 标准库 — CAN 初始化与收发 (F103)

```c
void CAN1_Init(void)
{
    CAN_InitTypeDef CAN_InitStruct;
    CAN_FilterInitTypeDef CAN_FilterStruct;

    RCC_APB1PeriphClockCmd(RCC_APB1Periph_CAN1, ENABLE);
    // GPIO PA11/PA12 配置 (略)

    CAN_DeInit(CAN1);
    CAN_InitStruct.CAN_TTCM = DISABLE;
    CAN_InitStruct.CAN_ABOM = ENABLE;   // 自动离线恢复
    CAN_InitStruct.CAN_AWUM = DISABLE;
    CAN_InitStruct.CAN_NART = DISABLE;  // 自动重传
    CAN_InitStruct.CAN_RFLM = DISABLE;
    CAN_InitStruct.CAN_TXFP = DISABLE;
    CAN_InitStruct.CAN_Mode = CAN_Mode_Normal;  // 或 CAN_Mode_LoopBack 调试用
    CAN_InitStruct.CAN_SJW = CAN_SJW_1tq;
    CAN_InitStruct.CAN_BS1 = CAN_BS1_7tq;
    CAN_InitStruct.CAN_BS2 = CAN_BS2_1tq;
    CAN_InitStruct.CAN_Prescaler = 8;   // 36M/(8×9) = 500Kbps
    CAN_Init(CAN1, &CAN_InitStruct);

    // 过滤器: 接收所有帧
    CAN_FilterStruct.CAN_FilterNumber = 0;
    CAN_FilterStruct.CAN_FilterMode = CAN_FilterMode_IdMask;
    CAN_FilterStruct.CAN_FilterScale = CAN_FilterScale_32bit;
    CAN_FilterStruct.CAN_FilterIdHigh = 0x0000;
    CAN_FilterStruct.CAN_FilterIdLow = 0x0000;
    CAN_FilterStruct.CAN_FilterMaskIdHigh = 0x0000;
    CAN_FilterStruct.CAN_FilterMaskIdLow = 0x0000;
    CAN_FilterStruct.CAN_FilterFIFOAssignment = CAN_Filter_FIFO0;
    CAN_FilterStruct.CAN_FilterActivation = ENABLE;
    CAN_FilterInit(&CAN_FilterStruct);
}

// 发送标准帧
void CAN1_Send(uint16_t id, uint8_t *data, uint8_t len)
{
    CanTxMsg tx;
    tx.StdId = id;
    tx.ExtId = 0;
    tx.IDE = CAN_Id_Standard;
    tx.RTR = CAN_RTR_Data;
    tx.DLC = len;
    for (uint8_t i = 0; i < len && i < 8; i++) tx.Data[i] = data[i];

    uint8_t mbox = CAN_Transmit(CAN1, &tx);
    uint32_t timeout = 0xFFFF;
    while (CAN_TransmitStatus(CAN1, mbox) != CAN_TxStatus_Ok && timeout--);
}

// 接收 (中断方式)
void USB_LP_CAN1_RX0_IRQHandler(void)  // F103 CAN1 RX0 中断
{
    CanRxMsg rx;
    CAN_Receive(CAN1, CAN_FIFO0, &rx);
    // 处理 rx.StdId, rx.Data, rx.DLC
}
```

---

## RTC 实时时钟

### F103 RTC (独立 32 位计数器)

```c
void RTC_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR | RCC_APB1Periph_BKP, ENABLE);
    PWR_BackupAccessCmd(ENABLE);  // 允许访问备份域

    if (BKP_ReadBackupRegister(BKP_DR1) != 0xA5A5) {
        // 首次配置
        RCC_LSEConfig(RCC_LSE_ON);
        while (RCC_GetFlagStatus(RCC_FLAG_LSERDY) == RESET);  // 等待 LSE 就绪

        RCC_RTCCLKConfig(RCC_RTCCLKSource_LSE);  // 32.768kHz
        RCC_RTCCLKCmd(ENABLE);
        RTC_WaitForSynchro();
        RTC_WaitForLastTask();

        RTC_SetPrescaler(32767);  // 32768-1 → 1Hz
        RTC_WaitForLastTask();

        // 设置初始时间 (Unix 时间戳)
        RTC_SetCounter(1710000000);  // 2024-03-09
        RTC_WaitForLastTask();

        BKP_WriteBackupRegister(BKP_DR1, 0xA5A5);
    } else {
        RTC_WaitForSynchro();
    }
}

uint32_t RTC_GetUnixTime(void) { return RTC_GetCounter(); }
```

### F407 RTC (日历模式, 带闹钟)

```c
// HAL 库
RTC_TimeTypeDef sTime = {0};
RTC_DateTypeDef sDate = {0};

// 设置时间
sTime.Hours = 14;
sTime.Minutes = 30;
sTime.Seconds = 0;
HAL_RTC_SetTime(&hrtc, &sTime, RTC_FORMAT_BIN);

sDate.Year = 24;   // 2024
sDate.Month = RTC_MONTH_MARCH;
sDate.Date = 14;
sDate.WeekDay = RTC_WEEKDAY_THURSDAY;
HAL_RTC_SetDate(&hrtc, &sDate, RTC_FORMAT_BIN);

// 读取时间
HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
HAL_RTC_GetDate(&hrtc, &sDate, RTC_FORMAT_BIN);  // 必须在 GetTime 之后调用!
```

---

## 看门狗

### IWDG (独立看门狗, LSI 驱动, 40kHz)

```c
// 标准库 F103
void IWDG_Init(uint16_t ms)
{
    IWDG_WriteAccessCmd(IWDG_WriteAccess_Enable);
    IWDG_SetPrescaler(IWDG_Prescaler_64);  // 40K/64 = 625Hz
    IWDG_SetReload(ms * 625 / 1000);       // 重载值
    IWDG_ReloadCounter();
    IWDG_Enable();  // 启动后不可关闭! 只能复位
}

// 在 main 循环中定期喂狗:
IWDG_ReloadCounter();

// HAL 库
HAL_IWDG_Refresh(&hiwdg);
```

### WWDG (窗口看门狗, 可设喂狗窗口)

```c
// 窗口看门狗: 必须在指定时间窗口内喂狗, 过早过晚都复位
// 适合检测程序流程异常

// HAL 库
HAL_WWDG_Refresh(&hwwdg);

// 窗口看门狗早期唤醒中断 (可用于紧急保存数据)
void HAL_WWDG_EarlyWakeupCallback(WWDG_HandleTypeDef *hwwdg)
{
    // 即将复位, 保存关键数据到 Flash/BKP
}
```

---

## 低功耗模式

```
功耗从高到低:
  Run → Sleep → Stop → Standby

Sleep:  CPU 停, 外设继续, 任何中断唤醒, 唤醒最快
Stop:   CPU+外设停, HSE/PLL 关, SRAM/寄存器保留, EXTI 唤醒, 需重配时钟
Standby: 全部关, 仅 RTC/IWDG/WKUP 运行, 唤醒=复位, 功耗最低 (μA级)
```

### 进入 Stop 模式 + RTC 唤醒 (HAL)

```c
// 进入 Stop 模式
void Enter_Stop_Mode(void)
{
    // 配置 RTC 闹钟唤醒 (5秒后)
    RTC_AlarmTypeDef sAlarm = {0};
    HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
    sAlarm.AlarmTime.Seconds = (sTime.Seconds + 5) % 60;
    sAlarm.Alarm = RTC_ALARM_A;
    HAL_RTC_SetAlarm_IT(&hrtc, &sAlarm, RTC_FORMAT_BIN);

    HAL_SuspendTick();
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);

    // --- 唤醒后从这里继续 ---
    SystemClock_Config();  // 必须重新配置时钟! (Stop 模式退出后 HSI 运行)
    HAL_ResumeTick();
}
```

### 进入 Standby 模式 + WKUP 引脚唤醒

```c
// Standby 唤醒后等效复位, 从 main() 重新开始
// 唤醒源: WKUP 引脚 (PA0) 上升沿 / RTC 闹钟 / IWDG

void Enter_Standby(void)
{
    __HAL_RCC_PWR_CLK_ENABLE();
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);  // PA0
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    HAL_PWR_EnterSTANDBYMode();
    // 不会执行到这里
}

// 判断是否从 Standby 唤醒:
if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB)) {
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
    // 从 Standby 唤醒, 恢复上下文
}
```

---

## 内部 Flash 编程

```c
// F103: 页大小 1K(小/中密度) 或 2K(大/超大密度)
// F407: 扇区大小 16K×4 + 64K×1 + 128K×7

// 标准库 — Flash 写入 (F103)
#define FLASH_SAVE_ADDR  0x0803F800  // 最后一页 (256K 芯片)

void Flash_Write(uint32_t addr, uint16_t *data, uint16_t len)
{
    FLASH_Unlock();
    FLASH_ErasePage(addr);  // 写前必须擦除!
    for (uint16_t i = 0; i < len; i++) {
        FLASH_ProgramHalfWord(addr + i * 2, data[i]);
    }
    FLASH_Lock();
}

void Flash_Read(uint32_t addr, uint16_t *data, uint16_t len)
{
    for (uint16_t i = 0; i < len; i++) {
        data[i] = *(volatile uint16_t *)(addr + i * 2);
    }
}

// HAL 库 — Flash 写入 (F407, 需指定 Sector)
HAL_FLASH_Unlock();
FLASH_EraseInitTypeDef erase;
erase.TypeErase = FLASH_TYPEERASE_SECTORS;
erase.Sector = FLASH_SECTOR_11;  // 最后一个扇区
erase.NbSectors = 1;
erase.VoltageRange = FLASH_VOLTAGE_RANGE_3;
uint32_t error;
HAL_FLASHEx_Erase(&erase, &error);

HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, 0x080E0000, 0x12345678);
HAL_FLASH_Lock();
```

### IAP (In-Application Programming) 架构

```
Flash 分区:
  0x08000000 ┌──────────────┐
             │ Bootloader   │ 16K-32K
  0x08008000 ├──────────────┤
             │ Application  │ 剩余空间
             └──────────────┘

Bootloader 流程:
  1. 上电 → 检查是否需要升级 (按键/标志位/串口命令)
  2. 需要升级 → 接收新固件 (UART/USB/CAN) → 写入 App 区
  3. 不需要 → 跳转到 App

跳转代码:
  typedef void (*AppFunc)(void);
  uint32_t app_addr = 0x08008000;
  uint32_t app_sp = *(volatile uint32_t *)app_addr;
  uint32_t app_entry = *(volatile uint32_t *)(app_addr + 4);
  __set_MSP(app_sp);
  ((AppFunc)app_entry)();

App 工程设置:
  Keil → Options → Target → IROM1 Start=0x08008000
  代码中: SCB->VTOR = 0x08008000;  // 中断向量表偏移
```

---

## SDIO / SD 卡

### HAL 库 — SDIO + FATFS (F407)

```c
// CubeMX: SDIO → SD 4-bit, DMA, 挂载 FATFS 中间件

FATFS fs;
FIL fp;
FRESULT res;
UINT bw;

// 挂载
res = f_mount(&fs, "0:", 1);
if (res == FR_NO_FILESYSTEM) {
    uint8_t work[4096];
    f_mkfs("0:", FM_FAT32, 0, work, sizeof(work));
    f_mount(&fs, "0:", 1);
}

// 写文件
res = f_open(&fp, "0:/log.txt", FA_WRITE | FA_CREATE_ALWAYS);
if (res == FR_OK) {
    char buf[] = "Hello FATFS\r\n";
    f_write(&fp, buf, strlen(buf), &bw);
    f_close(&fp);
}

// 读文件
res = f_open(&fp, "0:/log.txt", FA_READ);
if (res == FR_OK) {
    char rbuf[64];
    f_read(&fp, rbuf, sizeof(rbuf), &bw);
    f_close(&fp);
}

// SPI 模式 SD 卡 (F103, 无 SDIO 外设时):
// 使用 SPI1 + FATFS 的 user_diskio.c 自行实现底层读写
```

---

## FSMC / FMC 外部存储器

### FSMC 驱动 LCD (F103, 8080 并口)

```c
// FSMC Bank1 NOR/SRAM → LCD 控制器 (ILI9341/ST7789 等)
// RS(A16) 区分命令/数据:
//   命令地址: 0x60000000 (A16=0)
//   数据地址: 0x60020000 (A16=1, 因为 A16 对应 bit17 of byte addr)

#define LCD_CMD  (*(volatile uint16_t *)0x60000000)
#define LCD_DATA (*(volatile uint16_t *)0x60020000)

void LCD_WriteCmd(uint16_t cmd)  { LCD_CMD = cmd; }
void LCD_WriteData(uint16_t data) { LCD_DATA = data; }

// 填充矩形
void LCD_Fill(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2, uint16_t color)
{
    LCD_WriteCmd(0x2A);  // Column Address Set
    LCD_WriteData(x1 >> 8); LCD_WriteData(x1 & 0xFF);
    LCD_WriteData(x2 >> 8); LCD_WriteData(x2 & 0xFF);

    LCD_WriteCmd(0x2B);  // Row Address Set
    LCD_WriteData(y1 >> 8); LCD_WriteData(y1 & 0xFF);
    LCD_WriteData(y2 >> 8); LCD_WriteData(y2 & 0xFF);

    LCD_WriteCmd(0x2C);  // Memory Write
    uint32_t total = (uint32_t)(x2 - x1 + 1) * (y2 - y1 + 1);
    while (total--) LCD_DATA = color;
}
```

### FMC 外接 SRAM (F407)

```c
// IS62WV51216 (1MB SRAM) 接 FMC Bank1 SRAM3
// 基地址: 0x68000000

#define SRAM_BASE_ADDR  0x68000000
#define SRAM_SIZE       (1024 * 1024)  // 1MB

// 直接指针访问
volatile uint16_t *sram = (volatile uint16_t *)SRAM_BASE_ADDR;
sram[0] = 0x1234;
uint16_t val = sram[0];

// 可将堆/栈/大数组放到外部 SRAM (修改启动文件或分散加载文件)
```

---

## 以太网 (仅 F407)

### LWIP + ETH (HAL)

```c
// CubeMX: ETH → RMII Mode, 启用 LWIP 中间件
// 引脚: RMII 模式约需 9 个引脚 (PA1,PA2,PA7,PB11-13,PC1,PC4,PC5)

// 配置 IP (LWIP → General Settings)
// IP: 192.168.1.100 / 255.255.255.0 / 192.168.1.1

// TCP Server 示例
struct netconn *conn, *newconn;
conn = netconn_new(NETCONN_TCP);
netconn_bind(conn, IP_ADDR_ANY, 8080);
netconn_listen(conn);

while (1) {
    netconn_accept(conn, &newconn);
    struct netbuf *buf;
    netconn_recv(newconn, &buf);
    // 处理接收数据: netbuf_data(buf, &data, &len);
    netconn_write(newconn, "HTTP/1.1 200 OK\r\n\r\nHello", 24, NETCONN_COPY);
    netbuf_delete(buf);
    netconn_close(newconn);
    netconn_delete(newconn);
}
```

---

## DCMI 摄像头 (仅 F407)

```c
// OV2640 + DCMI + DMA
// CubeMX: DCMI → 8-bit data, VSYNC/HSYNC/PIXCLK, DMA

// 通过 SCCB (类 I2C) 配置 OV2640 寄存器
void OV2640_Init(void)
{
    // 复位
    SCCB_WriteReg(0xFF, 0x01);
    SCCB_WriteReg(0x12, 0x80);  // 软件复位
    HAL_Delay(10);

    // 配置输出 JPEG 320x240
    // ... 大量寄存器配置 (通常用数组批量写入)
}

// 拍照
uint32_t frame_buf[320 * 240 / 2];  // 注意: 不要放 CCM!
HAL_DCMI_Start_DMA(&hdcmi, DCMI_MODE_SNAPSHOT,
                   (uint32_t)frame_buf, 320 * 240 / 2);

// 帧完成回调
void HAL_DCMI_FrameEventCallback(DCMI_HandleTypeDef *hdcmi)
{
    HAL_DCMI_Stop(hdcmi);
    // frame_buf 中有 JPEG 数据
}
```

---

## 调试经验清单

```
问题: USB 枚举失败
  → 检查 48MHz USB 时钟 (F103: PLL→72M, USB 预分频 1.5 → 48M)
  → F407: PLLQ 输出必须为 48MHz
  → 检查 DP(PA12) 上拉电阻 1.5K (部分开发板已内置)

问题: CAN 无法通信
  → 必须至少两个节点! 单节点用 Loopback 模式测试
  → 检查终端电阻 120Ω (总线两端各一个)
  → 检查 CAN 收发器 (TJA1050) 供电和接线

问题: SDIO 初始化失败
  → SD 卡供电 3.3V, 不可用 5V
  → 检查 CMD/CLK/DAT0-3 上拉 (47K-100K)
  → 降低 SDIO 时钟频率测试

问题: FSMC LCD 花屏
  → 检查读写时序参数 (AddressSetupTime, DataSetupTime)
  → 确认 LCD 控制器型号, 初始化序列是否匹配
  → A16 地址偏移计算: 数据线 16bit 时, A16 对应地址偏移 0x20000

问题: Stop 模式唤醒后外设异常
  → 唤醒后必须重新调用 SystemClock_Config()
  → 外设时钟可能需要重新使能
  → 检查 GPIO 状态是否保留

问题: Flash 写入数据丢失
  → 写前必须先擦除整页/整扇区!
  → 写入期间不可断电 (考虑双 bank 方案)
  → F407 注意 VoltageRange 与实际供电匹配
```

---

## 推荐学习路径

```
阶段 1 (2-4周):
  LED → 按键 → USART printf → TIM 定时器 → PWM 呼吸灯 → EXTI 中断

阶段 2 (2-4周):
  ADC 电压采集 → DMA → SPI(W25Q/OLED) → I2C(传感器) → 看门狗

阶段 3 (4-6周):
  USB CDC → RTC → 低功耗 → Flash 存储 → SDIO+FATFS

阶段 4 (选修):
  CAN 通信 → FSMC LCD → DCMI 摄像头 → 以太网 LWIP → FreeRTOS
```

