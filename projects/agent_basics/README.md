# Agent 基础项目

## 项目目标

本项目把前一阶段实现的 Function Calling 与 RAG 检索模块组合成一个轻量级 RAG Agent。模型先判断问题是否需要实验室知识库；需要时调用 `search_knowledge_base`，不需要时直接回答。

项目重点是实现并测试一个可复用的 Agent 控制闭环，不将其描述为生产级或完全自主的智能体。

## 当前实现

- 使用 OpenAI Python SDK 的兼容接口调用 DeepSeek。
- 通过 `os.getenv("DEEPSEEK_API_KEY")` 读取密钥，代码中不保存真实密钥。
- 使用 System Prompt 说明助手角色和工具使用场景。
- 用 JSON Schema 定义 `search_knowledge_base` 工具参数。
- 通过 `tool_choice="auto"` 让模型决定是否调用工具。
- 将模型生成的 JSON 参数解析为 Python 字典并执行真实 RAG 函数。
- 将结构化 Tool Result 回传模型，再获取最终自然语言答案。
- 将主流程封装为 `run_agent(user_input: str) -> str`，同时保留命令行入口。
- 对普通回答、RAG 调用闭环和未知工具分支进行 3 项自动化测试。

## Agent 工作流程

```text
用户问题
  ↓
DeepSeek 第一次判断
  ├─ 不需要知识库 → 直接返回模型回答
  └─ 需要知识库
       ↓
     Function Calling 生成工具名与 JSON 参数
       ↓
     Python 解析参数并执行 search_knowledge_base()
       ↓
     返回结构化 RAG 检索结果
       ↓
     Tool Result 携带 tool_call_id 回传 DeepSeek
       ↓
     DeepSeek 第二次调用生成最终答案
```

## Function Calling + RAG

`rag_agent.py` 向模型提供 `search_knowledge_base` 的工具定义。工具参数包括必填的 `question` 和默认值为 `2` 的 `top_k`。

当模型返回 Tool Call 时，程序会：

1. 读取第一个 Tool Call。
2. 用 `json.loads()` 解析 `function.arguments`。
3. 检查工具名称是否为允许执行的 `search_knowledge_base`。
4. 调用上一阶段 `projects/rag_basics/rag_tool.py` 中的真实检索函数。
5. 用 `json.dumps(..., ensure_ascii=False)` 序列化结构化结果。
6. 将原始 Assistant Tool Call 与 `role="tool"` 的结果追加到消息列表。
7. 进行第二次模型调用，得到面向用户的最终回答。

未知工具不会被动态执行，程序会返回“暂不支持这个工具。”。

## `run_agent()` 封装

```python
run_agent(user_input: str) -> str
```

该函数包含一次请求所需的消息构造、模型判断、工具路由、RAG 执行和最终回答生成逻辑。命令行 `main()` 只负责接收输入和打印结果，因此主流程可以被测试代码或其他 Python 模块复用。

## 项目结构

```text
projects/
├─ agent_basics/
│  ├─ rag_agent.py              # Agent 主流程与命令行入口
│  ├─ test_rag_agent.py         # 3 项本地控制逻辑测试
│  ├─ README.md                 # 项目说明
│  └─ docs/
│     └─ interview_notes.md     # 面试讲解与快速复习
└─ rag_basics/
   ├─ rag_tool.py               # 被 Agent 复用的 RAG Tool
   ├─ semantic_rag.py           # BGE 向量检索实现
   ├─ knowledge.txt             # 实验室知识库
   └─ requirements.txt          # 本项目复用的依赖清单
```

## 环境配置

在 Windows PowerShell 中，从仓库根目录创建并激活虚拟环境：

```powershell
cd F:\git\python-practice
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\projects\rag_basics\requirements.txt
```

Agent 会复用 RAG 项目的向量检索实现，因此需要 `openai`、`sentence-transformers` 和 `numpy`。首次真实运行语义检索时，`sentence-transformers` 可能需要下载 `BAAI/bge-small-zh-v1.5` 模型。

