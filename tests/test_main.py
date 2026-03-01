from fastapi.testclient import TestClient
from src.main import app, get_ab_group

# FastAPI가 제공하는 가상 테스트 클라이언트
client = TestClient(app)

def test_ab_group_hashing():
    """A/B 테스트 라우팅 해시 함수가 일관되게 작동하는지 검증합니다."""
    # 1. 동일한 유저는 항상 같은 그룹이어야 함
    assert get_ab_group("test_user_1") == get_ab_group("test_user_1")
    
    # 2. 빈 문자열이 들어가면 방어 로직(HTTPException)이 터지는지 검증
    try:
        get_ab_group("")
    except Exception as e:
        assert e.status_code == 400

def test_recommend_api():
    """/recommend API가 정상(200 OK) 응답을 하고, 필수 키값을 포함하는지 검증합니다."""
    response = client.get("/recommend?user_id=test_user_alpha")
    
    # HTTP 상태 코드가 200(정상)인지 확인
    assert response.status_code == 200
    
    # 응답 데이터(JSON) 검증
    data = response.json()
    assert "user_id" in data
    assert "ab_group" in data
    assert "model_used" in data
    assert "recommended_items" in data
    
    # 추천 아이템이 3개 반환되는지 확인
    assert len(data["recommended_items"]) == 3

def test_click_api():
    """/click API가 정상(200 OK) 응답을 하는지 검증합니다."""
    response = client.post("/click?user_id=test_user_alpha&item_name=맥북")
    
    assert response.status_code == 200
    assert response.json()["item"] == "맥북"