---
name: research-scientific-research
description: AI辅助科研最佳实践调研报告：GitHub项目调研、学术论文方法论、工具生态、多Agent科研架构、文献综述自动化
disable-model-invocation: false
user-invocable: false
---

# AI辅助科研最佳实践调研报告

> 调研日期：2026-03-12
> 用途：构建科研辅助Skill的知识基础

---

## 1. GitHub相关项目调研

### 1.1 AI Research Assistant 类项目

| 项目 | Stars | 语言 | 核心定位 |
|------|-------|------|----------|
| MedgeClaw | ~973 | TeX/Python | 生物医学AI研究助手，支持RNA-seq、药物发现、临床分析 |
| DeepInnovator | ~183 | Python | 科学发现与idea生成，HKUDS出品 |
| AI-Co-Scientist | ~16 | JavaScript | 多agent系统，生成研究方向 + 分析文献 |
| EBARA | ~13 | Python | Evidence-Based AI Research Assistant，集成PubMed + OpenAI |
| sciclaw | ~5 | Go | 可复现科研工作流，支持manuscript集成 |

**设计思路提取：**
- 主流架构：多Agent系统（专门化agent分别负责检索、阅读、总结、生成）
- 领域专化优于通用：生物医学类项目star数明显高于通用类
- 工作流自动化：从检索→阅读→总结→生成idea形成完整pipeline

### 1.2 Literature Review Automation 类项目

| 项目 | Stars | 语言 | 核心功能 |
|------|-------|------|----------|
| PISMA-Literature-Review-Pipeline | ~3 | Python | 自动搜索学术数据库、收集论文、citation扩展 |
| papervisor | ~2 | Python | 模块化SLR pipeline，结合NLP |
| auto-literature-review | ~1 | TypeScript | Scopus + OpenAI自动study selection |
| CitationScreeningReplicability | ~4 | Jupyter | 神经网络辅助citation screening（ECIR 2022） |

**功能模块共性：**
1. 数据库API接入（Scopus、PubMed、Semantic Scholar）
2. 关键词扩展与搜索字符串生成
3. 去重与初筛（title/abstract screening）
4. 全文精读与数据提取
5. Citation网络扩展（snowballing）

### 1.3 Paper Reading / Summarization 类项目

**主流技术栈：**
- RAG架构：向量数据库（Pinecone、Chroma）+ LLM检索增强
- Multi-Agent：解析agent + 分节agent + 总结agent
- 代表项目：`paper-reading-agent`（GPT-4o-mini + RAG + Pinecone）、`research-paper-pipeline`（自动化批量处理）

---

## 2. 文献调研最佳实践

### 2.1 系统性文献综述（Systematic Literature Review）标准流程

遵循 **PRISMA 2020**（Preferred Reporting Items for Systematic reviews and Meta-Analyses）框架：

#### Phase 1：协议制定（Protocol）
- 明确研究问题（PICO框架：Population, Intervention, Comparison, Outcome）
- 预注册研究协议（PROSPERO数据库）
- 定义纳入/排除标准（Inclusion/Exclusion Criteria）

#### Phase 2：检索（Search）
- 制定检索字符串（Boolean operators: AND/OR/NOT）
- 多数据库并行检索
- 记录检索日期和检索式（可复现性要求）
- 补充手工检索（key journals、reference lists）

#### Phase 3：筛选（Screening）
- Title/Abstract screening（初筛）
- Full-text screening（精筛）
- 双人独立筛选 + 第三方仲裁（减少偏差）
- PRISMA Flow Diagram记录筛选过程

#### Phase 4：数据提取（Data Extraction）
- 标准化提取表格
- 提取：作者、年份、方法、数据集、指标、结论

#### Phase 5：质量评估（Quality Assessment）
- 使用标准工具：RoB 2（随机对照试验）、QUADAS-2（诊断研究）

#### Phase 6：综合与报告（Synthesis & Reporting）
- 定量综合（Meta-analysis）或定性综合（Narrative synthesis）
- PRISMA checklist逐项核对

### 2.2 AI高效阅读论文策略

**分层阅读法（Three-Pass Method）：**

| Pass | 时间 | 目标 | 关注点 |
|------|------|------|--------|
| 第一遍 | 5-10分钟 | 判断相关性 | Title、Abstract、Introduction首段、Conclusion、图表 |
| 第二遍 | 1小时 | 理解主要贡献 | 方法概述、实验结果、主要图表 |
| 第三遍 | 4-5小时 | 深度理解 | 完整方法、公式推导、实验细节、局限性 |

