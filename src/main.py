from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import hashlib
from src.database import SessionLocal, engine, Base, UserLog
from src.recommendation import get_popular_items, get_cf_recommendation

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OptiServe A/B Test API", description="추천 시스템 로깅 및 ML A/B 테스트 백엔드")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ab_group(user_id: str) -> str:
    hash_val = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16)
    return "A" if hash_val % 2 == 0 else "B"

@app.get("/recommend")
def get_recommendation(user_id: str, db: Session = Depends(get_db)):
    """상품을 추천해주고, '노출(impression)' 로그를 DB에 저장합니다."""
    group = get_ab_group(user_id)
    
    if group == "A":
        items = get_popular_items(n=3)
        model_name = "Popularity_Model (BestSeller)"
    else:
        items = get_cf_recommendation(user_id, n=3)
        model_name = "Collaborative_Filtering_Model (Personalized)"
        
    for item in items:
        new_log = UserLog(user_id=user_id, ab_group=group, item_name=item, action_type="impression")
        db.add(new_log)
    db.commit()

    return {
        "user_id": user_id,
        "ab_group": group,
        "model_used": model_name,
        "recommended_items": items
    }

@app.post("/click")
def log_click(user_id: str, item_name: str, db: Session = Depends(get_db)):
    """클릭 로그를 저장합니다."""
    group = get_ab_group(user_id)
    new_log = UserLog(user_id=user_id, ab_group=group, item_name=item_name, action_type="click")
    db.add(new_log)
    db.commit()
    return {"message": "클릭 로그 성공적 저장", "item": item_name}