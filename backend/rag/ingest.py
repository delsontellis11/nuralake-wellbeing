import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "../../knowledge_base")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "../chroma_db")

def build_vectorstore():
    print("Loading documents...")
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_DIR,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()
    print(f"Loaded {len(docs)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks")

    print("Creating embeddings (this takes 1-2 mins first time)...")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print(f"Vector store saved to {CHROMA_DIR}")
    return vectorstore

if __name__ == "__main__":
    build_vectorstore()
    print("Done! RAG pipeline ready.")