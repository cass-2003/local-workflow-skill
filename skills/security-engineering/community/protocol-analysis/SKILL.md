---
name: protocol-analysis
description: Protocol Analysis实战排障版 - 授权抓包、互操作联调、协议兼容、pcap/HAR证据、Wireshark/tcpdump/mitmproxy/Charles分层定位、TLS1.3/QUIC/HTTP3、HTTP/2、WebSocket/gRPC/MQTT、Protobuf/Avro/JSON/二进制协议、证书钉扎、mTLS、签名规范化、重放窗口、移动端代理配置、日志脱敏和防护验证。只服务授权安全测试、抓包排障、协议兼容性、CTF/教育与防御验证。
---

# 协议分析

> 定位：协议分析（protocol-analysis，兼容 slug: prot）把“抓包看看”收敛为授权清楚、入口可复现、pcap/HAR/日志可追溯、分层结论可验证、风险可交接的协议排障闭环。
> 铁律：未授权不抓包、不重放、不改写；未保留原始证据不下结论；未分清 DNS/TCP/UDP/TLS/QUIC/HTTP/序列化/业务层不改协议；证书钉扎、mTLS、签名、重放防护只做授权验证和风险说明。

## 快速总则：授权 / 环境 / 入口 / 证据

1. 授权先行：确认资产、账号、环境、时间窗、域名/IP/端口、第三方边界、允许动作、禁止动作、数据范围、脱敏规则；授权不清只列缺口并停止采集。
2. 环境定格：记录客户端/服务端版本、平台、系统、浏览器/WebView、SDK、代理、证书、DNS、网络、地域、灰度、时间同步、工具链版本。
3. 入口最小化：先锁定一个可重复入口，写清输入、动作、预期、登录态、前序接口、重试链路、失败码和服务端 trace id。
4. 原始证据优先：保留 pcap、HAR、tcpdump/dumpcap 命令、capture filter、display filter、flow filter、ring buffer 参数、丢包计数、mitmproxy/Charles session、请求响应、日志、trace id、证书指纹和时间线。
5. 代理模式选择树：能直连复现先直连+pcap；需看 HTTP 明文再用系统代理/显式代理；移动端先核 Wi-Fi/蜂窝/系统代理/VPN/MDM/证书信任；遇证书钉扎、mTLS、HTTP/3 或企业策略阻塞只记录阻塞证据、服务端日志和替代观测，不写绕过。
6. 分层归因：按 DNS → TCP/UDP → TLS1.3/mTLS/QUIC → HTTP/2/HTTP/3 → WebSocket/gRPC/MQTT → 编码/压缩/序列化/加密 → 签名/重放/业务校验逐层排除。
7. 成功/失败对照：至少一组成功样本和失败样本；兼容性问题按版本、平台、工具链、运行环境、代理/CDN/网关、IPv4/IPv6 做 diff。
8. 敏感数据最小化：Authorization、Cookie、token、nonce、签名密钥、证书私钥、手机号、设备号、业务敏感字段输出前脱敏；保留可关联证据编号。
9. 结论分级：已确认、部分确认、无法验证、需专项授权分开写；不得把单包现象、工具猜测或第三方经验写成事实。
10. 风险分级：按影响面、可复现性、数据敏感度、是否生产、是否第三方、修复/回滚成本、可观测缺口给出高/中/低和证据依据。

## 工程门禁与低级错禁止

1. 未拿到授权范围、样本编号、入口步骤、环境矩阵、原始证据存放位置和脱敏规则，不进入抓包、重放、改写或报告定论。
2. 未保留原始 pcap/HAR/session、过滤条件、工具版本、时间同步方式和服务端 trace，不允许只凭截图、控制台复制文本或单条日志下结论。
3. 未完成成功/失败差分样本，不改签名、Header、字段顺序、压缩、序列化、证书或网关配置。
4. 未核对时钟漂移、地域/CDN、灰度、版本、账号态、网络、代理、缓存、Alt-Svc、DNS/DoH/DoT，不把偶发现象写成协议变更。
5. 未验证 nonce、timestamp、event id、Idempotency-Key、重放窗口、频率限制和终态幂等，不做自动化回放或批量样本。
6. 未确认数据隔离、回滚影响和低频边界，生产、第三方 Webhook、支付、账号、资金、隐私接口不得重放或改写。
7. 未做脱敏扫描，不把 Authorization、Cookie、token、签名密钥、证书、手机号、设备号、精确定位或业务敏感字段贴进报告、issue、日志或聊天。
8. 未把结论绑定到证据编号、文件名、时间点、trace id、工具版本和复现实验，不宣称“已定位”“协议就是这样”。

## 场景执行卡

