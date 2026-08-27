def create_task(
    name: str,
    priority: str = "普通",
) -> dict[str, str]:
    """创建并返回任务对象，不进行持久化。"""
    task = {
        "name": name,
        "priority": priority,
        "status": "待处理",
    }

    return task
