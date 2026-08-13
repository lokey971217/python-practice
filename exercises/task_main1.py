from task_tools import (
    create_task,
    update_task_status
)

def main() -> None:
    task1 = create_task("读取论文")
    task2 = create_task("分析实验数据", "紧急")
    task3 = update_task_status(task1, "已处理")

    print(task1)
    print(task2)
    print(task3)


if __name__ == "__main__":
    main()