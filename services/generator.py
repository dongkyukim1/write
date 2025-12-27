"""
대본 생성 서비스
AI를 사용한 대본 생성 로직

핵심 원칙: 인간이 구조를 정하고, AI는 변주만 담당
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import get_provider, get_model_config, get_api_key
from models.database.crud import (
    get_project, get_episode, get_scene,
    create_scene, update_scene, get_characters_by_project
)
from models.schemas.scene import SceneCreate, SceneUpdate, SceneType, ConflictType, EmotionCurve, DialogDensity
from services.context_builder import ContextBuilder
from services.evaluator import SceneEvaluator


class ScriptGenerator:
    """
    대본 생성기
    
    컨텍스트 빌더와 연동하여 설정을 준수하면서 대본을 생성합니다.
    """
    
    def __init__(self, db: Session, provider_name: str = "openai"):
        """
        Args:
            db: 데이터베이스 세션
            provider_name: AI 프로바이더
        """
        self.db = db
        self.provider_name = provider_name
        
        api_key = get_api_key(provider_name)
        if not api_key:
            raise ValueError(f"{provider_name} API 키가 설정되지 않았습니다.")
        
        # 생성용은 creative 모델 사용
        config = get_model_config(provider_name, "creative")
        self.provider = get_provider(provider_name, api_key, config)
        
        self.context_builder = ContextBuilder(db)
    
    def generate_scene(self,
                      project_id: int,
                      episode_id: int,
                      scene_number: int,
                      scene_goal: str,
                      scene_type: SceneType = SceneType.DIALOGUE,
                      emotion_curve: Optional[List[EmotionCurve]] = None,
                      conflict_type: ConflictType = ConflictType.NONE,
                      dialog_density: DialogDensity = DialogDensity.MEDIUM,
                      character_ids: Optional[List[int]] = None,
                      additional_instructions: Optional[str] = None,
                      target_length: int = 1000) -> Dict[str, Any]:
        """
        장면을 생성합니다.
        
        인간이 정한 구조(목표, 감정 곡선, 갈등 유형)에 따라 AI가 변주합니다.
        
        Args:
            project_id: 프로젝트 ID
            episode_id: 에피소드 ID
            scene_number: 장면 번호
            scene_goal: 장면 목표 (필수)
            scene_type: 장면 타입
            emotion_curve: 감정 흐름
            conflict_type: 갈등 유형
            dialog_density: 대화 밀도
            character_ids: 참여 캐릭터 ID 목록
            additional_instructions: 추가 지시사항
            target_length: 목표 글자 수
        
        Returns:
            생성 결과 (content, evaluation 포함)
        """
        # 1. 컨텍스트 빌드
        context = self.context_builder.build_prompt_context(
            project_id=project_id,
            episode_id=episode_id,
            scene_goal=scene_goal,
            target_characters=character_ids
        )
        
        # 2. 프롬프트 구성
        prompt = self._build_generation_prompt(
            context=context,
            scene_goal=scene_goal,
            scene_type=scene_type,
            emotion_curve=emotion_curve,
            conflict_type=conflict_type,
            dialog_density=dialog_density,
            additional_instructions=additional_instructions,
            target_length=target_length
        )
        
        # 3. 생성
        content = self.provider.generate(
            prompt,
            temperature=0.8,
            max_tokens=min(target_length * 2, 4000)
        )
        
        # 4. 장면 저장
        scene_data = SceneCreate(
            episode_id=episode_id,
            scene_number=scene_number,
            scene_type=scene_type,
            title=scene_goal[:50] if len(scene_goal) > 50 else scene_goal,
            goal=scene_goal,
            emotion_curve=emotion_curve or [],
            conflict_type=conflict_type,
            dialog_density=dialog_density,
            character_ids=character_ids or [],
            content=content,
            writer_notes=additional_instructions
        )
        
        db_scene = create_scene(self.db, scene_data)
        
        # AI 생성 표시
        db_scene.ai_generated = True
        db_scene.generation_prompt = prompt[:2000]  # 프롬프트 일부 저장
        self.db.commit()
        
        # 5. 평가 (선택적)
        evaluation_result = None
        try:
            evaluator = SceneEvaluator(self.provider_name)
            evaluation = evaluator.evaluate(content)
            evaluation.scene_id = db_scene.id
            evaluation_result = {
                "overall_score": evaluation.overall_score,
                "creativity_score": evaluation.creativity_score,
                "cliche_detected": evaluation.cliche_detected,
                "summary": evaluation.summary,
                "suggestions": evaluation.suggestions
            }
        except Exception as e:
            print(f"평가 실패: {e}")
        
        return {
            "scene_id": db_scene.id,
            "scene_id_str": db_scene.scene_id,
            "content": content,
            "word_count": len(content),
            "evaluation": evaluation_result
        }
    
    def regenerate_scene(self,
                        scene_id: int,
                        modification_request: Optional[str] = None,
                        keep_structure: bool = True) -> Dict[str, Any]:
        """
        기존 장면을 재생성합니다.
        
        Args:
            scene_id: 재생성할 장면 ID
            modification_request: 수정 요청 (예: "더 긴장감 있게")
            keep_structure: 기존 구조(감정곡선 등) 유지 여부
        
        Returns:
            재생성 결과
        """
        scene = get_scene(self.db, scene_id)
        if not scene:
            raise ValueError(f"장면 ID {scene_id}를 찾을 수 없습니다.")
        
        episode = get_episode(self.db, scene.episode_id)
        project_id = episode.project_id
        
        # 컨텍스트 빌드
        context = self.context_builder.build_prompt_context(
            project_id=project_id,
            episode_id=scene.episode_id,
            scene_goal=scene.goal,
            target_characters=scene.character_ids
        )
        
        # 수정 프롬프트
        prompt = f"""{context}

