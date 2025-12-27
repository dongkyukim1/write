"""
샘플 데이터 생성 스크립트
프로젝트, 캐릭터, 에피소드, 장면을 생성합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.database import SessionLocal, init_db
from models.database.models import (
    ProjectModel, CharacterModel, EpisodeModel, 
    SceneModel, EvaluationModel
)
from datetime import datetime, date


def seed_database():
    """샘플 데이터 생성"""
    init_db()
    db = SessionLocal()
    
    try:
        # 기존 데이터 삭제
        db.query(EvaluationModel).delete()
        db.query(SceneModel).delete()
        db.query(EpisodeModel).delete()
        db.query(CharacterModel).delete()
        db.query(ProjectModel).delete()
        db.commit()
        print("기존 데이터 삭제 완료")
        
        # ==================== 프로젝트 생성 ====================
        project = ProjectModel(
            title="매불쇼 시즌1",
            project_type="talk_show",
            description="시사 토크쇼 - 매일 밤 정치/사회 이슈를 유쾌하게 분석하는 프로그램",
            world_setting="현대 한국 배경\n정치 풍자 가능\n실제 인물 패러디 가능\n욕설/비속어 자제\n특정 정당 편향 금지",
            style_guide="대화체 중심\n짧고 임팩트 있는 문장\n유머와 풍자의 균형\n시청자와 공감대 형성",
            status="active"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"프로젝트 생성: {project.title} (ID: {project.id})")
        
        # ==================== 캐릭터 생성 ====================
        characters_data = [
            {
                "name": "최욱",
                "role": "host",
                "description": "매불쇼의 메인 진행자. 날카로운 풍자와 유머의 달인.",
                "backstory": "전직 개그맨 출신으로, 정치 풍자 코미디로 인기를 얻음",
                "personality_traits": ["날카로움", "유머러스", "직설적", "카리스마"],
                "personality_description": "날카롭지만 유머러스한 성격. 어려운 주제도 쉽게 풀어내는 능력.",
                "speech_pattern": "짧고 임팩트 있는 문장. 풍자적 비유를 자주 사용.",
                "speech_examples": [
                    "이게 말이 됩니까? 안 되죠.",
                    "자, 여기서 중요한 건요...",
                    "시청자 여러분, 이거 웃으면 안 되는 거예요."
                ],
                "current_state": "오늘 방송 준비 완료",
                "forbidden_actions": ["욕설", "인신공격"]
            },
            {
                "name": "김어준",
                "role": "co_host",
                "description": "공동 진행자이자 시사 분석가. 깊이 있는 분석과 배경 설명 담당.",
                "personality_traits": ["분석적", "차분함", "박학다식", "논리적"],
                "personality_description": "차분하면서도 날카로운 분석을 제공.",
                "speech_pattern": "설명적이고 논리적인 문장.",
                "speech_examples": [
                    "이 사안의 본질은 이겁니다.",
                    "역사적 맥락에서 보면..."
                ],
                "current_state": "오늘 이슈 브리핑 준비 완료",
                "forbidden_actions": ["감정적 발언"]
            },
            {
                "name": "주진우",
                "role": "co_host",
                "description": "탐사보도 전문가. 팩트체크와 심층 취재 담당.",
                "personality_traits": ["끈질김", "정의감", "열정적"],
                "personality_description": "팩트에 기반한 날카로운 지적.",
                "speech_pattern": "확신에 찬 어조. 증거 기반 발언.",
                "speech_examples": [
                    "제가 취재해 본 결과...",
                    "이건 팩트입니다."
                ],
                "current_state": "팩트체크 자료 준비 완료",
                "forbidden_actions": ["출처 불명확한 정보"]
            }
        ]
        
        characters = []
        for char_data in characters_data:
            char = CharacterModel(project_id=project.id, **char_data)
            db.add(char)
            characters.append(char)
        
        db.commit()
        for char in characters:
            db.refresh(char)
            print(f"캐릭터 생성: {char.name} ({char.role})")
        
        # ==================== 에피소드 생성 ====================
        episode = EpisodeModel(
            project_id=project.id,
            episode_number=1,
            title="이번 주 핵심 이슈 - 예산안 국회 통과",
            summary="예산안 국회 통과를 둘러싼 여야 공방과 그 배경을 분석",
            status="completed",
            main_topic="2024년 예산안 국회 통과",
            sub_topics=["여야 합의 과정", "삭감된 예산 항목", "향후 전망"],
            target_runtime=60,
            actual_runtime=58,
            broadcast_date=date(2024, 12, 20),
            notes="연말 특집"
        )
        db.add(episode)
        db.commit()
        db.refresh(episode)
        print(f"에피소드 생성: EP{episode.episode_number} - {episode.title}")
        
        # ==================== 장면 생성 (AI 생성된 것처럼) ====================
        scenes_data = [
            {
                "scene_number": 1,
                "scene_id": "S01E01_SC01",
                "scene_type": "opening",
                "title": "오프닝 - 인사와 주제 소개",
                "goal": "시청자 흥미 유발 및 오늘 주제 소개",
                "content": """최욱: (카메라를 보며) 안녕하세요, 매불쇼입니다. 오늘 밤도 어김없이 찾아왔습니다.

