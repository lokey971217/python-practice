# RAG 基础学习项目

## 项目目标

这个项目用一个虚构的实验室知识库演示 RAG（Retrieval-Augmented Generation，检索增强生成）的基本链路，并对比两种检索方式：

- `simple_rag.py`：使用问题与知识片段的字符重合度进行关键词检索。
- `semantic_rag.py`：使用中文 Embedding 模型进行语义向量检索。
- `rag_tool.py`：将语义检索进一步封装为可复用的知识库搜索工具。

两个 RAG 程序都会先检索本地 `knowledge.txt`，再把用户问题和检索到的上下文交给 DeepSeek 生成回答。

`rag_tool.py` 不直接生成最终回答，而是返回结构化检索结果，便于后续注册为 Function Calling 工具并接入 Agent。

本项目用于学习和面试展示，不是生产级系统。

---

## RAG 基本流程

```text
读取本地知识库
  → 按空行切分知识片段
  → 将知识片段转换为可检索数据
  → 将用户问题转换为查询向量
  → 计算问题与知识片段的相关性
  → 选出 Top-1 或 Top-K 相关片段
  → 过滤低相关度结果
  → 将问题和检索上下文组成 Prompt
  → DeepSeek 基于上下文生成回答
```

RAG 的关键点是先从外部知识中找到相关上下文，再让模型回答，从而降低模型脱离资料编造答案的风险。

---

## 两种检索方式

| 对比项 | 关键词检索 `simple_rag.py` | 语义检索 `semantic_rag.py` |
| --- | --- | --- |
| 表示方法 | 问题中的去重字符 | BGE 中文语义向量 |
| 相关性计算 | 字符重合数量 | 归一化向量点积 |
| 最佳结果选择 | 遍历并保留最高分片段 | `argmax()` 选择最高相似度片段 |
| Top-K | 未作为主要检索方式 | 已实现 |
| 语义理解 | 较弱，依赖字面重合 | 能识别部分不同表达下的相近含义 |
| 无关问题处理 | 没有最低分阈值 | 支持最低相关度阈值 |
| 运行成本 | 低 | 需要加载本地 Embedding 模型 |

语义检索使用 `BAAI/bge-small-zh-v1.5`。

知识片段和问题编码时都设置：

```python
normalize_embeddings=True
```

因此两个归一化向量的点积可以用于比较余弦相似度。

---

## 已实现功能

### 关键词版

- 以 UTF-8 读取 `knowledge.txt`。
- 按空行切分知识片段，并过滤空片段。
- 统计问题字符与知识片段的重合数量。
- 选择得分最高的一个知识片段。
- 通过 OpenAI Python SDK 兼容接口调用 DeepSeek。
- 捕获模型调用异常并返回清晰错误信息。

### 语义向量版

- 使用 `BAAI/bge-small-zh-v1.5` 生成中文 Embedding。
- 对知识片段向量和问题向量进行归一化。
- 使用向量点积计算语义相似度。
- 使用 `argmax()` 选择最相关的一个知识片段。
- 实现 `retrieve_top_k_chunks()`，支持返回多个高相关片段。
- 使用最低相关度阈值拒绝明显无关的问题。
- 将检索上下文交给 DeepSeek 生成答案。
- 模型或接口调用失败时返回 `模型调用失败：...`。
- 将 Embedding 和 DeepSeek 调用拆分为可测试的函数。

### RAG Tool

新增 `rag_tool.py`，将语义检索封装为：

```python
search_knowledge_base(question, top_k=2)
```

该函数会：

1. 接收用户问题。
2. 对问题进行语义向量化。
3. 从本地知识库中执行 Top-K 检索。
4. 根据最低相关度阈值判断是否找到有效知识。
5. 返回统一的结构化结果。

示例：

```python
{
    "found": True,
    "question": "实验设备需要提前多久预约？",
    "chunks": [
        {
            "content": "【设备预约规定】...",
            "score": 0.8746
        },
        {
            "content": "【设备使用要求】...",
            "score": 0.5629
        }
    ]
}
```

这一层封装使 RAG 检索能力可以被其他 Python 程序直接调用，也为下一阶段接入 Function Calling 和 Agent 做准备。

---

## 项目结构

