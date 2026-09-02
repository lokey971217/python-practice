import json
import os
import sys
from pathlib import Path

from openai import OpenAI

RAG_DIR = Path(__file__).parent.parent / "rag_basics"
sys.path.insert(0, str(RAG_DIR))

from rag_tool import search_knowledge_base
from agent_basics.task_tool import create_task


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM_PROMPT = (
    "你是一个可以使用工具的智能助手。"
    "当用户询问实验室规定、设备使用、预约、数据管理等"
    "需要知识库信息的问题时，调用 search_knowledge_base 工具。"
    "当用户要求创建任务时，调用 create_task 工具。"
    "如果不需要工具，可以直接回答。"
)


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "搜索实验室知识库，获取与用户问题相关的实验室规定和信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "需要在实验室知识库中查询的问题",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "最多返回多少个相关知识片段",
                        "default": 2,
                    },
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "根据用户要求创建一个待处理任务。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "任务名称",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["普通", "紧急"],
                        "description": "任务优先级",
                    },
                },
                "required": ["name", "priority"],
            },
        },
    },
]


TOOL_REGISTRY = {
    "search_knowledge_base": search_knowledge_base,
    "create_task": create_task,
}


def dispatch_tool(
    tool_name: str,
    arguments: dict[str, object],
) -> object:
    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        return {
            "error": f"暂不支持这个工具:{tool_name}"
        }

    return tool_function(**arguments)


def create_initial_messages() -> list[dict]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]


def run_agent(
        user_input: str,
        messages:list[dict],
) -> str:
    # 1. 建立对话记录
    messages.append(
        {
            "role":"user",
            "content":user_input,
        }
    )

    # 2. 第一次调用模型，让模型决定是否使用工具
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # 3. 如果模型决定调用工具
    if message.tool_calls:
        tool_call = message.tool_calls[0]

        arguments = json.loads(
            tool_call.function.arguments
        )

        # 4. 根据工具名称执行不同 Python 函数

        tool_name = tool_call.function.name

        tool_result = dispatch_tool(
            tool_name,
            arguments,
        )

        if isinstance(tool_result, dict) and "error" in tool_result:
            return tool_result["error"]

        # 5. 保存模型提出的工具调用
        messages.append(message)

        # 6. 把工具执行结果返回给模型
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    tool_result,
                    ensure_ascii=False,
                ),
            }
        )

        # 7. 第二次调用模型，根据工具结果生成最终回答
        final_response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            tools=TOOL_DEFINITIONS,
        )

        final_message = final_response.choices[0].message

        messages.append(
            {
                "role": "assistant",
                "content": final_message.content,
            }
        )

        return final_message.content


    # 8. 不需要工具时，保存助手回复并返回
    messages.append(
        {
            "role": "assistant",
            "content": message.content,
        }
    )

    return message.content


def main() -> None:
    messages = create_initial_messages()

    while True:
        user_input = input("\n请输入你的问题，输入 exit 退出：")

        if user_input == "exit":
            print("已退出多轮对话。")
            break

        answer = run_agent(
            user_input,
            messages,
        )

        print("\n模型最终回复：")
        print(answer)


if __name__ == "__main__":
    main()
