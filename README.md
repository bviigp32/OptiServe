# OptiServe: A/B Testing & Recommendation Engine Backend

> **"대규모 트래픽 확장을 고려한 A/B 테스트 및 실시간 최적화 추천 시스템 백엔드"**
> 머신러닝 추천 모델을 서빙하고, Redis 분산 캐싱과 RabbitMQ 메시지 큐를 도입하여 병목 및 데이터 유실을 완벽히 해결했습니다. 이에 더해 실시간 성과 기반의 MAB(Multi-Armed Bandit) 트래픽 분배, 무중단 서빙(Fallback), 운영용 DB(PostgreSQL), 그리고 **Kubernetes(K8s)** 기반의 자동 확장 배포 환경까지 구축한 기업용 수준의 전체 주기(Full-Cycle) 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Message%20Queue-FF6600?logo=rabbitmq) ![Redis](https://img.shields.io/badge/Redis-Caching-DC382D?logo=redis) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit) ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?logo=github-actions) ![Locust](https://img.shields.io/badge/Locust-Load%20Testing-42b983?logo=locust) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5?logo=kubernetes)

## 프로젝트 개요 (Overview)
* **목표:** 머신러닝 추천 모델의 성능(CTR)을 검증하기 위한 A/B 테스트 환경 구축 및 대규모 트래픽 대응 아키텍처 설계.
* **기간:** 2026.02.22 ~ 2026.03.08
* **역할:** 백엔드/데이터 엔지니어링 (API 서빙, 분산 캐싱, 메시지 큐 비동기 저장, RDBMS 변경, 쿠버네티스 인프라 구축, 실시간 MAB 알고리즘 적용, A/B 대시보드)

## 시스템 아키텍처 (System Architecture)
1. **Routing & MAB (실시간 트래픽 최적화):** 단순 무작위 분산을 넘어, 실시간 성과(노출/클릭)를 Redis에 기록하고 이를 바탕으로 성과가 우수한 모델에 접속량을 자동으로 집중시키는 **톰슨 샘플링(Thompson Sampling) 기반 MAB(Multi-Armed Bandit)** 알고리즘 적용.
2. **Serving & Caching (성능 최적화):** 다중 서버 환경(Scale-out)을 고려한 **Redis 기반 분산 메모리 캐싱** 구축.
3. **Async Logging & Worker (무손실 비동기 구조):** 접속 폭증 시 서버 다운으로 인한 데이터 유실 방지를 위해 **RabbitMQ 메시지 큐** 도입. API는 저장할 메시지만 발행(Publish)하고, 독립된 **작업(Worker) 서버**가 이를 소비(Consume)하여 DB에 안전하게 적재하는 사건 기반(Event-Driven) 구조 설계.
4. **Resilience & Infrastructure (장애 대응 및 인프라):** * Redis 연결 오류 발생 시 즉시 DB 연산으로 우회하는 **방어 로직(Graceful Degradation)** 구현. 
   * 대용량 동시 쓰기(Write) 처리를 위해 **PostgreSQL로 데이터베이스 변경** 수행.
   * 단순 컨테이너 묶음을 넘어, 접속량 증가 시 API 서버를 다중으로 복제하고 부하를 분산할 수 있도록 **Kubernetes(K8s)** 환경으로 구조 개선.
5. **Analysis & Dashboard:** 카이제곱 검정(Chi-Square Test) 기반 승자 검증 및 `Streamlit` 실시간 대시보드.
6. **CI/CD & Test Automation (자동화/유지보수):** `pytest` 무결성 검증 및 `GitHub Actions` 자동화 파이프라인 구축.
7. **Performance Optimization (부하 테스트):** `Locust`를 활용하여 1,000명 규모의 가상 사용자 동시 접속 부하 테스트 수행. **평균 응답 속도 1~2ms 최적화 및 오류 발생률 0%** 달성.

### 부하 테스트 결과 (Load Testing Results)
![Locust Load Test Result](assets/locust_result.png)

* **테스트 환경:** `Locust`를 활용한 가상 사용자 1,000명 동시 접속 시나리오
* **테스트 성과:** * 분산 캐싱 및 메시지 큐 기반의 작업 서버 도입으로 DB 접근 및 기계학습 연산 병목 현상 완벽 해결
  * 최고 초당 처리량(Max RPS): **497.3 req/s** 방어
  * 평균 응답 속도: **1 ms** (상위 5% 기준 **2 ms**) 유지하며 초고속 서빙 달성
  * **오류 발생률 0%** 달성하여 대규모 트래픽 하에서도 안정적인 API 서빙 능력 검증

## 개발 로그 (Development Log)
* **Phase 1~4:** FastAPI 라우팅, SQLAlchemy ORM, Scikit-learn 협업 필터링 연동 및 Streamlit 대시보드 구축. (Day 1-5)
* **Phase 5~7:** `pytest`/`GitHub Actions` 자동화 및 `Locust` 부하 테스트. (Day 6-10)
* **Phase 8 (캐싱 고도화):** **Redis 분산 캐싱** 도입 및 **장애 방어 로직** 구현. (Day 11)
* **Phase 9 (DB 인프라 고도화):** 병목 및 잠금(Lock) 현상 방지를 위해 **PostgreSQL 변경** 수행. (Day 12)
* **Phase 10 (비동기 구조 고도화):** 데이터 유실률 0% 달성을 위해 **RabbitMQ 메시지 큐** 및 독립적인 DB 저장 **작업 서버(Worker)** 구축. (Day 13)
* **Phase 11 (인프라 고도화):** 대규모 트래픽 확장을 위한 **Kubernetes(K8s) 변경** 및 설계도(Manifest) 적용. (Day 14)
* **Phase 12 (추천 알고리즘 고도화):** 고정된 A/B 테스트의 한계를 극복하기 위해 실시간 클릭률 기반 트래픽 자동 분배 로직인 **MAB(Multi-Armed Bandit)** 도입 완료. (Day 15)

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend & Infra** | **FastAPI, RabbitMQ, Redis** | 비동기 API 서버, 메시지 브로커, 분산 캐싱 저장소 |
| **Database** | **PostgreSQL, SQLAlchemy** | 사용자 행동 기록 및 운영용 데이터베이스 |
| **ML & Logic** | **Scikit-learn, MAB** | 협업 필터링 모델 구현 및 톰슨 샘플링 기반 접속량 최적화 |
| **Analysis** | **Pandas, Scipy, Streamlit** | A/B 테스트 통계적 유의성 검증 및 대시보드 시각화 |
| **Infra & CI/CD**| **Kubernetes, Docker, GitHub Actions, Locust** | K8s 서버 관리, 자동화 파이프라인 및 부하 테스트 |

## 실행 방법 (How to Run)
```bash
# 1. 단일 서버 도커(Docker) 환경에서 실행 (기본)
docker-compose up --build -d

# 2. 쿠버네티스(Kubernetes) 환경에서 배포 (확장용)
kubectl apply -f k8s/optiserve-k8s.yaml

```
