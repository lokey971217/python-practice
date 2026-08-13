def check_task_name(name:str) -> None:
    if name == "":
        raise ValueError("任务名称不能为空")

    print("f任务名称正确：",name)


try:
    check_task_name("")
except ValueError as error:
    print("检查失败：",error)

print("继续执行其他代码")