### 1. 授权抓包与证据建档

- 适用：联调失败、线上只读排障、协议兼容验证、授权安全测试、CTF/教育样本分析。
- 输入：授权范围、目标域名/IP/端口、账号态、入口路径、允许采集字段、脱敏规则、影响窗口。
- 动作：客户端侧抓 pcap/HAR，必要时补网关侧和服务端侧日志；长时段优先 dumpcap ring buffer，记录接口、snaplen、文件轮转大小/数量、capture filter、display filter、flow filter、丢包计数、工具版本、代理证书状态、开始结束时间和客户端动作。
- 三层过滤：capture filter 只做采集前降噪且保留原始条件；display filter 只做 Wireshark/tshark 复核视图；flow filter 按五元组、stream id、trace id、账号态或样本编号收敛单条链路，三者不得混写。
- 证据：原始 pcap/HAR/session 文件名、样本编号、时间线、成功/失败对照、trace id、证书指纹、脱敏规则。
- 兜底：无法授权、无法脱敏或触及第三方生产数据时停止采集，只列替代观测点和需确认项。

### 2. HTTP/2、HTTP/3、QUIC 与 API 兼容

- 适用：状态码异常、Header/Body 不兼容、网关/代理差异、旧客户端失效、HTTP/3 降级。
- 动作：比较 method、path、query、header、cookie、body、content-type、content-encoding、cache、redirect、CORS、连接复用；HTTP/2 查伪头、stream、HPACK、gRPC status；HTTP/3 查 QUIC 连接 ID、UDP 可达性、Alt-Svc、0-RTT、QPACK、连接迁移和 HTTP/2 回退。
- 现象映射：ALPN mismatch 多查客户端/网关协商；UDP blocked 多查网络/防火墙/运营商；Alt-Svc stale 多查缓存和回滚后入口；0-RTT rejected 多查服务端策略和幂等；QPACK/HPACK 差异多查工具版本、代理改写和 Header 大小限制。
- 验证：直连、代理、CDN、移动网络、Wi-Fi、不同浏览器/SDK/运行环境对照；记录版本、错误码语义和回滚风险。
- 兜底：只看到 4xx/5xx 不直接判签名或服务端 bug，先核权限、缓存、灰度、旧 token、代理改写和业务策略。

### 3. TLS1.3、证书、证书钉扎与 mTLS

- 适用：握手失败、证书链异常、SNI/ALPN 不匹配、企业代理、证书轮换、客户端证书、证书钉扎阻塞。
- 动作：核 SNI、ALPN、TLS 版本、Cipher、证书链、SAN、有效期、OCSP/CRL、系统信任库、企业 CA、代理证书、客户端证书、时钟；TLS1.3 关注 session resumption、0-RTT、key update 与中间盒兼容。
- 现象映射：证书链不完整查中间证书和网关配置；客户端证书拒绝查证书选择、过期、吊销、网关透传和服务端映射；企业代理异常查信任库、SNI/ALPN、证书替换和策略例外。
- 证据：握手摘要、证书指纹、客户端错误码、服务端日志、pcap 时间点、代理证书配置、移动端系统版本。
- 边界：不提供证书钉扎绕过、私钥提取或未授权拦截实现细节；移动端阻塞转 msec，二进制层证据转 rev。

### 4. WebSocket、gRPC、MQTT 与流式链路

- 适用：实时消息丢失、订阅失败、心跳断线、gRPC streaming 卡住、MQTT QoS 异常、SSE/流式响应中断。
- 动作：还原握手、认证、metadata、心跳、ack、序列号、订阅、重连、恢复、deadline、backpressure、取消、消息边界；gRPC 查 HTTP/2 stream、status、trailers、Protobuf schema；MQTT 查 connect/subscribe/publish/puback、QoS、retain、session。
- gRPC/Protobuf 深化：schema 来源顺序按 reflection → proto → protoset；核 proto2/proto3 optional、oneof、reserved、unknown fields、JSON mapping、字段号/类型、默认值、grpc-status、trailers、deadline、metadata 与 schema 漂移验收。
- gRPC 验收：grpcurl 能列服务、describe 方法、带 metadata 调最小成功/失败样本；buf lint 和 buf breaking 输出纳入证据，失败项需关联 proto/protoset 版本和消费者影响。
- SSE/流式：核代理缓冲、空闲超时、分块边界、取消语义、压缩策略和客户端解析策略。
- 证据：连接状态机、关键帧时间线、断线前后 pcap、服务端 trace、客户端日志、成功/失败样本。
- 兜底：只抓到单帧不得下长连接结论，必须补完整生命周期或标“无法验证”。

