# Agent 基础项目

## 项目目标

本项目把 Function Calling、RAG 检索和任务创建函数组合成一个轻量级 Multi-Tool Agent v1。模型根据用户意图自主选择知识库搜索、任务创建或不调用工具。

项目重点是实现并测试一个可复用的 Agent 控制闭环，不将其描述为生产级或完全自主的智能体。

## 当前实现

- 使用 OpenAI Python SDK 的兼容接口调用 DeepSeek。
- 通过 `os.getenv("DEEPSEEK_API_KEY")` 读取密钥，代码中不保存真实密钥。
- 使用 System Prompt 说明助手角色和工具使用场景。
- 用 JSON Schema 定义 `search_knowledge_base` 和 `create_task` 两个 Tool。
- 通过 `tool_choice="auto"` 让模型决定是否调用工具以及调用哪个工具。
- 将模型生成的 JSON 参数解析为 Python 字典，再通过 `if / elif` 路由执行对应函数。
- 将结构化 Tool Result 回传模型，再获取最终自然语言答案。
- 将主流程封装为 `run_agent(user_input: str) -> str`，同时保留命令行入口。
- 对 No-Tool、RAG Tool、Task Tool 和 Unsupported Tool 四条路由进行自动化测试。

## Multi-Tool Agent 工作流程

```text
用户问题
  ↓
DeepSeek 第一次判断（tool_choice="auto"）
  ├─ 普通问题       → 不调用工具，直接回答
  ├─ 实验室知识问题 → Tool Call: search_knowledge_base() ┐
  └─ 创建任务请求   → Tool Call: create_task()           ┘
                                  ↓
                      Python 解析 JSON 参数
                                  ↓
                       if / elif 执行对应工具
                                  ↓
                  Tool Result 携带 tool_call_id 回传
                                  ↓
                   DeepSeek 第二次调用生成最终答案
```

## 当前两个 Tool

### `search_knowledge_base`

复用 `projects/rag_basics/rag_tool.py`。该工具读取实验室知识库，使用 BGE Embedding、归一化向量相似度和 Top-K 语义检索，并返回包含检索片段与分数的结构化结果。本阶段不修改已有 RAG 实现。

### `create_task`

定义在 `task_tool.py`：

```python
create_task(name: str, priority: str = "普通") -> dict[str, str]
```

它当前只创建并返回包含 `name`、`priority` 和 `status="待处理"` 的任务对象。它不会保存任务列表，不会写入 JSON 或数据库，也没有持久化能力。

## Tool Routing

`rag_agent.py` 向模型同时提供两个工具的 JSON Schema。模型返回 Tool Call 后，程序读取第一个调用，用 `json.loads()` 解析参数，再使用当前明确的 `if / elif` 路由：

```text
search_knowledge_base → 执行 RAG Tool
create_task           → 执行 Task Tool
其他名称              → 返回“暂不支持这个工具。”
```

当模型返回 Tool Call 时，程序会：

1. 读取第一个 Tool Call。
2. 用 `json.loads()` 解析 `function.arguments`。
3. 检查工具名称并执行 `search_knowledge_base` 或 `create_task`。
4. 未知工具进入安全分支，不动态执行模型给出的任意名称。
5. 用 `json.dumps(..., ensure_ascii=False)` 序列化结构化结果。
6. 将原始 Assistant Tool Call 与 `role="tool"` 的结果追加到消息列表。
7. 进行第二次模型调用，得到面向用户的最终回答。

未知工具不会被动态执行，程序会返回“暂不支持这个工具。”。

## `run_agent()` 封装

```python
run_agent(user_input: str) -> str
```

该函数把一次性脚本封装成可复用的 Agent 主流程，包含消息构造、模型判断、工具路由、工具执行和最终回答生成。命令行 `main()` 只负责接收输入和打印结果，因此 `run_agent()` 可以被其他 Python 模块调用、直接编写 unittest，并为后续接入 UI、API 或多轮 Agent 保留清晰入口；这些后续能力当前尚未实现。

## 项目结构

