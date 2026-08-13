def is_execllent(score:float) -> bool:
    return score >= 90.0

def calculate_average(scores:list[float]) -> float:
    if not scores:
        return 0.0
    average = sum(scores)/len(scores)
    return average

def create_task(name:str,priority:str = "普通") -> dict[str,str]:
    task = {
        "name": name,
        "priority": priority,
        "status": "待处理"
    }
    return task

def update_task_status(
        task:dict[str,str],
        new_status:str
) -> dict[str,str]:
    update_task = task.copy()
    update_task["status"] = new_status
    return update_task

def filter_task_by_priority(
        tasks:list[dict[str,str]],
        priority:str
) -> list[dict[str,str]]:
    filtered_tasks = []
    for task in tasks:
        if task["priority"] == priority:
            filtered_tasks.append(task)
    return filtered_tasks

def main() -> None:
    task1 = create_task("读取论文")
    task2 = create_task("分析实验数据","紧急")
    print(task1)
    print(task2)


    task3 = update_task_status(task1,"已处理")
    print(task1)#原任务
    print(task3)#现任务


    all_tasks = [task1,task2,task3]
    urgent_tasks = filter_task_by_priority(all_tasks,"紧急")
    normal_tasks = filter_task_by_priority(all_tasks,"普通")
    print(urgent_tasks)
    print(normal_tasks)









    scores1 = [90,80,70]
    scores2 = []
    print(calculate_average(scores1))  # Output: 80.0
    print(calculate_average(scores2))  # Output: 0.0


    result1 = is_execllent(95)
    result2 = is_execllent(80)

    print(result1)  # Output: True
    print(result2)  # Output: False

if __name__ == "__main__":
    main()