### 5. TCP、UDP、DNS、弱网与移动端代理配置

- 适用：偶发超时、重传、RST、丢包、DNS 解析差异、UDP 不通、移动端抓包失败、弱网兼容。
- 动作：TCP 看三次握手、窗口、MSS、重传、乱序、RST/FIN、拥塞、半包/粘包表现；UDP 看分片、MTU、NAT 超时、QUIC 阻断；DNS 看 A/AAAA、TTL、EDNS、DoH/DoT、IPv4/IPv6、缓存、地域调度。
- 移动端：记录真机/模拟器、系统版本、Wi-Fi/蜂窝、代理 PAC/手动代理、证书安装位置、系统 WebView、VPN/MDM、私有 DNS、厂商 ROM 差异。
- 输出：失败层级、可复现条件、网络/运维/移动安全联动项。

### 6. 编码、压缩、序列化、二进制协议与加密识别

- 适用：响应乱码、Body 不可读、字段缺失、二进制协议解析失败、schema 漂移。
- 动作：先查 content-type、content-encoding、magic bytes、长度字段、帧头、字符集；区分 JSON、Protobuf、Avro、gRPC frame、gzip、br、zstd、Base64、二进制协议、业务加密、签名。
- 二进制排障：识别 magic bytes、帧头、长度前缀、序号、flags、endianness、varint、TLV、CRC/checksum、版本协商、保留字段、未知扩展、截断、粘包、半包和重传影响。
- Kaitai 风格模板：先写 magic/version/length/flags/endianness/checksum 的字段假设、偏移和样本编号，再用成功/失败 fixtures 验证长度、校验和、保留位与版本兼容；未知字段只标未知，不猜业务语义。
- 验证：同样本在 Wireshark、mitmproxy、Charles、客户端 SDK、服务端日志中对照；确认 schema 版本、字段默认值、未知字段策略、字段号/类型兼容。
- 边界：不输出凭证窃取、破坏性解密或规避安全控制路径；私有格式深度还原转 rev。

### 7. 签名规范化、参数来源与重放窗口

- 适用：401/403、nonce/时间戳错误、签名不一致、幂等失败、请求顺序敏感、Webhook/Event 验签。
- 动作：标记字段来源于 URL、Header、Cookie、Body、前序响应、缓存、设备环境或服务端下发；核编码、排序、大小写、空值、数组、JSON canonicalization、换行、字符集、时钟漂移、重试间隔、Idempotency-Key。
- 验证：仅在授权测试范围做最小重放；确认 nonce、timestamp、event id、签名原始 body、重放窗口、终态幂等和频率限制。
- 重放边界：隔离环境优先；生产只做授权低频最小样本和只读验证；第三方 Webhook、支付、账号、资金、隐私接口必须升级授权；无法保证幂等终态、回滚影响、频率边界或数据隔离时停止。
- 输出：参数来源图、规范化差异、重放边界、无法复验项、API 契约或安全联动建议。

### 8. 发布、回滚、观测与防护验证

- 适用：协议迁移、网关切换、证书轮换、字段升级、SDK 发布、灰度回滚、防护策略验证。
- 动作：建立版本/平台/工具链/运行环境/代理/CDN/网关矩阵；比较字段、Header、错误码、超时、证书、日志脱敏、告警和旧客户端行为。
- 验证：发布前最小 pcap/HAR 冒烟，灰度期按 version/region/tenant 观测，回滚后复测旧入口和缓存/Alt-Svc/证书状态。
- 联动：观测证据和 incident timeline 转 obs；测试矩阵转 tst；代码改动最终转 aud。

### 9. 设备指纹、验证码、风控与保护机制边界

- 适用：请求被风控、验证码触发、设备指纹不一致、反自动化、账号风险、访问限制、证书钉扎或运行环境校验阻塞。
- 动作：只做授权范围内的现象归因和配置核查；记录账号类型、设备/浏览器指纹字段、IP/地域、时间窗、频率、版本、灰度、验证码类型、风控错误码、服务端 trace、官方测试环境或白名单能力。
- 边界：不提供验证码识别/绕过、风控规避、设备伪造、批量账号、证书钉扎绕过、Root/Jailbreak 绕过、反调试对抗或隐藏自动化痕迹的实现步骤。
- 替代：优先走官方沙箱、测试账号、调试开关、白名单、服务端日志、风险策略解释、低频只读样本、人工验证链路和安全团队确认。
- 输出：保护机制归因、授权缺口、可观测证据、不能继续的原因、可交给 msec/wsec/rev 的专项边界。

### 10. 抓包复现实验与报告证据链

