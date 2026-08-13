import json
from task_model import Task



task1 = Task("读取论文")
task2 = Task("分析实验数据","紧急")
task1.complete()
task1.change_priority("紧急")

print(task1.name)
print(task1.priority)
print(task1.status)
print("task1的状态",task1.status)

print(task2.name)
print(task2.priority)
print(task2.status)
print("task2的状态",task2.status)

print("task1修改后的优先级:",task1.priority)

try:
    task3 = Task("")
    print(task3.name)
except ValueError as error:
    print("创建任务失败:",error)

task1_dict = task1.to_dict()
print("task1字典:",task1_dict)

with open("task_data.json","w",encoding="utf-8") as file:
    json.dump(
        task1_dict,file,ensure_ascii=False,indent=4)
print("任务已保存")

with open("task_data.json","r",encoding="utf-8") as file:
    loaded_task = json.load(file)

print("读取到的任务：",loaded_task)
print("任务名称：",loaded_task["name"])
print("任务状态：",loaded_task["status"])
