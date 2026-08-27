# Agent 基础项目面试复习

## 30 秒项目介绍

我把 Function Calling、RAG 检索和任务创建函数组合成了一个轻量级 Multi-Tool Agent v1。DeepSeek 通过 `tool_choice="auto"` 在知识库搜索、任务创建和直接回答之间自主选择；工具结果回传模型后再生成最终回复。主流程封装成 `run_agent()`，并用 4 项 mock 测试覆盖 RAG Tool、Task Tool、No-Tool 和 Unsupported Tool 路由。

## 1 分钟项目介绍

这个项目解决的是“模型是否需要工具，以及应该选择哪个工具”的问题。程序向 DeepSeek 同时提供 `search_knowledge_base` 和 `create_task` 的 Function Calling Schema。第一次调用使用 `tool_choice="auto"`：实验室知识问题选择 RAG Tool，创建任务请求选择 Task Tool，普通问题不调用工具。

Python 使用 `json.loads()` 解析参数，再通过当前明确的 `if / elif` 路由执行两个允许的函数。`search_knowledge_base()` 复用上一阶段的 BGE 中文向量检索；`create_task()` 只创建并返回任务字典，不做持久化。程序用 `tool_call_id` 把 Tool Result 与原 Tool Call 对应起来，再进行第二次模型调用生成自然语言答案。

为了让逻辑可复用和可测试，我将主流程封装为 `run_agent(user_input)`。测试用 `MagicMock` 和 `patch` 隔离 DeepSeek、RAG Tool 和 Task Tool，验证不同意图选择正确路由、两个工具不会互相误调用、未知工具不会被执行。

## Multi-Tool Agent v1 核心问答

### 什么是 Multi-Tool Agent？

它是能够接收多个工具定义，并由模型结合用户意图决定是否调用工具以及调用哪个工具的 Agent。本项目有知识库搜索和任务创建两个 Tool。

### Tool Routing 是什么？

Tool Routing 是把模型返回的工具名称和参数分发给对应 Python 函数的过程。本项目使用直接、可读的 `if / elif` 路由；Tool Registry 和统一 Dispatcher 留到下一阶段。

### 模型如何选择 `search_knowledge_base` 和 `create_task`？

System Prompt 描述使用场景，Tool Schema 描述工具功能和参数，`tool_choice="auto"` 允许模型根据语义选择。实验室规定类问题应选择 RAG Tool，创建任务意图应选择 Task Tool。

### 为什么普通问题不应该调用工具？

普通知识或闲聊不需要外部动作。无意义调用会增加延迟、成本和错误上下文；No-Tool Route 允许模型直接回答。

### 为什么未知工具不能直接执行？

模型输出是不可信输入。程序必须限制可执行函数集合，未知名称进入 Unsupported Tool Route，避免动态调用任意代码。

### 为什么 Agent 需要二次调用 LLM？

第一次调用用于选择工具并生成参数；Python 执行后，第二次调用让模型读取真实 Tool Result，再生成面向用户的自然语言答案。No-Tool Route 只需要一次调用。

### Tool Result 的作用是什么？

它把 Python 函数的结构化执行结果放入 `role="tool"` 消息，并通过 `tool_call_id` 与原调用关联。模型据此回答，而不是假设工具执行结果。

### 为什么要 Mock 两个 Tool？

Agent 单元测试关注路由与控制逻辑。Mock RAG Tool 可避免加载 BGE 和访问 Hugging Face；Mock Task Tool 可精确验证参数与误调用，不把工具自身实现混入路由测试。

### 如何证明工具之间没有误调用？

RAG 路由测试断言 `search_knowledge_base.assert_called_once_with(...)` 与 `create_task.assert_not_called()`；Task 路由测试做相反断言。普通问题则断言两个工具都未调用。

### `run_agent()` 的作用是什么？

它把一次性脚本变成可复用函数，使其他模块可以调用、unittest 可以直接传入问题，后续也能作为 UI、API 或多轮循环的入口；这些后续层当前尚未实现。

