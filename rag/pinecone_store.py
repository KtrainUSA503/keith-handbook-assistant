# FILE: rag/pinecone_store.py
"""
Pinecone vector database operations for KEITH Handbook Assistant.
"""

from pinecone import Pinecone, ServerlessSpec
from typing import Optional, Any
import time

_pc: Optional[Pinecone] = None

EMBEDDING_DIMENSION = 1536
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"


def init_pinecone(api_key: str) -> Pinecone:
    """Initialize Pinecone client."""
    global _pc
    _pc = Pinecone(api_key=api_key)
    return _pc


def get_client() -> Pinecone:
    """Get the initialized Pinecone client."""
    if _pc is None:
        raise RuntimeError("Pinecone not initialized. Call init_pinecone() first.")
    return _pc


def create_index_if_not_exists(
    index_name: str,
    dimension: int = EMBEDDING_DIMENSION,
    metric: str = "cosine"
) -> bool:
    """Create a Pinecone serverless index if it doesn't exist."""
    pc = get_client()
    
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if index_name in existing_indexes:
        return False
    
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
    )
    
    # Wait for index to be ready
    max_wait = 60
    waited = 0
    while waited < max_wait:
        index_info = pc.describe_index(index_name)
        if index_info.status.ready:
            break
        time.sleep(2)
        waited += 2
    
    return True


def get_namespace_count(index_name: str, namespace: str) -> int:
    """Get the number of vectors in a namespace."""
    pc = get_client()
    index = pc.Index(index_name)
    
    stats = index.describe_index_stats()
    namespaces = stats.namespaces or {}
    
    if namespace in namespaces:
        return namespaces[namespace].vector_count
    return 0


def upsert_chunks(
    index_name: str,
    chunks: list[dict],
    embeddings: list[list[float]],
    namespace: str,
    batch_size: int = 100
) -> int:
    """Upsert chunk vectors with metadata to Pinecone."""
    pc = get_client()
    index = pc.Index(index_name)
    
    vectors = []
    for chunk, embedding in zip(chunks, embeddings):
        vectors.append({
            "id": chunk["chunk_id"],
            "values": embedding,
            "metadata": {
                "text": chunk["text"][:3000],
                "page_number": chunk["page_number"],
                "section_title": chunk["section_title"]
            }
        })
    
    total_upserted = 0
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)
        total_upserted += len(batch)
    
    return total_upserted


def query_similar(
    index_name: str,
    query_vector: list[float],
    namespace: str,
    top_k: int = 5,
    include_metadata: bool = True
) -> list[dict]:
    """Query for similar vectors in Pinecone."""
    pc = get_client()
    index = pc.Index(index_name)
    
    results = index.query(
        vector=query_vector,
        namespace=namespace,
        top_k=top_k,
        include_metadata=include_metadata
    )
    
    formatted = []
    for match in results.matches:
        result = {
            "chunk_id": match.id,
            "score": match.score,
        }
        if include_metadata and match.metadata:
            result["text"] = match.metadata.get("text", "")
            result["page_number"] = match.metadata.get("page_number", 0)
            result["section_title"] = match.metadata.get("section_title", "")
        formatted.append(result)
    
    return formatted


def clear_namespace(index_name: str, namespace: str) -> bool:
    """Clear all vectors in a namespace."""
    pc = get_client()
    index = pc.Index(index_name)
    index.delete(delete_all=True, namespace=namespace)
    return True
