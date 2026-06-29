---
name: ai-engineering
description: AI 工程实战排障版 - Claude/OpenAI/多模型接入、tool use/function calling、结构化输出、prompt caching、streaming、RAG、向量库、评测集、幻觉回放、token/延迟/成本、模型版本迁移、MCP/Agents、多模态、长上下文、推理模型、安全与可观测性。当设计、开发、评审或排查 LLM 应用、Agent、检索增强、模型调用、提示词、工具调用、评测体系、安全防护、成本性能问题时必须使用。
---

# AI 工程

AI 工程（ai-engineering，兼容 slug: aie）负责本技能描述范围内的定位、执行、验证和交接边界；旧短 slug 仅作兼容 alias/URL 主键，不作为规范技能名。

定位：把 AI / LLM 应用从“能跑 demo”收敛到可控、可测、可观测、可回滚、成本可接受、安全可上线。
铁律：没有模型、数据、工具、证据四类信息，不得宣称已优化；没有 eval / golden dataset / trace / 线上指标，只能标“需验证”。

## 开发门禁

- 需求门禁：先写任务边界、目标用户、输入来源、输出用途、错误代价、不可接受行为、人工接管点和上线后业务指标；需求不清时不改 prompt 代替产品判断。
- 指标门禁：每个 AI 功能至少定义质量、可靠性、安全、延迟、成本五类指标；没有基线、目标值和回滚阈值，不得宣称可上线。
- 版本门禁：prompt、system/developer message、tool schema、RAG corpus、embedding model、rerank、eval dataset、guardrail、模型参数都要有版本号和变更记录。
- 数据门禁：eval、日志、trace、prompt cache、Agent memory、向量库 ingestion 都要标注数据来源、权限、PII 状态、保留期、删除同步和训练/二次使用许可。
- 实验门禁：模型选择必须给候选、证据、失败样例和取舍；只写“换更强模型”“调温度”“加一句 prompt”不是工程方案。
- 发布门禁：灰度、A/B、kill switch、fallback、预算熔断、告警、回滚包、旧版本对照和负责人缺一项，只能发布到受控实验环境。

## 快速总则

- 模型：记录 provider、model、version/date、region、context window、reasoning/vision/audio/tool 支持、限流、SLA、退役时间；Claude、OpenAI、Gemini、开源模型不可只按“聪明程度”替换。
- 数据：用户输入、网页、文件、RAG 文档、工具结果、MCP resource、Agent memory 都是不可信数据；必须处理 PII、权限、来源、许可/版权、地域、保留期、删除同步、日志脱敏和二次使用授权。
- 工具：tool use / function calling / MCP tool 只给最小白名单、强 schema、幂等、超时、审计；写操作必须 preview、权限校验、dry-run 或人工确认。
- 证据：prompt、system prompt、RAG、embedding、向量库、chunking、rerank、guardrails、模型迁移都要绑定样例、指标、trace、测试命令或线上看板。
- 验收：上线前必须定义任务级成功标准、失败代价、人工接管条件、业务 KPI/用户体验指标；只给离线准确率而无线上口径，结论只能写“需灰度验证”。
- 输出：结构化输出优先 JSON schema / constrained decoding / provider 原生 structured output；解析失败必须有重试、降级、拒答或人工兜底。
- 安全：prompt injection、防泄密、越权检索、跨租户缓存命中、工具误调用是上线门禁，不是上线后优化。
- 红队：高风险链路必须覆盖 jailbreak、prompt injection、RAG poisoning、越权检索、工具参数 fuzz、数据外泄 canary、恶意文件和滥用输出评测；未跑红队不得宣称安全上线。
- 观测：生产链路至少记录 request_id、tenant/user、provider、model、prompt_version、rag_version、tool、token、latency、cost、finish_reason、cache_hit、error_code；推荐 OpenTelemetry trace 串联。
- 成本：优化前先拆 input/output token、reasoning token、embedding、rerank、tool roundtrip、stream 首 token、重试和缓存命中率，禁只看单次调用价格。
- 回滚：模型、prompt、RAG 索引、tool schema、guardrail 和路由策略必须能独立回滚；回滚后要清理错误缓存、队列、索引别名和正在运行的 Agent 任务。

## 场景执行卡

