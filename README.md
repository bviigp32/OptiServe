# OptiServe: A/B Testing & Recommendation Engine Backend

> **"대규모 트래픽 처리를 고려한 A/B 테스트 및 추천 시스템 백엔드 아키텍처"**
> 머신러닝 추천 모델을 서빙하고, Redis 분산 캐싱과 RabbitMQ 메시지 큐를 도입하여 병목 및 데이터 유실을 완벽히 해결했습니다. 무중단 서빙(Fallback)과 운영용 DB(PostgreSQL), Docker 기반 MSA(Microservices Architecture) 환경을 구축한 엔터프라이즈급 Full-Cycle 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Message%20Queue-FF6600?logo=rabbitmq) ![Redis](https://img.shields.io/badge/Redis-Caching-DC382D?logo=redis) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit) ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?logo=github-actions) ![Locust](https://img.shields.io/badge/Locust-Load%20Testing-42b983?logo=locust)

## 프로젝트 개요 (Overview)
* **목표:** 머신러닝 추천 모델의 성능(CTR)을 검증하기 위한 A/B 테스트 인프라 구축 및 API 성능 최적화.
* **기간:** 2026.02.22 ~ (진행 중)
* **역할:** 백엔드/데이터 엔지니어링 (API 서빙, 분산 캐싱, RabbitMQ 비동기 로깅, RDBMS 마이그레이션, A/B 대시보드)

## 시스템 아키텍처 (System Architecture)
1. **Routing:** `Hashlib(MD5)`을 통해 유저 트래픽을 일관된 A/B 그룹으로 분산.
2. **Serving & Caching (성능 최적화):** 다중 서버 환경(Scale-out)을 고려한 **Redis 기반 분산 인메모리 캐싱** 구축.
3. **Async Logging & Worker (무손실 비동기 아키텍처):** 트래픽 폭증 시 서버 다운으로 인한 데이터 유실(Data Loss)을 방지하기 위해 **RabbitMQ 메시지 큐** 도입. API는 로깅 메시지만 큐에 발행(Publish)하고, 독립된 **Worker 노드**가 이를 소비(Consume)하여 DB에 안전하게 적재하는 Event-Driven 구조 설계.
4. **Resilience & Infrastructure (장애 대응 및 인프라):** * Redis `ConnectionError` 발생 시 즉시 DB 연산으로 우회하는 **Graceful Degradation (Cache Fallback)** 로직 구현. 
   * 대용량 동시 쓰기(Write) 처리를 위해 **PostgreSQL 마이그레이션** 수행.
   * `Docker` / `docker-compose`를 활용한 6개의 멀티 컨테이너(API, Worker, RabbitMQ, Redis, DB, Dashboard) 오케스트레이션.
5. **Analysis & Dashboard:** 카이제곱 검정(Chi-Square Test) 기반 승자 검증 및 `Streamlit` 실시간 대시보드.
6. **CI/CD & Test Automation (자동화/유지보수):** `pytest` 무결성 검증 및 `GitHub Actions` CI 파이프라인 구축.
7. **Performance Optimization (부하 테스트):** `Locust`를 활용하여 1,000명 규모의 VUser 동시 접속 부하 테스트 수행. **평균 응답 속도 1~2ms 최적화 및 에러율(Fail Rate) 0%** 달성.

### 부하 테스트 결과 (Load Testing Results)
![Locust Load Test Result](assets/locust_result.png)

* **테스트 환경:** `Locust`를 활용한 가상 유저(VUser) 1,000명 동시 접속 시나리오
* **테스트 성과:** * 분산 캐싱 및 메시지 큐 기반의 백그라운드 워커 도입으로 DB I/O 및 ML 연산 병목 완벽 해결
  * 최고 초당 처리량(Max RPS): **497.3 req/s** 방어
  * 평균 응답 속도: **1 ms** (95th percentile 기준 **2 ms**) 유지 초고속 서빙 달성
  * **에러율(Fail Rate) 0%** 달성하여 대규모 트래픽 하에서도 무중단 안정적인 API 서빙 능력 검증

## 개발 로그 (Development Log)
* **Phase 1~4:** FastAPI 라우팅, SQLAlchemy ORM, Scikit-learn 협업 필터링 연동 및 Streamlit 대시보드 구축. (Day 1-5)
* **Phase 5~7:** `pytest`/`GitHub Actions` 자동화 및 `Locust` 부하 테스트. (Day 6-10)
* **Phase 8 (캐싱 고도화):** **Redis 분산 캐싱** 도입 및 **Fallback 장애 방어 로직** 구현. (Day 11)
* **Phase 9 (DB 인프라 고도화):** 병목 및 락(Lock) 현상 방지를 위해 **PostgreSQL 마이그레이션** 수행. (Day 12)
* **Phase 10 (비동기 아키텍처 고도화):** 데이터 유실률 0% 달성을 위해 **RabbitMQ 메시지 큐** 및 독립적인 DB Insert **Worker 노드** 구축. (Day 13)

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend & Infra** | **FastAPI, RabbitMQ, Redis** | 비동기 API 서버, 메시지 브로커, 분산 캐싱 저장소 |
| **Database** | **PostgreSQL, SQLAlchemy** | 유저 행동 로그 메타데이터 적재 및 운영용 RDBMS |
| **ML & Logic** | **Scikit-learn** | CF 코사인 유사도 모델 구현 및 추천 로직 |
| **Analysis** | **Pandas, Scipy, Streamlit** | A/B 테스트 통계적 유의성 검증 및 대시보드 시각화 |
| **Infra & CI/CD**| **Docker, GitHub Actions, Pytest, Locust** | 컨테이너(6-Tier) 배포, CI 파이프라인 및 부하 테스트 |

## 실행 방법 (How to Run)
```bash
# Docker 컨테이너로 MSA 인프라(API + Worker + PostgreSQL + Redis + RabbitMQ + 대시보드) 한 번에 실행 
docker-compose up --build -d
```

## 향후 고도화 계획 (Stretch Goals)

* **Kubernetes (K8s) 마이그레이션:** 현재의 Docker Compose 환경을 넘어, 트래픽 폭증 시 API와 Worker 노드를 독립적으로 Auto-Scaling 할 수 있도록 Kubernetes 기반 배포 환경으로 전환 검토.
* **MAB (Multi-Armed Bandit) 도입:** 정적인 50:50 A/B 테스트를 넘어, 실시간 승자 모델로 트래픽을 자동 집중시키는 MAB 알고리즘 고도화.