## 기존 장면
```
{scene.content}
```

## 수정 요청
{modification_request or "더 창의적이고 독창적인 버전으로 다시 작성해주세요."}

## 유지해야 할 구조
- 장면 목표: {scene.goal}
- 감정 흐름: {scene.emotion_curve}
- 갈등 유형: {scene.conflict_type}
- 대화 밀도: {scene.dialog_density}

위 구조를 유지하면서 수정 요청을 반영한 새 버전을 작성해주세요.
기존 버전보다 더 나은 품질의 대본을 생성해주세요.
"""
        
        # 재생성
        new_content = self.provider.generate(
            prompt,
            temperature=0.85,
            max_tokens=4000
        )
        
        # 새 버전으로 저장 (버전 증가)
        scene_update = SceneUpdate(
            content=new_content,
            human_edited=False
        )
        
        updated_scene = update_scene(self.db, scene_id, scene_update)
        updated_scene.version += 1
        updated_scene.generation_prompt = prompt[:2000]
        self.db.commit()
        
        return {
            "scene_id": updated_scene.id,
            "version": updated_scene.version,
            "content": new_content,
            "word_count": len(new_content)
        }
    
    def _build_generation_prompt(self,
                                context: str,
                                scene_goal: str,
                                scene_type: SceneType,
                                emotion_curve: Optional[List[EmotionCurve]],
                                conflict_type: ConflictType,
                                dialog_density: DialogDensity,
                                additional_instructions: Optional[str],
                                target_length: int) -> str:
        """생성 프롬프트 구성"""
        
        emotion_str = ""
        if emotion_curve:
            emotion_str = " → ".join([e.value for e in emotion_curve])
        
        density_guide = {
            DialogDensity.HIGH: "대화 위주로 진행, 지문은 최소화",
            DialogDensity.MEDIUM: "대화와 지문이 적절히 섞임",
            DialogDensity.LOW: "나레이션/묘사 위주, 대화는 최소화"
        }
        
        conflict_guide = {
            ConflictType.RELATIONSHIP: "인물 간의 관계에서 오는 갈등을 표현",
            ConflictType.INTERNAL: "캐릭터의 내면 갈등을 표현",
            ConflictType.EXTERNAL: "외부 상황/환경에서 오는 갈등을 표현",
            ConflictType.IDEOLOGICAL: "가치관/이념 충돌을 표현",
            ConflictType.COMEDIC: "코믹한 갈등/상황을 표현",
            ConflictType.NONE: "갈등 없이 진행"
        }
        
        prompt = f"""당신은 전문 방송작가입니다. 다음 컨텍스트와 지시에 따라 대본을 작성해주세요.

{context}

## 장면 작성 지침

### 장면 목표
{scene_goal}

### 장면 타입
{scene_type.value}

### 감정 흐름
{emotion_str or "자유롭게 구성"}

### 갈등 유형
{conflict_guide.get(conflict_type, "자유롭게 구성")}

### 대화 밀도
{density_guide.get(dialog_density, "적절히 조절")}

### 목표 분량
약 {target_length}자

### 추가 지시
{additional_instructions or "없음"}

## 작성 규칙
1. 위에 제시된 캐릭터의 말투와 성격을 정확히 반영하세요
2. 금지된 요소는 절대 사용하지 마세요
3. 세계관 규칙을 준수하세요
4. 클리셰를 피하고 창의적인 표현을 사용하세요
5. 감정 흐름을 자연스럽게 전개하세요

대본을 작성해주세요:
"""
        
        return prompt
    
    def generate_variations(self,
                           scene_id: int,
                           count: int = 3) -> List[Dict[str, Any]]:
        """
        한 장면의 여러 변형을 생성합니다.
        
        작가가 선택할 수 있도록 다양한 버전을 제시합니다.
        
        Args:
            scene_id: 원본 장면 ID
            count: 생성할 변형 수
        
        Returns:
            변형 목록
        """
        scene = get_scene(self.db, scene_id)
        if not scene:
            raise ValueError(f"장면 ID {scene_id}를 찾을 수 없습니다.")
        
        episode = get_episode(self.db, scene.episode_id)
        project_id = episode.project_id
        
        context = self.context_builder.build_prompt_context(
            project_id=project_id,
            episode_id=scene.episode_id,
            scene_goal=scene.goal,
            target_characters=scene.character_ids
        )
        
        variations = []
        
        variation_prompts = [
            "더 유머러스하고 가벼운 톤으로",
            "더 진지하고 긴장감 있게",
            "더 감정적이고 드라마틱하게"
        ][:count]
        
        for i, style in enumerate(variation_prompts):
            prompt = f"""{context}

## 원본 장면
{scene.content[:1500]}

## 변형 스타일
{style}

## 유지할 요소
- 장면 목표: {scene.goal}
- 참여 캐릭터: 동일
- 핵심 내용: 동일

위 스타일로 변형된 버전을 작성해주세요.
원본의 핵심은 유지하되, 톤과 표현 방식을 변경하세요.
"""
            
            variation_content = self.provider.generate(
                prompt,
                temperature=0.9,
                max_tokens=3000
            )
            
            variations.append({
                "variation_number": i + 1,
                "style": style,
                "content": variation_content,
                "word_count": len(variation_content)
            })
        
        return variations

