# 실행 방법 가이드

**비전공자도 쉽게 사용할 수 있는** 실행 방법입니다.

## 🚀 간단한 실행 방법

### 방법 1: 루트 폴더에서 실행 (가장 쉬움)

프로젝트 루트(`c:\write\`)에서:

```bash
# 방송 대본 생성
python create_script.py

# 장편 소설 생성
python create_novel.py
```

### 방법 2: scripts 폴더에서 실행

```bash
# scripts 폴더로 이동
cd scripts

# 방송 대본 생성
python generate_script.py

# 장편 소설 생성
python long_form_novel_generator.py
```

### 방법 3: 전체 경로로 실행

```bash
python scripts/generate_script.py
python scripts/long_form_novel_generator.py
```

## 📋 주요 스크립트 위치

| 기능 | 파일 위치 | 간단 실행 |
|------|----------|----------|
| 방송 대본 생성 | `scripts/generate_script.py` | `python create_script.py` |
| 장편 소설 생성 | `scripts/long_form_novel_generator.py` | `python create_novel.py` |
| 간단한 생성 | `scripts/simple_generate.py` | `python scripts/simple_generate.py` |
| 배치 생성 | `scripts/batch_generate.py` | `python scripts/batch_generate.py` |
| 백업 | `scripts/backup_restore.py` | `python scripts/backup_restore.py` |
| 분석 | `scripts/analyze_novel.py` | `python scripts/analyze_novel.py` |

## 💡 팁

**현재 위치 확인:**
```bash
cd
```

**프로젝트 루트로 이동:**
```bash
cd c:\write
```

**파일 목록 확인:**
```bash
dir
# 또는
ls
```

## ❓ 문제 해결

**"파일을 찾을 수 없습니다" 오류:**
- 현재 위치 확인: `cd`
- 프로젝트 루트로 이동: `cd c:\write`
- 다시 실행

**"모듈을 찾을 수 없습니다" 오류:**
- `pip install -r requirements.txt` 실행

