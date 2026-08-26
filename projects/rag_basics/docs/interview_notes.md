# RAG 项目面试复习笔记

## 使用说明

这份文件用于面试前快速复习 `rag_basics` 项目。

项目核心不是“我学过 RAG”，而是：

> 我使用 Python 从零实现了关键词检索和基于 BGE Embedding 的语义检索，并进一步加入 Top-K、相关度阈值、DeepSeek 回答、结构化检索结果和自动化测试，最后把语义检索封装成可供 Agent 调用的 `search_knowledge_base()` 工具。

面试时优先讲：

1. 为什么做这个项目。
2. RAG 的完整流程。
3. 关键词检索和语义检索的区别。
4. Embedding、Top-K、阈值分别解决什么问题。
5. 为什么要把检索封装成工具。
6. 如何使用 `unittest`、`mock` 和 `patch` 做测试。
7. 下一步如何接入 Function Calling 和 Agent。

---

## 30 秒项目介绍

> 我做了一个轻量级 RAG 知识库项目。最开始先实现了关键词检索作为基础版本，之后使用 `BAAI/bge-small-zh-v1.5` 把知识片段和用户问题转换成语义向量，通过归一化向量点积计算相似度，并实现了 Top-1、Top-K 和最低相关度阈值。检索到知识后，再把 Context 交给 DeepSeek 生成答案。后来我又把检索逻辑封装成 `search_knowledge_base()` 工具，并使用 `unittest`、`MagicMock` 和 `patch` 编写自动化测试，目前整个项目有 12 项测试通过。

---

## 1 分钟项目介绍

> 这个项目主要是为了完整理解和实现 RAG 的基本链路。我先做了一个 `simple_rag.py`，用字符重合度实现最简单的关键词检索，用它作为 Baseline。然后做了 `semantic_rag.py`，使用 `BAAI/bge-small-zh-v1.5` 对知识片段和问题做 Embedding，并设置 `normalize_embeddings=True`，这样可以直接用向量点积比较语义相似度。
>
> 在检索层，我先实现了 Top-1，也就是返回最高相关的一个片段，之后又实现 Top-K，同时加入 `0.55` 的最低相关度阈值，避免知识库完全不相关时仍然强行拿一个“最高分”片段去回答。
>
> 检索完成后，我把相关知识作为 Context 和用户问题一起交给 DeepSeek，并通过 Prompt 约束模型只根据知识库回答。
>
> 后来我又把检索能力封装成 `search_knowledge_base(question, top_k=2)`，返回 `found`、`question`、`chunks`、`content` 和 `score` 等结构化字段，这样它可以直接作为 Agent 的工具使用。
>
> 测试方面，我使用 `unittest`、`MagicMock` 和 `patch` 隔离 Embedding 和外部 API，目前整个 `rag_basics` 项目共有 12 项自动化测试通过。

---

## 项目结构怎么讲

```text
rag_basics/
├── knowledge.txt
├── simple_rag.py
├── semantic_rag.py
├── rag_tool.py
├── test_simple_rag.py
├── test_semantic_rag.py
├── test_rag_tool.py
├── requirements.txt
├── docs/
│   └── interview_notes.md
└── README.md
```

可以这样解释：

- `knowledge.txt`：本地知识库。
- `simple_rag.py`：关键词检索版本。
- `semantic_rag.py`：语义向量检索 + DeepSeek 回答。
- `rag_tool.py`：可复用的知识库搜索工具。
- `test_*.py`：对应不同模块的自动化测试。
- `README.md`：项目说明和运行方式。
- `docs/interview_notes.md`：面试复习材料。

---

## 面试官可能问：RAG 是什么

可以回答：

> RAG 是 Retrieval-Augmented Generation，也就是检索增强生成。它不是直接让大模型依靠自身参数回答，而是先从外部知识库中检索与问题相关的内容，再把这些内容作为 Context 交给模型生成答案。

项目中的实际流程：

