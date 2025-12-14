# 🌿 Eco RAG Assistant

**Eco RAG Assistant** is an intelligent Telegram bot designed to help students with Ecology questions. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to answer questions based on verified lecture materials, minimizing hallucinations.

Unlike simple RAG wrappers, this project focuses on **data quality** (using Docling for parsing) and **automated evaluation** (using Ragas framework).

## 🚀 Key Features

*   **🧠 Advanced RAG Pipeline:** Combines vector search (FAISS) with LLM generation.
*   **📄 SOTA Document Parsing:** Uses **Docling** & **HybridChunker** for high-quality text extraction from PDFs (handling headers, tables, and layout).
*   **📊 Automated Evaluation:** Integrated **Ragas** pipeline to measure *Faithfulness* and *Answer Relevancy*.
*   **📚 Source Citations:** The bot explicitly cites the source document and page number for every answer.
*   **🏠 Local LLM Support:** Fully compatible with **Ollama** (Gemma, Llama 3, Qwen) for privacy and offline usage.

## 🛠 Tech Stack

*   **Language:** Python 3.10+
*   **Orchestration:** LangChain
*   **LLM Serving:** Ollama
*   **Vector DB:** FAISS
*   **Parsing:** Docling (by DS4SD)
*   **Evaluation:** Ragas
*   **Bot Interface:** Aiogram 3

## ⚙️ Architecture

1.  **Ingestion:** PDFs are processed via `Docling`, split into semantic chunks using `HybridChunker`.
2.  **Embedding:** Chunks are embedded using `bge-m3` (via Ollama) and stored in `FAISS`.
3.  **Retrieval:** User query triggers a similarity search to find top-K relevant chunks.
4.  **Generation:** Context + Query are sent to the LLM (`gemma2` / `qwen2.5`) to generate a concise answer.
5.  **Response:** User receives the answer with references to specific lecture pages.

## 🏃‍♂️ How to Run

### Prerequisites
*   Python 3.10 or higher
*   [Ollama](https://ollama.com/) installed and running

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Ilya913/Eco-RAG-Assistant.git
    cd Eco-RAG-Assistant
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    ```

5.  **Run the Bot**
    Make sure Ollama is running (`ollama serve`).
    ```bash
    python src/bot.py
    ```

## 🧪 Evaluation (Ragas)

To ensure the quality of answers, I implemented a testing pipeline located in `tests/test.py`. It evaluates the RAG chain against a ground truth dataset.

Run evaluation:
```bash
python tests/test.py
```

*Metrics used: Faithfulness, Answer Relevancy.*

## 🗺 Roadmap & Future Improvements

- [ ] Dockerize the application (Docker Compose support).
- [ ] Add Hybrid Search (BM25 + Vector).
- [ ] Add Chat Memory (History).
- [ ] Deploy to cloud server.

## 📝 License

This project is open-source.