# DeepSeek API 与 AI Task Manager 学习项目

## 项目简介

本目录整理了 DeepSeek API、JSON 结构化输出、Function Calling 和 AI Task Manager 的阶段性学习成果。代码用于学习和演示，不是生产级任务管理系统。涉及模型的脚本会真实请求 DeepSeek API；自动化测试不会调用模型。

## 已实现功能

- `deepseek_api.py`：通过 OpenAI Python SDK 兼容接口连接 DeepSeek，并从 `DEEPSEEK_API_KEY` 环境变量读取密钥。
- `structured_output.py`：要求模型返回 JSON 对象，并用 `json.loads()` 转换成 Python 字典。
- `function_calling.py`：声明工具及参数 Schema，让模型生成参数，执行本地函数，把结果回传模型并获取最终回复。
- `ai_task_manager.py`：支持创建、查询和按名称完成任务；通过循环连续对话，输入“退出”结束；任务保存在本地 JSON 文件中，重启后可恢复。
- 持久化加载会处理 `FileNotFoundError` 和 `JSONDecodeError`。
- 使用 `main()` 和 `if __name__ == "__main__"` 组织程序入口。
- `test_ai_task_manager.py`：使用 `unittest`、`setUp`、`tearDown` 和 `unittest.mock.patch` 覆盖 5 项核心行为，避免测试写入真实任务文件。

## 文件结构

```text
projects/llm_basics/
├── ai_task_manager.py       # 支持 Function Calling 和 JSON 持久化的任务管理器
├── test_ai_task_manager.py  # 5 项 unittest 自动化测试
├── deepseek_api.py          # DeepSeek API 基础调用示例
├── structured_output.py     # JSON 结构化输出示例
├── function_calling.py      # 单工具 Function Calling 学习示例
├── README.md
├── ai_tasks.json            # 本地运行数据，不提交
└── ai_tasks_backup.json     # 本地备份数据，不提交
```

## Function Calling 完整流程

1. 在 Python 中实现 `create_task`、`list_tasks` 和 `complete_task`。
2. 在 `tools` 中声明工具名称、说明和 JSON 参数 Schema。
3. 将用户输入作为消息发送给模型，并允许模型自动选择工具。
4. 读取模型返回的 `tool_calls`。
5. 用 `json.loads()` 把模型生成的 JSON 参数转换为 Python 字典。
6. 根据工具名称执行对应的真实 Python 函数。
7. 用 `json.dumps()` 将执行结果转换为 JSON，并作为 `tool` 消息加入对话。
8. 再次调用模型，获得基于工具执行结果的最终回复。

当前实现每轮处理模型返回的第一个工具调用。

## AI Task Manager 与 JSON 持久化

- 创建任务：`create_task(name, priority)` 添加“待处理”任务并保存。
- 查询任务：`list_tasks()` 返回当前全部任务。
- 完成任务：`complete_task(name)` 按任务名称标记为“已完成”；找不到时返回错误字典。
- 程序启动时从 `ai_tasks.json` 加载数据，创建或完成任务后重新写入该文件。
- 文件不存在时返回空列表；JSON 内容损坏时提示并使用空列表。
- `while` 循环支持连续输入，输入“退出”安全结束。

`ai_tasks.json` 和 `ai_tasks_backup.json` 是本地运行数据，已被 Git 忽略，但不会从本地删除。

## 环境配置（Windows PowerShell）

在仓库根目录执行：

```powershell
cd projects\llm_basics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install openai
```

仅在当前 PowerShell 会话中安全配置密钥：

```powershell
$env:DEEPSEEK_API_KEY="在这里填写你自己的密钥"
```

不要把真实密钥写入代码、README、测试、日志或提交到 Git。`.env` 也已被忽略。

## 运行方法

运行 AI Task Manager（会调用 DeepSeek API，可能产生费用）：

```powershell
.\.venv\Scripts\python.exe ai_task_manager.py
```

运行其他学习示例同样会调用 API：

```powershell
.\.venv\Scripts\python.exe deepseek_api.py
.\.venv\Scripts\python.exe structured_output.py
.\.venv\Scripts\python.exe function_calling.py
```

运行自动化测试（不会调用 API）：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

## 当前局限与下一步计划

- 当前使用本地 JSON 文件，不支持数据库、并发写入或多用户隔离。
- 每轮只处理第一个工具调用，尚未实现多工具调用编排。
- 模型参数和工具参数的错误处理仍可加强。
- 尚未实现 RAG、多 Agent、网页界面或权限系统。
- 下一步可增加输入校验、更多异常测试，并把 API 客户端注入以提升可测试性。

## 本阶段掌握的技术点

- 使用 OpenAI Python SDK 兼容接口调用 DeepSeek。
- 使用环境变量管理 API Key。
- 使用 JSON 完成模型输出解析、函数参数转换和本地数据持久化。
- 理解 Function Calling 的工具声明、模型选择、本地执行、结果回传和最终回复流程。
- 使用函数、循环、异常处理和标准程序入口组织命令行应用。
- 使用 `unittest`、测试夹具和 `mock.patch` 隔离测试副作用。