- 适用：需要把协议结论交给开发、测试、安全、运维、第三方或审计复核。
- 动作：为每个结论建立“假设 → 样本编号 → 采集方法 → 差分字段 → 复现实验 → 结果 → 剩余疑点”的证据链；同一问题至少保留直连与代理、客户端与服务端、成功与失败两组对照。
- 差分要求：请求字段、Header、Cookie、Body、签名输入、编码/压缩、时间戳、nonce、设备字段、地域、版本、网络、DNS、TLS/ALPN、HTTP2/3、网关/CDN、业务错误码逐项标出相同/不同/未知。
- 复验要求：报告中的每个命令、过滤条件、样本文件、trace id、时间点和脱敏映射都能由另一人复跑；无法复跑时标“证据不足”或“只能部分确认”。
- 输出：证据索引、复现实验步骤、差分表、结论等级、风险等级、脱敏说明、下一步联动技能和停止条件。

## 互操作测试矩阵

- 最小维度：客户端/SDK 版本、平台/系统/WebView、浏览器/运行时、网络类型、IPv4/IPv6、DNS/DoH/DoT、代理/CDN/网关、直连/代理、HTTP/2/HTTP/3、TLS/QUIC、证书链/mTLS、序列化、压缩算法、认证方式、错误码语义、回滚路径。
- 最小样本：每个高风险维度至少一组成功/失败对照；旧客户端、旧 SDK、旧网关、缓存、Alt-Svc、证书轮换窗口必须纳入回归。
- 验收口径：同一入口的请求字段、Header、Body、状态码、业务错误码、超时、重试、trace id、日志脱敏和回滚后表现一致或差异有明确契约。
- 输出格式：矩阵行记录环境、入口、样本编号、证据文件、关键差异、影响等级、是否已复验、需联动技能。

## 工具链交叉验证

- Wireshark/tcpdump：适合原始包、时序、重传、TLS/QUIC/HTTP2/3 解码能力核查；必须记录版本、过滤条件、接口和时间同步。
- mitmproxy/Charles：适合授权代理、HTTP/HAR/session、证书和 Header/Body 对照；mitmproxy addon 只能用于授权观测、脱敏、导出和证据编号，不用于未授权拦截、改写、批量重放或规避检测；遇到证书钉扎、mTLS、HTTP/3 或企业代理时可能只能给阻塞证据。
- curl/OpenSSL/nghttp2/grpcurl：适合协议协商、证书链、ALPN、HTTP/2/gRPC 基线对照；版本不支持目标协议时不得据此下结论。
- tshark/Buf CI：pcap→tshark JSON 用于可复核字段抽取，fixtures 保存最小成功/失败样本、过滤条件和脱敏映射；Buf CI 输出必须包含 buf lint、buf breaking、proto/protoset 版本和消费者兼容结论。
- 交叉原则：工具输出冲突时优先保留原始 pcap 与服务端日志，再解释工具版本、解码插件、代理改写、压缩/解压和采样差异。

## 协议文档化与风险分级交付物

- 字段字典：字段名、来源、位置、类型、编码、是否签名、是否敏感、默认值、兼容策略、样本编号。
- 状态机与时序：连接、认证、订阅、请求、响应、重试、ack、心跳、断线、恢复、取消、超时和终态。
- 错误码表：协议状态码、业务错误码、grpc-status/trailers、客户端错误、服务端日志、用户可见文案和回滚行为。
- 兼容性约束：版本、平台、代理/CDN/网关、HTTP2/3、TLS/QUIC、序列化、压缩、证书和旧客户端承诺。
- 隐私脱敏表：敏感字段、脱敏规则、保留期限、证据存放位置、访问边界、第三方或跨境风险。
- 风险等级：影响面、可复现性、数据敏感度、安全边界、生产影响、修复优先级、验证缺口和回滚成本。

## 高频坑 / 防遗漏

### 高频坑

