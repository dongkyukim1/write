"""
AI 대본 생성 API 라우터
OpenAI API + 기존 대본/평가를 참조하여 진화하는 대본 생성
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models.database import get_db
from models.database.crud import (
    get_project, get_episode, get_characters_by_project,
    get_scene, get_scenes_by_episode, get_evaluation_by_scene
)
from models.database.models import SceneModel, EvaluationModel, EpisodeModel

router = APIRouter()


class GenerateRequest(BaseModel):
    """대본 생성 요청"""
    scene_id: int
    goal: str
    scene_type: str = "dialogue"
    conflict_type: str = "none"
    character_ids: List[int] = []
    additional_context: Optional[str] = None


class GenerateResponse(BaseModel):
    """대본 생성 응답"""
    scene_id: int
    content: str
    word_count: int
    success: bool
    context_used: dict  # 어떤 컨텍스트가 사용되었는지


def get_openai_client():
    """OpenAI 클라이언트 생성"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except ImportError:
        return None


def build_learning_context(db: Session, project_id: int, current_scene_id: int = None):
    """
    프로젝트의 기존 대본과 평가를 분석하여 학습 컨텍스트 구축
    
    Returns:
        dict: 학습된 컨텍스트 정보
    """
    context = {
        "best_scenes": [],       # 높은 점수 받은 장면들
        "style_patterns": [],    # 스타일 패턴
        "strengths_to_keep": [], # 유지해야 할 강점
        "issues_to_avoid": [],   # 피해야 할 문제점
        "character_examples": {},# 캐릭터별 대사 예시
        "scene_count": 0,
        "avg_score": 0
    }
    
    # 프로젝트의 모든 에피소드 가져오기
    episodes = db.query(EpisodeModel).filter(
        EpisodeModel.project_id == project_id
    ).all()
    
    all_scenes = []
    all_evaluations = []
    
    for ep in episodes:
        scenes = get_scenes_by_episode(db, ep.id)
        for scene in scenes:
            if current_scene_id and scene.id == current_scene_id:
                continue  # 현재 생성 중인 장면 제외
            
            if scene.content and len(scene.content) > 50:  # 유효한 대본만
                all_scenes.append(scene)
                
                # 평가 가져오기
                evaluation = get_evaluation_by_scene(db, scene.id)
                if evaluation:
                    all_evaluations.append({
                        "scene": scene,
                        "evaluation": evaluation
                    })
    
    context["scene_count"] = len(all_scenes)
    
    if not all_evaluations:
        return context
    
    # 평균 점수 계산
    scores = [e["evaluation"].overall_score for e in all_evaluations]
    context["avg_score"] = sum(scores) / len(scores) if scores else 0
    
    # 상위 3개 장면 선택 (가장 높은 점수)
    sorted_evals = sorted(all_evaluations, key=lambda x: x["evaluation"].overall_score, reverse=True)
    top_scenes = sorted_evals[:3]
    
    for item in top_scenes:
        scene = item["scene"]
        eval = item["evaluation"]
        
        # 대본 일부 추출 (너무 길면 앞부분만)
        content_preview = scene.content[:500] if len(scene.content) > 500 else scene.content
        
        context["best_scenes"].append({
            "scene_type": scene.scene_type,
            "score": eval.overall_score,
            "content_preview": content_preview
        })
        
        # 강점 수집
        if eval.strengths:
            context["strengths_to_keep"].extend(eval.strengths)
    
    # 모든 평가에서 피해야 할 점 수집
    for item in all_evaluations:
        eval = item["evaluation"]
        if eval.suggestions:
            context["issues_to_avoid"].extend(eval.suggestions[:2])  # 상위 2개만
        if eval.cliche_detected and eval.cliches:
            for cliche in eval.cliches[:2]:
                if isinstance(cliche, dict):
                    context["issues_to_avoid"].append(f"클리셰 피하기: {cliche.get('description', '')}")
    
    # 중복 제거
    context["strengths_to_keep"] = list(set(context["strengths_to_keep"]))[:5]
    context["issues_to_avoid"] = list(set(context["issues_to_avoid"]))[:5]
    
    # 캐릭터별 대사 예시 추출
    for scene in all_scenes[:5]:  # 최근 5개 장면에서
        if scene.content:
            lines = scene.content.split('\n')
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    char_name = parts[0].strip()
                    dialogue = parts[1].strip() if len(parts) > 1 else ""
                    
                    if char_name and dialogue and len(dialogue) > 10:
                        if char_name not in context["character_examples"]:
                            context["character_examples"][char_name] = []
                        if len(context["character_examples"][char_name]) < 2:
                            context["character_examples"][char_name].append(dialogue[:100])
    
    return context


