# Agent 基础项目面试复习

## 30 秒项目介绍

我把前一阶段的 Function Calling 与 RAG 检索组合成了一个轻量级 RAG Agent。DeepSeek 先判断用户问题是否需要实验室知识库；需要时通过 Tool Call 调用 `search_knowledge_base()`，Python 执行 BGE 语义检索，再把结构化结果回传模型生成最终答案；普通问题则直接回答。我把主流程封装成 `run_agent()`，并用 3 项 mock 测试覆盖直接回答、完整工具闭环和未知工具分支。

## 1 分钟项目介绍

这个项目解决的是“模型什么时候应该查询外部知识”的问题。程序在 System Prompt 中说明实验室助手角色，并向 DeepSeek 提供 `search_knowledge_base` 的 Function Calling Schema。第一次模型调用使用 `tool_choice="auto"`：如果模型认为是普通问题，就直接返回回答；如果问题需要实验室规定，模型返回工具名和 JSON 参数。

Python 使用 `json.loads()` 解析参数，只允许执行已注册的 `search_knowledge_base()`。该工具复用上一阶段的 BGE 中文向量检索和 Top-K 结果，并返回结构化字典。程序用 `tool_call_id` 把 Tool Result 与原 Tool Call 对应起来，再进行第二次模型调用，让模型基于检索结果生成自然语言答案。

为了让逻辑可复用和可测试，我将主流程封装为 `run_agent(user_input)`。测试用 `MagicMock` 和 `patch` 隔离 DeepSeek、BGE 模型与 Hugging Face，验证普通问题不误用 RAG、实验室问题形成完整两次调用闭环、未知工具不会被执行。

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

因为目标是让模型根据问题意图决定是否检索。若强制调用工具，`1+1等于几？` 这类普通问题也会产生不必要的 RAG 开销；若禁用工具，实验室问题又无法获得外部知识。

### 9. 为什么需要 `run_agent()`？

它把核心控制逻辑从命令行输入输出中分离出来，使其他 Python 模块能够复用，也使测试可以直接传入问题并断言返回值和依赖调用情况。`main()` 只保留交互职责。

### 10. 为什么测试不能真实调用 DeepSeek？

单元测试应快速、稳定、可重复。真实 API 会受到网络、额度、模型输出波动和费用影响，无法只验证本地控制逻辑。Mock 可以给出确定响应，并精确检查调用次数和参数。

### 11. 为什么还要 Mock RAG Tool？

真实 RAG 会加载 BGE 模型，首次还可能访问 Hugging Face，执行更慢且结果可能受模型版本影响。本阶段 Agent 测试的目标是工具路由和消息闭环，不是重复测试上一阶段的向量检索实现。

### 12. 普通问题为什么不能固定执行 RAG？

固定执行会增加延迟和算力消耗，还可能把不相关知识片段带入回答。让模型先判断，可以把知识库检索限制在需要外部知识的场景。

### 13. 未知工具为什么不能直接执行？

模型输出不能直接当作任意代码或函数入口。程序需要显式白名单或工具注册表，确认工具名称和参数后才能执行。本项目当前只允许 `search_knowledge_base`，其他名称返回受控提示。

### 14. 工具参数如何从模型进入 Python？

工具 Schema 规定参数结构；模型把参数放在 `tool_call.function.arguments` 的 JSON 字符串里；Python 用 `json.loads()` 转成字典，再通过键值调用真实函数。

### 15. 结构化 RAG 结果有什么价值？

字典中可以保留 `found`、问题、知识片段和分数等字段，比拼接一段无结构文本更容易测试、扩展和交给模型解释。回传前再序列化为 JSON 字符串。

### 16. 当前 3 项测试分别验证什么？

第一项验证普通回答时 RAG 不被调用且模型只调用一次；第二项验证 Tool Call 参数、RAG 调用和第二次模型调用，模型接口共调用两次；第三项验证未知工具不会被执行，并返回明确提示。

### 17. 当前 Agent 有哪些局限？

只有一个业务工具，只处理一次用户输入和第一个 Tool Call；没有多轮 Memory、Planner、Tool Registry、通用 Dispatcher，也没有统一的 JSON 解析、API 超时和网络异常处理。项目没有 UI、Web API、部署、生产级日志和监控。

### 18. 下一步如何扩展为多工具 Agent？

先增加第二个真实工具，例如 `create_task`；为工具建立名称到函数及 Schema 的注册映射；让模型在 `create_task` 与 `search_knowledge_base` 之间选择；再补充参数校验、连续 Tool Call 循环和每个路由分支的 mock 测试。

## 代码流程速记

```text
run_agent(user_input)
  1. 构造 system + user messages
  2. 第一次 DeepSeek 调用，tool_choice="auto"
  3. 无 tool_calls：直接返回 message.content
  4. 有 tool_calls：读取第一个调用并 json.loads(arguments)
  5. 工具名白名单检查
  6. 执行 search_knowledge_base(question, top_k)
  7. 追加 Assistant Tool Call
  8. 追加带 tool_call_id 的 Tool Result
  9. 第二次 DeepSeek 调用
 10. 返回最终 content
```

## 关键实现点

- 密钥只通过 `os.getenv("DEEPSEEK_API_KEY")` 获取。
- DeepSeek 使用 OpenAI Compatible SDK 和 `https://api.deepseek.com`。
- Tool Schema 中 `question` 必填，`top_k` 默认值为 `2`。
- `json.loads()` 负责模型参数字符串到 Python 字典。
- `json.dumps(..., ensure_ascii=False)` 保留中文 Tool Result。
- 未知工具通过显式名称分支拦截，不动态执行。
- 测试同时 Mock 模型接口和 RAG Tool，不访问外部服务。

## 面试前 5 分钟快速复习

1. 一句话定位：这是一个 Function Calling + RAG 的轻量级单工具 Agent。
2. 核心闭环：模型判断 → Tool Call → Python 执行 RAG → Tool Result → 模型最终回答。
3. 为什么两次模型调用：第一次选工具，第二次基于真实工具结果生成答案。
4. 为什么 `auto`：需要知识时检索，普通问题直接回答。
5. 为什么 `tool_call_id`：关联工具结果和原调用。
6. 安全边界：只允许显式支持的工具，不按模型名称任意执行函数。
7. 测试重点：一次调用分支、两次调用分支、未知工具分支。
8. 测试隔离：Mock DeepSeek 和 RAG，不花费 API、不加载 BGE、不访问 Hugging Face。
9. 诚实局限：单工具、单轮、只处理第一个 Tool Call、异常处理有限、无 UI/API/部署。
10. 下一步：增加 `create_task`，抽象 Tool Registry/Dispatcher，补多工具路由测试。