### 0. 需求 / 指标 / 方案定义
- 先查：用户任务、不可做事项、输出消费者、上下游系统、SLA、成本预算、合规边界、人工审核责任和已有失败样例。
- 必做：把“成功”拆成可测指标；定义离线 eval 通过线、线上灰度阈值、投诉/拦截口径、人工接管和停止条件。
- 方案：说明模型选择证据、prompt/tool/RAG 版本、数据集来源、fallback、缓存策略、观测字段、上线批次和回滚方案。
- 验证：需求样例、负样例、边界长度、权限样例、旧 bug replay、成本延迟预算、数据脱敏检查。
- 易漏：没定义失败代价就优化指标；只优化离线分数，忽略线上投诉、人工复核和业务转化。

### 1. Claude / OpenAI / 多模型接入与迁移
- 先查：任务类型、输入输出长度、tool use、结构化输出、多模态、推理深度、SLA、QPS、预算、数据区域、供应商合规、模型退役公告。
- 必做：候选模型横评；区分主模型、小模型、重模型兜底、离线批处理、fallback；锁 model id、API version、SDK version、参数默认值。
- 发布：prompt、model、rag、agent/tool 配置必须版本化并可一键回滚；灰度需有分桶、kill switch、预算阈值、失败率阈值和旧版本对照组。
- 验证：同一 golden dataset 下质量、拒答、P50/P95/P99、cost/request、限流、失败率、model drift diff、旧 bug replay。
- 易漏：Claude 与 OpenAI 的平台差异包括 system/developer/message 层级、tool_choice、stream delta、JSON schema 严格度、reasoning token 计费口径，不可用同一适配假设硬迁移。
- 自托管/开源模型：若采用自托管，需查许可证、权重来源、量化精度、推理服务、GPU/显存容量、并发、冷启动、批处理、监控、漏洞公告和模型供应链；不得只用离线分数替代生产压测。

### 2. prompt / system prompt / 结构化输出
- 先查：上游输入、下游字段、语言、长度、错误码、拒答、安全边界、兼容旧客户端。
- 必做：拆分 system prompt、业务规则、上下文、用户输入、输出 schema；用户内容不得覆盖高优先级指令。
- 验证：schema 合法率、解析失败率、边界样例、旧 bug、注入样本、多语言样本、回滚版本。
- 易漏：prompt 越写越长却无 eval；把格式要求混入用户内容；few-shot 泄露答案或引入偏见。

### 3. tool use / function calling / MCP / Agents
- 先查：工具清单、权限、幂等键、side effect、超时、重试、审计、用户确认、MCP server trust boundary。
- 必做：工具 schema 最小化；参数强校验；工具结果标注来源和可信度；Agent 状态、memory、scratchpad、handoff、停止条件、任务队列、并发锁、resume/replay、补偿动作和 side effect 去重可观测。
- 验证：工具误选、参数缺失、重复执行、长链路超时、工具失败恢复、越权调用、循环调用、人工接管。
- 易漏：把自然语言工具结果当事实；MCP resource 混租户；Agent 递归调用造成成本爆炸。

### 4. RAG / embedding / 向量库
- 先查：数据来源、权限模型、更新/删除频率、文档结构、语言、召回目标、答案是否必须引用。
- 必做：ingestion 清洗去重、chunking、metadata、tenant/role filter、版本、删除同步；embedding 维度和模型版本稳定；向量库 collection/schema、索引、top_k、阈值、备份恢复。
- 检索：评估 hybrid search、query rewrite、rerank、引用片段、无答案判断、权限隔离和 long-context stuffing 的取舍。
- 验证：Recall@K、MRR/NDCG、引用准确率、无答案拒答率、跨租户隔离、脏数据、增量更新、删除同步。

### 5. streaming / 长上下文 / 多模态
- 先查：SSE/WebSocket/HTTP chunk、客户端取消、断线重连、首 token SLA、图片/音频/视频大小、上下文窗口和截断策略。
- 必做：streaming 事件协议、done/error 事件、partial JSON 处理、cancel propagation、token budget、附件摘要、引用定位。
- 交互：UI 必须区分生成中/完成/失败/取消，展示引用、置信边界和不可验证声明；高风险建议或不可恢复写操作必须二次确认，不能用半截流式输出误导用户。
- 验证：慢客户端、断线、重试、半包、超长输入、图片 OCR 失败、多模态文件过大、长上下文注意力稀释。
- 易漏：把长上下文当无限记忆；stream 中途失败未落 finish_reason；多模态输入未做安全扫描和成本预估。