@router.post("/scene", response_model=GenerateResponse, summary="AI 대본 생성")
async def generate_scene_content(
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    """
    AI를 사용하여 장면의 대본을 생성합니다.
    기존 대본과 평가를 학습하여 일관된 스타일과 개선된 품질로 생성합니다.
    """
    # 장면 조회
    scene = get_scene(db, request.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="장면을 찾을 수 없습니다.")
    
    # 에피소드 & 프로젝트 정보
    episode = get_episode(db, scene.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="에피소드를 찾을 수 없습니다.")
    
    project = get_project(db, episode.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 캐릭터 정보
    all_characters = get_characters_by_project(db, project.id)
    selected_characters = [c for c in all_characters if c.id in request.character_ids]
    
    # 🔥 핵심: 기존 대본/평가에서 학습 컨텍스트 구축
    learning_context = build_learning_context(db, project.id, scene.id)
    
    # OpenAI 클라이언트 확인
    client = get_openai_client()
    
    if client:
        # OpenAI로 실제 생성 (학습 컨텍스트 포함)
        content = await generate_with_openai(
            client=client,
            project=project,
            episode=episode,
            scene=scene,
            characters=selected_characters,
            goal=request.goal,
            scene_type=request.scene_type,
            conflict_type=request.conflict_type,
            learning_context=learning_context
        )
    else:
        # OpenAI 없으면 샘플 대본 생성
        content = generate_sample_script(
            project=project,
            characters=selected_characters,
            goal=request.goal,
            scene_type=request.scene_type,
            learning_context=learning_context
        )
    
    # DB 업데이트
    scene.content = content
    scene.word_count = len(content)
    scene.ai_generated = True
    scene.goal = request.goal
    # title이 없으면 goal의 첫 줄을 title로 설정
    if not scene.title or scene.title == "":
        scene.title = request.goal.split('\n')[0][:50] if request.goal else f"장면 {scene.scene_number}"
    db.commit()
    
    # 🔥 자동 평가 생성
    evaluation_result = await auto_evaluate_scene(
        db=db,
        client=client,
        scene=scene,
        content=content,
        learning_context=learning_context
    )
    
    return GenerateResponse(
        scene_id=scene.id,
        content=content,
        word_count=len(content),
        success=True,
        context_used={
            "scenes_referenced": learning_context["scene_count"],
            "avg_score": round(learning_context["avg_score"], 2),
            "strengths_applied": len(learning_context["strengths_to_keep"]),
            "issues_avoided": len(learning_context["issues_to_avoid"]),
            "auto_evaluation": evaluation_result
        }
    )


async def generate_with_openai(client, project, episode, scene, characters, goal, scene_type, conflict_type, learning_context):
    """OpenAI API로 대본 생성 (학습 컨텍스트 반영)"""
    
    # 캐릭터 정보 포맷
    char_info_parts = []
    for c in characters:
        char_text = f"- {c.name} ({c.role}): {c.personality_description or ''}"
        if c.speech_pattern:
            char_text += f"\n  말투: {c.speech_pattern}"
        
        # 기존 대사 예시 추가
        if c.name in learning_context.get("character_examples", {}):
            examples = learning_context["character_examples"][c.name]
            char_text += f"\n  실제 대사 예시: " + " / ".join(examples)
        elif c.speech_examples:
            char_text += f"\n  대사 예시: " + " / ".join(c.speech_examples[:2])
        
        char_info_parts.append(char_text)
    
    char_info = "\n".join(char_info_parts) if char_info_parts else "캐릭터 정보 없음"
    
    # 장면 타입 설명
    type_desc = {
        "opening": "오프닝 - 시청자의 관심을 끌고 주제를 소개",
        "dialogue": "대화 장면 - 캐릭터 간 자연스러운 대화",
        "talk": "본격 토크 - 주제에 대한 심층 토론",
        "highlight": "하이라이트 - 핵심 포인트, 임팩트 있는 장면",
        "closing": "마무리 - 정리와 다음 회 예고"
    }.get(scene_type, "대화 장면")
    
    # 갈등 유형 설명
    conflict_desc = {
        "none": "갈등 없음 - 편안한 분위기",
        "relationship": "관계 갈등 - 인물 간 긴장",
        "internal": "내면 갈등 - 고민, 딜레마",
        "ideological": "가치관 갈등 - 의견 대립",
        "comedic": "코믹 갈등 - 유머러스한 대립"
    }.get(conflict_type, "")
    
    # 🔥 학습 컨텍스트 프롬프트 구성
    learning_prompt = ""
    
    if learning_context["scene_count"] > 0:
        learning_prompt = f"""
## 🎯 이 프로젝트의 학습된 스타일 (기존 {learning_context['scene_count']}개 장면 분석)

### 유지해야 할 강점 (이전 대본에서 높은 평가를 받은 요소):
{chr(10).join(['- ' + s for s in learning_context['strengths_to_keep']]) if learning_context['strengths_to_keep'] else '- 자연스러운 대화 흐름'}

### 피해야 할 점 (이전 피드백에서 지적된 문제):
{chr(10).join(['- ' + s for s in learning_context['issues_to_avoid']]) if learning_context['issues_to_avoid'] else '- 진부한 표현'}

### 참고할 좋은 대본 예시 (점수 {learning_context['avg_score']:.0%} 이상):
"""
        for i, best in enumerate(learning_context["best_scenes"][:2], 1):
            learning_prompt += f"""
예시 {i} ({best['scene_type']}, 점수: {best['score']:.0%}):
```
{best['content_preview'][:300]}...
```
"""

    prompt = f"""당신은 전문 대본 작가입니다. 기존 대본의 스타일과 피드백을 학습하여 더 나은 대본을 작성합니다.

## 프로젝트 정보
- 제목: {project.title}
- 타입: {project.project_type}
- 세계관: {project.world_setting or '없음'}
- 스타일 가이드: {project.style_guide or '없음'}

## 에피소드 정보
- EP{episode.episode_number}: {episode.title}
- 메인 토픽: {episode.main_topic or '없음'}

## 장면 정보
- 장면 번호: {scene.scene_number}
- 장면 타입: {type_desc}
- 갈등 유형: {conflict_desc}

## 참여 캐릭터
{char_info}

## 장면 목표
{goal}
{learning_prompt}

## 작성 지침
1. 위에서 분석된 강점을 유지하고, 지적된 문제점은 피해주세요
2. 캐릭터의 말투와 성격을 일관되게 유지해주세요
3. 이 프로젝트만의 톤과 분위기를 유지해주세요
4. 대사는 "캐릭터명: 대사" 형식으로 작성해주세요
5. 지문은 (괄호) 안에 작성해주세요
6. 한국어로 작성해주세요
7. 기존 대본보다 더 나은 품질로 작성해주세요

대본을 작성해주세요:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 전문 대본 작가입니다. 기존 대본의 스타일을 학습하고, 피드백을 반영하여 점점 더 좋은 대본을 작성합니다. 일관된 톤과 캐릭터 특성을 유지하면서도 더 창의적이고 재미있는 대본을 만듭니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.75
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI 에러: {e}")
        return generate_sample_script(project, characters, goal, scene_type, learning_context)


def generate_sample_script(project, characters, goal, scene_type, learning_context=None):
    """OpenAI 없을 때 샘플 대본 생성 (학습 컨텍스트 반영)"""
    
    char_names = [c.name for c in characters] if characters else ["진행자A", "진행자B"]
    
    if len(char_names) < 2:
        char_names = char_names + ["진행자"]
    
    # 학습된 강점 반영
    style_note = ""
    if learning_context and learning_context.get("strengths_to_keep"):
        style_note = f"(스타일 참고: {', '.join(learning_context['strengths_to_keep'][:2])})"
    
    scripts = {
        "opening": f"""{char_names[0]}: (카메라를 보며 에너지 넘치게) 안녕하세요! 오늘도 찾아왔습니다.

{char_names[1]}: 네, 오늘은 정말 흥미로운 주제가 있어요.

{char_names[0]}: 맞아요. {goal}

{char_names[1]}: (시청자를 향해) 오늘 방송 끝나면 이 주제, 완벽하게 이해하실 수 있을 거예요.

{char_names[0]}: 자, 그럼 바로 시작해볼까요?

{char_names[1]}: 네, 들어갑니다!

{style_note}""",

        "dialogue": f"""{char_names[0]}: 이 부분이 핵심인 것 같아요.

{char_names[1]}: 맞아요. {goal}

{char_names[0]}: 그런데 여기서 중요한 포인트가 있어요.

{char_names[1]}: (끄덕이며) 그 부분이 정말 중요하죠.

{char_names[0]}: 좀 더 자세히 풀어볼게요.

{char_names[1]}: (자료를 보며) 여기 보시면...

{char_names[0]}: 아, 이게 바로 그거네요!

{style_note}""",

        "talk": f"""{char_names[0]}: 자, 본격적으로 들어가 보겠습니다.

{char_names[1]}: {goal}

{char_names[0]}: 이게 왜 중요하냐면요...

{char_names[1]}: 맥락을 보면 이해가 됩니다.

{char_names[0]}: (자료를 보며) 여기 보시면 명확해요.

{char_names[1]}: 아, 그렇군요. 이게 핵심 포인트네요.

{char_names[0]}: 시청자분들도 이제 이해되셨죠?

{style_note}""",

        "highlight": f"""{char_names[0]}: (강조하며) 여기가 오늘의 핵심입니다!

{char_names[1]}: {goal}

{char_names[0]}: 이건 꼭 기억하셔야 해요.

{char_names[1]}: (끼어들며) 정말 중요한 부분이에요.

{char_names[0]}: 다시 한번 정리하면...

{char_names[1]}: 바로 이거예요!

{char_names[0]}: 시청자 여러분, 이거 놓치시면 안 됩니다!

{style_note}""",

        "closing": f"""{char_names[0]}: 자, 오늘 내용을 정리해 보면요.

{char_names[1]}: 첫째, {goal}

{char_names[0]}: 이게 오늘의 핵심이었습니다.

{char_names[1]}: 다음 주에는 더 재미있는 주제로 찾아뵙겠습니다.

{char_names[0]}: 시청해 주셔서 감사합니다!

(함께) 다음에 또 만나요!

{style_note}"""
    }
    
    return scripts.get(scene_type, scripts["dialogue"])


async def auto_evaluate_scene(db: Session, client, scene, content: str, learning_context: dict) -> dict:
    """장면 생성 후 자동으로 평가 수행"""
    
    # 기존 평가가 있으면 삭제
    existing_eval = db.query(EvaluationModel).filter(
        EvaluationModel.scene_id == scene.id
    ).first()
    if existing_eval:
        db.delete(existing_eval)
        db.commit()
    
    if client:
        # OpenAI로 평가
        eval_result = await evaluate_with_openai(client, content, learning_context)
    else:
        # 샘플 평가 생성
        eval_result = generate_sample_evaluation(content, learning_context)
    
    # 평가 저장
    evaluation = EvaluationModel(
        scene_id=scene.id,
        creativity_score=eval_result["creativity_score"],
        consistency_score=eval_result["consistency_score"],
        emotion_score=eval_result["emotion_score"],
        pacing_score=eval_result["pacing_score"],
        dialogue_score=eval_result["dialogue_score"],
        overall_score=eval_result["overall_score"],
        cliche_detected=eval_result["cliche_detected"],
        cliches=eval_result.get("cliches", []),
        issues=eval_result.get("issues", []),
        summary=eval_result["summary"],
        suggestions=eval_result.get("suggestions", []),
        strengths=eval_result.get("strengths", []),
        evaluator_model="auto"
    )
    db.add(evaluation)
    db.commit()
    
    return {
        "overall_score": eval_result["overall_score"],
        "evaluated": True
    }


async def evaluate_with_openai(client, content: str, learning_context: dict) -> dict:
    """OpenAI로 대본 평가"""
    
    prompt = f"""다음 대본을 평가해주세요. JSON 형식으로 응답해주세요.

대본:
```
{content[:1500]}
```

평가 기준:
1. creativity_score (0.0~1.0): 창의성, 신선함
2. consistency_score (0.0~1.0): 일관성, 캐릭터 유지
3. emotion_score (0.0~1.0): 감정 전달력
4. pacing_score (0.0~1.0): 페이싱, 리듬
5. dialogue_score (0.0~1.0): 대화 자연스러움

다음 JSON 형식으로만 응답해주세요:
{{
    "creativity_score": 0.0,
    "consistency_score": 0.0,
    "emotion_score": 0.0,
    "pacing_score": 0.0,
    "dialogue_score": 0.0,
    "overall_score": 0.0,
    "cliche_detected": false,
    "cliches": [],
    "strengths": ["강점1", "강점2"],
    "suggestions": ["제안1", "제안2"],
    "summary": "전체 평가 요약"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 대본 평가 전문가입니다. JSON 형식으로만 응답합니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        import json
        result_text = response.choices[0].message.content
        # JSON 부분만 추출
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        return json.loads(result_text.strip())
    except Exception as e:
        print(f"평가 에러: {e}")
        return generate_sample_evaluation(content, learning_context)


def generate_sample_evaluation(content: str, learning_context: dict) -> dict:
    """샘플 평가 생성"""
    
    # 간단한 휴리스틱 평가
    word_count = len(content)
    line_count = content.count('\n') + 1
    dialogue_count = content.count(':')
    
    # 기본 점수 (0.7~0.9)
    import random
    base = 0.75 + random.random() * 0.15
    
    # 대화가 많으면 대화 점수 높임
    dialogue_bonus = min(0.1, dialogue_count * 0.02)
    
    return {
        "creativity_score": round(base + random.random() * 0.1, 2),
        "consistency_score": round(base + 0.05, 2),
        "emotion_score": round(base + random.random() * 0.08, 2),
        "pacing_score": round(base + random.random() * 0.05, 2),
        "dialogue_score": round(base + dialogue_bonus, 2),
        "overall_score": round(base + 0.03, 2),
        "cliche_detected": random.random() < 0.2,
        "cliches": [],
        "strengths": ["자연스러운 대화 흐름", "캐릭터 말투 유지"],
        "suggestions": ["감정 표현을 더 다양하게"],
        "summary": f"총 {word_count}자, {dialogue_count}개 대사. 전반적으로 양호한 대본입니다."
    }


@router.get("/context/{project_id}", summary="학습 컨텍스트 조회")
async def get_learning_context(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    프로젝트의 학습된 컨텍스트를 조회합니다.
    AI가 어떤 정보를 학습했는지 확인할 수 있습니다.
    """
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    context = build_learning_context(db, project_id)
    
    return {
        "project_id": project_id,
        "project_title": project.title,
        "learning_summary": {
            "total_scenes_analyzed": context["scene_count"],
            "average_score": round(context["avg_score"], 3),
            "strengths_learned": context["strengths_to_keep"],
            "issues_to_avoid": context["issues_to_avoid"],
            "character_patterns": {
                name: len(examples) 
                for name, examples in context["character_examples"].items()
            }
        },
        "best_scenes_count": len(context["best_scenes"]),
        "ready_for_generation": context["scene_count"] > 0
    }
