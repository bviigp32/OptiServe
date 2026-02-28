from fastapi import FastAPI, BackgroundTasks, HTTPException
import hashlib
import logging 

from src.database import SessionLocal, engine, Base, UserLog
from src.recommendation import get_popular_items, get_cf_recommendation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OptiServe A/B Test API", description="대규모 트래픽 및 무중단 배포를 고려한 최적화 API")

def get_ab_group(user_id: str) -> str:
    if not user_id or user_id.strip() == "":
        raise HTTPException(status_code=400, detail="유효하지 않은 user_id 입니다.") 
    hash_val = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16)
    return "A" if hash_val % 2 == 0 else "B"

def write_log_to_db_background(user_id: str, ab_group: str, item_name: str, action_type: str):
    db = SessionLocal()
    try:
        new_log = UserLog(user_id=user_id, ab_group=ab_group, item_name=item_name, action_type=action_type)
        db.add(new_log)
        db.commit()
        logger.info(f"[DB Log Success] {action_type.upper()} 이벤트 저장 완료 (User: {user_id})")
    except Exception as e:
        logger.error(f"[DB Log Error] 저장 실패: {str(e)}") 
    finally:
        db.close()

@app.get("/recommend")
def get_recommendation(user_id: str, background_tasks: BackgroundTasks):
    try:
        group = get_ab_group(user_id)
        
        if group == "A":
            items = get_popular_items(n=3)
            model_name = "Popularity_Model (Cached)"
        else:
            items = get_cf_recommendation(user_id, n=3)
            model_name = "Collaborative_Filtering_Model (Cached)"
            
        for item in items:
            background_tasks.add_task(write_log_to_db_background, user_id, group, item, "impression")

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
def log_click(user_id: str, item_name: str, background_tasks: BackgroundTasks):
    if not item_name:
        raise HTTPException(status_code=400, detail="클릭한 상품명(item_name)이 없습니다.")
        
    group = get_ab_group(user_id)
    background_tasks.add_task(write_log_to_db_background, user_id, group, item_name, "click")
    return {"message": "클릭 이벤트가 성공적으로 접수되었습니다. (백그라운드 처리 중)", "item": item_name}