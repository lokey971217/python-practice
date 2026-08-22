# RAG 基础学习项目

## 项目目标

这个项目用一个虚构的实验室知识库演示 RAG（Retrieval-Augmented Generation，检索增强生成）的基本链路，并对比两种检索方式：

- `simple_rag.py`：使用问题与知识片段的字符重合度进行关键词检索。
- `semantic_rag.py`：使用中文 Embedding 模型进行语义向量检索。

两个程序都会先检索本地 `knowledge.txt`，再把用户问题和检索到的上下文交给 DeepSeek 生成回答。本项目用于学习和面试展示，不是生产级系统。

## RAG 基本流程

```text
读取本地知识库
  → 按空行切分知识片段
  → 将问题与知识片段进行相关性比较
  → 选出最相关片段
  → 把问题和检索上下文组成 Prompt
  → DeepSeek 基于上下文生成回答
```

RAG 的关键点是先从外部知识中找到相关上下文，再让模型回答，从而降低模型脱离资料编造答案的风险。

## 两种检索方式

| 对比项 | 关键词检索 `simple_rag.py` | 语义检索 `semantic_rag.py` |
| --- | --- | --- |
| 表示方法 | 问题中的去重字符 | BGE 中文语义向量 |
| 相关性计算 | 字符重合数量 | 归一化向量点积 |
| 最佳结果选择 | 遍历并保留最高分片段 | `argmax()` 选择最高相似度片段 |
| 语义理解 | 较弱，依赖字面重合 | 能识别部分不同表达下的相近含义 |
| 无关问题处理 | 没有最低分阈值 | 低于 `0.55` 时拒绝回答 |
| 运行成本 | 低 | 需要加载本地 Embedding 模型 |

语义检索使用 `BAAI/bge-small-zh-v1.5`。知识片段和问题编码时都设置 `normalize_embeddings=True`，所以两个归一化向量的点积可以用于比较余弦相似度。

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
- 使用最低相关度阈值拒绝明显无关的问题。
- 将检索上下文交给 DeepSeek 生成答案。
- 模型或接口调用失败时返回 `模型调用失败：...`。
- 延迟初始化 BGE 模型和 DeepSeek 客户端，导入模块和运行单元测试时不会自动联网。

代码中还保留了一个学习用的 `retrieve_top_k_chunks()` 辅助函数，但当前主流程和答案生成仍然只使用一个最佳片段；Top-K 多片段检索尚未完整接入。

## 项目结构

```text
rag_basics/
├── knowledge.txt          # 虚构的实验室知识库
├── simple_rag.py          # 关键词/字符重合度 RAG
├── semantic_rag.py        # BGE 语义向量 RAG
├── test_simple_rag.py     # 关键词版的 3 项测试
├── test_semantic_rag.py   # 语义版的 4 项测试
├── requirements.txt       # 项目直接依赖
└── README.md              # 项目说明
```

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

首次运行语义版时，`sentence-transformers` 会下载 BGE 模型。下载后的 Hugging Face 缓存是本地运行数据，不应提交到 Git。未设置 `HF_TOKEN` 的公开模型下载警告通常不影响运行。

## 安全配置 DeepSeek API Key

只在当前 PowerShell 会话中设置环境变量：

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key-here"
```

只检查变量是否存在，不输出密钥内容：

```powershell
if ($env:DEEPSEEK_API_KEY) { "DEEPSEEK_API_KEY 已设置" } else { "DEEPSEEK_API_KEY 未设置" }
```

代码仅通过 `os.getenv("DEEPSEEK_API_KEY")` 读取密钥。不要把真实密钥写入 Python 文件、README、日志或 `.env` 并提交到 Git。

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

## 运行检查和测试

基础语法检查：

```powershell
python -m py_compile simple_rag.py semantic_rag.py test_simple_rag.py test_semantic_rag.py
```

运行全部测试：

```powershell
python -m unittest discover -v
```

测试中的 DeepSeek 调用使用 `unittest.mock.patch` 替换，Embedding 模型初始化也被 mock，因此不会产生真实 API 请求、费用或模型下载。

## 7 项自动化测试

`test_simple_rag.py` 包含 3 项：

1. `test_split_knowledge`：验证按空行切片并保留片段内容。
2. `test_retrieve_best_chunk`：验证关键词检索返回最相关片段。
3. `test_relevant_chunk_has_higher_score`：验证相关片段得分高于无关片段。

`test_semantic_rag.py` 包含 4 项：

1. `test_split_knowledge`：验证语义版同样正确切分和过滤知识片段。
2. `test_retrieve_best_chunk`：使用 mock 问题向量验证点积、`argmax()` 和最佳片段选择。
3. `test_generate_answer`：使用 mock DeepSeek 响应验证答案内容和调用发生一次。
4. `test_generate_answer_handles_error`：模拟网络异常并验证返回清晰错误信息。

## 核心知识点

- 文本切片：把长知识文本拆成可以独立检索的上下文单元。
- Embedding：把中文问题和知识片段转换为数值向量。
- 向量归一化：让向量长度为 1，便于用点积比较方向相似性。
- 语义相似度：衡量问题与知识片段在语义上的接近程度。
- `argmax()`：返回最高相似度所在的位置，再映射回知识片段。
- 相关度阈值：最高相似度低于阈值时拒绝把无关上下文交给模型。
- 基于检索上下文生成：将问题和已检索片段共同发送给 DeepSeek。
- `unittest` 与 mock：隔离外部模型和网络调用，稳定验证本地逻辑。

## 当前局限

- 知识库规模小，切片只依据空行，没有按标题、长度或语义分块。
- 关键词版无法真正理解近义表达，也没有无关问题阈值。
- 语义版的阈值 `0.55` 是学习项目中的经验值，尚未通过数据集评估。
- 当前主流程只把一个最佳片段交给模型，可能遗漏分散在多个片段中的信息。
- 每次启动语义版都会重新计算知识片段向量。
- 没有向量数据库、检索结果持久化、来源引用或 Web 界面。

## 下一步计划

- 将 Top-K 辅助检索完整接入主流程和 Prompt，一次使用多个相关片段。
- 增加多片段排序、去重和上下文长度控制。
- 为阈值拒答、空知识库和 Top-K 边界情况补充测试。
- 缓存知识向量，避免每次启动重复编码。
- 在理解本地向量检索后尝试 FAISS、Chroma 等向量数据库。
- 在最终答案中标明引用的知识片段来源。