```text
用户问题
  ↓
知识库检索
  ↓
找到相关片段
  ↓
构造 Context
  ↓
DeepSeek
  ↓
最终回答
```

---

## 面试官可能问：为什么先写关键词版

可以回答：

> 我先写关键词版是为了建立一个最简单、容易验证的 Baseline。这样可以先把“知识切片 → 检索 → Context → LLM”的完整流程跑通，再把检索部分升级成 Embedding 语义检索。

关键词版主要依赖：

```text
字面字符重合
```

它的优点是：

- 简单。
- 速度快。
- 容易理解和调试。

缺点是：

- 对近义表达不敏感。
- 依赖问题和知识片段出现相同文字。

---

## 面试官可能问：为什么要用 Embedding

可以回答：

> 关键词检索只能比较字面重合，而 Embedding 可以把文本转换成能够表示语义的向量。这样即使用户问题和知识片段没有完全相同的词，只要语义接近，也可能得到较高的相似度。

例如：

```text
知识：
设备需要提前一天预约

问题：
设备应该提前多久申请使用？
```

字面并不完全一致，但语义非常接近。

---

## 面试官可能问：你用了什么 Embedding 模型

项目使用：

```text
BAAI/bge-small-zh-v1.5
```

加载方式：

```python
SentenceTransformer("BAAI/bge-small-zh-v1.5")
```

可以回答：

> 这是一个中文语义向量模型，适合当前中文知识库的学习项目。我主要用它把知识片段和用户问题转换成向量，再进行相似度计算。

---

## 面试官可能问：`normalize_embeddings=True` 是什么

可以回答：

> 它会把 Embedding 向量归一化，使每个向量长度变成 1。归一化后，两个向量的点积可以用来比较方向相似性，也就是可以作为余弦相似度来使用。

项目中使用：

```python
similarities = chunk_vectors @ question_vector
```

因此：

```text
相似度越高
↓
通常表示语义越接近
```

---

## 面试官可能问：Top-1 和 Top-K 有什么区别

Top-1：

```text
只返回最高相关的一个片段
```

Top-K：

```text
返回相关度最高的前 K 个片段
```

可以回答：

> Top-1 实现简单，但答案如果分散在多个知识片段中，可能丢失信息。Top-K 可以保留多个高相关候选片段，为后续组合 Context 提供更多信息。

项目实现：

```python
retrieve_top_k_chunks(...)
```

以及：

```python
search_knowledge_base(question, top_k=2)
```

---

## 面试官可能问：为什么要设置相关度阈值

可以回答：

> 因为无论问题和知识库多么不相关，数学上总能找到一个“最高分”的片段。如果直接把这个片段交给大模型，就可能造成错误回答。所以我设置最低相关度阈值，当最高相关度不足时直接认为知识库没有有效答案。

项目阈值：

```python
MIN_RELEVANCE_SCORE = 0.55
```

要主动说明：

> `0.55` 是当前学习项目中的经验值，没有经过完整数据集评估。

这一点不要包装成“最优阈值”。

---

## 面试官可能问：为什么还要 `found`

`search_knowledge_base()` 会返回：

```python
{
    "found": True,
    "question": "...",
    "chunks": [...]
}
```

可以回答：

> `found` 是给上层程序看的明确状态。如果 `found=False`，Agent 或其他调用者就知道当前知识库没有足够相关的信息，不需要继续把无关 Context 交给模型。

这是把：

```text
检索结果
```

变成：

```text
其他程序可以直接判断的结构化结果
```

---

## 面试官可能问：为什么要封装 `search_knowledge_base()`

可以回答：

> 最开始的 RAG 是一个交互式程序，只适合自己运行。后来我把检索逻辑封装成 `search_knowledge_base()`，让其他 Python 模块可以直接传入问题并获得结构化结果，这样它才能进一步作为 Function Calling 或 Agent 的 Tool。

核心接口：

```python
search_knowledge_base(question, top_k=2)
```

输入：

```text
question
top_k
```

输出：

