from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import hashlib

# 방금 만든 database.py에서 DB 설정 불러오기
from src.database import SessionLocal, engine, Base, UserLog

# DB 테이블 자동 생성 (optiserve.db 파일이 만들어짐)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OptiServe A/B Test API", description="추천 시스템 로깅 및 A/B 테스트 백엔드")

# DB 세션을 열고 닫는 함수 (FastAPI 의존성 주입용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- (어제 만든 해시 & 추천 로직 그대로) ---
def get_ab_group(user_id: str) -> str:
    hash_val = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16)
    return "A" if hash_val % 2 == 0 else "B"

def get_recommendation_model_A():
    return ["맥북 프로", "아이폰 15", "에어팟 프로"]

def get_recommendation_model_B(user_id: str):
    return ["파이썬 코딩의 기술", "데이터 분석 실무", "FastAPI 바이블"]
# ------------------------------------------

@app.get("/recommend")
def get_recommendation(user_id: str, db: Session = Depends(get_db)):
    """상품을 추천해주고, '노출(impression)' 로그를 DB에 저장합니다."""
    group = get_ab_group(user_id)
    
    if group == "A":
        items = get_recommendation_model_A()
        model_name = "Popularity_Model"
    else:
        items = get_recommendation_model_B(user_id)
        model_name = "Personalized_CF_Model"
        
    # 추가된 부분: 추천해준 아이템들을 DB에 '노출(impression)'로 기록
    for item in items:
        new_log = UserLog(
            user_id=user_id, 
            ab_group=group, 
            item_name=item, 
            action_type="impression"
        )
        db.add(new_log)
    db.commit() # DB에 확정 저장

    return {
        "user_id": user_id,
        "ab_group": group,
        "model_used": model_name,
        "recommended_items": items
    }

@app.post("/click")
def log_click(user_id: str, item_name: str, db: Session = Depends(get_db)):
    """유저가 상품을 클릭했을 때 호출되어 '클릭(click)' 로그를 DB에 저장합니다."""
    group = get_ab_group(user_id)
    
    # 추가된 부분: 클릭한 아이템을 DB에 '클릭(click)'으로 기록
    new_log = UserLog(
        user_id=user_id, 
        ab_group=group, 
        item_name=item_name, 
        action_type="click"
    )
    db.add(new_log)
    db.commit()

    return {"message": "클릭 로그가 성공적으로 저장되었습니다.", "item": item_name}