### 当前 `if / elif` Dispatcher 有什么局限？

工具较少时它很直观，但每增加一个 Tool 都要同时修改 Schema 列表和分支代码，注册信息分散，扩展和测试成本会逐步上升。

### 下一步为什么做 Tool Registry？

Registry 可以集中管理工具名、Schema 和 Python 函数，统一 Dispatcher 再按名称查找和执行，减少不断增长的条件分支。这是下一阶段目标，本次没有提前实现。

## 高频问题与回答

### 1. Agent 是什么？

在本项目语境中，Agent 是由大模型参与决策、能选择并调用外部工具、读取工具结果后继续完成回答的控制流程。它不仅生成文本，还决定是否采取工具动作。

### 2. Function Calling 和 Agent 有什么关系？

Function Calling 是模型表达“我要调用哪个工具、参数是什么”的协议能力；Agent 是围绕这个能力实现的完整运行循环，包括模型判断、参数解析、真实函数执行、结果回传和最终生成。Function Calling 是手段，Agent 是包含它的控制流程。

### 3. RAG 和 Agent 有什么关系？

RAG 提供外部知识检索能力，Agent 决定何时使用这项能力。本项目把 RAG 包装成 `search_knowledge_base` 工具，普通问题不必检索，涉及实验室知识时才由模型选择调用。

### 4. 为什么模型需要调用两次？

第一次调用用于判断是否使用工具并生成工具参数，此时模型还没有真实检索结果。Python 执行工具后，第二次调用让模型读取 Tool Result，并把结构化数据组织成最终自然语言答案。

### 5. `tool_call` 是什么？

它是模型在 Assistant Message 中返回的工具调用请求，包含调用 ID、函数名和 JSON 字符串参数。它表示模型的调用意图，不代表函数已经执行。

### 6. Tool Result 为什么必须返回模型？

工具是由 Python 在模型外部执行的。模型只有收到 Tool Result，才能知道实际检索到了什么，并据此生成有上下文依据的最终答案。

### 7. `tool_call_id` 有什么作用？

`tool_call_id` 将 `role="tool"` 的执行结果与模型先前发出的具体 Tool Call 对应起来。多个调用并存时，这个关联尤其重要；即使当前只处理一个调用，也应遵循消息协议。

### 8. 为什么使用 `tool_choice="auto"`？

因为目标是让模型根据问题意图选择 RAG Tool、Task Tool 或 No-Tool Route。强制调用会让普通问题产生不必要动作，禁用工具又会阻断检索和任务创建能力。

### 9. 为什么需要 `run_agent()`？

它把核心控制逻辑从命令行输入输出中分离出来，使其他 Python 模块能够复用，也使测试可以直接传入问题并断言返回值和依赖调用情况。`main()` 只保留交互职责。

### 10. 为什么测试不能真实调用 DeepSeek？

单元测试应快速、稳定、可重复。真实 API 会受到网络、额度、模型输出波动和费用影响，无法只验证本地控制逻辑。Mock 可以给出确定响应，并精确检查调用次数和参数。

### 11. 为什么还要 Mock 两个 Tool？

真实 RAG 会加载 BGE 模型，首次还可能访问 Hugging Face；Task Tool 的真实结果也不属于路由测试重点。分别 Mock 两个 Tool，才能稳定验证参数、调用次数以及它们不会互相误调用。

### 12. 普通问题为什么不能固定执行工具？

固定执行会增加延迟和错误动作，还可能引入无关知识或创建错误任务。让模型先判断，可以把工具调用限制在有明确外部知识或操作意图的场景。

### 13. 未知工具为什么不能直接执行？

模型输出不能直接当作任意代码或函数入口。程序需要显式白名单，确认工具名称和参数后才能执行。本项目当前只允许 `search_knowledge_base` 和 `create_task`，其他名称返回受控提示。

### 14. 工具参数如何从模型进入 Python？