### 6. eval / 幻觉回放 / 回归
- 先查：业务成功标准、失败代价、线上投诉、人工标注、灰度流量、历史 hallucination cases。
- 必做：golden dataset、负样本、对抗样本、多语言样本、权限样本；保存 prompt_version、model_version、retrieved_chunks、tool_trace。
- 反馈闭环：线上反馈、人工标注、投诉、拒答、工具失败和低置信样本进入样本池；入池需去重、脱敏、标注来源、版本化，并防止 eval 集被 prompt 过拟合或训练污染。
- 验证：准确率、拒答率、引用命中、schema 合法率、人工一致性、漂移趋势、旧幻觉回放。
- 易漏：只测 happy path；只看离线分数不看线上转化/投诉；评测集被 prompt 过拟合。

### 7. token / 延迟 / 成本 / prompt caching
- 先查：输入 token、输出 token、reasoning token、embedding/rerank 成本、工具 roundtrip、缓存命中、限流重试。
- 必做：静态前缀抽离、cache key 隔离、上下文压缩、批处理、并发限制、重试退避、模型分层路由。
- 韧性：定义 provider outage、限流、预算耗尽、索引不可用、工具超时的降级路径；可选小模型、静态答案、队列削峰、离线补偿、跨区域切换和人工接管。
- 验证：cache hit rate、TTFT、P95/P99、cost/request、失败重试放大、供应商限流、region 差异。
- 易漏：跨用户共享 prompt caching；缓存含 PII；为了省 token 删除安全规则或引用证据。

### 8. 上线 / 灰度 / 回滚 / 漂移
- 先查：发布面、分桶规则、旧版本对照、监控看板、告警接收人、预算阈值、数据更新频率、供应商状态页和回滚权限。
- 必做：A/B 或灰度分桶稳定；prompt/model/rag/tool 路由可按租户、用户、任务、百分比切换；回滚不依赖重新部署代码。
- 漂移：跟踪输入分布、检索命中、无答案率、拒答率、人工改写率、投诉率、模型输出长度、tool failure、成本和延迟趋势；漂移样本进入复核池。
- 回滚：定义回滚触发阈值、执行命令、验证样例、缓存/队列/索引清理、补偿动作和用户影响公告；回滚后保留事故 trace。
- 验证：灰度前后指标对比、在线 shadow eval、canary tenant、kill switch 演练、旧版本重放、降级路径压测。
- 易漏：只回滚 prompt 不回滚 RAG 索引；停用模型但缓存还命中旧危险输出；Agent 任务在回滚后继续执行旧 tool schema。

## 高频坑 / 防遗漏

- 需求指标没有落文档就开始调模型，通常会把产品问题伪装成 prompt 问题。
- provider SDK 升级会改变默认超时、重试、stream 事件名、tool schema 校验、错误码结构，必须锁版本并回放旧样例。
- OpenAI structured outputs、Claude tool use、Gemini function calling 的 schema 支持差异不能靠同一解析器硬兼容。
- reasoning model 可能隐藏中间推理、增加 reasoning token、降低 streaming 可见性；不能按普通 chat model 做成本和延迟估算。
- RAG 删除同步和权限过滤比召回率更优先；向量库 metadata filter 必须进测试集。
- Agent memory 不等于事实库；长期记忆写入要有来源、过期、用户可删、隐私策略。
- Agent 编排有副作用时要状态机化，记录 plan-act-observe、幂等键、补偿、锁和可恢复检查点。
- 多模态文件要检查大小、格式、EXIF/PII、OCR 错读、版权和平台可用性。
- long context 仍会丢重点；关键证据应排序、分块、引用和压缩，不要整库塞入上下文。
- streaming 不是只把文本流出来；要定义 error/done/cancel/usage 事件和客户端幂等渲染。
- guardrails 不能只靠 prompt；高风险动作要权限、规则、工具沙箱和审计日志。
- eval 结果必须能追到 prompt_version、model_version、数据版本和随机参数；线上 A/B 需明确分桶、显著性口径和回滚阈值。
- 观察日志是生产数据；不得把完整 prompt、用户文件、密钥、身份证、手机号、cookie、合同、病历、客户数据原文直接入日志或第三方看板。
- fallback 不是“失败后再问一次大模型”；必须限制重试放大、避免重复写工具、标记降级来源并保留用户可理解状态。

