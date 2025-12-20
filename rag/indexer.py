# FILE: rag/indexer.py
"""
Handbook indexer for KEITH Manufacturing.
Handles one-time indexing of the pre-loaded handbook PDF.
"""

import os
from typing import Optional

from .pdf import extract_pdf_chunks, HANDBOOK_TEXT
from .embeddings import get_embeddings
from .pinecone_store import (
    init_pinecone,
    create_index_if_not_exists,
    upsert_chunks,
    get_namespace_count
)


def check_index_exists(
    api_key: str,
    index_name: str,
    namespace: str,
    min_vectors: int = 10
) -> bool:
    """
    Check if the handbook has already been indexed.
    
    Args:
        api_key: Pinecone API key
        index_name: Pinecone index name
        namespace: Namespace to check
        min_vectors: Minimum vector count to consider "indexed"
        
    Returns:
        True if index exists and has vectors
    """
    try:
        init_pinecone(api_key)
        create_index_if_not_exists(index_name)
        count = get_namespace_count(index_name, namespace)
        return count >= min_vectors
    except Exception:
        return False


def index_handbook(
    openai_api_key: str,
    pinecone_api_key: str,
    index_name: str,
    namespace: str
) -> int:
    """
    Index the KEITH handbook into Pinecone.
    Uses the embedded handbook text to avoid needing the PDF file.
    
    Args:
        openai_api_key: OpenAI API key
        pinecone_api_key: Pinecone API key
        index_name: Pinecone index name
        namespace: Namespace to store vectors
        
    Returns:
        Number of chunks indexed
    """
    # Initialize Pinecone
    init_pinecone(pinecone_api_key)
    create_index_if_not_exists(index_name)
    
    # Extract chunks from embedded handbook text
    chunks = extract_pdf_chunks()
    
    if not chunks:
        raise ValueError("No chunks extracted from handbook")
    
    # Generate embeddings
    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(texts, openai_api_key)
    
    # Upsert to Pinecone
    upsert_chunks(
        index_name=index_name,
        chunks=chunks,
        embeddings=embeddings,
        namespace=namespace
    )
    
    return len(chunks)