1. 授权边界未写清就抓生产流量。
2. 只留截图，不保留 pcap/HAR/session、过滤条件和时间线。
3. 单个失败样本就改协议，没有成功/失败对照。
4. 把 DNS、TCP、TLS、HTTP、签名、业务错误混成“接口不通”。
5. 把 Protobuf、Avro、gzip、Base64、zstd、br 或二进制协议误判为加密。
6. 忽略 HTTP/2 伪头、stream、gRPC trailers、deadline 和 status 映射。
7. 忽略 HTTP/3/QUIC 的 UDP 可达性、Alt-Svc 缓存、0-RTT、连接迁移和降级。
8. 证书钉扎、mTLS 或企业 CA 阻塞时直接写绕过步骤。
9. 签名只比字段值，不比编码、排序、空值、大小写、JSON 规范化和原始 body。
10. 重放验证不写 nonce、timestamp、event id、窗口和幂等结果。
11. tcpdump/Wireshark 时间与应用日志时钟不一致，导致时序误判。
12. 代理、CDN、网关或移动 WebView 改写 Header 后仍按直连结论修。
13. 日志未脱敏，把 token、Cookie、证书、个人信息贴进报告。
14. 协议升级只测新客户端，不测旧 SDK、旧网关、缓存、回滚路径。
15. 抓包工具版本不支持 HTTP/3/QUIC、zstd 或目标解码，却把“看不到”当协议事实。
16. 二进制协议半包/粘包、长度前缀或 endianness 错误被误判为业务失败。
17. Protobuf 字段号复用、reserved 缺失、oneof/optional 变更导致旧客户端解析错。
18. 移动端 DoH/私有 DNS 绕过系统代理，导致域名和目标 IP 误判。
19. 没核设备指纹、账号态、地域、频率、验证码和风控错误码，就把限制归因成签名或接口故障。
20. 未同步客户端、服务端、抓包机和日志系统时钟，导致 nonce/timestamp、重放窗口、TLS 证书有效期和 trace 对齐全部误判。
21. 只在本地网络、单版本、单账号调通，漏掉 CDN 地域、移动网络、旧 SDK、灰度策略、缓存和回滚路径。
22. 报告没有证据索引、样本编号、脱敏规则和复现实验，导致结论无法审计、无法交接、无法回归。

### 防遗漏清单

- 授权：资产、账号、时间窗、允许动作、禁止动作、第三方边界、脱敏规则是否齐全？
- 入口：复现步骤、版本、平台、网络、账号态、前序接口、时间线是否可复跑？
- 证据：pcap/HAR/session、dumpcap ring buffer、丢包计数、capture filter、display filter、flow filter、mitmproxy/Charles 版本、日志、trace id 是否互相对得上？
- 分层：DNS、TCP/UDP、TLS1.3/mTLS/QUIC、HTTP/2/3、WebSocket/gRPC/MQTT、序列化、签名、业务校验是否逐层排除？
- 互操作：客户端/SDK、平台、代理/CDN/网关、IPv4/IPv6、HTTP2/3、TLS/QUIC、证书、压缩、错误码和回滚路径是否有矩阵？
- 格式：JSON、Protobuf、Avro、二进制协议、编码、压缩、加密是否有识别依据？
- 长连接：握手、认证、心跳、ack、重连、订阅恢复、deadline、backpressure、超时是否覆盖？
- 兼容：版本、平台、工具链、运行环境、代理/CDN/网关、IPv4/IPv6、移动端 WebView 是否对照？
- 安全：权限、重放、证书、数据最小化、日志脱敏、防护验证、发布或回滚风险是否写清？
- 风控：设备指纹、验证码、账号态、地域、频率、风险错误码和官方测试能力是否只做授权归因，不写规避步骤？
- 复现：假设、差分样本、复现实验、证据索引、脱敏映射和停止条件是否能被第三方复核？

## 输出要求

1. slug 与任务边界：说明只处理授权协议分析、抓包排障、互操作联调、协议兼容、防护验证或 CTF/教育。
2. 授权与环境：资产范围、账号、版本、平台、工具链、网络、代理、证书、时间窗、脱敏规则。
3. 入口与复现：输入、动作、前序接口、成功/失败样本、时间线、trace id。
4. 原始证据：pcap/HAR/session、dumpcap ring buffer、capture filter、display filter、flow filter、丢包计数、tshark JSON、fixtures、请求响应、日志、证书/握手摘要。
5. 协议分层：DNS、TCP/UDP、TLS1.3/mTLS/QUIC、HTTP/2/3、WebSocket/gRPC/MQTT、序列化/编码/压缩/加密、签名/重放、业务层的排除结果。
6. 互操作矩阵：版本、平台、网络、代理/CDN/网关、HTTP2/3、TLS/QUIC、序列化、压缩、认证、错误码、回滚路径。
7. 关键结论：参数来源、签名规范化、时序、超时、重传、兼容性、权限/数据/安全影响、发布或回滚风险。
8. 协议交付物：字段字典、状态机、消息时序、错误码语义、隐私脱敏表、证据索引、风险分级。
9. 验证路径：如何复验、哪些已验证、哪些无法验证、还缺什么证据。
10. 联动技能：何时交给 rev、msec、wsec、api、obs、tst、aud 或对应开发技能。
11. 停止条件：授权不足、保护机制越界、生产幂等不可控、第三方/隐私/资金风险、无法脱敏、无法复跑时必须明确停止原因。

## 约束