工具 Schema 规定参数结构；模型把参数放在 `tool_call.function.arguments` 的 JSON 字符串里；Python 用 `json.loads()` 转成字典，再通过键值调用真实函数。

### 15. 结构化 RAG 结果有什么价值？

字典中可以保留 `found`、问题、知识片段和分数等字段，比拼接一段无结构文本更容易测试、扩展和交给模型解释。回传前再序列化为 JSON 字符串。

### 16. 当前 4 项测试分别验证什么？

第一项验证普通回答时两个 Tool 都不调用；第二项验证实验室问题只调用 RAG Tool；第三项验证任务请求只调用 Task Tool；第四项验证未知工具不会被执行。两个真实工具分支都验证模型接口共调用两次。

### 17. 当前 Agent 有哪些局限？

当前只有两个 Tool，`create_task()` 只返回对象且不持久化；分发仍是 `if / elif`，只处理一次输入和第一个 Tool Call。没有 Tool Registry、统一 Dispatcher、多轮 Memory、Planner、复杂任务拆解或并行工具调用，也没有 UI、API 服务、部署、生产级日志和监控。

### 18. 下一步如何继续扩展？

下一步是 Tool Registry / Dispatcher：集中登记工具名称、Schema 与 Python 函数，用统一分发逻辑替代不断增长的 `if / elif`。之后再考虑多轮对话；本阶段不做持久化、复杂 RAG、UI 或部署。

## 代码流程速记

```text
run_agent(user_input)
  1. 构造 system + user messages
  2. 第一次 DeepSeek 调用，tool_choice="auto"
  3. 无 tool_calls：直接返回 message.content
  4. 有 tool_calls：读取第一个调用并 json.loads(arguments)
  5. if / elif 工具名白名单与路由
  6. 执行 search_knowledge_base(...) 或 create_task(...)
  7. 追加 Assistant Tool Call
  8. 追加带 tool_call_id 的 Tool Result
  9. 第二次 DeepSeek 调用
 10. 返回最终 content
```

## 关键实现点

- 密钥只通过 `os.getenv("DEEPSEEK_API_KEY")` 获取。
- DeepSeek 使用 OpenAI Compatible SDK 和 `https://api.deepseek.com`。
- 两个 Tool 分别定义参数 Schema，模型自主选择路由。
- RAG Tool 使用 `question` 和 `top_k`；Task Tool 使用 `name` 和 `priority`。
- `json.loads()` 负责模型参数字符串到 Python 字典。
- `json.dumps(..., ensure_ascii=False)` 保留中文 Tool Result。
- 未知工具通过显式名称分支拦截，不动态执行。
- `create_task()` 只返回结构化对象，不保存任务。
- 测试同时 Mock 模型接口、RAG Tool 和 Task Tool，不访问外部服务。

## 面试前 5 分钟快速复习

1. 一句话定位：这是一个 Function Calling + RAG + Task Tool 的 Multi-Tool Agent v1。
2. 三条核心选择：知识库问题走 RAG、任务请求走 Task、普通问题不调用工具。
3. 核心闭环：模型判断 → Tool Call → Python 路由并执行 → Tool Result → 模型最终回答。
4. 为什么两次模型调用：第一次选工具，第二次基于真实工具结果生成答案。
5. 为什么 `tool_call_id`：关联工具结果和原调用。
6. 安全边界：只允许两个显式支持的 Tool，未知名称不执行。
7. 测试重点：4 条路由，以及两个 Tool 不会互相误调用。
8. 测试隔离：Mock DeepSeek、RAG 和 Task Tool，不花费 API、不加载 BGE。
9. 任务边界：`create_task()` 只返回对象，没有列表、JSON 或数据库持久化。
10. 诚实局限：两个 Tool、单轮、只处理第一个 Tool Call、`if / elif` 分发、无 UI/API/部署。
11. 下一步：Tool Registry / Dispatcher，然后再考虑多轮对话。
