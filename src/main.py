from fastapi import FastAPI, BackgroundTasks # 🌟 백그라운드 태스크 추가
import hashlib

from src.database import SessionLocal, engine, Base, UserLog
from src.recommendation import get_popular_items, get_cf_recommendation

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OptiServe A/B Test API", description="대규모 트래픽을 고려한 비동기 로깅 및 캐싱 API")

def get_ab_group(user_id: str) -> str:
    hash_val = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16)
    return "A" if hash_val % 2 == 0 else "B"

def write_log_to_db_background(user_id: str, ab_group: str, item_name: str, action_type: str):
    """API 응답 후, 백그라운드에서 조용히 실행되는 DB 저장 로직"""
    db = SessionLocal() # 백그라운드 전용 독립 DB 세션 생성
    try:
        new_log = UserLog(user_id=user_id, ab_group=ab_group, item_name=item_name, action_type=action_type)
        db.add(new_log)
        db.commit()
    finally:
        db.close()

@app.get("/recommend")
def get_recommendation(user_id: str, background_tasks: BackgroundTasks):
    group = get_ab_group(user_id)
    
    if group == "A":
        items = get_popular_items(n=3)
        model_name = "Popularity_Model (Cached)"
    else:
        items = get_cf_recommendation(user_id, n=3)
        model_name = "Collaborative_Filtering_Model (Cached)"
        
    for item in items:
        background_tasks.add_task(write_log_to_db_background, user_id, group, item, "impression")

    # 유저에게는 초고속으로 즉시 응답 반환
    return {
        "user_id": user_id,
        "ab_group": group,
        "model_used": model_name,
        "recommended_items": items
    }

@app.post("/click")
def log_click(user_id: str, item_name: str, background_tasks: BackgroundTasks):
    group = get_ab_group(user_id)
    
    background_tasks.add_task(write_log_to_db_background, user_id, group, item_name, "click")
    
    return {"message": "클릭 이벤트가 성공적으로 접수되었습니다. (백그라운드 처리 중)", "item": item_name}