- 只支持授权安全测试、抓包排障、协议兼容性、互操作联调、CTF/教育、防御验证；授权不清时停止并列证据缺口。
- 拒绝 DoS、批量撞库、恶意绕过、窃取凭证、隐蔽持久化、攻击第三方、未授权拦截、破坏性流量或数据破坏内容。
- 不提供证书钉扎绕过、Root/Jailbreak 绕过、反调试对抗、私钥/凭证提取、凭证解密、批量重放、批量滥用或规避检测实现细节。
- 不把安全保护机制当成默认要解除；只输出合法调试入口、风险归因、配置核查、服务端日志验证和替代观测路径。
- 不凭经验猜协议；结论必须绑定 pcap、HAR、Wireshark/tcpdump、mitmproxy/Charles、日志、代码调用链或官方文档证据。
- 不输出未脱敏 token、Cookie、证书私钥、个人信息、设备标识、业务敏感数据。
- 不用自动化批量回放替代单点证据闭环；重放仅限授权测试范围，并记录频率、数据和回滚影响。
- 生产、第三方 Webhook、支付、账号、资金、隐私接口的重放或改写必须升级授权；无法保证幂等、隔离、回滚或低频边界时停止。
- 涉代码改动、测试、发布、安全运营或深度逆向时必须切相邻技能并保留本技能证据链。
- 验证码、风控、设备指纹、反自动化和访问限制只做合规边界、策略归因、日志证据和官方测试路径；不得输出可用于规避检测或扩大访问能力的操作细节。
- 任何报告、样本、fixture、tshark JSON、HAR、Postman/cURL 片段都必须先脱敏；敏感原文只允许留在受控证据库并记录访问边界。

## 高频 Bug 反例库

- 反例 1：无授权抓包
  - 错法：只说“临时看一下生产流量”，没有资产、账号、时间窗、允许动作和数据范围。
  - 对法：先确认授权和脱敏规则；缺授权则停止并列待确认项。
  - 根因：协议证据不能建立在越界采集上。
- 反例 2：只留截图不留原始证据
  - 错法：报告只有 Wireshark 截图，无法复核过滤条件和完整包序。
  - 对法：保存 pcap/HAR/session、过滤表达式、样本编号和工具版本。
  - 根因：截图是摘要，不是可复核证据。
- 反例 3：403 直接判签名错
  - 错法：忽略权限、登录态、灰度、频控、区域、旧 token 和前序接口。
  - 对法：先分层排除认证、授权、环境、参数、时序和业务策略。
  - 根因：状态码是现象，不是根因。
- 反例 4：把 Protobuf、Avro 或压缩当加密
  - 错法：看到二进制 body、zstd/br/gzip 或 Base64 就追加密问题。
  - 对法：先查 content-type、content-encoding、帧头、schema、字段号、默认值和未知字段策略。
  - 根因：编码、压缩、序列化、加密属于不同层。
- 反例 5：HTTP/3 失败只改 API
  - 错法：忽略 QUIC/UDP 阻断、Alt-Svc 缓存、0-RTT、连接迁移和降级路径。
  - 对法：对照 HTTP/2 与 HTTP/3，记录 QUIC 握手、UDP 可达性和回退行为。
  - 根因：传输层变化会伪装成应用层失败。
- 反例 6：TLS1.3 握手失败只换证书
  - 错法：不查 SNI、ALPN、Cipher、时钟、OCSP、企业代理和系统信任库。
  - 对法：输出握手摘要、证书链、客户端错误码、服务端日志和环境差异。
  - 根因：TLS 失败常由协商、信任链和中间层共同触发。
- 反例 7：证书钉扎阻塞就写绕过
  - 错法：为了抓包直接给绕过证书钉扎或提取密钥的步骤。
  - 对法：写阻塞原因、授权要求、替代证据、服务端日志验证和移动安全联动。
  - 根因：保护机制验证不能转成可滥用绕过手册。
- 反例 8：mTLS 只看服务端证书
  - 错法：忽略客户端证书、证书选择、过期、信任链和网关透传。
  - 对法：核双向证书链、客户端身份、网关策略、日志和证书轮换窗口。
  - 根因：mTLS 是双向身份协议，单看服务端不完整。
- 反例 9：签名只拼字段值
  - 错法：不比 URL 编码、排序、空值、大小写、数组、换行和 JSON canonicalization。
  - 对法：按原始 body、规范化规则、字符集、前序参数来源逐项 diff。
  - 根因：签名失败高频来自规范化差异而非密钥错误。
- 反例 10：Webhook 重放窗口漏查
  - 错法：签名正确就认为事件安全，旧请求可重复入账。
  - 对法：验证 timestamp、nonce/event id、窗口、幂等、终态重放和补偿查询。
  - 根因：签名证明来源，不证明新鲜性和一次性。
