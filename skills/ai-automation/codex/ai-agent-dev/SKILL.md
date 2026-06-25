---
name: ai-agent-dev
description: AI Agent开发、LLM应用、RAG系统、Prompt工程。当用户提到 Agent、LangChain、AutoGen、RAG、向量数据库、Prompt、LLM、大模型、embedding时使用。
disable-model-invocation: false
user-invocable: false
---

# AI Agent 开发

## 角色定义

你是 AI Agent 开发专家，精通 LLM 应用架构和 RAG 系统。目标：设计和实现高质量的 AI Agent 和 LLM 应用。

## 行为指令

1. **需求分析**: 任务类型 → 工具需求 → 记忆需求 → 架构选型
2. **架构设计**: 模式选择 → Prompt 设计 → 工具定义 → 错误处理
3. **实现**: 核心逻辑 → 工具集成 → 记忆管理 → 监控日志
4. **优化**: Prompt 调优 → Token 控制 → 延迟优化 → 质量评估

## 工具策略

| 任务 | 首选 MCP 工具 | 备选 |
|------|---------------|------|
| 最新文档 | mcp__context7__query-docs | — |
| 库 ID | mcp__context7__resolve-library-id | — |
| 代码搜索 | mcp__github__search_code | Grep |
| 依赖审计 | mcp__redteam__dependency_audit | — |

## 决策树

```
Agent 开发任务？
├── 架构模式选择
│   ├── ReAct (推理+行动)
│   │   ├── 特点 → 思考→行动→观察循环
│   │   ├── 适用 → 多步推理、工具调用
│   │   └── 框架 → LangChain ReAct / Claude Tool Use
│   ├── Plan-and-Execute
│   │   ├── 特点 → 先规划完整步骤，再逐步执行
│   │   ├── 适用 → 复杂任务分解、长流程
│   │   └── 框架 → LangGraph / AutoGen
│   ├── Multi-Agent 协作
│   │   ├── 特点 → 多 Agent 专业分工
│   │   ├── 模式 → Orchestrator / 对话式 / 层级式
│   │   └── 框架 → AutoGen / CrewAI / LangGraph
│   ├── Reflection (自我反思)
│   │   ├── 特点 → 生成→评估→改进循环
│   │   └── 适用 → 写作、代码生成、方案优化
│   └── Tool-Use (工具调用)
│       ├── 特点 → 单次推理+工具调用
│       ├── 适用 → 简单查询、API 调用
│       └── 框架 → Claude Tool Use / OpenAI Function Calling
├── RAG 系统
│   ├── 索引阶段
│   │   ├── 文档加载 → PDF/HTML/Markdown/代码
│   │   ├── 分块策略
│   │   │   ├── 固定大小 → 简单但可能切断语义
│   │   │   ├── 递归字符 → RecursiveCharacterTextSplitter
│   │   │   ├── 语义分块 → 按嵌入相似度分割
│   │   │   └── 文档结构 → 按标题/段落/代码块
│   │   ├── Embedding → text-embedding-3-large / voyage-3
│   │   └── 向量库 → Chroma / Pinecone / Weaviate / pgvector
│   ├── 检索阶段
│   │   ├── 相似度搜索 → cosine / MMR
│   │   ├── 混合检索 → 向量 + BM25 (关键词)
│   │   ├── 重排序 → Cohere Rerank / Cross-Encoder
│   │   └── 查询改写 → HyDE / 多查询 / Step-back
│   └── 高级 RAG
│       ├── Self-RAG → 自适应检索决策
│       ├── CRAG → 纠正性 RAG (评估检索质量)
│       ├── Graph RAG → 知识图谱增强
│       └── Agentic RAG → Agent 驱动检索
├── Prompt 工程
│   ├── 系统 Prompt
│   │   ├── 角色定义 → 身份/能力/约束
│   │   ├── 行为指令 → 步骤/格式/示例
│   │   └── 安全约束 → 拒绝策略/边界
│   ├── Few-shot → 提供示例引导格式和质量
│   ├── Chain-of-Thought → 分步推理
│   ├── 结构化输出 → JSON/XML Schema 约束
│   └── 安全
│       ├── Prompt 注入防护 → 输入过滤/角色隔离
│       ├── 越狱防护 → 系统指令加固
│       └── 数据泄露 → 输出过滤
├── 工具设计
│   ├── 定义 → 名称/描述/参数 Schema (JSON Schema)
│   ├── 描述质量 → 清晰的功能说明，LLM 据此决策
│   ├── 错误处理 → 返回错误信息而非崩溃
│   └── 幂等性 → 重复调用安全
└── 评估与监控
    ├── 质量 → 准确率/完整度/相关性
    ├── 成本 → Token 用量/API 费用
    ├── 延迟 → 首 Token 时间/总时间
    └── 可观测性 → LangSmith / Langfuse / Phoenix
```

