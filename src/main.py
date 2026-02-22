from fastapi import FastAPI
import hashlib

app = FastAPI(title="OptiServe A/B Test API", description="추천 시스템 A/B 테스트 라우팅 백엔드")

def get_ab_group(user_id: str) -> str:
    """
    유저 ID를 해싱하여 A군(50%) 또는 B군(50%)으로 일관되게 할당합니다.
    """
    # 유저 ID를 MD5 해시로 변환한 후 정수로 바꿈
    hash_val = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16)
    
    # 짝수면 A군, 홀수면 B군 (정확히 50:50으로 분산됨)
    if hash_val % 2 == 0:
        return "A"
    else:
        return "B"

# 가상의 추천 모델 (나중에는 실제 ML 로직으로 교체될 예정)
def get_recommendation_model_A():
    return ["맥북 프로", "아이폰 15", "에어팟 프로"] # 베스트셀러 (대조군)

def get_recommendation_model_B(user_id: str):
    return ["파이썬 코딩의 기술", "데이터 분석 실무", "FastAPI 바이블"] # 개인화 추천 (실험군)

@app.get("/")
def read_root():
    return {"message": "OptiServe API 서버가 정상 작동 중입니다."}

@app.get("/recommend")
def get_recommendation(user_id: str):
    """
    유저 ID를 받아 A/B 그룹을 판별하고, 해당 그룹의 추천 로직을 실행합니다.
    """
    # 1. A/B 그룹 판별
    group = get_ab_group(user_id)
    
    # 2. 그룹에 맞는 알고리즘 호출
    if group == "A":
        items = get_recommendation_model_A()
        model_name = "Popularity_Model"
    else:
        items = get_recommendation_model_B(user_id)
        model_name = "Personalized_CF_Model"
        
    # 3. 결과 및 로그용 메타데이터 반환
    return {
        "user_id": user_id,
        "ab_group": group,
        "model_used": model_name,
        "recommended_items": items
    }