安全配置 DeepSeek API Key：

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key-here"
```

上面的值只是占位符。不要把真实密钥写入源码、README、测试或 Git 跟踪的 `.env` 文件。

## 如何运行

在 `projects/agent_basics` 目录运行：

```powershell
cd F:\git\python-practice\projects\agent_basics
python .\rag_agent.py
```

示例问题：

```text
设备需要提前多久预约？
```

该问题需要实验室知识，模型可以选择调用 RAG Tool。普通问题例如：

```text
1+1等于几？
```

模型可以不调用知识库，直接回答。工具是否调用由模型输出决定，因此真实请求结果也会受到模型行为影响。

## 自动化测试

在 `projects` 目录运行：

```powershell
cd F:\git\python-practice\projects
python -m unittest agent_basics.test_rag_agent -v
```

测试使用 `unittest`、`MagicMock` 和 `patch` 替换 DeepSeek API 与 RAG Tool，不发送真实 API 请求、不加载 BGE 模型，也不会访问 Hugging Face。

## 3 项 Agent 测试

1. `test_normal_question_does_not_use_rag`：模拟模型直接回答，验证 RAG Tool 未被调用，模型接口只调用一次。
2. `test_lab_question_uses_rag`：模拟完整 Tool Call，验证参数解析、RAG Tool 调用及两次模型调用。
3. `test_unsupported_tool_returns_message`：模拟未知工具，验证程序返回受控提示，不执行未知函数。

## 核心知识点

- Agent 控制闭环：模型判断、工具执行、结果回传、最终生成。
- Function Calling：工具 Schema、`tool_choice="auto"`、JSON 参数解析。
- Tool Message：使用 `tool_call_id` 将结果与原 Tool Call 对应。
- RAG 模块复用：将语义检索能力包装为模型可选择的业务工具。
- 函数封装：把交互入口与可测试的 `run_agent()` 主流程分离。
- 安全路由：仅执行显式支持的工具名称。
- 自动化测试：隔离外部 API 和本地向量模型，验证控制逻辑与调用次数。

## 求职展示能力

本项目能够展示以下实际开发能力：

- 使用 Python 组织跨目录模块并封装可复用函数。
- 使用 OpenAI Compatible SDK 接入 DeepSeek。
- 编写工具 JSON Schema，处理 Tool Call 参数和结构化结果。
- 将 Function Calling 与既有 RAG 检索模块组合成完整调用闭环。
- 使用白名单分支处理未知工具，避免按模型输出任意执行函数。
- 使用 `unittest.mock` 隔离外部依赖，验证正常分支、工具分支和边界分支。

### 面试简介

在完成基础 Function Calling 和 RAG 模块后，我将两者组合成了一个轻量级 RAG Agent。模型先根据用户问题自主判断是否需要调用知识库；需要时通过 Function Calling 调用 `search_knowledge_base()`，执行 BGE 语义检索并取得结构化结果，再把 Tool Result 回传模型生成最终答案；普通问题则直接回答。主流程封装为 `run_agent(user_input)`，并使用 `unittest`、`MagicMock` 和 `patch` 验证了直接回答、完整 RAG 闭环和未知工具三个分支。

## 当前局限

- 当前只有一个业务工具 `search_knowledge_base`，还不是多工具 Agent。
- 每次命令行运行只处理一次用户输入，没有完整多轮 Memory。
- 只处理模型返回的第一个 Tool Call，不支持并行或连续多工具调用。
- 没有 Planner、Tool Registry 或通用 Dispatcher。
- 工具参数 JSON 解析、API 超时和网络异常尚未形成统一错误处理。
- 通过 `sys.path` 复用相邻项目模块，适合当前练习结构，但还不是正式 Python 包。
- 没有 UI、Web API、部署、生产级日志或监控。
- 模型输出具有不确定性，真实 API 场景需要补充重试、超时和可观测性设计。

## 下一步计划

优先增加第二个业务工具，例如复用任务管理阶段的 `create_task`，让模型在 `create_task` 与 `search_knowledge_base` 之间自主选择，形成多工具 Agent。之后再逐步补充：

- 通用工具注册与分发机制。
- 多 Tool Call 和多轮对话。
- 参数校验、异常处理、超时与重试。
- 更完整的分支和消息序列测试。
- UI、Web API、部署与日志监控。
