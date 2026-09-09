import os
from rag.rag_engine import RAGEngine

def extract_content():
    # Load index using existing RAGEngine
    engine = RAGEngine()
    engine.load_index()
    
    # Access the FAISS vector store directly
    vector_store = engine.vector_store
    docstore = vector_store.docstore
    
    print(f"Total documents in docstore: {len(docstore._dict)}")
    
    # Group by source
    files_content = {}
    for doc_id, doc in docstore._dict.items():
        source = doc.metadata.get("source")
        if not source or "rag" not in source:
            continue
            
        if source not in files_content:
            files_content[source] = []
        files_content[source].append(doc.page_content)
        
    # Write recovered files to a 'recovered_rag_emergency' directory
    os.makedirs("recovered_rag_emergency", exist_ok=True)
    
    for source, chunks in files_content.items():
        # Reconstruct file
        filename = os.path.basename(source)
        recovered_path = os.path.join("recovered_rag_emergency", filename)
        
        # Join chunks with a newline
        content = "\n\n".join(chunks)
        
        with open(recovered_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Extracted {filename}")

if __name__ == "__main__":
    extract_content()
