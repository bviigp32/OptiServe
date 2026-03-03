from locust import HttpUser, task, between
import random

class OptiServeUser(HttpUser):
    # 유저가 API를 한 번 호출하고 다음 호출까지 기다리는 시간 (1~3초 랜덤)
    wait_time = between(1, 3)

    @task(3) # 가중치 3: 추천 API를 더 자주 호출함 (보통 조회 트래픽이 훨씬 많음)
    def get_recommendation(self):
        # 1부터 1000 사이의 랜덤 유저 ID 생성 (캐싱 효과를 확인하기 위함)
        user_id = f"test_user_{random.randint(1, 1000)}"
        
        # /recommend API GET 요청 (이름표 달기: name="/recommend")
        self.client.get(f"/recommend?user_id={user_id}", name="/recommend")

    @task(1) # 가중치 1: 클릭 API 호출 (조회 후 간헐적으로 클릭 발생)
    def click_item(self):
        user_id = f"test_user_{random.randint(1, 1000)}"
        items = ["맥북 프로", "아이폰 15", "에어팟 프로", "파이썬 코딩의 기술", "데이터 분석 실무"]
        item_name = random.choice(items)
        
        # /click API POST 요청
        self.client.post(f"/click?user_id={user_id}&item_name={item_name}", name="/click")