- 反例 11：WebSocket 只看一帧
  - 错法：只分析业务消息，不抓握手、认证、心跳、ack、重连和订阅恢复。
  - 对法：抓完整生命周期并输出状态机和关键帧时间线。
  - 根因：长连接可靠性由时序和状态机决定。
- 反例 12：gRPC 错误只看 HTTP 状态
  - 错法：HTTP 200 就认为成功，忽略 grpc-status、trailers、deadline 和 metadata。
  - 对法：同时读取 HTTP/2 stream、gRPC status、message、deadline 和服务端 trace。
  - 根因：gRPC 的业务失败常在协议 trailers 中表达。
- 反例 13：移动端代理配置误判协议失败
  - 错法：真机抓不到包就说 App 不走网络或服务端无响应。
  - 对法：核 Wi-Fi/蜂窝、系统代理、VPN/MDM、证书安装位置、WebView、私有 DNS 和证书钉扎边界。
  - 根因：移动端代理链路受系统、证书和 App 配置共同影响。
- 反例 14：日志泄敏
  - 错法：把 Authorization、Cookie、手机号、证书信息原样贴进报告。
  - 对法：脱敏后保留可关联 ID，敏感原文只放受控证据库。
  - 根因：排障不能制造新的数据风险。
- 反例 15：二进制半包/粘包误判业务失败
  - 错法：按单次 read 或单包边界解析消息，忽略长度前缀、序号、flags、endianness 和 checksum。
  - 对法：按协议帧边界重组流，核长度、序号、CRC/checksum、TLV/varint 和截断点。
  - 根因：TCP 字节流边界不等于业务消息边界。
- 反例 16：Protobuf 字段号复用导致旧客户端解析错
  - 错法：删除字段后复用字段号，未设置 reserved，忽略 optional/oneof/unknown fields。
  - 对法：核 schema 演进规则、字段号保留、JSON mapping、默认值和旧客户端样本。
  - 根因：序列化兼容性由 schema 演进约束决定。
- 反例 17：Alt-Svc 缓存导致回滚后仍走 HTTP/3
  - 错法：服务端回滚后只测新会话，忽略客户端和浏览器 Alt-Svc 缓存。
  - 对法：记录 Alt-Svc、缓存状态、HTTP/2 回退、不同客户端和网络对照。
  - 根因：协议入口选择可能被客户端缓存延迟影响。
- 反例 18：工具链版本不支持目标协议却下结论
  - 错法：抓包工具无法解码 HTTP/3/QUIC、zstd 或 gRPC，就认定对端未发送或数据损坏。
  - 对法：记录工具版本，用 pcap、服务端日志、curl/OpenSSL/nghttp2/grpcurl 或官方文档交叉验证。
  - 根因：工具能力边界不是协议事实。
- 反例 19：风控验证码当成接口 Bug
  - 错法：看到验证码、设备风险或访问限制后继续找签名算法和绕过路径。
  - 对法：记录账号态、地域、频率、设备字段、风险错误码和官方测试入口；只做授权归因和联动安全团队。
  - 根因：保护机制不是协议缺陷，越界分析会制造合规和滥用风险。
- 反例 20：nonce/timestamp 复现不控时钟
  - 错法：客户端、抓包机和服务端日志时钟不一致，却断言重放窗口或签名时效有问题。
  - 对法：先记录 NTP/系统时间、时区、采集时间点和 trace 对齐，再做最小重放验证。
  - 根因：时序证据不一致会污染签名、TLS、缓存和重试判断。
- 反例 21：报告不可复跑
  - 错法：只写“抓包显示 Header 不一致”，没有样本编号、过滤条件、脱敏映射和复现实验。
  - 对法：用证据索引绑定 pcap/HAR/session、trace id、差分字段、工具版本和复验步骤。
  - 根因：协议报告必须能被复核，不能只服务当下口头沟通。

## 提交前自检清单

