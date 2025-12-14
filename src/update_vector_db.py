import os
import json
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
import faiss

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

from src.config import cfg

STATE_FILE = os.path.join(cfg.DB_DIR, "processed_files.json")

def get_processed_files() -> List[str]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return []

def save_processed_files(files: List[str]):
    if not os.path.exists(cfg.DB_DIR):
        os.makedirs(cfg.DB_DIR)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=4)

def load_documents(source_dir: str, processed_files: List[str]) -> List[Document]:
    converter = DocumentConverter()
    chunker = HybridChunker(
        tokenizer="intfloat/multilingual-e5-base",
        max_tokens=500,
        merge_peers=True
        )

    documents = []

    debug_dir = os.path.join(os.getcwd(), "debug_chunks")
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    if not os.path.exists(source_dir):
        print(f"Directory {source_dir} does not exist")
        return []
    
    all_files = [f for f in os.listdir(source_dir)]
    new_files = [f for f in all_files if f not in processed_files]

    if not new_files:
        print("Nothing to update")
        return []
    
    for filename in new_files:
        file_path = os.path.join(source_dir, filename)

        try:
            result = converter.convert(file_path)

            docling_chunks = list(chunker.chunk(result.document))
            
            for chunk in docling_chunks:
                pages = sorted(set(
                    prov_item.page_no 
                    for item in chunk.meta.doc_items 
                    for prov_item in item.prov
                ))
                
                if len(pages) > 0:
                    page_str = f"{pages[0]}-{pages[-1]}" if len(pages) > 1 else str(pages[0])
                else:
                    page_str = "?"

                doc = Document(
                    page_content=chunk.text,
                    metadata={
                        "source": filename,
                        "page": page_str
                    }
                )
                documents.append(doc)

            print(f"Success: {filename}")
        
        except Exception as e:
            print(f"Error {filename}: {e}")

    return documents

def update_vector_db(chunks: List[Document]):
    embeddings = OllamaEmbeddings(model=cfg.EMBEDDING_MODEL, base_url=cfg.BASE_URL)

    vectore_store = None

    if os.path.exists(os.path.join(cfg.DB_DIR, f"{cfg.DB_NAME}.faiss")):
        vectore_store = FAISS.load_local(
            folder_path=cfg.DB_DIR,
            index_name=cfg.DB_NAME,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

    if vectore_store is None:
        sample_embedding = embeddings.embed_query("test")
        index = faiss.IndexFlatL2(len(sample_embedding))
        vectore_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )

    if chunks:
        vectore_store.add_documents(documents=chunks)

        vectore_store.save_local(folder_path=cfg.DB_DIR, index_name=cfg.DB_NAME)
        print("Database update")



def main():
    print("START PROCESS")
    print("="*30)

    processed_files = get_processed_files()

    chunks = load_documents(cfg.DATA_DIR, processed_files)
    
    if chunks:
        update_vector_db(chunks)

        new_filenames = list(set(doc.metadata["source"] for doc in chunks))

        processed_files.extend(new_filenames)
        save_processed_files(processed_files)
    else:
        print("Nothing to update")
    print("="*30)

if __name__ == "__main__":
    main()



