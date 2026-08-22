import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from semantic_rag import generate_answer, retrieve_best_chunk, split_knowledge


class TestSemanticRAG(unittest.TestCase):
    def test_split_knowledge(self) -> None:
        text = "片段一\n\n片段二\n\n"

        result = split_knowledge(text)

        self.assertEqual(
            result,
            ["片段一", "片段二"],
        )

    @patch("semantic_rag.get_model")
    def test_retrieve_best_chunk(self, mock_get_model) -> None:
        mock_model = mock_get_model.return_value
        mock_model.encode.return_value = np.array([1.0, 0.0])

        knowledge_chunks = [
            "设备需要提前一天预约",
            "实验数据需要及时备份",
        ]

        chunk_vectors = np.array([
            [1.0, 0.0],
            [0.0, 1.0],
        ])

        best_chunk, best_score = retrieve_best_chunk(
            "设备需要提前多久预约",
            knowledge_chunks,
            chunk_vectors,
        )

        self.assertEqual(
            best_chunk,
            "设备需要提前一天预约",
        )
        self.assertAlmostEqual(
            float(best_score),
            1.0,
        )
        mock_model.encode.assert_called_once_with(
            "设备需要提前多久预约",
            normalize_embeddings=True,
        )

    @patch("semantic_rag.get_client")
    def test_generate_answer(self, mock_get_client) -> None:
        mock_message = MagicMock()
        mock_message.content = "设备需要提前一天预约。"

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_create = mock_get_client.return_value.chat.completions.create
        mock_create.return_value = mock_response

        answer = generate_answer(
            "设备需要提前多久预约？",
            "实验设备需要至少提前一天预约。",
        )

        self.assertEqual(answer, "设备需要提前一天预约。")
        mock_create.assert_called_once()

    @patch("semantic_rag.get_client")
    def test_generate_answer_handles_error(self, mock_get_client) -> None:
        mock_create = mock_get_client.return_value.chat.completions.create
        mock_create.side_effect = RuntimeError("模拟网络错误")

        answer = generate_answer(
            "设备需要提前多久预约？",
            "实验设备需要至少提前一天预约。",
        )

        self.assertEqual(
            answer,
            "模型调用失败：模拟网络错误",
        )


if __name__ == "__main__":
    unittest.main()
