import chromadb
from datetime import datetime
import os

_chroma_client = None
_memory_collection = None

def get_memory_collection():
    global _chroma_client, _memory_collection
    if _memory_collection is None:
        db_path = os.getenv("CHROMA_PATH", "app/vector_db")
        _chroma_client = chromadb.PersistentClient(path=db_path)
        _memory_collection = _chroma_client.get_or_create_collection(name="agent_memory")
    return _memory_collection

def save_memory(memory_type: str, content: str, metadata: dict = None) -> str:
    collection = get_memory_collection()
    meta = {"type": memory_type, "timestamp": datetime.now().isoformat()}
    if metadata:
        meta.update(metadata)
    
    doc_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
    collection.add(
        documents=[content],
        metadatas=[meta],
        ids=[doc_id]
    )
    return doc_id

def search_memory(query: str, n_results: int = 3) -> dict:
    collection = get_memory_collection()
    if collection.count() == 0:
        return {"query": query, "results": []}

    res = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )
    
    formatted_results = []
    if res and "documents" in res and res["documents"]:
        docs = res["documents"][0]
        metas = res["metadatas"][0] if "metadatas" in res else [{}] * len(docs)
        for d, m in zip(docs, metas):
            formatted_results.append({
                "content": d,
                "type": m.get("type", "general"),
                "timestamp": m.get("timestamp", "")
            })

    return {
        "query": query,
        "count": len(formatted_results),
        "results": formatted_results
    }
