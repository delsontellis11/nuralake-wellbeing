import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "../chroma_db")

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )
    return _vectorstore

def search_knowledge_base(query: str, k: int = 3) -> str:
    vs = get_vectorstore()
    docs = vs.similarity_search(query, k=k)
    if not docs:
        return "No relevant information found in the knowledge base."
    results = []
    for i, doc in enumerate(docs, 1):
        results.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(results)