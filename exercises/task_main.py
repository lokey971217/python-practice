from task_tools import(
    create_task,
    update_task_status,
    filter_task_by_priority
)

def main() -> None:
    try:
        invalid_task = create_task("整理实验记录","非常紧急")
        print(invalid_task)
    except ValueError as error:
        print("创建任务失败:", error)

    try:
        error_task = create_task("")
        print(error_task)
    except ValueError as error:
        print("创建任务失败:", error)


    task1 = create_task("读取论文")
    task2 = create_task("分析实验数据","紧急")
    task3 = update_task_status(task1,"已处理")

    all_tasks = [task1,task2,task3]

    urgent_tasks = filter_task_by_priority(all_tasks,"紧急")
    normal_tasks = filter_task_by_priority(all_tasks,"普通")

    print("所有任务：", all_tasks)
    print("紧急任务：", urgent_tasks)
    print("普通任务：", normal_tasks)

if __name__ == "__main__":
    main()