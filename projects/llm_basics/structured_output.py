import json
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

system_prompt = """
请把用户输入的任务转换成json格式。

必须包含以下字段：
name:任务名称
priority:只能是“普通”或“紧急”
status:固定为“待处理”
"""

user_input = input("请输入任务：")

response = client.chat.completions.create(
    model = "deepseek-v4-flash",
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ],
    response_format = {"type": "json_object"},
)

json_text = response.choices[0].message.content
task_data = json.loads(json_text)

print("模型返回的json:",json_text)
print("任务名称:", task_data["name"])
print("任务优先级:",task_data["priority"])
print("任务状态:",task_data["status"])