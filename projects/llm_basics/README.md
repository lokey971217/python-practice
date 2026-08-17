# DeepSeek API 与 AI Task Manager

一个面向 Python 与大模型 API 初学阶段的命令行学习项目。项目把 DeepSeek API、JSON 结构化输出、Function Calling、本地函数执行、JSON 持久化和自动化测试串成一个可以运行和讲解的完整案例。

> 项目定位：个人学习与求职展示案例，不是生产级任务管理系统。运行模型相关脚本会产生真实 API 请求，自动化测试不会调用模型。

## 项目背景

普通的大模型对话只能返回文本。本项目进一步解决一个工程问题：如何让模型理解自然语言操作意图，由 Python 程序执行确定性的任务增删改查逻辑，并把真实执行结果交给模型组织成最终回复。

AI Task Manager 支持以下自然语言操作：

- 创建任务，并设置“普通”或“紧急”优先级。
- 查询当前任务列表。
- 按任务名称将任务标记为已完成。
- 使用 JSON 保存数据，程序重启后恢复任务。
- 在命令行中连续对话，输入“退出”结束程序。

## 技术栈

- Python 3.10+
- OpenAI Python SDK 兼容接口
- DeepSeek API
- Function Calling / Tool Calling
- JSON 数据持久化
- `unittest` 与 `unittest.mock`
- Git 与 GitHub

## 项目结构

```text
projects/llm_basics/
├── ai_task_manager.py       # AI 任务管理器主程序
├── test_ai_task_manager.py  # 本地逻辑与异常场景测试
├── deepseek_api.py          # DeepSeek API 基础调用示例
├── structured_output.py     # JSON 结构化输出示例
├── function_calling.py      # 单工具 Function Calling 示例
├── requirements.txt         # Python 依赖
├── README.md                # 项目说明与面试讲解材料
├── ai_tasks.json            # 本地运行数据，不提交
└── ai_tasks_backup.json     # 本地备份数据，不提交
```

## 核心执行流程

```mermaid
flowchart LR
    A[用户自然语言输入] --> B[DeepSeek 判断操作意图]
    B --> C[返回工具名称与 JSON 参数]
    C --> D[Python 解析并校验参数]
    D --> E[执行本地任务函数]
    E --> F[写入或读取 JSON 数据]
    F --> G[工具结果回传模型]
    G --> H[生成最终中文回复]
```

一次完整的 Function Calling 包括：

1. 使用 JSON Schema 向模型声明 `create_task`、`list_tasks` 和 `complete_task`。
2. 将用户输入发送给模型，由模型选择工具并生成 JSON 参数。
3. 使用 `json.loads()` 将参数转换为 Python 字典。
4. `execute_tool()` 将工具名分发到真实 Python 函数。
5. 本地函数修改内存中的任务列表，并通过 JSON 文件持久化。
6. 使用 `json.dumps()` 将执行结果作为 `tool` 消息回传模型。
7. 再次请求模型，获得基于真实执行结果的最终回复。

模型只负责理解意图和组织语言；数据修改由确定性的 Python 函数完成。这种职责划分比让模型直接“假装完成操作”更可靠，也更容易测试。

## 关键设计与代码亮点

### 安全管理 API Key

程序只从环境变量读取密钥，并在真正运行命令行程序时创建客户端：

```python
api_key = os.getenv("DEEPSEEK_API_KEY")
```

真实密钥不会写入代码、README 或测试；`.env`、虚拟环境、缓存和本地任务数据均被 Git 忽略。

### JSON 持久化与异常处理

- `save_tasks()` 使用 UTF-8 和 `ensure_ascii=False` 保存中文任务。
- `load_tasks()` 处理文件不存在和 JSON 内容损坏两种场景。
- 数据文件路径基于脚本位置生成，从其他目录启动程序时仍能找到正确文件。
- 创建和完成任务后立即保存，重启程序可以恢复数据。

### 可测试的工具分发

