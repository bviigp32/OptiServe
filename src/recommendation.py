import pandas as pd
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
import redis
import logging

logger = logging.getLogger(__name__)
DB_PATH = "optiserve.db"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def get_popular_items(n=3):
    """[Model A: 인기도 기반 추천] (Redis 캐싱 + Fallback 적용)"""
    cache_key = f"popular_items:{n}"
    
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except redis.ConnectionError:
        logger.warning("[Cache Miss] Redis 연결 실패! 기본 DB 연산으로 우회합니다.")
        pass 

    if not os.path.exists(DB_PATH):
        return ["베스트셀러_A", "베스트셀러_B", "베스트셀러_C"]

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT item_name, COUNT(*) as click_count 
        FROM user_logs 
        WHERE action_type='click' 
        GROUP BY item_name 
        ORDER BY click_count DESC 
        LIMIT ?
    """
    df = pd.read_sql(query, conn, params=(n,))
    conn.close()

    result = ["맥북 프로", "아이폰 15", "에어팟 프로"] if df.empty else df['item_name'].tolist()
    
    # 🌟 3. 캐시 저장 시도 (실패해도 무시)
    try:
        redis_client.setex(cache_key, 3600, json.dumps(result))
    except redis.ConnectionError:
        pass
    
    return result

def get_cf_recommendation(user_id, n=3):
    """[Model B: 협업 필터링] (Redis 캐싱 + Fallback 적용)"""
    cache_key = f"cf_recommend:{user_id}:{n}"
    
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except redis.ConnectionError:
        logger.warning(f"[Cache Miss] Redis 연결 실패! 유저({user_id}) CF 연산으로 우회합니다.")
        pass

    if not os.path.exists(DB_PATH):
        return get_popular_items(n)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT user_id, item_name FROM user_logs WHERE action_type='click'", conn)
    conn.close()

    if df.empty or user_id not in df['user_id'].values:
        return get_popular_items(n)

    df['clicked'] = 1
    user_item_matrix = df.pivot_table(index='user_id', columns='item_name', values='clicked', fill_value=0)

    user_sim = cosine_similarity(user_item_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)

    similar_users = user_sim_df[user_id].sort_values(ascending=False)[1:]
    if similar_users.empty:
        return get_popular_items(n)
        
    most_similar_user = similar_users.index[0]

    target_user_clicked = user_item_matrix.loc[user_id]
    unclicked_items = target_user_clicked[target_user_clicked == 0].index.tolist()

    similar_user_clicked = user_item_matrix.loc[most_similar_user]
    recommendations = similar_user_clicked[(similar_user_clicked == 1) & (similar_user_clicked.index.isin(unclicked_items))].index.tolist()

    if len(recommendations) < n:
        popular = get_popular_items(n)
        for item in popular:
            if item not in recommendations and len(recommendations) < n:
                recommendations.append(item)

    result = recommendations[:n]
    
    try:
        redis_client.setex(cache_key, 3600, json.dumps(result))
    except redis.ConnectionError:
        pass
    
    return result