import json
import asyncio
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.run_config import RunConfig 

from langchain_ollama import ChatOllama, OllamaEmbeddings

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from src.rag import rag_service
from src.config import cfg

async def main():
    print(f"🚀 Запуск Ragas с локальным конфигом...")
    print(f"🤖 Judge Model: {cfg.TEST_MODEL}")
    print(f"🧠 Embeddings: {cfg.EMBEDDING_MODEL}")

    judge_llm = ChatOllama(
        model=cfg.TEST_MODEL,
        base_url=cfg.BASE_URL,
        temperature=0,  
        timeout=120     
    )

    judge_embeddings = OllamaEmbeddings(
        model=cfg.EMBEDDING_MODEL,
        base_url=cfg.BASE_URL
    )

    evaluator_llm = LangchainLLMWrapper(judge_llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(judge_embeddings)

    data_path = os.path.join("tests", "test_data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_path} не найден.")
        return

    user_inputs = []
    references = []
    responses = []
    retrieved_contexts = []

    print(f"📝 Генерация ответов через RAG ({len(test_cases)} вопросов)...")

    for i, case in enumerate(test_cases, 1):
        q = case["question"]
        gt = case["ground_truth"] 
        
        print(f"[{i}/{len(test_cases)}] Вопрос: {q[:40]}...")

        try:
            docs = rag_service.retriever.invoke(q)
            current_contexts = [doc.page_content for doc in docs]

           
            full_response = await rag_service.get_answer(q)
            clean_answer = full_response.split("\n\n📚")[0] 

            user_inputs.append(q)
            references.append(gt) 
            responses.append(clean_answer)
            retrieved_contexts.append(current_contexts)
            

        except Exception as e:
            print(f"Ошибка генерации: {e}")
            continue

    data = {
        "user_input": user_inputs,
        "response": responses,
        "retrieved_contexts": retrieved_contexts,
        "reference": references
    }
    dataset = Dataset.from_dict(data)

    print("\nНачинается проверка...")

    run_config = RunConfig(
        max_workers=1,     
        timeout=600,       
    )

    try:
        results = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,      
                answer_relevancy   
            ],
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            run_config=run_config,
            raise_exceptions=False          
        )

        print("\n📊 ИТОГОВЫЕ ОЦЕНКИ:")
        print(results)

    except Exception as e:
        print(f"\n❌ Ошибка во время оценки: {e}")

if __name__ == "__main__":
    asyncio.run(main())
