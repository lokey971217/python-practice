import unittest

from rag_tool import search_knowledge_base


class TestRAGTool(unittest.TestCase):

    def test_related_question_returns_found_true(self):
        result = search_knowledge_base(
            "实验设备需要提前多久预约？"
        )

        self.assertTrue(result["found"])


    def test_unrelated_question_returns_found_false(self):
        result = search_knowledge_base(
            "法国的首都是哪里？"
        )

        self.assertFalse(result["found"])

    def test_top_k_limits_number_of_chunks(self):
        result = search_knowledge_base(
            "实验设备需要提前多久预约？",
            top_k=2,
        )

        self.assertLessEqual(
            len(result["chunks"]),
            2,
        )

    def test_each_chunk_contains_content_and_score(self):
        result = search_knowledge_base(
            "实验设备需要提前多久预约？",
            top_k=2,
        )

        for chunk in result["chunks"]:
            self.assertIn("content", chunk)
            self.assertIn("score", chunk)

if __name__ == "__main__":
    unittest.main()