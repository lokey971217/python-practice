import os
import unittest
from unittest.mock import MagicMock, patch


# 测试仅需让 OpenAI 客户端完成初始化，不会发送真实请求。
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

from agent_basics.rag_agent import run_agent


class TestRAGAgent(unittest.TestCase):
    @patch("agent_basics.rag_agent.create_task")
    @patch("agent_basics.rag_agent.search_knowledge_base")
    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_normal_question_uses_no_tool(
        self,
        mock_create,
        mock_search,
        mock_task,
    ):
        # 模拟模型直接回答，不调用任何工具
        message = MagicMock()
        message.tool_calls = None
        message.content = "1+1等于2。"

        response = MagicMock()
        response.choices = [
            MagicMock(message=message)
        ]

        mock_create.return_value = response

        answer = run_agent("1+1等于几？")

        self.assertEqual(
            answer,
            "1+1等于2。",
        )

        # 普通问题两个工具都不应该调用
        mock_search.assert_not_called()
        mock_task.assert_not_called()

        # 模型只调用一次
        mock_create.assert_called_once()


    @patch("agent_basics.rag_agent.create_task")
    @patch("agent_basics.rag_agent.search_knowledge_base")
    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_lab_question_uses_rag(
        self,
        mock_create,
        mock_search,
        mock_task,
    ):
        # 第一次模型调用：选择 RAG Tool
        tool_call = MagicMock()
        tool_call.id = "call_rag"
        tool_call.function.name = "search_knowledge_base"
        tool_call.function.arguments = (
            '{"question": "设备需要提前多久预约？", "top_k": 2}'
        )

        first_message = MagicMock()
        first_message.tool_calls = [tool_call]

        first_response = MagicMock()
        first_response.choices = [
            MagicMock(message=first_message)
        ]

        # 模拟 RAG Tool 返回结果
        mock_search.return_value = {
            "found": True,
            "question": "设备需要提前多久预约？",
            "chunks": [
                {
                    "content": "实验设备需要至少提前一天预约。",
                    "score": 0.81,
                }
            ],
        }

        # 第二次模型调用：生成最终回答
        final_message = MagicMock()
        final_message.content = (
            "实验设备需要至少提前一天预约。"
        )

        final_response = MagicMock()
        final_response.choices = [
            MagicMock(message=final_message)
        ]

        mock_create.side_effect = [
            first_response,
            final_response,
        ]

        answer = run_agent(
            "设备需要提前多久预约？"
        )

        self.assertEqual(
            answer,
            "实验设备需要至少提前一天预约。",
        )

        # RAG 应该被调用
        mock_search.assert_called_once_with(
            question="设备需要提前多久预约？",
            top_k=2,
        )

        # create_task 不应该被误调用
        mock_task.assert_not_called()

        # 模型总共调用两次
        self.assertEqual(mock_create.call_count, 2)

    @patch("agent_basics.rag_agent.create_task")
    @patch("agent_basics.rag_agent.search_knowledge_base")
    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_task_question_uses_create_task(
        self,
        mock_create,
        mock_search,
        mock_task,
    ):
        # 第一次模型调用：选择 create_task
        tool_call = MagicMock()
        tool_call.id = "call_task"
        tool_call.function.name = "create_task"
        tool_call.function.arguments = (
            '{"name": "学习Python", "priority": "紧急"}'
        )

        first_message = MagicMock()
        first_message.tool_calls = [tool_call]

        first_response = MagicMock()
        first_response.choices = [
            MagicMock(message=first_message)
        ]

        # 模拟 create_task 返回结果
        mock_task.return_value = {
            "name": "学习Python",
            "priority": "紧急",
            "status": "待处理",
        }

        # 第二次模型调用：生成最终回答
        final_message = MagicMock()
        final_message.content = (
            "已创建学习Python的紧急任务。"
        )

        final_response = MagicMock()
        final_response.choices = [
            MagicMock(message=final_message)
        ]

        mock_create.side_effect = [
            first_response,
            final_response,
        ]

        answer = run_agent(
            "帮我创建一个学习Python的紧急任务"
        )

        self.assertEqual(
            answer,
            "已创建学习Python的紧急任务。",
        )

        # create_task 应该被正确调用
        mock_task.assert_called_once_with(
            name="学习Python",
            priority="紧急",
        )

        # 不应该误调用 RAG
        mock_search.assert_not_called()

        # Function Calling 完整流程调用模型两次
        self.assertEqual(mock_create.call_count, 2)

    @patch("agent_basics.rag_agent.create_task")
    @patch("agent_basics.rag_agent.search_knowledge_base")
    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_unsupported_tool_returns_message(
        self,
        mock_create,
        mock_search,
        mock_task,
    ):
        tool_call = MagicMock()
        tool_call.id = "call_unknown"
        tool_call.function.name = "unknown_tool"
        tool_call.function.arguments = "{}"

        message = MagicMock()
        message.tool_calls = [tool_call]

        response = MagicMock()
        response.choices = [
            MagicMock(message=message)
        ]

        mock_create.return_value = response

        answer = run_agent(
            "调用一个未知工具"
        )

        self.assertEqual(
            answer,
            "暂不支持这个工具。",
        )

        mock_search.assert_not_called()
        mock_task.assert_not_called()


if __name__ == "__main__":
    unittest.main()
