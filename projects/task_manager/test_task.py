import unittest

from task_model import Task


class TestTask(unittest.TestCase):
    def test_create_task(self) -> None:
        task = Task("读取论文")


        self.assertEqual(task.name, "读取论文")
        self.assertEqual(task.priority, "普通")
        self.assertEqual(task.status, "待处理")

    def test_complete_task(self) -> None:

        task = Task("获取论文")
        task.complete()

        self.assertEqual(task.status, "已处理")

    def test_empty_name_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            Task("")


if __name__ == "__main__":
    unittest.main()