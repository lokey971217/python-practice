import os

from openai import OpenAI
from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-zh-v1.5"
MIN_RELEVANCE_SCORE = 0.55

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """首次进行语义检索时再加载向量模型。"""
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_client() -> OpenAI:
    """使用环境变量创建 DeepSeek 兼容客户端。"""
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )


def load_knowledge(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def split_knowledge(text: str) -> list[str]:
    # 知识库中的每个主题之间用空行分隔。
    chunks = text.split("\n\n")

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def retrieve_best_chunk(question, knowledge_chunks, chunk_vectors):
    model = get_model()
    question_vector = model.encode(
        question,
        normalize_embeddings=True,
    )

    # 向量已经归一化，因此点积可用于比较余弦相似度。
    similarities = chunk_vectors @ question_vector

    best_index = similarities.argmax()
    best_score = similarities[best_index]
    best_chunk = knowledge_chunks[best_index]

    return best_chunk, best_score


def retrieve_top_k_chunks(
    question: str,
    knowledge_chunks: list[str],
    chunk_vectors,
    top_k: int = 2,
) -> list[tuple[str, float]]:
    """学习用 Top-K 辅助函数；当前主流程仍使用单片段检索。"""
    model = get_model()
    question_vector = model.encode(
        question,
        normalize_embeddings=True,
    )

    similarities = chunk_vectors @ question_vector
    top_indices = similarities.argsort()[::-1][:top_k]

    return [
        (knowledge_chunks[index], float(similarities[index]))
        for index in top_indices
    ]


def generate_answer(question: str, context: str) -> str:
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是实验室知识库助手。"
                        "只能根据提供的知识片段回答问题。"
                        "如果知识片段中没有答案，就明确说明无法回答。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"知识片段：\n{context}\n\n"
                        f"用户问题：\n{question}"
                    ),
                },
            ],
        )

        return response.choices[0].message.content

    except Exception as error:
        return f"模型调用失败：{error}"


def main() -> None:
    # 读取知识库、切片，并生成归一化知识向量。
    knowledge_text = load_knowledge("knowledge.txt")
    knowledge_chunks = split_knowledge(knowledge_text)

    model = get_model()
    chunk_vectors = model.encode(
        knowledge_chunks,
        normalize_embeddings=True,
    )

    question = input("请输入问题：")
    best_chunk, best_score = retrieve_best_chunk(
        question,
        knowledge_chunks,
        chunk_vectors,
    )

    print("最高相似度", round(float(best_score), 4))

    if best_score < MIN_RELEVANCE_SCORE:
        print("\n没有找到足够相关的知识，无法根据知识库进行回答。")
        return

    print("\n检索到的知识片段：")
    print(best_chunk)

    answer = generate_answer(question, best_chunk)

    print("\n模型生成的答案：")
    print(answer)


if __name__ == "__main__":
    main()
