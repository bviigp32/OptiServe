# OptiServe: A/B Testing & Recommendation Engine Backend

> **"데이터 기반 의사결정을 위한 A/B 테스트 및 추천 시스템 백엔드 아키텍처"**
> 단순한 추천 알고리즘 구현을 넘어, 사용자 트래픽을 A/B 그룹으로 분산(Routing)하고, 노출(Impression) 및 클릭(Click) 로그를 적재하여 알고리즘의 비즈니스 성과(CTR)를 통계적으로 검증하는 Full-Cycle 백엔드 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) 

## 프로젝트 개요 (Overview)
* **목표:** 머신러닝 추천 모델의 성능을 비즈니스 지표(클릭률, 구매 전환율)로 검증하기 위한 A/B 테스트 인프라 구축.
* **기간:** 2026.02.22 ~ (진행 중)
* **역할:** 백엔드 API 개발, 로깅 파이프라인 구축, A/B 테스트 통계 분석 (1인 프로젝트)

## 시스템 아키텍처 (System Architecture)
1. **Routing (API):** 유저 요청 인입 시, MD5 Hashing을 통해 유저를 일관된 A군(대조군) 또는 B군(실험군)으로 50:50 분산.
2. **Serving (ML):** 할당된 그룹에 따라 서로 다른 추천 알고리즘(베스트셀러 vs 협업 필터링)의 결과값 반환.
3. **Logging (DB):** 유저에게 노출된 아이템(Impression)과 실제 클릭한 아이템(Click) 로그를 비동기적으로 DB에 적재. *(예정)*
4. **Analysis (Stats):** 적재된 로그를 바탕으로 T-Test 등 통계적 가설 검정을 수행하여 승리자(Winner) 모델 선정. *(예정)*

## 개발 로그 (Development Log)
### Phase 1: 라우팅 백엔드 구축 (Backend Focus)
* **Day 1: FastAPI 초기 세팅 및 A/B 라우팅 구현** (`src/main.py`)
  * `hashlib`을 활용하여 유저 ID 기반의 일관된 A/B 그룹 해싱(Hashing) 로직 구현.
  * 그룹별 가상의 추천 모델(Popularity vs Personalized) 응답 API 분리.

### Phase 2: 데이터 로깅 파이프라인 (Data Pipeline Focus)
* *Coming Soon* (노출/클릭 로그 DB 적재)

### Phase 3: 통계 분석 및 대시보드 (Analysis Focus)
* *Coming Soon* (CTR 계산 및 p-value 검증 대시보드)

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend** | **FastAPI, Uvicorn** | 비동기 기반 고성능 API 서버 구축 |
| **Logic** | Python `hashlib` | 유저 ID 해싱 및 그룹핑 |
| **Database** | *TBD (SQLite/PostgreSQL)* | *유저 로그 및 추천 메타데이터 적재 예정* |
| **Analysis** | *TBD (Scipy, Streamlit)* | *통계적 유의성 검증 및 대시보드 예정* |

## 실행 방법 (How to Run)
```bash
# 1. 가상환경 세팅
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# 2. 필수 라이브러리 설치
pip install fastapi uvicorn pydantic

# 3. FastAPI 서버 실행
uvicorn src.main:app --reload

# 4. API 테스트 (Swagger UI)
# 브라우저에서 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 접속

```

---

*Created by [Kim Kyunghun]*
