"""
Git 워크플로우 자동화 유틸리티
대본 버전 관리를 위한 Git 통합

브랜치 전략:
- main          : 최종 승인된 대본
- draft/ai_v1   : AI 초안
- draft/edited  : 작가 수정본
- review/       : 검토 중
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class GitManager:
    """
    Git 워크플로우 관리자
    
    대본 작성 시스템을 위한 Git 자동화 도구
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Args:
            repo_path: Git 저장소 경로 (기본값: 프로젝트 루트)
        """
        if repo_path is None:
            repo_path = Path(__file__).parent.parent
        
        self.repo_path = repo_path
        
        # Git이 설치되어 있는지 확인
        try:
            self._run_git(["--version"])
        except FileNotFoundError:
            raise RuntimeError("Git이 설치되어 있지 않습니다.")
    
    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Git 명령 실행"""
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check
        )
    
    # ==================== 브랜치 관리 ====================
    
    def create_draft_branch(self, scene_id: str, draft_type: str = "ai") -> str:
        """
        드래프트 브랜치 생성
        
        Args:
            scene_id: 장면 ID (예: S01E03_SC02)
            draft_type: 드래프트 타입 (ai, edited, review)
        
        Returns:
            생성된 브랜치 이름
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        branch_name = f"draft/{draft_type}/{scene_id}_{timestamp}"
        
        self._run_git(["checkout", "-b", branch_name])
        
        return branch_name
    
    def get_current_branch(self) -> str:
        """현재 브랜치 이름 조회"""
        result = self._run_git(["branch", "--show-current"])
        return result.stdout.strip()
    
    def list_branches(self, pattern: Optional[str] = None) -> List[str]:
        """
        브랜치 목록 조회
        
        Args:
            pattern: 필터 패턴 (예: "draft/*")
        
        Returns:
            브랜치 이름 목록
        """
        args = ["branch", "-a"]
        result = self._run_git(args)
        
        branches = [
            line.strip().replace("* ", "")
            for line in result.stdout.split("\n")
            if line.strip()
        ]
        
        if pattern:
            import fnmatch
            branches = [b for b in branches if fnmatch.fnmatch(b, pattern)]
        
        return branches
    
    def switch_branch(self, branch_name: str) -> bool:
        """브랜치 전환"""
        try:
            self._run_git(["checkout", branch_name])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def merge_branch(self, source_branch: str, target_branch: str = "main") -> Dict[str, Any]:
        """
        브랜치 병합
        
        Args:
            source_branch: 소스 브랜치
            target_branch: 타겟 브랜치 (기본: main)
        
        Returns:
            병합 결과
        """
        try:
            # 타겟 브랜치로 전환
            self._run_git(["checkout", target_branch])
            
            # 병합
            result = self._run_git(["merge", source_branch, "--no-ff"])
            
            return {
                "success": True,
                "message": f"{source_branch}가 {target_branch}에 병합되었습니다.",
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": "병합 실패",
                "error": e.stderr
            }
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """브랜치 삭제"""
        try:
            flag = "-D" if force else "-d"
            self._run_git(["branch", flag, branch_name])
            return True
        except subprocess.CalledProcessError:
            return False
    
    # ==================== 커밋 관리 ====================
    
    def commit_scene(self, 
                    scene_id: str, 
                    action: str,
                    description: Optional[str] = None,
                    ai_generated: bool = False) -> str:
        """
        장면 변경사항 커밋
        
        Args:
            scene_id: 장면 ID
            action: 액션 (create, edit, enhance, fix)
            description: 추가 설명
            ai_generated: AI 생성 여부
        
        Returns:
            커밋 해시
        """
        # 스테이징
        self._run_git(["add", "."])
        
        # 커밋 메시지 생성
        prefix = "ai" if ai_generated else "feat"
        message = f"{prefix}(scene): {action} {scene_id}"
        
        if description:
            message += f"\n\n{description}"
        
        if ai_generated:
            message += "\n\n[AI Generated]"
        
        # 커밋
        result = self._run_git(["commit", "-m", message])
        
        # 커밋 해시 가져오기
        hash_result = self._run_git(["rev-parse", "HEAD"])
        return hash_result.stdout.strip()[:8]
    
    def commit_with_evaluation(self,
                              scene_id: str,
                              action: str,
                              evaluation: Dict[str, Any]) -> str:
        """
        평가 정보가 포함된 커밋
        
        커밋 메시지에 평가 점수를 포함합니다.
        """
        self._run_git(["add", "."])
        
        # 평가 정보 포맷팅
        eval_info = []
        if "overall_score" in evaluation:
            eval_info.append(f"Overall: {evaluation['overall_score']:.2f}")
        if "creativity_score" in evaluation:
            eval_info.append(f"Creativity: {evaluation['creativity_score']:.2f}")
        if evaluation.get("cliche_detected"):
            eval_info.append("Cliche: detected")
        
        message = f"feat(scene): {action} {scene_id}"
        if eval_info:
            message += f"\n\n평가: {', '.join(eval_info)}"
        
        self._run_git(["commit", "-m", message])
        
        hash_result = self._run_git(["rev-parse", "HEAD"])
        return hash_result.stdout.strip()[:8]
    
    def get_commit_history(self, file_path: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        커밋 히스토리 조회
        
        Args:
            file_path: 특정 파일 경로 (선택)
            limit: 조회할 커밋 수
        
        Returns:
            커밋 목록
        """
        args = [
            "log",
            f"-{limit}",
            "--pretty=format:%H|%h|%an|%ad|%s",
            "--date=short"
        ]
        
        if file_path:
            args.append("--")
            args.append(file_path)
        
        result = self._run_git(args)
        
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "short_hash": parts[1],
                        "author": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
        
        return commits
    
    # ==================== 버전 비교 ====================
    
    def diff_versions(self, 
                     commit1: str, 
                     commit2: str, 
                     file_path: Optional[str] = None) -> str:
        """
        두 버전 간 차이 비교
        
        Args:
            commit1: 첫 번째 커밋
            commit2: 두 번째 커밋
            file_path: 비교할 파일 경로
        
        Returns:
            diff 결과
        """
        args = ["diff", commit1, commit2]
        
        if file_path:
            args.append("--")
            args.append(file_path)
        
        result = self._run_git(args, check=False)
        return result.stdout
    
    def get_file_at_version(self, commit: str, file_path: str) -> Optional[str]:
        """
        특정 버전의 파일 내용 조회
        
        Args:
            commit: 커밋 해시
            file_path: 파일 경로
        
        Returns:
            파일 내용
        """
        try:
            result = self._run_git(["show", f"{commit}:{file_path}"])
            return result.stdout
        except subprocess.CalledProcessError:
            return None
    
    # ==================== 워크플로우 ====================
    
    def start_writing_session(self, project_name: str) -> Dict[str, Any]:
        """
        작성 세션 시작
        
        새 브랜치를 만들고 작업을 시작합니다.
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        branch_name = f"session/{project_name}_{timestamp}"
        
        # 현재 브랜치 저장
        current_branch = self.get_current_branch()
        
        # 새 브랜치 생성
        self._run_git(["checkout", "-b", branch_name])
        
        return {
            "session_branch": branch_name,
            "previous_branch": current_branch,
            "started_at": datetime.now().isoformat()
        }
    
    def end_writing_session(self, 
                           session_branch: str,
                           merge_to_main: bool = False,
                           delete_branch: bool = False) -> Dict[str, Any]:
        """
        작성 세션 종료
        
        Args:
            session_branch: 세션 브랜치 이름
            merge_to_main: main에 병합 여부
            delete_branch: 브랜치 삭제 여부
        """
        result = {
            "session_branch": session_branch,
            "ended_at": datetime.now().isoformat()
        }
        
        if merge_to_main:
            merge_result = self.merge_branch(session_branch, "main")
            result["merged"] = merge_result["success"]
            
            if merge_result["success"] and delete_branch:
                self.delete_branch(session_branch)
                result["branch_deleted"] = True
        
        return result
    
    def push_to_remote(self, branch_name: Optional[str] = None) -> Dict[str, Any]:
        """원격 저장소에 푸시"""
        try:
            if branch_name:
                self._run_git(["push", "-u", "origin", branch_name])
            else:
                self._run_git(["push"])
            
            return {"success": True, "message": "푸시 완료"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}
    
    def pull_from_remote(self) -> Dict[str, Any]:
        """원격 저장소에서 풀"""
        try:
            self._run_git(["pull"])
            return {"success": True, "message": "풀 완료"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}
    
    # ==================== 유틸리티 ====================
    
    def get_status(self) -> Dict[str, Any]:
        """저장소 상태 조회"""
        status_result = self._run_git(["status", "--porcelain"])
        
        changes = []
        for line in status_result.stdout.strip().split("\n"):
            if line:
                status = line[:2].strip()
                filename = line[3:]
                changes.append({
                    "status": status,
                    "file": filename
                })
        
        return {
            "current_branch": self.get_current_branch(),
            "changes": changes,
            "has_changes": len(changes) > 0
        }
    
    def stash_changes(self, message: Optional[str] = None) -> bool:
        """변경사항 임시 저장"""
        try:
            args = ["stash"]
            if message:
                args.extend(["push", "-m", message])
            self._run_git(args)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def apply_stash(self, pop: bool = True) -> bool:
        """임시 저장 적용"""
        try:
            action = "pop" if pop else "apply"
            self._run_git(["stash", action])
            return True
        except subprocess.CalledProcessError:
            return False


def quick_commit(message: str, push: bool = False) -> Dict[str, Any]:
    """
    빠른 커밋 헬퍼 함수
    
    Args:
        message: 커밋 메시지
        push: 푸시 여부
    
    Returns:
        커밋 결과
    """
    manager = GitManager()
    
    result = {"message": message}
    
    try:
        manager._run_git(["add", "."])
        manager._run_git(["commit", "-m", message])
        
        hash_result = manager._run_git(["rev-parse", "HEAD"])
        result["commit_hash"] = hash_result.stdout.strip()[:8]
        result["success"] = True
        
        if push:
            push_result = manager.push_to_remote()
            result["pushed"] = push_result["success"]
    except subprocess.CalledProcessError as e:
        result["success"] = False
        result["error"] = e.stderr
    
    return result

