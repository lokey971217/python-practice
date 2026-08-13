class Task:
    def __init__(
            self,
            name:str,
            priority:str = "普通"
    ) -> None:
        if not name.strip():
            raise ValueError("任务名称不能为空")
        self.name = name
        self.priority = priority
        self.status = "待处理"

    def complete(self) -> None:
        self.status = "已处理"

    def change_priority(
            self,
            new_priority:str
    ) -> None:
        self.priority = new_priority

    def to_dict(self) -> dict:
        return{
            "name":self.name,
            "priority":self.priority,
            "status":self.status
        }