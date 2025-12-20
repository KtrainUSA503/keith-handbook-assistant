# FILE: rag/embeddings.py
"""
OpenAI embeddings client for KEITH Handbook Assistant.
Uses text-embedding-3-small model with 1536 dimensions.
"""

from openai import OpenAI
import time

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
MAX_BATCH_SIZE = 100


def get_embeddings(
    texts: list[str],
    api_key: str,
    model: str = EMBEDDING_MODEL,
    batch_size: int = MAX_BATCH_SIZE,
    retry_attempts: int = 3
) -> list[list[float]]:
    """Generate embeddings for a list of texts using OpenAI API."""
    client = OpenAI(api_key=api_key)
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        for attempt in range(retry_attempts):
            try:
                response = client.embeddings.create(
                    model=model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                break
            except Exception as e:
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise RuntimeError(f"Failed to generate embeddings: {e}")
    
    return all_embeddings


def get_single_embedding(text: str, api_key: str, model: str = EMBEDDING_MODEL) -> list[float]:
    """Generate embedding for a single text."""
    embeddings = get_embeddings([text], api_key, model)
    return embeddings[0]
