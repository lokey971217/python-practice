import unittest
from unittest.mock import patch
import ai_task_manager


class TestAITaskManager(unittest.TestCase):
    @patch("ai_task_manager.save_tasks")
    def test_complete_task(self,mock_save_tasks) -> None:
        task = {
            "name":"测试任务",
            "priority":"紧急",
            "status":"待处理",
        }
        ai_task_manager.all_tasks.append(task)

        result = ai_task_manager.complete_task("测试任务")

        self.assertEqual(result["status"], "已完成")
        self.assertEqual(task["status"], "已完成")
        mock_save_tasks.assert_called_once()
    @patch("ai_task_manager.save_tasks")
    def test_create_task(self,mock_save_tasks) -> None:
        task = ai_task_manager.create_task("测试任务","紧急")

        self.assertEqual(task["name"],"测试任务")
        self.assertEqual(task["priority"], "紧急")
        self.assertEqual(task["status"], "待处理")
        self.assertIn(task, ai_task_manager.all_tasks)
        mock_save_tasks.assert_called_once()

    def setUp(self) -> None:
        self.original_tasks = ai_task_manager.all_tasks.copy()
        ai_task_manager.all_tasks.clear()

    def tearDown(self) -> None:
        ai_task_manager.all_tasks[:] = self.original_tasks

    def test_load_tasks_returns_list(self) ->None:
        tasks = ai_task_manager.load_tasks()

        self.assertIsInstance(tasks,list)

    def test_list_tasks_return_all_tasks(self) -> None:
        result = ai_task_manager.list_tasks()

        self.assertEqual(result, ai_task_manager.all_tasks)

    def test_complete_missing_task_returns_error(self) -> None:
        result = ai_task_manager.complete_task("不存在的任务")

        self.assertEqual(
            result,
            {"error": "没有找到任务:不存在的任务"},
        )



if __name__ == "__main__":
    unittest.main()