김어준: 네, 오늘은 정말 이야기할 게 많은 날이에요.

최욱: 예산안이 드디어 통과됐거든요. 근데 이게 좀... 복잡해요.

주진우: 복잡한 정도가 아니에요. 제가 보기엔 역대급입니다.

최욱: (웃으며) 자, 그래서 오늘 우리가 이걸 확실하게 정리해 드리려고 합니다. 시청자 여러분, 편하게 앉으시고 오늘 방송 끝나면 이 예산안, 완벽하게 이해하실 수 있을 거예요.

김어준: 그럼 바로 들어가볼까요?

최욱: 네, 들어갑니다!""",
                "emotion_curve": ["기대", "흥미", "호기심"],
                "conflict_type": "none",
                "dialog_density": "high",
                "ai_generated": True,
                "human_edited": True,
                "generation_prompt": "매불쇼 스타일의 가벼우면서도 기대감을 주는 오프닝 장면",
                "version": 2,
                "character_ids": [1, 2, 3]
            },
            {
                "scene_number": 2,
                "scene_id": "S01E01_SC02",
                "scene_type": "talk",
                "title": "이슈 브리핑 - 예산안 통과 경위",
                "goal": "예산안 통과 과정을 쉽게 설명",
                "content": """김어준: 자, 이번 예산안 통과 과정을 간단히 정리해 드릴게요.

(화면에 타임라인 그래픽)

김어준: 먼저 정부가 10월에 예산안을 제출했습니다. 총 656조 규모였어요.

최욱: 656조... 이게 얼마나 큰 돈이냐면요, 1초에 1만 원씩 써도 2천 년이 걸립니다.

주진우: (끼어들며) 그런데 여기서 중요한 건, 이 중에서 얼마가 삭감됐느냐예요.

김어준: 네, 결과적으로 4.1조가 삭감됐습니다. 이 중에서 가장 논란이 됐던 게...

최욱: R&D 예산이죠.

김어준: 맞습니다. 연구개발 예산이 크게 줄었어요. 이게 왜 문제냐면...

주진우: 제가 과학기술부 출입 기자들한테 들은 얘기인데요, 현장에서 난리가 났다고 해요.

최욱: (심각하게) 이거 진짜 심각한 문제인 게, 한 번 끊기면 다시 시작하기 어려운 연구들이 많거든요.

김어준: 그래서 과학계에서 반발이 큰 상황입니다.""",
                "emotion_curve": ["집중", "놀람", "우려"],
                "conflict_type": "ideological",
                "dialog_density": "high",
                "ai_generated": True,
                "human_edited": True,
                "generation_prompt": "예산안 통과 과정을 쉽게 설명. 숫자는 비유로.",
                "version": 3,
                "character_ids": [1, 2, 3]
            },
            {
                "scene_number": 3,
                "scene_id": "S01E01_SC03",
                "scene_type": "highlight",
                "title": "팩트체크 - 여야 주장 검증",
                "goal": "여야 주장의 팩트 확인",
                "content": """주진우: 자, 이제 팩트체크 시간입니다.

(화면에 '팩트체크' 로고)

주진우: 여당에서는 이번 예산안이 '민생 중심'이라고 주장했습니다. 실제로 그런지 확인해 봤어요.

(자료 화면)

주진우: 먼저 복지 예산. 전년 대비 5.2% 증가했습니다. 이건 팩트예요.

최욱: 그럼 민생 중심 맞는 거 아니에요?

주진우: 근데 여기서 함정이 있어요. 물가 상승률을 감안하면 실질적으로는 2.1% 증가에 불과합니다.

김어준: 아, 그러니까 숫자만 보면 늘었지만 실제 체감은 다를 수 있다는 거네요.

주진우: 정확합니다. 그리고 야당에서 주장한 'R&D 예산 역대급 삭감'... 이것도 확인해 봤습니다.

최욱: 이건 어떻습니까?

주진우: 이건 사실입니다. IMF 이후 가장 큰 폭의 삭감이에요. 자료 다 있습니다.

김어준: 그러니까 양쪽 다 일부는 맞고 일부는 과장이 있다는 거네요.

주진우: 네, 그래서 저희가 균형 잡힌 시각을 드리려고 합니다.""",
                "emotion_curve": ["기대", "집중", "이해"],
                "conflict_type": "ideological",
                "dialog_density": "high",
                "ai_generated": True,
                "human_edited": False,
                "generation_prompt": "팩트체크 장면. 객관적 검증.",
                "version": 1,
                "character_ids": [1, 2, 3]
            },
            {
                "scene_number": 4,
                "scene_id": "S01E01_SC04",
                "scene_type": "closing",
                "title": "마무리 - 정리 및 다음 예고",
                "goal": "오늘 내용 정리 및 인사",
                "content": """최욱: 자, 오늘 내용을 정리해 보면요.

