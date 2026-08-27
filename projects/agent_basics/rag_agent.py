import json
import os
import sys
from pathlib import Path

from openai import OpenAI

RAG_DIR = Path(__file__).parent.parent / "rag_basics"
sys.path.insert(0, str(RAG_DIR))

from rag_tool import search_knowledge_base


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


tools = [
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
    }
]


def run_agent(user_input: str) -> str:
    # 1. 建立对话记录
    messages = [
        {
            "role": "system",
            "content": (
                "你是实验室助手。"
                "当用户询问实验室规定、设备使用、预约、数据管理等"
                "需要知识库信息的问题时，可以调用 search_knowledge_base 工具。"
                "如果是普通闲聊，可以直接回答。"
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    # 2. 第一次调用模型，让模型决定是否使用工具
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # 3. 如果模型决定调用工具
    if message.tool_calls:
        tool_call = message.tool_calls[0]

        arguments = json.loads(
            tool_call.function.arguments
        )

        if tool_call.function.name == "search_knowledge_base":
            tool_result = search_knowledge_base(
                question=arguments["question"],
                top_k=arguments.get("top_k", 2),
            )

            # 保存模型提出的工具调用
            messages.append(message)

            # 保存工具执行结果
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

            # 第二次调用模型
            final_response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                tools=tools,
            )

            return final_response.choices[0].message.content

        return "暂不支持这个工具。"

    # 4. 不需要工具时，直接返回模型回答
    return message.content


def main() -> None:
    user_input = input("请输入你的问题：")

    answer = run_agent(user_input)

    print("\n模型最终回复：")
    print(answer)


if __name__ == "__main__":
    main()
