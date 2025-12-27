"""
방송 대본 생성 (간단 실행)
"""

import sys
from pathlib import Path

# scripts 폴더의 스크립트 실행
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

# generate_script.py 실행
if __name__ == "__main__":
    import subprocess
    script_path = scripts_dir / "generate_script.py"
    subprocess.run([sys.executable, str(script_path)] + sys.argv[1:])