김어준: 첫째, 예산안 656조 중 4.1조가 삭감됐다.

주진우: 둘째, R&D 예산 삭감이 가장 논란이다.

최욱: 셋째, 여야 주장 모두 일부는 맞고 일부는 과장이 있다.

(웃으며) 복잡한 예산안, 오늘 이해되셨죠?

김어준: 다음 주에는 이 예산안이 실제로 어떻게 집행되는지 살펴보겠습니다.

주진우: 저도 몇 가지 더 취재해 올 게 있어요. 기대해 주세요.

최욱: 네, 오늘 방송 여기까지입니다. 시청해 주신 여러분 감사합니다!

(세 사람 함께) 매불쇼였습니다!

(엔딩 음악)""",
                "emotion_curve": ["정리", "기대", "따뜻함"],
                "conflict_type": "none",
                "dialog_density": "medium",
                "ai_generated": True,
                "human_edited": True,
                "generation_prompt": "따뜻한 마무리. 오늘 내용 요약.",
                "version": 2,
                "character_ids": [1, 2, 3]
            }
        ]
        
        scenes = []
        for scene_data in scenes_data:
            scene = SceneModel(
                episode_id=episode.id,
                word_count=len(scene_data["content"]),
                **scene_data
            )
            db.add(scene)
            scenes.append(scene)
        
        db.commit()
        for scene in scenes:
            db.refresh(scene)
            print(f"장면 생성: {scene.scene_id} - {scene.title}")
        
        # ==================== 평가 생성 ====================
        evaluations_data = [
            {
                "scene_id": 1,
                "overall_score": 0.85,
                "creativity_score": 0.82,
                "consistency_score": 0.90,
                "emotion_score": 0.88,
                "pacing_score": 0.80,
                "dialogue_score": 0.85,
                "cliche_detected": False,
                "cliches": [],
                "issues": [],
                "strengths": ["자연스러운 대화", "시청자 친화적", "적절한 유머"],
                "suggestions": ["첫 대사를 좀 더 임팩트 있게"],
                "summary": "전반적으로 우수한 오프닝. 세 진행자의 케미가 잘 드러남."
            },
            {
                "scene_id": 2,
                "overall_score": 0.88,
                "creativity_score": 0.75,
                "consistency_score": 0.92,
                "emotion_score": 0.85,
                "pacing_score": 0.78,
                "dialogue_score": 0.88,
                "cliche_detected": False,
                "cliches": [],
                "issues": [],
                "strengths": ["복잡한 정보를 쉽게 풀어냄", "비유 효과적"],
                "suggestions": ["그래픽 전환 타이밍 조정"],
                "summary": "정보 전달과 재미를 잘 균형 잡음."
            },
            {
                "scene_id": 3,
                "overall_score": 0.92,
                "creativity_score": 0.78,
                "consistency_score": 0.95,
                "emotion_score": 0.90,
                "pacing_score": 0.88,
                "dialogue_score": 0.92,
                "cliche_detected": False,
                "cliches": [],
                "issues": [],
                "strengths": ["객관적 검증", "균형 잡힌 시각"],
                "suggestions": ["시각 자료 더 활용"],
                "summary": "팩트체크의 정수. 신뢰성과 재미 모두 잡음."
            },
            {
                "scene_id": 4,
                "overall_score": 0.87,
                "creativity_score": 0.80,
                "consistency_score": 0.92,
                "emotion_score": 0.82,
                "pacing_score": 0.85,
                "dialogue_score": 0.90,
                "cliche_detected": True,
                "cliches": [{"type": "ending", "description": "다음 주에 또 만나요 표현이 진부함"}],
                "issues": [],
                "strengths": ["내용 정리 명확", "다음 회 기대감"],
                "suggestions": ["개성 있는 엔딩 멘트 개발"],
                "summary": "안정적인 마무리."
            }
        ]
        
        for i, eval_data in enumerate(evaluations_data):
            eval_data["scene_id"] = scenes[i].id
            evaluation = EvaluationModel(**eval_data)
            db.add(evaluation)
        
        db.commit()
        print(f"평가 생성: {len(evaluations_data)}개 장면 평가 완료")
        
        # 통계 출력
        total_words = sum(s.word_count for s in scenes)
        
        print("\n" + "="*50)
        print("샘플 데이터 생성 완료!")
        print("="*50)
        print(f"프로젝트: {project.title}")
        print(f"캐릭터: {len(characters)}명")
        print(f"에피소드: 1개")
        print(f"장면: {len(scenes)}개")
        print(f"평가: {len(evaluations_data)}개")
        print(f"총 글자 수: {total_words}자")
        
    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