**AI辅助阅读流程：**
1. 用AI提取论文结构（5W1H：Who/What/Why/Where/When/How）
2. 让AI识别核心贡献（novelty points）
3. 让AI对比related work差异
4. 让AI列出局限性和future work
5. 让AI生成可复现的实验checklist

### 2.3 文献管理策略

**工具选择：**
- **Zotero**：开源，浏览器插件，支持PDF注释同步，推荐首选
- **Mendeley**：Elsevier生态，适合团队协作
- **Obsidian + Zotero**：笔记与文献双向链接，适合知识图谱构建

**引用追踪策略：**
- **Forward citation**：用Semantic Scholar / Google Scholar查"Cited by"
- **Backward citation**：精读参考文献列表
- **Snowballing**：从核心论文向前向后扩展
- **Alert设置**：Google Scholar Alerts监控新引用

### 2.4 主要学术数据库特点与搜索技巧

#### Google Scholar
- **特点**：覆盖最广（含灰色文献、预印本），免费，引用数据丰富
- **技巧**：
  - `"exact phrase"` 精确匹配
  - `author:lastname` 作者搜索
  - `site:arxiv.org` 限定来源
  - 设置Alert追踪关键词新论文

#### Semantic Scholar
- **特点**：AI驱动，2.33亿篇论文，提供免费API，语义搜索能力强
- **独特功能**：
  - TLDR自动摘要
  - Influential Citations识别（区分高影响力引用）
  - Research Fields分类
  - 开放API（`api.semanticscholar.org`）适合程序化检索

#### arXiv
- **特点**：预印本服务器，CS/Math/Physics/Stats领域必查，论文最新
- **搜索技巧**：
  - 支持字段搜索：`ti:` (title), `au:` (author), `abs:` (abstract)
  - 通配符：`?`单字符，`*`多字符
  - TeX数学表达式：用`$...$`包裹
  - 按分类浏览：cs.LG, cs.AI, stat.ML等

#### DBLP
- **特点**：计算机科学专用，数据干净，适合精确作者/会议/期刊检索
- **技巧**：直接搜索作者名获取完整publication list

#### PubMed
- **特点**：生物医学领域权威，MeSH词表支持语义扩展
- **技巧**：使用MeSH Terms扩展同义词，Boolean检索，Filter限定年份/文章类型

---

## 3. 数据查找最佳实践

### 3.1 主要公开数据集平台

| 平台 | 特点 | 适用场景 |
|------|------|----------|
| **HuggingFace Datasets** | 90万+数据集，支持模态/大小/格式筛选，API直接加载 | NLP、CV、多模态ML任务 |
| **Kaggle** | 竞赛数据集，社区notebook，数据质量有保障 | 监督学习、竞赛baseline |
| **UCI ML Repository** | 经典ML数据集，标注清晰，适合算法验证 | 传统ML算法对比 |
| **Papers with Code** | 与论文绑定，含benchmark排行榜 | 找SOTA对比数据集 |
| **Google Dataset Search** | 元搜索引擎，聚合多平台数据集 | 跨领域数据集发现 |
| **OpenML** | 自动化ML实验平台，数据集+实验结果 | AutoML研究 |
| **Zenodo** | 科研数据存档，DOI引用，跨学科 | 需要可引用数据集 |

### 3.2 领域特定数据源

| 领域 | 数据源 |
|------|--------|
| 计算机视觉 | ImageNet, COCO, Open Images, LAION |
| NLP | Common Crawl, The Pile, C4, GLUE/SuperGLUE |
| 生物医学 | MIMIC-III/IV, PhysioNet, TCGA, UniProt |
| 时间序列 | UCR Time Series Archive, M4 Competition |
| 图数据 | OGB (Open Graph Benchmark), TUDataset |
| 地理空间 | OpenStreetMap, NASA Earthdata |
| 金融 | WRDS, Quandl, Yahoo Finance |

### 3.3 数据质量评估标准

**FAIR原则（Findable, Accessible, Interoperable, Reusable）：**

1. **Findable**：有唯一标识符（DOI）、元数据完整
2. **Accessible**：开放访问或明确授权协议
3. **Interoperable**：标准格式（CSV/JSON/Parquet），有数据字典
4. **Reusable**：明确license（CC BY, MIT等），有引用方式

