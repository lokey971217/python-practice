import json
import os
from openai import OpenAI

# 1.创建DeepSeek客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# 2.定义真正执行任务的python函数
def create_task(
        name:str,
        priority:str = "普通",
) -> dict[str,str]:
    task = {
        "name":name,
        "priority":priority,
        "status":"待处理",
    }

    return task


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
                        "descriptions":"任务名称",
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
    }
]


# 4.接收用户输入
user_input = input("请输入你的要求：")


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

        print("函数执行结果：",task_result)

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
else:
    print("模型没有调用函数：", message.content)
