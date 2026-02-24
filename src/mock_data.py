import uuid
import random
from src.database import SessionLocal, UserLog, Base, engine
from src.main import get_ab_group

# DB 테이블 생성 확인
Base.metadata.create_all(bind=engine)

def generate_mock_traffic(num_users=2000):
    """2000명의 가상 유저가 접속해서 상품을 보고 클릭하는 상황을 시뮬레이션합니다."""
    db = SessionLocal()
    
    print(f"{num_users}명의 가상 유저 트래픽을 생성 중입니다...")
    
    for _ in range(num_users):
        # 1. 랜덤 유저 ID 생성
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        group = get_ab_group(user_id)
        
        # 2. 노출(Impression) 로그 3개씩 생성
        items = ["아이템1", "아이템2", "아이템3"]
        for item in items:
            imp_log = UserLog(user_id=user_id, ab_group=group, item_name=item, action_type="impression")
            db.add(imp_log)
        
        # 3. 클릭(Click) 시뮬레이션 (의도된 확률 적용)
        # 그룹 A(베스트셀러)는 5% 확률로 클릭, 그룹 B(개인화)는 8% 확률로 클릭
        click_prob = 0.05 if group == "A" else 0.08
        
        for item in items:
            if random.random() < click_prob:
                click_log = UserLog(user_id=user_id, ab_group=group, item_name=item, action_type="click")
                db.add(click_log)
                
    db.commit()
    db.close()
    print("데이터 생성 완료! DB를 확인하세요.")

if __name__ == "__main__":
    generate_mock_traffic()