**实践评估维度：**
- 数据规模：样本量是否足够支撑统计显著性
- 标注质量：inter-annotator agreement（Cohen's Kappa > 0.7为良好）
- 类别平衡：是否存在严重class imbalance
- 时效性：数据收集时间是否与研究场景匹配
- 泄露风险：train/test split是否合理，有无data leakage

### 3.4 数据集选择考量因素

1. **任务匹配度**：数据集的任务定义是否与研究问题一致
2. **Benchmark地位**：是否是领域公认benchmark（便于对比）
3. **规模适配**：数据量与模型复杂度匹配
4. **License合规**：商业使用/学术使用限制
5. **可复现性**：数据集是否稳定可获取（避免链接失效）
6. **社区活跃度**：是否有持续维护和leaderboard

---

## 4. 科研方法设计最佳实践

### 4.1 实验设计原则

#### 对照组设计
- **Ablation Study（消融实验）**：逐一移除模型组件，验证每个组件的贡献
  - 例：完整模型 → 去掉模块A → 去掉模块B → 去掉A+B
- **Baseline选择**：
  - 必须包含：Random/Majority baseline（下界）
  - 必须包含：当前SOTA方法（上界参考）
  - 推荐包含：经典方法（如BERT、ResNet等）
  - 避免：只与弱baseline对比

#### 统计显著性
- 多次运行取均值±标准差（至少3-5次随机种子）
- 使用统计检验：t-test、Wilcoxon signed-rank test
- 报告p-value（p < 0.05为显著）
- 效应量（Effect Size）：Cohen's d，避免只看p-value

#### 超参数处理
- 超参数搜索在验证集上进行，测试集只用一次
- 报告超参数搜索范围和最终值
- 使用固定随机种子保证可复现

### 4.2 Baseline选择策略

```
Baseline层级（从弱到强）：
1. Naive baseline：随机猜测、多数类、均值预测
2. 经典方法：SVM、Random Forest、LSTM等
3. 预训练模型：BERT、GPT、ResNet等
4. 近期SOTA：最近1-2年顶会论文方法
5. 自己的变体：消融实验中的简化版本
```

**选择原则：**
- 公平对比：相同数据集、相同评估协议
- 复现优先：优先使用官方代码复现，记录复现结果
- 差异说明：若结果与原论文不同，需解释原因

### 4.3 评估指标选择

| 任务类型 | 主要指标 | 辅助指标 |
|----------|----------|----------|
| 分类 | Accuracy, F1, AUC-ROC | Precision, Recall, MCC |
| 回归 | RMSE, MAE | R², MAPE |
| NLP生成 | BLEU, ROUGE, BERTScore | Perplexity, Human eval |
| 信息检索 | NDCG, MAP, MRR | Precision@K, Recall@K |
| 聚类 | NMI, ARI | Silhouette Score |
| 目标检测 | mAP | IoU, FPS |

**指标选择原则：**
- 与领域惯例一致（便于横向对比）
- 多指标互补（单一指标可能误导）
- 考虑实际应用需求（如延迟、内存）

### 4.4 可复现性最佳实践

**代码层面：**
- 固定所有随机种子（Python random, NumPy, PyTorch/TF）
- 环境管理：`requirements.txt` 或 `conda env export`
- Docker容器化：确保环境完全一致
- 配置文件化：所有超参数写入config文件，不hardcode

**实验记录层面：**
- 使用实验追踪工具：MLflow、Weights & Biases、Neptune
- 记录：数据版本、代码commit hash、超参数、结果
- 数据版本控制：DVC（Data Version Control）

**报告层面：**
- 提供完整实现代码（GitHub）
- 提供预训练模型权重
- 详细描述数据预处理步骤
- 报告计算资源（GPU型号、训练时间）

---

## 5. AI辅助科研的Prompt策略

### 5.1 文献总结Prompt模板

```
## 论文精读模板

请按以下结构分析这篇论文：

**基本信息**
- 标题、作者、发表年份、发表venue（期刊/会议）

**核心贡献（3点以内）**
- 用一句话描述每个贡献

**问题定义**
- 解决什么问题？为什么重要？

**方法概述**
- 核心思路（用类比或直觉解释）
- 关键技术组件
- 与prior work的本质区别

**实验设计**
- 数据集、baseline、评估指标
- 主要实验结果（数字）

**局限性与Future Work**
- 作者承认的局限
- 潜在改进方向

**我的评价**
- 方法的优雅程度（1-5）
- 实验的说服力（1-5）
- 对我研究的参考价值
```

