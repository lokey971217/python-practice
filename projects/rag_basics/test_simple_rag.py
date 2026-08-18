import unittest

import simple_rag


class TestSimpleRAG(unittest.TestCase):
    def test_split_knowledge(self) -> None:
        text = "片段一\n内容一\n\n片段二\n内容二"

        chunks = simple_rag.split_knowledge(text)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], "片段一\n内容一")

    def test_retrieve_best_chunk(self) -> None:
        chunks = [
            "实验室工作日开放。",
            "实验室设备需要提前一天预约。",
        ]

        result = simple_rag.retrieve_best_chunk(
            "设备需要提前多久预约？",
            chunks
        )

        self.assertEqual(result,"实验室设备需要提前一天预约。")

    def test_relevant_chunk_has_higher_score(self) -> None:
        question = "设备需要提前多久预约？"

        relevant_score = simple_rag.calculate_score(
            question,
            "实验室设备需要提前一天预约。",
        )

        unrelated_score = simple_rag.calculate_score(
            question,
            "实验室周末正常开放。",
        )

        self.assertGreater(relevant_score, unrelated_score)


if __name__ == "__main__":
    unittest.main()