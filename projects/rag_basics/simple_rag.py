import os
from openai import OpenAI

KNOWLEDGE_FILE = "knowledge.txt"


def load_knowledge() -> str:
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return file.read()


def split_knowledge(text: str) -> list[str]:
    # 知识库中的每个主题之间用空行分隔。
    chunks = text.split("\n\n")

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def calculate_score(question: str, chunk: str) -> int:
    # 去重后统计字符重合数，保留当前容易理解的基础检索逻辑。
    question_chars = set(question)

    score = sum(
        1
        for char in question_chars
        if char.strip() and char in chunk
    )

    return score


def retrieve_best_chunk(question: str, chunks: list[str]) -> str:
    best_chunk = ""
    best_score = -1

    for chunk in chunks:
        score = calculate_score(question, chunk)

        if score > best_score:
            best_score = score
            best_chunk = chunk
    return best_chunk


def generate_answer(question: str, context: str) -> str:
    try:
        # 在真正调用模型时才创建客户端，导入模块不会发起 API 请求。
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是实验室知识库助手，只能根据提供的知识片段回答问题。"
                        "如果知识片段不包含答案，请明确说明知识库中没有相关信息，不要编造。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"知识片段：\n{context}\n\n用户问题：\n{question}",
                },
            ],
        )

        return response.choices[0].message.content

    except Exception as error:
        return f"模型调用失败：{error}"


def main() -> None:
    knowledge_text = load_knowledge()
    knowledge_chunks = split_knowledge(knowledge_text)

    question = input("请输入问题:\n")
    best_chunk = retrieve_best_chunk(question, knowledge_chunks)

    print("\n检索到的知识片段:")
    print(best_chunk)

    answer = generate_answer(question, best_chunk)

    print("\n模型生成的答案：")
    print(answer)


if __name__ == "__main__":
    main()