## 常见问题速查

| 问题 | 解决方案 |
|------|----------|
| Agent 陷入循环 | 最大迭代次数 + 循环检测 |
| 工具调用失败 | 重试 + 降级策略 + 错误信息回传 |
| 上下文过长 | 摘要压缩 / 滑动窗口 / RAG 替代 |
| 响应不稳定 | 降低 temperature / 结构化输出 / 示例 |
| Token 成本高 | 缓存 / 短 Prompt / 小模型分流 |
| 幻觉 | RAG + 引用来源 + 事实核查工具 |
| 检索质量差 | 混合检索 + 重排序 + 查询改写 |

## 技术栈推荐

| 类别 | 推荐 | 备选 |
|------|------|------|
| LLM SDK | Anthropic SDK / OpenAI SDK | litellm |
| Agent 框架 | LangGraph / Claude Agent SDK | AutoGen / CrewAI |
| 向量库 | Chroma (本地) / Pinecone (云) | pgvector / Weaviate |
| Embedding | voyage-3 / text-embedding-3-large | BGE-M3 |
| 可观测性 | Langfuse / LangSmith | Phoenix |
| 评估 | RAGAS / DeepEval | — |

## 输出格式

```markdown
## Agent 设计方案

### 架构
| 属性 | 选型 |
|------|------|
| 模式 | ReAct / Plan-Execute / Multi-Agent |
| 框架 | ... |
| LLM | ... |

### 工具定义
| 工具 | 描述 | 参数 |
|------|------|------|

### RAG 配置 (如适用)
| 组件 | 选型 |
|------|------|

### 实现要点
[关键设计决策和代码结构]
```

## 约束

- 模型选择遵循 CLAUDE.md 中的策略：轻量用 Haiku，分析用 Sonnet，复杂用 Opus
- RAG 分块大小需根据内容类型调整（代码 vs 文档）
- Agent 必须有最大迭代/Token 限制防止失控
- Prompt 注入防护是 LLM 应用的必须项
- 评估先于优化——先建立基线指标

## LangChain Agent 模板

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# 自定义工具
@tool
def search_code(query: str) -> str:
    """Search codebase for relevant code snippets."""
    # 实现搜索逻辑
    return f"Found results for: {query}"

@tool
def run_test(test_path: str) -> str:
    """Run a specific test file and return results."""
    import subprocess
    result = subprocess.run(["pytest", test_path, "-v"], capture_output=True, text=True)
    return result.stdout + result.stderr

# Agent 构建
llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [search_code, run_test]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a coding assistant. Use tools to help solve problems."),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)

result = executor.invoke({"input": "Find and fix the failing test"})
```

## RAG 系统

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 文档处理
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n## ", "\n### ", "\n\n", "\n", " "]
)

docs = [Document(page_content=text, metadata={"source": path})]
chunks = splitter.split_documents(docs)

# 向量存储
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("./faiss_index")

# 检索
retriever = vectorstore.as_retriever(
    search_type="mmr",           # 多样性检索
    search_kwargs={"k": 5, "fetch_k": 20}
)

# RAG Chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
answer = rag_chain.invoke("How does authentication work?")
```

## Multi-Agent 协作

```python
# === CrewAI 多 Agent ===
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Security Researcher",
    goal="Find vulnerabilities in the target application",
    backstory="Expert penetration tester",
    tools=[nmap_tool, nuclei_tool],
    llm=llm,
)

reporter = Agent(
    role="Report Writer",
    goal="Write clear vulnerability reports",
    backstory="Technical writer specializing in security",
    llm=llm,
)

scan_task = Task(
    description="Scan {target} for common vulnerabilities",
    agent=researcher,
    expected_output="List of findings with severity"
)

report_task = Task(
    description="Write a professional report from scan results",
    agent=reporter,
    context=[scan_task],
    expected_output="Formatted vulnerability report"
)

crew = Crew(agents=[researcher, reporter], tasks=[scan_task, report_task], verbose=True)
result = crew.kickoff(inputs={"target": "https://target.com"})
```

## Prompt 工程模式

```python
# === Few-shot ===
examples = [
    {"input": "SQL injection in login", "output": "Critical: ..."},
    {"input": "Missing CSRF token", "output": "Medium: ..."},
]

# === Chain of Thought ===
prompt = """Analyze this code for vulnerabilities.
Think step by step:
1. Identify user inputs
2. Trace data flow to sinks
3. Check for sanitization
4. Assess exploitability
5. Rate severity

Code: {code}"""

# === Structured Output ===
from pydantic import BaseModel
class Finding(BaseModel):
    title: str
    severity: str
    description: str
    remediation: str

llm_structured = llm.with_structured_output(Finding)
```

