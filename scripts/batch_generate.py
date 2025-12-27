"""
배치 생성 스크립트
여러 챕터를 한 번에 생성합니다.
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

from scripts.long_form_novel_generator import LongFormNovelGenerator


def batch_generate_chapters(novel_id: str, chapter_goals: list, 
                           target_length: int = 5000, delay: int = 1):
    """
    여러 챕터를 배치로 생성
    
    Args:
        novel_id: 소설 ID
        chapter_goals: 챕터 목표 리스트 [{"chapter": 1, "goal": "..."}, ...]
        target_length: 목표 분량
        delay: 챕터 간 대기 시간 (초)
    """
    import time
    
    generator = LongFormNovelGenerator(novel_id)
    
    # 체크포인트 확인
    checkpoint = generator.checkpoint.load()
    if not checkpoint:
        print(f"오류: 소설 '{novel_id}'가 초기화되지 않았습니다.")
        return
    
    print(f"소설 '{checkpoint.get('title', novel_id)}' 배치 생성 시작")
    print(f"총 {len(chapter_goals)}개 챕터 생성 예정\n")
    
    for i, chapter_info in enumerate(chapter_goals, 1):
        chapter_num = chapter_info.get("chapter", i)
        chapter_goal = chapter_info.get("goal", "")
        
        if not chapter_goal:
            print(f"챕터 {chapter_num}: 목표가 없어 건너뜁니다.")
            continue
        
        print(f"[{i}/{len(chapter_goals)}] 챕터 {chapter_num} 생성 중...")
        print(f"  목표: {chapter_goal}")
        
        try:
            generator.generate_chapter(chapter_num, chapter_goal, target_length)
            print(f"  ✓ 완료\n")
            
            # API 비용 고려하여 대기
            if i < len(chapter_goals):
                time.sleep(delay)
        
        except Exception as e:
            print(f"  ✗ 오류: {e}\n")
            import traceback
            traceback.print_exc()
    
    # 최종 상태 출력
    status = generator.get_novel_status()
    print("=" * 50)
    print("배치 생성 완료")
    print("=" * 50)
    print(f"총 챕터: {status['total_chapters']}개")
    print(f"총 분량: {status['total_words']:,}자")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='배치 챕터 생성')
    parser.add_argument('novel_id', help='소설 ID')
    parser.add_argument('--goals-file', type=Path, help='챕터 목표 JSON 파일')
    parser.add_argument('--target-length', type=int, default=5000, help='목표 분량 (기본: 5000)')
    parser.add_argument('--delay', type=int, default=1, help='챕터 간 대기 시간 초 (기본: 1)')
    
    args = parser.parse_args()
    
    if args.goals_file:
        # JSON 파일에서 목표 로드
        with open(args.goals_file, 'r', encoding='utf-8') as f:
            chapter_goals = json.load(f)
    else:
        # 대화형 입력
        print("챕터 목표를 입력하세요 (빈 줄로 종료):")
        chapter_goals = []
        chapter_num = 1
        while True:
            goal = input(f"챕터 {chapter_num} 목표: ").strip()
            if not goal:
                break
            chapter_goals.append({
                "chapter": chapter_num,
                "goal": goal
            })
            chapter_num += 1
    
    batch_generate_chapters(
        args.novel_id,
        chapter_goals,
        args.target_length,
        args.delay
    )


if __name__ == "__main__":
    main()