## 低级错禁止

- 禁止无 eval 合并 prompt；禁止无版本号覆盖 prompt；禁止用线上用户输入直接扩充 eval 而不脱敏、不去重、不标来源。
- 禁止把模型输出当可信 JSON、SQL、Shell、HTML、权限判断或事实库；必须由 schema、白名单、沙箱、权限和引用证据约束。
- 禁止只测一次 happy path；任何涉及 tool/RAG/结构化输出/权限/成本的改动至少要覆盖成功、失败、空结果、越权、超时、重试和回滚样例。
- 禁止在 prompt、日志、trace、向量库、截图、bug 单、eval 样本中保存真实密钥、cookie、token、未脱敏 PII 或客户原文。
- 禁止把 RAG 文档、网页、邮件、工单、MCP resource、工具结果写成“系统事实”；必须保留来源、时间、权限、置信度和可引用片段。
- 禁止跨租户共享缓存、memory、向量 collection、文件摘要或工具结果，除非有明确隔离 key 和隔离测试。
- 禁止上线没有预算上限、最大轮次、最大工具次数、最大上下文、最大重试、最大输出长度的 Agent。
- 禁止把模型供应商 5xx、429、内容过滤、超时、schema 失败统一吞成“无结果”；错误类型要进入指标和用户态降级。

## 输出要求

- 结论：先给是否可上线/可合并/需回滚/需补证据。
- 证据：列出模型、数据、工具、指标、trace、测试命令、样例 ID，不得只写“已优化”。
- 风险：明确安全、权限、成本、延迟、幻觉、漂移、供应商锁定、兼容性影响。
- 方案：给最小改动、回滚路径、灰度策略、监控告警、负责人和验证口径。
- 边界：涉及 API 契约、Web 安全、SRE、数据工程、后端、内容营销或生图提示词时，说明已交给相邻技能处理的部分。

## 约束

- 不凭模型名判断能力；版本、区域、API 参数不确定必须查官方文档或标“需验证”。
- 不把用户输入、RAG 文档、工具结果、MCP resource 提升为系统指令。
- 不为追求成本删除权限过滤、安全策略、引用证据、审计日志。
- 不在日志、eval 样本、prompt cache、Agent memory 中保存未脱敏 PII、密钥、受版权限制内容。
- 不越界替代 api、wsec、obs、be、de、acm、aip 的专业结论。
- 不输出无法复验的“提示词玄学优化”；所有建议必须绑定失败样例或指标。
- 不把离线 eval 通过写成“线上已验证”；线上结论必须来自灰度、A/B、shadow、人工复核、投诉率或观测看板。

## 高频 Bug 反例库

