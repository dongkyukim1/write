"""
RAG (Retrieval-Augmented Generation) 유틸리티
벡터 DB를 활용한 컨텍스트 검색 시스템
"""

from .vector_db import VectorDB, NovelRAG

__all__ = ["VectorDB", "NovelRAG"]