```text
rag_basics/
├── knowledge.txt          # 虚构的实验室知识库
├── simple_rag.py          # 关键词/字符重合度 RAG
├── semantic_rag.py        # BGE 语义向量 RAG
├── rag_tool.py            # 可复用的语义知识库检索工具
├── test_simple_rag.py     # 关键词版测试
├── test_semantic_rag.py   # 语义版测试
├── test_rag_tool.py       # RAG Tool 测试
├── requirements.txt       # 项目直接依赖
├── docs/
│   └── interview_notes.md # 面试复习与项目讲解记录
└── README.md              # 项目说明
```

---

## 环境安装（Windows PowerShell）

进入项目目录：

```powershell
cd F:\git\python-practice\projects\rag_basics
```

创建并激活虚拟环境：

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

安装直接依赖：

```powershell
python -m pip install -r requirements.txt
```

首次运行语义版时，`sentence-transformers` 会下载 BGE 模型。

下载后的 Hugging Face 缓存是本地运行数据，不应提交到 Git。

未设置 `HF_TOKEN` 时出现的公开模型下载警告通常不影响正常运行。

---

## 安全配置 DeepSeek API Key

只在当前 PowerShell 会话中设置环境变量：

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key-here"
```

只检查变量是否存在，不输出密钥内容：

```powershell
if ($env:DEEPSEEK_API_KEY) {
    "DEEPSEEK_API_KEY 已设置"
} else {
    "DEEPSEEK_API_KEY 未设置"
}
```

代码仅通过：

```python
os.getenv("DEEPSEEK_API_KEY")
```

读取密钥。

不要把真实密钥写入 Python 文件、README、日志或 `.env` 并提交到 Git。

---

## 运行程序

关键词检索版：

```powershell
python simple_rag.py
```

语义向量检索版：

```powershell
python semantic_rag.py
```

示例问题：

- `设备需要提前多久预约？`
- `实验结束后数据应该怎么处理？`
- `设备发生故障时应该怎么办？`
- `实验室周末几点开放？`

---

## 调用 RAG Tool

可以直接在其他 Python 程序中调用：

```python
from rag_tool import search_knowledge_base

result = search_knowledge_base(
    "实验设备需要提前多久预约？",
    top_k=2,
)

print(result)
```

返回结果包含：

- `found`：是否找到足够相关的知识。
- `question`：原始用户问题。
- `chunks`：检索到的知识片段列表。
- `content`：知识片段正文。
- `score`：语义相似度分数。

---

## 运行检查和测试

基础语法检查：

```powershell
python -m py_compile \
    simple_rag.py \
    semantic_rag.py \
    rag_tool.py \
    test_simple_rag.py \
    test_semantic_rag.py \
    test_rag_tool.py
