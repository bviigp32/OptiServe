# OptiServe: A/B Testing & Recommendation Engine Backend

> **"데이터 기반 의사결정을 위한 A/B 테스트 및 추천 시스템 백엔드 아키텍처"**
> 머신러닝 기반의 추천 알고리즘을 서빙하고, 사용자 트래픽을 A/B 그룹으로 분산(Routing)시켜 CTR(클릭률) 성과를 통계적으로 검증하는 Full-Cycle 데이터/백엔드 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![Scikit-Learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?logo=scikit-learn) ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)

## 프로젝트 개요 (Overview)
* **목표:** 머신러닝 추천 모델의 성능을 비즈니스 지표(클릭률)로 검증하기 위한 A/B 테스트 인프라 구축.
* **기간:** 2026.02.22 ~ (진행 중)
* **역할:** ML 추천 알고리즘 구현, 백엔드 API 서빙, 로깅 파이프라인, A/B 테스트 통계 분석 대시보드 개발 (1인 프로젝트)

## 시스템 아키텍처 (System Architecture)
1. **Routing (API):** MD5 Hashing을 통해 유저 트래픽을 일관된 A군(대조군) / B군(실험군)으로 50:50 분산.
2. **Serving (ML):** - **Model A (대조군):** DB 클릭 로그를 집계한 **인기도 기반 베스트셀러 추천 (Popularity)**
   - **Model B (실험군):** `Scikit-learn` 코사인 유사도(Cosine Similarity)를 활용한 **유저 기반 협업 필터링 (User-Based CF)**
   - *Cold Start 처리: 클릭 기록이 없는 신규 유저 진입 시 Model A(베스트셀러)로 Fallback 처리.*
3. **Logging (DB):** `SQLAlchemy` ORM으로 Impression/Click 로그 SQLite 실시간 적재.
4. **Analysis & Dashboard:** 카이제곱 검정(Chi-Square Test)을 통한 승리 알고리즘 검증 및 `Streamlit` 실시간 모니터링 환경 제공.

## 개발 로그 (Development Log)
### Phase 1: 라우팅 백엔드 & 로깅 (Backend & Data Pipeline)
* **Day 1~2:** FastAPI 기반 A/B 라우팅 로직 구현 및 SQLAlchemy ORM 로깅(`impression`, `click`) 파이프라인 구축.
### Phase 2: 머신러닝 추천 엔진 (ML Serving)
* **Day 5: 머신러닝 추천 로직 연동** (`src/recommendation.py`)
  * 하드코딩된 모의 데이터를 제거하고 Pandas, Scikit-learn을 활용해 DB 기반 추천 엔진 구현.
  * User-Item 행렬을 구성하여 코사인 유사도 기반 CF 추천 알고리즘 적용 및 Cold Start 방어 로직 추가.
### Phase 3: 통계 분석 및 대시보드 (Analysis Focus)
* **Day 3~4:** 가상 트래픽 시뮬레이터(`src/mock_data.py`), Scipy 카이제곱 가설 검정, Streamlit 실시간 CTR 대시보드(`src/dashboard.py`) 구축.

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend** | **FastAPI, Uvicorn, SQLite** | 비동기 API 서버 및 행동 로그 데이터베이스 |
| **ML / Logic** | **Scikit-learn, Python Hashlib** | 코사인 유사도 기반 CF 모델 구현, 트래픽 해싱 |
| **Analysis** | **Pandas, Scipy, Streamlit** | 통계적 가설 검정(p-value) 및 실시간 대시보드 |

## 실행 방법 (How to Run)
```bash
# 1. 패키지 설치
pip install fastapi uvicorn pydantic sqlalchemy pandas scipy streamlit scikit-learn

# 2. FastAPI 서버 실행 (API 및 로깅용)
uvicorn src.main:app --reload

# 3. [선택] 가상 트래픽 발생
python -m src.mock_data

# 4. 실시간 대시보드 실행
streamlit run src/dashboard.py

```

---

*Created by [Kim Kyunghun]*