```text
projects/
├─ agent_basics/
│  ├─ rag_agent.py              # Agent 主流程与命令行入口
│  ├─ task_tool.py              # 仅创建并返回任务对象
│  ├─ test_rag_agent.py         # 4 项 Tool Routing 测试
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

在 `projects` 目录以模块方式运行：

```powershell
cd F:\git\python-practice\projects
python -m agent_basics.rag_agent
```

示例问题：

```text
设备需要提前多久预约？
```

该问题需要实验室知识，模型可以选择调用 RAG Tool。创建任务示例：

```text
帮我创建一个学习Python的紧急任务
```

模型可以调用 Task Tool；返回的任务对象只存在于当前调用结果中，不会保存到任务列表。普通问题例如：

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

测试使用 `unittest`、`MagicMock` 和 `patch` 替换 DeepSeek API、RAG Tool 和 Task Tool，不发送真实 API 请求、不加载 BGE 模型，也不会访问 Hugging Face。

## 4 项 Multi-Tool Agent 测试

1. `test_normal_question_uses_no_tool`：验证普通问题直接回答，RAG Tool 和 Task Tool 均不调用，模型接口只调用一次。
2. `test_lab_question_uses_rag`：验证实验室问题只调用 RAG Tool、不误调用 Task Tool，并完成两次模型调用。
3. `test_task_question_uses_create_task`：验证任务请求只调用 Task Tool、不误调用 RAG Tool，并完成两次模型调用。
4. `test_unsupported_tool_returns_message`：验证未知工具返回受控提示，不执行未知函数。

## 核心知识点

- Multi-Tool Agent 控制闭环：模型判断、工具选择、执行、结果回传、最终生成。
- Function Calling：工具 Schema、`tool_choice="auto"`、JSON 参数解析。
- Tool Message：使用 `tool_call_id` 将结果与原 Tool Call 对应。
- RAG 模块复用：将语义检索能力包装为模型可选择的业务工具。
- Task Tool：返回结构化任务对象，但当前不持久化。
- Tool Routing：通过明确的 `if / elif` 分发两个工具，并提供 No-Tool 和 Unsupported Tool 路由。
- 函数封装：把交互入口与可测试的 `run_agent()` 主流程分离。
- 安全路由：仅执行显式支持的工具名称。
- 自动化测试：隔离外部 API 和本地向量模型，验证控制逻辑与调用次数。

## 求职展示能力

本项目能够展示以下实际开发能力：

- 使用 Python 组织跨目录模块并封装可复用函数。
- 使用 OpenAI Compatible SDK 接入 DeepSeek。
- 编写工具 JSON Schema，处理 Tool Call 参数和结构化结果。
- 将 Function Calling、既有 RAG 检索与任务创建函数组合成 Multi-Tool Agent v1。
- 使用 `if / elif` 完成 RAG Tool、Task Tool、No-Tool 和 Unsupported Tool 路由。
- 使用白名单分支处理未知工具，避免按模型输出任意执行函数。
- 使用 `unittest.mock` 隔离 DeepSeek 与两个 Tool，验证工具选择正确且不会互相误调用。

### 面试简介

在完成 Function Calling 和 RAG 模块后，我将它们与任务创建函数组合成了一个轻量级 Multi-Tool Agent v1。模型通过 `tool_choice="auto"` 根据用户意图选择 `search_knowledge_base()`、`create_task()` 或直接回答；工具执行结果通过 Tool Message 回传模型，再由模型完成最终回复。主流程封装为 `run_agent(user_input)`，并使用 `unittest`、`MagicMock` 和 `patch` 验证了四条核心路由及工具之间不会互相误调用。

## 当前局限

- 当前只有 `search_knowledge_base` 和 `create_task` 两个 Tool。
- `create_task()` 只返回任务对象，没有任务列表、JSON 或数据库持久化。
- 每次命令行运行只处理一次用户输入，没有完整多轮 Memory。
- 只处理模型返回的第一个 Tool Call，不支持并行或连续多工具调用。
- 当前工具分发仍是 `if / elif`，没有 Tool Registry 或统一 Dispatcher。
- 没有 Planner 或复杂任务拆解。
- 工具参数 JSON 解析、API 超时和网络异常尚未形成统一错误处理。
- 通过 `sys.path` 复用相邻项目模块，适合当前练习结构，但还不是正式 Python 包。
- 没有 UI、Web API、部署、生产级日志或监控。
- 模型输出具有不确定性，真实 API 场景需要补充重试、超时和可观测性设计。

## 下一步计划

下一阶段主线明确为：

```text
Multi-Tool Agent v1
        ↓
Tool Registry
        ↓
统一 Tool Dispatcher
        ↓
多轮对话
```

下一步只先抽象工具注册与统一分发，避免继续扩张 `if / elif`。本阶段不实现任务持久化、向量数据库、复杂 RAG、UI 或部署。
