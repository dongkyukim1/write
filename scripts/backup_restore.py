"""
백업 및 복원 스크립트
소설 데이터와 체크포인트를 백업/복원합니다.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import zipfile


class BackupManager:
    """백업 관리 클래스"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Args:
            backup_dir: 백업 저장 디렉토리 (기본값: 프로젝트 루트/backups)
        """
        project_root = Path(__file__).parent.parent
        if backup_dir is None:
            backup_dir = project_root / "backups"
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_novel(self, novel_id: str, novels_dir: Optional[Path] = None) -> Path:
        """
        소설 백업
        
        Args:
            novel_id: 소설 ID
            novels_dir: 소설 디렉토리 (기본값: 프로젝트 루트/novels)
        
        Returns:
            백업 파일 경로
        """
        project_root = Path(__file__).parent.parent
        if novels_dir is None:
            novels_dir = project_root / "novels"
        
        novel_path = novels_dir / novel_id
        if not novel_path.exists():
            raise FileNotFoundError(f"소설 '{novel_id}'를 찾을 수 없습니다.")
        
        # 백업 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{novel_id}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        # ZIP 파일로 압축
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in novel_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(novel_path.parent)
                    zipf.write(file_path, arcname)
        
        # 메타데이터 저장
        metadata = {
            "novel_id": novel_id,
            "backup_time": timestamp,
            "backup_date": datetime.now().isoformat(),
            "files_count": len(list(novel_path.rglob('*')))
        }
        
        metadata_path = self.backup_dir / f"{novel_id}_{timestamp}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"백업 완료: {backup_path}")
        print(f"  파일 수: {metadata['files_count']}")
        return backup_path
    
    def restore_novel(self, backup_file: Path, novels_dir: Optional[Path] = None, 
                     overwrite: bool = False) -> Path:
        """
        소설 복원
        
        Args:
            backup_file: 백업 파일 경로
            novels_dir: 복원할 소설 디렉토리 (기본값: 프로젝트 루트/novels)
            overwrite: 기존 파일 덮어쓰기 여부
        
        Returns:
            복원된 소설 경로
        """
        project_root = Path(__file__).parent.parent
        if novels_dir is None:
            novels_dir = project_root / "novels"
        
        if not backup_file.exists():
            raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_file}")
        
        # 임시 디렉토리에 압축 해제
        temp_dir = self.backup_dir / "temp_restore"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # 소설 ID 추출 (첫 번째 디렉토리명)
        extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise ValueError("백업 파일이 올바르지 않습니다.")
        
        novel_id = extracted_dirs[0].name
        restored_path = novels_dir / novel_id
        
        # 기존 파일 확인
        if restored_path.exists() and not overwrite:
            raise FileExistsError(
                f"소설 '{novel_id}'가 이미 존재합니다. "
                "덮어쓰려면 overwrite=True를 사용하세요."
            )
        
        # 복원
        if restored_path.exists():
            shutil.rmtree(restored_path)
        
        shutil.move(str(extracted_dirs[0]), str(restored_path))
        shutil.rmtree(temp_dir)
        
        print(f"복원 완료: {restored_path}")
        return restored_path
    
    def list_backups(self, novel_id: Optional[str] = None) -> list:
        """
        백업 목록 조회
        
        Args:
            novel_id: 특정 소설의 백업만 조회 (선택사항)
        
        Returns:
            백업 파일 목록
        """
        backups = []
        for file_path in self.backup_dir.glob("*.zip"):
            if novel_id and novel_id not in file_path.name:
                continue
            
            # 메타데이터 파일 찾기
            metadata_path = file_path.with_suffix('.json').with_name(
                file_path.stem.replace('.zip', '') + '_metadata.json'
            )
            
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            backups.append({
                "file": file_path,
                "metadata": metadata,
                "size": file_path.stat().st_size
            })
        
        # 날짜순 정렬 (최신순)
        backups.sort(key=lambda x: x["metadata"].get("backup_date", ""), reverse=True)
        return backups


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='소설 백업/복원 도구')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], help='작업 선택')
    parser.add_argument('--novel-id', help='소설 ID')
    parser.add_argument('--backup-file', type=Path, help='백업 파일 경로 (restore 시 필요)')
    parser.add_argument('--overwrite', action='store_true', help='덮어쓰기 (restore 시)')
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.action == 'backup':
        if not args.novel_id:
            print("오류: --novel-id가 필요합니다.")
            return
        manager.backup_novel(args.novel_id)
    
    elif args.action == 'restore':
        if not args.backup_file:
            print("오류: --backup-file이 필요합니다.")
            return
        manager.restore_novel(args.backup_file, overwrite=args.overwrite)
    
    elif args.action == 'list':
        backups = manager.list_backups(args.novel_id)
        if not backups:
            print("백업이 없습니다.")
        else:
            print(f"\n총 {len(backups)}개의 백업:")
            for backup in backups:
                metadata = backup["metadata"]
                size_mb = backup["size"] / (1024 * 1024)
                print(f"\n  파일: {backup['file'].name}")
                print(f"  소설 ID: {metadata.get('novel_id', 'N/A')}")
                print(f"  백업 시간: {metadata.get('backup_date', 'N/A')}")
                print(f"  크기: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()