```

PowerShell 中也可以直接逐个文件检查。

运行全部测试：

```powershell
python -m unittest discover -v
```

当前测试结果：

```text
Ran 12 tests
OK
```

---

## 12 项自动化测试

### `test_simple_rag.py`：3 项

1. `test_split_knowledge`  
   验证按空行切片并保留片段内容。

2. `test_retrieve_best_chunk`  
   验证关键词检索返回最相关片段。

3. `test_relevant_chunk_has_higher_score`  
   验证相关片段得分高于无关片段。

### `test_semantic_rag.py`：5 项

1. `test_split_knowledge`  
   验证语义版正确切分和过滤知识片段。

2. `test_retrieve_best_chunk`  
   使用 mock 问题向量验证点积、`argmax()` 和最佳片段选择。

3. `test_retrieve_top_k_chunks`  
   验证 Top-K 检索能够按相似度返回多个结果。

4. `test_generate_answer`  
   使用 mock DeepSeek 响应验证答案内容和调用过程。

5. `test_generate_answer_handles_error`  
   模拟网络异常并验证返回清晰错误信息。

### `test_rag_tool.py`：4 项

1. `test_related_question_returns_found_true`  
   验证相关问题返回 `found=True`。

2. `test_unrelated_question_returns_found_false`  
   验证无关问题返回 `found=False`。

3. `test_top_k_limits_number_of_chunks`  
   验证 `top_k=2` 时返回片段数量不超过 2。

4. `test_each_chunk_contains_content_and_score`  
   验证每个结果片段都包含 `content` 和 `score`。

测试中的 DeepSeek 调用使用 `unittest.mock.patch` 替换，因此不会产生真实 API 请求或费用。

语义检索测试中也使用 Mock 控制问题向量，使测试重点放在本地检索逻辑，而不是依赖模型本身的随机性或外部网络状态。

---

## 核心知识点

- 文本切片：把长知识文本拆成可以独立检索的上下文单元。
- Embedding：把中文问题和知识片段转换为数值向量。
- 向量归一化：让向量长度为 1，便于用点积比较方向相似性。
- 语义相似度：衡量问题与知识片段在语义上的接近程度。
- `argmax()`：返回最高相似度所在的位置，再映射回知识片段。
- Top-K：不只返回一个最佳片段，而是保留多个高相关候选结果。
- 相关度阈值：最高相似度不足时，不把无关知识当作有效检索结果。
- Context：把检索到的知识和用户问题共同发送给大模型。
- 结构化返回：使用统一字典结构向其他模块提供检索结果。
- `unittest` 与 Mock：隔离外部模型和网络调用，稳定验证本地逻辑。

---

## 求职展示能力

这个项目能够体现以下实际开发能力：

### Python 工程

- 函数拆分和模块导入。
- 类型注解。
- 文件读写。
- 异常处理。
- 环境变量管理。
- 字典和列表结构化数据处理。
- `unittest` 自动化测试。
- `MagicMock` 和 `patch`。

### 大模型应用开发

- 使用 OpenAI Compatible SDK 调用 DeepSeek。
- 构造 System Prompt 和 User Prompt。
- 将检索结果作为 Context 提供给模型。
- 处理模型调用失败等异常场景。

### RAG

- 文本切片。
- Embedding。
- 语义向量检索。
- Top-1 / Top-K。
- 相关度阈值过滤。
- 无关问题拒答。
- 将检索能力封装为可复用工具。

### Agent 前置能力

`search_knowledge_base()` 已经具备明确输入和结构化输出，因此可以进一步注册为 Function Calling 工具。

下一阶段可以让大模型自主判断：

```text
当前问题是否需要查知识库？
        ↓
如果需要
        ↓
调用 search_knowledge_base()
        ↓
获取知识
        ↓
继续生成最终答案
```

---

## 面试时可以如何介绍

可以简要描述为：

> 使用 Python 从零实现了一个轻量级 RAG 知识库项目。先实现关键词检索作为基础版本，再使用 BGE 中文 Embedding 实现语义检索，并加入 Top-K 和最低相关度阈值。之后把检索能力封装成 `search_knowledge_base()` 工具，返回统一的结构化结果，为后续 Function Calling 和 Agent 接入做准备。项目使用 `unittest`、`MagicMock` 和 `patch` 对检索逻辑和 DeepSeek API 调用进行了自动化测试，目前共有 12 项测试通过。

更详细的面试复习内容放在：

```text
docs/interview_notes.md
```

---

## 当前局限

- 知识库规模较小。
- 切片只依据空行，没有按标题、长度或语义分块。
- 关键词版无法真正理解近义表达，也没有无关问题阈值。
- 语义版阈值 `0.55` 是学习项目中的经验值，尚未通过数据集评估。
- `semantic_rag.py` 的交互式回答流程仍以最佳片段为主。
- `rag_tool.py` 已支持 Top-K，但尚未增加 rerank。
- 每次启动仍需要准备知识片段向量，没有向量数据库或持久化索引。
- 没有来源引用机制。
- 没有 Web UI。
- 尚未部署为服务。

---

## 下一步计划

当前 RAG 阶段的重点能力已经完成。

下一步不继续无限扩展 RAG，而是将已有能力组合起来：

```text
Function Calling
        +
search_knowledge_base()
        ↓
      Agent
```

计划：

1. 将 `search_knowledge_base()` 定义为 Function Calling 工具。
2. 让大模型判断用户问题是否需要查询知识库。
3. 执行本地 RAG Tool。
4. 将工具结果返回给模型。
5. 由模型生成最终回答。
6. 补充 Agent 主流程测试。
7. 将完整项目提交到 GitHub 作品集。

目标是从：

```text
“能运行的 RAG Demo”
```

继续升级为：

```text
“能够自主选择工具并执行任务的 AI Agent”
```
