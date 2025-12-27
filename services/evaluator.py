"""
평가 AI 서비스
창의성, 클리셰, 감정 강도 등을 평가하는 AI 시스템

핵심 원칙: 생성 AI ≠ 평가 AI (분리)
"""

import json
import re
from typing import Optional, List, Dict, Any
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import get_provider, get_model_config, get_api_key
from models.schemas.evaluation import (
    EvaluationCreate, ClicheDetection, EvaluationIssue,
    ClicheType, EvaluationCategory, SeverityLevel
)


class SceneEvaluator:
    """
    장면 평가 AI
    
    생성 AI와 분리된 평가 전용 AI 시스템입니다.
    창의성, 일관성, 감정 강도, 클리셰 감지 등을 수행합니다.
    """
    
    def __init__(self, provider_name: str = "openai"):
        """
        Args:
            provider_name: 평가에 사용할 AI 프로바이더
        """
        self.provider_name = provider_name
        api_key = get_api_key(provider_name)
        
        if not api_key:
            raise ValueError(f"{provider_name} API 키가 설정되지 않았습니다.")
        
        # 평가용은 structured 모델 사용 (일관된 결과를 위해)
        config = get_model_config(provider_name, "structured")
        self.provider = get_provider(provider_name, api_key, config)
        
        # 클리셰 데이터베이스 (확장 가능)
        self.common_cliches = {
            "dialogue": [
                "그럴 리가 없어",
                "이게 무슨 일이야",
                "설마...",
                "아닐 거야",
                "믿을 수 없어",
                "이건 시작에 불과해",
            ],
            "plot": [
                "알고 보니 쌍둥이",
                "죽은 줄 알았던 사람이 살아있음",
                "모든 것이 꿈이었음",
                "마지막에 반전으로 악당이 가족",
            ],
            "transition": [
                "그때였다",
                "순간",
                "바로 그 순간",
                "그러던 어느 날",
            ]
        }
    
    def evaluate(self, 
                 content: str, 
                 context: Optional[Dict[str, Any]] = None,
                 characters: Optional[List[Dict]] = None) -> EvaluationCreate:
        """
        장면을 평가합니다.
        
        Args:
            content: 평가할 장면 본문
            context: 세계관, 이전 장면 등 컨텍스트 정보
            characters: 참여 캐릭터 정보
        
        Returns:
            EvaluationCreate: 평가 결과
        """
        # 1. 기본 분석 (규칙 기반)
        rule_based_analysis = self._analyze_with_rules(content)
        
        # 2. AI 평가
        ai_evaluation = self._evaluate_with_ai(content, context, characters)
        
        # 3. 결과 통합
        return self._merge_evaluations(rule_based_analysis, ai_evaluation, content)
    
    def _analyze_with_rules(self, content: str) -> Dict[str, Any]:
        """규칙 기반 분석 (빠른 검사)"""
        result = {
            "cliches": [],
            "issues": [],
            "word_count": len(content),
            "dialogue_ratio": 0.0
        }
        
        # 클리셰 감지
        for cliche_type, patterns in self.common_cliches.items():
            for pattern in patterns:
                if pattern in content:
                    result["cliches"].append({
                        "type": cliche_type,
                        "text": pattern,
                        "explanation": f"'{pattern}'은(는) 자주 사용되는 클리셰입니다."
                    })
        
        # 대화 비율 계산
        dialogue_lines = len(re.findall(r'"[^"]*"', content))
        total_lines = max(len(content.split('\n')), 1)
        result["dialogue_ratio"] = dialogue_lines / total_lines
        
        # 길이 검사
        if len(content) < 100:
            result["issues"].append({
                "category": "structure",
                "severity": "warning",
                "message": "장면이 너무 짧습니다. 더 자세한 묘사가 필요할 수 있습니다."
            })
        
        return result
    
    def _evaluate_with_ai(self, 
                         content: str,
                         context: Optional[Dict] = None,
                         characters: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """AI를 사용한 평가"""
        
        context_text = ""
        if context:
            context_text = f"""
## 컨텍스트
세계관: {context.get('world_setting', 'N/A')}
이전 장면 요약: {context.get('previous_summary', 'N/A')}
"""
        
        characters_text = ""
        if characters:
            char_info = [f"- {c.get('name', 'N/A')}: {c.get('speech_pattern', 'N/A')}" 
                        for c in characters]
            characters_text = f"""
## 등장인물
{chr(10).join(char_info)}
"""
        
        prompt = f"""당신은 전문 방송작가/대본 평론가입니다. 다음 대본 장면을 분석하고 평가해주세요.

{context_text}
{characters_text}

## 평가할 장면
{content[:3000]}

## 평가 기준
1. **창의성 (creativity_score)**: 독창적인 표현, 예상을 뛰어넘는 전개가 있는가?
2. **일관성 (consistency_score)**: 캐릭터의 말투와 성격이 일관되는가?
3. **감정 전달 (emotion_score)**: 감정이 효과적으로 전달되는가?
4. **페이싱 (pacing_score)**: 장면의 속도감과 리듬이 적절한가?
5. **대화 퀄리티 (dialogue_score)**: 대화가 자연스럽고 개성이 있는가?

## 출력 형식 (JSON)
```json
{{
    "creativity_score": 0.0-1.0,
    "consistency_score": 0.0-1.0,
    "emotion_score": 0.0-1.0,
    "pacing_score": 0.0-1.0,
    "dialogue_score": 0.0-1.0,
    "cliches": [
        {{
            "type": "dialogue|plot|character|transition",
            "text": "클리셰가 발견된 텍스트",
            "explanation": "왜 클리셰인지 설명",
            "alternatives": ["대안1", "대안2"]
        }}
    ],
    "issues": [
        {{
            "category": "creativity|consistency|emotion|pacing|dialogue|structure",
            "severity": "info|warning|error",
            "message": "이슈 설명",
            "suggestion": "개선 제안"
        }}
    ],
    "summary": "전체 평가 요약 (2-3문장)",
    "strengths": ["잘된 점1", "잘된 점2"],
    "suggestions": ["개선 제안1", "개선 제안2"]
}}
```

JSON만 출력해주세요:"""

        try:
            response = self.provider.generate(prompt, temperature=0.3, max_tokens=1500)
            
            # JSON 추출
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_default_evaluation()
                
        except Exception as e:
            print(f"AI 평가 실패: {e}")
            return self._get_default_evaluation()
    
    def _get_default_evaluation(self) -> Dict[str, Any]:
        """기본 평가 결과 (AI 실패 시)"""
        return {
            "creativity_score": 0.5,
            "consistency_score": 0.5,
            "emotion_score": 0.5,
            "pacing_score": 0.5,
            "dialogue_score": 0.5,
            "cliches": [],
            "issues": [],
            "summary": "AI 평가를 수행할 수 없었습니다.",
            "strengths": [],
            "suggestions": ["AI 평가를 다시 시도해주세요."]
        }
    
    def _merge_evaluations(self, 
                          rule_based: Dict, 
                          ai_based: Dict,
                          content: str) -> EvaluationCreate:
        """규칙 기반과 AI 평가 결과를 통합"""
        
        # 클리셰 통합
        all_cliches = []
        
        # 규칙 기반 클리셰
        for c in rule_based.get("cliches", []):
            all_cliches.append(ClicheDetection(
                cliche_type=ClicheType(c["type"]),
                detected_text=c["text"],
                explanation=c["explanation"],
                alternatives=[]
            ))
        
        # AI 클리셰
        for c in ai_based.get("cliches", []):
            try:
                all_cliches.append(ClicheDetection(
                    cliche_type=ClicheType(c.get("type", "dialogue")),
                    detected_text=c.get("text", ""),
                    explanation=c.get("explanation", ""),
                    alternatives=c.get("alternatives", [])
                ))
            except:
                pass
        
        # 이슈 통합
        all_issues = []
        
        for issue in rule_based.get("issues", []):
            try:
                all_issues.append(EvaluationIssue(
                    category=EvaluationCategory(issue.get("category", "structure")),
                    severity=SeverityLevel(issue.get("severity", "warning")),
                    message=issue.get("message", ""),
                    suggestion=issue.get("suggestion")
                ))
            except:
                pass
        
        for issue in ai_based.get("issues", []):
            try:
                all_issues.append(EvaluationIssue(
                    category=EvaluationCategory(issue.get("category", "structure")),
                    severity=SeverityLevel(issue.get("severity", "warning")),
                    message=issue.get("message", ""),
                    suggestion=issue.get("suggestion")
                ))
            except:
                pass
        
        # 종합 점수 계산
        scores = {
            "creativity": ai_based.get("creativity_score", 0.5),
            "consistency": ai_based.get("consistency_score", 0.5),
            "emotion": ai_based.get("emotion_score", 0.5),
            "pacing": ai_based.get("pacing_score", 0.5),
            "dialogue": ai_based.get("dialogue_score", 0.5)
        }
        
        # 클리셰가 많으면 창의성 감점
        if len(all_cliches) > 0:
            penalty = min(len(all_cliches) * 0.1, 0.3)
            scores["creativity"] = max(0, scores["creativity"] - penalty)
        
        overall_score = sum(scores.values()) / len(scores)
        
        return EvaluationCreate(
            scene_id=0,  # 호출자가 설정
            creativity_score=scores["creativity"],
            consistency_score=scores["consistency"],
            emotion_score=scores["emotion"],
            pacing_score=scores["pacing"],
            dialogue_score=scores["dialogue"],
            overall_score=overall_score,
            cliche_detected=len(all_cliches) > 0,
            cliches=all_cliches,
            issues=all_issues,
            summary=ai_based.get("summary", "평가 완료"),
            suggestions=ai_based.get("suggestions", []),
            strengths=ai_based.get("strengths", [])
        )
    
    def quick_evaluate(self, content: str) -> Dict[str, Any]:
        """
        빠른 평가 (규칙 기반만)
        
        AI 호출 없이 빠르게 기본적인 평가를 수행합니다.
        """
        analysis = self._analyze_with_rules(content)
        
        cliche_count = len(analysis["cliches"])
        issue_count = len(analysis["issues"])
        
        # 간단한 점수 계산
        base_score = 0.7
        if cliche_count > 0:
            base_score -= cliche_count * 0.1
        if issue_count > 0:
            base_score -= issue_count * 0.05
        
        base_score = max(0.3, min(1.0, base_score))
        
        return {
            "quick_score": base_score,
            "cliche_count": cliche_count,
            "issue_count": issue_count,
            "cliches": analysis["cliches"],
            "issues": analysis["issues"],
            "needs_full_evaluation": cliche_count > 0 or issue_count > 0
        }


# 평가 API 엔드포인트에서 사용할 함수
def evaluate_scene(scene_id: int, content: str, 
                  context: Optional[Dict] = None,
                  characters: Optional[List[Dict]] = None,
                  provider: str = "openai") -> EvaluationCreate:
    """
    장면 평가 헬퍼 함수
    
    Args:
        scene_id: 장면 DB ID
        content: 장면 본문
        context: 컨텍스트 정보
        characters: 캐릭터 정보
        provider: AI 프로바이더
    
    Returns:
        EvaluationCreate: 평가 결과 (DB 저장용)
    """
    evaluator = SceneEvaluator(provider)
    result = evaluator.evaluate(content, context, characters)
    result.scene_id = scene_id
    return result

