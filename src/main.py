from fastapi import FastAPI, HTTPException
import logging
import os
import pika
import json
import random 
import redis  

from src.database import engine, Base
from src.recommendation import get_popular_items, get_cf_recommendation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OptiServe A/B Test API", description="메시지 큐 및 MAB(톰슨 샘플링) 적용 API")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# 실시간 통계 기록을 위한 Redis 연결
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def send_log_to_queue(user_id: str, ab_group: str, item_name: str, action_type: str):
    """메시지 큐(RabbitMQ)로 로그 데이터를 즉시 전송합니다."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='log_queue', durable=True)
        
        log_data = {"user_id": user_id, "ab_group": ab_group, "item_name": item_name, "action_type": action_type}
        
        channel.basic_publish(
            exchange='', routing_key='log_queue', body=json.dumps(log_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        logger.error(f"[RabbitMQ 오류] 큐 전송 실패: {e}")

# 5:5 고정 분배가 아닌, 실시간 MAB(톰슨 샘플링) 기반 분배 함수
def get_mab_group() -> str:
    try:
        # 1. Redis에서 A군과 B군의 실시간 노출(imp) 및 클릭(clk) 횟수 조회
        imp_a = int(redis_client.get("mab:imp:A") or 0)
        clk_a = int(redis_client.get("mab:clk:A") or 0)
        imp_b = int(redis_client.get("mab:imp:B") or 0)
        clk_b = int(redis_client.get("mab:clk:B") or 0)
    except redis.ConnectionError:
        # Redis 장애 시 기본 5:5 무작위 분배 (안전 장치)
        return random.choice(["A", "B"])

    # 2. 톰슨 샘플링 계산 (베타 분포 활용)
    # 성공(클릭) + 1, 실패(노출 - 클릭) + 1 을 기준으로 확률값 생성
    score_a = random.betavariate(clk_a + 1, (imp_a - clk_a) + 1)
    score_b = random.betavariate(clk_b + 1, (imp_b - clk_b) + 1)

    # 3. 더 높은 확률 점수를 받은 집단을 선택
    return "A" if score_a >= score_b else "B"

@app.get("/recommend")
def get_recommendation(user_id: str):
    try:
        if not user_id or user_id.strip() == "":
            raise HTTPException(status_code=400, detail="유효하지 않은 사용자 ID 입니다.")
        
        group = get_mab_group()
        
        if group == "A":
            items = get_popular_items(n=3)
            model_name = "인기도 기반 모델 (Popularity)"
        else:
            items = get_cf_recommendation(user_id, n=3)
            model_name = "협업 필터링 모델 (CF)"
            
        try:
            redis_client.incr(f"mab:imp:{group}")
        except:
            pass

        for item in items:
            send_log_to_queue(user_id, group, item, "impression")

        return {"user_id": user_id, "ab_group": group, "model_used": model_name, "recommended_items": items}
    except Exception as e:
        logger.error(f"추천 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@app.post("/click")
def log_click(user_id: str, item_name: str, group: str):
    if not item_name:
        raise HTTPException(status_code=400, detail="상품명이 없습니다.")
        
    try:
        redis_client.incr(f"mab:clk:{group}")
    except:
        pass

    send_log_to_queue(user_id, group, item_name, "click")
    return {"message": "클릭이 접수되었습니다.", "item": item_name}