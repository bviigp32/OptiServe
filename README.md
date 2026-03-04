# OptiServe: A/B Testing & Recommendation Engine Backend

> **"대규모 트래픽 처리를 고려한 A/B 테스트 및 추천 시스템 백엔드 아키텍처"**
> 머신러닝 추천 모델을 서빙하고, Redis 분산 캐싱과 비동기 로깅(Async Logging)을 도입하여 병목을 해결했습니다. 또한 장애 발생 시 무중단 서빙을 보장하는 Fallback 로직과 Docker 배포 환경을 구축한 Full-Cycle 데이터/백엔드 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![Redis](https://img.shields.io/badge/Redis-Caching-DC382D?logo=redis) ![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit) ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?logo=github-actions) ![Locust](https://img.shields.io/badge/Locust-Load%20Testing-42b983?logo=locust)

## 프로젝트 개요 (Overview)
* **목표:** 머신러닝 추천 모델의 성능(CTR)을 검증하기 위한 A/B 테스트 인프라 구축 및 API 성능 최적화.
* **기간:** 2026.02.22 ~ (진행 중)
* **역할:** 백엔드/데이터 엔지니어링 (API 서빙, 비동기 로깅 파이프라인, 분산 캐싱 고도화, ML 모델 연동, A/B 대시보드)

## 시스템 아키텍처 (System Architecture)
1. **Routing:** `Hashlib(MD5)`을 통해 유저 트래픽을 일관된 A/B 그룹으로 분산.
2. **Serving & Caching (성능 최적화):** Model A/B 연동 및 다중 서버 환경(Scale-out)을 고려한 **Redis 기반 분산 인메모리 캐싱** 구축.
3. **Async Logging (병목 해결):** FastAPI `BackgroundTasks`를 활용한 비동기 로깅 및 Python `logging` 기반 서버 모니터링 추적.
4. **Resilience & Infrastructure (장애 대응 및 배포):** Redis `ConnectionError` 발생 시 서버 다운 없이 즉시 DB 연산으로 우회하는 **Graceful Degradation (Cache Fallback)** 로직 구현. `Docker` 및 `docker-compose`를 활용한 컨테이너 오케스트레이션.
5. **Analysis & Dashboard:** 카이제곱 검정(Chi-Square Test) 기반 승자 검증 및 `Streamlit` 실시간 대시보드.
6. **CI/CD & Test Automation (자동화/유지보수):** `pytest` 무결성 검증 및 `GitHub Actions`를 도입한 CI(Continuous Integration) 파이프라인 구축.
7. **Performance Optimization (부하 테스트):** `Locust`를 활용하여 1,000명 규모의 VUser 동시 접속 부하 테스트 수행. **평균 응답 속도 1~2ms 최적화 및 에러율(Fail Rate) 0%** 달성.

### 부하 테스트 결과 (Load Testing Results)
![Locust Load Test Result](assets/locust_result.png)

* **테스트 환경:** `Locust`를 활용한 가상 유저(VUser) 1,000명 동시 접속 시나리오
* **테스트 성과:** * In-Memory 캐싱 및 비동기 백그라운드 태스크 도입으로 DB I/O 및 ML 연산 병목 완벽 해결
  * 최고 초당 처리량(Max RPS): **497.3 req/s** 방어
  * 평균 응답 속도: **1 ms** (95th percentile 기준 **2 ms**) 유지 초고속 서빙 달성
  * **에러율(Fail Rate) 0%** 달성하여 대규모 트래픽 하에서도 무중단 안정적인 API 서빙 능력 검증

## 개발 로그 (Development Log)
* **Phase 1~2:** FastAPI 기반 A/B 라우팅 로직 및 SQLAlchemy ORM 로깅 파이프라인 구축. (Day 1-2)
* **Phase 3~4:** Scikit-learn 기반 협업 필터링(CF) 추천 연동, 가상 트래픽 발생 봇 및 Streamlit A/B 대시보드 구축. (Day 3-5)
* **Phase 5~6:** FastAPI `BackgroundTasks` 비동기 처리, `pytest` 자동 테스트 및 `GitHub Actions` CI 구축. (Day 6-9)
* **Phase 7:** `Locust` 기반 1,000명 대규모 트래픽 시나리오 작성 및 병목 개선 수치화(RPS, Response Time) 검증. (Day 10)
* **Phase 8 (아키텍처 고도화):** 단일 서버 메모리 캐싱(`lru_cache`)의 한계를 극복하기 위해 **Redis 기반 분산 캐싱** 도입 및 Redis 서버 다운 시의 무중단 서빙을 위한 **Fallback 장애 방어 로직** 구현. (Day 11)

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend & Infra** | **FastAPI, BackgroundTasks, Redis** | 비동기 API 서버, Non-blocking 로깅, 분산 캐싱 저장소 |
| **Database** | **SQLite, SQLAlchemy** | 유저 행동 로그 메타데이터 적재 |
| **ML & Logic** | **Scikit-learn** | CF 코사인 유사도 모델 구현 및 추천 로직 |
| **Analysis** | **Pandas, Scipy, Streamlit** | A/B 테스트 통계적 유의성 검증 및 대시보드 시각화 |
| **Infra & CI/CD**| **Docker, GitHub Actions, Pytest, Locust** | 컨테이너 배포, CI 자동화 파이프라인 및 부하 테스트 |

## 실행 방법 (How to Run)
```bash
docker-compose up --build -d
```

## 향후 고도화 계획 (Future Work)

* **메시지 큐(Message Queue) 도입:** 트래픽 폭증 시 서버 재부팅 등의 상황에서 로깅 데이터 유실(Data Loss)을 방지하기 위한 비동기 메시지 브로커(Kafka / RabbitMQ) 도입 검토.
* **운영용 RDBMS 마이그레이션:** 대규모 동시 쓰기(Write) 작업 시 락(Lock) 이슈를 방지하기 위해 파일 기반 SQLite에서 PostgreSQL로의 데이터베이스 마이그레이션 적용.
