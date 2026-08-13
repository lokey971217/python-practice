# Python Practice

这是一个记录 Python 学习过程的仓库，也包含目前可以独立运行和展示的任务管理器小项目。

## 目录结构

```text
python-practice/
|-- exercises/              # 学习过程、阶段练习和迭代版本
|-- projects/
|   `-- task_manager/
|       |-- task_app.py     # 程序入口与 JSON 读写
|       |-- task_model.py   # Task 类
|       |-- test_task.py    # unittest 自动测试
|       `-- task_data.json  # 示例任务数据
|-- .gitignore
`-- README.md
```

## 练习与项目的区别

- `exercises/` 保存学习过程代码和阶段性版本，可能包含早期写法或重复迭代，用于回顾学习过程，不代表正式项目质量。
- `projects/` 保存经过整理、可以独立运行的项目。目前包含任务管理器项目。

## 完整项目：任务管理器

位置：`projects/task_manager/`

- `task_app.py`：任务管理器演示程序和 JSON 数据读写
- `task_model.py`：任务模型及状态、优先级操作
- `test_task.py`：基于 `unittest` 的单元测试
- `task_data.json`：示例任务数据

目前实现的功能：

- 创建 `Task` 对象
- 修改任务状态
- 修改任务优先级
- 检查任务名称是否为空
- 将任务对象转换为字典
- 将任务数据保存为 JSON 并重新读取
- 使用 `unittest` 进行自动测试

运行项目：

```powershell
cd projects\task_manager
python task_app.py
python test_task.py
```

## 练习记录

`exercises/` 保存从基础语法到函数封装、异常处理、字典 CRUD、任务拆分和天气数据抓取的练习代码。过程版本也保留在这里，方便回顾学习轨迹。

天气练习需要额外依赖：

```powershell
pip install requests beautifulsoup4 pandas openpyxl
python exercises\weather_practice.py
```

## 当前学习阶段

目前处于 Python 基础与简单工程化练习阶段，正在学习类、函数、异常处理、文件读写、目录组织和自动测试。

## 后续计划

继续学习大模型 API、Prompt、RAG 和 AI Agent，并逐步整理为可以运行和展示的小项目。
