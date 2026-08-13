def create_task(name:str,priority:str = "普通") -> dict[str,str]:
    if not name.strip():
        raise ValueError("任务名称不能为空")

    valid_priorities = ["普通","紧急"]
    if priority not in valid_priorities:
        raise ValueError(f"不支持的优先级: {priority}")


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