### 5.2 Research Gap识别Prompt

```
## Research Gap分析模板

我正在研究[研究领域]，已阅读以下论文：
[论文列表]

请帮我分析：

1. **已解决的问题**
   - 列出这些论文共同解决了哪些核心问题

2. **现有方法的共同局限**
   - 跨论文的系统性不足（非个别论文的局限）

3. **未被充分探索的方向**
   - 哪些假设从未被质疑？
   - 哪些场景/数据类型被忽视？
   - 哪些评估维度缺失？

4. **矛盾与争议点**
   - 不同论文之间的结论冲突
   - 这些冲突背后的原因假设

5. **潜在Research Gap（按重要性排序）**
   - Gap描述 + 为什么重要 + 初步解决思路
```

### 5.3 方法论设计Prompt

```
## 研究方法设计模板

**研究问题**：[明确的研究问题]

**已知约束**：
- 可用数据：[描述]
- 计算资源：[描述]
- 时间限制：[描述]

请帮我设计研究方法：

1. **方法空间探索**
   - 列出3-5种可能的技术路线
   - 每种路线的核心假设、优势、风险

2. **推荐方案**
   - 基于约束条件推荐最可行方案
   - 说明选择理由

3. **实验设计**
   - 核心实验（验证主要贡献）
   - 消融实验（验证各组件）
   - 分析实验（理解模型行为）

4. **风险预案**
   - 如果核心假设不成立，备选方案是什么？

5. **评估标准**
   - 什么结果算"成功"？
   - 最低可接受结果是什么？
```

### 5.4 实验方案生成Prompt

```
## 实验方案生成模板

**方法描述**：[你的方法]
**声称的贡献**：[你声称解决了什么问题]

请生成完整实验方案：

1. **数据集选择**
   - 推荐数据集及理由
   - 数据预处理步骤

2. **Baseline配置**
   - 必须对比的baseline（含理由）
   - 每个baseline的实现来源（官方代码/复现）

3. **评估协议**
   - 数据划分方式（train/val/test比例）
   - 评估指标及计算方式
   - 统计显著性检验方法

4. **超参数设置**
   - 需要调整的超参数列表
   - 搜索范围建议
   - 调参策略（grid search/random search/Bayesian）

5. **消融实验设计**
   - 列出所有需要验证的组件
   - 消融顺序建议

6. **预期结果与风险**
   - 预期改进幅度
   - 可能失败的原因及应对
```

### 5.5 文献检索Query生成Prompt

```
## 检索策略生成模板

我的研究主题是：[主题描述]

请帮我生成：

1. **核心关键词**（5-10个）
   - 主题词、方法词、应用词

2. **同义词与变体**
   - 每个核心词的同义表达

3. **Boolean检索式**
   - Google Scholar版本
   - Semantic Scholar版本
   - arXiv版本（含分类限定）

4. **排除词**
   - 需要用NOT排除的噪声词

5. **相关领域扩展**
   - 可能有交叉的相邻领域关键词
```

---

## 6. 科研工作流整体架构建议

### 6.1 完整科研Pipeline

```
Phase 1: 问题定义
├── 领域调研（广度优先）
├── Research Gap识别
└── 研究问题精确化

Phase 2: 文献综述
├── 检索策略制定
├── 多数据库并行检索
├── PRISMA筛选流程
├── 精读核心论文（三遍法）
└── 知识图谱构建

Phase 3: 方法设计
├── 技术路线探索
├── 方法选型与论证
└── 实验方案设计

Phase 4: 数据准备
├── 数据集选择
├── 数据质量评估
└── 预处理pipeline

Phase 5: 实验执行
├── Baseline复现
├── 方法实现
├── 消融实验
└── 统计分析

Phase 6: 结果分析
├── 定量分析
├── 定性分析（case study）
├── Error analysis
└── 局限性讨论

Phase 7: 写作与发表
├── 论文结构设计
├── 图表制作
└── 投稿策略
```

### 6.2 推荐工具栈

