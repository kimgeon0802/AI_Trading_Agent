import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Define Knowledge Directory
KNOWLEDGE_DIR = "rag"
VECTOR_STORE_PATH = "data/vector_store"

class RAGEngine:
    def __init__(self):
        # Using a model suitable for Korean/Multilingual
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None

    def build_index(self):
        print("[INFO] Loading documents...")
        # Load all markdown files from rag/ directory
        loader = DirectoryLoader(KNOWLEDGE_DIR, glob="**/*.md", loader_cls=lambda p: TextLoader(p, encoding='utf-8'), show_progress=True)
        docs = loader.load()
        
        # Split by markdown headers
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        
        print("[INFO] Chunking documents...")
        all_chunks = []
        for doc in docs:
            chunks = text_splitter.split_text(doc.page_content)
            # Add metadata
            for chunk in chunks:
                chunk.metadata["source"] = doc.metadata["source"]
                # category from directory name
                chunk.metadata["category"] = os.path.basename(os.path.dirname(doc.metadata["source"]))
            all_chunks.extend(chunks)
        
        print(f"[INFO] Total chunks created: {len(all_chunks)}")
        
        print("[INFO] Building FAISS index...")
        self.vector_store = FAISS.from_documents(all_chunks, self.embeddings)
        
        # Save index
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        self.vector_store.save_local(VECTOR_STORE_PATH)
        print("[INFO] Index saved to", VECTOR_STORE_PATH)

    def load_index(self):
        print("[INFO] Loading FAISS index...")
        self.vector_store = FAISS.load_local(VECTOR_STORE_PATH, self.embeddings, allow_dangerous_deserialization=True)
        print("[INFO] Index loaded.")

    def retrieve(self, query, top_k=3):
        if not self.vector_store:
            raise RuntimeError("Index not loaded.")
        return self.vector_store.similarity_search(query, k=top_k)

if __name__ == "__main__":
    engine = RAGEngine()
    engine.build_index()
    engine.load_index()
    
    # Test Retrieval
    test_query = "volatility and trading risk"
    results = engine.retrieve(test_query)
    print(f"\n[INFO] Test Query: {test_query}")
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Content: {res.page_content[:100]}...")
        print(f"Metadata: {res.metadata}")
