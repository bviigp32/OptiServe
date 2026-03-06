import pika
import json
import os
import time
import logging
from src.database import SessionLocal, UserLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def callback(ch, method, properties, body):
    """RabbitMQ에서 메시지를 받으면 실행되는 함수"""
    data = json.loads(body)
    db = SessionLocal()
    try:
        new_log = UserLog(
            user_id=data['user_id'], 
            ab_group=data['ab_group'], 
            item_name=data['item_name'], 
            action_type=data['action_type']
        )
        db.add(new_log)
        db.commit()
        logger.info(f"[Worker Success] {data['action_type'].upper()} 로그 DB 저장 완료: {data['user_id']}")
    except Exception as e:
        logger.error(f"[Worker Error] DB 저장 실패: {e}")
        db.rollback()
    finally:
        db.close()

def start_worker():
    """RabbitMQ 서버에 연결하고 대기합니다."""
    # RabbitMQ 서버가 켜질 때까지 약간의 대기 시간 부여
    time.sleep(10) 
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # 'log_queue'라는 이름의 우체통(Queue) 생성
    channel.queue_declare(queue='log_queue', durable=True)

    # 우체통에서 편지를 꺼내 callback 함수로 전달
    channel.basic_consume(queue='log_queue', on_message_callback=callback, auto_ack=True)

    logger.info("Worker 가동 시작! RabbitMQ에서 로그를 기다리는 중...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()