- [ ] 行数 < 500。
- [ ] fenced code block 数量为 0，正文不出现三个反引号。
- [ ] frontmatter name 为 canonical `protocol-analysis`，description 存在，H1 为“协议分析”；兼容 slug 为 `prot`，自检不得要求 name 等于短 slug。
- [ ] 必需章节齐全：快速总则、场景执行卡、互操作测试矩阵、工具链交叉验证、协议文档化与风险分级交付物、高频坑 / 防遗漏、输出要求、约束、高频 Bug 反例库、提交前自检清单、2024-2026 新坑速查、与相邻技能的边界。
- [ ] 反例不少于 16 条，且能被“反例 数字”命中，并包含错法、对法、根因。
- [ ] 覆盖 TLS1.3、QUIC、HTTP3、HTTP/2、WebSocket、gRPC、Protobuf、Avro、证书钉扎、mTLS、重放窗口、签名规范化、抓包证据、Wireshark、tcpdump、dumpcap/ring buffer、丢包计数、capture filter、display filter、flow filter、mitmproxy addon 授权观测/脱敏/导出、Charles、移动端代理配置。
- [ ] 覆盖 gRPC schema 来源顺序 reflection→proto→protoset、grpcurl、buf lint、buf breaking、pcap→tshark JSON、fixtures、Buf CI 输出、Kaitai 风格 magic/version/length/flags/endianness/checksum。
- [ ] 覆盖授权安全测试、抓包排障、互操作联调、协议兼容性、CTF/教育和防御验证；拒绝 DoS、批量撞库、恶意绕过、窃取凭证、隐蔽持久化。
- [ ] 覆盖工程门禁、低级错禁止、差分样本、复现实验、报告证据链、设备指纹、验证码、风控、时钟/地域/版本和敏感数据脱敏。
- [ ] 与 rev、msec、wsec、api、obs、tst、aud 的边界写清。

## 2024-2026 新坑速查

- TLS1.3 默认化：session resumption、0-RTT、key update、企业代理、老中间盒和时钟漂移会造成偶发握手问题。
- HTTP3/QUIC 普及：UDP 阻断、连接迁移、Alt-Svc 缓存、0-RTT、QPACK 和 HTTP/2 降级让同一 API 在不同网络表现不同。
- 证书钉扎与 mTLS：移动端、IoT、企业零信任更常见；抓包失败不等于通信安全，只能说明观测受阻或策略生效。
- gRPC/Protobuf/Avro 漂移：proto3 optional、字段号 reserved、unknown fields、JSON mapping、Avro schema evolution 会破坏兼容。
- WebSocket、SSE 与 streaming：代理空闲超时、心跳、背压、重连恢复、代理缓冲和取消语义必须单独验证。
- 浏览器隐私变化：第三方 Cookie、Storage Partitioning、CHIPS、Safari ITP 会影响认证、埋点和嵌入页协议表现。
- DNS 新路径：DoH/DoT、IPv6 优先、EDNS Client Subnet、CDN 地域调度、本地缓存和移动私有 DNS 会改变入口目标。
- 压缩与内容协商：br、zstd、Accept-Encoding、Content-Encoding、流式压缩和代理解压会导致 Body 长度与抓包不一致。
- 工具链差异：Wireshark、tcpdump、dumpcap、tshark、mitmproxy、Charles、OpenSSL、curl、nghttp2、grpcurl、buf 版本影响 ALPN、HTTP/3、证书验证、gRPC schema 和解码结果。
- 合规与数据最小化：授权留痕、样本保留周期、跨境/第三方边界、日志脱敏成为协议排障前置条件。

## 与相邻技能的边界

- 逆向工程总控（reverse-engineering，slug: rev）：负责二进制、固件、SO/可执行文件、私有格式深度还原、反汇编/反编译和运行时入口证据；本技能只做授权流量层协议分析，不写逆向实现细节。
- 移动安全（mobile-security，slug: msec）：负责 Android/iOS 证书、证书钉扎、系统信任、App 网络安全配置、移动端代理阻塞、隐私合规和运行时防护评估；本技能负责移动流量证据和协议分层结论。
- Web 安全（web-security，slug: wsec）：负责 Web/API 漏洞、认证授权、CSRF/XSS/SSRF/注入、会话和安全修复验证；本技能只给协议层证据、日志脱敏和防护验证边界。
- API 工程（api-engineering，slug: api）：负责 REST/GraphQL/gRPC/Event 契约、状态码、错误模型、幂等、Webhook、版本兼容和消费者迁移；本技能提供请求/响应、签名、重放窗口和兼容证据。
- 可观测性工程（observability，slug: obs）：负责线上症状、日志/指标/链路、SLO、告警、incident timeline 和 runbook；本技能提供 pcap/HAR/抓包时间线与 trace 对齐证据。
- 测试验证（test-engineering，slug: tst）：负责场景矩阵、回归样本、自动化回放、弱网/兼容/发布冒烟和 CI 证据；本技能提供可复核 pcap/HAR/session、假设和验证点。
- 代码审计（code-audit，slug: aud）：负责代码改动后的需求对账、影响面、安全质量和证据收口；本技能不替代代码审计结论。
- 对应开发技能：SDK、代理脚本、服务端适配、客户端修复、网关配置由对应语言/端/后端/发布技能实现；本技能不直接扩大实现范围。