反例 1：错法：只把模型从旧版换成新版 Claude/OpenAI 后直接上线；对法：锁 model id/API/SDK，跑 golden dataset、旧 bug replay、成本延迟对比和回滚；根因：模型版本迁移会改变工具调用、拒答、长度、语气和默认参数。
反例 2：错法：把用户上传文档拼进 system prompt；对法：用户内容放低优先级上下文并加来源边界、引用和注入检测；根因：混淆指令层级导致 prompt injection 覆盖系统规则。
反例 3：错法：tool use 参数只靠模型生成后直接执行写操作；对法：schema 校验、权限校验、幂等键、preview、人工确认、审计；根因：LLM 输出不是可信命令，工具有真实副作用。
反例 4：错法：RAG 只调 top_k 追召回；对法：清洗、chunk、metadata filter、hybrid search、rerank、无答案拒答和引用评测一起做；根因：召回、排序、权限、引用是耦合链路。
反例 5：错法：向量库跨租户共用 collection 且只在应用层过滤；对法：tenant/role metadata filter 下推、隔离索引或命名空间、隔离测试；根因：检索阶段越权会把敏感片段送入上下文。
反例 6：错法：JSON 输出解析失败就正则截取；对法：provider 原生 structured output/schema 校验、有限重试、错误码和降级；根因：自然语言输出不稳定，正则会吞错字段。
反例 7：错法：streaming 中途失败仍把半截答案当完成；对法：定义 done/error/cancel/usage 事件，客户端只在完成态提交；根因：流式传输存在断线、半包和取消。
反例 8：错法：prompt caching 把含用户资料的大前缀跨用户复用；对法：缓存只放稳定公共前缀，cache key 加租户/权限边界，PII 禁入；根因：缓存命中可能造成跨用户泄露。
反例 9：错法：用长上下文替代 RAG 和证据排序；对法：保留检索、分块、rerank、引用和摘要压缩；根因：长上下文有注意力稀释、成本高和截断风险。
反例 10：错法：Agent 没有最大步数和停止条件；对法：限制轮次、预算、工具次数、超时和人工接管；根因：循环规划会放大成本并重复执行工具。
反例 11：错法：eval 只用十个成功样例；对法：加入失败、拒答、注入、权限、多语言、边界长度和线上投诉样例；根因：评测集偏差会掩盖真实风险。
反例 12：错法：幻觉投诉只改 prompt 文案；对法：保存 hallucination replay、retrieved_chunks、tool_trace、model_version 并回放验证；根因：幻觉可能来自检索缺失、旧数据、工具失败或模型漂移。
反例 13：错法：多模态图片直接送模型不做预处理；对法：检查格式、大小、EXIF/PII、OCR 置信度、版权和失败兜底；根因：视觉模型会误读细节且输入成本高。
反例 14：错法：只看平均延迟和单价；对法：拆 TTFT、P95/P99、输出长度、reasoning token、工具 roundtrip、重试和缓存命中率；根因：用户体验和账单由尾延迟与放大因子决定。
反例 15：错法：MCP server 默认全信任；对法：按 server/resource/tool 建 trust boundary、权限白名单、审计和数据脱敏；根因：MCP 扩展了模型可见数据和可执行动作。
反例 16：错法：推理模型要求输出完整思维链；对法：只要求可验证摘要、引用、步骤结果和工具证据；根因：2024-2026 推理模型常隐藏思考且不保证 chain-of-thought 可导出。
反例 17：错法：没有定义业务指标就让模型“回答更好”；对法：先定义样例、评分标准、失败代价和人工接管阈值；根因：不可测需求会让 prompt 迭代失控。
反例 18：错法：线上投诉后只改 system prompt；对法：把投诉样本脱敏入池，回放 retrieved_chunks、tool_trace、model/prompt/rag 版本并定位来源；根因：投诉可能来自数据、检索、工具、权限、漂移或模型选择。
反例 19：错法：fallback 失败后自动换模型重复执行写工具；对法：写操作用幂等键、preview、人工确认和补偿日志，fallback 只重试只读或可撤销步骤；根因：模型重试会放大副作用。
反例 20：错法：A/B 分桶按请求随机，用户同一会话多版本混跑；对法：按用户/租户/任务稳定分桶，trace 记录 variant；根因：不稳定分桶会污染指标和用户体验。
反例 21：错法：观察日志记录完整 prompt 和用户文件方便排障；对法：记录摘要、hash、样例 ID、脱敏字段和受控采样，敏感内容单独受权访问；根因：AI trace 极易包含 PII、密钥和客户数据。
反例 22：错法：检测到数据漂移后只调 top_k；对法：分析输入分布、语料 freshness、chunk、metadata filter、rerank、无答案率和人工标注；根因：漂移是系统问题，不一定是召回数量问题。
反例 23：错法：预算超限时删除安全 prompt 和引用要求；对法：先做模型路由、缓存公共前缀、压缩上下文、批处理和降级；根因：成本优化不能牺牲权限、安全和可解释证据。
反例 24：错法：上线后没有 kill switch，只能发版回滚；对法：模型、prompt、RAG、tool 路由和 Agent 任务开关配置化；根因：AI 事故需要分钟级停止能力。

## 提交前自检清单

