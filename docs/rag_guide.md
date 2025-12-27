# RAG 시스템 사용 가이드

RAG (Retrieval-Augmented Generation)를 활용하여 장편 소설 작성 시 컨텍스트를 효과적으로 관리합니다.

## RAG란?

RAG는 벡터 데이터베이스를 사용하여 관련 정보를 검색하고, 이를 프롬프트에 포함시켜 더 정확하고 일관된 텍스트를 생성하는 시스템입니다.

## 설치

```bash
pip install chromadb
```

## 기본 사용법

### 1. RAG 시스템 초기화

```python
from utils.rag import NovelRAG

# 소설별 RAG 시스템 생성
rag = NovelRAG("my_novel_001")
```

### 2. 세계관 설정 추가

```python
rag.add_world_setting("""
이 세계는 마법과 기술이 공존하는 판타지 세계입니다.
마법사들은 기술을 경멸하고, 기술자들은 마법을 두려워합니다.
"""
)
```

### 3. 캐릭터 정보 추가

```python
rag.add_character("주인공", """
이름: 김철수
나이: 25세
성격: 용감하고 정의로운 성격
능력: 마법과 기술을 모두 사용할 수 있는 희귀한 재능
""")
```

### 4. 관련 컨텍스트 검색

```python
# 챕터 생성 시 관련 정보 검색
context = rag.get_relevant_context(
    "주인공이 마법을 사용하는 장면",
    context_types=["character", "world_setting"]
)

# 검색된 컨텍스트를 프롬프트에 포함
prompt = f"""
{context}

위 정보를 바탕으로 챕터를 작성해주세요.
"""
```

## 장편 소설 생성기와 통합

`long_form_novel_generator.py`를 수정하여 RAG 시스템을 통합할 수 있습니다:

```python
from utils.rag import NovelRAG

class LongFormNovelGenerator:
    def __init__(self, novel_id: str, ...):
        # ... 기존 코드 ...
        self.rag = NovelRAG(novel_id)
    
    def initialize_novel(self, ...):
        # ... 기존 초기화 ...
        
        # RAG에 초기 정보 추가
        self.rag.add_world_setting(world_setting)
        for char in characters:
            self.rag.add_character(char["name"], char["description"])
    
    def generate_chapter(self, ...):
        # 관련 컨텍스트 검색
        relevant_context = self.rag.get_relevant_context(
            chapter_goal,
            context_types=["character", "world_setting", "plot"]
        )
        
        # 프롬프트에 컨텍스트 포함
        prompt = f"""
        {relevant_context}
        
        {기존 프롬프트}
        """
        # ... 생성 ...
```

## 고급 사용법

### 복선 관리

```python
# 복선 추가
rag.add_foreshadowing("주인공의 과거에 숨겨진 비밀이 있다", chapter=5)

# 미해결 복선 조회
unresolved = rag.get_unresolved_foreshadowing()
for f in unresolved:
    print(f"챕터 {f['metadata']['chapter']}: {f['text']}")
```

### 플롯 포인트 추가

```python
rag.add_plot_point("주인공이 최종 보스와 대면한다", chapter=20)
```

### 모든 캐릭터 정보 조회

```python
characters_context = rag.get_characters_context()
# 모든 캐릭터 정보를 한 번에 가져옴
```

## 효과

### Before (RAG 없이)
- 초반 설정을 프롬프트에 모두 포함 → 토큰 낭비
- 관련 정보를 찾기 어려움
- 일관성 유지 어려움

### After (RAG 사용)
- 필요한 정보만 검색하여 포함 → 효율적
- 관련 정보를 정확히 찾아냄
- 일관성 유지 용이

## 주의사항

⚠️ **ChromaDB 설치 필요**
- `pip install chromadb` 실행 필요
- 설치하지 않으면 RAG 기능 사용 불가

⚠️ **초기 설정 중요**
- 세계관과 캐릭터 정보를 상세히 입력할수록 효과적
- 정보가 부족하면 검색 품질 저하

⚠️ **벡터 DB 크기**
- 소설이 길어질수록 DB 크기 증가
- 필요시 오래된 정보는 정리 고려

## 트러블슈팅

**Q: 검색 결과가 부정확해요**
A: 검색 쿼리를 더 구체적으로 작성하거나, context_types를 지정해보세요.

**Q: DB가 너무 커져요**
A: 오래된 정보는 삭제하거나, 소설별로 별도 컬렉션을 사용하세요.

**Q: 설치 오류가 발생해요**
A: Python 버전을 확인하세요 (3.8 이상 필요). 또는 다른 벡터 DB(FAISS, Qdrant)를 사용할 수도 있습니다.

