"""
벡터 DB 유틸리티 (RAG 시스템)
ChromaDB를 사용한 벡터 검색 구현
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import json

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("경고: ChromaDB가 설치되지 않았습니다. 'pip install chromadb' 실행하세요.")


class VectorDB:
    """벡터 DB 클래스 (ChromaDB 기반)"""
    
    def __init__(self, db_path: Optional[Path] = None, collection_name: str = "novel_context"):
        """
        Args:
            db_path: DB 저장 경로 (기본값: 프로젝트 루트/vector_db)
            collection_name: 컬렉션 이름
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB가 설치되지 않았습니다.")
        
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "vector_db"
        
        db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_document(self, text: str, metadata: Dict, doc_id: Optional[str] = None):
        """
        문서 추가
        
        Args:
            text: 문서 텍스트
            metadata: 메타데이터 (예: {"type": "character", "name": "주인공"})
            doc_id: 문서 ID (없으면 자동 생성)
        """
        if doc_id is None:
            import uuid
            doc_id = str(uuid.uuid4())
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id
    
    def search(self, query: str, n_results: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        유사 문서 검색
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 수
            filter_dict: 필터 조건 (예: {"type": "character"})
        
        Returns:
            검색 결과 리스트 [{"text": "...", "metadata": {...}, "distance": 0.5}]
        """
        where = filter_dict if filter_dict else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None,
                    "id": results['ids'][0][i]
                })
        
        return formatted_results
    
    def delete_document(self, doc_id: str):
        """문서 삭제"""
        self.collection.delete(ids=[doc_id])
    
    def get_all_documents(self) -> List[Dict]:
        """모든 문서 조회"""
        results = self.collection.get()
        documents = []
        for i in range(len(results['ids'])):
            documents.append({
                "id": results['ids'][i],
                "text": results['documents'][i],
                "metadata": results['metadatas'][i]
            })
        return documents


class NovelRAG:
    """소설 작성을 위한 RAG 시스템"""
    
    def __init__(self, novel_id: str):
        """
        Args:
            novel_id: 소설 ID
        """
        self.novel_id = novel_id
        self.vector_db = VectorDB(collection_name=f"novel_{novel_id}")
    
    def add_world_setting(self, setting: str):
        """세계관 설정 추가"""
        self.vector_db.add_document(
            text=setting,
            metadata={
                "type": "world_setting",
                "novel_id": self.novel_id
            }
        )
    
    def add_character(self, name: str, description: str):
        """캐릭터 정보 추가"""
        self.vector_db.add_document(
            text=f"{name}: {description}",
            metadata={
                "type": "character",
                "name": name,
                "novel_id": self.novel_id
            },
            doc_id=f"char_{self.novel_id}_{name}"
        )
    
    def add_plot_point(self, plot_point: str, chapter: int):
        """플롯 포인트 추가"""
        self.vector_db.add_document(
            text=plot_point,
            metadata={
                "type": "plot",
                "chapter": chapter,
                "novel_id": self.novel_id
            }
        )
    
    def add_foreshadowing(self, content: str, chapter: int):
        """복선 추가"""
        self.vector_db.add_document(
            text=content,
            metadata={
                "type": "foreshadowing",
                "chapter": chapter,
                "novel_id": self.novel_id,
                "resolved": False
            }
        )
    
    def get_relevant_context(self, query: str, context_types: Optional[List[str]] = None) -> str:
        """
        관련 컨텍스트 검색
        
        Args:
            query: 검색 쿼리
            context_types: 검색할 컨텍스트 타입 (예: ["character", "world_setting"])
        
        Returns:
            관련 컨텍스트 텍스트
        """
        if context_types:
            # 타입별로 검색
            all_results = []
            for context_type in context_types:
                results = self.vector_db.search(
                    query,
                    n_results=3,
                    filter_dict={"type": context_type, "novel_id": self.novel_id}
                )
                all_results.extend(results)
        else:
            # 전체 검색
            all_results = self.vector_db.search(
                query,
                n_results=5,
                filter_dict={"novel_id": self.novel_id}
            )
        
        # 거리순 정렬
        all_results.sort(key=lambda x: x.get("distance", 1.0))
        
        # 텍스트 조합
        context_parts = []
        for result in all_results[:5]:  # 상위 5개만
            context_parts.append(result["text"])
        
        return "\n\n".join(context_parts)
    
    def get_characters_context(self) -> str:
        """모든 캐릭터 정보 조회"""
        results = self.vector_db.search(
            "",
            n_results=100,
            filter_dict={"type": "character", "novel_id": self.novel_id}
        )
        return "\n".join([r["text"] for r in results])
    
    def get_unresolved_foreshadowing(self) -> List[Dict]:
        """미해결 복선 조회"""
        all_docs = self.vector_db.get_all_documents()
        unresolved = [
            {
                "text": doc["text"],
                "metadata": doc["metadata"]
            }
            for doc in all_docs
            if doc["metadata"].get("type") == "foreshadowing" 
            and doc["metadata"].get("novel_id") == self.novel_id
            and not doc["metadata"].get("resolved", False)
        ]
        return unresolved

