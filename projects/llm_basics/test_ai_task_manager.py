"""Unit tests for the local task-management behavior."""

import unittest
from unittest.mock import mock_open, patch

import ai_task_manager


class TestAITaskManager(unittest.TestCase):
    def setUp(self) -> None:
        """Isolate the shared in-memory task list before every test."""
        self.original_tasks = ai_task_manager.all_tasks.copy()
        ai_task_manager.all_tasks.clear()

    def tearDown(self) -> None:
        """Restore the task list so tests do not affect local application data."""
        ai_task_manager.all_tasks[:] = self.original_tasks

    def test_load_tasks_returns_list(self) -> None:
        task_file = mock_open(
            read_data='[{"name":"学习测试","priority":"普通","status":"待处理"}]'
        )

        with patch("pathlib.Path.open", task_file):
            tasks = ai_task_manager.load_tasks()

        self.assertIsInstance(tasks, list)
        self.assertEqual(tasks[0]["name"], "学习测试")

    def test_load_tasks_returns_empty_list_when_file_is_missing(self) -> None:
        with patch("pathlib.Path.open", side_effect=FileNotFoundError):
            tasks = ai_task_manager.load_tasks()

        self.assertEqual(tasks, [])

    def test_load_tasks_returns_empty_list_for_invalid_json(self) -> None:
        with (
            patch("pathlib.Path.open", mock_open(read_data="{invalid json")),
            patch("builtins.print") as mock_print,
        ):
            tasks = ai_task_manager.load_tasks()

        self.assertEqual(tasks, [])
        mock_print.assert_called_once_with("任务文件内容损坏，将使用空任务列表")

    def test_list_tasks_returns_all_tasks(self) -> None:
        task = {"name": "测试任务", "priority": "普通", "status": "待处理"}
        ai_task_manager.all_tasks.append(task)

        result = ai_task_manager.list_tasks()

        self.assertEqual(result, [task])

    @patch("ai_task_manager.save_tasks")
    def test_create_task(self, mock_save_tasks) -> None:
        task = ai_task_manager.create_task("测试任务", "紧急")

        self.assertEqual(
            task,
            {"name": "测试任务", "priority": "紧急", "status": "待处理"},
        )
        self.assertIn(task, ai_task_manager.all_tasks)
        mock_save_tasks.assert_called_once_with()

    @patch("ai_task_manager.save_tasks")
    def test_complete_task(self, mock_save_tasks) -> None:
        task = {"name": "测试任务", "priority": "紧急", "status": "待处理"}
        ai_task_manager.all_tasks.append(task)

        result = ai_task_manager.complete_task("测试任务")

        self.assertEqual(result["status"], "已完成")
        self.assertEqual(task["status"], "已完成")
        mock_save_tasks.assert_called_once_with()

    def test_complete_missing_task_returns_error(self) -> None:
        result = ai_task_manager.complete_task("不存在的任务")

        self.assertEqual(result, {"error": "没有找到任务:不存在的任务"})

    @patch("ai_task_manager.create_task")
    def test_execute_tool_dispatches_to_create_task(self, mock_create_task) -> None:
        expected = {"name": "写项目说明", "priority": "紧急", "status": "待处理"}
        mock_create_task.return_value = expected

        result = ai_task_manager.execute_tool(
            "create_task",
            {"name": "写项目说明", "priority": "紧急"},
        )

        self.assertEqual(result, expected)
        mock_create_task.assert_called_once_with(name="写项目说明", priority="紧急")


if __name__ == "__main__":
    unittest.main()
