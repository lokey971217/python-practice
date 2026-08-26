from pathlib import Path

from semantic_rag import (
    MIN_RELEVANCE_SCORE,
    get_model,
    load_knowledge,
    retrieve_top_k_chunks,
    split_knowledge,
)

KNOWLEDGE_FILE = Path(__file__).with_name("knowledge.txt")

def search_knowledge_base(
        question:str,
        top_k:int = 2,
) -> dict[str,object]:
     """从实验室知识库中检索与问题最相关的内容。"""

     # 1. 读取并切分知识库
     knowledge_text = load_knowledge(str(KNOWLEDGE_FILE))
     knowledge_chunks = split_knowledge(knowledge_text)

     # 2. 把所有知识片段转换成向量
     model = get_model()
     chunk_vectors = model.encode(
          knowledge_chunks,
          normalize_embeddings=True,
     )

     # 3. 找出最相关的前 top_k 个片段
     results = retrieve_top_k_chunks(
          question,
          knowledge_chunks,
          chunk_vectors,
          top_k = top_k,
     )

     # 4. 检查最高相似度
     best_score = results[0][1]

     if best_score < MIN_RELEVANCE_SCORE:
          return{
               "found":False,
               "message":"知识库中没有找到足够相关的内容",
               "chunk":[],
          }

     # 5. 返回结构化检索结果
     return{
          "found":True,
          "question":question,
          "chunks":[
               {
                    "content":chunk,
                    "score":round(score,4)
               }
               for chunk,score in results
          ],
     }


if __name__ == "__main__":
    result = search_knowledge_base("设备需要提前多久预约？")

    print("是否找到：", result["found"])

    if result["found"]:
        for index, item in enumerate(result["chunks"], start=1):
            print(f"\n--- 知识片段 {index} ---")
            print(item["content"])
            print(f"相似度：{item['score']:.4f}")
    else:
        print(result["message"])