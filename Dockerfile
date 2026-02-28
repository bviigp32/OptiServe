# 파이썬 3.11 환경 사용
FROM python:3.11-slim

# 작업 폴더 지정
WORKDIR /app

# 필요한 패키지 설치를 위해 요구사항 파일 복사
# (터미널에서 pip freeze > requirements.txt 로 파일을 먼저 만들어두면 좋습니다)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 코드 전체 복사
COPY . .

# FastAPI 서버 포트 열기
EXPOSE 8000
EXPOSE 8501

# 기본 실행 명령어 (FastAPI 실행)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]