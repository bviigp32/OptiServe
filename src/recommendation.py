import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import json
import redis
import logging
import os
from src.database import engine 

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def get_popular_items(n=3):
    cache_key = f"popular_items:{n}"
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except redis.ConnectionError:
        logger.warning("[Cache Miss] Redis 연결 실패! 기본 DB 연산으로 우회합니다.")
        pass

    query = """
        SELECT item_name, COUNT(*) as click_count 
        FROM user_logs 
        WHERE action_type='click' 
        GROUP BY item_name 
        ORDER BY click_count DESC 
        LIMIT %(n)s
    """
    try:
        df = pd.read_sql(query, engine, params={"n": n})
        result = ["맥북 프로", "아이폰 15", "에어팟 프로"] if df.empty else df['item_name'].tolist()
    except Exception as e:
        logger.error(f"DB Query Error: {e}")
        result = ["맥북 프로", "아이폰 15", "에어팟 프로"]
    
    try:
        redis_client.setex(cache_key, 3600, json.dumps(result))
    except redis.ConnectionError:
        pass
    
    return result

def get_cf_recommendation(user_id, n=3):
    cache_key = f"cf_recommend:{user_id}:{n}"
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except redis.ConnectionError:
        logger.warning(f"[Cache Miss] Redis 연결 실패! 유저({user_id}) CF 연산으로 우회합니다.")
        pass

    try:
        df = pd.read_sql("SELECT user_id, item_name FROM user_logs WHERE action_type='click'", engine)
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
    except Exception as e:
         logger.error(f"CF DB Query Error: {e}")
         result = get_popular_items(n)
    
    try:
        redis_client.setex(cache_key, 3600, json.dumps(result))
    except redis.ConnectionError:
        pass
    
    return result