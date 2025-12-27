"""
소설 분석 도구
통계, 일관성 검사, 품질 분석 등을 수행합니다.
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter
import re


class NovelAnalyzer:
    """소설 분석 클래스"""
    
    def __init__(self, novel_id: str):
        """
        Args:
            novel_id: 소설 ID
        """
        project_root = Path(__file__).parent.parent
        self.novel_id = novel_id
        self.novel_dir = project_root / "novels" / novel_id
        self.checkpoint_file = self.novel_dir / "checkpoints" / f"{novel_id}_checkpoint.json"
        self.chapters_dir = self.novel_dir / "chapters"
    
    def load_checkpoint(self) -> Dict:
        """체크포인트 로드"""
        if not self.checkpoint_file.exists():
            return {}
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_statistics(self) -> Dict:
        """통계 정보 조회"""
        checkpoint = self.load_checkpoint()
        chapters = checkpoint.get("chapters", [])
        
        # 챕터 파일 읽기
        total_words = 0
        chapter_lengths = []
        chapter_files = sorted(self.chapters_dir.glob("chapter_*.md"))
        
        for chapter_file in chapter_files:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = len(content)
                total_words += word_count
                chapter_lengths.append(word_count)
        
        # 캐릭터 통계
        characters = checkpoint.get("characters", {})
        
        # 복선 통계
        foreshadowing = checkpoint.get("foreshadowing", [])
        unresolved = [f for f in foreshadowing if not f.get("resolved", False)]
        
        return {
            "novel_id": self.novel_id,
            "title": checkpoint.get("title", "N/A"),
            "genre": checkpoint.get("genre", "N/A"),
            "total_chapters": len(chapters),
            "total_words": total_words,
            "average_chapter_length": sum(chapter_lengths) / len(chapter_lengths) if chapter_lengths else 0,
            "min_chapter_length": min(chapter_lengths) if chapter_lengths else 0,
            "max_chapter_length": max(chapter_lengths) if chapter_lengths else 0,
            "characters_count": len(characters),
            "foreshadowing_total": len(foreshadowing),
            "foreshadowing_unresolved": len(unresolved),
            "foreshadowing_resolved": len(foreshadowing) - len(unresolved)
        }
    
    def check_consistency(self) -> Dict:
        """일관성 검사"""
        issues = []
        checkpoint = self.load_checkpoint()
        
        # 캐릭터 이름 일관성 검사
        characters = checkpoint.get("characters", {})
        character_names = set(characters.keys())
        
        # 챕터 파일에서 캐릭터 이름 추출
        chapter_files = sorted(self.chapters_dir.glob("chapter_*.md"))
        mentioned_characters = set()
        
        for chapter_file in chapter_files:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 간단한 이름 추출 (한글 이름 가정)
                # 실제로는 더 정교한 방법 필요
                for char_name in character_names:
                    if char_name in content:
                        mentioned_characters.add(char_name)
        
        # 정의되었지만 언급되지 않은 캐릭터
        unused_characters = character_names - mentioned_characters
        if unused_characters:
            issues.append({
                "type": "unused_character",
                "severity": "low",
                "message": f"정의되었지만 언급되지 않은 캐릭터: {', '.join(unused_characters)}"
            })
        
        # 복선 회수 확인
        foreshadowing = checkpoint.get("foreshadowing", [])
        unresolved = [f for f in foreshadowing if not f.get("resolved", False)]
        if len(unresolved) > 10:
            issues.append({
                "type": "too_many_unresolved_foreshadowing",
                "severity": "medium",
                "message": f"미해결 복선이 {len(unresolved)}개입니다. 회수를 고려하세요."
            })
        
        # 챕터 길이 일관성
        chapter_lengths = []
        for chapter_file in chapter_files:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_lengths.append(len(f.read()))
        
        if chapter_lengths:
            avg_length = sum(chapter_lengths) / len(chapter_lengths)
            for i, length in enumerate(chapter_lengths):
                if abs(length - avg_length) / avg_length > 0.5:  # 50% 이상 차이
                    issues.append({
                        "type": "inconsistent_chapter_length",
                        "severity": "low",
                        "message": f"챕터 {i+1}의 길이가 평균과 크게 다릅니다 ({length}자 vs 평균 {avg_length:.0f}자)"
                    })
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "severity_counts": {
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"]),
                "low": len([i for i in issues if i["severity"] == "low"])
            }
        }
    
    def analyze_style(self) -> Dict:
        """문체 분석"""
        chapter_files = sorted(self.chapters_dir.glob("chapter_*.md"))
        if not chapter_files:
            return {"error": "챕터 파일이 없습니다."}
        
        # 첫 3개 챕터와 나머지 비교
        early_chapters = chapter_files[:3]
        later_chapters = chapter_files[3:] if len(chapter_files) > 3 else []
        
        # 간단한 문체 지표 (문장 길이, 대화 비율 등)
        def analyze_chapter(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sentences = re.split(r'[.!?。！？]', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
            dialogue_count = len(re.findall(r'["""]', content))
            
            return {
                "avg_sentence_length": avg_sentence_length,
                "dialogue_ratio": dialogue_count / len(sentences) if sentences else 0,
                "total_sentences": len(sentences)
            }
        
        early_stats = [analyze_chapter(f) for f in early_chapters]
        later_stats = [analyze_chapter(f) for f in later_chapters] if later_chapters else []
        
        return {
            "early_chapters": {
                "count": len(early_chapters),
                "avg_sentence_length": sum(s["avg_sentence_length"] for s in early_stats) / len(early_stats) if early_stats else 0,
                "avg_dialogue_ratio": sum(s["dialogue_ratio"] for s in early_stats) / len(early_stats) if early_stats else 0
            },
            "later_chapters": {
                "count": len(later_chapters),
                "avg_sentence_length": sum(s["avg_sentence_length"] for s in later_stats) / len(later_stats) if later_stats else 0,
                "avg_dialogue_ratio": sum(s["dialogue_ratio"] for s in later_stats) / len(later_stats) if later_stats else 0
            },
            "style_consistency": "good" if not later_stats else (
                "warning" if abs(
                    sum(s["avg_sentence_length"] for s in early_stats) / len(early_stats) -
                    sum(s["avg_sentence_length"] for s in later_stats) / len(later_stats)
                ) > 10 else "good"
            )
        }
    
    def generate_report(self) -> str:
        """전체 분석 리포트 생성"""
        stats = self.get_statistics()
        consistency = self.check_consistency()
        style = self.analyze_style()
        
        report = f"""
# 소설 분석 리포트: {stats['title']}

## 기본 정보
- 소설 ID: {stats['novel_id']}
- 장르: {stats['genre']}
- 총 챕터: {stats['total_chapters']}개
- 총 분량: {stats['total_words']:,}자

## 통계
- 평균 챕터 길이: {stats['average_chapter_length']:.0f}자
- 최소 챕터 길이: {stats['min_chapter_length']:,}자
- 최대 챕터 길이: {stats['max_chapter_length']:,}자
- 등장인물 수: {stats['characters_count']}명
- 복선 총계: {stats['foreshadowing_total']}개
  - 해결됨: {stats['foreshadowing_resolved']}개
  - 미해결: {stats['foreshadowing_unresolved']}개

## 일관성 검사
- 발견된 이슈: {consistency['total_issues']}개
  - 높음: {consistency['severity_counts']['high']}개
  - 중간: {consistency['severity_counts']['medium']}개
  - 낮음: {consistency['severity_counts']['low']}개

### 이슈 상세
"""
        for issue in consistency['issues']:
            report += f"- [{issue['severity'].upper()}] {issue['message']}\n"
        
        report += f"""
## 문체 분석
- 초반 챕터 ({style.get('early_chapters', {}).get('count', 0)}개):
  - 평균 문장 길이: {style.get('early_chapters', {}).get('avg_sentence_length', 0):.1f}자
  - 대화 비율: {style.get('early_chapters', {}).get('avg_dialogue_ratio', 0):.2%}

"""
        if style.get('later_chapters', {}).get('count', 0) > 0:
            report += f"""- 후반 챕터 ({style.get('later_chapters', {}).get('count', 0)}개):
  - 평균 문장 길이: {style.get('later_chapters', {}).get('avg_sentence_length', 0):.1f}자
  - 대화 비율: {style.get('later_chapters', {}).get('avg_dialogue_ratio', 0):.2%}

- 문체 일관성: {style.get('style_consistency', 'N/A')}
"""
        
        return report


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='소설 분석 도구')
    parser.add_argument('novel_id', help='소설 ID')
    parser.add_argument('--output', type=Path, help='리포트 저장 경로')
    
    args = parser.parse_args()
    
    analyzer = NovelAnalyzer(args.novel_id)
    
    print("분석 중...")
    report = analyzer.generate_report()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"리포트 저장: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()

