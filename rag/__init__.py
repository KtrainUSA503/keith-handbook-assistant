# FILE: rag/__init__.py
"""
RAG package for KEITH Manufacturing Handbook AI Assistant.
"""

from .pdf import extract_pdf_chunks, HANDBOOK_PAGES
from .embeddings import get_embeddings, get_single_embedding
from .pinecone_store import (
    init_pinecone,
    create_index_if_not_exists,
    upsert_chunks,
    query_similar,
    clear_namespace,
    get_namespace_count
)
from .indexer import check_index_exists, index_handbook
from .agent import AgenticRAG

__all__ = [
    "extract_pdf_chunks",
    "HANDBOOK_PAGES",
    "get_embeddings",
    "get_single_embedding",
    "init_pinecone",
    "create_index_if_not_exists",
    "upsert_chunks",
    "query_similar",
    "clear_namespace",
    "get_namespace_count",
    "check_index_exists",
    "index_handbook",
    "AgenticRAG"
]