```text
found
question
chunks
content
score
```

---

## 面试官可能问：RAG 和 Function Calling 有什么区别

可以回答：

> RAG 主要解决“模型怎么获得外部知识”，Function Calling 主要解决“模型怎么调用外部工具执行动作”。

可以这样理解：

```text
RAG
↓
查资料

Function Calling
↓
调用工具

两者结合
↓
Agent
```

当前项目下一阶段就是：

```text
LLM
 ↓
判断是否需要搜索知识库
 ↓
Function Calling
 ↓
search_knowledge_base()
 ↓
返回知识
 ↓
LLM 继续回答
```

---

## 面试官可能问：为什么测试时不用真实 DeepSeek API

可以回答：

> 单元测试应该尽量稳定、快速、可重复。如果每次测试都真实调用 DeepSeek，会受到网络、接口状态和费用影响。因此我使用 `patch` 把真实 API 调用替换成 Mock Response，只测试本地函数能否正确调用接口和解析返回值。

项目中测试的典型思路：

```text
真实 DeepSeek
↓
测试时替换成 Mock
↓
返回预先设计的数据
↓
验证 generate_answer() 的逻辑
```

---

## 面试官可能问：`MagicMock` 是干什么的

可以回答：

> `MagicMock` 用来模拟真实对象。在项目中，我用它模拟 DeepSeek SDK 返回的 `response → choices[0] → message → content` 这一层对象结构，这样不需要真实请求 API，也能验证解析逻辑。

---

## 面试官可能问：`patch` 是干什么的

可以回答：

> `patch` 可以在测试期间临时替换某个函数或对象。例如我会把 `semantic_rag.model.encode` 替换成固定返回值，这样就可以独立验证检索算法，而不是同时测试 Embedding 模型本身。

例如：

```python
@patch("semantic_rag.model.encode")
```

测试重点是：

```text
给定一个已知向量
↓
检索逻辑能不能找到正确片段
```

---

## 面试官可能问：为什么要 Mock Embedding

可以回答：

> 如果单元测试直接依赖真实 Embedding 模型，那么测试结果不仅受本地逻辑影响，还受模型加载和实际输出影响。通过 Mock，我可以人为规定问题向量，比如 `[1.0, 0.0]`，然后确认点积和 `argmax()` 是否得到预期结果。

这属于：

```text
隔离依赖
↓
只测试当前函数职责
```

---

## 面试官可能问：你现在有多少测试

当前：

```text
12 tests
```

分布：

| 文件 | 数量 |
| --- | ---: |
| `test_simple_rag.py` | 3 |
| `test_semantic_rag.py` | 5 |
| `test_rag_tool.py` | 4 |
| 合计 | 12 |

运行：

```powershell
python -m unittest discover -v
```

结果：

```text
Ran 12 tests
OK
```

---

## `test_rag_tool.py` 四项测试怎么讲

### 1. 相关问题

验证：

```text
知识库存在相关内容
↓
found=True
```

### 2. 无关问题

验证：

```text
知识库不存在有效内容
↓
found=False
```

### 3. Top-K

验证：

```text
top_k=2
↓
chunks 数量 <= 2
```

### 4. 结构化结果

验证每个 Chunk 都包含：

```python
{
    "content": ...,
    "score": ...
}
```

---

## 面试官可能问：这个项目现在有什么不足

不要回答“已经很完善”。

可以主动说：

> 这是一个学习和求职展示级项目，当前知识库规模比较小，Chunking 只按空行切分，还没有向量数据库、Embedding 持久化缓存、Rerank 和来源引用机制。相关度阈值也是经验值，并没有经过数据集系统评估。

当前局限包括：

- 知识库规模小。
- 只按空行切片。
- 没有向量数据库。
- 没有向量持久化。
- 没有 Rerank。
- 阈值没有系统评估。
- 没有来源引用。
- 没有 Web UI。
- 尚未部署成服务。

这个回答的重点是：

