"""
장편 소설 생성 시스템
RAG와 체크포인트를 활용한 장기 기억 유지
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

from models import get_provider, get_model_config, get_api_key
from models.config.model_config import load_config

# 환경 변수 로드
load_dotenv(project_root / ".env")

# Notion 자동 업로드 (선택사항)
try:
    from utils.notion.notion_client import NotionClient
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False


class NovelCheckpoint:
    """소설 체크포인트 관리 클래스"""
    
    def __init__(self, novel_id: str, checkpoint_dir: Path):
        self.novel_id = novel_id
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = checkpoint_dir / f"{novel_id}_checkpoint.json"
    
    def save(self, data: Dict):
        """체크포인트 저장"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> Optional[Dict]:
        """체크포인트 로드"""
        if not self.checkpoint_file.exists():
            return None
        with open(self.checkpoint_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def update_character_state(self, character: str, state: Dict):
        """캐릭터 상태 업데이트"""
        checkpoint = self.load() or {}
        if "characters" not in checkpoint:
            checkpoint["characters"] = {}
        checkpoint["characters"][character] = {
            **checkpoint["characters"].get(character, {}),
            **state,
            "updated_at": datetime.now().isoformat()
        }
        self.save(checkpoint)
    
    def add_foreshadowing(self, content: str, chapter: int):
        """복선/떡밥 추가"""
        checkpoint = self.load() or {}
        if "foreshadowing" not in checkpoint:
            checkpoint["foreshadowing"] = []
        checkpoint["foreshadowing"].append({
            "content": content,
            "chapter": chapter,
            "created_at": datetime.now().isoformat(),
            "resolved": False
        })
        self.save(checkpoint)
    
    def get_context_summary(self) -> str:
        """컨텍스트 요약 생성"""
        checkpoint = self.load()
        if not checkpoint:
            return ""
        
        summary_parts = []
        
        # 캐릭터 상태
        if "characters" in checkpoint:
            summary_parts.append("## 캐릭터 상태")
            for char, state in checkpoint["characters"].items():
                summary_parts.append(f"- {char}: {state.get('current_state', 'N/A')}")
        
        # 미해결 복선
        if "foreshadowing" in checkpoint:
            unresolved = [f for f in checkpoint["foreshadowing"] if not f.get("resolved", False)]
            if unresolved:
                summary_parts.append("\n## 미해결 복선")
                for f in unresolved[-5:]:  # 최근 5개만
                    summary_parts.append(f"- [챕터 {f['chapter']}] {f['content']}")
        
        # 세계관 설정 변경사항
        if "world_building_changes" in checkpoint:
            summary_parts.append("\n## 세계관 설정 변경사항")
            for change in checkpoint["world_building_changes"][-3:]:  # 최근 3개만
                summary_parts.append(f"- {change}")
        
        return "\n".join(summary_parts)


class ChapterSummarizer:
    """챕터 요약 생성 클래스"""
    
    def __init__(self, provider):
        self.provider = provider
    
    def summarize_chapter(self, chapter_text: str, chapter_num: int) -> Dict:
        """챕터 요약 생성"""
        prompt = f"""다음 챕터를 요약해주세요. 다음 형식으로 작성해주세요:

## 챕터 {chapter_num} 요약

### 주요 사건
- [사건 1]
- [사건 2]

### 캐릭터 변화
- [캐릭터명]: [변화 내용]

### 복선/떡밥
- [복선 내용]

### 중요 설정
- [설정 변경사항]

챕터 내용:
{chapter_text[:5000]}  # 처음 5000자만
"""
        
        summary_text = self.provider.generate(
            prompt,
            temperature=0.5,
            max_tokens=1000
        )
        
        return {
            "chapter": chapter_num,
            "summary": summary_text,
            "word_count": len(chapter_text),
            "created_at": datetime.now().isoformat()
        }


class LongFormNovelGenerator:
    """장편 소설 생성기"""
    
    def __init__(self, novel_id: str, provider_name: str = "openai"):
        self.novel_id = novel_id
        self.provider_name = provider_name
        
        # 프로바이더 설정
        api_key = get_api_key(provider_name)
        if not api_key:
            raise ValueError(f"{provider_name} API 키가 설정되지 않았습니다.")
        
        config = get_model_config(provider_name, "creative")
        self.provider = get_provider(provider_name, api_key, config)
        
        # 체크포인트 시스템
        checkpoint_dir = project_root / "novels" / novel_id / "checkpoints"
        self.checkpoint = NovelCheckpoint(novel_id, checkpoint_dir)
        
        # 요약 시스템
        self.summarizer = ChapterSummarizer(self.provider)
        
        # 챕터 저장 디렉토리
        self.chapters_dir = project_root / "novels" / novel_id / "chapters"
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_novel(self, title: str, genre: str, world_setting: str, 
                        characters: List[Dict], plot_outline: str):
        """소설 초기화"""
        checkpoint_data = {
            "title": title,
            "genre": genre,
            "world_setting": world_setting,
            "characters": {char["name"]: char for char in characters},
            "plot_outline": plot_outline,
            "chapters": [],
            "foreshadowing": [],
            "world_building_changes": [],
            "style_samples": []
        }
        self.checkpoint.save(checkpoint_data)
        
        print(f"소설 '{title}' 초기화 완료")
        print(f"장르: {genre}")
        print(f"등장인물: {len(characters)}명")
    
    def generate_chapter(self, chapter_num: int, chapter_goal: str, 
                        target_length: int = 5000) -> str:
        """챕터 생성"""
        checkpoint = self.checkpoint.load()
        if not checkpoint:
            raise ValueError("소설이 초기화되지 않았습니다. initialize_novel()을 먼저 호출하세요.")
        
        # 컨텍스트 구성
        context_summary = self.checkpoint.get_context_summary()
        
        # 이전 챕터 요약
        previous_chapters = checkpoint.get("chapters", [])
        previous_summaries = []
        if previous_chapters:
            for ch in previous_chapters[-3:]:  # 최근 3개 챕터 요약만
                if "summary" in ch:
                    previous_summaries.append(f"챕터 {ch['chapter']}: {ch['summary'][:200]}")
        
        # 문체 샘플
        style_samples = checkpoint.get("style_samples", [])
        style_sample = ""
        if style_samples:
            style_sample = f"\n문체 참고 샘플:\n{style_samples[0][:500]}"
        
        # 프롬프트 구성
        prompt = f"""당신은 전문 소설가입니다. 다음 정보를 바탕으로 소설의 챕터 {chapter_num}을 작성해주세요.

## 소설 정보
제목: {checkpoint['title']}
장르: {checkpoint['genre']}

## 세계관 설정
{checkpoint['world_setting']}

## 등장인물
{self._format_characters(checkpoint['characters'])}

## 플롯 구조
{checkpoint['plot_outline']}

## 현재 상황 요약
{context_summary}

## 이전 챕터 요약
{chr(10).join(previous_summaries) if previous_summaries else "첫 챕터입니다."}
{style_sample}

## 챕터 목표
{chapter_goal}

## 요구사항
1. 위의 세계관과 캐릭터 설정을 정확히 따르세요
2. 이전 챕터의 흐름을 자연스럽게 이어가세요
3. 문체는 일관되게 유지하세요
4. 복선을 회수하거나 새로운 복선을 심어주세요
5. 목표 분량: 약 {target_length}자

챕터 {chapter_num}을 작성해주세요:
"""
        
        print(f"챕터 {chapter_num} 생성 중...")
        chapter_text = self.provider.generate(
            prompt,
            temperature=0.8,
            max_tokens=min(target_length * 2, 4000)  # 토큰 제한 고려
        )
        
        # 챕터 저장
        chapter_file = self.chapters_dir / f"chapter_{chapter_num:03d}.md"
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(f"# 챕터 {chapter_num}\n\n")
            f.write(f"**목표**: {chapter_goal}\n\n")
            f.write("---\n\n")
            f.write(chapter_text)
        
        # 챕터 요약 생성
        print("챕터 요약 생성 중...")
        chapter_summary = self.summarizer.summarize_chapter(chapter_text, chapter_num)
        
        # 체크포인트 업데이트
        checkpoint["chapters"].append({
            "chapter": chapter_num,
            "goal": chapter_goal,
            "file": str(chapter_file),
            "word_count": len(chapter_text),
            "summary": chapter_summary["summary"],
            "created_at": datetime.now().isoformat()
        })
        
        # 문체 샘플 저장 (첫 3개 챕터만)
        if chapter_num <= 3:
            checkpoint["style_samples"].append(chapter_text[:1000])
        
        self.checkpoint.save(checkpoint)
        
        print(f"챕터 {chapter_num} 생성 완료 ({len(chapter_text)}자)")
        
        # Notion 자동 업로드 (설정되어 있으면)
        if NOTION_AVAILABLE:
            try:
                config = load_config()
                notion_config = config.get("notion", {})
                auto_upload = notion_config.get("auto_upload", False)
                parent_url = notion_config.get("default_parent_url")
                
                if auto_upload and parent_url:
                    print("Notion에 자동 업로드 중...")
                    client = NotionClient()
                    parent_id = client.get_page_id_from_url(parent_url)
                    
                    checkpoint = self.checkpoint.load()
                    novel_title = checkpoint.get('title', self.novel_id)
                    
                    page = client.create_page(
                        parent_page_id=parent_id,
                        title=f"{novel_title} - 챕터 {chapter_num}",
                        content=chapter_text
                    )
                    print(f"[OK] Notion 페이지 생성 완료!")
                    print(f"   URL: {page.get('url', 'N/A')}")
            except Exception as e:
                print(f"[WARNING] Notion 업로드 실패: {e}")
                print("   (챕터는 정상적으로 생성되었습니다)")
        
        return chapter_text
    
    def _format_characters(self, characters: Dict) -> str:
        """캐릭터 정보 포맷팅"""
        result = []
        for name, info in characters.items():
            char_info = f"- **{name}**: {info.get('description', 'N/A')}"
            if 'current_state' in info:
                char_info += f"\n  현재 상태: {info['current_state']}"
            result.append(char_info)
        return "\n".join(result)
    
    def get_novel_status(self) -> Dict:
        """소설 진행 상황 조회"""
        checkpoint = self.checkpoint.load()
        if not checkpoint:
            return {"status": "not_initialized"}
        
        total_words = sum(ch.get("word_count", 0) for ch in checkpoint.get("chapters", []))
        unresolved_foreshadowing = len([
            f for f in checkpoint.get("foreshadowing", [])
            if not f.get("resolved", False)
        ])
        
        return {
            "title": checkpoint.get("title", "N/A"),
            "total_chapters": len(checkpoint.get("chapters", [])),
            "total_words": total_words,
            "unresolved_foreshadowing": unresolved_foreshadowing,
            "characters": len(checkpoint.get("characters", {})),
            "last_updated": checkpoint.get("last_updated", "N/A")
        }


def main():
    """메인 함수"""
    print("=" * 60)
    print("장편 소설 생성 시스템")
    print("=" * 60)
    print()
    
    # 소설 ID 입력
    novel_id = input("소설 ID (영문/숫자만): ").strip()
    if not novel_id:
        print("소설 ID를 입력해주세요.")
        return
    
    generator = LongFormNovelGenerator(novel_id)
    
    # 초기화 여부 확인
    checkpoint = generator.checkpoint.load()
    if not checkpoint:
        print("\n새 소설을 초기화합니다.")
        title = input("제목: ").strip()
        genre = input("장르: ").strip()
        
        print("\n세계관 설정을 입력하세요 (여러 줄, 빈 줄로 종료):")
        world_setting_lines = []
        while True:
            line = input()
            if not line.strip():
                break
            world_setting_lines.append(line)
        world_setting = "\n".join(world_setting_lines)
        
        print("\n등장인물 정보를 입력하세요 (이름:설명 형식, 빈 줄로 종료):")
        characters = []
        while True:
            char_input = input("인물: ").strip()
            if not char_input:
                break
            if ":" in char_input:
                name, desc = char_input.split(":", 1)
                characters.append({"name": name.strip(), "description": desc.strip()})
        
        print("\n플롯 구조를 입력하세요 (여러 줄, 빈 줄로 종료):")
        plot_lines = []
        while True:
            line = input()
            if not line.strip():
                break
            plot_lines.append(line)
        plot_outline = "\n".join(plot_lines)
        
        generator.initialize_novel(title, genre, world_setting, characters, plot_outline)
    else:
        print(f"\n기존 소설 '{checkpoint.get('title', 'N/A')}' 로드됨")
        status = generator.get_novel_status()
        print(f"총 챕터: {status['total_chapters']}개")
        print(f"총 분량: {status['total_words']:,}자")
    
    # 챕터 생성
    print("\n챕터 생성을 시작합니다.")
    while True:
        chapter_num = input("\n생성할 챕터 번호 (종료: q): ").strip()
        if chapter_num.lower() == 'q':
            break
        
        try:
            chapter_num = int(chapter_num)
            chapter_goal = input("이 챕터의 목표/주요 사건: ").strip()
            target_length = input("목표 분량 (기본 5000자): ").strip()
            target_length = int(target_length) if target_length else 5000
            
            generator.generate_chapter(chapter_num, chapter_goal, target_length)
            
            # 상태 출력
            status = generator.get_novel_status()
            print(f"\n현재 진행: {status['total_chapters']}챕터, {status['total_words']:,}자")
            
        except ValueError:
            print("올바른 챕터 번호를 입력하세요.")
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n작업이 취소되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

