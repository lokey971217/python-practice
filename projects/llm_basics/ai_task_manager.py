"""A small AI-assisted task manager built for learning Function Calling.

The language model is responsible for understanding a natural-language request
and selecting a tool. Local Python functions remain responsible for changing
task data and persisting it to JSON.
"""

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI, OpenAIError


MODEL_NAME = "deepseek-v4-flash"
TASKS_FILE = Path(__file__).with_name("ai_tasks.json")

Task = dict[str, str]
ToolResult = Task | list[Task]


def create_client() -> OpenAI:
    """Create a DeepSeek-compatible client from an environment variable."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY 环境变量")

    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def load_tasks() -> list[Task]:
    """Load tasks from disk, returning an empty list when data is unavailable."""
    try:
        with TASKS_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("任务文件内容损坏，将使用空任务列表")
        return []

    if not isinstance(tasks, list):
        print("任务文件格式错误，将使用空任务列表")
        return []
    return tasks


all_tasks: list[Task] = load_tasks()


def save_tasks() -> None:
    """Persist all current tasks to the local JSON data file."""
    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(all_tasks, file, ensure_ascii=False, indent=4)


def create_task(name: str, priority: str = "普通") -> Task:
    """Create and persist a task in the pending state."""
    task = {
        "name": name,
        "priority": priority,
        "status": "待处理",
    }
    all_tasks.append(task)
    save_tasks()
    return task


def list_tasks() -> list[Task]:
    """Return all tasks currently held in memory."""
    return all_tasks


def complete_task(name: str) -> Task:
    """Mark the first task with the requested name as completed."""
    for task in all_tasks:
        if task["name"] == name:
            task["status"] = "已完成"
            save_tasks()
            return task

    return {"error": f"没有找到任务:{name}"}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "根据用户的要求创建一个任务",
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
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "查看当前保存的所有任务",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "根据任务名称将指定任务标记为已完成",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "需要完成的任务名称",
                    },
                },
                "required": ["name"],
            },
        },
    },
]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> ToolResult:
    """Dispatch a model-selected tool to the matching local Python function."""
    if tool_name == "create_task":
        return create_task(
            name=arguments["name"],
            priority=arguments["priority"],
        )
    if tool_name == "list_tasks":
        return list_tasks()
    if tool_name == "complete_task":
        return complete_task(name=arguments["name"])
    raise ValueError(f"程序暂时不支持工具：{tool_name}")


def process_user_request(client: OpenAI, user_input: str) -> str:
    """Run one complete Function Calling round trip and return the final reply."""
    messages: list[Any] = [{"role": "user", "content": user_input}]
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    message = response.choices[0].message

    if not message.tool_calls:
        return message.content or "模型没有选择可执行的工具"

    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    if not isinstance(arguments, dict):
        raise ValueError("模型返回的工具参数不是 JSON 对象")

    tool_result = execute_tool(tool_call.function.name, arguments)
    messages.append(message)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result, ensure_ascii=False),
        }
    )

    final_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
    )
    return final_response.choices[0].message.content or "任务操作已完成"


def main() -> None:
    """Start the interactive command-line application."""
    try:
        client = create_client()
    except RuntimeError as error:
        print(error)
        return

    while True:
        user_input = input("请输入你的要求（输入“退出”结束）：")
        if user_input.strip() == "退出":
            print("任务管理器已退出")
            break

        try:
            reply = process_user_request(client, user_input)
            print("模型最终回复：", reply)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            print("工具调用参数错误：", error)
        except OpenAIError as error:
            print("模型请求失败：", error)


if __name__ == "__main__":
    main()