```text
知道项目边界
+
知道下一步怎么优化
```

而不是假装项目已经达到生产级。

---

## 面试官可能问：如果知识库变大怎么办

当前项目没有实现这一部分，所以不要说“已经做过”。

可以回答：

> 当前项目为了理解 RAG 底层流程，直接在本地对知识片段生成向量并计算相似度。如果知识库规模变大，我会考虑把 Embedding 预先计算并持久化，再使用 FAISS、Chroma 或其他向量数据库做索引和检索，避免每次启动重新计算全部向量。

要明确：

> 这是后续扩展思路，不是当前已经实现的功能。

---

## 面试官可能问：为什么不用 LangChain

可以回答：

> 这个阶段我希望先理解 RAG 的底层链路，所以没有直接用框架把检索过程封装掉。我自己实现了文本切片、Embedding、相似度计算、Top-K、阈值判断和 Context 构造。这样后面再使用 LangChain 或其他框架时，我能理解它们内部主要在帮我做什么。

这个回答与当前项目的学习路线一致。

---

## 面试官可能问：为什么现在还不是完整 Agent

可以回答：

> 当前 `search_knowledge_base()` 已经是一个可复用工具，但现在仍然需要程序主动调用它。真正的 Agent 应该由 LLM 根据用户意图判断是否需要调用这个工具，再执行工具并继续生成最终回答。

当前状态：

```text
RAG Tool
✅
```

下一步：

```text
LLM 自主选择 Tool
↓
Function Calling
↓
RAG
↓
最终回答
```

---

## 面试官可能问：你下一步准备怎么做

可以回答：

> 下一步我会把 `search_knowledge_base()` 注册成 Function Calling 工具，把之前已经实现过的 Function Calling 流程和现在的 RAG Tool 组合起来。目标是让模型自主判断什么时候需要查知识库，而不是每次都固定执行 RAG。

---

## 项目中最值得强调的三点

如果面试时间很短，优先强调：

### 1. 不是只调 API

```text
自己实现了：
Chunking
Embedding
Similarity
Top-K
Threshold
```

### 2. 做了工程化封装

```text
search_knowledge_base()
↓
结构化输入输出
↓
可作为 Agent Tool
```

### 3. 有自动化测试

```text
unittest
MagicMock
patch
12 tests passed
```

---

## 不要这样说

不要说：

> 我精通 RAG。

当前项目不足以支撑“精通”。

不要说：

> 这个阈值 0.55 是最优值。

目前只是经验值。

不要说：

> 我实现了向量数据库。

没有实现。

不要说：

> 我已经实现完整 Agent。

当前还没有正式进入 Agent。

不要说：

> 这是生产级系统。

README 已明确这是学习 / 求职展示级项目。

---

## 推荐说法

可以说：

> 我已经能够独立实现一个基础 RAG 链路，并理解文本切片、Embedding、Top-K、相关度阈值、Context 构造和模型调用的关系。

可以说：

> 我不仅跑通了 RAG，还把语义检索进一步封装成了一个结构化工具接口，并为它补了自动化测试。

可以说：

> 我现在正在把之前做过的 Function Calling 和 RAG Tool 组合起来，继续进入 Agent 阶段。

---

## 面试前 5 分钟快速复习

面试前只看这一段：

```text
项目：
Python 轻量级 RAG 知识库

模型：
BAAI/bge-small-zh-v1.5
DeepSeek

检索：
关键词 Baseline
Semantic Search
Top-1
Top-K
Threshold = 0.55

核心接口：
search_knowledge_base(question, top_k=2)

返回：
found
question
chunks
content
score

测试：
unittest
MagicMock
patch
12 tests passed

下一步：
Function Calling + search_knowledge_base()
→ Agent
```

然后记住一句项目总结：

> 我从零实现了一个轻量级 RAG 知识库系统，并将语义检索封装成可复用的结构化工具接口，通过 12 项自动化测试验证核心逻辑，下一步将它接入 Function Calling 构建 Agent。
