from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

VECTOR_STORE_PATH = "c:/AI_Trading_Agent/data/vector_store"

def check_vector_store():
    # Use the same model as in rag_engine.py
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    print("[INFO] Loading FAISS index...")
    vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    
    # In LangChain FAISS, the documents are in the docstore
    # We can get the index size by looking at the index's ntotal
    # Or by counting the keys in the docstore
    
    # docstore is a dictionary mapping id to document
    num_chunks = len(vector_store.docstore._dict)
    
    print(f"[INFO] Total chunk count: {num_chunks}")

if __name__ == "__main__":
    check_vector_store()
