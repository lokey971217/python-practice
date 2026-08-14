# DeepSeek API 学习笔记

## 项目简介

本目录记录 DeepSeek API 基础学习成果，重点练习三件事：直接调用模型、让模型返回 JSON 结构化结果，以及使用 Function Calling 完成一次从用户输入到本地函数执行再回传模型的完整流程。

这些脚本是学习用示例，会真实调用 DeepSeek API。运行前需要配置 API Key，日常检查代码时不要直接执行脚本，避免产生费用。

## 已完成功能

- `deepseek_api.py`：使用 OpenAI SDK 连接 DeepSeek API，通过 `responses.create()` 发送用户问题；读取模型回复；统计输入、输出和总 token；按示例单价估算费用；捕获认证错误、限流、网络错误、API 状态错误和其他异常。
- `structured_output.py`：使用 `chat.completions.create()`，通过 `response_format={"type": "json_object"}` 要求模型返回 JSON；用 `json.loads()` 把 JSON 字符串转换为 Python 字典并读取字段。
- `function_calling.py`：定义本地 `create_task()` 函数；向模型声明 `tools`；让模型根据用户输入决定是否调用函数；解析模型生成的函数参数；执行本地函数；用 `json.dumps()` 把函数结果写回 `messages`；再次调用模型得到最终回复。

## 文件结构

```text
projects/llm_basics/
├── deepseek_api.py
├── structured_output.py
├── function_calling.py
├── README.md
└── .venv/              # 本地虚拟环境，不提交
```

## 运行环境

- Python 3.10 或更高版本
- `openai` Python 包
- DeepSeek API Key
- Windows PowerShell、命令提示符或其他终端

## 安装和运行方法

在仓库根目录执行：

```powershell
cd projects/llm_basics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install openai
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

运行示例：

```powershell
python deepseek_api.py
python structured_output.py
python function_calling.py
```

注意：以上三个脚本都会请求 DeepSeek API，可能产生费用。

## DeepSeek API 调用说明

三个脚本都通过 `OpenAI` 客户端连接 DeepSeek：

```python
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
```

`deepseek_api.py` 使用 `client.responses.create()`，通过 `instructions` 传入系统要求，通过 `input` 传入用户问题。脚本会打印 `response.output_text`，并从 `response.usage` 中读取 token 用量，按代码中的输入单价 `0.14` 和输出单价 `0.28` 估算费用。

异常处理覆盖了常见情况：

- `AuthenticationError`：API Key 错误或未正确配置。
- `RateLimitError`：请求过于频繁。
- `APIConnectionError`：网络连接异常。
- `APIStatusError`：服务端状态错误，其中 `402` 被当作余额不足处理。

## JSON 结构化输出说明

`structured_output.py` 的目标是把用户输入的任务转换成固定字段的 JSON：

- `name`：任务名称
- `priority`：只能是“普通”或“紧急”
- `status`：固定为“待处理”

代码使用：

```python
response_format = {"type": "json_object"}
```

这会要求模型返回 JSON 对象格式。随后代码取出：

```python
json_text = response.choices[0].message.content
task_data = json.loads(json_text)
```

这样就可以像普通字典一样访问 `task_data["name"]`、`task_data["priority"]` 和 `task_data["status"]`。

## Function Calling 完整流程

`function_calling.py` 实现了一个 `create_task()` 的完整闭环：

1. 定义本地 Python 函数 `create_task(name, priority)`，返回包含任务名称、优先级和状态的字典。
2. 在 `tools` 中把 `create_task` 的名称、说明和参数结构告诉模型。
3. 把用户输入保存到 `messages`。
4. 第一次调用模型，传入 `messages`、`tools` 和 `tool_choice="auto"`。
5. 检查模型是否返回 `message.tool_calls`。
6. 如果模型选择 `create_task`，读取 `tool_call.function.arguments`。
7. 使用 `json.loads()` 把模型生成的 JSON 参数转换成 Python 字典。
8. 调用本地 `create_task()` 得到真实执行结果。
9. 把模型的工具调用消息和本地函数结果追加到 `messages`。
10. 使用 `json.dumps(..., ensure_ascii=False)` 把任务结果转换成 JSON 字符串后作为 `tool` 消息传回模型。
11. 第二次调用模型，让模型基于函数执行结果生成最终回复。

## 关键对象和方法的作用

- `tools`：告诉模型当前程序有哪些可调用工具、工具名是什么、参数有哪些、参数类型和必填字段是什么。模型不会直接执行 Python 函数，只会提出调用哪个工具以及传入什么参数。
- `messages`：保存对话上下文，包括用户输入、模型提出的工具调用、本地工具执行结果。第二次调用模型时，模型依靠完整 `messages` 理解函数已经执行过。
- `json.loads()`：把 JSON 字符串转换成 Python 对象。在本项目中用于把模型生成的函数参数或结构化输出转换成字典。
- `json.dumps()`：把 Python 对象转换成 JSON 字符串。在 Function Calling 中用于把本地函数结果作为 `tool` 消息内容传回模型。

## 示例输入与预期输出

### deepseek_api.py

示例输入：

```text
什么是函数调用？
```

预期输出：

```text
模型回答：
函数调用是让模型请求程序执行特定工具。
输入的token数量: ...
输出的token数量: ...
总token数量: ...
输入的费用: $...
输出的费用: $...
总费用: $...
```

实际文本和 token 数会随模型响应变化。

### structured_output.py

示例输入：

```text
明天整理 DeepSeek API 学习笔记，比较紧急
```

预期输出：

```text
模型返回的json: {"name":"整理 DeepSeek API 学习笔记","priority":"紧急","status":"待处理"}
任务名称: 整理 DeepSeek API 学习笔记
任务优先级: 紧急
任务状态: 待处理
```

### function_calling.py

示例输入：

```text
帮我创建一个紧急任务：完成 AI Task Manager 原型
```

预期输出：

```text
模型选择的函数： create_task
转换后的字典： {'name': '完成 AI Task Manager 原型', 'priority': '紧急'}
函数执行结果： {'name': '完成 AI Task Manager 原型', 'priority': '紧急', 'status': '待处理'}
模型最终回复： ...
```

最终回复由模型生成，内容可能略有不同。

## API Key 安全说明

- 不要把真实 API Key 写进代码或 README。
- 使用环境变量 `DEEPSEEK_API_KEY` 读取密钥。
- 本目录内的 `.venv/`、`__pycache__/` 和 `.env` 都不应提交。
- 如果需要本地保存密钥，可以放在 `.env` 中，但 `.env` 必须被 `.gitignore` 忽略。

## 下一阶段

下一阶段计划进入 AI Task Manager：把当前学习到的 DeepSeek API 调用、JSON 结构化输出和 Function Calling 串起来，逐步实现一个可以从自然语言创建任务、识别优先级、保存任务状态并支持后续管理的任务管理器。
