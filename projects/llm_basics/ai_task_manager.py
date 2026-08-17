import json
import os

from openai import OpenAI

# 1.创建DeepSeek客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

TASKS_FILE = "ai_tasks.json"


def load_tasks() -> list[dict[str, str]]:
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("任务文件内容损坏，将使用空任务列表")
        return []


all_tasks: list[dict[str, str]] = load_tasks()

# 2.定义真正执行任务的python函数
def save_tasks() -> None:
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(all_tasks, file, ensure_ascii=False, indent=4)


def create_task(
    name: str,
    priority: str = "普通",
) -> dict[str, str]:
    task = {
        "name": name,
        "priority": priority,
        "status": "待处理",
    }

    all_tasks.append(task)
    save_tasks()
    return task

def list_tasks() -> list[dict[str, str]]:
    return all_tasks


def complete_task(name: str) -> dict[str, str]:
    for task in all_tasks:
        if task["name"] == name:
            task["status"] = "已完成"
            save_tasks()
            return task

    return {"error": f"没有找到任务:{name}"}

# 3.向模型介绍create_task工具
tools = [
    {
        "type":"function",
        "function":{
            "name":"create_task",
            "description":"根据用户的要求创建一个任务",
            "parameters":{
                "type":"object",
                "properties":{
                    "name":{
                        "type":"string",
                        "description":"任务名称",
                    },
                    "priority":{
                        "type":"string",
                        "enum":["普通","紧急"],
                        "description":"任务优先级",
                    },
                },
                "required":["name","priority"],
            },
        },
    },

    {
         "type":"function",
         "function":{
              "name":"list_tasks",
              "description":"查看当前保存的所有任务",
              "parameters":{
                   "type":"object",
                   "properties":{},
              },
         },
    },

    {
         "type":"function",
         "function":{
              "name":"complete_task",
              "description":"根据任务名称将指定任务标记为已完成",
              "parameters":{
                   "type":"object",
                   "properties":{
                        "name":{
                             "type":"string",
                             "description":"需要完成的任务名称",
                        },
                   },
                   "required":["name"],
              },
         },
    },
]
# 4.接收用户输入
def main() -> None:
    while True:
        user_input = input("请输入你的要求(输入“退出”结束):")

        if user_input.strip() == "退出":
            print("任务管理器已退出")
            break


    # 5.建立对话记录
        messages = [
            {
                "role":"user",
                "content":user_input,
            }
        ]


        # 6.第一次调用模型
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages = messages,
            tools=tools,
            tool_choice="auto",
        )


        # 7.取出模型消息,看是否要调用create_task函数
        message = response.choices[0].message


        # 8.检查模型是否选择了函数
        if message.tool_calls:
            tool_call = message.tool_calls[0]

            # 9.把模型生成的JSON参数转换成python字典
            arguments_json = tool_call.function.arguments
            arguments = json.loads(arguments_json)

            print("模型选择的函数：", tool_call.function.name)
            print("转换后的字典：", arguments)


            # 10.真正执行create_task函数
            if tool_call.function.name == "create_task":
                task_result = create_task(
                    name = arguments["name"],
                    priority = arguments["priority"],
                )

            elif tool_call.function.name == "list_tasks":
                task_result = list_tasks()

            elif tool_call.function.name == "complete_task":
                task_result = complete_task(
                    name=arguments["name"]
                )

            else:
                print("程序暂时不支持这个函数")
                continue

            print("函数执行结果：",task_result)
            print("当前所有任务：",all_tasks)

                # 11.保存模型刚才提出的函数调用
            messages.append(message)

                # 12.保存python函数的执行结果
            messages.append(
                    {
                        "role":"tool",
                        "tool_call_id":tool_call.id,
                        "content":json.dumps(
                            task_result,
                            ensure_ascii=False,
                        ),
                    }
                )

                # 13.第二次调用模型

            final_response = client.chat.completions.create(
                        model="deepseek-v4-flash",
                        messages=messages,
                        tools=tools,
                    )

                # 14.取出并打印最终回复
            final_message = final_response.choices[0].message

            print("模型最终回复：", final_message.content)

        else:
                    print("程序暂不支持这个函数")
if __name__ == "__main__":
    main()