`execute_tool()` 将模型返回的工具名称映射到本地函数，使业务逻辑与模型请求相对分离。测试通过 `mock.patch` 隔离文件写入和函数调用，不会修改真实 `ai_tasks.json`，也不会产生 API 费用。

## 安装与配置（Windows PowerShell）

在仓库根目录执行：

```powershell
cd projects\llm_basics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

仅在当前 PowerShell 会话配置自己的密钥：

```powershell
$env:DEEPSEEK_API_KEY="在这里填写你自己的密钥"
```

不要把真实密钥复制到源代码、测试、日志或 Git 提交中。

## 运行项目

AI Task Manager 会真实调用 DeepSeek API，可能产生费用：

```powershell
.\.venv\Scripts\python.exe ai_task_manager.py
```

示例交互：

```text
请输入你的要求（输入“退出”结束）：创建一个紧急任务，明天整理项目 README
模型最终回复：已创建紧急任务“明天整理项目 README”。

请输入你的要求（输入“退出”结束）：查看所有任务
模型最终回复：当前共有 1 个待处理任务……

请输入你的要求（输入“退出”结束）：完成任务“明天整理项目 README”
模型最终回复：任务已标记为完成。
```

最终文字由模型生成，可能与示例不同。

其他阶段性示例：

```powershell
.\.venv\Scripts\python.exe deepseek_api.py
.\.venv\Scripts\python.exe structured_output.py
.\.venv\Scripts\python.exe function_calling.py
```

## 自动化测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

当前 8 项测试覆盖：

- 从 JSON 加载任务并返回列表。
- 文件不存在时返回空列表。
- JSON 损坏时返回空列表并给出提示。
- 返回全部任务。
- 正确创建任务。
- 正确完成任务。
- 完成不存在的任务时返回错误。
- 将模型选择的工具正确分发到本地函数。

## 我在这个项目中解决的问题

1. **模型输出不能直接执行**：先用工具 Schema 约束参数结构，再将 JSON 参数解析为 Python 字典。
2. **模型不能真正修改本地数据**：由 Python 函数执行操作，模型只负责选择工具。
3. **程序重启会丢失任务**：使用 JSON 文件保存并在启动时恢复。
4. **测试可能污染真实数据**：使用 `setUp`、`tearDown`、`mock_open` 和 `patch` 隔离副作用。
5. **密钥可能被误提交**：使用环境变量并通过 `.gitignore` 排除敏感文件。

## 面试讲解提纲

可以用下面这段逻辑介绍项目：

> 我用 Python 和 DeepSeek 的 OpenAI 兼容接口实现了一个命令行 AI 任务管理器。模型负责把自然语言识别为创建、查询或完成任务的工具调用，程序用 JSON Schema 约束参数，再由本地 Python 函数执行真实操作。任务通过 JSON 持久化，加载时处理文件不存在和数据损坏。测试使用 unittest 和 mock 隔离磁盘写入，因此不会污染真实数据或调用付费 API。这个项目让我完整实践了从模型调用到工具执行、结果回传、安全配置和自动化测试的闭环。

建议演示顺序：

1. 展示 `TOOLS` 中的参数 Schema。
2. 展示 `execute_tool()` 如何把模型决策映射到本地函数。
3. 创建、查询并完成一个任务。
4. 重启程序，证明 JSON 持久化有效。
5. 运行测试，说明如何避免真实文件和 API 副作用。

## 当前局限与下一步

- 每轮只处理模型返回的第一个工具调用。
- JSON 文件不适合并发写入、多用户或大规模数据。
- 任务名称重复时，只完成第一个匹配任务。
- 模型生成参数的业务规则校验仍可增强。
- 尚未实现数据库、RAG、多 Agent、网页界面或登录权限。

下一步可以增加任务 ID、参数校验、更多模型响应测试，并将存储层抽象为可替换组件。项目不会把尚未实现的规划描述成现有功能。