- [ ] 已写清需求边界、成功指标、失败代价、人工接管、灰度阈值和回滚阈值。
- [ ] 已记录 provider、model id、API/SDK version、region、参数、prompt_version、rag_version。
- [ ] 已版本化 prompt、tool schema、RAG corpus、embedding/rerank、eval dataset、guardrail 和路由策略。
- [ ] 已跑 golden dataset、旧 bug replay、注入样本、权限样本、负样本、多语言样本和结构化输出解析测试。
- [ ] 已验证 tool use / MCP 工具的 schema、权限、幂等、超时、重试、审计和人工确认。
- [ ] 已验证 RAG 的 Recall@K、引用准确率、无答案拒答、metadata filter、删除同步和跨租户隔离。
- [ ] 已给出 token、latency、cost、cache hit、限流、失败率的基线与改后对比。
- [ ] 已覆盖 streaming 的 done/error/cancel/usage、断线、慢客户端和半截答案处理。
- [ ] 已处理 PII、日志脱敏、prompt cache 隔离、Agent memory 可删和合规边界。
- [ ] 已准备灰度、A/B 或 shadow eval、监控、告警、kill switch、预算熔断、人工接管、回滚模型/回滚 prompt/回滚索引方案。
- [ ] 已检查 drift：输入分布、检索命中、无答案率、拒答率、人工改写率、投诉率、成本、延迟和 tool failure 趋势。
- [ ] 已说明相邻技能边界，未越界替代 API、安全、SRE、数据、后端、营销、生图结论。

## 2024-2026 新坑速查

- 模型退役和别名漂移：不要用 floating alias 上线关键链路；记录退役日、替代模型、回滚窗口。
- Structured output 普及但差异大：JSON schema 支持、strict 模式、枚举、递归、nullable、tool 参数在不同 provider 不一致。
- Prompt caching 成本收益明显但泄露风险上升：公共前缀、租户边界、缓存失效和命中率必须可观测。
- 长上下文窗口扩大但不是数据库：超长输入会带来注意力稀释、引用错位、截断和成本尾部风险。
- 推理模型改变成本与延迟：reasoning token、effort 参数、隐藏思考、非流式阶段会影响 SLA。
- 多模态进入生产：图片、音频、视频输入要做格式、大小、版权、PII、OCR/ASR 置信度和失败兜底。
- Agents 与 MCP 扩张攻击面：外部 tool/resource 必须按不可信输入处理，最小权限和审计优先。
- RAG 从“向量检索”变成“检索系统”：hybrid、rerank、query rewrite、citation、permission filter、data freshness 缺一不可。
- EvalOps 成为必需：离线 eval、在线 A/B、人工复核、投诉回放、漂移检测要能关联版本。
- 成本优化从模型单价转向系统账单：token、缓存、重试、工具、embedding、rerank、批处理和限流共同决定成本。

## 与相邻技能的边界

- API 工程/api-engineering（api）：负责 HTTP/API 契约、OpenAPI、错误码、认证授权、幂等、版本兼容；本技能只定义 LLM 调用契约和模型输出契约。
- Web 安全/web-security（wsec）：负责 Web/API 安全、OWASP、会话、CSRF/XSS/SSRF/JWT/OAuth；本技能聚焦 prompt injection、工具越权、RAG 泄密、模型输出安全。
- 可观测性/observability（obs）：负责 SLI/SLO、告警、incident、容量和运行手册；本技能提供 LLM 维度的 token、latency、cost、model/prompt/rag trace 字段。
- 后端工程/backend-engineering（be）：负责服务分层、DB/缓存/队列、配置、部署、限流熔断；本技能只约束模型调用、工具执行、Agent/RAG 链路的工程质量。
- 数据工程/data-engineering（de）：负责 ETL/ELT、湖仓、Kafka/Flink/Spark、数据质量、血缘和回填；本技能只处理 RAG ingestion、embedding、向量库、eval dataset 与模型上下文数据。
- AI 内容营销/ai-content-marketing（acm）：负责内容策略、渠道、转化、合规文案和素材运营；本技能只保证生成链路可靠、安全、可测，不判断营销定位。
- AI 图片提示词/ai-image-prompt（aip）：负责图像提示词、构图、风格、品牌视觉、负面词和出图可控性；本技能只处理多模态模型接入、文件安全、成本、延迟和评测。
- 测试验证/test-engineering（tst）：负责测试分层、场景矩阵、CI 和回归策略；本技能提供 AI 特有样本、指标、trace 和幻觉回放要求。
- 代码审计/code-audit（aud）：负责最终需求对账、影响面、安全质量复核和证据收口；本技能提交前必须把 AI 改动证据交给 代码审计/code-audit（aud） 收口。