| 环节 | 工具 |
|------|------|
| 文献检索 | Semantic Scholar API + arXiv + Google Scholar |
| 文献管理 | Zotero + Better BibTeX |
| 笔记知识库 | Obsidian（双向链接） |
| 实验追踪 | Weights & Biases / MLflow |
| 数据版本 | DVC |
| 代码管理 | Git + GitHub |
| 论文写作 | LaTeX + Overleaf |
| 数据集发现 | HuggingFace + Papers with Code + Kaggle |

---

## 关键发现摘要

### 1. GitHub项目格局
当前AI科研辅助项目呈现**领域专化**趋势，生物医学方向（MedgeClaw ~973 stars）远超通用科研助手。主流架构为**多Agent + RAG**，核心模块包括：数据库API接入、文献筛选、全文解析、知识提取、idea生成。

### 2. 文献综述的核心规范
PRISMA 2020是系统性文献综述的黄金标准，AI辅助的最大价值在于**初筛自动化**（title/abstract screening）和**结构化信息提取**，可将传统SLR数百小时工作量压缩至数十小时。三遍阅读法配合AI结构化提取是高效精读的最佳实践。

### 3. 数据集生态
HuggingFace Datasets（90万+数据集）已成为ML领域数据集的事实标准平台，Papers with Code提供任务-数据集-benchmark的三角关联，是找SOTA对比基准的首选。数据质量评估应遵循FAIR原则，重点关注标注质量（Kappa > 0.7）和data leakage风险。

### 4. 实验设计的关键原则
- **消融实验**是验证方法贡献的核心手段，必须设计
- **多随机种子**（≥3次）+ 统计检验是结果可信度的基础
- **Baseline选择**需覆盖naive→经典→近期SOTA三个层级
- **可复现性**要求：固定种子 + 环境容器化 + 实验追踪工具

### 5. Prompt策略的核心洞察
科研辅助Prompt的关键是**结构化输出约束**：强制AI按固定schema输出（贡献/方法/实验/局限），而非自由发挥。Research Gap识别需要**跨论文的横向分析**，而非单篇总结。实验方案生成需要**约束条件前置**（数据/算力/时间），才能得到可执行的方案。

### 6. Skill构建建议
基于以上调研，科研辅助Skill应包含以下核心能力模块：
1. **文献检索模块**：多数据库检索式生成 + API调用
2. **论文解析模块**：结构化提取（三遍法自动化）
3. **Gap分析模块**：跨论文横向对比分析
4. **实验设计模块**：baseline推荐 + 消融方案生成
5. **数据集推荐模块**：任务匹配 + 质量评估
6. **写作辅助模块**：论文结构生成 + 相关工作撰写

#### 超参数与随机性控制
- 固定随机种子（random seed）并报告
- 超参数搜索：Grid Search / Random Search / Bayesian Optimization
- 使用验证集调参，测试集只用一次（避免test set leakage）

### 4.2 Baseline选择策略

**分层Baseline体系：**

```
Level 0: Trivial baseline（随机猜测、多数类）
Level 1: 经典方法（SVM、Random Forest、LSTM）
Level 2: 预训练模型（BERT、ResNet、GPT-2）
Level 3: 当前领域SOTA
Level 4: 本文提出方法
```

**选择原则：**
- 公平对比：相同数据集、相同评估协议
- 复现优先：优先使用官方代码复现，记录复现结果与原文差异
- 计算公平：若计算资源差异大，需单独说明

### 4.3 评估指标选择

| 任务类型 | 主要指标 | 辅助指标 |
|----------|----------|----------|
| 分类 | Accuracy, F1, AUC-ROC | Precision, Recall, MCC |
| 回归 | RMSE, MAE | R², MAPE |
| NLP生成 | BLEU, ROUGE, BERTScore | Perplexity, Human eval |
| 信息检索 | NDCG, MAP, MRR | Precision@K, Recall@K |
| 目标检测 | mAP | IoU, FPS |
| 聚类 | NMI, ARI | Silhouette Score |

**指标选择原则：**
- 与领域惯例一致（便于横向对比）
- 多指标互补（单一指标可能误导）
- 报告置信区间而非单点值

### 4.4 可复现性最佳实践

**代码层面：**
- 固定所有随机种子（Python random, NumPy, PyTorch/TensorFlow）
- 环境管理：`requirements.txt` / `conda env export` / Docker镜像
- 配置文件化：所有超参数写入config文件（YAML/JSON），不hardcode

**实验管理工具：**
- **MLflow**：实验追踪、模型注册、参数记录
- **Weights & Biases (W&B)**：可视化、超参数扫描、团队协作
- **DVC**：数据版本控制，与Git集成
- **Hydra**：配置管理框架

