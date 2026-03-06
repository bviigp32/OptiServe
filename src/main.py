from fastapi import FastAPI, HTTPException
import hashlib
import logging
import os
import pika
import json

from src.database import engine, Base
from src.recommendation import get_popular_items, get_cf_recommendation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OptiServe A/B Test API", description="메시지 큐(RabbitMQ) 기반 무손실 비동기 로깅 API")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def send_log_to_queue(user_id: str, ab_group: str, item_name: str, action_type: str):
    """DB를 거치지 않고 RabbitMQ(메시지 큐)로 로그 데이터를 즉시 전송합니다."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='log_queue', durable=True)
        
        log_data = {
            "user_id": user_id,
            "ab_group": ab_group,
            "item_name": item_name,
            "action_type": action_type
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='log_queue',
            body=json.dumps(log_data),
            properties=pika.BasicProperties(delivery_mode=2) # 메시지 영구 저장 설정
        )
        connection.close()
    except Exception as e:
        logger.error(f"[RabbitMQ Error] 큐 전송 실패: {e}")

def get_ab_group(user_id: str) -> str:
    if not user_id or user_id.strip() == "":
        raise HTTPException(status_code=400, detail="유효하지 않은 user_id 입니다.")
    hash_val = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16)
    return "A" if hash_val % 2 == 0 else "B"

@app.get("/recommend")
def get_recommendation(user_id: str):
    try:
        group = get_ab_group(user_id)
        
        if group == "A":
            items = get_popular_items(n=3)
            model_name = "Popularity_Model (Cached)"
        else:
            items = get_cf_recommendation(user_id, n=3)
            model_name = "Collaborative_Filtering_Model (Cached)"
            
        for item in items:
            send_log_to_queue(user_id, group, item, "impression")

        return {
            "user_id": user_id,
            "ab_group": group,
            "model_used": model_name,
            "recommended_items": items
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"추천 로직 에러: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부에서 추천 로직을 처리하는 중 문제가 발생했습니다.")

@app.post("/click")
def log_click(user_id: str, item_name: str):
    if not item_name:
        raise HTTPException(status_code=400, detail="클릭한 상품명(item_name)이 없습니다.")
        
    group = get_ab_group(user_id)
    
    send_log_to_queue(user_id, group, item_name, "click")
    return {"message": "클릭 이벤트가 성공적으로 큐에 접수되었습니다.", "item": item_name}