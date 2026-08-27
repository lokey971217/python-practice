import os
import unittest
from unittest.mock import MagicMock, patch


# 测试时不真正使用 API Key，只保证导入 rag_agent 时 client 能创建
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

from agent_basics.rag_agent import run_agent


class TestRAGAgent(unittest.TestCase):
    @patch("agent_basics.rag_agent.search_knowledge_base")
    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_normal_question_does_not_use_rag(
        self,
        mock_create,
        mock_search,
    ):
        # 模拟 DeepSeek 直接回答，不调用任何工具
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "1+1等于2。"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]

        mock_create.return_value = mock_response

        answer = run_agent("1+1等于几？")

        self.assertEqual(answer, "1+1等于2。")

        # 普通问题不应该调用 RAG
        mock_search.assert_not_called()

        # 只需要调用一次 DeepSeek
        mock_create.assert_called_once()

    @patch("agent_basics.rag_agent.search_knowledge_base")
    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_lab_question_uses_rag(
        self,
        mock_create,
        mock_search,
    ):
        # 第一次 DeepSeek 返回：决定调用 search_knowledge_base
        tool_call = MagicMock()
        tool_call.id = "call_123"
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

        # 模拟 RAG 工具返回结果
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

        # 第二次 DeepSeek 返回最终答案
        final_message = MagicMock()
        final_message.content = "实验设备需要至少提前一天预约。"

        final_response = MagicMock()
        final_response.choices = [
            MagicMock(message=final_message)
        ]

        # 第一次调用返回工具调用，第二次调用返回最终答案
        mock_create.side_effect = [
            first_response,
            final_response,
        ]

        answer = run_agent("设备需要提前多久预约？")

        self.assertEqual(
            answer,
            "实验设备需要至少提前一天预约。",
        )

        # 确认真正调用了我们的 RAG Tool
        mock_search.assert_called_once_with(
            question="设备需要提前多久预约？",
            top_k=2,
        )

        # Function Calling 完整流程应该调用模型两次
        self.assertEqual(mock_create.call_count, 2)

    @patch("agent_basics.rag_agent.client.chat.completions.create")
    def test_unsupported_tool_returns_message(
        self,
        mock_create,
    ):
        # 模拟模型调用一个当前程序不支持的工具
        tool_call = MagicMock()
        tool_call.id = "call_456"
        tool_call.function.name = "unknown_tool"
        tool_call.function.arguments = "{}"

        mock_message = MagicMock()
        mock_message.tool_calls = [tool_call]

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=mock_message)
        ]

        mock_create.return_value = mock_response

        answer = run_agent("帮我执行一个未知工具")

        self.assertEqual(
            answer,
            "暂不支持这个工具。",
        )


if __name__ == "__main__":
    unittest.main()