**报告层面：**
- 完整报告：数据集版本、模型架构、训练细节、硬件环境
- 提供预训练模型checkpoint
- 开源代码（GitHub + Zenodo存档）
- 数据处理脚本完整公开

---

## 5. AI辅助科研的Prompt策略

### 5.1 文献总结Prompt模板

#### 单篇论文深度总结
```
你是一位资深科研助手。请对以下论文进行结构化分析：

[粘贴论文Abstract/全文]

请按以下框架输出：
1. **核心问题**：本文解决什么问题？为什么重要？
2. **主要贡献**：列出3-5个具体创新点
3. **方法概述**：核心方法/模型架构（100字以内）
4. **实验设置**：数据集、baseline、评估指标
5. **关键结果**：最重要的定量结果（含数字）
6. **局限性**：作者承认或你发现的局限
7. **Future Work**：论文提出或你认为的后续方向
8. **与[你的研究方向]的关联**：[填入你的研究方向]
```

#### 批量论文快速筛选
```
以下是[N]篇论文的标题和摘要。请判断每篇与"[研究主题]"的相关性，
输出格式：
- 高度相关（核心方法/数据集直接匹配）
- 部分相关（方法或场景有参考价值）
- 不相关

对高度相关的论文，额外说明相关原因（1句话）。

[论文列表]
```

### 5.2 Research Gap识别Prompt

#### 从综述中识别gap
```
你是科研方法论专家。我将提供一个领域的若干代表性论文摘要。
请帮我识别：

1. **已解决的问题**：当前方法已经做得较好的方面
2. **部分解决的问题**：有进展但仍有明显不足
3. **未解决的问题**：现有方法完全没有涉及或效果很差
4. **矛盾发现**：不同论文之间存在相互矛盾的结论
5. **方法迁移机会**：其他领域的成熟方法可以迁移到本领域

请为每个gap评估：重要性（高/中/低）× 可行性（高/中/低）

[论文摘要列表]
```

#### 研究问题精炼
```
我有一个初步研究想法：[描述你的想法]

请帮我：
1. 将其转化为可操作的研究问题（RQ）
2. 识别这个RQ的前提假设
3. 列出验证这个RQ需要的关键实验
4. 指出潜在的反驳论点（counter-arguments）
5. 建议3个相关的已有工作作为起点
```

### 5.3 方法论设计Prompt

#### 实验方案生成
```
我正在研究：[研究问题]
现有方法的主要局限：[局限描述]
我的核心思路：[方法思路]

请帮我设计完整实验方案，包括：
1. **数据集选择**：推荐3-5个合适的benchmark，说明选择理由
2. **Baseline设计**：
   - Trivial baseline
   - 经典方法baseline（2-3个）
   - SOTA baseline（2-3个）
3. **消融实验设计**：列出需要验证的每个组件
4. **评估指标**：主指标 + 辅助指标，说明选择理由
5. **统计显著性**：建议的检验方法
6. **预期结果**：如果方法有效，各实验应呈现什么模式？
```

#### 方法创新点强化
```
我的方法：[方法描述]

请从以下角度分析并提出改进建议：
1. 理论支撑：是否有理论保证？能否加入收敛性分析？
2. 计算效率：时间/空间复杂度，与baseline对比
3. 泛化性：方法是否依赖特定假设？如何增强泛化？
4. 可解释性：能否提供可视化或解释性分析？
5. 工程实用性：实际部署的障碍是什么？
```

### 5.4 文献检索策略Prompt

#### 关键词扩展
```
我的研究主题是：[主题]

请帮我生成：
1. 核心关键词（5-8个）
2. 同义词/近义词扩展
3. 上位概念（broader terms）
4. 下位概念（narrower terms）
5. 相关概念（related terms）
6. 适合arXiv的搜索式（使用ti: abs: 字段）
7. 适合Google Scholar的搜索式
8. 适合PubMed的MeSH Terms（如适用）
```

#### 论文重要性评估
```
以下论文被引用了[N]次，发表于[年份]，来自[会议/期刊]。
标题：[标题]
摘要：[摘要]

请评估：
1. 这篇论文在领域中的地位（奠基性/重要进展/边缘工作）
2. 引用数是否与其实际影响力匹配（被过誉/被低估）
3. 是否值得精读（给出明确建议）
4. 如果精读，重点关注哪些章节
```

### 5.5 写作辅助Prompt

#### Introduction写作框架
```
帮我为以下研究写Introduction框架：
- 研究领域：[领域]
- 核心问题：[问题]
- 现有方法局限：[局限]
- 本文贡献：[贡献]

按照"漏斗结构"组织：
1. 领域重要性（2-3句，宏观背景）
2. 具体问题定义（2-3句）
3. 现有方法综述及不足（3-5句）
4. 本文方法概述（2-3句）
5. 主要贡献列表（bullet points，3-5条）
6. 论文结构说明（1-2句）
```

---

## 6. 科研工作流整体设计

### 6.1 AI辅助科研完整Pipeline

```
阶段1：问题定义
├── 领域调研（AI辅助关键词扩展 + 数据库检索）
├── 文献聚类（按方法/数据集/任务分类）
└── Gap分析（AI辅助识别未解决问题）

阶段2：方案设计
├── 方法创新点设计
├── 实验方案规划（AI辅助生成baseline列表）
└── 数据集选择（多平台检索 + 质量评估）

阶段3：实验执行
├── 环境配置（Docker/conda，固定seed）
├── Baseline复现（官方代码优先）
├── 消融实验（逐组件验证）
└── 实验追踪（MLflow/W&B）

阶段4：结果分析
├── 定量分析（统计显著性检验）
├── 定性分析（case study，error analysis）
└── AI辅助结果解读

阶段5：论文写作
├── AI辅助生成初稿框架
├── Related Work自动化整理
└── 图表设计建议
```

### 6.2 推荐工具栈

| 环节 | 工具 | 用途 |
|------|------|------|
| 文献检索 | Semantic Scholar API, arXiv API | 程序化批量检索 |
| 文献管理 | Zotero + Better BibTeX | 引用管理 |
| 笔记系统 | Obsidian + Zotero插件 | 知识图谱 |
| 数据集 | HuggingFace datasets库 | 一行代码加载 |
| 实验追踪 | Weights & Biases | 可视化+协作 |
| 数据版本 | DVC | 数据集版本控制 |
| 环境管理 | conda + Docker | 可复现环境 |
| 论文写作 | Overleaf + GitHub | 协作LaTeX |

---

## 关键发现摘要

### 1. GitHub项目生态现状
当前AI科研辅助项目整体star数偏低（最高~1000），说明该领域仍处于早期阶段，存在较大的工具建设机会。主流架构已收敛到**多Agent + RAG**模式，领域专化（尤其生物医学）比通用方案更受欢迎。

### 2. 文献调研的核心瓶颈
最耗时的环节是**初筛**（title/abstract screening）和**数据提取**，这两个环节最适合AI自动化。PRISMA 2020是SLR的行业标准，任何科研辅助工具都应支持其流程。Semantic Scholar提供免费API（2.33亿篇），是程序化检索的最佳入口。

### 3. 数据集发现的最优路径
- **ML任务**：HuggingFace Datasets（90万+）→ Papers with Code（与benchmark绑定）
- **跨领域**：Google Dataset Search（元搜索）
- **生物医学**：PubMed + PhysioNet
- 数据质量评估应优先检查：FAIR合规性、标注一致性（Kappa>0.7）、train/test split合理性

### 4. 实验设计的常见错误
- 只与弱baseline对比（cherry-picking）
- 单次运行不报置信区间
- 测试集多次使用导致过拟合
- 消融实验不完整（无法证明各组件贡献）
- 超参数在测试集上调优（数据泄露）

### 5. Prompt策略的核心原则
- **结构化输出**：要求AI按固定框架输出，便于后续处理
- **角色设定**：明确AI扮演"资深科研助手"角色
- **分层任务**：复杂任务拆分为多个子prompt，逐步深入
- **验证闭环**：AI生成的方案需要用工具验证（检索数据库确认gap真实存在）

### 6. 构建科研辅助Skill的优先级建议

```
P0（核心功能）：
- 论文结构化总结（Abstract → 5W1H）
- 关键词扩展 + 检索式生成
- Research gap识别

P1（高价值功能）：
- 实验方案自动生成
- Baseline推荐
- 数据集推荐（按任务类型）

P2（增强功能）：
- 统计显著性分析辅助
- Related work自动整理
- Introduction框架生成
```

---

*报告生成时间：2026-03-12 | 基于公开资料调研整理*

